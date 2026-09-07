"""paths.py -- the one place this pipeline's directories and taxon map are defined.

Ported from `gempaths.py` of the standalone Candida etcGEM (Candidas repository,
`gem/`). The standalone hard-coded a single repository layout and a single four-species
map; here both come from a **reconstruction config** so the pipeline can build the
inputs for any taxon, and the scripts themselves are unchanged apart from this import.

Resolution order for the config file:

    1. the ``--config`` argument a script passes to :func:`configure`
    2. ``$RECON_CONFIG``
    3. ``./reconstruction.yaml``
    4. ``tools/reconstruction/reconstruction.yaml`` (the committed template)

Layout (all relative to ``work_dir``, which defaults to
``tools/reconstruction/work/<name>``; nothing here is inside a strain folder):

    <work>/inputs/      hand-curated inputs: medium maps, KO annotations, KEGG SMILES
    <work>/models/      SBML models, curated (fetched) and draft (built by 06)
    <work>/tables/      everything a script writes
    <work>/notes/       written record

    <external>/         third-party code, weights and databases -- NOT tracked,
                        fetched by fetch_external.sh (default tools/reconstruction/external)
    <proteomes>/        one FASTA (or UniProt TSV) per taxon

The final step is not here: `to_strain_inputs.py` turns ``<work>/tables`` into a
populated ``strains/<name>/`` folder. Nothing in this directory implements the model.
"""
from __future__ import annotations

import os
from pathlib import Path

_CFG = None

DEFAULT_CONFIG = Path(__file__).resolve().parent / "reconstruction.yaml"


def _load_yaml(path: Path) -> dict:
    import yaml
    with open(path) as fh:
        return yaml.safe_load(fh) or {}


def find_config(explicit: str | None = None) -> Path:
    for cand in (explicit, os.environ.get("RECON_CONFIG"),
                 "reconstruction.yaml", str(DEFAULT_CONFIG)):
        if cand and Path(cand).exists():
            return Path(cand).resolve()
    raise FileNotFoundError(
        "no reconstruction config found; pass --config, set $RECON_CONFIG, or run "
        "from a directory containing reconstruction.yaml")


def configure(explicit: str | None = None, work_dir: str | None = None,
              external: str | None = None, proteomes: str | None = None,
              out_strain: str | None = None) -> dict:
    """Load the reconstruction config and populate this module's path globals.

    Every argument overrides the corresponding config key, so a script can expose
    ``--work``, ``--external``, ``--proteomes`` and ``--out-strain`` and have them win.
    Returns the resolved config dict; the globals below are set as a side effect so
    that ``from paths import *`` keeps working the way ``from gempaths import *`` did.
    """
    global _CFG, PROJECT, WORK, INPUTS, MODELS, TABLES, EXTERNAL, NOTES
    global PROTEOMES, PROTEOME, SP, STRAIN_OUT, NAME
    cfg_path = find_config(explicit)
    cfg = _load_yaml(cfg_path)
    here = Path(__file__).resolve().parent
    base = cfg_path.parent

    def _p(v, default):
        v = v if v is not None else default
        p = Path(os.path.expandvars(str(v))).expanduser()
        return p if p.is_absolute() else (base / p).resolve()

    NAME = cfg.get("name", "reconstruction")
    PROJECT = _p(cfg.get("project_root"), here.parent.parent)
    WORK = _p(work_dir or cfg.get("work_dir"), here / "work" / NAME)
    EXTERNAL = _p(external or cfg.get("external_dir"), here / "external")
    PROTEOMES = _p(proteomes or cfg.get("proteomes_dir"), WORK / "proteomes")
    STRAIN_OUT = _p(out_strain or cfg.get("strain_out_dir"), PROJECT / "strains")
    INPUTS, MODELS, TABLES, NOTES = (WORK / "inputs", WORK / "models",
                                     WORK / "tables", WORK / "notes")
    for d in (INPUTS, MODELS, TABLES, NOTES):
        d.mkdir(parents=True, exist_ok=True)

    # taxa: name -> (model file, medium file); and where its sequences come from.
    SP = {k: (v["model"], v["medium"]) for k, v in (cfg.get("taxa") or {}).items()}
    PROTEOME = {}
    for k, v in (cfg.get("taxa") or {}).items():
        pr = v.get("proteome")
        if pr:
            PROTEOME[k] = _p(pr, PROTEOMES / pr) if os.path.isabs(str(pr)) else (
                PROTEOMES / pr if not str(pr).startswith((".", "/")) else _p(pr, pr))
    _CFG = cfg
    return cfg


def config() -> dict:
    if _CFG is None:
        configure()
    return _CFG


def load_proteome(sp):
    """gene id -> amino-acid sequence for one taxon (terminal '*' and 'X' removed).

    FASTA is keyed by record id; a UniProt TSV by every name in its
    'Gene Names (ordered locus)' column, first entry winning. Unchanged from the
    standalone; only the file location is now configured."""
    import pandas as pd
    if _CFG is None:
        configure()
    path = Path(PROTEOME[sp])
    out = {}
    if path.suffix == ".tsv":
        t = pd.read_csv(path, sep="\t", dtype=str).fillna("")
        for _, r in t.iterrows():
            for g in r["Gene Names (ordered locus)"].split():
                out.setdefault(g, r["Sequence"])
    else:
        from Bio import SeqIO
        for rec in SeqIO.parse(str(path), "fasta"):
            out.setdefault(rec.id, str(rec.seq))
    return {k: v.rstrip("*").replace("X", "") for k, v in out.items()}


def add_common_args(ap):
    """Attach the four path overrides every script in this directory accepts."""
    ap.add_argument("--config", default=None, help="reconstruction.yaml (see paths.py)")
    ap.add_argument("--work", default=None, help="work directory (inputs/models/tables/notes)")
    ap.add_argument("--external", default=None, help="third-party code/weights/databases")
    ap.add_argument("--proteomes", default=None, help="directory of per-taxon proteomes")
    ap.add_argument("--out-strain", dest="out_strain", default=None,
                    help="where populated strains/<name>/ folders are written")
    return ap


def cli_configure(argv=None):
    """Apply --config/--work/--external/--proteomes/--out-strain from the command line.

    Uses ``parse_known_args`` so a script keeps its own arguments; call it right after
    ``from paths import *``. This is the only line each ported pipeline script needed:
    the standalone's `gempaths` fixed one layout, here the layout is an argument."""
    import argparse
    ap = add_common_args(argparse.ArgumentParser(add_help=False))
    args, _ = ap.parse_known_args(argv)
    return configure_from_args(args)


def configure_from_args(args):
    return configure(getattr(args, "config", None), getattr(args, "work", None),
                     getattr(args, "external", None), getattr(args, "proteomes", None),
                     getattr(args, "out_strain", None))


# Populate on import so `from paths import *` behaves like the standalone's
# `from gempaths import *`; a script that parses arguments calls configure_from_args
# afterwards to apply its overrides.
configure()

__all__ = ["PROJECT", "WORK", "INPUTS", "MODELS", "TABLES", "EXTERNAL", "NOTES",
           "PROTEOMES", "PROTEOME", "SP", "STRAIN_OUT", "NAME",
           "configure", "configure_from_args", "cli_configure", "add_common_args", "config",
           "find_config", "load_proteome"]
