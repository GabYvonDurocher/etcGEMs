#!/usr/bin/env python3
"""T2 TASK 1 -- is Parsa's configuration-D NLDM theta (MAP and posterior median of his committed chain)
FEASIBLE at every measured temperature? The P3 gate compares R2 over a dense grid and never reads the
likelihood; the -inf rule would only touch a gate point if that point were infeasible somewhere. This
reuses gate_def's own loaders and provider construction (nothing re-implemented) and records the LP
status at the twelve measured temperatures beside the gate's dense grid."""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "reports", "P3_gate")); sys.path.insert(0, os.path.join(ROOT, "src")); os.chdir(ROOT)
import gate_def as G                                   # noqa: E402
from etcgem.gasflux import flux_tpc as _orig           # noqa: E402
MEASURED = [15.0, 20.0, 25.0, 27.0, 30.0, 35.0, 37.0, 40.0, 43.0, 45.0, 47.0, 50.0]
REC = []


def _wrapped(pm, temps, pert, **kw):
    df = _orig(pm, temps, pert, **kw)
    d2 = _orig(pm, MEASURED, pert, metabolites=("o2",))
    REC.append(dict(status=list(map(str, d2["status"])), growth=d2["growth"].round(5).tolist(), o2=d2["o2_uptake"].round(4).tolist(),
                    dense_infeasible=int((df["status"] != "optimal").sum())))
    return df


def main():
    G.flux_tpc = _wrapped
    chains = os.environ.get("PARSA_ROOT", "/Users/g.yvon-durocher/Downloads/etcGEMs-main_3") + "/strains/eciML1515/outputs"
    cdir = os.path.join(chains, "calibration_configD_NLDM_full"); cfg = json.load(open(os.path.join(cdir, "meta.json"))).get("cfg") or {}
    specs = G.build_specs("NLDM", cfg); th_map, th_med, it, nw = G.read_points(cdir)
    gdw = float(G.gas_exchange()["gdw_per_cell"]); etc_e = os.path.join(ROOT, "strains/eciML1515/etc/complexes_szenk_merged_bd.csv")
    out = {}
    for point, th in (("MAP", th_map), ("posterior_median", th_med)):
        for mk in ("NLDM", "NLDM_blanket"):
            REC.clear(); G.predict("NLDM", mk, cfg, th, specs, gdw, etc_e, False)
            r = REC[-1]; out[f"{point}:{mk}"] = r
            print(f"[parsa] D NLDM {point:16s} model={mk:13s} measured-T statuses: {r['status']} | dense non-optimal {r['dense_infeasible']}/{len(G.DENSE)} | growth {r['growth']}", flush=True)
    out["all_measured_optimal"] = all(all(s == "optimal" for s in v["status"]) for k, v in out.items() if ":" in k)
    json.dump(out, open(os.path.join(HERE, "task1_parsa_feasible.json"), "w"), indent=1); print("[parsa] all measured temperatures optimal at every point/medium:", out["all_measured_optimal"])


if __name__ == "__main__":
    main()
