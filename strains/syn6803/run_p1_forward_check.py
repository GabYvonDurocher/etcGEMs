#!/usr/bin/env python
"""P1 forward-check for the Synechocystis 6803 etc-GEM scaffold.

Reproduces the P1 result: the PLAIN base GEM (iSynCJ816) is photon-LINEAR (photon always
binds -- a stoichiometric model has no per-throughput enzyme cap), while the enzyme-
constrained ecModel (iSynCJ816_STAR) delivers LIGHT SATURATION -- under saturating light
and pure autotrophy the enzyme pool binds and the photon exchange goes SLACK (shadow price
0), i.e. carbon-fixation CAPACITY sets the rate. This is the in-mechanism confirmation.

Run from the strain dir or repo root with the venv + Gurobi active. The ecModel path
points at the local copy under model/ecmodel_iSynCJ816_STAR/.
"""
import logging, warnings, os
logging.getLogger("cobra").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")
import cobra
cobra.Configuration().solver = "gurobi"

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "model", "iSynCJ816.xml")
ECM = os.path.join(HERE, "model", "ecmodel_iSynCJ816_STAR", "iSynCJ816_STAR.xml")
E = lambda i: f"EX_{i}_e"
BIOMASS = "BIOMASS_Ec_SynAuto_1"


def autotrophic_medium(m, photon_lb):
    """Light-saturated photoautotrophic medium: photon non-limiting, inorganic C available,
    organic C closed."""
    if E("glc__D") in [r.id for r in m.reactions]:
        m.reactions.get_by_id(E("glc__D")).lower_bound = 0.0          # close organic C
    for oc in ("ac", "pyr", "succ", "glcglyc"):
        if E(oc) in [r.id for r in m.reactions]:
            m.reactions.get_by_id(E(oc)).lower_bound = 0.0
    m.reactions.get_by_id(E("co2")).lower_bound = -1000.0             # inorganic C (CO2)
    m.reactions.get_by_id("EX_photon_e").lower_bound = -float(photon_lb)  # saturating light
    m.objective = BIOMASS
    return m


def main():
    print("=== PLAIN base GEM (iSynCJ816): photon-linear, photon always binds ===")
    base = cobra.io.read_sbml_model(BASE)
    for ph in (100, 1000, 10000, 100000):
        mm = autotrophic_medium(base.copy(), ph)
        s = mm.optimize()
        used = -s.fluxes["EX_photon_e"]
        print(f"  photon<={ph:7d}  mu={s.objective_value:9.4f}  photon_used={used:9.1f}  "
              f"binds={used >= ph - 1e-3}  RuBisCO={s.fluxes.get('RBPC_1', 0):.3f}")

    print("\n=== enzyme-constrained ecModel (iSynCJ816_STAR): light SATURATES ===")
    ec = cobra.io.read_sbml_model(ECM)
    pool = ec.reactions.get_by_id("ER_pool_TG_")
    for ph in (10, 24, 50, 1000, 999999):
        mm = autotrophic_medium(ec.copy(), ph)
        s = mm.optimize()
        used = -s.fluxes["EX_photon_e"]
        pd = s.fluxes["ER_pool_TG_"]
        print(f"  photon<={ph:7d}  mu={s.objective_value:7.4f}  photon_used={used:7.2f}  "
              f"photon_binds={used >= ph - 1e-3}  pool={pd:.4f}/{pool.upper_bound} "
              f"binds={abs(pd - pool.upper_bound) < 1e-4}")
    mm = autotrophic_medium(ec.copy(), 999999)
    s = mm.optimize()
    print(f"\n  saturating light, PURE autotrophy: mu={s.objective_value:.4f}  "
          f"glucose={-s.fluxes['EX_glc__D_e']:.3f}  RuBisCO RBPC_1={s.fluxes['RBPC_1']:.3f}  "
          f"photoresp RBCh_2={s.fluxes.get('RBCh_2', 0):.3f}")
    print(f"  photon shadow price={s.reduced_costs['EX_photon_e']:.2e} (~0 -> NON-binding, light-saturated)")
    print(f"  enzyme-pool draw={s.fluxes['ER_pool_TG_']:.4f}/{pool.upper_bound} "
          f"(binds -> carbon-fixation-capacity limited = in-mechanism)")


if __name__ == "__main__":
    main()
