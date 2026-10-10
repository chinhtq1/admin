"""MQTT 5 uplink: session, LWT, store-and-forward drain with ordered backfill (07 §6.12, §7.1).

Every uplink message goes through the SQLite outbox first. A drain thread publishes in id order:
rows created while connected go to their live topic; rows created before the current connection
(i.e. buffered during an outage) are telemetry backfill -> `up/backfill`, oldest first, rate-limited.
Telemetry stays in the outbox until the cloud's TELEMETRY_ACK on down/config (PUBACK only proves the
broker got it); unacknowledged batches are re-sent after RESEND_S and de-duplicated by seq at ingest.
"""
from __future__ import annotations

import json
import logging
import os
import threading
import time

import paho.mqtt.client as mqtt
from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.properties import Properties

from bridge.store import Store, now_ms

log = logging.getLogger("bridge.uplink")


def props_for(packet_type, d: dict) -> Properties:
    p = Properties(packet_type)
    if "content_type" in d:
        p.ContentType = d["content_type"]
    if "payload_format_indicator" in d:
        p.PayloadFormatIndicator = d["payload_format_indicator"]
    if "correlation_data" in d:
        p.CorrelationData = d["correlation_data"].encode()
    if "message_expiry_interval" in d:
        p.MessageExpiryInterval = d["message_expiry_interval"]
    if d.get("user_properties"):
        p.UserProperty = [(k, str(v)) for k, v in d["user_properties"].items()]
    return p


class Uplink:
    def __init__(self, edge_id: str, host: str, port: int, username: str, password: str, store: Store,
                 backfill_rate: float = 20.0):
        self.edge_id, self.store, self.backfill_rate = edge_id, store, backfill_rate
        self.prefix = f"ems/v1/{edge_id}"
        self.connected = threading.Event()
        self.connected_since_ms = 0
        self.on_command = None          # callable(payload: bytes, properties) set by main
        self.state_provider = None      # callable() -> dict for up/state
        self.stats = {"published": 0, "backfilled": 0, "acked": 0}
        self.resend_ms = int(os.environ.get("TELEMETRY_RESEND_S", "20")) * 1000
        c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=edge_id, protocol=mqtt.MQTTv5)
        c.username_pw_set(username, password)
        will_props = Properties(PacketTypes.WILLMESSAGE)
        will_props.WillDelayInterval = 2
        will_props.ContentType = "application/json"
        c.will_set(f"{self.prefix}/up/state", json.dumps({"schema": "ems.state.v1", "edge_id": edge_id, "online": False}),
                   qos=1, retain=True, properties=will_props)
        # 07 §6.12: exponential backoff 1 s -> 5 min; PoC caps at MQTT_RECONNECT_MAX_S (default 10 s) for quick demos
        c.reconnect_delay_set(min_delay=1, max_delay=int(os.environ.get("MQTT_RECONNECT_MAX_S", "10")))
        c.on_connect, c.on_disconnect, c.on_message = self._on_connect, self._on_disconnect, self._on_message
        self.client = c
        self.host, self.port = host, port

    # ---- connection -----------------------------------------------------------------
    def start(self) -> None:
        cp = Properties(PacketTypes.CONNECT)
        cp.SessionExpiryInterval = 3600     # still-valid commands survive short drops (07 §8.2a)
        self.client.connect_async(self.host, self.port, keepalive=30, clean_start=False, properties=cp)
        self.client.loop_start()
        threading.Thread(target=self._drain, name="drain", daemon=True).start()

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            log.error("MQTT connect refused: %s", reason_code)
            return
        self.connected_since_ms = now_ms()
        unacked = self.store.reset_unacked()
        self.connected.set()
        backlog = self.store.outbox_stats()
        log.warning("MQTT connected (session_present=%s); outbox backlog=%d (incl. %d sent but unacknowledged)",
                    flags.session_present, backlog["buffered"], unacked)
        client.subscribe(f"{self.prefix}/down/cmd", qos=1)
        client.subscribe(f"{self.prefix}/down/config", qos=1)
        self.publish_state()

    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        self.connected.clear()
        log.warning("MQTT disconnected: %s -> buffering to SQLite", reason_code)

    def _on_message(self, client, userdata, msg):
        if msg.topic.endswith("/down/cmd") and self.on_command:
            self.on_command(msg.payload, msg.properties)
        elif msg.topic.endswith("/down/config"):
            try:
                body = json.loads(msg.payload)
            except ValueError:
                return
            if body.get("type") == "TELEMETRY_ACK":
                self.stats["acked"] += self.store.ack_telemetry(body["stream"], int(body["ack_seq"]))

    def publish_state(self) -> None:
        if not self.state_provider or not self.connected.is_set():
            return
        p = props_for(PacketTypes.PUBLISH, {"content_type": "application/json", "payload_format_indicator": 1,
                                            "user_properties": {"schema": "ems.state.v1"}})
        self.client.publish(f"{self.prefix}/up/state", json.dumps(self.state_provider()), qos=1, retain=True, properties=p)

    # ---- drain ----------------------------------------------------------------------
    def _publish_row(self, row, backfill: bool) -> bool:
        row_id, kind, topic, bf_topic, payload, props = row
        if backfill and bf_topic:
            topic = bf_topic
        try:
            info = self.client.publish(topic, payload, qos=1, retain=False,
                                       properties=props_for(PacketTypes.PUBLISH, json.loads(props)))
            info.wait_for_publish(timeout=5)
            if not info.is_published():
                return False
        except (RuntimeError, ValueError) as ex:          # not connected / queue full
            log.debug("publish failed: %s", ex)
            return False
        if kind == "telemetry":
            self.store.mark_sent(row_id)          # delete on TELEMETRY_ACK, not on PUBACK
        else:
            self.store.delete(row_id)
        self.stats["backfilled" if backfill and bf_topic else "published"] += 1
        return True

    def _drain(self) -> None:
        last_bf = 0.0
        while True:
            if not self.connected.wait(timeout=1):
                continue
            since = self.connected_since_ms
            live = self.store.pending(since, live=True, limit=100, resend_ms=self.resend_ms)
            ok = all(self._publish_row(r, backfill=False) for r in live) if live else True
            if not ok:
                time.sleep(0.5)
                continue
            # backlog from before this connection: ordered, rate-limited (07 §6.7 / §6.12 step 5)
            if time.monotonic() - last_bf >= 1.0:
                last_bf = time.monotonic()
                backlog = self.store.pending(since, live=False, limit=max(1, int(self.backfill_rate)),
                                             resend_ms=self.resend_ms)
                for r in backlog:
                    if not self._publish_row(r, backfill=True):
                        break
                if backlog:
                    log.info("backfill: sent %d buffered message(s), remaining unsent %d", len(backlog),
                             self.store.outbox_stats()["buffered"])
            if not live:
                time.sleep(0.2)
