import sys, uuid
from pathlib import Path
R = str(Path(__file__).resolve().parents[4]); sys.path[:0]=[f"{R}/tools", f"{R}/edge/bridge", f"{R}/simulators/vsite/maps"]
import ems_cli
bad=[u for u in (ems_cli.uuid7() for _ in range(2000)) if uuid.UUID(u).version!=7 or uuid.UUID(u).variant!=uuid.RFC_4122]
print("R16 uuid7: 2000 generated, invalid version/variant:", len(bad))
from bridge.aggregate import Aggregator
from bridge.poller import Reading
a=Aggregator(); pt={"pid":1,"sampling_class":"C1"}
for t in (10_000,11_000,12_000): a.add(pt, Reading(1.0,"GOOD",t))
a.add(pt, Reading(5.0,"GOOD",4_000))  # wall clock stepped back 8 s
out=a.flush(100_000)
print("R17 clock step back: samples emitted:", out)
a=Aggregator(); 
for t in range(0,5000,1000): a.add(pt, Reading(None,"BAD_COMM",t))
print("R18 all-BAD window:", a.flush(10_000))
a=Aggregator()
a.add(pt, Reading(2.0,"GOOD",0)); a.add(pt, Reading(None,"BAD_COMM",1000))
print("R19 partial window:", a.flush(10_000))
