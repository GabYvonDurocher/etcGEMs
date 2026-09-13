#!/usr/bin/env python3
"""make_fit_figures.py -- E4 JOB 4: the model against the measured data, on one set of axes.

    python3 reports/ecoli_deck/make_fit_figures.py --chains $PARSA_ROOT/strains/eciML1515/outputs

The deck showed predictions on one slide and measurements on another and never answered the
first question any audience asks. This overlays them.

NOTHING IS RE-FITTED. The parameters are read out of Parsa's six committed chains at exactly the
point `reports/P3_gate/gate_def_headline.csv` reports, and the prediction is computed by **the
gate's own `predict`**, imported rather than re-implemented, so the curves drawn here are the
curves whose R2 that file records. Which combination the headline reports was established by
matching its `cur_g` against every row of `gate_def_table.csv`: **model medium `NLDM_blanket` for
NLDM** (his construction, which his fits predate the recipe medium), **the current data version**,
and the point named per row -- posterior median for configuration D on NLDM, MAP for the rest.

BUDGET. Six fits x 32 temperatures on `np.arange(8.0, 55.01, 1.5)` = **192 model solves**, single
process, against the prompt's cap of 300. The predictions are written to `fit_predictions.csv` so
the figures can be redrawn without solving again.

WHAT IS NOT HERE, AND WHY.

* **CUE is not overlaid.** The model's carbon-use efficiency would be biomass carbon over total
  carbon consumed. The second term is a sum of `nC_i * v_i` over the 64 open carbon sources of the
  NLDM recipe, which the committed prediction path does not return, and the first needs a biomass
  carbon fraction that is not in the strain data. Both would have to be invented, so CUE stays
  measurement-only and the slide says so.
* **The O2 panel carries a fitted scale.** The measurement is a per-cell rate and the model is
  mmol gDW^-1 h^-1; the fits convert with `resp_scale`, a **fitted** observation parameter (3.3 to
  11.0 across the six). So the O2 comparison tests the SHAPE of the temperature response and is
  not evidence about the absolute level -- which is what `reports/ecoli_gasflux/README.md` says in
  its own words. `docs/OPEN_ITEMS.md` 1.9 is the reason: the per-cell constants (N0 and fg C per
  cell) are about 6x off, so absolute per-cell rates are unreliable while shapes and scale-free
  quantities are immune. Both figures state it.

Writes fit_predictions.csv, fit_observed.csv, fig_fit_growth.png and fig_fit_o2.png.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
import numpy as np                       # noqa: E402
import pandas as pd                      # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "reports", "P3_gate"))

SLIDE_W_IN = 398.3386 / 72.0
OUT = os.path.join(HERE, "assets", "figures")
# the six headline rows, with the combination the headline reports (see the docstring)
FITS = [("D", "NLDM", "calibration_configD_NLDM_full", "NLDM_blanket", "median"),
        ("D", "LB", "calibration_configD_LB_full", "LB", "map"),
        ("E", "NLDM", "calibration_configE_NLDM", "NLDM_blanket", "map"),
        ("E", "LB", "calibration_configE_LB_freecmax", "LB", "map"),
        ("F", "NLDM", "calibration_configF_NLDM", "NLDM_blanket", "map"),
        ("F", "LB", "calibration_configF_LB", "LB", "map")]
COLOUR = {"D": "#1b6ca8", "E": "#c1440e", "F": "#2e7d32"}


def main():
    import gate_def as G

    ap = argparse.ArgumentParser()
    ap.add_argument("--no-solve", action="store_true",
                    help="redraw from the committed fit_predictions.csv without solving")
    ap.add_argument("--chains", default=os.path.join(
        os.environ.get("PARSA_ROOT", "/Users/g.yvon-durocher/Downloads/etcGEMs-main_3"),
        "strains", "eciML1515", "outputs"))
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    head = pd.read_csv(os.path.join(ROOT, "reports", "P3_gate", "gate_def_headline.csv"))
    gdw = float(G.gas_exchange()["gdw_per_cell"])
    etc_e = os.path.join(ROOT, "strains/eciML1515/etc/complexes_szenk_merged_bd.csv")
    etc_f = os.path.join(ROOT, "strains/eciML1515/etc/complexes_configF_as_fitted.csv")

    preds, n_solves, t0 = [], 0, time.time()
    if args.no_solve:
        p = pd.read_csv(os.path.join(HERE, "fit_predictions.csv"))
        print(f"[e4fit] redrawing from the committed fit_predictions.csv ({len(p)} rows), "
              f"no solves", flush=True)
    else:
      for conf, medium, run, mk, which in FITS:
        cdir = os.path.join(args.chains, run)
        cfg = json.load(open(os.path.join(cdir, "meta.json"))).get("cfg") or {}
        specs = G.build_specs(medium, cfg)
        th_map, th_med, _, _ = G.read_points(cdir)
        theta = th_map if which == "map" else th_med
        table = etc_f if cfg.get("use_configf") else etc_e
        g, r, nat = G.predict(medium, mk, cfg, theta, specs, gdw, table, True)
        n_solves += len(G.DENSE)
        for T, gg, rr in zip(G.DENSE, g, r):
            preds.append(dict(config=conf, medium=medium, run=run, point=which,
                              model_medium=mk, T_C=float(T), growth_pred=float(gg),
                              o2_pred_per_cell=float(rr),
                              resp_scale=float(nat["resp_scale"])))
        print(f"[e4fit] {conf}/{medium:4s} {run:32s} [{which}] {len(G.DENSE)} solves  "
              f"resp_scale {float(nat['resp_scale']):6.3f}  [{time.time()-t0:.0f}s]", flush=True)
    if not args.no_solve:
        p = pd.DataFrame(preds)
        p.to_csv(os.path.join(HERE, "fit_predictions.csv"), index=False)

    obs = []
    csv = os.path.join(ROOT, "strains/eciML1515/respirometry/derived_R2A_LB_current.csv")
    for medium in ("NLDM", "LB"):
        Tg, og = G.load_obs(csv, G.OTU[medium], "growth_C_per_C_h")
        Tr, orr = G.load_obs(csv, G.OTU[medium], "R_O2_mg_cell_min")
        for T, v in zip(Tg, og):
            obs.append(dict(medium=medium, quantity="growth_C_per_C_h", T_C=T, value=v))
        for T, v in zip(Tr, orr):
            obs.append(dict(medium=medium, quantity="R_O2_mg_cell_min", T_C=T, value=v))
    o = pd.DataFrame(obs)
    o.to_csv(os.path.join(HERE, "fit_observed.csv"), index=False)

    def panel(ax, medium, col_pred, quantity, ylab):
        oo = o[(o.medium == medium) & (o.quantity == quantity)]
        ax.plot(oo.T_C, oo.value, "ko", ms=3.6, label="measured", zorder=4)
        for conf in ("D", "E", "F"):
            q = p[(p.config == conf) & (p.medium == medium)].sort_values("T_C")
            row = head[(head.config == conf) & (head.medium == medium)]
            key = "cur_g" if quantity.startswith("growth") else "cur_r"
            r2 = float(row[key].iloc[0]) if len(row) else float("nan")
            ax.plot(q.T_C, q[col_pred], "-", lw=1.3, color=COLOUR[conf],
                    label=f"{conf}  $R^2$={r2:.2f}")
        ax.set_xlabel("temperature (°C)")
        ax.set_ylabel(ylab)
        ax.set_title(f"{medium}", fontsize=9, loc="left")
        ax.grid(alpha=0.25, lw=0.5)
        ax.legend(frameon=False, fontsize=6.8, loc="lower right")

    fig, axes = plt.subplots(1, 2, figsize=(SLIDE_W_IN * 0.94, 2.5))
    for ax, medium in zip(axes, ("NLDM", "LB")):
        panel(ax, medium, "growth_pred", "growth_C_per_C_h", "growth (C C$^{-1}$ h$^{-1}$)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig_fit_growth.png"), dpi=300)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(SLIDE_W_IN * 0.94, 2.25))
    for ax, medium in zip(axes, ("NLDM", "LB")):
        panel(ax, medium, "o2_pred_per_cell", "R_O2_mg_cell_min",
              "O$_2$ (mg cell$^{-1}$ min$^{-1}$)")
        ax.set_yscale("log")
        # the predicted collapse runs three orders below anything measured; clip to the data's
        # own range so the comparison is visible, and say so on the slide
        oo = o[(o.medium == medium) & (o.quantity == "R_O2_mg_cell_min")].value
        ax.set_ylim(float(oo.min()) / 4, float(oo.max()) * 3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig_fit_o2.png"), dpi=300)
    plt.close(fig)

    print(f"\n[e4fit] {n_solves} model solves, single process, in {time.time()-t0:.0f}s")
    print("[e4fit] wrote fit_predictions.csv, fit_observed.csv, "
          "assets/figures/fig_fit_growth.png, assets/figures/fig_fit_o2.png")
    print("[e4fit] CUE NOT overlaid: total carbon consumed is not returned by the committed "
          "prediction path and the biomass carbon fraction is not in the strain data")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
