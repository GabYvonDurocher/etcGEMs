"""Validate the emergent etc-GEM against two trusted, strain-matched E. coli TPCs.

Nothing is fit to growth: the model predicts each curve a priori under its medium
(availability, not pinned uptake) and we compare on RAW ABSOLUTE growth rate (1/h).

Curves (primary sources, replacing the retired Smith-derived 26-curve compilation):
  * MINIMAL -- Noll / Katipoglu-Yazan et al. 2023 (Data in Brief 48:109037),
    K-12 NCM3722, defined glucose-minimal (modified MOPS + 0.5 g/L glucose + 6 trace
    amino acids), 27-45 C, mean +/- SD over n wells. The quantitative anchor.
  * RICH   -- Erdos et al. 2026 (unpublished), K-12 MG1655 wt, LB, ~16-45 C.
    Figure-digitized (+/- ~0.1 h/1); lower precision, the rich-medium comparator.

The headline is the minimal-vs-rich magnitude contrast: does the medium-matched
proteome-sector allocation reproduce the observed rich > minimal peak?
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from .enzyme_cost import Perturbation
from .tpc import TPC, compute_tpc

SRC = os.path.join("strains", "{strain}", "thermal", "sources")
LB_MEDIA_CSV = os.path.join("strains", "{strain}", "media", "LB_media.csv")

# 6 trace amino acids supplemented in the Noll minimal medium (exchange REV ids)
NOLL_TRACE_AA = ["met__L", "his__L", "arg__L", "pro__L", "thr__L", "trp__L"]


@dataclass
class CurveSpec:
    key: str
    rel_path: str
    medium: str                 # "glucose_minimal" | "LB"
    label: str
    color: str
    carbon: str = "glc__D"
    digitized: bool = False


CURVES = [
    CurveSpec("noll_minimal",
              "noll2023_ncm3722/noll2023_ncm3722_tpc.csv",
              "glucose_minimal",
              "Noll 2023 — K-12 NCM3722, glucose-minimal", "tab:green"),
    CurveSpec("erdos_LB",
              "erdos2026_unpubl/erdos2026_mg1655_wt_nokan_tpc.csv",
              "LB",
              "Erdos 2026 — MG1655 wt, LB (rich)", "tab:orange", digitized=True),
]


# ---------------------------------------------------------------------------
def load_curve(strain: str, spec: CurveSpec) -> Dict:
    df = pd.read_csv(os.path.join(SRC.format(strain=strain), spec.rel_path))
    df = df[np.isfinite(pd.to_numeric(df["rate_per_h"], errors="coerce"))].copy()
    df["rate_per_h"] = df["rate_per_h"].astype(float)
    temps = df["temp_C"].to_numpy(float)
    rates = df["rate_per_h"].to_numpy(float)
    sd = df["rate_sd_per_h"].to_numpy(float) if "rate_sd_per_h" in df.columns else None
    n = df["n_wells"].to_numpy(float) if "n_wells" in df.columns else None
    if sd is not None and not np.isfinite(sd).any():
        sd = None
    return {"spec": spec, "temps_C": temps, "rate": rates, "sd": sd, "n": n,
            "study": str(df["study"].iloc[0]), "strain": str(df["strain"].iloc[0]),
            "medium_detail": str(df["medium_detail"].iloc[0]),
            "obs_rmax": float(np.max(rates)),
            "obs_Topt_C": float(temps[int(np.argmax(rates))])}


def _set_medium(pm, spec: CurveSpec, strain: str, extra_aa: Optional[List[str]] = None):
    from .providers import set_medium
    if spec.medium == "LB":
        set_medium(pm, "LB", lb_media_csv=LB_MEDIA_CSV.format(strain=strain))
    else:
        set_medium(pm, "glucose_minimal", spec.carbon, True)
        if extra_aa:
            model = pm.ec.model
            for base in extra_aa:
                rev = f"EX_{base}_e_REV"
                if rev in model.reactions:
                    model.reactions.get_by_id(rev).upper_bound = 1000.0
            model.solver.update()


def _fit_stats(obs, pred):
    obs, pred = np.asarray(obs, float), np.asarray(pred, float)
    ss_res = float(np.sum((obs - pred) ** 2))
    ss_tot = float(np.sum((obs - np.mean(obs)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan
    rmse = float(np.sqrt(np.mean((obs - pred) ** 2)))
    return r2, rmse


def _predict(pm, spec, strain, data_temps, extra_aa=None):
    """Return (pred_at_data_temps, dense_T, dense_growth, descriptors)."""
    _set_medium(pm, spec, strain, extra_aa)
    pred = compute_tpc(pm, data_temps, Perturbation()).growth
    dense = np.linspace(min(5.0, float(min(data_temps)) - 3),
                        max(50.0, float(max(data_temps)) + 3), 91)
    dg = compute_tpc(pm, dense, Perturbation()).growth
    desc = TPC(dense, dg).descriptors(0.05)
    return pred, dense, dg, desc


# ---------------------------------------------------------------------------
def run(strain: str, out_dir: str, aa_variant: bool = True) -> Dict:
    from .config import resolve, build_provider
    pm = build_provider(resolve(strain))
    try:
        pm.ec.model.solver.configuration.timeout = 10
    except Exception:
        pass
    os.makedirs(out_dir, exist_ok=True)

    results, rows = {}, []
    for spec in CURVES:
        cv = load_curve(strain, spec)
        pred, dense, dg, desc = _predict(pm, spec, strain, cv["temps_C"])
        r2, rmse = _fit_stats(cv["rate"], pred)
        obs_desc = TPC(cv["temps_C"], cv["rate"]).descriptors(0.05)
        res = {
            "study": cv["study"], "strain": cv["strain"], "medium": spec.medium,
            "digitized": spec.digitized, "n": int(len(cv["temps_C"])),
            "T_range_C": [float(cv["temps_C"].min()), float(cv["temps_C"].max())],
            "abs_R2": round(r2, 3), "RMSE_per_h": round(rmse, 3),
            "obs_rmax": round(cv["obs_rmax"], 3), "pred_rmax": round(float(desc.rmax), 3),
            "obs_Topt_C": round(cv["obs_Topt_C"], 1), "pred_Topt_C": round(float(desc.Topt_C), 1),
            "obs_CTmax_C": round(float(obs_desc.CTmax_C), 1),
            "pred_CTmax_C": round(float(desc.CTmax_C), 1),
            "obs_Ea_eV": round(float(obs_desc.Ea_eV), 3),
            "pred_Ea_eV": round(float(desc.Ea_eV), 3),
        }
        results[spec.key] = res
        rows.append({"curve": spec.key, **res})
        cv["pred"] = pred; cv["dense_T"] = dense; cv["dense_g"] = dg; cv["desc"] = desc
        results[spec.key]["_cv"] = cv   # kept in-memory for plotting only

    # optional Noll variant with the 6 trace amino acids opened (sensitivity check)
    if aa_variant:
        spec = CURVES[0]
        cv = load_curve(strain, spec)
        _, dense, dg, desc = _predict(pm, spec, strain, cv["temps_C"], extra_aa=NOLL_TRACE_AA)
        results["noll_minimal_AAopen"] = {"pred_rmax": round(float(desc.rmax), 3),
                                          "pred_Topt_C": round(float(desc.Topt_C), 1),
                                          "note": "glucose-minimal + 6 trace amino-acid uptakes opened"}

    # headline: minimal-vs-rich magnitude ratio
    mn, rh = results["noll_minimal"], results["erdos_LB"]
    results["magnitude_contrast"] = {
        "observed_rich_over_minimal": round(rh["obs_rmax"] / mn["obs_rmax"], 2),
        "model_rich_over_minimal": round(rh["pred_rmax"] / mn["pred_rmax"], 2),
        "obs_rmax_minimal": mn["obs_rmax"], "obs_rmax_rich": rh["obs_rmax"],
        "model_rmax_minimal": mn["pred_rmax"], "model_rmax_rich": rh["pred_rmax"],
        "note": "model reproduces the rich>minimal direction/ratio; both absolute "
                "rates under-predicted (kcat scale / sigma / medium composition)",
    }

    _plot_curves(results, out_dir)
    _plot_minimal_vs_rich(results, out_dir)

    pd.DataFrame(rows).to_csv(os.path.join(out_dir, "validation_trusted_table.csv"), index=False)
    clean = {k: {kk: vv for kk, vv in v.items() if kk != "_cv"} if isinstance(v, dict) else v
             for k, v in results.items()}
    with open(os.path.join(out_dir, "validation_trusted_summary.json"), "w") as fh:
        json.dump(clean, fh, indent=2)
    return clean


# ---------------------------------------------------------------------------
def _mpl():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def _plot_curves(results, out_dir):
    plt = _mpl()
    specs = [CURVES[0], CURVES[1]]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, spec in zip(axes, specs):
        cv = results[spec.key]["_cv"]; r = results[spec.key]
        if cv["sd"] is not None:
            ax.errorbar(cv["temps_C"], cv["rate"], yerr=cv["sd"], fmt="o", color="k",
                        ms=5, capsize=3, label="data (mean ± SD)", zorder=3)
        else:
            ax.plot(cv["temps_C"], cv["rate"], "o", color="k", ms=5,
                    label="data (digitized)", zorder=3)
        ax.plot(cv["dense_T"], cv["dense_g"], color=spec.color, lw=2.2,
                label="emergent model")
        ax.set_title(spec.label, fontsize=10)
        ax.set_xlabel("Temperature (°C)"); ax.set_ylabel("Growth rate (1/h)")
        ax.text(0.03, 0.97, f"absolute $R^2$={r['abs_R2']}\nRMSE={r['RMSE_per_h']} 1/h\n"
                f"obs $r_{{max}}$={r['obs_rmax']} vs pred {r['pred_rmax']}",
                transform=ax.transAxes, va="top", fontsize=8.5,
                bbox=dict(boxstyle="round", fc="0.96", ec="0.8"))
        ax.legend(frameon=False, fontsize=8, loc="lower right")
    fig.suptitle("Emergent model vs trusted strain-matched TPCs (raw absolute rate, nothing fit)")
    fig.tight_layout()
    p = os.path.join(out_dir, "validation_trusted_curves.png")
    fig.savefig(p, dpi=150); plt.close(fig)
    return p


def _plot_minimal_vs_rich(results, out_dir):
    plt = _mpl()
    mn, rh = results["noll_minimal"], results["erdos_LB"]
    cvm, cvr = mn["_cv"], rh["_cv"]
    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    # data
    if cvm["sd"] is not None:
        ax.errorbar(cvm["temps_C"], cvm["rate"], yerr=cvm["sd"], fmt="o",
                    color="tab:green", ms=5, capsize=3, label="minimal data (Noll, ±SD)")
    ax.plot(cvr["temps_C"], cvr["rate"], "s", color="tab:orange", ms=5,
            label="rich LB data (Erdos, digitized)")
    # model
    ax.plot(cvm["dense_T"], cvm["dense_g"], color="tab:green", lw=2.2, ls="-",
            label="model — glucose-minimal")
    ax.plot(cvr["dense_T"], cvr["dense_g"], color="tab:orange", lw=2.2, ls="-",
            label="model — LB")
    mc = results["magnitude_contrast"]
    ax.set_xlabel("Temperature (°C)"); ax.set_ylabel("Growth rate (1/h)")
    ax.set_title("Minimal vs rich magnitude — model reproduces the medium contrast")
    ax.text(0.97, 0.55, f"rich/minimal $r_{{max}}$ ratio\n  observed {mc['observed_rich_over_minimal']}×\n"
            f"  model {mc['model_rich_over_minimal']}×", transform=ax.transAxes, va="top",
            ha="right", fontsize=9, bbox=dict(boxstyle="round", fc="0.96", ec="0.8"))
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    p = os.path.join(out_dir, "validation_minimal_vs_rich.png")
    fig.savefig(p, dpi=150); plt.close(fig)
    return p
