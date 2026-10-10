"""Virtual site entry point: model + Modbus servers + fault-injection REST API (aiohttp).

    python -m vsite --site /config/site.yaml --maps /app/maps --scenario /app/scenario.yaml
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import os
import time

import yaml
from aiohttp import web

from regmap import load_maps
from vsite.model import Profile, Site
from vsite.server import DeviceServer, Faults

log = logging.getLogger("vsite")


def build(args):
    scenario = yaml.safe_load(open(args.scenario))
    # Environment overrides (docker compose .env): SIM_SPEED, SIM_START_LOCAL
    scenario["clock"]["speed"] = float(os.getenv("SIM_SPEED", scenario["clock"]["speed"]))
    scenario["clock"]["start_local"] = os.getenv("SIM_START_LOCAL", scenario["clock"]["start_local"])
    site_cfg = yaml.safe_load(open(args.site))
    maps = load_maps(args.maps)
    devices = [d for e in site_cfg["edges"] for d in e["devices"] if d["endpoint"].get("host") == args.host_name]
    inv_ids = [d["device_id"] for d in devices if d["driver"].startswith("sunspec.der.inverter")]
    site = Site(scenario, Profile(os.path.join(os.path.dirname(args.scenario), scenario["pv"]["profile_csv"])), inv_ids)
    servers, faults = {}, {}
    for d in devices:
        drv = d["driver"]
        if drv.startswith("sunspec.der.inverter"):
            model = site.inverters[d["device_id"]]
        elif drv.startswith("generic.bess.pcs"):
            model = site.bess
        elif d.get("metering_point") == "MTR_POC":
            model = site.meter_poc
        else:
            model = site.meter_load
        faults[d["device_id"]] = Faults()
        servers[d["device_id"]] = DeviceServer(d["device_id"], maps[drv], model, int(d["endpoint"]["port"]),
                                               int(d["endpoint"]["unit_id"]), faults[d["device_id"]])
    return site, servers, faults


def api(site: Site, servers: dict, faults: dict) -> web.Application:
    routes = web.RouteTableDef()

    @routes.get("/health")
    async def health(_):
        return web.json_response({"ok": True})

    @routes.get("/state")
    async def state(_):
        snap = site.snapshot()
        snap["faults"] = {k: f.active() for k, f in faults.items() if f.active()}
        return web.json_response(snap)

    @routes.put("/faults/{device_id}")
    async def set_fault(req):
        dev = req.match_info["device_id"]
        if dev not in servers:
            return web.json_response({"error": f"unknown device {dev}", "devices": list(servers)}, status=404)
        body = await req.json()
        f, model = faults[dev], servers[dev].model
        for k in ("comm_loss", "exception", "frozen", "sentinel"):
            if k in body:
                setattr(f, k, body[k])
        if "alarm_word" in body:
            model.alarm_word = int(body["alarm_word"])
        if body.get("counter_reset"):
            for attr in ("e_import", "e_export", "e_total", "e_charge", "e_discharge"):
                if hasattr(model, attr):
                    setattr(model, attr, 0.0)
        if "clock_offset_s" in body and hasattr(model, "clock_offset_s"):
            model.clock_offset_s = int(body["clock_offset_s"])
        if "bms_derate_w" in body and hasattr(model, "bms_derate_w"):
            model.bms_derate_w = body["bms_derate_w"]
        log.warning("FAULT %s <- %s (active: %s)", dev, body, f.active())
        return web.json_response({"device_id": dev, "faults": f.active()})

    @routes.delete("/faults/{device_id}")
    async def clear_fault(req):
        dev = req.match_info["device_id"]
        if dev in faults:
            faults[dev].__init__()
            m = servers[dev].model
            if hasattr(m, "alarm_word"):
                m.alarm_word = 0
            if hasattr(m, "clock_offset_s"):
                m.clock_offset_s = 0
            if hasattr(m, "bms_derate_w"):
                m.bms_derate_w = None
        log.warning("FAULT %s cleared", dev)
        return web.json_response({"device_id": dev, "faults": {}})

    @routes.post("/ev")
    async def ev(req):
        """EV charging power reported by the CSMS stub (couples OCPP side into the POC balance)."""
        body = await req.json()
        site.set_ev(float(body.get("p_w", 0)))
        return web.json_response({"p_ev_w": site.p_ev})

    @routes.post("/clock")
    async def clock(req):
        body = await req.json()
        if "speed" in body:
            site.clock.speed = float(body["speed"])
        if "start_local" in body:
            h, m = (int(x) for x in body["start_local"].split(":"))
            site.clock.t_sim = h * 3600 + m * 60
        return web.json_response({"clock_local": site.clock.local_hhmm, "speed": site.clock.speed})

    app = web.Application()
    app.add_routes(routes)
    return app


async def physics(site: Site, period: float = 0.2) -> None:
    last = time.monotonic()
    n = 0
    while True:
        await asyncio.sleep(period)
        now = time.monotonic()
        site.step(now - last)
        last = now
        n += 1
        if n % int(60 / period) == 0:
            s = site.snapshot()
            log.info("t=%s pv=%d load=%d ev=%d ess=%+d (sp %+d, soc %.2f%%) grid=%+d W",
                     s["clock_local"], s["p_pv_w"], s["p_load_w"], s["p_ev_w"], s["ess"]["p_w"],
                     s["ess"]["p_setpoint_w"], s["ess"]["soc_pct"], s["p_grid_w"])


async def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--site", default="/config/site.yaml")
    p.add_argument("--maps", default="/app/maps")
    p.add_argument("--scenario", default="/app/scenario.yaml")
    p.add_argument("--host-name", default=os.getenv("VSITE_HOST_NAME", "vsite"))
    p.add_argument("--api-port", type=int, default=int(os.getenv("VSITE_API_PORT", "8080")))
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    logging.getLogger("pymodbus").setLevel(logging.WARNING)
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)
    site, servers, faults = build(args)
    runner = web.AppRunner(api(site, servers, faults))
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", args.api_port).start()
    log.info("vsite: %d devices, clock %s x%.1f, REST :%d", len(servers), site.clock.local_hhmm,
             site.clock.speed, args.api_port)
    await asyncio.gather(physics(site), *(s.serve() for s in servers.values()))


if __name__ == "__main__":
    asyncio.run(main())
