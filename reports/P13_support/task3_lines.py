#!/usr/bin/env python3
"""P13 TASK 3 -- P11's twelve lines, re-scanned at p38 under `current` and `clamp`.

The absolute rule, unchanged from P11: a line is SAMPLEABLE if no single 0.05 sd step exceeds
5 log-likelihood units; the surface is SAMPLEABLE if every line is. Reported beside P11's own
numbers at theta_A so the reader can separate "the scheme changed it" from "the centre changed it"
-- which is why `current` is re-run at p38 too rather than quoting P11's table for both.
"""
import json, os, sys, time
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from common13 import p12_points, NAMES, ROOT                      # noqa: E402
from task3_worker import scan, SCHEMES                            # noqa: E402

P9 = os.path.join(ROOT, "reports", "P9_surface")
LINES = ["axis:topt_scale", "axis:dCp_scale", "axis:kcat_scale", "axis:f_maint", "axis:ngam_scale",
         "axis:clearance_mult", "PC1", "PC2", "PC3", "random1", "random2", "random3"]
RULE = 5.0
COLD = 25.0      # a step "carried by the cold end" is one whose minimum growth sits at <= 25 C


def main():
    meta = json.load(open(os.path.join(P9, "task1_meta.json")))
    sd = np.array(meta["sd"]); names = meta["names"]
    pts, _ = p12_points(); theta0 = pts["p38(b22)"]
    tasks = [(l, s, theta0.tolist(), sd.tolist(), names) for s in SCHEMES for l in LINES]
    print(f"[t3] {len(tasks)} scans ({len(LINES)} lines x {len(SCHEMES)} schemes), 41 points each, "
          f"fresh model per evaluation, centred on p38", flush=True)
    from multiprocessing import Pool
    rows, t0 = [], time.time()
    with Pool(8) as pool:
        for lname, scheme, out, w in pool.imap_unordered(scan, tasks):
            rows.extend(out)
            pd.DataFrame(rows).to_csv(os.path.join(HERE, "task3_lines.csv"), index=False)
            print(f"[t3] {scheme:8s} {lname:22s} done ({w/60:.1f} min)  [{len(rows)//41}/{len(tasks)}]",
                  flush=True)
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "task3_lines.csv"), index=False)
    p11 = pd.read_csv(os.path.join(ROOT, "reports", "P11_nested", "lines_p11floor_summary.csv"))
    p11m = dict(zip(p11.line, p11.max_jump))
    summ = []
    for s in SCHEMES:
        for l in LINES:
            d = df[(df.scheme == s) & (df.line == l)].sort_values("step_sd")
            y = d.logL.to_numpy(); st = np.abs(np.diff(y)); i = int(np.argmax(st))
            summ.append(dict(scheme=s, line=l, max_step=float(st.max()),
                             at_step_sd=float(d.step_sd.to_numpy()[i]),
                             rng=float(y.max() - y.min()),
                             T_at_max_step=float(d.T_min_growth.to_numpy()[i]),
                             n_infeasible_max=int(d.n_infeasible.max()),
                             n_below_mask_max=int(d.n_below_mask.max()),
                             p11_max_jump_at_thetaA=float(p11m.get(l, np.nan)),
                             sampleable=bool(st.max() <= RULE)))
    S = pd.DataFrame(summ); S.to_csv(os.path.join(HERE, "task3_lines_summary.csv"), index=False)
    pd.set_option("display.width", 240)
    for s in SCHEMES:
        d = S[S.scheme == s]
        print(f"\n[t3] === {s.upper()} at p38 ===")
        print(d[["line", "max_step", "at_step_sd", "rng", "T_at_max_step", "n_infeasible_max",
                 "n_below_mask_max", "p11_max_jump_at_thetaA", "sampleable"]].round(4).to_string(index=False))
        bad = d[~d.sampleable]
        print(f"[t3] {s}: largest step {d.max_step.max():.4f}; "
              f"{'SAMPLEABLE (every line <= 5)' if len(bad) == 0 else '*** NOT SAMPLEABLE: ' + ','.join(bad.line) + ' ***'}")
        cold = d[d.T_at_max_step <= COLD]
        print(f"[t3] {s}: cold-carried lines (min growth at <= {COLD:.0f} C): "
              f"{len(cold)} of {len(d)}, largest step among them "
              f"{cold.max_step.max() if len(cold) else float('nan'):.4f}")
    json.dump(dict(rule=RULE, wall_h=round((time.time() - t0) / 3600, 2),
                   max_step={s: float(S[S.scheme == s].max_step.max()) for s in SCHEMES},
                   sampleable={s: bool(S[S.scheme == s].sampleable.all()) for s in SCHEMES}),
              open(os.path.join(HERE, "task3_lines_verdict.json"), "w"), indent=1)
    print(f"\n[t3] {(time.time()-t0)/3600:.2f} h")
    print("[t3] done", flush=True)


if __name__ == "__main__":
    main()
