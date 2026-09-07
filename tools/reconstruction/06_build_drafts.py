"""06_build_drafts.py -- sequence-linked GPRs for C. auris, C. haemulonii and C. duobushaemulonii
from the curated iRV973 scaffold and each species' own KO annotation.

Why the same procedure is applied to C. auris itself. iRV973's gene-protein-reaction rules
use B8441 GenBank locus tags (CJI97_*) that exist in no protein-sequence database, so the
curated model cannot be linked to sequences as published. Re-keying it by the procedure
below onto the B8441 RefSeq proteome (XP_ accessions) gives auris_iRV973_rekeyed.xml, the
model every downstream script uses; regenerating it here reproduces the committed file's
GPRs reaction for reaction (checked 2026-09-06: 2510 of 2510 metabolic reactions).

Method (scaffold projection, NOT deletion-only), identical for the three species:
  * keep the auris reaction network intact (no deletion on sparse evidence);
  * assign each metabolic reaction's GPR from the TARGET species' own genes, by evidence:
    KO -> KEGG reaction (primary, via inputs/ko_reaction.list) then KO -> EC number
    (secondary, via KOfam's ko_list), the KOs coming from KofamScan (04_kofam_annotate.sh);
  * reactions with no species evidence are KEPT but GPR-cleared and flagged orphan;
  * all CJI97 ids are removed, so every gene in every model has a sequence.
Limitation (disclosed): KO/EC evidence yields isozyme-OR rules. The curated enzyme-complex
AND structure is not reconstructed, for C. auris either; the models have only a handful of
transporter complexes, so all GPRs are treated as isozyme OR (<work>/audits/sens_complex.py
tests the SUM-of-subunits alternative).
C. parapsilosis keeps its curated iDC1003 GPRs, which are already CPAR2_ locus tags.

    python3 tools/reconstruction/06_build_drafts.py
Inputs : <work>/models/<scaffold_model>, <work>/inputs/ko_reaction.list,
         <work>/inputs/kofam/<taxon kofam table>, <external>/kofam/ko_list
         (scaffold_model and the per-taxon kofam/model names come from reconstruction.yaml)
Outputs: <work>/models/<taxon model> for every taxon with a `kofam:` table
         <work>/tables/<taxon>_evidence.csv

PORTED from the standalone Candida etcGEM (Candidas repository, `gem/`) into
tools/reconstruction/ by K1. The ONLY change is that the layout and the taxon map now
come from a reconstruction config (paths.py / reconstruction.yaml) instead of the
standalone's fixed gempaths.py, so this step can build the inputs for any taxon. The
method is unchanged; nothing here implements the model.
"""
import cobra, re, collections, csv
from pathlib import Path
from paths import *  # PROJECT, WORK, INPUTS, MODELS, TABLES, EXTERNAL, NOTES,
                    # PROTEOMES, PROTEOME, SP, STRAIN_OUT, load_proteome
cli_configure()     # --config/--work/--external/--proteomes/--out-strain (paths.py)
# Layout and taxon set from the reconstruction config (was hard-coded in the standalone):
# the scaffold model whose network is projected, and, for every taxon that needs a draft,
# its KofamScan KO table and the model file to write.
_CFG = config()
KOF = WORK / str(_CFG.get("kofam_dir", "inputs/kofam"))
TMPL = MODELS / _CFG["scaffold_model"]
BUILD = [(tag, v["kofam"], v["model"]) for tag, v in _CFG["taxa"].items() if v.get("kofam")]

ko2r=collections.defaultdict(set); ko2ec=collections.defaultdict(set)
for line in open(INPUTS / "ko_reaction.list"):
    a,b=line.split(); ko2r[a.split(":")[1]].add(b.split(":")[1])
for line in open(EXTERNAL / "kofam" / "ko_list"):
    p=line.split("\t")
    if p[0].startswith("K"):
        for ec in re.findall(r"EC:([0-9.\- ]+)",p[-1]):
            for e in ec.split(): ko2ec[p[0]].add(e.strip())

def species_maps(kofile):
    r2g=collections.defaultdict(set); ec2g=collections.defaultdict(set)
    for line in open(kofile):
        c=line.rstrip("\n").split("\t")
        if len(c)>=2 and c[1].startswith("K"):
            for r in ko2r.get(c[1],()): r2g[r].add(c[0])
            for e in ko2ec.get(c[1],()): ec2g[e].add(c[0])
    return r2g,ec2g
def base_R(rid):
    m=re.match(r"(R\d{5})",rid); return m.group(1) if m else None
def rx_ecs(r):
    a=r.annotation.get("ec-code",[]); a=[a] if isinstance(a,str) else a
    return {x for e in a for x in re.split(r"[;, ]+",e) if re.match(r"\d+\.\d+\.\d+\.\d+",x)}

tmpl=cobra.io.read_sbml_model(str(TMPL))
for tag,ko,out_xml in BUILD:
    r2g,ec2g=species_maps(KOF/ko); m=tmpl.copy(); m.id=out_xml[:-4]
    rows=[]
    for r in m.reactions:
        cls=None; genes=set()
        if r.id.startswith(("EX_","Drain")) or r.boundary or "iomass" in r.id:
            cls="exchange/biomass"
        else:
            R=base_R(r.id)
            if R and R in r2g: genes=r2g[R]; cls="KO->R"
            if not genes:
                for e in rx_ecs(r):
                    genes|=ec2g.get(e,set()); genes|=ec2g.get(".".join(e.split(".")[:3])+".-",set())
                if genes: cls="EC"
            if genes: r.gene_reaction_rule=" or ".join(sorted(genes))
            else: r.gene_reaction_rule=""; cls="orphan_no_species_evidence"
        rows.append((r.id, base_R(r.id) or "", ";".join(sorted(rx_ecs(r))), cls,
                     r.gene_reaction_rule))
    cobra.manipulation.remove_genes(m,[g for g in list(m.genes) if not g.reactions],remove_reactions=False)
    cobra.io.write_sbml_model(m,str(MODELS/out_xml))
    with open(TABLES/f"{tag}_evidence.csv","w",newline="") as fh:
        w=csv.writer(fh); w.writerow(["reaction","kegg_R","EC","evidence_class","GPR"]); w.writerows(rows)
    ev=collections.Counter(r[3] for r in rows)
    prefix=_CFG.get("gene_id_prefix","XP_")   # was hard-coded XP_ (RefSeq); a diagnostic only
    foreign=sum(1 for g in m.genes if not g.id.startswith(prefix))
    print(f"{tag}: growth {m.slim_optimize():.3f}/h | genes {len(m.genes)} (foreign {foreign}) | "
          +", ".join(f"{k}={v}" for k,v in ev.most_common()))
