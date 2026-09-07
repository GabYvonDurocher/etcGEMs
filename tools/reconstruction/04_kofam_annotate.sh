#!/usr/bin/env bash
# =============================================================================
# 04_kofam_annotate.sh -- KEGG Orthology (KO) for every protein in the three Candidozyma proteomes
# =============================================================================
#   bash tools/reconstruction/04_kofam_annotate.sh            (~1-2 h per proteome on 8 cores; run once)
#
# KofamScan (Aramaki et al. 2020, Bioinformatics 36:2251) assigns KOs by HMM search against
# the KOfam profiles with per-family adaptive score thresholds. Output in "mapper" format:
# one line per protein, <protein id><TAB><KO> when a KO passes its threshold, the id alone
# when none does. These KO tables are the evidence 06_build_drafts.py uses to give every
# reaction of the iRV973 scaffold a gene-protein-reaction rule from the target species' own
# genome (KO -> KEGG reaction, then KO -> EC).
#
# Inputs   $RECON_PROTEOMES/<taxon>.faa, one per TAXA entry below
#          $RECON_EXTERNAL/kofam/profiles/ and ko_list  (KOfam, from ftp.genome.jp/pub/db/kofam;
#          fetch_external.sh)
# Outputs  $RECON_WORK/inputs/kofam/<tag>_ko.txt   (the Candida run: 5527 / 5461 / 5363 lines)
#
# PORTED from the standalone Candida etcGEM (Candidas `gem/`). The only change is that the
# proteome list and the directories are configurable (TAXA below and common.sh) rather than
# the three Candidozyma proteomes at fixed paths. The method is unchanged.
#
# The committed tables were produced on 2026-09-02 against the KOfam release current on
# that day (the profiles and ko_list downloaded then are the ones in $RECON_EXTERNAL/kofam/);
# the KofamScan and HMMER versions were not recorded at the time. Re-running against a
# newer KOfam release can change a handful of assignments, so the committed tables are the
# reference; regenerate only with the same profiles.
# =============================================================================
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/common.sh"
KOFAM="$RECON_EXTERNAL/kofam"
OUT="$RECON_INPUTS/kofam"; mkdir -p "$OUT"
CPU="${CPU:-8}"
# <proteome basename>:<output tag>, one per taxon needing a draft. Must agree with the
# `proteome:` and `kofam:` entries of reconstruction.yaml (06_build_drafts.py reads those).
TAXA=("${@:-}")
[ -z "${TAXA[*]}" ] && TAXA=("auris_cladeI:auris" "haemulonii:hae" "duobushaemulonii:duo")

command -v exec_annotation >/dev/null || { echo "!! exec_annotation (KofamScan) not in PATH: conda install -c bioconda kofamscan"; exit 1; }
[ -d "$KOFAM/profiles" ] || { echo "!! $KOFAM/profiles missing; run tools/reconstruction/fetch_external.sh"; exit 1; }

for pair in "${TAXA[@]}"; do
  faa="${pair%%:*}"; tag="${pair##*:}"
  echo "== $faa -> $tag"
  exec_annotation -f mapper --cpu "$CPU" -p "$KOFAM/profiles" -k "$KOFAM/ko_list" \
      --tmp-dir "$KOFAM/tmp_$tag" -o "$OUT/${tag}_ko.txt" "$RECON_PROTEOMES/$faa.faa"
  echo "   $(awk -F'\t' 'NF>1' "$OUT/${tag}_ko.txt" | wc -l) proteins with a KO of $(wc -l < "$OUT/${tag}_ko.txt")"
done
echo "next: python3 tools/reconstruction/06_build_drafts.py"
