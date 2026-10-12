"""MQTT 5 client wrapper for contract/integration/system tests (paho-mqtt 2.1, same as the product).

Features
- synchronous connect/subscribe/publish that wait for CONNACK/SUBACK/PUBACK with explicit timeouts
- every received message is recorded (topic, payload, qos, retain, MQTT 5 properties)
- `wait_for_message` / `wait_for_acks(command_id)` poll the recording (no sleeps)
- correlation by MQTT 5 Correlation Data (07 §8.2a) with payload `command_id` as fallback
- optional JSONL transcript written on close (picked up as a failure artifact)
"""

from __future__ import annotations

import json
import threading
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import paho.mqtt.client as paho
from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.properties import Properties

from framework.wait import WaitTimeout, wait_for_value

# Command lifecycle states (07 §8.4) that end a command's processing for waiting purposes.
TERMINAL_ACK_STATES = frozenset({"APPLIED", "APPLIED_CLAMPED", "COMPLETED", "SUPERSEDED", "EXPIRED"})


def is_final_ack_state(state: str) -> bool:
    return state in TERMINAL_ACK_STATES or state.startswith(("REJECTED", "FAILED"))


@dataclass(frozen=True)
class ReceivedMessage:
    topic: str
    payload: bytes
    qos: int
    retain: bool
    properties: dict[str, Any]
    received_monotonic: float = field(default_factory=time.monotonic)

    def json(self) -> Any:
        return json.loads(self.payload.decode("utf-8"))

    @property
    def correlation_data(self) -> bytes | None:
        return self.properties.get("CorrelationData")

    def user_properties(self) -> dict[str, str]:
        return dict(self.properties.get("UserProperty", []))

    def as_record(self) -> dict[str, Any]:
        try:
            body: Any = self.json()
        except (ValueError, UnicodeDecodeError):
            body = self.payload.hex()
        props = {k: (v.hex() if isinstance(v, bytes) else v) for k, v in self.properties.items()}
        return {"topic": self.topic, "qos": self.qos, "retain": self.retain, "properties": props, "payload": body}


def _props_to_dict(props: Properties | None) -> dict[str, Any]:
    if props is None:
        return {}
    out: dict[str, Any] = {}
    for name in (
        "ContentType",
        "PayloadFormatIndicator",
        "MessageExpiryInterval",
        "ResponseTopic",
        "CorrelationData",
        "UserProperty",
        "SubscriptionIdentifier",
    ):
        if hasattr(props, name):
            out[name] = getattr(props, name)
    return out


class MqttError(RuntimeError):
    pass


class Mqtt5Client:
    """Thin, test-oriented MQTT 5 client. Use as a context manager or call close()."""

    def __init__(
        self,
        *,
        host: str,
        port: int,
        username: str | None,
        password: str | None,
        client_id: str,
        transcript_path: Path | None = None,
        clean_start: bool = True,
    ) -> None:
        self.client_id = client_id
        self._host, self._port = host, port
        self._clean_start = clean_start
        self._transcript_path = transcript_path
        self._lock = threading.Lock()
        self._messages: list[ReceivedMessage] = []
        self._connack: tuple[bool, Any] | None = None
        self._suback: dict[int, list[Any]] = {}
        self._client = paho.Client(paho.CallbackAPIVersion.VERSION2, client_id=client_id, protocol=paho.MQTTv5)
        if username is not None:
            self._client.username_pw_set(username, password)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.on_subscribe = self._on_subscribe

    # ---- paho callbacks (network thread) ----------------------------------------------
    def _on_connect(self, _c, _u, _flags, reason_code, _props) -> None:
        self._connack = (not reason_code.is_failure, reason_code)

    def _on_subscribe(self, _c, _u, mid, reason_codes, _props) -> None:
        self._suback[mid] = list(reason_codes)

    def _on_message(self, _c, _u, msg) -> None:
        rec = ReceivedMessage(
            msg.topic, bytes(msg.payload), msg.qos, bool(msg.retain), _props_to_dict(getattr(msg, "properties", None))
        )
        with self._lock:
            self._messages.append(rec)

    # ---- lifecycle ----------------------------------------------------------------------
    def connect(self, timeout: float = 10.0) -> Mqtt5Client:
        self._client.connect(self._host, self._port, keepalive=30, clean_start=self._clean_start)
        self._client.loop_start()
        try:
            ok, rc = wait_for_value(
                lambda: self._connack, lambda v: v is not None, timeout=timeout, desc=f"CONNACK for {self.client_id}"
            )
        except WaitTimeout:
            self._client.loop_stop()
            raise
        if not ok:
            self._client.loop_stop()
            raise MqttError(f"CONNACK refused for {self.client_id}: {rc}")
        return self

    def close(self) -> None:
        try:
            self._client.disconnect()
        finally:
            self._client.loop_stop()
            self.write_transcript()

    def __enter__(self) -> Mqtt5Client:
        return self.connect()

    def __exit__(self, *exc: object) -> None:
        self.close()

    # ---- subscribe / publish ----------------------------------------------------------------
    def subscribe(self, topic_filter: str, qos: int = 1, timeout: float = 5.0) -> list[Any]:
        """Subscribe and wait for SUBACK; returns the reason codes (>= 0x80 = refused)."""
        rc, mid = self._client.subscribe(topic_filter, qos=qos)
        if rc != paho.MQTT_ERR_SUCCESS:
            raise MqttError(f"subscribe({topic_filter}) failed locally: rc={rc}")
        return wait_for_value(
            lambda: self._suback.get(mid), lambda v: v is not None, timeout=timeout, desc=f"SUBACK {topic_filter}"
        )

    def publish(
        self,
        topic: str,
        payload: dict | list | str | bytes,
        *,
        qos: int = 1,
        retain: bool = False,
        correlation_data: bytes | str | None = None,
        message_expiry_s: int | None = None,
        response_topic: str | None = None,
        user_properties: Iterable[tuple[str, str]] = (),
        content_type: str | None = "application/json",
        timeout: float = 5.0,
    ) -> paho.MQTTMessageInfo:
        if isinstance(payload, (dict, list)):
            data = json.dumps(payload).encode()
        elif isinstance(payload, str):
            data = payload.encode()
        else:
            data = payload
        props = Properties(PacketTypes.PUBLISH)
        if content_type:
            props.ContentType = content_type
            props.PayloadFormatIndicator = 1
        if correlation_data is not None:
            props.CorrelationData = correlation_data.encode() if isinstance(correlation_data, str) else correlation_data
        if message_expiry_s is not None:
            props.MessageExpiryInterval = int(message_expiry_s)
        if response_topic:
            props.ResponseTopic = response_topic
        ups = list(user_properties)
        if ups:
            props.UserProperty = ups
        info = self._client.publish(topic, data, qos=qos, retain=retain, properties=props)
        if qos > 0:
            info.wait_for_publish(timeout)
            if not info.is_published():
                raise WaitTimeout(f"no PUBACK within {timeout}s for {topic}")
        return info

    # ---- reading the recording --------------------------------------------------------------
    def messages(self, topic_filter: str | None = None) -> list[ReceivedMessage]:
        with self._lock:
            msgs = list(self._messages)
        if topic_filter is None:
            return msgs
        return [m for m in msgs if paho.topic_matches_sub(topic_filter, m.topic)]

    def mark(self) -> int:
        """Index to pass as `since` so later waits ignore messages received before this point."""
        with self._lock:
            return len(self._messages)

    def wait_for_message(
        self,
        topic_filter: str = "#",
        predicate: Callable[[ReceivedMessage], bool] = lambda m: True,
        *,
        timeout: float,
        since: int = 0,
    ) -> ReceivedMessage:
        def find() -> ReceivedMessage | None:
            with self._lock:
                msgs = self._messages[since:]
            for m in msgs:
                if paho.topic_matches_sub(topic_filter, m.topic) and predicate(m):
                    return m
            return None

        return wait_for_value(find, lambda m: m is not None, timeout=timeout, desc=f"message on {topic_filter}")

    def acks_for(self, command_id: str, topic_filter: str = "ems/v1/+/up/cmd-ack") -> list[dict[str, Any]]:
        cid = command_id.encode()
        out = []
        for m in self.messages(topic_filter):
            body = m.json()
            if m.correlation_data == cid or body.get("command_id") == command_id:
                out.append(body)
        return out

    def wait_for_acks(
        self,
        command_id: str,
        *,
        until: Callable[[list[dict[str, Any]]], bool] | None = None,
        timeout: float = 30.0,
        topic_filter: str = "ems/v1/+/up/cmd-ack",
    ) -> list[dict[str, Any]]:
        """Wait until the ack list for `command_id` satisfies `until` (default: a final state arrived)."""

        def default_until(acks: list[dict[str, Any]]) -> bool:
            return any(is_final_ack_state(a.get("state", "")) for a in acks)

        cond = until or default_until
        return wait_for_value(
            lambda: self.acks_for(command_id, topic_filter),
            cond,
            timeout=timeout,
            desc=f"acks for command {command_id}",
        )

    # ---- artifacts --------------------------------------------------------------------------
    def write_transcript(self) -> None:
        if not self._transcript_path:
            return
        self._transcript_path.parent.mkdir(parents=True, exist_ok=True)
        with self._transcript_path.open("w", encoding="utf-8") as fh:
            for m in self.messages():
                fh.write(json.dumps(m.as_record(), ensure_ascii=False, default=str) + "\n")
