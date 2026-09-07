#!/usr/bin/env python3
"""a3_gene_content.py -- N1 TASK 1 / discussion-notes A3: the metabolic gene-content screen.

Presence/absence is the one species difference that needs no new data and no predictor. This
asks it at two levels, which answer different questions:

  (a) PROTEOME level -- what each species' genome encodes. Orthology by DIAMOND blastp, with
      three nested absence criteria so "absent" is a graded claim rather than a binary one:
        no_rbh      no reciprocal best hit               (weakest: paralogy breaks reciprocity)
        no_hit_e10  no hit at all at e < 1e-10           (the pipeline's standard threshold)
        no_hit_e3   no hit at all at e < 1e-3            (strongest evidence of true absence)
  (b) MODEL level -- which of those reached each metabolic model's GPRs at all.

THE TRAP AT LEVEL (b), from K1, stated before any number is printed: the C. haemulonii and
C. duobushaemulonii models are the C. auris NETWORK with genes reassigned by KO evidence
(2863 reactions in all three, 1310-1314 enzyme-costed, differing by 2-4). Their model-level
gene content is therefore nearly identical BY CONSTRUCTION. Only C. parapsilosis, whose
iDC1003 is independently curated (2162 reactions), can differ genuinely at level (b).

NAMESPACES. Each species is taken in the namespace ITS MODEL uses, so level (b) is a direct
lookup: RefSeq XP_ for the three Candidozyma (phylo/proteomes/*.faa) and UniProt/CGD
ordered-locus CPAR2_ for C. parapsilosis (gem/inputs/parap_uniprot.tsv, which is what
iDC1003's GPRs are keyed on). The two are different assemblies of different organisms, so
every cross-species statement here is made by ALIGNMENT, never by identifier.

    python3 reports/N1_overnight/a3_gene_content.py

Reads $CANDIDAS_ROOT read-only and this repository's committed strain models. Writes tables
beside this file. Annotation is whatever the proteome FASTA headers and the repository's
existing KO tables already say; nothing is fetched.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import re
import subprocess
import sys
import tempfile

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SPECIES = ["auris", "haemulonii", "duobushaemulonii", "parapsilosis"]
LABEL = {"auris": "C. auris (clade I)", "haemulonii": "C. haemulonii",
         "duobushaemulonii": "C. duobushaemulonii", "parapsilosis": "C. parapsilosis"}
STRAIN = {"auris": "cauris_iRV973", "haemulonii": "chaemulonii_draft",
          "duobushaemulonii": "cduobushaemulonii_draft",
          "parapsilosis": "cparapsilosis_iDC1003"}
DRAFT_FROM_AURIS = {"haemulonii", "duobushaemulonii"}

# Xiao et al. 2025 candidates, matched on the description text the proteomes already carry.
CANDIDATES = {
    "alternative oxidase (AOX)": r"alternative oxidase",
    "glutaredoxin (GRX5 family)": r"glutaredoxin",
    "iron uptake: ferroxidase / multicopper oxidase (FET3-like)": r"ferroxidase|multicopper oxidase",
    "iron uptake: ferric reductase (FRE-like)": r"ferric.reductase|ferric-chelate reductase",
    "iron uptake: high-affinity iron permease (FTR1-like)": r"iron permease|ferric permease",
    "iron uptake: siderophore transporter (SIT1-like)": r"siderophore",
}


def read_fasta(path):
    """id -> (description, sequence)."""
    out, pid, desc, buf = {}, None, "", []
    for line in open(path):
        if line.startswith(">"):
            if pid:
                out[pid] = (desc, "".join(buf))
            h = line[1:].rstrip("\n")
            pid = h.split()[0]
            desc = h[len(pid):].strip()
            buf = []
        else:
            buf.append(line.strip())
    if pid:
        out[pid] = (desc, "".join(buf))
    return out


def read_parap_tsv(path):
    t = pd.read_csv(path, sep="\t", dtype=str).fillna("")
    out = {}
    for _, r in t.iterrows():
        names = r["Gene Names (ordered locus)"].split()
        if not names:
            continue
        out.setdefault(names[0], (f"UniProt {r['Entry']}", r["Sequence"]))
    return out


def write_fasta(seqs, path):
    with open(path, "w") as fh:
        for k, (_d, s) in seqs.items():
            fh.write(f">{k}\n{s}\n")
    return path


def blast(q, s, td, tag, evalue="1e-3"):
    """One-way DIAMOND blastp, most permissive threshold; returns qid -> (sid, pid, evalue)."""
    db, out = os.path.join(td, f"{tag}.dmnd"), os.path.join(td, f"{tag}.tsv")
    if not os.path.exists(db + ""):
        subprocess.run(["diamond", "makedb", "--in", s, "-d", db, "--quiet"], check=True)
    subprocess.run(["diamond", "blastp", "-q", q, "-d", db, "-o", out, "--sensitive",
                    "--max-target-seqs", "1", "--evalue", evalue, "--quiet", "--outfmt", "6",
                    "qseqid", "sseqid", "pident", "evalue", "bitscore"], check=True)
    best = {}
    for line in open(out):
        qid, sid, pid, ev, bs = line.rstrip("\n").split("\t")
        bs = float(bs)
        if qid not in best or bs > best[qid][3]:
            best[qid] = (sid, float(pid), float(ev), bs)
    return best


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--candidas-root", default=os.environ.get("CANDIDAS_ROOT"))
    ap.add_argument("--workdir", default=None)
    a = ap.parse_args(argv)
    if not a.candidas_root:
        sys.exit("need --candidas-root or $CANDIDAS_ROOT (read-only)")
    C = a.candidas_root

    # ---- proteomes, each in the namespace its model uses -------------------------
    prot = {}
    for sp in SPECIES:
        if sp == "parapsilosis":
            prot[sp] = read_parap_tsv(os.path.join(C, "gem", "inputs", "parap_uniprot.tsv"))
        else:
            f = "auris_cladeI" if sp == "auris" else sp
            prot[sp] = read_fasta(os.path.join(C, "phylo", "proteomes", f"{f}.faa"))
        print(f"{LABEL[sp]:24s} proteome {len(prot[sp])} proteins")

    # ---- model gene sets ---------------------------------------------------------
    import cobra
    import glob
    model_genes = {}
    for sp in SPECIES:
        x = glob.glob(os.path.join(ROOT, "strains", STRAIN[sp], "model", "*.xml"))[0]
        m = cobra.io.read_sbml_model(x)
        model_genes[sp] = {g.id for g in m.genes}
        print(f"{LABEL[sp]:24s} model {os.path.basename(x)}: {len(m.reactions)} reactions, "
              f"{len(model_genes[sp])} genes")

    # ---- all-vs-all one-way best hits --------------------------------------------
    td = a.workdir or tempfile.mkdtemp(prefix="a3_")
    os.makedirs(td, exist_ok=True)
    faa = {sp: write_fasta(prot[sp], os.path.join(td, f"{sp}.faa")) for sp in SPECIES}
    hits = {}
    for x, y in itertools.permutations(SPECIES, 2):
        print(f"[diamond] {x} -> {y}", flush=True)
        hits[(x, y)] = blast(faa[x], faa[y], td, f"{x}2{y}")

    # ---- presence/absence, three nested criteria ---------------------------------
    rows, per_gene = [], []
    for x, y in itertools.permutations(SPECIES, 2):
        fwd, rev = hits[(x, y)], hits[(y, x)]
        n_e3 = n_e10 = n_rbh = 0
        for g in prot[x]:
            h = fwd.get(g)
            no_e3 = h is None
            no_e10 = h is None or h[2] >= 1e-10
            no_rbh = h is None or rev.get(h[0], (None,))[0] != g
            n_e3 += no_e3
            n_e10 += no_e10
            n_rbh += no_rbh
            if no_e10:
                per_gene.append(dict(present_in=x, absent_from=y, gene=g,
                                     description=prot[x][g][0],
                                     in_model=g in model_genes[x],
                                     best_hit=(h[0] if h else ""),
                                     pident=(h[1] if h else float("nan")),
                                     evalue=(h[2] if h else float("nan")),
                                     criterion=("no_hit_e3" if no_e3 else "no_hit_e10")))
        rows.append(dict(present_in=LABEL[x], absent_from=LABEL[y], n_proteome=len(prot[x]),
                         no_rbh=n_rbh, no_hit_e10=n_e10, no_hit_e3=n_e3,
                         pct_no_hit_e3=round(100 * n_e3 / len(prot[x]), 2)))
    P = pd.DataFrame(rows)
    P.to_csv(os.path.join(HERE, "A3_presence_absence_counts.csv"), index=False)
    G = pd.DataFrame(per_gene)
    G.to_csv(os.path.join(HERE, "A3_absent_genes.csv"), index=False)

    # ---- model level: of the genes absent from a relative, how many are IN a model -
    mrows = []
    for x, y in itertools.permutations(SPECIES, 2):
        sub = G[(G.present_in == x) & (G.absent_from == y)]
        strong = sub[sub.criterion == "no_hit_e3"]
        mrows.append(dict(present_in=LABEL[x], absent_from=LABEL[y],
                          absent_e10=len(sub), absent_e10_in_model=int(sub.in_model.sum()),
                          absent_e3=len(strong), absent_e3_in_model=int(strong.in_model.sum())))
    M = pd.DataFrame(mrows)
    M.to_csv(os.path.join(HERE, "A3_model_level_counts.csv"), index=False)

    # ---- the Xiao et al. candidates ----------------------------------------------
    # Descriptions come from the RefSeq FASTAs, which carry them; C. parapsilosis' model
    # namespace (UniProt/CPAR2_) does NOT, so a description search there returns zero for
    # everything and would be reported as absence when it is a missing annotation field. So
    # the description search is run on RefSeq proteomes for all four, and PRESENCE IS THEN
    # DECIDED BY ALIGNMENT: every candidate found in any species is aligned against every
    # species' model-namespace proteome, and "absent" means no DIAMOND hit, not no keyword.
    refseq = {}
    for sp in SPECIES:
        f = "auris_cladeI" if sp == "auris" else sp
        refseq[sp] = read_fasta(os.path.join(C, "phylo", "proteomes", f"{f}.faa"))
    crows = []
    cand_seqs, cand_key = {}, {}
    for name, pat in CANDIDATES.items():
        rx = re.compile(pat, re.I)
        for sp in SPECIES:
            g = [k for k, (d, _s) in refseq[sp].items() if rx.search(d)]
            crows.append(dict(candidate=name, species=LABEL[sp],
                              n_by_description=len(g),
                              n_by_description_in_model=sum(1 for k in g
                                                            if k in model_genes[sp]),
                              genes=";".join(sorted(g)[:12])))
            for k in g:
                # DIAMOND takes the first whitespace-delimited token as the query id, so the
                # key must contain no spaces; the readable name is kept in cand_key.
                cand_seqs[f"c{len(cand_seqs):04d}"] = ("", refseq[sp][k][1])
                cand_key[f"c{len(cand_seqs)-1:04d}"] = (name, sp, k)
    Cc = pd.DataFrame(crows)
    Cc.to_csv(os.path.join(HERE, "A3_candidates_by_description.csv"), index=False)

    # alignment-based presence for every candidate against every species
    cq = write_fasta(cand_seqs, os.path.join(td, "candidates.faa"))
    arows = []
    for sp in SPECIES:
        h = blast(cq, faa[sp], td, f"cand2{sp}")
        for key in cand_seqs:
            name, src, gid = cand_key[key]
            hit = h.get(key)
            arows.append(dict(candidate=name, found_in=LABEL[src], query_gene=gid,
                              searched=LABEL[sp],
                              best_hit=(hit[0] if hit else ""),
                              pident=(round(hit[1], 1) if hit else float("nan")),
                              evalue=(hit[2] if hit else float("nan")),
                              present=bool(hit),
                              hit_in_model=bool(hit and hit[0] in model_genes[sp])))
    A = pd.DataFrame(arows)
    A.to_csv(os.path.join(HERE, "A3_candidates_by_alignment.csv"), index=False)
    # per candidate x species: is ANY copy detectable, and is any copy in the model?
    piv = (A.groupby(["candidate", "searched"])
             .agg(any_present=("present", "any"), best_pident=("pident", "max"),
                  any_in_model=("hit_in_model", "any"))
             .reset_index())
    piv.to_csv(os.path.join(HERE, "A3_candidates_summary.csv"), index=False)

    with pd.option_context("display.width", 220, "display.max_colwidth", 40):
        print("\n(a) PROTEOME level -- genes present in one species and absent from another")
        print(P.to_string(index=False))
        print("\n(b) MODEL level -- how many of those absences involve a gene that is in a model")
        print(M.to_string(index=False))
        print("\nXiao et al. 2025 candidates -- by DESCRIPTION (RefSeq proteomes)")
        print(Cc[["candidate", "species", "n_by_description",
                  "n_by_description_in_model"]].to_string(index=False))
        print("\nXiao et al. 2025 candidates -- by ALIGNMENT (the defensible call)")
        print(piv.to_string(index=False))
    json.dump(dict(proteome_sizes={sp: len(prot[sp]) for sp in SPECIES},
                   model_gene_counts={sp: len(model_genes[sp]) for sp in SPECIES},
                   workdir=td),
              open(os.path.join(HERE, "A3_meta.json"), "w"), indent=2)
    print("\nwrote A3_*.csv beside this script")
    return 0


if __name__ == "__main__":
    sys.exit(main())
