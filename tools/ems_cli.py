"""EMS PoC CLI — chạy trong container `tools` (docker compose --profile tools run --rm tools ...).

  send-ess-p --p-kw -100 --minutes 10        lệnh SET_ESS_P (âm = sạc), in vòng đời ack
  send-ess-p --p-kw 80 --expired             lệnh đã hết hạn (expires_at trong quá khứ)
  send-ess-p --p-kw 50 --repeat 2            gửi trùng command_id hai lần
  send-ev-limit --amps 10 --minutes 5        SET_EV_LIMIT -> SetChargingProfile
  fault ess-01 --comm-loss | --exception 6 | --frozen | --sentinel | --alarm 0x2104 | --counter-reset
        | --clock-offset -3600 | --bms-derate-kw 50 | --clear
  latest [--device ess-01]                   giá trị mới nhất trong DB
  balance [--minutes 5] [--max-err-pct 3]    kiểm cân bằng công suất tại công tơ POC
  seq-check                                  kiểm lỗ seq theo stream
  coverage                                   có dữ liệu cho PV, BESS, công tơ, EV chưa
  check-ess --expect-p-kw -100               ess.p bám setpoint, SOC đi đúng chiều
  state                                      trạng thái virtual site (REST)
Exit code != 0 khi kiểm tra thất bại (dùng cho tests/smoke.sh).
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone

import paho.mqtt.client as mqtt
import psycopg
from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.properties import Properties

ENV = os.environ.get
DB = ENV("DATABASE_URL", "postgresql://ems:ems@db:5432/ems")
VSITE = ENV("VSITE_URL", "http://vsite:8080")
TERMINAL = {"APPLIED", "APPLIED_CLAMPED", "COMPLETED", "SUPERSEDED"}


def uuid7() -> str:
    ms = int(time.time() * 1000)
    rnd = int.from_bytes(secrets.token_bytes(10), "big")
    v = (ms << 80) | (0x7 << 76) | ((rnd >> 68) & 0xFFF) << 64 | (0b10 << 62) | (rnd & ((1 << 62) - 1))
    h = f"{v:032x}"
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}"


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def db():
    return psycopg.connect(DB, autocommit=True)


def http(method: str, path: str, body: dict | None = None) -> dict:
    req = urllib.request.Request(VSITE + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=5).read())


def publish_command(edge_id: str, env: dict, expiry_s: int | None, repeat: int = 1) -> None:
    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"dispatcher-{secrets.token_hex(3)}", protocol=mqtt.MQTTv5)
    c.username_pw_set("dispatcher", ENV("MQTT_PASSWORD", ""))
    c.connect(ENV("MQTT_HOST", "mosquitto"), int(ENV("MQTT_PORT", "1883")))
    c.loop_start()
    p = Properties(PacketTypes.PUBLISH)
    p.ContentType, p.PayloadFormatIndicator = "application/json", 1
    p.CorrelationData = env["command_id"].encode()
    p.ResponseTopic = f"ems/v1/{edge_id}/up/cmd-ack"
    p.UserProperty = [("schema", "ems.command.v1")]
    if expiry_s is not None:
        p.MessageExpiryInterval = expiry_s                    # = expires_at - sent_at, rounded down (07 §8.2a)
    for _ in range(repeat):
        c.publish(f"ems/v1/{edge_id}/down/cmd", json.dumps(env), qos=1, retain=False, properties=p).wait_for_publish(5)
        time.sleep(0.3)
    c.loop_stop()
    c.disconnect()


def envelope(edge_id: str, ctype: str, params: dict, minutes: float, expired: bool, asset: str, reason: str | None) -> dict:
    now = datetime.now(timezone.utc)
    valid_from, expires = (now - timedelta(minutes=20), now - timedelta(minutes=10)) if expired else \
        (now, now + timedelta(minutes=minutes))
    env = {"schema": "ems.command.v1", "command_id": uuid7(), "seq": int(time.time() * 1000), "type": ctype,
           "target": {"edge_id": edge_id, "site_id": "site-bd-01", "asset_id": asset}, "params": params,
           "source": "OPERATOR", "danger_class": "C1", "issued_by": "user:poc-cli",
           "valid_from": iso(valid_from), "expires_at": iso(expires), "sent_at": iso(now), "max_latency_ms": 10000,
           "on_expiry": "REVERT_DEFAULT", "tolerance": {"abs_w": 1, "readback_timeout_s": 10}, "dry_run": False,
           "kid": "poc-dispatcher", "signature": "UNSIGNED-POC"}
    if reason:
        env["reason"] = reason
    return env


def follow(command_id: str, wait_s: float, until: set[str]) -> list[tuple]:
    """Print the ack lifecycle from the DB until a terminal state (+2 s for trailing duplicate acks)."""
    deadline, seen, done_at = time.time() + wait_s, [], None
    with db() as conn:
        while time.time() < deadline and (done_at is None or time.time() < done_at + 2):
            rows = conn.execute("SELECT state, ts, payload FROM command_ack WHERE command_id=%s ORDER BY id",
                                (command_id,)).fetchall()
            for r in rows[len(seen):]:
                extra = {k: r[2][k] for k in ("reason", "requested", "effective_setpoint", "readback", "measured",
                                               "clamp", "duplicate") if k in r[2]}
                print(f"  {r[1].strftime('%H:%M:%S.%f')[:-3]}  {r[0]:<26} {json.dumps(extra, ensure_ascii=False)}")
            seen = rows
            if done_at is None and rows and (rows[-1][0] in until or rows[-1][0].startswith(("REJECTED", "FAILED"))):
                done_at = time.time()
            time.sleep(0.5)
    return seen


def cmd_send_ess_p(a) -> int:
    edge = "edge-vsite01"
    env = envelope(edge, "SET_ESS_P", {"p_w": int(a.p_kw * 1000)}, a.minutes, a.expired, "ess-01", a.reason)
    if a.danger_class:
        env["danger_class"] = a.danger_class
    expiry = None if a.expired else int((datetime.fromisoformat(env["expires_at"][:-1]) -
                                         datetime.fromisoformat(env["sent_at"][:-1])).total_seconds())
    with db() as conn:
        conn.execute("INSERT INTO command(command_id, edge_id, type, params, envelope, last_state) VALUES(%s,%s,%s,%s,%s,'SENT')",
                     (env["command_id"], edge, env["type"], json.dumps(env["params"]), json.dumps(env)))
    print(f"SET_ESS_P p_w={env['params']['p_w']} command_id={env['command_id']} expires_at={env['expires_at']}"
          f" message_expiry={expiry} repeat={a.repeat}")
    publish_command(edge, env, expiry, a.repeat)
    acks = follow(env["command_id"], a.wait, TERMINAL)
    states = [s for s, _, p in acks if not p.get("duplicate")]
    dup_states = [s for s, _, p in acks if p.get("duplicate")]
    if a.expect:
        ok = a.expect in states
        if a.expect.startswith("REJECTED") and any(s in ("DISPATCHED", "APPLIED", "APPLIED_CLAMPED") for s in states):
            ok = False
        if a.repeat > 1:
            ok = ok and states.count("DISPATCHED") <= 1 and len(dup_states) == a.repeat - 1
            print(f"duplicate check: DISPATCHED x{states.count('DISPATCHED')}, duplicate acks x{len(dup_states)}")
        print("RESULT", "OK" if ok else "FAIL", f"(expected {a.expect})")
        return 0 if ok else 1
    return 0


def cmd_send_ev_limit(a) -> int:
    edge = "edge-ev01"
    env = envelope(edge, "SET_EV_LIMIT", {"i_max_a": a.amps}, a.minutes, False, "evse-01", None)
    print(f"SET_EV_LIMIT i_max_a={a.amps} command_id={env['command_id']}")
    with db() as conn:
        conn.execute("INSERT INTO command(command_id, edge_id, type, params, envelope, last_state) VALUES(%s,%s,%s,%s,%s,'SENT')",
                     (env["command_id"], edge, env["type"], json.dumps(env["params"]), json.dumps(env)))
    publish_command(edge, env, int(a.minutes * 60))
    follow(env["command_id"], a.wait, TERMINAL)
    return 0


def cmd_fault(a) -> int:
    if a.clear:
        print(json.dumps(http("DELETE", f"/faults/{a.device}")))
        return 0
    body = {}
    if a.comm_loss: body["comm_loss"] = True
    if a.exception is not None: body["exception"] = a.exception
    if a.frozen: body["frozen"] = True
    if a.sentinel: body["sentinel"] = True
    if a.alarm is not None: body["alarm_word"] = int(a.alarm, 0)
    if a.counter_reset: body["counter_reset"] = True
    if a.clock_offset is not None: body["clock_offset_s"] = a.clock_offset
    if a.bms_derate_kw is not None: body["bms_derate_w"] = a.bms_derate_kw * 1000
    print(json.dumps(http("PUT", f"/faults/{a.device}", body)))
    return 0


def cmd_latest(a) -> int:
    with db() as conn:
        q = "SELECT device_id, point_code, ts, value, quality, w_s, stream FROM latest_value"
        rows = conn.execute(q + (" WHERE device_id=%s" if a.device else "") + " ORDER BY device_id, point_code",
                            (a.device,) if a.device else ()).fetchall()
    for r in rows:
        v = "NULL" if r[3] is None else f"{r[3]:.3f}"
        print(f"{r[0]:<11} {r[1]:<24} {r[2].strftime('%H:%M:%S')} {v:>16} {r[4]:<14} w={r[5]} {r[6]}")
    return 0 if rows else 1


BALANCE_SQL = """
WITH b AS (
  SELECT date_bin('60 seconds', ts, timestamptz '2000-01-01') AS minute, device_id, point_code,
         avg(value) AS v, count(*) AS k
  FROM telemetry
  WHERE ts > now() - make_interval(mins => %s) AND quality = 'GOOD'
    AND point_code IN ('meter.p', 'pv_inverter.p', 'ess.p', 'evse.p')
  GROUP BY 1, 2, 3)
SELECT minute,
       sum(v) FILTER (WHERE device_id = 'meter-poc')          AS p_grid,
       sum(v) FILTER (WHERE device_id = 'meter-load')         AS p_load,
       sum(v) FILTER (WHERE point_code = 'pv_inverter.p')     AS p_pv,
       sum(v) FILTER (WHERE point_code = 'ess.p')             AS p_ess,
       coalesce(sum(v) FILTER (WHERE point_code = 'evse.p'), 0) AS p_ev
FROM b
GROUP BY minute
HAVING count(*) FILTER (WHERE point_code = 'pv_inverter.p') = 7
   AND max(k) FILTER (WHERE device_id = 'meter-poc') = 12
   AND count(*) FILTER (WHERE device_id = 'meter-load') = 1
ORDER BY minute"""


def cmd_balance(a) -> int:
    with db() as conn:
        rows = conn.execute(BALANCE_SQL, (a.minutes,)).fetchall()
    print("minute(UTC)  P_grid(kW)  P_load  P_ev   P_pv   P_ess  | residual = grid-(load+ev-pv-ess)")
    worst = 0.0
    for m, g, l, pv, e, ev in rows:
        res = g - (l + ev - pv - e)
        pct = abs(res) / max(l, 1) * 100
        worst = max(worst, pct)
        print(f"{m.strftime('%H:%M')}     {g/1e3:9.1f} {l/1e3:7.1f} {ev/1e3:5.1f} {pv/1e3:6.1f} {e/1e3:7.1f}  | {res/1e3:+7.2f} kW ({pct:.2f}% of load)")
    ok = bool(rows) and worst <= a.max_err_pct
    print("RESULT", "OK" if ok else "FAIL", f"({len(rows)} complete minute(s), worst residual {worst:.2f}% <= {a.max_err_pct}%)")
    return 0 if ok else 1


def cmd_seq_check(a) -> int:
    """No seq gaps per (edge, stream) and backfill arrived in seq order (07 §6.10, §6.12)."""
    sql = """SELECT edge_id, stream, count(*) AS batches, min(seq), max(seq), max(seq)-min(seq)+1-count(*) AS gaps,
                    count(*) FILTER (WHERE topic LIKE '%%/up/backfill') AS via_backfill,
                    min(seq) FILTER (WHERE topic LIKE '%%/up/backfill') AS bf_min,
                    max(seq) FILTER (WHERE topic LIKE '%%/up/backfill') AS bf_max
             FROM telemetry_batch WHERE ts_ingest > now() - make_interval(mins => %s) GROUP BY 1, 2 ORDER BY 1, 2"""
    order_sql = """SELECT count(*) FROM (
             SELECT seq < lag(seq) OVER (PARTITION BY edge_id, stream ORDER BY arrival) AS backwards
             FROM telemetry_batch WHERE topic LIKE '%%/up/backfill' AND ts_ingest > now() - make_interval(mins => %s)) x
             WHERE backwards"""
    with db() as conn:
        rows = conn.execute(sql, (a.minutes,)).fetchall()
        backwards = conn.execute(order_sql, (a.minutes,)).fetchone()[0]
    print("edge_id       stream batches  min_seq  max_seq  gaps  via_backfill  backfill_seq_range")
    bad = 0
    for r in rows:
        rng = f"{r[7]}..{r[8]}" if r[6] else "-"
        print(f"{r[0]:<13} {r[1]:<6} {r[2]:>7} {r[3]:>8} {r[4]:>8} {r[5]:>5} {r[6]:>12}  {rng}")
        bad += r[5] if r[0] == "edge-vsite01" else 0      # edge-ev01 (CSMS stub) has no store-and-forward
    print(f"backfill batches arrived out of seq order: {backwards}")
    ok = bool(rows) and bad == 0 and backwards == 0
    print("RESULT", "OK" if ok else "FAIL", "(edge-vsite01: no gaps, ordered backfill)")
    return 0 if ok else 1


def cmd_check_ess(a) -> int:
    """Measured ess.p tracks the setpoint and SOC moves in the expected direction (last N c1 windows)."""
    sql = """SELECT ts, point_code, value FROM telemetry WHERE device_id='ess-01' AND quality='GOOD'
             AND point_code IN ('ess.p','ess.soc') AND ts > now() - make_interval(secs => %s) ORDER BY ts"""
    with db() as conn:
        rows = conn.execute(sql, (a.seconds,)).fetchall()
    p = [(t, v) for t, c, v in rows if c == "ess.p"]
    soc = [(t, v) for t, c, v in rows if c == "ess.soc"]
    if len(p) < 2 or len(soc) < 2:
        print("RESULT FAIL (not enough ess windows)")
        return 1
    p_last, d_soc = p[-1][1], soc[-1][1] - soc[0][1]
    print(f"ess.p last 5 s window avg = {p_last/1e3:+.1f} kW (expect {a.expect_p_kw:+.1f} ± {a.tol_kw} kW)")
    print(f"ess.soc {soc[0][0].strftime('%H:%M:%S')} {soc[0][1]:.3f}% -> {soc[-1][0].strftime('%H:%M:%S')} {soc[-1][1]:.3f}%"
          f" (delta {d_soc:+.3f} %)")
    ok = abs(p_last / 1e3 - a.expect_p_kw) <= a.tol_kw
    if a.expect_p_kw < 0:
        ok = ok and d_soc > 0
    elif a.expect_p_kw > 0:
        ok = ok and d_soc < 0
    print("RESULT", "OK" if ok else "FAIL")
    return 0 if ok else 1


def cmd_coverage(a) -> int:
    sql = """SELECT point_code, count(*), count(DISTINCT device_id), max(ts)
             FROM telemetry WHERE ts > now() - make_interval(mins => %s)
               AND point_code IN ('pv_inverter.p','ess.p','ess.soc','meter.p','meter.e_import','evse.p','evse.e_session')
             GROUP BY 1 ORDER BY 1"""
    with db() as conn:
        rows = conn.execute(sql, (a.minutes,)).fetchall()
    for r in rows:
        print(f"{r[0]:<18} rows={r[1]:<5} devices={r[2]} last={r[3].strftime('%H:%M:%S')}")
    need = {"pv_inverter.p", "ess.p", "ess.soc", "meter.p", "evse.p"}
    missing = need - {r[0] for r in rows}
    print("RESULT", "OK" if not missing else f"FAIL missing {sorted(missing)}")
    return 0 if not missing else 1


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("send-ess-p"); s.add_argument("--p-kw", type=float, required=True)
    s.add_argument("--minutes", type=float, default=10); s.add_argument("--expired", action="store_true")
    s.add_argument("--repeat", type=int, default=1); s.add_argument("--wait", type=float, default=20)
    s.add_argument("--expect"); s.add_argument("--reason"); s.add_argument("--danger-class")
    s = sub.add_parser("send-ev-limit"); s.add_argument("--amps", type=float, required=True)
    s.add_argument("--minutes", type=float, default=5); s.add_argument("--wait", type=float, default=20)
    s = sub.add_parser("fault"); s.add_argument("device")
    for f in ("--comm-loss", "--frozen", "--sentinel", "--counter-reset", "--clear"):
        s.add_argument(f, action="store_true")
    s.add_argument("--exception", type=int); s.add_argument("--alarm"); s.add_argument("--clock-offset", type=int)
    s.add_argument("--bms-derate-kw", type=float)
    s = sub.add_parser("latest"); s.add_argument("--device")
    s = sub.add_parser("balance"); s.add_argument("--minutes", type=int, default=5); s.add_argument("--max-err-pct", type=float, default=3.0)
    s = sub.add_parser("seq-check"); s.add_argument("--minutes", type=int, default=30)
    s = sub.add_parser("coverage"); s.add_argument("--minutes", type=int, default=10)
    s = sub.add_parser("check-ess"); s.add_argument("--expect-p-kw", type=float, required=True)
    s.add_argument("--tol-kw", type=float, default=5.0); s.add_argument("--seconds", type=int, default=40)
    sub.add_parser("state")
    a = p.parse_args()
    if a.cmd == "state":
        print(json.dumps(http("GET", "/state"), indent=1))
        return 0
    return {"send-ess-p": cmd_send_ess_p, "send-ev-limit": cmd_send_ev_limit, "fault": cmd_fault, "latest": cmd_latest,
            "balance": cmd_balance, "check-ess": cmd_check_ess, "seq-check": cmd_seq_check, "coverage": cmd_coverage}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
