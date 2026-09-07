#!/usr/bin/env bash
# a1_predict.sh -- run Seq2Tm and Seq2Topt over the five proteomes A1 needs.
#
# PROTOCOL. Every run is batch 4 in FILE ORDER, with no length truncation. That is not a
# default, it is the protocol that produced the Candida predictions, and it is verified
# rather than assumed: taking the first 200 rows of the committed
# gem/tables/{thermal_tm,thermal_topt}.csv in file order and re-predicting them reproduces
# them to 1.8e-5 C (Tm) and 1.1e-4 C (Topt), r = 1.000000000 in both cases. The padding
# artefact documented in gem/FIG4_LOCKED.md therefore applies equally to both sides of every
# comparison in A1, which is what is wanted: we are measuring the predictor AS USED.
#
# DEVICE. mps (Apple GPU) by default because it is ~13x cheaper, and only after checking
# that it changes nothing: on the same 200-row reproduction it agrees with the committed
# table to 3.5e-5 C, r = 1.000000000, against CPU's 1.8e-5 C. Both are four orders of
# magnitude below the smallest difference A1 reports. Set A1_DEVICE=cpu to pin the CPU.
#
# Each file is written in ONE run. The script's resume path re-batches whatever is left,
# which would change batch composition and therefore the predictions, so a partial output is
# deleted rather than continued.
#
#   bash reports/predictor_calibration/a1_predict.sh [OUTDIR]
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
DATA="$ROOT/tools/reconstruction/external/a1_data"
OUT="${1:-$DATA/predictions}"
PY="$ROOT/tools/reconstruction/external/predictor_venv/bin/python"
DEV="${A1_DEVICE:-mps}"
RUN="$ROOT/tools/reconstruction/15_run_seq2tm.py"
export TORCH_HOME="$ROOT/tools/reconstruction/external/torch_home"
mkdir -p "$OUT"

# id,sequence inputs from the two UniProt TSVs (the clade proteomes are read as FASTA)
"$PY" - "$DATA" <<'PYEOF'
import sys, os, pandas as pd
D = sys.argv[1]
for key in ("scerevisiae", "suvarum"):
    t = pd.read_csv(os.path.join(D, f"proteome_{key}.tsv"), sep="\t")
    t = t[["Entry", "Sequence"]].rename(columns={"Entry": "id", "Sequence": "sequence"})
    t = t.dropna().drop_duplicates("id")
    t.to_csv(os.path.join(D, f"seqs_{key}.csv"), index=False)
    print(f"{key}: {len(t)} sequences")
PYEOF

for m in tm topt; do
  for k in scerevisiae suvarum; do
    o="$OUT/${k}_${m}.csv"
    [ -f "$o.done" ] && { echo "have $o"; continue; }
    rm -f "$o"   # never resume: re-batching would change the predictions
    echo "== $k / $m"
    "$PY" "$RUN" --model "$m" --seqs-from "$DATA/seqs_${k}.csv" "$o" \
        --batch-size 4 --device "$DEV" && touch "$o.done"
  done
  # the four C. auris clades (PART D's noise floor) and the three relatives (so the Candida
  # paired difference can be measured PROTEOME-WIDE, through the same RBH pairing and the
  # same predictor run as the yeast benchmark, rather than only taken from the standalone's
  # model-enzyme subset)
  for c in cladeI cladeII cladeIII cladeIV ; do
    f="${CANDIDAS_ROOT:?set CANDIDAS_ROOT}/phylo/proteomes/auris_${c}.faa"
    o="$OUT/auris_${c}_${m}.csv"
    [ -f "$o.done" ] && { echo "have $o"; continue; }
    rm -f "$o"   # never resume: re-batching would change the predictions
    echo "== auris $c / $m"
    "$PY" "$RUN" --model "$m" "$f" "$o" --batch-size 4 --device "$DEV" && touch "$o.done"
  done
  for r in haemulonii duobushaemulonii parapsilosis ; do
    f="${CANDIDAS_ROOT:?set CANDIDAS_ROOT}/phylo/proteomes/${r}.faa"
    o="$OUT/${r}_${m}.csv"
    [ -f "$o.done" ] && { echo "have $o"; continue; }
    rm -f "$o"
    echo "== $r / $m"
    "$PY" "$RUN" --model "$m" "$f" "$o" --batch-size 4 --device "$DEV" && touch "$o.done"
  done
done
echo "all predictions in $OUT"
