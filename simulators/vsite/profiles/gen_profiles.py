"""Generate the 1-minute day profile used by the virtual site (run once, CSV is committed).

PV: pvlib clear-sky (Ineichen) for Binh Duong, 800 kWp DC on 7 x 100 kW inverters (PVWatts),
then a seeded two-state Markov cloud model. Load: synthetic factory shape (2 shifts) + noise.
Requires: pvlib==0.16.1 pandas numpy (NOT needed inside the vsite image).

    python gen_profiles.py day_binhduong.csv
"""
import sys

import numpy as np
import pandas as pd
import pvlib
from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.pvsystem import PVSystem
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS

LAT, LON = 10.98, 106.65          # Thu Dau Mot, Binh Duong
KWP_DC, N_INV, INV_KW = 800.0, 7, 100.0
DAY = "2026-10-10"
SEED = 20261010


def pv_clear_sky():
    loc = Location(LAT, LON, tz="Asia/Ho_Chi_Minh", altitude=20)
    times = pd.date_range(f"{DAY} 00:00", f"{DAY} 23:59", freq="1min", tz=loc.tz)
    cs = loc.get_clearsky(times, model="ineichen")
    system = PVSystem(
        surface_tilt=10, surface_azimuth=180,
        module_parameters={"pdc0": KWP_DC * 1000, "gamma_pdc": -0.0037},
        inverter_parameters={"pdc0": N_INV * INV_KW * 1000 / 0.96},   # AC cap = 700 kW
        temperature_model_parameters=TEMPERATURE_MODEL_PARAMETERS["sapm"]["open_rack_glass_glass"],
    )
    mc = ModelChain(system, loc, aoi_model="physical", spectral_model="no_loss")
    mc.run_model(cs)
    return times, cs["ghi"], mc.results.ac.clip(lower=0)


def cloud_factor(n, rng):
    """Two-state Markov chain (clear/cloudy) per minute, smoothed -> attenuation in [0.25, 1]."""
    state, out = 0, np.empty(n)
    depth = 0.0
    for i in range(n):
        if state == 0 and rng.random() < 0.05:
            state, depth = 1, rng.uniform(0.35, 0.75)
        elif state == 1 and rng.random() < 0.12:
            state = 0
        out[i] = 1.0 - (depth if state else 0.0)
    kernel = np.ones(5) / 5
    return np.clip(np.convolve(out, kernel, mode="same"), 0.25, 1.0)


def factory_load(times, rng):
    h = times.hour + times.minute / 60.0
    base = np.full(len(h), 220_000.0)                                  # night base (W)
    shift = np.clip((h - 5.5) / 1.0, 0, 1) * np.clip((22.5 - h) / 1.0, 0, 1)
    load = base + 330_000.0 * shift                                    # 2 shifts 06:00-22:00
    load -= 120_000.0 * ((h >= 11.5) & (h < 12.5))                     # lunch break
    load += 40_000.0 * ((h >= 8) & (h < 11.5))                         # morning peak line
    return load * (1 + 0.03 * rng.standard_normal(len(h)))


def main(path):
    rng = np.random.default_rng(SEED)
    times, ghi_cs, p_cs = pv_clear_sky()
    cf = cloud_factor(len(times), rng)
    df = pd.DataFrame({
        "time_local": times.strftime("%H:%M"),
        "ghi_clear": ghi_cs.round(1).values,
        "cloud_factor": cf.round(3),
        "ghi": (ghi_cs.values * cf).round(1),
        "p_pv_ac_w": (p_cs.values * cf).round(0),
        "p_pv_clear_w": p_cs.round(0).values,
        "p_load_w": factory_load(times, rng).round(0),
    })
    df.to_csv(path, index=False)
    e_pv = df.p_pv_ac_w.sum() / 60 / 1000
    e_cs = df.p_pv_clear_w.sum() / 60 / 1000
    print(f"pvlib {pvlib.__version__}: rows={len(df)} peak_clear={df.p_pv_clear_w.max()/1000:.0f} kW "
          f"peak={df.p_pv_ac_w.max()/1000:.0f} kW E_pv={e_pv:.0f} kWh (clear {e_cs:.0f} kWh, "
          f"{e_pv/KWP_DC:.2f} kWh/kWp) E_load={df.p_load_w.sum()/60/1000:.0f} kWh")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "day_binhduong.csv")
