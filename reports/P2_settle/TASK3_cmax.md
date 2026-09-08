# P2 TASK 3 — where does c_max = 60 come from, and where does it sit?

Gathers and reports. It does **not** change `c_max` and does **not** conclude whether the cap
is fitted — only Parsa can give the intent. Sweep: `python reports/P2_settle/task3_cmax.py`,
numbers in `task3_cmax_table.csv`.

## 1. What justification exists in `$PARSA_ROOT` — searched, and this is all of it

**No literature citation for any value of `c_max` appears anywhere in his folder** — not in
the code, not in the two PDF reports, not in the configuration summary.

What does exist:

* **His own words: it is a swept boundary condition, not a fit.** The configuration summary,
  configuration B: *"Subsequently C_max is swept. … The cap is a boundary condition (a sweep),
  not a fitted likelihood, so it is not scored by R²."*
* **His own sweep, and it does not recommend 60.** The Gas Flux report tabulates C_max
  60 / 100 / 120 / 180 with, in his columns, "growth shape" and "gas (RQ range)":

  | C_max | glucose r_max | NLDM r_max | LB/BHI r_max | growth shape | gas (RQ range) |
  |---|---|---|---|---|---|
  | **60** | 0.83 | 0.97 | 0.93 | **flat plateau** | respiratory (0.90–1.07) |
  | 100 | 1.07 | 1.56 | 1.51 | defined peak | respiratory (0.96–1.10) |
  | 120 | 1.13 | 1.73 | 1.70 | near-clean peak | respiratory near opt. |
  | 180 | 1.17 | 2.03 | 1.99 | clean peak | **degrading** (glc 0.67) |

  and his key finding reads: *"A tight cap gives respiratory gas but a flat growth plateau; a
  loose cap gives a peaked TPC but fermentative gas. **C_max ≈ 100–120 is the sweet spot**."*
  **His own analysis prefers 100–120 and describes 60 as a flat plateau.**
* **Where 60 actually appears:** only as the representative configuration-B run in the later
  *configuration summary* (Figure B2), whose CSV is dated 2026-09-01 — after the Gas Flux
  report's sweep. The driver script's own default is `--caps 80 100`, and his other committed
  cap runs are C60/C80/C100/C120/C180.
* **Configuration D uses a different construction entirely:** there the cap is *fitted*, as
  `C_max_mult × C_MAX_NOM` with `C_MAX_NOM = 230.0` ("NLDM nominal; fitted as a multiplier of
  this"). So "the carbon cap" means a swept boundary condition in B and a fitted parameter in
  D, and 60 belongs to the first sense only.
* **One dead end, recorded so nobody re-treads it:** `scripts_posterior_configD_capfit.py`
  reports a "best-match cap" against Basan's line. Re-evaluating its own committed output, that
  best match is **c_max = 30**, where the model's acetate and Basan's line are *both zero* —
  the minimiser is matching 0 to 0 at the bottom of the sweep. It is not a provenance for 60 or
  for anything else.

**Not found:** any statement of why 60 rather than 100–120, in code, comment, report or figure
caption.

## 2. The sensitivity, tabulated

Two media, cap from off to strongly binding, 5–52 °C on 95 points, everything else at the v3
posterior operating point.

| medium | c_max | T_opt | r_max | CT_max | CT_min | niche | E_a | O₂ | CO₂ | acetate | RQ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| glucose | off | 38.0 | 1.1949 | 40.98 | 15.90 | 25.08 | 0.975 | 48.14 | 0.92 | 0 | 0.019 |
| glucose | 230 | 38.0 | 1.1869 | 40.98 | 15.87 | 25.11 | 0.974 | 29.56 | 6.44 | 5.52 | 0.218 |
| glucose | 180 | 38.0 | 1.1704 | 40.98 | — | — | 0.969 | — | — | 17.55 | 0.673 |
| glucose | 150 | 38.0 | 1.1605 | 40.99 | — | — | 0.964 | — | — | 24.76 | 0.983 |
| glucose | 120 | 38.0 | 1.1251 | 40.99 | — | — | 0.993 | — | — | 23.53 | 1.099 |
| glucose | 100 | 38.0 | 1.0714 | 41.02 | — | — | 0.977 | — | — | 14.88 | 1.095 |
| glucose | 80 | 38.0 | 0.9778 | 41.08 | — | — | 0.966 | — | — | 5.53 | 1.078 |
| glucose | **60** | **37.5** | 0.8269 | 41.18 | 14.66 | 26.52 | 0.989 | 24.30 | 26.06 | **0** | 1.073 |
| glucose | 50 | 36.5 | 0.7036 | 41.26 | — | — | 1.090 | — | — | 0 | 1.076 |
| glucose | 40 | 35.5 | 0.5628 | 41.35 | — | — | 1.195 | — | — | 0 | 1.076 |
| NLDM | off | 39.0 | 1.9110 | 46.08 | 14.43 | 31.65 | 0.949 | 36.58 | 38.21 | 24.99 | 1.044 |
| NLDM | 230 | 39.0 | 1.9110 | 46.08 | 14.43 | 31.65 | 0.949 | 36.58 | 38.21 | 24.99 | 1.044 |
| NLDM | 180 | 39.0 | 1.9001 | 46.08 | — | — | 0.949 | — | — | 29.46 | 1.219 |
| NLDM | 150 | 39.0 | 1.8252 | 46.11 | — | — | 0.964 | — | — | 18.25 | 1.108 |
| NLDM | 120 | 39.5 | 1.6815 | 46.15 | — | — | 0.952 | — | — | 3.90 | 1.109 |
| NLDM | 100 | 39.5 | 1.5239 | 46.20 | — | — | 0.981 | — | — | 0 | 1.020 |
| NLDM | 80 | 39.0 | 1.2595 | 46.29 | — | — | 1.075 | — | — | 0 | 0.973 |
| NLDM | **60** | **32.5** | 0.9544 | 46.38 | 12.28 | 34.10 | **1.230** | 22.45 | 20.83 | **0** | 0.928 |
| NLDM | 50 | 30.5 | 0.7988 | 46.43 | — | — | 1.307 | — | — | 0 | 0.901 |
| NLDM | 40 | 29.5 | 0.6395 | 46.48 | — | — | 1.374 | — | — | 0 | 0.896 |

Full columns in `task3_cmax_table.csv`.

## 3. Where the thermal descriptors start to move — and where 60 sits

Change against the uncapped run:

| c_max | glucose T_opt | glucose E_a | NLDM T_opt | NLDM E_a | CT_max (either) |
|---|---|---|---|---|---|
| 230 | 0.00 % | 0.07 % | 0.00 % | 0.00 % | ≤0.00 % |
| 180 | 0.00 % | 0.57 % | 0.00 % | 0.05 % | ≤0.01 % |
| 150 | 0.00 % | 1.10 % | 0.00 % | 1.61 % | ≤0.06 % |
| 120 | 0.00 % | 1.86 % | **1.28 %** | 0.33 % | ≤0.16 % |
| 100 | 0.00 % | 0.27 % | 1.28 % | 3.33 % | ≤0.27 % |
| 80 | 0.00 % | 0.94 % | 0.00 % | **13.27 %** | ≤0.45 % |
| **60** | **1.32 %** | 1.46 % | **16.67 %** | **29.61 %** | ≤0.66 % |
| 50 | 3.95 % | 11.86 % | 21.79 % | 37.71 % | ≤0.76 % |
| 40 | 6.58 % | 22.62 % | 24.36 % | 44.74 % | ≤0.91 % |

**T_opt is flat down to c_max ≈ 150 and then is not.** On NLDM it holds 39.0 °C from off to
150, moves half a degree at 120–100, returns at 80, and then **falls to 32.5 °C at 60** — a
6.5 °C drop across a single step of the sweep. On glucose it holds 38.0 °C all the way to 80
and first moves at 60.

**E_a behaves the same way**, one step earlier on NLDM: 0.949 eV down to 150, then 1.075 at 80
and **1.230 at 60** (+29.6 %).

**CT_max is insensitive throughout**: ≤0.66 % at c_max = 60 and ≤0.91 % even at 40, monotone
and small. It is the one descriptor the cap does not touch.

### The answer to the question a reader needs

**c_max = 60 does not sit in a flat region. It sits past the steepest part of the slope.** On
NLDM the thermal descriptors are flat from ∞ down to about 150, begin to stir between 120 and
80, and change abruptly between 80 and 60 — T_opt −6.5 °C, E_a +30 %. The value his
configuration-B figures use is on the far side of that transition, not before it.

Two further observations, reported not adjudicated:

* **At c_max = 60 there is no acetate overflow at all**, on either medium (glucose 0 from 60
  down; NLDM 0 from 100 down). His own 37 °C sweep agrees: on glucose, overflow begins only
  above c_max ≈ 65–70. So the cap value used for the configuration-B gas-exchange figures is
  one at which the emergent overflow configuration D exists to produce has been suppressed
  entirely.
* **r_max, unlike the shape descriptors, moves continuously** from the first binding cap
  (0.67 % at 230 on glucose) — there is no flat region for it at all, so "the cap does not
  affect growth" is not available at any value.
