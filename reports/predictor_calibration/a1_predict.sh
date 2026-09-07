#!/usr/bin/env bash
# a1_predict.sh -- run Seq2Tm and Seq2Topt over the five proteomes A1 needs.
#
# PROTOCOL. Every run is batch 4 in FILE ORDER on CPU, with no length truncation. That is
# not a default, it is the protocol that produced the Candida predictions, and it is
# verified rather than assumed: taking the first 200 rows of the committed
# gem/tables/{thermal_tm,thermal_topt}.csv in file order and re-predicting them reproduces
# them to 1.8e-5 C (Tm) and 1.1e-4 C (Topt), r = 1.000000000 in both cases. The padding
# artefact documented in gem/FIG4_LOCKED.md therefore applies equally to both sides of every
# comparison in A1, which is what is wanted: we are measuring the predictor AS USED.
#
#   bash reports/predictor_calibration/a1_predict.sh [OUTDIR]
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
DATA="$ROOT/tools/reconstruction/external/a1_data"
OUT="${1:-$DATA/predictions}"
PY="$ROOT/tools/reconstruction/external/predictor_venv/bin/python"
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
    echo "== $k / $m"
    "$PY" "$RUN" --model "$m" --seqs-from "$DATA/seqs_${k}.csv" "$o" \
        --batch-size 4 --device cpu && touch "$o.done"
  done
  for c in I II III IV; do
    f="${CANDIDAS_ROOT:?set CANDIDAS_ROOT}/phylo/proteomes/auris_clade${c}.faa"
    o="$OUT/auris_clade${c}_${m}.csv"
    [ -f "$o.done" ] && { echo "have $o"; continue; }
    echo "== clade $c / $m"
    "$PY" "$RUN" --model "$m" "$f" "$o" --batch-size 4 --device cpu && touch "$o.done"
  done
done
echo "all predictions in $OUT"
