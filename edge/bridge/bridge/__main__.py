"""PoC edge bridge: Modbus (YAML maps) -> canonical MQTT 5 telemetry, commands -> Modbus.

!! PoC only. The production edge (06/07: signed config, JWS, arbiter, local control loop, mTLS,
Protobuf+zstd, TELEMETRY_ACK) is a different component. This one proves the contracts end to end.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from pathlib import Path

import yaml

from bridge.aggregate import Aggregator
from bridge.commands import CommandHandler
from bridge.poller import EndpointPoller
from bridge.store import Store, now_ms
from bridge.uplink import Uplink
from regmap import load_maps

log = logging.getLogger("bridge")
ENV = os.environ.get
MAX_BATCH_BYTES = int(ENV("MAX_BATCH_BYTES", "262144"))
HEALTH_FILE = Path("/tmp/bridge.alive")


class Bridge:
    def __init__(self):
        self.edge_id = ENV("EDGE_ID", "edge-vsite01")
        site = yaml.safe_load(open(ENV("SITE_CONFIG", "/config/site.yaml")))
        self.site_id, self.config_version = site["site_id"], site["config_version"]
        edge = next(e for e in site["edges"] if e["edge_id"] == self.edge_id)
        maps = load_maps(ENV("MAPS_DIR", "/app/maps"))
        os.makedirs(ENV("DATA_DIR", "/data"), exist_ok=True)
        self.store = Store(os.path.join(ENV("DATA_DIR", "/data"), "bridge.sqlite"))
        self.period = float(ENV("POLL_PERIOD_S", "1"))
        self.agg = Aggregator(poll_period_s=self.period)
        self.pollers = [EndpointPoller(d, maps[d["driver"]], self.period, self.on_reading, self.on_device_event)
                        for d in edge["devices"] if d["endpoint"]["protocol"] == "MODBUS_TCP"]
        self.alarm_state: dict[tuple, int] = {}
        self.uplink = Uplink(self.edge_id, ENV("MQTT_HOST", "mosquitto"), int(ENV("MQTT_PORT", "1883")),
                             ENV("MQTT_USERNAME", self.edge_id), ENV("MQTT_PASSWORD", ""), self.store,
                             float(ENV("BACKFILL_RATE", "20")))
        ess_dev = next(d for d in edge["devices"] if d["device_id"] == "ess-01")
        self.ess = next(p for p in self.pollers if p.device_id == "ess-01")
        self.cmd = CommandHandler(self.edge_id, self.store, self.uplink, self.ess, ess_dev["control"]["soe"],
                                  rated_w=float(ess_dev["control"]["soe"]["p_discharge_max_w"]))
        self.uplink.state_provider = self.state

    # ---- callbacks from pollers -----------------------------------------------------
    def on_reading(self, device_id: str, point: dict, rd) -> None:
        if point["sampling_class"] == "C5":                      # alarm word -> event on change
            if rd.value is None:
                return
            key, val = (device_id, point["code"]), int(rd.value)
            prev = self.alarm_state.get(key, 0)
            if val != prev:
                self.alarm_state[key] = val
                self.emit_event({"type": "DEVICE_ALARM", "device_id": device_id, "point": point["code"],
                                 "ts": rd.ts_ms, "ts_src": rd.ts_src_ms, "src_clock_state": "UNKNOWN",
                                 "code_raw": hex(val if val else prev), "state": "RAISED" if val else "CLEARED",
                                 "q": rd.q})
            return
        self.agg.add(point, rd)

    def on_device_event(self, device_id: str, etype: str, state: str, ts: int, detail) -> None:
        self.emit_event({"type": etype, "device_id": device_id, "ts": ts, "state": state})

    def emit_event(self, ev: dict) -> None:
        seq = self.store.next_seq("event")
        ev = {"event_id": f"{self.edge_id}-ev-{seq}", **ev}
        log.info("event %s", ev)
        self.store.enqueue("event", f"ems/v1/{self.edge_id}/up/event",
                           {"schema": "ems.event.v1", "edge_id": self.edge_id, "seq": seq, "events": [ev]},
                           {"content_type": "application/json", "payload_format_indicator": 1,
                            "user_properties": {"schema": "ems.event.v1", "edge_seq": seq}})

    def state(self) -> dict:
        return {"schema": "ems.state.v1", "edge_id": self.edge_id, "online": True, "firmware_version": "bridge-poc-0.1.0",
                "config_version_reported": self.config_version, "clock_state": "SYNCED", "run_mode": "NORMAL",
                "active_commands": self.cmd.active_commands(), **self.store.outbox_stats(),
                "last_seq_by_stream": self.store.last_seqs(), "ts": now_ms()}

    # ---- loops ----------------------------------------------------------------------
    async def flush_loop(self) -> None:
        """Close windows every second, batch per stream (<= MAX_BATCH_BYTES), enqueue with seq."""
        while True:
            await asyncio.sleep(1.0)
            HEALTH_FILE.touch()
            for stream, samples in self.agg.flush(now_ms()).items():
                for chunk in self._chunks(samples):
                    seq = self.store.next_seq(stream)
                    payload = {"schema": "ems.telemetry.v1", "edge_id": self.edge_id, "stream": stream, "seq": seq,
                               "batch_ts": now_ms(), "config_version": self.config_version, "points": chunk}
                    self.store.enqueue("telemetry", f"ems/v1/{self.edge_id}/up/telemetry/{stream}", payload,
                                       {"content_type": "application/json", "payload_format_indicator": 1,
                                        "user_properties": {"schema": "ems.telemetry.v1", "edge_seq": seq}},
                                       stream=stream, seq=seq, backfill_topic=f"ems/v1/{self.edge_id}/up/backfill")

    @staticmethod
    def _chunks(samples: list[dict]):
        chunk, size = [], 300
        for s in samples:
            n = len(json.dumps(s)) + 1
            if chunk and size + n > MAX_BATCH_BYTES:
                yield chunk
                chunk, size = [], 300
            chunk.append(s)
            size += n
        if chunk:
            yield chunk

    async def heartbeat_loop(self) -> None:
        """Refresh the BESS watchdog register (07 §8.6: device-side revert if the EMS goes silent)."""
        n = 0
        period = float(ENV("HEARTBEAT_PERIOD_S", "2"))
        while True:
            n = (n + 1) % 65536
            err = await self.ess.write("_ess.heartbeat", n)
            if err:
                log.warning("heartbeat write failed: %s", err)
            await asyncio.sleep(period)

    async def state_loop(self) -> None:
        while True:
            await asyncio.sleep(30)                 # 07 §6.11: heartbeat 30 s
            self.uplink.publish_state()
            st = self.store.outbox_stats()
            log.info("uplink: connected=%s published=%d backfilled=%d acked=%d buffered=%d awaiting_ack=%d",
                     self.uplink.connected.is_set(), self.uplink.stats["published"], self.uplink.stats["backfilled"],
                     self.uplink.stats["acked"], st["buffered"], st["awaiting_ack"])

    async def run(self) -> None:
        loop = asyncio.get_running_loop()
        self.uplink.on_command = lambda payload, props: self.cmd.submit(loop, payload, props)
        self.uplink.start()
        log.info("PoC bridge %s: %d Modbus endpoints, poll %.1f s", self.edge_id, len(self.pollers), self.period)
        await asyncio.gather(self.flush_loop(), self.heartbeat_loop(), self.state_loop(), self.cmd.run(),
                             *(p.run() for p in self.pollers))


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    logging.getLogger("pymodbus").setLevel(logging.CRITICAL)
    async def amain():
        await Bridge().run()        # pymodbus clients need a running loop at construction
    asyncio.run(amain())


if __name__ == "__main__":
    main()
