#!/usr/bin/env python3
"""T1 TASK 3 -- analysis of task3_trace.json under the rule registered in DECISIONS D7. Reads only;
nothing is smoothed; every classification prints the evidence it rests on."""
import os, sys, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
os.chdir(ROOT)
AXES = ["dTopt", "topt_scale", "dCp_scale", "tm_scale", "kcat_scale", "sigma", "clearance_mult"]
MECH = ["clipped_low", "above_Topt", "past_Tm"]

def curv(Lp, L0, Lm, h): return -(Lp - 2 * L0 + Lm) / h ** 2

def refine_verdict(series):
    d = [s.get("delta") for s in series]
    if any(x is None for x in d) or len(d) < 4: return "UNEVALUATED", []
    ratios = []
    for a, b in zip(d[:-1], d[1:]):
        ratios.append(None if abs(a) < 1e-6 else abs(b) / abs(a))
    if any(r is None for r in ratios): return "UNDEFINED(|delta|<1e-6)", ratios
    if any(r > 0.80 for r in ratios): return "JUMP", ratios
    if all(0.35 <= r <= 0.65 for r in ratios): return "SMOOTH", ratios
    return "AMBIGUOUS", ratios

def moves(evA, evB):
    """which mechanisms move between two evaluations, per temperature index."""
    out = {}
    for m in MECH:
        a = [x[m] for x in evA["enzyme_state"]]; b = [x[m] for x in evB["enzyme_state"]]
        out[m] = [i for i in range(len(a)) if a[i] != b[i]]
    out["status"] = [i for i in range(len(evA["status"])) if evA["status"][i] != evB["status"][i]]
    # diverse-point stencils carry no "scored" list; the clamp scores a datum iff its respiration term is
    # non-zero (a skipped term is exactly 0.0), so the mask is recovered from resp_term where absent.
    sa = evA.get("scored") or [int(x != 0.0) for x in evA["resp_term"]]; sb = evB.get("scored") or [int(x != 0.0) for x in evB["resp_term"]]
    out["scored"] = [i for i in range(len(sa)) if sa[i] != sb[i]]
    return out

def analyse_point(name, base, stencil_of, refine_by_axis, T):
    """stencil_of(ax, off) -> evaluation dict or None; refine_by_axis: {axis: series} or {}. Returns per-axis rows."""
    rows = []
    for ax in AXES:
        refine = (refine_by_axis or {}).get(ax)
        # refine may be {"plus": series, "minus": series}; the verdict comes from the CARRYING side (D9)
        rp = (refine or {}).get("plus") if isinstance(refine, dict) else refine
        rm = (refine or {}).get("minus") if isinstance(refine, dict) else None
        vp, rat_p = refine_verdict(rp) if rp is not None else ("NOT_RUN", [])
        vm, rat_m = refine_verdict(rm) if rm is not None else ("NOT_RUN", [])
        st = {off: stencil_of(ax, off) for off in (-0.04, -0.02, 0.02, 0.04)}
        if any(v is None or "logl" not in v for v in st.values()):
            rows.append(dict(point=name, axis=ax, classification="UNEVALUATED")); continue
        k1 = curv(st[0.02]["logl"], base["logl"], st[-0.02]["logl"], 0.02)
        k2 = curv(st[0.04]["logl"], base["logl"], st[-0.04]["logl"], 0.04)
        rel = abs(k1 - k2) / max(1.0, abs(k1), abs(k2))
        # by observation: per-datum curvature differences
        g0 = np.asarray(base["growth_term"]); r0 = np.asarray(base["resp_term"])
        per = []
        for term, key in (("growth", "growth_term"), ("resp", "resp_term")):
            b0 = np.asarray(base[key])
            c1 = -(np.asarray(st[0.02][key]) - 2 * b0 + np.asarray(st[-0.02][key])) / 0.02 ** 2
            c2 = -(np.asarray(st[0.04][key]) - 2 * b0 + np.asarray(st[-0.04][key])) / 0.04 ** 2
            for i in range(len(b0)): per.append((term, i, float(c1[i] - c2[i])))
        tot = k1 - k2; per.sort(key=lambda x: -abs(x[2]))
        top = per[0]; share = top[2] / tot if abs(tot) > 0 else float("nan")
        recon = abs(sum(p[2] for p in per) - tot) < 1e-6
        # by mechanism, on the four intervals of the five-point stencil
        order = [-0.04, -0.02, 0.0, 0.02, 0.04]; ev = {0.0: base, **st}
        mv = {}
        for a, b in zip(order[:-1], order[1:]):
            mv[f"{a:+.2f}->{b:+.2f}"] = moves(ev[a], ev[b])
        any_mv = {m: sorted({i for iv in mv.values() for i in iv[m]}) for m in MECH + ["status", "scored"]}
        # D7: the CARRYING interval and temperature -- the interval whose total step departs most from the
        # linear extrapolation of its neighbours, and the datum carrying most of that departure; then the
        # mechanisms that move AT THAT TEMPERATURE ON THAT INTERVAL.
        steps = {f"{a:+.2f}->{b:+.2f}": ev[b]["logl"] - ev[a]["logl"] for a, b in zip(order[:-1], order[1:])}
        keys = list(steps); vals = np.array([steps[k] for k in keys])
        excess = np.abs(vals - np.median(vals)); ci = int(np.argmax(excess)); ck = keys[ci]; a, b = order[ci], order[ci + 1]
        dg = np.asarray(ev[b]["growth_term"]) - np.asarray(ev[a]["growth_term"]); drr = np.asarray(ev[b]["resp_term"]) - np.asarray(ev[a]["resp_term"])
        med_g = np.median([np.asarray(ev[y]["growth_term"]) - np.asarray(ev[x]["growth_term"]) for x, y in zip(order[:-1], order[1:])], axis=0)
        med_r = np.median([np.asarray(ev[y]["resp_term"]) - np.asarray(ev[x]["resp_term"]) for x, y in zip(order[:-1], order[1:])], axis=0)
        exg = dg - med_g; exr = drr - med_r
        cands = [(abs(exg[i]), "growth", i, exg[i]) for i in range(len(exg))] + [(abs(exr[i]), "resp", i, exr[i]) for i in range(len(exr))]
        cands.sort(reverse=True); cterm, cT, cval = cands[0][1], cands[0][2], cands[0][3]
        mvc = mv[ck]; at_T = {m: (cT in mvc[m]) for m in MECH + ["status", "scored"]}
        o2_path = [ev[o].get("o2", [float("nan")] * 12)[cT] for o in order]; g_path = [ev[o].get("growth", [float("nan")] * 12)[cT] for o in order]   # diverse stencils carry terms, not fluxes
        clip_c = at_T["clipped_low"]; phys_c = at_T["above_Topt"] or at_T["past_Tm"] or at_T["status"] or at_T["scored"]
        side = "minus" if b <= 0 else "plus"
        verdict, ratios = (vm, rat_m) if side == "minus" else (vp, rat_p)
        if verdict == "NOT_RUN": verdict = f"NOT_RUN({side} side)"

        # the rule (D7)
        clip = bool(any_mv["clipped_low"]); phys = bool(any_mv["above_Topt"] or any_mv["past_Tm"] or any_mv["status"] or any_mv["scored"])
        if verdict == "SMOOTH": cls = "SUPPORTED_BY_PHYSIOLOGY(smooth,non-quadratic)"
        elif verdict in ("JUMP", "AMBIGUOUS"):
            if clip_c and not phys_c: cls = "IMPLEMENTATION_DEFECT(clip at the carrying T)"
            elif phys_c and not clip_c: cls = "SUPPORTED_BY_PHYSIOLOGY(mechanism moves at the carrying T)"
            elif clip_c and phys_c: cls = "UNDETERMINED(clip and physiology move together at the carrying T)"
            else: cls = "UNDETERMINED(no traced mechanism moves at the carrying T; untraced basis change is the candidate)"
        else: cls = f"UNDETERMINED(refinement {verdict})"
        rows.append(dict(point=name, axis=ax, k_0p02=k1, k_0p04=k2, rel_diff=rel, per_datum_reconciles=recon,
                         top_datum=f"{top[0]}@{T[top[1]]:.0f}C", top_share=share,
                         top3=";".join(f"{p[0]}@{T[p[1]]:.0f}C:{p[2]:+.3f}" for p in per[:3]),
                         clip_moves_T=";".join(f"{T[i]:.0f}" for i in any_mv["clipped_low"]),
                         topt_moves_T=";".join(f"{T[i]:.0f}" for i in any_mv["above_Topt"]),
                         tm_moves_T=";".join(f"{T[i]:.0f}" for i in any_mv["past_Tm"]),
                         status_moves_T=";".join(f"{T[i]:.0f}" for i in any_mv["status"]),
                         scored_moves_T=";".join(f"{T[i]:.0f}" for i in any_mv["scored"]),
                         carrying_interval=ck, carrying_datum=f"{cterm}@{T[cT]:.0f}C", carrying_excess=float(cval),
                         moves_at_carrying_T=";".join(m for m, v in at_T.items() if v) or "none",
                         o2_at_carrying_T=";".join(f"{x:.4f}" for x in o2_path), growth_at_carrying_T=";".join(f"{x:.5f}" for x in g_path),
                         carrying_side=side, refinement=verdict, refinement_plus=vp, ratios_plus=";".join("-" if r is None else f"{r:.3f}" for r in rat_p),
                         refinement_minus=vm, ratios_minus=";".join("-" if r is None else f"{r:.3f}" for r in rat_m), ratios=";".join("-" if r is None else f"{r:.3f}" for r in ratios),
                         refine_deltas_plus=";".join(f"{s.get('delta', float('nan')):+.5f}" for s in (rp or [])),
                         refine_deltas_minus=";".join(f"{s.get('delta', float('nan')):+.5f}" for s in (rm or [])),
                         classification=cls))
    return rows

def main():
    rec = json.load(open(os.path.join(HERE, "task3_trace.json")))
    T = np.asarray(json.load(open("reports/P17_inactive_prior/real_curvature_probe/evaluations.json"))[0]["flux"]["temp_C"], float)
    ev = {e.get("label"): e for e in rec["evaluations"] if e.get("point") == "D44"}
    n = len(ev); ok = [e for e in ev.values() if "logl" in e]
    repro = [(e["label"], e["vs_saved"]) for e in ok]; worst = max(repro, key=lambda x: x[1]) if repro else None
    recon = all(e["reconciles"] for e in ok)
    print(f"[a3] D44: {n} labels, {len(ok)} evaluated, {n - len(ok)} unresolved; worst |fresh - saved| = {worst}; per-datum reconciles at every evaluation: {recon}")
    bad = [(l, v) for l, v in repro if v > 1e-6]; print(f"[a3] D44 reproductions failing 1e-6: {len(bad)} {bad[:5]}")
    base = ev.get("baseline_start")
    ref = {r["axis"]: {"plus": r["series"]} for r in rec.get("refinements", [])}
    for r in rec.get("refinements_minus", []): ref.setdefault(r["axis"], {})["minus"] = r["series"]
    rows = analyse_point("D44", base, lambda ax, off: ev.get(f"{ax}_{'plus' if off > 0 else 'minus'}_{abs(off):.2f}"), ref, T)
    for d in rec.get("diverse", []):
        if "base" not in d:
            rows += [dict(point=d["point"], axis=ax, classification=d.get("status", "NOT_EVALUATED"), provenance=d.get("provenance")) for ax in AXES]; continue
        sts = {(s["axis"], s["off"]): s for s in d["stencils"]}
        rows += analyse_point(d["point"], d["base"], lambda ax, off: sts.get((ax, off)), {}, T)
        for r in rows:
            if r["point"] == d["point"]: r["provenance"] = d.get("provenance")
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "task3_classification.csv"), index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    cols = [c for c in ["point", "axis", "k_0p02", "k_0p04", "rel_diff", "carrying_side", "refinement", "ratios", "refinement_plus", "refinement_minus", "carrying_interval", "carrying_datum", "carrying_excess", "moves_at_carrying_T", "o2_at_carrying_T", "classification"] if c in df.columns]
    print(df[cols].to_string(index=False))
    print(f"[a3] wall {rec.get('wall_min')} min")

if __name__ == "__main__":
    main()
