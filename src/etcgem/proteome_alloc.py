"""Temperature-dependent proteome allocation grounded in measured *E. coli*
proteomics (Wang et al. 2026, github.com/DeyuWang-itp/protein_allocation).

The unfolding thermal model grounds the enzyme *envelope* in per-enzyme melting
temperatures; this module grounds the temperature dependence of proteome
*allocation* in a temperature-resolved proteome. It is a data product + an opt-in
model input, and is fully backward compatible: nothing here runs unless a strain /
experiment sets ``allocation_from_data``.

Pipeline
--------
1. Map each measured protein (b-number ``Accession``) to a coarse proteome sector
   via its COG functional category (:data:`COG_SECTOR_MAP`).
2. Compute MASS-weighted sector fractions at each LB temperature (16/25/30/37/43 C)
   -- weighting each protein's replicate-averaged abundance by its molecular weight
   (residue count x 110 Da) -- giving f_metab, f_bio, f_chaperone, f_other summing
   to 1 at each temperature.
3. Map proteins to eciML1515 enzymes (UniProt) via the model's gene<->protein links
   (b-number gene id <-> ``prot_<UniProt>``), for the predicted-vs-measured test.
4. Supply a temperature-dependent sector allocation to the sector model: the model's
   three sectors (metabolic / biosynthesis / maintenance) are moved with temperature
   by the *relative* change in the measured fractions, anchored at a reference
   temperature so the nominal calibration is preserved there.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np
import pandas as pd

# COG one-letter functional category -> coarse proteome sector. Multi-letter COG
# strings use their first (primary) letter. Documented, configurable default.
COG_SECTOR_MAP: Dict[str, str] = {
    "J": "f_bio",         # translation / ribosome biogenesis
    "O": "f_chaperone",   # post-translational modification, chaperones, stress
    # metabolism (energy, carbohydrate, amino-acid, nucleotide, coenzyme, lipid,
    # inorganic-ion, secondary-metabolite transport & metabolism):
    "C": "f_metab", "G": "f_metab", "E": "f_metab", "F": "f_metab",
    "H": "f_metab", "I": "f_metab", "P": "f_metab", "Q": "f_metab",
    # everything else (K,L,D,M,N,T,U,V,W,Y,Z,S,R and blank) -> housekeeping/other
}
SECTORS = ["f_metab", "f_bio", "f_chaperone", "f_other"]
LB_TEMPS = [16, 25, 30, 37, 43]
_MW_PER_RESIDUE = 110.0   # Da; mean residue mass for a length-based MW estimate


def sector_of(cog) -> str:
    """Map a COG category (possibly multi-letter or blank) to a coarse sector."""
    if cog is None or (isinstance(cog, float) and np.isnan(cog)):
        return "f_other"
    c = str(cog).strip()
    return COG_SECTOR_MAP.get(c[:1], "f_other") if c else "f_other"


# ---------------------------------------------------------------------------
# identifier mapping: proteomics b-number -> model UniProt enzyme id
# ---------------------------------------------------------------------------
def build_b_to_uniprot(model, prot_prefix: str = "prot_") -> Dict[str, str]:
    """Map iML1515 gene b-numbers to GECKO UniProt ids using the model's own
    gene<->protein links: a reaction that consumes exactly one ``prot_<UniProt>``
    and carries gene(s) pins those b-numbers to that UniProt."""
    from .providers import _clean_uniprot
    out: Dict[str, str] = {}
    for rxn in model.reactions:
        prots = [x.id for x in rxn.metabolites
                 if x.id.startswith(prot_prefix) and "pool" not in x.id
                 and rxn.metabolites[x] < 0]
        if len(prots) == 1 and rxn.genes:
            u = _clean_uniprot(prots[0], prot_prefix)
            for g in rxn.genes:
                out.setdefault(g.id, u)
    return out


# ---------------------------------------------------------------------------
# load + annotate the temperature proteome
# ---------------------------------------------------------------------------
def load_temperature_proteome(path: str, b_to_uniprot: Optional[Dict[str, str]] = None,
                              temps=LB_TEMPS) -> pd.DataFrame:
    """Read tem_proteomic.csv, average LB replicates per temperature, assign a
    sector and a length-based MW, and (optionally) join UniProt ids.

    Returns a DataFrame with columns: Accession, genename, COG, sector, MW,
    UniProt (if a map is given) and one abundance column ``ab_<T>`` per temperature.
    """
    df = pd.read_csv(path)
    df["sector"] = df["COG"].map(sector_of)
    df["MW"] = df["protein_sequence"].astype(str).str.len() * _MW_PER_RESIDUE
    for T in temps:
        cols = [c for c in (f"LB{T}_1_norm", f"LB{T}_2_norm") if c in df.columns]
        df[f"ab_{T}"] = df[cols].mean(axis=1) if cols else np.nan
    if b_to_uniprot is not None:
        df["UniProt"] = df["Accession"].map(b_to_uniprot)
    return df


def sector_fractions_vs_T(df: pd.DataFrame, temps=LB_TEMPS) -> pd.DataFrame:
    """MASS-weighted sector mass fractions at each temperature (rows: temperature;
    columns: the four sectors, summing to 1)."""
    rows = {}
    for T in temps:
        mass = df[f"ab_{T}"] * df["MW"]
        by = mass.groupby(df["sector"]).sum()
        tot = by.sum()
        rows[T] = {s: float(by.get(s, 0.0) / tot) if tot > 0 else np.nan for s in SECTORS}
    out = pd.DataFrame(rows).T
    out.index.name = "temp_C"
    return out[SECTORS]


# ---------------------------------------------------------------------------
# temperature-dependent allocation for the sector model
# ---------------------------------------------------------------------------
@dataclass
class TemperatureAllocation:
    """Maps a temperature (C) to model sector fractions (f_metab, f_maint) from
    measured proteomics. The model's three sectors (metabolic / biosynthesis /
    maintenance) map onto the four measured sectors as

        f_metab(model)  <- f_metab(measured)
        f_maint(model)  <- f_chaperone + f_other (measured)
        f_bio(model)    <- f_bio(measured)   (= 1 - f_metab - f_maint)

    To preserve the nominal calibration, the model fractions are scaled by the
    *relative* change of the measured fractions about a reference temperature
    (default 30 C, the model T0): at the reference the allocation equals the
    strain's nominal sectors, and its temperature dependence follows the data.
    Outside [min, max] measured temperature the fractions are clamped."""
    temps: np.ndarray                # measured temperatures (C)
    emp_metab: np.ndarray            # measured f_metab(T)
    emp_maint: np.ndarray            # measured f_chaperone + f_other (T)
    ref_C: float = 30.0
    f_metab_nom: float = 0.5
    f_maint_nom: float = 0.15

    @classmethod
    def from_fractions(cls, sf: pd.DataFrame, ref_C: float = 30.0,
                       f_metab_nom: float = 0.5, f_maint_nom: float = 0.15):
        temps = sf.index.to_numpy(float)
        return cls(temps=temps,
                   emp_metab=sf["f_metab"].to_numpy(float),
                   emp_maint=(sf["f_chaperone"] + sf["f_other"]).to_numpy(float),
                   ref_C=ref_C, f_metab_nom=f_metab_nom, f_maint_nom=f_maint_nom)

    def _interp(self, arr, T_C):
        lo, hi = float(self.temps.min()), float(self.temps.max())
        return float(np.interp(np.clip(T_C, lo, hi), self.temps, arr))

    def model_alloc(self, T_C: float):
        """Return (f_metab, f_maint) for the sector model at temperature T_C."""
        m_ref = self._interp(self.emp_metab, self.ref_C)
        mt_ref = self._interp(self.emp_maint, self.ref_C)
        f_metab = self.f_metab_nom * (self._interp(self.emp_metab, T_C) / m_ref) if m_ref > 0 else self.f_metab_nom
        f_maint = self.f_maint_nom * (self._interp(self.emp_maint, T_C) / mt_ref) if mt_ref > 0 else self.f_maint_nom
        # keep the simplex valid (f_bio = 1 - f_metab - f_maint > 0)
        if f_metab + f_maint > 0.95:
            s = 0.95 / (f_metab + f_maint)
            f_metab, f_maint = f_metab * s, f_maint * s
        return f_metab, f_maint


# ---------------------------------------------------------------------------
# predicted-vs-measured validation (PART 4)
# ---------------------------------------------------------------------------
def measured_enzyme_mass(df: pd.DataFrame, T: int) -> pd.Series:
    """Measured per-enzyme mass (abundance x MW) at temperature T, aggregated by
    UniProt over mapped proteins."""
    d = df.dropna(subset=["UniProt"]).copy()
    d["mass"] = d[f"ab_{T}"] * d["MW"]
    return d.groupby("UniProt")["mass"].sum()


def enzyme_sector(df: pd.DataFrame) -> Dict[str, str]:
    """UniProt -> sector (from the protein's COG)."""
    d = df.dropna(subset=["UniProt"])
    return dict(zip(d["UniProt"], d["sector"]))


def predicted_enzyme_mass(pm, T_C: float) -> pd.Series:
    """Predicted per-enzyme proteome mass drawn from the pool at temperature T_C:
    cost_i(T)*|v_i| summed by enzyme (UniProt), from an FBA solution that uses the
    same temperature-dependent allocation as the model run."""
    from .enzyme_cost import Perturbation
    ec = pm.ec
    Tk = T_C + 273.15
    ec.set_temperature(Tk, Perturbation())
    if getattr(ec, "_alloc_from_data", None) is not None and ec._sectors is not None:
        fm, fmaint = ec._alloc_from_data.model_alloc(float(T_C))
        ec.set_allocation(fm, fmaint)
    sol = ec.model.optimize()
    costs = ec._costs(Tk, Perturbation())
    mass: Dict[str, float] = {}
    if sol.status == "optimal":
        for i, e in enumerate(ec.table.entries):
            v = abs(sol.fluxes.get(e.rxn_id, 0.0))
            if v > 0 and e.enzyme_id:
                mass[e.enzyme_id] = mass.get(e.enzyme_id, 0.0) + float(costs[i]) * v
    return pd.Series(mass, name="pred", dtype=float)


def validate(pm, df: pd.DataFrame, temps=LB_TEMPS):
    """Predicted-vs-measured per-enzyme usage and sector fractions across
    temperature. Returns (per_enzyme_df, corr_df, pred_sectors_df, meas_sectors_df)."""
    from scipy.stats import spearmanr, pearsonr
    sec = enzyme_sector(df)
    per_rows, corr_rows = [], []
    pred_sec, meas_sec = {}, {}
    for T in temps:
        pred = predicted_enzyme_mass(pm, float(T))
        meas = measured_enzyme_mass(df, T)
        common = pred.index.intersection(meas.index)
        p, m = pred.loc[common].values, meas.loc[common].values
        ok = (p > 0) & (m > 0) & np.isfinite(p) & np.isfinite(m)
        p, m, common = p[ok], m[ok], common[ok]
        rho = float(spearmanr(p, m).correlation) if len(p) > 2 else np.nan
        lp = float(pearsonr(np.log10(p), np.log10(m))[0]) if len(p) > 2 else np.nan
        corr_rows.append({"temp_C": T, "n": len(p), "spearman": rho, "log_pearson_r2": lp**2})
        for u, pi, mi in zip(common, p, m):
            per_rows.append({"temp_C": T, "enzyme_id": u, "sector": sec.get(u, "f_other"),
                             "pred_mass": pi, "meas_mass": mi})
        # sector fractions over the matched (predicted & measured) set
        dfm = pd.DataFrame({"pred": p, "meas": m, "sector": [sec.get(u, "f_other") for u in common]})
        for name, col in (("pred", pred_sec), ("meas", meas_sec)):
            by = dfm.groupby("sector")[name].sum()
            tot = by.sum()
            col[T] = {s: float(by.get(s, 0.0) / tot) if tot > 0 else np.nan for s in SECTORS}
    return (pd.DataFrame(per_rows), pd.DataFrame(corr_rows),
            pd.DataFrame(pred_sec).T[SECTORS], pd.DataFrame(meas_sec).T[SECTORS])


# ---------------------------------------------------------------------------
# figures
# ---------------------------------------------------------------------------
def _mpl():
    from .plotting import _mpl as m
    return m()


def plot_sector_fractions(sf: pd.DataFrame, out_path: str):
    plt = _mpl()
    fig, ax = plt.subplots(figsize=(7, 5))
    colors = {"f_metab": "tab:blue", "f_bio": "tab:green",
              "f_chaperone": "tab:red", "f_other": "0.6"}
    for s in SECTORS:
        ax.plot(sf.index, sf[s], marker="o", label=s, color=colors.get(s))
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("mass fraction of measured proteome")
    ax.set_title("Measured temperature-dependent proteome-sector fractions (E. coli, LB)")
    ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(out_path, dpi=150); plt.close(fig)
    return out_path


def plot_usage_pred_vs_meas(per_df: pd.DataFrame, corr_df: pd.DataFrame, out_path: str):
    plt = _mpl()
    temps = sorted(per_df["temp_C"].unique())
    n = len(temps); ncol = min(3, n); nrow = int(np.ceil(n / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(4 * ncol, 3.6 * nrow))
    axes = np.atleast_1d(axes).ravel()
    for ax, T in zip(axes, temps):
        sub = per_df[per_df.temp_C == T]
        ax.scatter(sub.meas_mass, sub.pred_mass, s=8, alpha=0.4, color="tab:blue")
        ax.set_xscale("log"); ax.set_yscale("log")
        c = corr_df[corr_df.temp_C == T].iloc[0]
        ax.set_title(f"{T}°C  ρ={c.spearman:.2f}  log-R²={c.log_pearson_r2:.2f} (n={int(c.n)})", fontsize=9)
        ax.set_xlabel("measured mass"); ax.set_ylabel("predicted mass")
    for ax in axes[n:]:
        ax.axis("off")
    fig.suptitle("Predicted vs measured per-enzyme proteome mass")
    fig.tight_layout(); fig.savefig(out_path, dpi=150); plt.close(fig)
    return out_path


def plot_sector_pred_vs_meas(pred_sec: pd.DataFrame, meas_sec: pd.DataFrame, out_path: str):
    plt = _mpl()
    fig, ax = plt.subplots(figsize=(7, 5))
    colors = {"f_metab": "tab:blue", "f_bio": "tab:green",
              "f_chaperone": "tab:red", "f_other": "0.6"}
    for s in SECTORS:
        ax.plot(meas_sec.index, meas_sec[s], marker="o", ls="-", color=colors[s], label=f"{s} measured")
        ax.plot(pred_sec.index, pred_sec[s], marker="s", ls="--", color=colors[s], label=f"{s} predicted")
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("sector mass fraction (matched enzymes)")
    ax.set_title("Predicted vs measured sector fractions across temperature")
    ax.legend(frameon=False, fontsize=7, ncol=2)
    fig.tight_layout(); fig.savefig(out_path, dpi=150); plt.close(fig)
    return out_path
