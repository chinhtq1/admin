"""A1 code audit: cheap reproductions of suspected bugs (read-only on product code).
Run: /home/user/admin/.venv/bin/python a1_repro.py
"""
import asyncio, json, os, sys, tempfile, time, types
from pathlib import Path
R = str(Path(__file__).resolve().parents[4])
sys.path[:0] = [f"{R}/simulators/vsite/maps", f"{R}/simulators/vsite", f"{R}/edge/bridge", f"{R}/ingest"]

from regmap import load_maps, load_map, Register
from vsite.model import Bess, Site, Profile
import yaml

def hdr(s): print("\n=== " + s)

# ---------------------------------------------------------------- R1 ess.clock never populated
hdr("R1 ess.clock: map has register, Bess.values() does not")
maps = load_maps(f"{R}/simulators/vsite/maps")
bmap = maps["generic.bess.pcs@0.1.0"]
print("ess.clock in map:", "ess.clock" in bmap.by_point, "| in Bess().values():", "ess.clock" in Bess().values())
from vsite.server import DeviceServer, Faults
ds = DeviceServer("ess-01", bmap, Bess(), 5030, 1, Faults())
regs = [0] * 47
ds.refresh(regs, 0)
clk = bmap.by_point["ess.clock"]
print("ess.clock register words after refresh:", regs[23:25], "-> decoded", clk.decode(regs[23:25])[0])
# poller logic (poller.py:97-99): Reading truthy, value 0 is not None -> ts_src_ms = 0
from bridge.poller import Reading
img = {"ess.clock": Reading(0, "GOOD", 1)}
ts_src = int(img["ess.clock"].value * 1000) if img.get("ess.clock") and img["ess.clock"].value is not None else None
print("poller ts_src_ms =", ts_src)
from datetime import datetime, timezone
print("ingest ts(0) ->", datetime.fromtimestamp(0 / 1000, tz=timezone.utc))
f = Faults(); m = Bess()
print("PUT /faults clock_offset_s on ess-01 applies? hasattr(Bess,'clock_offset_s') =", hasattr(m, "clock_offset_s"))

# ---------------------------------------------------------------- R2 codec silent wrap
hdr("R2 regmap encode silently wraps out-of-range values")
r = Register(point="x", address=0, type="I32")
for v in (2**31 - 1, 2**31, 3_000_000_000):
    print(f"encode({v}) -> decode = {r.decode(r.encode(v))[0]}")
u = Register(point="soc", address=0, type="U16", scale=0.1)
print("U16 scale .1 encode(-5.0) -> decode =", u.decode(u.encode(-5.0))[0])

# ---------------------------------------------------------------- R3 SOC overshoot at high SIM_SPEED
hdr("R3 BESS SOC vs soc_max with lag + large dt_sim (charge at -250 kW)")
for speed in (1, 60, 600):
    b = Bess(soc=93.0)
    b.p_setpoint = -250_000.0
    b._hb_seen_at = float("inf")  # disable watchdog for the experiment
    mx = 0
    for _ in range(20000):
        b.step(0.2, 0.2 * speed)
        mx = max(mx, b.soc)
    print(f"speed x{speed}: max SOC {mx:.3f}% (soc_max {b.soc_max})")

# ---------------------------------------------------------------- R4 bms_derate_w type not validated
hdr("R4 PUT /faults bms_derate_w as string -> physics step raises")
b = Bess(); b.bms_derate_w = "50000"  # __main__.py:82 assigns body value without float()
try:
    b.step(0.2, 0.2); print("no error")
except Exception as e:
    print("Bess.step ->", type(e).__name__, e)

# ---------------------------------------------------------------- R5 watchdog revert + setpoint write
hdr("R5 BESS after watchdog revert: setpoint write executes while state stays 3/alarm set")
import vsite.model as vm
_orig_mono = time.monotonic
t = [1000.0]; vm.time.monotonic = lambda: t[0]  # patch module clock
b = Bess(); b._hb_seen_at = t[0]
b.on_write("ess.p_setpoint", -100_000); b.step(0.2, 0.2)
t[0] += 20; b.step(0.2, 0.2)
print("after 20 s silence: setpoint", b.p_setpoint, "state", b.state, "alarm", hex(b.alarm_word))
b.on_write("ess.p_setpoint", -100_000)
for _ in range(50): t[0] += 0.2; b.step(0.2, 0.2)
print("after setpoint write w/o heartbeat: p", round(b.p), "state", b.state, "alarm", hex(b.alarm_word))
vm.time.monotonic = _orig_mono

# ---------------------------------------------------------------- command handler fakes
from bridge.store import Store
import bridge.commands as bc
from bridge.commands import CommandHandler

class FakeEss:
    def __init__(self):
        self.setpoint = 0.0; self.fail_next = None; self.fail_all = None
        now = int(time.time() * 1000)
        self.image = {"ess.p_charge_max": Reading(250000.0, "GOOD", now), "ess.p_discharge_max": Reading(250000.0, "GOOD", now),
                      "ess.p": Reading(0.0, "GOOD", now)}
    async def write(self, point, value):
        if self.fail_all: return self.fail_all
        if self.fail_next: e, self.fail_next = self.fail_next, None; return e
        if point == "ess.p_setpoint": self.setpoint = value
        return None
    async def read_point(self, point): return self.setpoint

def iso(ms): return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
SEQ = [int(time.time() * 1000)]
def env(p_w, minutes=10, **over):
    now = int(time.time() * 1000); SEQ[0] += 1
    e = {"schema": "ems.command.v1", "command_id": f"cmd-{SEQ[0]}", "seq": SEQ[0], "type": "SET_ESS_P",
         "target": {"edge_id": "edge-vsite01"}, "params": {"p_w": p_w}, "source": "OPERATOR", "danger_class": "C1",
         "valid_from": iso(now), "expires_at": iso(now + int(minutes * 60000)), "sent_at": iso(now),
         "max_latency_ms": 10000, "on_expiry": "REVERT_DEFAULT", "tolerance": {"readback_timeout_s": 2}}
    e.update(over); return e

def acks(store, cid):
    return [json.loads(p)["state"] for (p,) in store.db.execute(
        "SELECT payload FROM outbox WHERE kind='ack' ORDER BY id").fetchall() if json.loads(p)["command_id"] == cid]

async def r6():
    hdr("R6 supersede then write failure: old setpoint stays on device, no expiry task")
    st = Store(tempfile.mktemp(suffix=".sqlite")); ess = FakeEss()
    h = CommandHandler("edge-vsite01", st, None, ess, {"p_charge_max_w": 250000, "p_discharge_max_w": 250000}, 250000)
    a = env(-100000, minutes=0.05)  # A expires in 3 s
    await h.handle(json.dumps(a).encode(), None, int(time.time() * 1000))
    ess.fail_next = "EXC_4"
    b = env(-50000)
    await h.handle(json.dumps(b).encode(), None, int(time.time() * 1000))
    await asyncio.sleep(4)  # past A's expires_at
    print("A acks:", acks(st, a["command_id"]))
    print("B acks:", acks(st, b["command_id"]))
    print("device setpoint after A expired:", ess.setpoint, "| active task cancelled:", h.active["task"].cancelled(), "| active cid == A:", h.active["command_id"] == a["command_id"])

async def r7():
    hdr("R7 readback FAILED_NO_EFFECT path: setpoint written, no lifetime/expiry revert")
    st = Store(tempfile.mktemp(suffix=".sqlite")); ess = FakeEss()
    async def bad_rb(point): return 12345.0
    ess.read_point = bad_rb
    h = CommandHandler("edge-vsite01", st, None, ess, {"p_charge_max_w": 250000, "p_discharge_max_w": 250000}, 250000)
    a = env(-80000, minutes=0.03)
    await h.handle(json.dumps(a).encode(), None, int(time.time() * 1000))
    await asyncio.sleep(2.5)
    print("acks:", acks(st, a["command_id"]), "| device setpoint after expiry:", ess.setpoint, "| active:", h.active)

async def r8():
    hdr("R8 expiry revert write fails -> still EXPIRED + COMPLETED")
    st = Store(tempfile.mktemp(suffix=".sqlite")); ess = FakeEss()
    h = CommandHandler("edge-vsite01", st, None, ess, {"p_charge_max_w": 250000, "p_discharge_max_w": 250000}, 250000)
    orig = asyncio.sleep
    async def fast(s): await orig(min(s, 0.05))
    bc.asyncio.sleep = fast
    try:
        a = env(-70000, minutes=0.01)
        await h.handle(json.dumps(a).encode(), None, int(time.time() * 1000))
        ess.fail_all = "COMM:ConnectionException"
        await orig(1.0)
    finally:
        bc.asyncio.sleep = orig
    print("acks:", acks(st, a["command_id"]), "| device setpoint:", ess.setpoint)

async def r9():
    hdr("R9 malformed envelopes -> no terminal ack (exception swallowed in run())")
    st = Store(tempfile.mktemp(suffix=".sqlite")); ess = FakeEss()
    h = CommandHandler("edge-vsite01", st, None, ess, {"p_charge_max_w": 250000, "p_discharge_max_w": 250000}, 250000)
    cases = {"expires_at garbage": env(-1000, expires_at="tomorrow"), "valid_from garbage": env(-1000, valid_from="x"),
             "danger_class int": env(-1000, danger_class=1), "params list": env(-1000, params=[1]),
             "seq string": env(-1000, seq="abc")}
    for name, e in cases.items():
        try:
            await h.handle(json.dumps(e).encode(), None, int(time.time() * 1000)); err = None
        except Exception as ex:
            err = type(ex).__name__
        print(f"{name:20s} exception={err!s:12s} acks={acks(st, e['command_id'])}")

asyncio.run(r6()); asyncio.run(r7()); asyncio.run(r8()); asyncio.run(r9())

# ---------------------------------------------------------------- ingest
import ingest as ing
class Cur:
    def __init__(self, rows=None, one=("x",)): self.rows, self.one = rows or [], one
    def fetchall(self): return self.rows
    def fetchone(self): return self.one
    def executemany(self, sql, rows): FakeDB.rows.extend(rows)
class Tx:
    def __enter__(self): return self
    def __exit__(self, *a): return False
class FakeDB:
    rows = []; batches = set(); closed = False
    def __init__(self, seqs): self.seqs = seqs
    def transaction(self): return Tx()
    def cursor(self): return Cur()
    def execute(self, sql, params=()):
        if sql.startswith("INSERT INTO telemetry_batch"):
            k = params[:3]
            if k in FakeDB.batches: return Cur(one=None)
            FakeDB.batches.add(k); return Cur(one=(params[2],))
        if sql.startswith("SELECT seq FROM telemetry_batch"):
            return Cur(rows=[(s,) for (e, st, s) in sorted(FakeDB.batches) if (e, st) == params])
        return Cur()
class FakeClient:
    def __init__(self): self.pub = []
    def publish(self, topic, payload, qos=0, properties=None): self.pub.append((topic, json.loads(payload)))

def mk_ingest():
    i = ing.Ingest.__new__(ing.Ingest)
    site = yaml.safe_load(open(f"{R}/infra/config/site.yaml"))
    i.registry = {(e["edge_id"], p["pid"]): (site["site_id"], d["device_id"], p["code"]) for e in site["edges"] for d in e["devices"] for p in d["points"]}
    i.monotonic = {(e["edge_id"], p["pid"]) for e in site["edges"] for d in e["devices"] for p in d["points"] if p["sampling_class"] == "C4" and p.get("monotonic", True)}
    i.last_counter, i.contig, i.above = {}, {}, {}
    i.db = FakeDB([]); i.stats = {"batches": 0, "dups": 0, "rows": 0}; i.client = FakeClient(); i.conn = lambda: i.db
    FakeDB.rows, FakeDB.batches = [], set()
    return i

hdr("R10 ingest trusts payload edge_id, not topic (cross-edge spoof + foreign TELEMETRY_ACK)")
i = mk_ingest()
msg = {"edge_id": "edge-vsite01", "stream": "c1", "seq": 999, "batch_ts": 1, "points": [{"pid": 3001, "ts": 1_000, "avg": 123.0, "q": "GOOD"}]}
i.telemetry("ems/v1/edge-ev01/up/telemetry/c1", msg)   # published by edge-ev01 credentials (ACL allows own up/#)
print("row stored for device:", FakeDB.rows[0][1], FakeDB.rows[0][2], "edge_id col:", FakeDB.rows[0][13])
print("TELEMETRY_ACK published to:", i.client.pub[-1])

hdr("R11 contig init from first-seen seq: first arrival seq 6 -> ack_seq 6 although 1..5 never committed")
i = mk_ingest()
i.telemetry("ems/v1/edge-vsite01/up/telemetry/c1", {"edge_id": "edge-vsite01", "stream": "c1", "seq": 6, "points": []})
print("ack:", i.client.pub[-1][1])
st = Store(tempfile.mktemp(suffix=".sqlite"))
for s in range(1, 7):
    st.enqueue("telemetry", "t", {"seq": s}, {}, stream="c1", seq=s)
print("edge outbox rows deleted by that ack:", st.ack_telemetry("c1", i.client.pub[-1][1]["ack_seq"]), "(seq 1..5 were never stored in cloud)")

hdr("R12 seq hole never acked -> contig stuck, everything above stays in edge outbox")
i = mk_ingest()
for s in (1, 2, 4, 5, 6):
    i.telemetry("ems/v1/edge-vsite01/up/telemetry/c1", {"edge_id": "edge-vsite01", "stream": "c1", "seq": s, "points": []})
print("ack_seq sequence:", [p[1]["ack_seq"] for p in i.client.pub])

hdr("R13 counter check in arrival order: backfill (older, smaller) after live -> false COUNTER_RESET")
i = mk_ingest(); events = []
orig_exec = i.db.execute
def ex(sql, params=()):
    if "COUNTER_RESET" in sql: events.append(json.loads(params[-1]))
    return orig_exec(sql, params)
i.db.execute = ex
i.telemetry("ems/v1/edge-vsite01/up/telemetry/c4", {"edge_id": "edge-vsite01", "stream": "c4", "seq": 3, "points": [{"pid": 3007, "ts": 180_000, "raw": 1300, "q": "GOOD"}]})
i.telemetry("ems/v1/edge-vsite01/up/backfill", {"edge_id": "edge-vsite01", "stream": "c4", "seq": 2, "points": [{"pid": 3007, "ts": 120_000, "raw": 1200, "q": "GOOD"}]})
print("COUNTER_RESET events:", events)

hdr("R14 uplink: malformed TELEMETRY_ACK raises inside paho callback (suppress_exceptions=False)")
from bridge.uplink import Uplink
up = Uplink("edge-vsite01", "127.0.0.1", 1, "u", "p", Store(tempfile.mktemp(suffix=".sqlite")))
print("client.suppress_exceptions =", up.client.suppress_exceptions)
try:
    up._on_message(None, None, types.SimpleNamespace(topic="ems/v1/edge-vsite01/down/config", payload=b'{"type":"TELEMETRY_ACK"}'))
    print("no exception")
except Exception as e:
    print("_on_message ->", type(e).__name__, e)

hdr("R15 aggregator: UNCERTAIN_STALE hold re-labels old value as GOOD with new ts (poller.py:126-127)")
print("see poller.py:126 -> Reading(last.value, 'GOOD', ts)  (code inspection)")
