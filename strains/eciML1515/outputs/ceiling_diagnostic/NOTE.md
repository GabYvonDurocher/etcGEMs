# Ceiling diagnostic (P2c): what caps rich-BHI growth at ~1.55 h-1

The ~1.55 h-1 rich-medium ceiling (P2 re-run, calibration_vanderlinden_v2) is an
**enzyme-mass PROTEOME constraint, not a non-proteome/structural limit**. Two
redundant proteome pools bind in sequence at the tuned rich/40 C point: the etcgem
sMOMENT sector pool at ~1.44, then the underlying **GECKO base total-protein pool**
`prot_pool_exchange` (ub = 0.091 g enzyme/gDW) at ~1.55. Relaxing ALL proteome
lifts growth to ~7.6 h-1; O2, glucose uptake, ATPM, GAM and biomass precursors
all had slack (not the bottleneck).

`kcat_scale` scales only the etcgem per-flux cost, not the GECKO pool, so kcat
saturates at the GECKO-pool ceiling (~1.55) -- which is why the P2 re-run's kcat
x2.56 reached only 1.44 and the residual looked "structural." It is not: scaling the
total enzyme budget x1.8 reaches the observed ~2.4.

**Classification: PROTEOME (fixable/closable), not structural.** Two things for P3:
(1) the GECKO base pool (0.091 g/gDW) is tighter than and unreconciled with the
emergent P_total x sigma budget -- a fixable inconsistency that should be reconciled
so the magnitude levers act on the true binding pool; (2) closing the full gap needs
~1.8x more enzyme budget (sigma ~0.45 -> ~0.77, above the 0.4-0.5 literature
range), so part of the rich-medium magnitude may be a genuinely higher in-vivo
capacity, not a network gap.
