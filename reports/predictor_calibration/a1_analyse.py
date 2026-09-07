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

    with open(os.path.join(HERE, "a1_results.json"), "w") as fh:
        json.dump(res, fh, indent=2, default=float)
    print("\nwrote", os.path.join(HERE, "a1_results.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
