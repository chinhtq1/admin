"""Command validation + ack lifecycle for SET_ESS_P (07 §8.2–§8.7). PoC scope, see README.

States published on up/cmd-ack (Correlation Data = command_id):
RECEIVED -> ACCEPTED -> DISPATCHED -> APPLIED | APPLIED_CLAMPED | FAILED_*   ... -> EXPIRED -> COMPLETED
or RECEIVED -> REJECTED_{INVALID, STALE, OUT_OF_LIMIT, REPLAY, INTERLOCK:IL-04};  SUPERSEDED by a newer one.
Not implemented in the PoC: JWS signature check (A.1), clock-sync interlock (IL-06), arbiter levels.
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import datetime

from bridge.store import now_ms

log = logging.getLogger("bridge.cmd")

MAX_SETPOINT_DURATION_S = 3600         # 07 §8.2: setpoint max 1 h
STALE_BMS_MS = 5000                    # 07 §6.6: T_stale_bms


def parse_ts(s: str) -> int:
    return int(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() * 1000)


class CommandHandler:
    def __init__(self, edge_id: str, store, uplink, ess_poller, soe: dict, rated_w: float):
        self.edge_id, self.store, self.uplink, self.ess = edge_id, store, uplink, ess_poller
        self.soe, self.rated_w = soe, rated_w
        self.active: dict | None = None            # {"command_id", "effective", "expires_ms", "task"}
        self.queue: asyncio.Queue = asyncio.Queue()

    # ---- ack ------------------------------------------------------------------------
    def ack(self, env: dict, state: str, **extra) -> dict:
        cid = env.get("command_id", "unknown")
        payload = {"schema": "ems.cmd-ack.v1", "edge_id": self.edge_id, "command_id": cid, "state": state,
                   "ts": now_ms(), **extra}
        self.store.enqueue("ack", f"ems/v1/{self.edge_id}/up/cmd-ack", payload,
                           {"content_type": "application/json", "payload_format_indicator": 1,
                            "correlation_data": cid, "user_properties": {"schema": "ems.cmd-ack.v1"}})
        self.store.put_command(cid, state, env, payload, env.get("_expires_ms"))
        log.info("ack %s %s %s", cid[:13], state, {k: v for k, v in extra.items() if k in ("reason", "effective_setpoint")})
        return payload

    def event(self, etype: str, detail: dict) -> None:
        seq = self.store.next_seq("event")
        ev = {"event_id": f"{self.edge_id}-ev-{seq}", "type": etype, "ts": now_ms(), "device_id": "ess-01", **detail}
        self.store.enqueue("event", f"ems/v1/{self.edge_id}/up/event",
                           {"schema": "ems.event.v1", "edge_id": self.edge_id, "seq": seq, "events": [ev]},
                           {"content_type": "application/json", "payload_format_indicator": 1,
                            "user_properties": {"schema": "ems.event.v1", "edge_seq": seq}})

    # ---- intake (called from paho thread) -------------------------------------------
    def submit(self, loop, payload: bytes, props) -> None:
        loop.call_soon_threadsafe(self.queue.put_nowait, (payload, props, now_ms()))

    async def run(self) -> None:
        while True:
            payload, props, rx_ms = await self.queue.get()
            try:
                await self.handle(payload, props, rx_ms)
            except Exception:
                log.exception("command handling failed")

    async def handle(self, payload: bytes, props, rx_ms: int) -> None:
        try:
            env = json.loads(payload)
            cid = env["command_id"]
        except (ValueError, KeyError, TypeError):
            log.error("SECURITY: unparseable command dropped")
            return
        corr = getattr(props, "CorrelationData", b"") or b""
        rt = getattr(props, "ResponseTopic", None)
        mei = getattr(props, "MessageExpiryInterval", None)
        if rt and rt != f"ems/v1/{self.edge_id}/up/cmd-ack":
            log.warning("SECURITY: foreign Response Topic %s ignored (07 §8.2a)", rt)
        # A.4 idempotency: command_id already seen -> report old state, do not execute again
        seen = self.store.get_command(cid)
        if seen:
            last = json.loads(seen[1]) if seen[1] else {}
            log.warning("duplicate command_id %s -> not executed again (state %s)", cid[:13], seen[0])
            self.ack(env, seen[0], duplicate=True, reason="DUPLICATE_COMMAND_ID",
                     **{k: last[k] for k in ("requested", "effective_setpoint") if k in last})
            return
        env["_expires_ms"] = parse_ts(env["expires_at"]) if env.get("expires_at") else None
        self.ack(env, "RECEIVED", mqtt={"correlation_data_ok": corr.decode(errors="replace") == cid,
                                       "message_expiry_remaining_s": mei})
        verdict = self.validate(env, rx_ms)
        if verdict:
            self.ack(env, verdict[0], reason=verdict[1], requested=env.get("params"))
            return
        await self.execute(env)

    # ---- 07 §8.7 checks --------------------------------------------------------------
    def validate(self, env: dict, rx_ms: int) -> tuple[str, str] | None:
        # A.2 target
        if env.get("target", {}).get("edge_id") != self.edge_id:
            return "REJECTED_INVALID", "TARGET_MISMATCH"
        # A.3 structure / class
        required = ("schema", "command_id", "seq", "type", "params", "source", "danger_class", "valid_from",
                    "expires_at", "sent_at", "max_latency_ms", "on_expiry")
        missing = [k for k in required if k not in env]
        if missing:
            return "REJECTED_INVALID", f"MISSING_FIELDS:{','.join(missing)}"
        if env["type"] != "SET_ESS_P":
            return "REJECTED_UNSUPPORTED", f"TYPE_NOT_IN_POC:{env['type']}"
        if set(env["params"]) != {"p_w"} or not isinstance(env["params"]["p_w"], (int, float)):
            return "REJECTED_INVALID", "PARAMS"
        valid_from, expires = parse_ts(env["valid_from"]), env["_expires_ms"]
        if expires - valid_from > MAX_SETPOINT_DURATION_S * 1000:
            return "REJECTED_INVALID", "DURATION_GT_1H"
        p_w = float(env["params"]["p_w"])
        min_class = "C2" if abs(p_w) > 0.8 * self.rated_w else "C1"
        if env["danger_class"] < min_class or (env["danger_class"] >= "C2" and not env.get("reason")):
            return "REJECTED_INVALID", f"DANGER_CLASS_MIN_{min_class}"
        # A.4 anti-replay (seq per signer)
        if not self.store.check_and_set_signer_seq(env.get("kid", "unsigned"), int(env["seq"])):
            return "REJECTED_REPLAY", "SEQ_NOT_INCREASING"
        # B. safe-ify path: SET_ESS_P p_w = 0 skips the operational checks
        if p_w == 0:
            env["_safe_path"] = True
            return None
        # C.7 validity window + latency
        now = now_ms()
        if not (valid_from <= now <= expires):
            return "REJECTED_STALE", "OUTSIDE_VALIDITY_WINDOW" if now < expires else "EXPIRED_BEFORE_EXECUTION"
        if rx_ms - parse_ts(env["sent_at"]) > int(env["max_latency_ms"]):
            return "REJECTED_STALE", "MAX_LATENCY_EXCEEDED"
        # C.11 static SOE limits -> reject; dynamic BMS limits -> clamp later
        if p_w > self.soe["p_discharge_max_w"] or -p_w > self.soe["p_charge_max_w"]:
            return "REJECTED_OUT_OF_LIMIT", "OUTSIDE_SOE"
        for code in ("ess.p_charge_max", "ess.p_discharge_max"):
            rd = self.ess.image.get(code)
            if rd is None or rd.value is None or now - rd.ts_ms > STALE_BMS_MS:
                return "REJECTED_INTERLOCK:IL-04", f"STALE_BMS:{code}"
        return None

    # ---- execution ------------------------------------------------------------------
    async def execute(self, env: dict) -> None:
        p_req = float(env["params"]["p_w"])
        pch = self.ess.image["ess.p_charge_max"].value if "ess.p_charge_max" in self.ess.image else 0
        pdis = self.ess.image["ess.p_discharge_max"].value if "ess.p_discharge_max" in self.ess.image else 0
        effective = max(-(pch or 0), min(pdis or 0, p_req)) if not env.get("_safe_path") else 0.0
        clamp = None
        if effective != p_req:
            src = "ess.p_discharge_max" if p_req > 0 else "ess.p_charge_max"
            clamp = {"code": "CLAMPED_BY_BMS", "limit_w": abs(effective), "source_point": src}
        self.ack(env, "ACCEPTED", requested={"p_w": p_req}, effective_setpoint={"p_w": effective},
                 **({"safe_path": True} if env.get("_safe_path") else {}))
        if self.active and self.active["command_id"] != env["command_id"]:
            old = self.active
            old["task"].cancel()
            self.ack(old["env"], "SUPERSEDED", superseded_by=env["command_id"])
        err = await self.ess.write("ess.p_setpoint", effective)
        if err:
            self.ack(env, "FAILED_DEVICE_EXCEPTION", reason=err)
            return
        self.ack(env, "DISPATCHED", effective_setpoint={"p_w": effective})
        tol = env.get("tolerance", {})
        timeout_s = float(tol.get("readback_timeout_s", 10))
        deadline = time.monotonic() + timeout_s
        rb = None
        while time.monotonic() < deadline:                       # 07 §8.5 (1) readback of the setpoint register
            rb = await self.ess.read_point("ess.p_setpoint")
            if rb is not None and abs(rb - effective) <= 1:       # ±1 LSB
                break
            await asyncio.sleep(0.5)
        else:
            self.ack(env, "FAILED_TIMEOUT" if rb is None else "FAILED_NO_EFFECT", readback={"point": "ess.p_setpoint", "value": rb})
            return
        meas = self.ess.image.get("ess.p")
        state = "APPLIED_CLAMPED" if clamp else "APPLIED"
        self.ack(env, state, requested={"p_w": p_req}, effective_setpoint={"p_w": effective},
                 **({"clamp": clamp} if clamp else {}),
                 readback={"point": "ess.p_setpoint", "value": rb, "ts": now_ms()},
                 measured={"point": "ess.p", "value": meas.value if meas else None, "ts": meas.ts_ms if meas else None})
        task = asyncio.create_task(self.lifetime(env, effective))
        self.active = {"command_id": env["command_id"], "env": env, "effective": effective, "task": task}

    async def lifetime(self, env: dict, effective: float) -> None:
        """07 §8.5 (2) response tracking, then §8.6 expiry -> on_expiry REVERT_DEFAULT."""
        try:
            await asyncio.sleep(8)
            meas = self.ess.image.get("ess.p")
            tol_w = max(0.02 * self.rated_w, 1000.0)
            if meas and meas.value is not None:
                dev = abs(meas.value - effective)
                self.event("CTRL.TRACKING_OK" if dev <= tol_w else "CTRL.TRACKING_DEVIATION",
                           {"command_id": env["command_id"], "setpoint_w": effective, "measured_w": meas.value,
                            "tolerance_w": tol_w, "q": meas.q})
            wait_s = (env["_expires_ms"] - now_ms()) / 1000.0
            if wait_s > 0:
                await asyncio.sleep(wait_s)
            await self.ess.write("ess.p_setpoint", 0.0)
            self.ack(env, "EXPIRED", on_expiry=env.get("on_expiry", "REVERT_DEFAULT"))
            self.ack(env, "COMPLETED", effective_setpoint={"p_w": 0})
            if self.active and self.active["command_id"] == env["command_id"]:
                self.active = None
        except asyncio.CancelledError:
            pass

    def active_commands(self) -> list[dict]:
        if not self.active:
            return []
        e = self.active["env"]
        return [{"command_id": e["command_id"], "state": "ACTIVE", "expires_at": e["expires_at"],
                 "effective_setpoint": {"p_w": self.active["effective"]}}]
