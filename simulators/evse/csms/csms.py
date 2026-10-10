"""Minimal OCPP 1.6J CSMS stub (mobilityhouse `ocpp`, MIT) -> canonical EV telemetry on MQTT 5.

Accepts BootNotification / Heartbeat / StatusNotification / Authorize / Start/StopTransaction /
MeterValues; after boot it sets MeterValueSampleInterval=5 s and installs a safe TxDefaultProfile
(SetChargingProfile, 07 §5.9). Command SET_EV_LIMIT on ems/v1/edge-ev01/down/cmd -> SetChargingProfile.
EV power is also POSTed to the virtual site so the POC meter balance includes the chargers.
PoC: no store-and-forward, no security profile 2/3 (production CSMS lives inside the edge, 07 §5.9).
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
import urllib.request
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
import websockets
from ocpp.routing import on
from ocpp.v16 import ChargePoint as CP16
from ocpp.v16 import call, call_result
from ocpp.v16.enums import Action, AuthorizationStatus, RegistrationStatus
from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.properties import Properties

log = logging.getLogger("csms")
ENV = os.environ.get
EDGE_ID = ENV("EDGE_ID", "edge-ev01")
PID = {"evse.p": 4001, "evse.i_limit_active": 4002, "evse.e_session": 4003}
W_C1, W_C2, C4_PERIOD = 5, 60, 60


def now_ms() -> int:
    return int(time.time() * 1000)


def iso(ms: int | None = None) -> str:
    return datetime.fromtimestamp((ms or now_ms()) / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z")


class Mqtt:
    def __init__(self):
        self.c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=EDGE_ID, protocol=mqtt.MQTTv5)
        self.c.username_pw_set(ENV("MQTT_USERNAME", EDGE_ID), ENV("MQTT_PASSWORD", ""))
        self.seq: dict[str, int] = {}
        self.on_cmd = None
        self.c.on_connect = lambda c, u, f, rc, p: (log.info("MQTT connected %s", rc),
                                                    c.subscribe(f"ems/v1/{EDGE_ID}/down/cmd", qos=1))
        self.c.on_message = lambda c, u, m: self.on_cmd and self.on_cmd(m.payload)
        self.c.connect_async(ENV("MQTT_HOST", "mosquitto"), int(ENV("MQTT_PORT", "1883")), keepalive=30)
        self.c.reconnect_delay_set(1, 10)
        self.c.loop_start()

    def publish(self, suffix: str, payload: dict, schema: str, correlation: str | None = None) -> None:
        p = Properties(PacketTypes.PUBLISH)
        p.ContentType, p.PayloadFormatIndicator = "application/json", 1
        p.UserProperty = [("schema", schema)] + ([("edge_seq", str(payload["seq"]))] if "seq" in payload else [])
        if correlation:
            p.CorrelationData = correlation.encode()
        self.c.publish(f"ems/v1/{EDGE_ID}/{suffix}", json.dumps(payload), qos=1, properties=p)

    def telemetry(self, stream: str, points: list[dict]) -> None:
        self.seq[stream] = self.seq.get(stream, int(time.time())) + 1     # PoC: time-seeded, not persisted
        self.publish(f"up/telemetry/{stream}", {"schema": "ems.telemetry.v1", "edge_id": EDGE_ID, "stream": stream,
                                                "seq": self.seq[stream], "batch_ts": now_ms(), "config_version": 1,
                                                "points": points}, "ems.telemetry.v1")

    def event(self, ev: dict) -> None:
        self.seq["event"] = self.seq.get("event", int(time.time())) + 1
        ev = {"event_id": f"{EDGE_ID}-ev-{self.seq['event']}", "device_id": "evse-01", "ts": now_ms(), **ev}
        self.publish("up/event", {"schema": "ems.event.v1", "edge_id": EDGE_ID, "seq": self.seq["event"],
                                  "events": [ev]}, "ems.event.v1")


class Site:
    """Station-level state (device evse-01 = sum of connectors) + window aggregation."""

    def __init__(self, bus: Mqtt):
        self.bus = bus
        self.p_conn: dict[int, float] = {}
        self.e_conn: dict[int, float] = {}
        self.e_start: dict[int, float] = {}
        self.i_limit = None
        self.win = {"c1": [], "c2": []}
        self.cp: CS | None = None

    @property
    def p(self) -> float:
        return sum(self.p_conn.values())

    def sample(self) -> None:
        self.win["c1"].append(self.p)
        if self.i_limit is not None:
            self.win["c2"].append(self.i_limit)
        try:
            req = urllib.request.Request(ENV("VSITE_URL", "http://vsite:8080") + "/ev", method="POST",
                                         data=json.dumps({"p_w": self.p}).encode(),
                                         headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=1).read()
        except OSError as ex:
            log.debug("vsite /ev: %s", ex)

    async def loop(self) -> None:
        nxt = {"c1": 0, "c2": 0, "c4": 0}
        while True:
            await asyncio.sleep(1)
            if self.cp is None:
                continue
            self.sample()                      # hold-last 1 s sampling of the latest MeterValues
            t = now_ms()
            for stream, w, pid in (("c1", W_C1, PID["evse.p"]), ("c2", W_C2, PID["evse.i_limit_active"])):
                start = t - t % (w * 1000)
                if nxt[stream] == 0:
                    nxt[stream] = start + w * 1000
                if t >= nxt[stream]:
                    vals, self.win[stream] = self.win[stream], []
                    ws = nxt[stream] - w * 1000
                    nxt[stream] = start + w * 1000
                    if vals:
                        self.bus.telemetry(stream, [{"pid": pid, "ts": ws, "w": w, "avg": round(sum(vals) / len(vals), 1),
                                                     "min": min(vals), "max": max(vals), "last": vals[-1], "n": len(vals),
                                                     "q": "GOOD"}])
            if t >= nxt["c4"]:
                nxt["c4"] = t - t % (C4_PERIOD * 1000) + C4_PERIOD * 1000
                e = sum(self.e_conn[c] - self.e_start.get(c, self.e_conn[c]) for c in self.e_conn)
                self.bus.telemetry("c4", [{"pid": PID["evse.e_session"], "ts": t, "raw": int(e), "q": "GOOD"}])


class CS(CP16):
    site: Site

    @on(Action.boot_notification)
    async def on_boot(self, charge_point_vendor, charge_point_model, **kw):
        log.info("[%s] BootNotification vendor=%s model=%s", self.id, charge_point_vendor, charge_point_model)
        self.site.cp = self
        asyncio.get_running_loop().call_later(2, lambda: asyncio.ensure_future(self.configure()))
        return call_result.BootNotification(current_time=iso(), interval=60, status=RegistrationStatus.accepted)

    async def configure(self):
        for k, v in (("MeterValueSampleInterval", "5"), ("MeterValuesSampledData", "Energy.Active.Import.Register,Power.Active.Import")):
            r = await self.call(call.ChangeConfiguration(key=k, value=v))
            log.info("[%s] ChangeConfiguration %s=%s -> %s", self.id, k, v, r.status)
        r = await self.set_limit(32.0, purpose="TxDefaultProfile", profile_id=1)      # safe default (07 §5.9)
        log.info("[%s] SetChargingProfile TxDefaultProfile 32 A (safe default) -> %s", self.id, r.status)

    async def set_limit(self, amps: float, purpose="TxDefaultProfile", profile_id=2, valid_to: str | None = None):
        prof = {"chargingProfileId": profile_id, "stackLevel": profile_id, "chargingProfilePurpose": purpose,
                "chargingProfileKind": "Absolute",
                "chargingSchedule": {"chargingRateUnit": "A", "chargingSchedulePeriod": [{"startPeriod": 0, "limit": amps}]}}
        if valid_to:
            prof["validTo"] = valid_to
        r = await self.call(call.SetChargingProfile(connector_id=0, cs_charging_profiles=prof))
        if r.status == "Accepted":
            self.site.i_limit = amps
        return r

    @on(Action.heartbeat)
    async def on_hb(self):
        return call_result.Heartbeat(current_time=iso())

    @on(Action.status_notification)
    async def on_status(self, connector_id, error_code, status, **kw):
        log.info("[%s] StatusNotification c%s=%s", self.id, connector_id, status)
        self.site.bus.event({"type": "EVSE_STATUS", "connector_id": connector_id, "state": status, "code_raw": error_code})
        if status in ("Available", "Finishing", "Faulted", "Unavailable"):
            self.site.p_conn[connector_id] = 0.0
        return call_result.StatusNotification()

    @on(Action.authorize)
    async def on_authorize(self, id_tag):
        return call_result.Authorize(id_tag_info={"status": AuthorizationStatus.accepted})

    @on(Action.start_transaction)
    async def on_start_tx(self, connector_id, id_tag, meter_start, timestamp, **kw):
        log.info("[%s] StartTransaction c%s meter_start=%s Wh", self.id, connector_id, meter_start)
        self.site.e_start[connector_id] = float(meter_start)
        self.site.e_conn[connector_id] = float(meter_start)
        return call_result.StartTransaction(transaction_id=int(time.time()) % 1_000_000,
                                            id_tag_info={"status": AuthorizationStatus.accepted})

    @on(Action.stop_transaction)
    async def on_stop_tx(self, meter_stop, timestamp, transaction_id, **kw):
        log.info("[%s] StopTransaction tx=%s meter_stop=%s Wh", self.id, transaction_id, meter_stop)
        return call_result.StopTransaction()

    @on(Action.meter_values)
    async def on_meter_values(self, connector_id, meter_value, **kw):
        for mv in meter_value:
            for s in mv["sampled_value"]:
                if s.get("phase"):
                    continue
                meas, val = s.get("measurand", "Energy.Active.Import.Register"), float(s["value"])
                if meas == "Power.Active.Import":
                    self.site.p_conn[connector_id] = val * (1000 if s.get("unit") == "kW" else 1)
                elif meas == "Energy.Active.Import.Register":
                    self.site.e_conn[connector_id] = val * (1000 if s.get("unit") == "kWh" else 1)
        log.info("[%s] MeterValues c%s -> evse.p=%.0f W", self.id, connector_id, self.site.p)
        return call_result.MeterValues()


async def handle_command(site: Site, raw: bytes) -> None:
    env = json.loads(raw)
    cid = env.get("command_id", "?")

    def ack(state, **x):
        site.bus.publish("up/cmd-ack", {"schema": "ems.cmd-ack.v1", "edge_id": EDGE_ID, "command_id": cid,
                                        "state": state, "ts": now_ms(), **x}, "ems.cmd-ack.v1", correlation=cid)
    ack("RECEIVED")
    exp = datetime.fromisoformat(env["expires_at"].replace("Z", "+00:00")).timestamp() * 1000 if env.get("expires_at") else 0
    if env.get("type") != "SET_EV_LIMIT" or env.get("target", {}).get("edge_id") != EDGE_ID:
        return ack("REJECTED_INVALID", reason="TYPE_OR_TARGET")
    if now_ms() > exp:
        return ack("REJECTED_STALE", reason="EXPIRED_BEFORE_EXECUTION")
    amps = float(env["params"]["i_max_a"])
    if amps != 0 and amps < 6:
        return ack("REJECTED_OUT_OF_LIMIT", reason="BELOW_I_MIN_6A")
    if site.cp is None:
        return ack("FAILED_TIMEOUT", reason="NO_CHARGER_CONNECTED")
    ack("ACCEPTED", requested=env["params"])
    r = await site.cp.set_limit(amps, purpose="TxDefaultProfile", profile_id=2, valid_to=env["expires_at"])
    ack("DISPATCHED")
    if r.status != "Accepted":
        return ack("FAILED_DEVICE_EXCEPTION", reason=f"SetChargingProfile {r.status}")
    ack("APPLIED", readback={"point": "SetChargingProfile.status", "value": r.status}, effective_setpoint={"i_max_a": amps})
    await asyncio.sleep(max(0, (exp - now_ms()) / 1000))
    await site.cp.call(call.ClearChargingProfile(id=2))
    site.i_limit = 32.0
    ack("EXPIRED", on_expiry="REVERT_DEFAULT")
    ack("COMPLETED")


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    logging.getLogger("ocpp").setLevel(logging.WARNING)
    logging.getLogger("websockets.server").setLevel(logging.WARNING)
    site = Site(Mqtt())
    loop = asyncio.get_running_loop()
    site.bus.on_cmd = lambda raw: asyncio.run_coroutine_threadsafe(handle_command(site, raw), loop)

    async def handler(ws):
        cp_id = ws.request.path.strip("/").split("/")[-1] or "unknown"
        log.info("charger connected id=%s subprotocol=%s", cp_id, ws.subprotocol)
        cp = CS(cp_id, ws)
        cp.site = site
        try:
            await cp.start()
        except websockets.ConnectionClosed:
            log.info("charger %s disconnected", cp_id)
            site.cp, site.p_conn = None, {}

    async with websockets.serve(handler, "0.0.0.0", 9000, subprotocols=["ocpp1.6"]):
        log.info("CSMS stub listening on :9000 (OCPP 1.6J), MQTT edge_id=%s", EDGE_ID)
        open("/tmp/csms.alive", "w").close()
        await site.loop()


if __name__ == "__main__":
    asyncio.run(main())
