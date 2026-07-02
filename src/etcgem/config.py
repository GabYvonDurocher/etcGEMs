"""Config loading and provider dispatch for the CLI."""
from __future__ import annotations

import json
import os
from typing import Any, Dict

import numpy as np

from . import providers


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
