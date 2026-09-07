# YMS — the medium the four Candida strains are grown on, as the model encodes it

**Source of truth:** `medium_iRV973_auris.csv` in this folder, copied verbatim from
`gem/inputs/medium_iRV973_auris.csv` of the Candidas repository at commit
`f123bc7489cc4f8a1d0e198a93725034c9f347e6`. *C. parapsilosis* uses
`medium_iDC1003_parapsilosis.csv` (same encoding, iDC1003's exchange ids and its own
set of amino acids present). The file is the authority; this note explains it.

## The assay medium

The experiment was run in YMS (yeast extract / mineral salts / sucrose). The models
cannot represent that literally: sucrose has no transporter in either reconstruction
(only a cytoplasmic drain plus invertase R00801), and yeast extract is undefined.
The standalone therefore encodes YMS as

* **carbon** — D-glucose as the sucrose-derived hexose proxy, at a *fitted* uptake
  scale (`setting = FIT`, lower bound −10 mmol/gDW/h);
* **a pooled amino-acid budget** — every proteinogenic amino acid that the
  reconstruction has an exchange for, each at lower bound −3 mmol/gDW/h
  (`setting = AA_POOL`). iRV973 has 17 of 20 (no alanine, asparagine or cysteine
  exchange); iDC1003 has 17 of 20 (no alanine, cysteine or tryptophan). This stands
  in for the yeast extract's organic-N and amino-acid supply and is a *budget*, not a
  pinned uptake: the enzyme-constrained LP decides how much of it to use.
* **biotin, retained as an auxotrophy** — `EX_C00120__extr` is OPEN. Neither model can
  synthesise biotin, so without this exchange nothing grows; yeast extract supplies it.
  This is the one medium component that is load-bearing for feasibility rather than
  for rate.
* **non-limiting inorganics** — O2 (aerobic), ammonia, sulfate, orthophosphate, H+,
  H2O and CO2 at lower bound −1000 (`setting = OPEN`).

Everything else is closed: `apply_exchange_medium` first sets every exchange
(`EX_*`, `Drain*`, or a cobra boundary reaction) to `lower_bound = 0`, so a component
is available only if the medium file lists it.

## How it is applied

`src/etcgem/providers.apply_exchange_medium(model, csv)`, called from
`from_gem_smoment` when `medium.exchange_csv` is set in `strain.yaml`. The three
settings map to the three lower bounds above. This is the same procedure, in the same
order, as the standalone's `setup_pool()` in `gem/18_build_etcgem_tpc.py`; it is a new
function only because the core's existing `set_medium` works on GECKO-split
`EX_<met>_e_REV` uptake reactions, which a plain SBML GEM does not have.

Rows whose `exchange_id` is not an exchange in the model are ignored and counted; the
`missing` row in each file (`setting = ABSENT`) is a deliberate record of the amino
acids the reconstruction lacks, and accounts for the one "absent" component reported
on every build.

## Columns

| column | meaning |
|---|---|
| `role` | what the component is for (carbon, oxygen, …, aa_pool) |
| `exchange_id` | the reaction id in that species' SBML |
| `kegg` | KEGG compound id |
| `name` | compound name |
| `setting` | `OPEN` (lb −1000), `FIT` (lb −10), `AA_POOL` (lb −3), `ABSENT` (record only) |
| `note` | the standalone's own justification for the row |
