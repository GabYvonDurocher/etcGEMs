#!/usr/bin/env python3
"""a1_analyse.py -- A1 PARTs A-F: score the sequence predictors against measurement.

    python3 reports/predictor_calibration/a1_analyse.py

Reads the predictions written by a1_predict.sh and the ortholog sets written by
a1_orthologs.py, and writes every table beside this file. It computes; it does not fetch
and it does not predict.

The one measurement in the whole exercise is the S. cerevisiae meltome (1949 proteins with
a melting point). Everything that is scored is scored against it, or against the one other
measured quantity available -- Walunjkar et al.'s mean ortholog dTm of 1.6 C between
S. cerevisiae and S. uvarum, which is published only as a summary.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(ROOT, "tools", "reconstruction", "external", "a1_data")

MEASURED_SCER_SUVA_DTM = 1.6      # C, Walunjkar et al. 2025, 827 pairs, parental context
STANDALONE_DTM_DEDUP = 0.411      # C, auris - haemulonii, unique protein pairs (n = 432)
STANDALONE_DTM_RXN = 0.518        # C, the same before deduplication (n = 1041)
K2_REQUIRED_DTM = 13.77           # C, K2 ladder rung B4, median over the three relatives
STANDALONE_REQUIRED_DTM = 32.54   # C, the standalone's phenomenological form

CLADES = ["I", "II", "III", "IV"]
RELATIVES = ["haemulonii", "duobushaemulonii", "parapsilosis"]


# ---------------------------------------------------------------------------- helpers
def load_pred(name, head):
    p = os.path.join(DATA, "predictions", f"{name}_{head}.csv")
    if not os.path.exists(p):
        return None
    d = pd.read_csv(p)
    col = "pred_tm" if head == "tm" else "pred_topt"
    return dict(zip(d["id"].astype(str), d[col].astype(float)))


def load_pairs(tag):
    p = os.path.join(DATA, "orthologs", f"{tag}.tsv")
    if not os.path.exists(p):
        return None
    return [(a, b, float(c)) for a, b, c in
            (l.rstrip("\n").split("\t") for l in open(p))]


def ci95(x):
    """Mean and a t-based 95% CI of a sample."""
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if len(x) < 2:
        return float("nan"), float("nan"), float("nan"), len(x)
    from scipy import stats
    m = float(x.mean())
    h = float(stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x)))
    return m, m - h, m + h, len(x)


def paired_difference(pairs, pred_a, pred_b, seq_a=None, seq_b=None):
    """Paired predicted difference (a - b) over UNIQUE protein pairs.

    Unique by construction: reciprocal best hits are one-to-one. Returns the per-pair
    differences plus, when sequences are supplied, the subset whose two sequences are
    IDENTICAL -- for those the predictor's only reason to differ is batch padding, so their
    spread is pure predictor noise."""
    d, d_ident = [], []
    for a, b, _pid in pairs:
        va, vb = pred_a.get(a), pred_b.get(b)
        if va is None or vb is None:
            continue
        d.append(va - vb)
        if seq_a is not None and seq_b is not None:
            sa, sb = seq_a.get(a), seq_b.get(b)
            if sa is not None and sb is not None and sa == sb:
                d_ident.append(va - vb)
    return np.array(d), np.array(d_ident)


def read_fasta_seqs(path):
    out, pid, buf = {}, None, []
    for line in open(path):
        if line.startswith(">"):
            if pid:
                out[pid] = "".join(buf)
            pid = line[1:].split()[0]
            buf = []
        else:
            buf.append(line.strip())
    if pid:
        out[pid] = "".join(buf)
    return out


# ---------------------------------------------------------------------------- parts
def part_ab(res):
    """PART A absolute accuracy and PART B variance compression, against the meltome."""
    from scipy import stats
    meas = pd.read_csv(os.path.join(DATA, "meltome_scerevisiae.csv"))
    pred = load_pred("scerevisiae", "tm")
    if pred is None:
        print("PART A/B: no S. cerevisiae Tm predictions yet", file=sys.stderr)
        return
    meas["pred"] = meas.uniprotAccession.map(pred)
    n_all = len(meas)
    m = meas.dropna(subset=["pred", "meltingPoint"])
    a, b = m.meltingPoint.values, m.pred.values
    r_p = float(stats.pearsonr(a, b)[0])
    r_s = float(stats.spearmanr(a, b)[0])
    rmse = float(np.sqrt(np.mean((b - a) ** 2)))
    bias = float(b.mean() - a.mean())
    sl, ic, _, _, se = stats.linregress(b, a)      # measured ~ predicted
    res["A"] = dict(n_measured=n_all, n_matched=len(m), pearson_r=r_p, spearman_rho=r_s,
                    rmse_C=rmse, bias_C=bias,
                    measured_mean=float(a.mean()), predicted_mean=float(b.mean()))
    res["B"] = dict(
        n=len(m),
        sd_measured=float(a.std(ddof=1)), sd_predicted=float(b.std(ddof=1)),
        iqr_measured=float(np.percentile(a, 75) - np.percentile(a, 25)),
        iqr_predicted=float(np.percentile(b, 75) - np.percentile(b, 25)),
        p5_95_measured=float(np.percentile(a, 95) - np.percentile(a, 5)),
        p5_95_predicted=float(np.percentile(b, 95) - np.percentile(b, 5)),
        compression_sd=float(a.std(ddof=1) / b.std(ddof=1)),
        compression_iqr=float((np.percentile(a, 75) - np.percentile(a, 25)) /
                              (np.percentile(b, 75) - np.percentile(b, 25))),
        compression_p5_95=float((np.percentile(a, 95) - np.percentile(a, 5)) /
                                (np.percentile(b, 95) - np.percentile(b, 5))),
        regression_slope=float(sl), regression_slope_se=float(se),
        regression_intercept=float(ic))
    m[["uniprotAccession", "proteinId", "meltingPoint", "pred"]].to_csv(
        os.path.join(HERE, "partAB_measured_vs_predicted.csv"), index=False)
    _plot_A(m, res)


def _plot_A(m, res):
    """Predicted against measured, with the 1:1 line -- and beside it the same plot for the
    cross-species control, because the pair is the finding."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    panels = [(m.meltingPoint.values, m.pred.values,
               "Within one proteome\nS. cerevisiae (Meltome Atlas)",
               f"n = {len(m)}   Pearson r = {res['A']['pearson_r']:+.3f}")]
    ctrl_p = os.path.join(HERE, "control_measured_vs_predicted.csv")
    ctrl_j = os.path.join(HERE, "control_results.json")
    if os.path.exists(ctrl_p) and os.path.exists(ctrl_j):
        c = pd.read_csv(ctrl_p)
        r = json.load(open(ctrl_j))["pearson_r"]
        panels.append((c.target.values, c.pred_tm.values,
                       "Across the tree of life\nrandom Meltome Atlas sample",
                       f"n = {len(c)}   Pearson r = {r:+.3f}"))
    fig, axes = plt.subplots(1, len(panels), figsize=(5.3 * len(panels), 4.8))
    for ax, (x, y, title, sub) in zip(np.atleast_1d(axes), panels):
        lo, hi = min(x.min(), y.min()) - 2, max(x.max(), y.max()) + 2
        ax.plot([lo, hi], [lo, hi], color="0.4", lw=1, ls="--", zorder=1, label="1:1")
        ax.scatter(x, y, s=7, alpha=0.35, edgecolor="none", color="#2b6cb0", zorder=2)
        ax.set_xlim(lo, hi); ax.set_ylim(lo, hi); ax.set_aspect("equal")
        ax.set_xlabel("measured $T_m$ (°C)")
        ax.set_ylabel("Seq2Tm predicted $T_m$ (°C)")
        ax.set_title(title, fontsize=10)
        ax.text(0.03, 0.97, sub, transform=ax.transAxes, va="top", fontsize=9)
        ax.legend(loc="lower right", fontsize=8, frameon=False)
    fig.suptitle("Seq2Tm against measurement", fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "fig_partA_predicted_vs_measured.png"), dpi=170)
    plt.close(fig)


def part_cd(res, head):
    """PART C the interspecies test, PART D the same-species noise floor. Both heads."""
    croot = os.environ.get("CANDIDAS_ROOT")
    key = "Tm" if head == "tm" else "Topt"
    rows = []

    # -- C: S. cerevisiae vs S. uvarum, against a measured benchmark ---------------
    pairs = load_pairs("scerevisiae__suvarum")
    pa, pb = load_pred("scerevisiae", head), load_pred("suvarum", head)
    if pairs and pa and pb:
        d, _ = paired_difference(pairs, pa, pb)
        mean, lo, hi, n = ci95(d)
        rows.append(dict(comparison="S. cerevisiae - S. uvarum", kind="interspecies",
                         head=key, n_pairs=n, mean_diff_C=mean, ci_lo=lo, ci_hi=hi,
                         sd_of_pair_diffs=float(np.std(d, ddof=1)),
                         frac_positive=float((d > 0).mean())))

    # -- D: the four C. auris clades, whose true difference is ~0 ------------------
    if croot:
        pr = os.path.join(croot, "phylo", "proteomes")
        seqs = {c: read_fasta_seqs(os.path.join(pr, f"auris_clade{c}.faa")) for c in CLADES}
        preds = {c: load_pred(f"auris_clade{c}", head) for c in CLADES}
        for i, ci in enumerate(CLADES):
            for cj in CLADES[i + 1:]:
                p = load_pairs(f"auris_clade{ci}__clade{cj}")
                if not p or not preds[ci] or not preds[cj]:
                    continue
                d, di = paired_difference(p, preds[ci], preds[cj], seqs[ci], seqs[cj])
                mean, lo, hi, n = ci95(d)
                mi, _, _, ni = ci95(di)
                rows.append(dict(comparison=f"C. auris clade {ci} - clade {cj}",
                                 kind="same-species (noise floor)", head=key,
                                 n_pairs=n, mean_diff_C=mean, ci_lo=lo, ci_hi=hi,
                                 sd_of_pair_diffs=float(np.std(d, ddof=1)) if n > 1 else np.nan,
                                 frac_positive=float((d > 0).mean()) if n else np.nan,
                                 n_identical_seq_pairs=ni,
                                 mean_diff_identical_seqs=mi))
        # -- the interspecies estimate Figure 4 rests on, measured the same way ----
        seqI = seqs["I"]
        predI = preds["I"]
        for rel in RELATIVES:
            p = load_pairs(f"auris_cladeI__{rel}")
            pr_ = load_pred(rel, head)
            if not p or not predI or not pr_:
                continue
            d, _ = paired_difference(p, predI, pr_)
            mean, lo, hi, n = ci95(d)
            rows.append(dict(comparison=f"C. auris - C. {rel}", kind="interspecies",
                             head=key, n_pairs=n, mean_diff_C=mean, ci_lo=lo, ci_hi=hi,
                             sd_of_pair_diffs=float(np.std(d, ddof=1)),
                             frac_positive=float((d > 0).mean())))
    res.setdefault("CD", []).extend(rows)


def part_e_spreads(res):
    """PART E's spread test. PARTs A and B cannot be done for Seq2Topt: there is no measured
    proteome-wide set of enzyme catalytic optima to score it against, in yeast or anywhere
    else. What can be reported without a benchmark is the SPREAD each predictor produces
    across each proteome, on one scale, so the two channels are comparable -- and, for Tm,
    against the one measured spread there is."""
    rows = []
    names = [("scerevisiae", "S. cerevisiae"), ("suvarum", "S. uvarum"),
             ("auris_cladeI", "C. auris clade I"), ("auris_cladeII", "C. auris clade II"),
             ("auris_cladeIII", "C. auris clade III"), ("auris_cladeIV", "C. auris clade IV"),
             ("haemulonii", "C. haemulonii"), ("duobushaemulonii", "C. duobushaemulonii"),
             ("parapsilosis", "C. parapsilosis")]
    for head in ("tm", "topt"):
        for key, label in names:
            p = load_pred(key, head)
            if not p:
                continue
            v = np.array(list(p.values()), float)
            rows.append(dict(head=("Tm" if head == "tm" else "Topt"), proteome=label,
                             n=len(v), mean=float(v.mean()), sd=float(v.std(ddof=1)),
                             iqr=float(np.percentile(v, 75) - np.percentile(v, 25)),
                             p5_95=float(np.percentile(v, 95) - np.percentile(v, 5))))
    res["E_spreads"] = rows


def part_f(res):
    """PART F -- what the correction does to Figure 4's arithmetic.

    Figure 4's claim is a ratio: the separation the MODEL requires, over the separation the
    PROTEOMES have. K2 fixed the denominator's counterpart (the requirement is 13.8 C, not
    32.5). This fixes the numerator, or says why it cannot be fixed.

    The correction factor is empirical and comes from the one place a predicted paired
    interspecies difference can be checked against a measured one: S. cerevisiae vs
    S. uvarum, measured mean 1.6 C. The assumption that makes it valid, stated so it can be
    disagreed with, is that compression measured in one congeneric yeast pair transfers to
    another congeneric pair at comparable divergence."""
    D = pd.DataFrame(res.get("CD", []))
    if not len(D):
        return
    tm = D[D["head"] == "Tm"]
    row = tm[tm.comparison == "S. cerevisiae - S. uvarum"]
    if not len(row):
        return
    pred_yeast = abs(float(row.iloc[0].mean_diff_C))
    factor = MEASURED_SCER_SUVA_DTM / pred_yeast if pred_yeast > 0 else float("inf")

    hae = tm[tm.comparison == "C. auris - C. haemulonii"]
    pred_candida_proteome = abs(float(hae.iloc[0].mean_diff_C)) if len(hae) else float("nan")

    # the noise floor: what the predictor returns for proteomes whose true difference is ~0
    floor = tm[tm.kind.str.startswith("same-species")]
    floor_abs = float(np.abs(floor.mean_diff_C).mean()) if len(floor) else float("nan")
    floor_max = float(np.abs(floor.mean_diff_C).max()) if len(floor) else float("nan")
    n_signif = int(((floor.ci_lo > 0) | (floor.ci_hi < 0)).sum()) if len(floor) else 0

    # interval on the correction factor and on the corrected difference. The factor is a
    # ratio to a predicted difference that is itself only a few times the noise floor, so
    # its interval is wide and is carried through rather than dropped.
    ylo, yhi = sorted(abs(float(v)) for v in (row.iloc[0].ci_lo, row.iloc[0].ci_hi))
    f_lo, f_hi = sorted((MEASURED_SCER_SUVA_DTM / yhi if yhi > 0 else float("inf"),
                         MEASURED_SCER_SUVA_DTM / ylo if ylo > 0 else float("inf")))
    c_lo, c_hi = (sorted(abs(float(v)) for v in (hae.iloc[0].ci_lo, hae.iloc[0].ci_hi))
                  if len(hae) else (float("nan"), float("nan")))

    rows = []
    for label, required, available, note in (
            ("standalone (phenomenological form, deduplicated pairs)",
             STANDALONE_REQUIRED_DTM, STANDALONE_DTM_DEDUP,
             "as published: gem/FIG4_LOCKED.md"),
            ("K2-corrected requirement, same available difference",
             K2_REQUIRED_DTM, STANDALONE_DTM_DEDUP,
             "K2 rung B4: the core's unfolding form needs 13.8 C, not 32.5"),
            ("K2-corrected requirement, A1 proteome-wide available difference",
             K2_REQUIRED_DTM, pred_candida_proteome,
             "the same predicted quantity measured over all RBH orthologs rather than the "
             "model-enzyme subset"),
            ("K2-corrected requirement, A1 compression-corrected difference",
             K2_REQUIRED_DTM, pred_candida_proteome * factor,
             f"predicted difference scaled by {factor:.1f}x, the factor by which the "
             f"predictor under-states the MEASURED S. cerevisiae/S. uvarum difference")):
        rows.append(dict(scenario=label, required_dTm_C=required,
                         available_dTm_C=available,
                         fold_gap=(required / available if available else float("inf")),
                         note=note))
    # the same, against the largest measured proteome-wide difference on record
    rows.append(dict(scenario="K2-corrected requirement, vs the MEASURED yeast benchmark",
                     required_dTm_C=K2_REQUIRED_DTM,
                     available_dTm_C=MEASURED_SCER_SUVA_DTM,
                     fold_gap=K2_REQUIRED_DTM / MEASURED_SCER_SUVA_DTM,
                     note="Walunjkar et al. 2025: 1.6 C over 827 pairs, measured, for an "
                          "8 C difference in growth limit"))
    res["F"] = dict(predicted_scer_suva_dTm=pred_yeast,
                    predicted_scer_suva_ci=[float(row.iloc[0].ci_lo), float(row.iloc[0].ci_hi)],
                    measured_scer_suva_dTm=MEASURED_SCER_SUVA_DTM,
                    correction_factor=factor, correction_factor_ci=[f_lo, f_hi],
                    predicted_candida_proteomewide_dTm=pred_candida_proteome,
                    predicted_candida_ci=[c_lo, c_hi],
                    corrected_candida_dTm=pred_candida_proteome * factor,
                    corrected_candida_ci=sorted([c_lo * f_lo, c_hi * f_hi]),
                    fold_gap_corrected=K2_REQUIRED_DTM / (pred_candida_proteome * factor),
                    fold_gap_corrected_ci=sorted([K2_REQUIRED_DTM / (c_hi * f_hi),
                                                  K2_REQUIRED_DTM / (c_lo * f_lo)]),
                    noise_floor_mean_abs=floor_abs, noise_floor_max_abs=floor_max,
                    noise_floor_n_significant=n_signif, noise_floor_n_pairs=len(floor),
                    standalone_dTm_as_multiple_of_floor=STANDALONE_DTM_DEDUP / floor_abs,
                    proteomewide_dTm_as_multiple_of_floor=pred_candida_proteome / floor_abs,
                    table=rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args(argv)
    res = {}
    part_ab(res)
    for head in ("tm", "topt"):
        part_cd(res, head)

    # ------------------------------------------------------------------ print + write
    if "A" in res:
        A, B = res["A"], res["B"]
        print("PART A -- Seq2Tm against the measured S. cerevisiae meltome")
        print(f"  n measured {A['n_measured']}, matched to the reference proteome {A['n_matched']}")
        print(f"  Pearson r  {A['pearson_r']:+.3f}    Spearman rho {A['spearman_rho']:+.3f}")
        print(f"  RMSE       {A['rmse_C']:.2f} C      bias {A['bias_C']:+.2f} C "
              f"(measured mean {A['measured_mean']:.2f}, predicted {A['predicted_mean']:.2f})")
        print("\nPART B -- variance compression")
        print(f"  {'':16s} {'measured':>10s} {'predicted':>10s} {'ratio':>8s}")
        for lab, k in (("SD", "sd"), ("IQR", "iqr"), ("5-95 range", "p5_95")):
            print(f"  {lab:16s} {B[k+'_measured']:10.3f} {B[k+'_predicted']:10.3f} "
                  f"{B['compression_'+k]:8.2f}")
        print(f"  regression of measured on predicted: slope "
              f"{B['regression_slope']:.3f} +/- {B['regression_slope_se']:.3f}")

    if res.get("CD"):
        D = pd.DataFrame(res["CD"])
        D.to_csv(os.path.join(HERE, "paired_differences.csv"), index=False)
        for head in ("Tm", "Topt"):
            sub = D[D["head"] == head]
            if not len(sub):
                continue
            print(f"\nPARTs C/D/E -- paired predicted {head} differences over unique "
                  f"ortholog pairs")
            cols = ["comparison", "kind", "n_pairs", "mean_diff_C", "ci_lo", "ci_hi",
                    "sd_of_pair_diffs", "frac_positive"]
            if "n_identical_seq_pairs" in sub.columns:
                cols += ["n_identical_seq_pairs", "mean_diff_identical_seqs"]
            print(sub[cols].round(4).to_string(index=False))

    part_e_spreads(res)
    if res.get("E_spreads"):
        S = pd.DataFrame(res["E_spreads"])
        S.to_csv(os.path.join(HERE, "predicted_spreads.csv"), index=False)
        print("\nPART E -- predicted spread per proteome (no measured benchmark exists for "
              "Topt; the measured S. cerevisiae Tm spread is SD 3.98, IQR 5.30)")
        print(S.round(3).to_string(index=False))

    part_f(res)
    if "F" in res:
        F = res["F"]
        print(f"\nPART F -- the corrected Figure 4 arithmetic")
        print(f"  predicted S. cerevisiae - S. uvarum paired dTm : "
              f"{F['predicted_scer_suva_dTm']:.3f} C")
        print(f"  measured  (Walunjkar et al. 2025, n = 827)     : "
              f"{F['measured_scer_suva_dTm']:.3f} C")
        print(f"  empirical correction factor                    : "
              f"{F['correction_factor']:.1f}x  [{F['correction_factor_ci'][0]:.1f}, "
              f"{F['correction_factor_ci'][1]:.1f}]")
        print(f"  noise floor (six same-species clade pairs, true dTm ~ 0): mean |mean| "
              f"{F['noise_floor_mean_abs']:.3f} C, max {F['noise_floor_max_abs']:.3f} C; "
              f"{F['noise_floor_n_significant']}/{F['noise_floor_n_pairs']} of them "
              f"significantly non-zero")
        print(f"  the standalone's 0.411 C is {F['standalone_dTm_as_multiple_of_floor']:.1f}x "
              f"that floor; A1's proteome-wide 0.151 C is "
              f"{F['proteomewide_dTm_as_multiple_of_floor']:.1f}x")
        print(f"  corrected C. auris - C. haemulonii dTm         : "
              f"{F['corrected_candida_dTm']:.2f} C  [{F['corrected_candida_ci'][0]:.2f}, "
              f"{F['corrected_candida_ci'][1]:.2f}]")
        print(f"  corrected fold gap against K2's 13.77 C        : "
              f"{F['fold_gap_corrected']:.1f}x  [{F['fold_gap_corrected_ci'][0]:.1f}, "
              f"{F['fold_gap_corrected_ci'][1]:.1f}]")
        T = pd.DataFrame(F["table"])
        T.to_csv(os.path.join(HERE, "figure4_arithmetic.csv"), index=False)
        with pd.option_context("display.width", 200, "display.max_colwidth", 62):
            print(T[["scenario", "required_dTm_C", "available_dTm_C", "fold_gap"]]
                  .round(3).to_string(index=False))

    with open(os.path.join(HERE, "a1_results.json"), "w") as fh:
        json.dump(res, fh, indent=2, default=float)
    print("\nwrote", os.path.join(HERE, "a1_results.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
