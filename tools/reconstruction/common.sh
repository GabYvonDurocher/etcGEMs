# common.sh -- the layout the shell steps of this pipeline use. Source it, do not run it.
#
# The standalone's shell scripts resolved everything from `gem/`'s own location. Here the
# same four directories are configurable, so the pipeline can be pointed at a work area
# for any taxon:
#
#   RECON_HOME       this directory (tools/reconstruction)
#   RECON_WORK       inputs/, models/, tables/, notes/   (default $RECON_HOME/work/candida)
#   RECON_EXTERNAL   third-party code, weights, databases (default $RECON_HOME/external)
#   RECON_PROTEOMES  one FASTA (or UniProt TSV) per taxon (default $RECON_WORK/proteomes)
#
# Set any of them in the environment to override. They mirror paths.py's defaults, so the
# Python and shell steps agree without a second config file.
RECON_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RECON_NAME="${RECON_NAME:-candida}"
RECON_WORK="${RECON_WORK:-$RECON_HOME/work/$RECON_NAME}"
RECON_EXTERNAL="${RECON_EXTERNAL:-$RECON_HOME/external}"
RECON_PROTEOMES="${RECON_PROTEOMES:-$RECON_WORK/proteomes}"
RECON_INPUTS="$RECON_WORK/inputs"
RECON_MODELS="$RECON_WORK/models"
RECON_TABLES="$RECON_WORK/tables"
RECON_NOTES="$RECON_WORK/notes"
mkdir -p "$RECON_INPUTS" "$RECON_MODELS" "$RECON_TABLES" "$RECON_NOTES" "$RECON_EXTERNAL"
