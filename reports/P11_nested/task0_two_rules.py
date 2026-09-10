#!/usr/bin/env python3
"""P11 TASK 0 -- P9's twelve lines under the new floor, read by BOTH rules side by side:
P9's relative rule (a step above 20 % of the line's range) and P11's absolute rule (a step
above 5 log-likelihood units, DECISIONS D0, written before this scan). The growth-term kinks
appear here; they are expected and reported, not fixed. Writes task0_two_rules.csv and
task0_verdict.json beside this file."""
import glob, json, os
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
P10 = os.path.join(ROOT, "reports", "P10_respiration_likelihood")
ABS_LIMIT = 5.0     # D0, written before the scan
REL_LIMIT = 0.20    # P9's rule


def main():
    old = pd.read_csv(os.path.join(P10, "lines_both_summary.csv")).set_index("line")          # floor 0.76
    new = pd.read_csv(os.path.join(HERE, "lines_p11floor_summary.csv")).set_index("line")     # floor 1.42
    base = pd.read_csv(os.path.join(P10, "lines_baseline_summary.csv")).set_index("line")     # P10's pre-fix
    rows = []
    for ln in new.index:
        n, o = new.loc[ln], old.loc[ln]
        rows.append(dict(line=ln, baseline_max_jump=float(base.loc[ln, "max_jump"]),
                         floor076_max_jump=float(o.max_jump), floor076_frac=float(o.max_jump_frac),
                         floor142_max_jump=float(n.max_jump), floor142_frac=float(n.max_jump_frac),
                         floor142_range=float(n["range"]), floor142_sign_changes=int(n.sign_changes),
                         absolute_sampleable=bool(n.max_jump <= ABS_LIMIT),
                         relative_p9_smooth=bool(n.max_jump_frac <= 0.05),
                         relative_p9_rough=bool(n.max_jump_frac > REL_LIMIT)))
    df = pd.DataFrame(rows).sort_values("floor142_max_jump", ascending=False)
    df.to_csv(os.path.join(HERE, "task0_two_rules.csv"), index=False)
    n_abs_fail = int((~df.absolute_sampleable).sum()); n_rel_rough = int(df.relative_p9_rough.sum())
    med_sc = float(df.floor142_sign_changes.median())
    p9_verdict = "SMOOTH" if (med_sc <= 2 and df.floor142_frac.max() <= 0.05) else ("ROUGH" if (med_sc >= 5 or df.floor142_frac.max() > REL_LIMIT) else "MIXED")
    out = dict(absolute_rule="no single 0.05 sd step above 5 log-likelihood units",
               lines=len(df), lines_failing_absolute=n_abs_fail, max_step_units=float(df.floor142_max_jump.max()),
               max_step_line=str(df.iloc[0].line), SAMPLEABLE=bool(n_abs_fail == 0),
               p9_relative_verdict=p9_verdict, lines_over_20pct_relative=n_rel_rough,
               median_sign_changes=med_sc)
    json.dump(out, open(os.path.join(HERE, "task0_verdict.json"), "w"), indent=1)
    print(df[["line", "baseline_max_jump", "floor076_max_jump", "floor142_max_jump", "floor142_frac", "floor142_range", "absolute_sampleable"]].round(3).to_string(index=False), flush=True)
    print(f"\n[t0] ABSOLUTE rule (<= {ABS_LIMIT} units): {len(df)-n_abs_fail} of {len(df)} lines pass; largest step {df.floor142_max_jump.max():.2f} units on {df.iloc[0].line} -> SAMPLEABLE: {n_abs_fail == 0}", flush=True)
    print(f"[t0] P9's RELATIVE rule on the same data: {p9_verdict} ({n_rel_rough} lines above 20 % of range; median sign changes {med_sc:.0f})", flush=True)
    print("[t0] done", flush=True)


if __name__ == "__main__":
    main()
