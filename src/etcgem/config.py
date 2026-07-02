"""Config loading and provider dispatch for the CLI.

Three-tier config model, merged as ``defaults <- strain <- experiment``:

* ``defaults.yaml`` (project root)      -- universal METHOD defaults only
  (solver_timeout, crit_frac, a fallback temperature_grid).
* ``strains/<name>/strain.yaml``        -- ORGANISM only (provider block, T0_C,
  temperature_grid); self-sufficient to build + run the model.
* ``experiments/<name>.yaml``           -- OPTIONAL method overlays (kind +
  sensitivity / decomposition blocks).

``resolve(strain, experiment=None)`` returns the merged dict with
``provider.model_path`` injected; ``dump_resolved`` records the exact merged
config into each run's output folder.
"""
from __future__ import annotations

import copy
import json
import os
from typing import Any, Dict, Optional

import numpy as np

from . import providers

# Project-root-relative locations (commands run from the project root).
DEFAULTS_FILE = "defaults.yaml"
STRAINS_DIR = "strains"
EXPERIMENTS_DIR = "experiments"


def load_config(path: str) -> Dict[str, Any]:
    with open(path) as fh:
        text = fh.read()
    if path.lower().endswith((".yaml", ".yml")):
        try:
            import yaml
            return yaml.safe_load(text)
        except ImportError as e:
            raise ImportError("Install pyyaml, or use a .json config.") from e
    return json.loads(text)


# ---------------------------------------------------------------------------
# three-tier config model
# ---------------------------------------------------------------------------
def _deep_merge(base: Dict[str, Any], over: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge ``over`` onto a copy of ``base`` (dicts merge, scalars/
    lists replace)."""
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def strain_dir(name: str) -> str:
    return os.path.abspath(os.path.join(STRAINS_DIR, name))


def load_defaults() -> Dict[str, Any]:
    return load_config(DEFAULTS_FILE) if os.path.exists(DEFAULTS_FILE) else {}


def load_strain(name: str) -> Dict[str, Any]:
    return load_config(os.path.join(strain_dir(name), "strain.yaml"))


def load_experiment(name: str) -> Dict[str, Any]:
    return load_config(os.path.join(EXPERIMENTS_DIR, f"{name}.yaml"))


def resolve(strain: str, experiment: Optional[str] = None) -> Dict[str, Any]:
    """Compose defaults <- strain <- experiment and inject provider.model_path.

    Organism keys come from the strain; method keys from defaults, overridden by
    the experiment. The absolute model path is derived from the strain folder +
    ``provider.model_file``; ``output_dir`` is left for the CLI to set per run.
    """
    cfg = _deep_merge(load_defaults(), load_strain(strain))
    if experiment:
        cfg = _deep_merge(cfg, load_experiment(experiment))
    model_file = cfg.get("provider", {}).get("model_file")
    if model_file:
        cfg["provider"]["model_path"] = os.path.join(strain_dir(strain), "model", model_file)
    cfg.setdefault("_strain", strain)
    if experiment:
        cfg["_experiment"] = experiment
    return cfg


def dump_resolved(cfg: Dict[str, Any], out_dir: str) -> str:
    """Write the exact merged config used for a run into its output folder."""
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "resolved_config.yaml")
    try:
        import yaml
        with open(path, "w") as fh:
            yaml.safe_dump(cfg, fh, sort_keys=False)
    except ImportError:
        with open(path.replace(".yaml", ".json"), "w") as fh:
            json.dump(cfg, fh, indent=2)
        path = path.replace(".yaml", ".json")
    return path


def build_provider(cfg: Dict[str, Any]):
    p = cfg["provider"]
    T0 = (cfg.get("T0_C", 30.0)) + 273.15
    kind = p["type"]
    if kind == "toy":
        return providers.toy_ecoli_core(
            T0=T0, seed=p.get("seed", 0),
            topt_mean_offset=p.get("topt_mean_offset", 8.0),
            topt_sd=p.get("topt_sd", 6.0),
            dCp_mean=p.get("dCp_mean", -8.0),
            target_fraction=p.get("target_fraction", 0.6),
        )
    if kind == "gecko":
        return providers.from_gecko(
            model_path=p["model_path"], T0=T0,
            default_Topt_offset=p.get("default_Topt_offset", 7.0),
            default_dCp=p.get("default_dCp", -12.0),
            prot_prefix=p.get("prot_prefix", "prot_"),
            pool_id=p.get("pool_id", "prot_pool"),
            biomass_rxn=p.get("biomass_rxn"),
            target_fraction=p.get("target_fraction"),
            pool_scale=p.get("pool_scale", 1.0),
        )
    if kind == "csv":
        return providers.from_kcat_csv(
            model_path=p["model_path"], csv_path=p["csv_path"], T0=T0,
            default_Topt_offset=p.get("default_Topt_offset", 8.0),
            default_dCp=p.get("default_dCp", -8.0),
            biomass_rxn=p.get("biomass_rxn"),
            target_fraction=p.get("target_fraction", 0.6),
        )
    raise ValueError(f"Unknown provider type: {kind}")


def temperature_grid(cfg: Dict[str, Any]) -> np.ndarray:
    g = cfg["temperature_grid"]
    return np.linspace(g["start_C"], g["stop_C"], int(g["n"]))
