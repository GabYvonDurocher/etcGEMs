#!/usr/bin/env python3
"""P10 TASK 3 -- the three-condition smoothness table on P9's twelve ROUGH lines, P9's rule
applied: SMOOTH if the median sign-change count <= 2 AND no single step exceeds 5 % of its
line's range; ROUGH if the median count >= 5 OR any step exceeds 20 %; else MIXED.
Writes task3_table.csv and task3_verdict.json beside this file."""
import glob, json, os
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
COND = {"baseline (P9)": "lines_baseline_summary.csv", "(a) tie-break only": "lines_tiebreak_summary.csv",
        "(b) variance + support only": None, "(c) both": "lines_both_summary.csv"}
COND["(b) variance + support only"] = [f for f in glob.glob(os.path.join(HERE, "lines_variance*_summary.csv"))][0]


FLAT = 2.0   # D4: a line whose range over +/-1 sd is below 2 units counts as SMOOTH regardless of fraction


def verdict(df):
    med = df.sign_changes.median()
    frac = df.max_jump_frac.where(df.range >= FLAT, 0.0)      # flat lines contribute no fraction
    mx = frac.max()
    if med <= 2 and mx <= 0.05: return "SMOOTH"
    if med >= 5 or mx > 0.20: return "ROUGH"
    return "MIXED"


def main():
    tabs, out = {}, {}
    for cond, f in COND.items():
        p = f if os.path.isabs(f) else os.path.join(HERE, f)
        if not os.path.exists(p): print(f"[t3] {cond}: missing"); continue
        d = pd.read_csv(p).set_index("line"); tabs[cond] = d
        out[cond] = dict(n_lines=int(len(d)), median_sign_changes=float(d.sign_changes.median()), max_sign_changes=int(d.sign_changes.max()),
                         median_jump_units=float(d.max_jump.median()), max_jump_units=float(d.max_jump.max()),
                         median_jump_frac=float(d.max_jump_frac.median()), max_jump_frac=float(d.max_jump_frac.max()),
                         lines_over_20pct=int(((d.max_jump_frac > 0.2) & (d.range >= FLAT)).sum()), lines_over_5pct=int(((d.max_jump_frac > 0.05) & (d.range >= FLAT)).sum()), flat_lines=int((d.range < FLAT).sum()), max_step_units=float(d.max_jump.max()), verdict=verdict(d))
        print(f"[t3] {cond:30s} lines {len(d):2d}  sign changes median {d.sign_changes.median():.0f} max {d.sign_changes.max():2d}  jump units median {d.max_jump.median():6.2f} max {d.max_jump.max():6.2f}  "
              f"frac median {100*d.max_jump_frac.median():5.1f} % max {100*d.max_jump_frac.max():5.1f} %  >20 %: {int((d.max_jump_frac>0.2).sum())}  >5 %: {int((d.max_jump_frac>0.05).sum())}  -> {verdict(d)}", flush=True)
    lines = list(tabs["baseline (P9)"].index); rows = []
    for ln in lines:
        r = dict(line=ln)
        for cond, d in tabs.items():
            if ln in d.index:
                r[f"{cond} | sign changes"] = int(d.loc[ln, "sign_changes"]); r[f"{cond} | max step (units)"] = round(float(d.loc[ln, "max_jump"]), 2); r[f"{cond} | max step (% range)"] = round(100 * float(d.loc[ln, "max_jump_frac"]), 1); r[f"{cond} | range"] = round(float(d.loc[ln, "range"]), 2)
        rows.append(r)
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "task3_table.csv"), index=False)
    json.dump(out, open(os.path.join(HERE, "task3_verdict.json"), "w"), indent=2)
    print("[t3] done")


if __name__ == "__main__":
    main()
