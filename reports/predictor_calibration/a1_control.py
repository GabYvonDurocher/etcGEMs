#!/usr/bin/env python3
"""a1_control.py -- the positive control PART A needs before its result can be believed.

PART A scores Seq2Tm against the measured S. cerevisiae meltome and gets a correlation of
essentially zero. Before that is reported as a property of the predictor, it has to be shown
that the pipeline can recover a correlation that IS there. So: run the same predictor,
through the same code, on a random sample of the WHOLE Meltome Atlas -- every species, a Tm
range of tens of degrees rather than one proteome's few -- and correlate.

If the cross-species correlation is high and the within-yeast correlation is zero, the
pipeline is sound and the predictor resolves between-organism thermophily but not
within-proteome variation. If both are zero, something is wrong with the pipeline and PART A
means nothing. Either way it has to be checked.

    python3 reports/predictor_calibration/a1_control.py --prepare      # write the input
    bash  ... 15_run_seq2tm.py --seqs-from <input> <out> --batch-size 4
    python3 reports/predictor_calibration/a1_control.py --score <out>
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
FASTA = os.path.join(DATA, "mixed_split.fasta")
N = 1500
SEED = 0
# Same length regime as the real use. The Candida pipeline's own predictor input caps at
# 2000 aa (13_seq2topt_input.py), and the Atlas contains sequences up to 35 kaa: a single
# 35,213-residue protein in a batch of four exhausted memory and killed the first attempt at
# this control. Excluding them keeps the control in the regime it is a control FOR, and the
# number excluded is reported.
MAXLEN = 2000


def read():
    recs, sid, tgt, buf = [], None, None, []
    for line in open(FASTA):
        if line.startswith(">"):
            if sid:
                recs.append((sid, tgt, "".join(buf)))
            h = line[1:].split()
            sid = h[0]
            tgt = float([x for x in h if x.startswith("TARGET=")][0].split("=")[1])
            buf = []
        else:
            buf.append(line.strip())
    if sid:
        recs.append((sid, tgt, "".join(buf)))
    return pd.DataFrame(recs, columns=["id", "target", "sequence"])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prepare", action="store_true")
    ap.add_argument("--score", metavar="PREDICTIONS_CSV")
    a = ap.parse_args(argv)

    if a.prepare:
        d = read()
        print(f"{len(d)} sequences with a melting point in {os.path.basename(FASTA)}")
        n_long = int((d.sequence.str.len() > MAXLEN).sum())
        d = d[d.sequence.str.len() <= MAXLEN]
        print(f"excluded {n_long} sequences longer than {MAXLEN} aa "
              f"({100*n_long/(len(d)+n_long):.1f}%); {len(d)} remain")
        s = d.sample(N, random_state=SEED).reset_index(drop=True)
        s[["id", "sequence"]].to_csv(os.path.join(DATA, "control_input.csv"), index=False)
        s[["id", "target"]].to_csv(os.path.join(DATA, "control_truth.csv"), index=False)
        print(f"sampled {len(s)} (seed {SEED}); measured Tm mean {s.target.mean():.2f} "
              f"sd {s.target.std():.2f} range {s.target.min():.1f}-{s.target.max():.1f} C")
        return 0

    if a.score:
        from scipy import stats
        truth = pd.read_csv(os.path.join(DATA, "control_truth.csv"))
        pred = pd.read_csv(a.score)
        m = truth.merge(pred, on="id").dropna()
        x, y = m.target.values, m.pred_tm.values
        out = dict(n=len(m), pearson_r=float(stats.pearsonr(x, y)[0]),
                   spearman_rho=float(stats.spearmanr(x, y)[0]),
                   rmse_C=float(np.sqrt(np.mean((y - x) ** 2))),
                   bias_C=float(y.mean() - x.mean()),
                   sd_measured=float(x.std(ddof=1)), sd_predicted=float(y.std(ddof=1)),
                   compression_sd=float(x.std(ddof=1) / y.std(ddof=1)),
                   regression_slope=float(stats.linregress(y, x)[0]))
        print("POSITIVE CONTROL -- Seq2Tm on a random sample of the whole Meltome Atlas")
        for k, v in out.items():
            print(f"  {k:18s} {v:.4f}" if isinstance(v, float) else f"  {k:18s} {v}")
        with open(os.path.join(HERE, "control_results.json"), "w") as fh:
            json.dump(out, fh, indent=2)
        m.to_csv(os.path.join(HERE, "control_measured_vs_predicted.csv"), index=False)
        print("wrote", os.path.join(HERE, "control_results.json"))
        return 0
    ap.error("give --prepare or --score")


if __name__ == "__main__":
    sys.exit(main())
