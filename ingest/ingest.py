"""PoC ingest: MQTT 5 shared subscription -> PostgreSQL/TimescaleDB.

- Telemetry (live + backfill): dedupe batch by (edge_id, stream, seq) (07 §6.10), resolve pid via the
  site point mapping (stand-in for the cloud registry), upsert narrow rows keyed by (series, ts).
  After COMMIT, send TELEMETRY_ACK {"stream", "ack_seq"} on ems/v1/{edge}/down/config (07 §7.1).
- cmd-ack -> command_ack (+ command.last_state), event -> event, state -> edge_state.
- Simplified counter state machine: a C4 raw value lower than the previous one -> COUNTER_RESET event.
"""
from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
import psycopg
import yaml
from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.properties import Properties

log = logging.getLogger("ingest")
ENV = os.environ.get


def ts(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc) if ms is not None else None


class Ingest:
    def __init__(self):
        site = yaml.safe_load(open(ENV("SITE_CONFIG", "/config/site.yaml")))
        self.registry = {(e["edge_id"], p["pid"]): (site["site_id"], d["device_id"], p["code"])
                         for e in site["edges"] for d in e["devices"] for p in d["points"]}
        # counters that must be monotonic (07 §6.10); session energy (evse.e_session) restarts per session
        self.monotonic = {(e["edge_id"], p["pid"]) for e in site["edges"] for d in e["devices"] for p in d["points"]
                          if p["sampling_class"] == "C4" and p.get("monotonic", True)}
        self.last_counter: dict[tuple, int] = {}
        self.contig: dict[tuple, int] = {}             # (edge, stream) -> highest gap-free committed seq
        self.above: dict[tuple, set] = {}
        self.dsn = ENV("DATABASE_URL", "postgresql://ems:ems@db:5432/ems")
        self.db = None
        self.stats = {"batches": 0, "dups": 0, "rows": 0}

    def conn(self):
        while self.db is None or self.db.closed:
            try:
                self.db = psycopg.connect(self.dsn, autocommit=True)
            except psycopg.OperationalError as ex:
                log.warning("DB not ready: %s", ex)
                time.sleep(2)
        return self.db

    # ---- handlers -------------------------------------------------------------------
    def telemetry(self, topic: str, msg: dict) -> None:
        edge, stream, seq = msg["edge_id"], msg["stream"], msg["seq"]
        backfill = topic.endswith("/up/backfill")
        with self.conn().transaction():
            cur = self.db.execute(
                "INSERT INTO telemetry_batch(edge_id, stream, seq, topic, n_points, batch_ts) VALUES(%s,%s,%s,%s,%s,%s) "
                "ON CONFLICT DO NOTHING RETURNING seq", (edge, stream, seq, topic, len(msg["points"]), ts(msg.get("batch_ts"))))
            if cur.fetchone() is None:
                self.stats["dups"] += 1
                self.telemetry_ack(edge, stream, seq)
                return
            rows = []
            for p in msg["points"]:
                key = self.registry.get((edge, p["pid"]))
                if key is None:
                    log.warning("unknown pid %s from %s", p["pid"], edge)
                    continue
                value = p.get("raw", p.get("avg"))
                rows.append((*key, ts(p["ts"]), value, p["q"], p.get("w"), p.get("min"), p.get("max"), p.get("last"),
                             p.get("n"), p.get("cov_ms"), ts(p.get("ts_src")), edge, stream, seq, backfill))
                if "raw" in p and (edge, p["pid"]) in self.monotonic:
                    self.check_counter(key, p)
            self.db.cursor().executemany(
                "INSERT INTO telemetry(site_id, device_id, point_code, ts, value, quality, w_s, v_min, v_max, v_last, n, "
                "cov_ms, ts_src, edge_id, stream, seq, via_backfill) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                "ON CONFLICT (site_id, device_id, point_code, ts) DO NOTHING", rows)
        self.stats["batches"] += 1
        self.stats["rows"] += len(rows)
        self.telemetry_ack(edge, stream, seq)          # only after the transaction committed

    def telemetry_ack(self, edge: str, stream: str, seq: int) -> None:
        """Cumulative TELEMETRY_ACK (07 §7.1): ack_seq = highest seq with no gap below it, so the edge never
        drops a batch that the cloud has not committed (a missing seq keeps everything above it buffered)."""
        key = (edge, stream)
        if key not in self.contig:
            seqs = [r[0] for r in self.db.execute("SELECT seq FROM telemetry_batch WHERE edge_id=%s AND stream=%s "
                                                  "ORDER BY seq", key).fetchall()]
            c = seqs[0] - 1 if seqs else seq - 1
            for x in seqs:
                if x != c + 1:
                    break
                c = x
            self.contig[key], self.above[key] = c, {x for x in seqs if x > c}
        self.above[key].add(seq)
        while self.contig[key] + 1 in self.above[key]:
            self.contig[key] += 1
            self.above[key].discard(self.contig[key])
        p = Properties(PacketTypes.PUBLISH)
        p.ContentType, p.PayloadFormatIndicator = "application/json", 1
        self.client.publish(f"ems/v1/{edge}/down/config", json.dumps({"type": "TELEMETRY_ACK", "stream": stream,
                            "ack_seq": self.contig[key]}), qos=1, properties=p)

    def check_counter(self, key: tuple, p: dict) -> None:
        prev = self.last_counter.get(key)
        self.last_counter[key] = p["raw"]
        if prev is not None and p["raw"] < prev:
            self.db.execute("INSERT INTO event(edge_id, event_id, type, device_id, ts, state, payload) "
                            "VALUES(%s,%s,'COUNTER_RESET',%s,%s,'RAISED',%s) ON CONFLICT DO NOTHING",
                            ("cloud", f"cr-{key[1]}-{key[2]}-{p['ts']}", key[1], ts(p["ts"]),
                             json.dumps({"point_code": key[2], "prev_raw": prev, "raw": p["raw"]})))
            log.warning("COUNTER_RESET %s %s: %s -> %s", key[1], key[2], prev, p["raw"])

    def ack(self, msg: dict, props) -> None:
        corr = (getattr(props, "CorrelationData", b"") or b"").decode(errors="replace")
        if corr and corr != msg["command_id"]:
            log.error("ack correlation mismatch %s != %s", corr, msg["command_id"])
        db = self.conn()
        db.execute("INSERT INTO command_ack(command_id, edge_id, state, ts, payload) VALUES(%s,%s,%s,%s,%s)",
                   (msg["command_id"], msg["edge_id"], msg["state"], ts(msg["ts"]), json.dumps(msg)))
        db.execute("INSERT INTO command(command_id, edge_id, last_state, last_state_at) VALUES(%s,%s,%s,%s) "
                   "ON CONFLICT (command_id) DO UPDATE SET last_state=excluded.last_state, last_state_at=excluded.last_state_at",
                   (msg["command_id"], msg["edge_id"], msg["state"], ts(msg["ts"])))

    def event(self, msg: dict) -> None:
        db = self.conn()
        for ev in msg["events"]:
            db.execute("INSERT INTO event(edge_id, event_id, type, device_id, ts, ts_src, state, code_raw, payload) "
                       "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                       (msg["edge_id"], ev["event_id"], ev["type"], ev.get("device_id"), ts(ev["ts"]),
                        ts(ev.get("ts_src")), ev.get("state"), ev.get("code_raw"), json.dumps(ev)))

    def state(self, msg: dict) -> None:
        self.conn().execute("INSERT INTO edge_state(edge_id, payload, updated_at) VALUES(%s,%s,now()) "
                            "ON CONFLICT (edge_id) DO UPDATE SET payload=excluded.payload, updated_at=now()",
                            (msg["edge_id"], json.dumps(msg)))

    def on_message(self, client, userdata, m) -> None:
        try:
            msg = json.loads(m.payload)
            if "/up/telemetry/" in m.topic or m.topic.endswith("/up/backfill"):
                self.telemetry(m.topic, msg)
            elif m.topic.endswith("/up/cmd-ack"):
                self.ack(msg, m.properties)
            elif m.topic.endswith("/up/event"):
                self.event(msg)
            elif m.topic.endswith("/up/state"):
                self.state(msg)
        except psycopg.Error as ex:
            log.error("DB error on %s: %s", m.topic, ex)
            self.db = None
        except Exception:
            log.exception("bad message on %s", m.topic)

    def run(self) -> None:
        self.conn()
        c = self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="ingest-1", protocol=mqtt.MQTTv5)
        c.username_pw_set(ENV("MQTT_USERNAME", "ingest"), ENV("MQTT_PASSWORD", ""))
        c.on_message = self.on_message

        def on_connect(client, userdata, flags, rc, props):
            log.info("connected to broker: %s", rc)
            client.subscribe("$share/ingest/ems/v1/+/up/#", qos=1)
        c.on_connect = on_connect
        cp = Properties(PacketTypes.CONNECT)
        cp.SessionExpiryInterval = 3600
        c.connect_async(ENV("MQTT_HOST", "mosquitto"), int(ENV("MQTT_PORT", "1883")), keepalive=30,
                        clean_start=False, properties=cp)
        c.reconnect_delay_set(1, 10)
        c.loop_start()
        open("/tmp/ingest.alive", "w").close()
        while True:
            time.sleep(30)
            log.info("ingest stats %s", self.stats)
            open("/tmp/ingest.alive", "w").close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    Ingest().run()
