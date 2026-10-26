#!/usr/bin/env python3
"""The paper's measured values, from committed result files at pinned commits, into data files and LaTeX macros.

Reads (git archive, no checkout) from the amd-npu bare at AMD_NPU_PIN and from the census workspace's aie-cosched at
COSCHED_PIN, and writes:
  data/prefill-cells.json  per LLM and prompt length: OPCORD's pick, the baseline, the gain and its interval
  data/decode-cells.json   per LLM and context: time per token of the unmodified decode design and of the loop pass
  data/choice.json         per cell, the loss of OPCORD's choice and of each fixed rule against the measured minimum
  data/absolute.json       TTFT of FastFlowLM's release, the original program on S2, and OPCORD's pick (D1)
  ../paper/fig/numbers.tex one macro per value the text states

Definitions (Section 6.1 of the paper):
- baseline: the original program on the fastest supported split measured, each split timed both on its own host code
  (orig) and on our runtime package issuing the original order (identb), whichever is faster;
- OPCORD: the pick of the event model (choose() at the batch's pin) as measured; a pick of the original order is the
  baseline itself (1.000);
- for the amendment-1 cells, the gain and interval are that batch's registered analysis (paired, chained where the
  baseline split differs from the pick's); for the rest, the pick runs on S2 in the grid's process beside the baseline,
  and the ratio of medians carries a paired bootstrap interval.
"""
import io
import math
import json
import re
import statistics as st
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
TEX = ROOT.parent / "paper" / "fig" / "numbers.tex"

AMD_NPU = Path.home() / "git" / "amd-npu.git"
AMD_NPU_PIN = "a6abaf19"  # npu-gap-0 head, 2026-10-25 night; holds every result read below
COSCHED = Path.home() / "aie2p-gmk" / "aie-cosched-pass-0" / "aie-cosched"
DECOMP = ("c4a8650", "passes/results/2026-10-25-gain-decompose/decompose.json")

MOD = {"1b": "llama32_1b_q4nx", "8b": "llama31_8b_q4nx", "qwen": "qwen3_4b_q4nx", "lfm2": "lfm2_1_2b_q4nx",
       "gemma": "gemma3_4b_q4nx"}
NAME = {"1b": "Llama-3.2-1B", "lfm2": "LFM2-1.2B", "qwen": "Qwen3-4B", "gemma": "Gemma3-4B", "8b": "Llama-3.1-8B"}
NS = [128, 129, 256, 512, 1024, 2048, 2049, 4096, 8192, 16384, 16385, 32768]
GRID = {"1b": ["grid-1b-2026-10-23/cells", "large-1b-2026-10-24"], "8b": ["grid-8b-shared-2026-10-24"],
        "qwen": ["grid-qwen-2026-10-24", "qwen-32768-shared-2026-10-24"], "lfm2": ["grid-lfm2-shared-2026-10-24"],
        "gemma": ["grid-gemma-shared-2026-10-24"]}
ARM = {"ship": "orig", "shipar": "stream", "comp": "comp"}


class Tree:
    """One commit's files under a prefix, read once through git archive."""

    def __init__(self, repo, rev, prefix):
        raw = subprocess.run(["git", "-C", str(repo), "archive", rev, prefix], capture_output=True, check=True).stdout
        self.files = {}
        with tarfile.open(fileobj=io.BytesIO(raw)) as t:
            for m in t.getmembers():
                if m.isfile():
                    self.files[m.name] = t.extractfile(m).read()

    def json(self, path):
        return json.loads(self.files[path])

    def lines(self, path):
        return [json.loads(x) for x in self.files[path].decode().splitlines() if x.strip()]

    def glob(self, pattern):
        rx = re.compile("^" + re.escape(pattern).replace(r"\*", "[^/]*") + "$")
        return sorted(p for p in self.files if rx.match(p))


def kept(j):
    w = j.get("warm_used", j.get("warm", 0)) or 0
    return {a: list(v[w:]) for a, v in j["ms"].items() if v[w:]}


def ratio_ci(a, b, draws=2000, seed=20261023):
    """median(a) / median(b) with a paired bootstrap 95% interval (abstats.ratio_ci, re-stated without numpy)."""
    import random
    assert len(a) == len(b)
    rng = random.Random(seed)
    n = len(a)
    rs = []
    for _ in range(draws):
        idx = [rng.randrange(n) for _ in range(n)]
        rs.append(st.median([a[i] for i in idx]) / st.median([b[i] for i in idx]))
    rs.sort()
    return st.median(a) / st.median(b), rs[int(0.025 * draws)], rs[int(0.975 * draws) - 1]


def parse_ci(s):
    m = re.match(r"([\d.]+)(?: \[([\d.]+), ([\d.]+)\])?", s)
    v = float(m.group(1))
    return v, float(m.group(2) or v), float(m.group(3) or v)


def prefill(ab):
    R = "ab/results/"
    choose = {(c["model"], c["N"]): c for c in ab.lines(R + "amend1-2026-10-24/choose-pin.jsonl")}
    amend = {r["cell"]: r for r in ab.lines(R + "amend1-2026-10-24/results.jsonl")}
    # every measured median per cell: (split, arm) -> (median, source); later sources replace earlier ones
    med = {}

    def put(t, N, split, arms, src, only=None):
        for a, v in arms.items():
            if (only and a not in only) or not v:
                continue
            med.setdefault((t, N), {})[(split, a)] = (st.median(v), src)

    def from_dir(d, t, split, only=None):
        for p in ab.glob(R + d + "/ab-*.json"):
            N = int(re.search(r"ab-(\d+)\.json$", p).group(1))
            put(t, N, split, kept(ab.json(p)), d, only)

    for t, ds in GRID.items():
        for d in ds:
            from_dir(d, t, "S2")
    for t in ("qwen", "lfm2"):
        from_dir(f"s4-cells-2026-10-24/{t}", t, "S4")
    from_dir("s1-cells-lfm2-2026-10-24/a", "lfm2", "S1")
    from_dir("s1-cells-lfm2-2026-10-24/b", "lfm2", "S2", {"orig"})
    from_dir("split-cells-gemma-2026-10-24/a-S1", "gemma", "S1")
    from_dir("split-cells-gemma-2026-10-24/a-S4", "gemma", "S4")
    from_dir("split-cells-gemma-2026-10-24/b", "gemma", "S2", {"orig"})
    for p in ab.glob(R + "amend1-2026-10-24/t*/A/*-S*/ab-*.json"):
        t, X = p.split("/")[-2].split("-")
        N = int(re.search(r"ab-(\d+)\.json$", p).group(1))
        put(t, N, X, kept(ab.json(p)), "amend1 A")
    for p in ab.glob(R + "amend1-2026-10-24/t*/B/*-S*/ab-*.json"):
        t, X = p.split("/")[-2].split("-")
        N = int(re.search(r"ab-(\d+)\.json$", p).group(1))
        put(t, N, X, kept(ab.json(p)), "amend1 B", {"orig"})
    for p in ab.glob(R + "amend1-2026-10-24/t*/rounds/*-S*/r*-S*/ab-*.json"):
        t = p.split("/")[-3].split("-")[0]
        s = p.split("/")[-2].split("-")[1]
        N = int(re.search(r"ab-(\d+)\.json$", p).group(1))
        key = (t, N)
        reps = kept(ab.json(p)).get("orig", [])
        acc = med.setdefault(("rounds",) + key + (s,), [])
        acc.extend(reps)
    for k in [k for k in med if k[0] == "rounds"]:
        _, t, N, s = k
        med.setdefault((t, N), {})[(s, "orig")] = (st.median(med.pop(k)), "amend1 rounds")
    for j in ab.lines(R + "comps4-2026-10-24/results.jsonl"):
        t, N = j["cell"].split()
        for k, v in j["medians"].items():
            a, s = k.split("-")
            med.setdefault((t, int(N)), {})[(s, a)] = (v, "comps4")

    cells = []
    for t in MOD:
        for N in NS:
            c = choose.get((MOD[t], N))
            d = med.get((t, N), {})
            row = {"llm": NAME[t], "key": t, "N": N}
            if not c:
                row["unpriced"] = True
                cells.append(row)
                continue
            X, pa = c["pick"]["split"], ARM[c["pick"]["arm"]]
            row.update(pick_split=X, pick_arm=pa)
            # the original per split: the faster of its own host code and our runtime package
            orig = {}
            for (s, a), (v, _) in d.items():
                if a in ("orig", "identb"):
                    orig[s] = min(v, orig.get(s, float("inf")))
            row["orig_ms"] = orig
            row["baseline_split"] = min(orig, key=orig.get)
            row["baseline_ms"] = orig[row["baseline_split"]]
            row["measured"] = {f"{a}@{s}": v for (s, a), (v, _) in sorted(d.items())}
            a1 = amend.get(f"{t} {N}")
            if a1:
                g, lo, hi = parse_ci(a1.get("OPCORD") or a1["OPCORD (chained, primary)"])
                row.update(gain=g, lo=lo, hi=hi, source="amend1 registered analysis: " + a1["baseline"])
            else:
                # the pick beside the original in one process at the pick's split (the grid on S2, the S4 cells on S4)
                dirs = {"S2": GRID[t], "S4": [f"s4-cells-2026-10-24/{t}", f"split-cells-gemma-2026-10-24/a-S4"],
                        "S1": ["s1-cells-lfm2-2026-10-24/a", "split-cells-gemma-2026-10-24/a-S1"]}[X]
                dirs = [dd for dd in dirs if t in dd or X == "S2" or (X == "S4" and "s4-cells" in dd)]
                f = None
                for dd in dirs:
                    p = R + dd + f"/ab-{N}.json"
                    if p in ab.files:
                        f = p
                assert f, (t, N, X)
                k = kept(ab.json(f))
                base = min(("orig", "identb"), key=lambda a: st.median(k[a]) if a in k else float("inf"))
                if pa == "orig":
                    g = lo = hi = 1.0
                else:
                    g, lo, hi = ratio_ci(k[base], k[pa])
                if row["baseline_split"] != X:
                    # a faster original on another split, measured in another process: an unpaired ratio
                    g = row["baseline_ms"] / st.median(k[pa])
                    lo = hi = None
                row.update(gain=g, lo=lo, hi=hi, source=f"{f.split('results/')[1]} {base}/{pa}"
                           + (", paired" if lo is not None else f", baseline {row['baseline_split']} unpaired"))
            pick = d.get((X, pa))
            row["pick_ms"] = pick[0] if pick else None
            cells.append(row)
    return cells, med


def choice(cells, med):
    """Loss against the minimum measured over every split and order of the cell (lower bounds where a candidate was not
    measured): OPCORD's pick, never reordering, always composing at the pick's split, the best order on S2, composing
    from four chunks on S2, and composing from four chunks on the baseline's split."""
    out = []
    for r in cells:
        if r.get("unpriced"):
            continue
        d = {k: v[0] for k, v in med[(r["key"], r["N"])].items()}
        best = min(v for (s, a), v in d.items() if a in ("orig", "identb", "stream", "comp"))
        X, N = r["pick_split"], r["N"]

        def g(s, a):
            if a == "orig":
                vs = [d.get((s, "orig")), d.get((s, "identb"))]
                vs = [v for v in vs if v is not None]
                return min(vs) if vs else None
            return d.get((s, a))

        pick = g(X, r["pick_arm"])
        base = r["baseline_ms"]
        s2 = [v for (s, a), v in d.items() if s == "S2" and a in ("orig", "identb", "stream", "comp")]
        L = lambda x: None if x is None else 100 * (x / best - 1)  # noqa: E731
        out.append({"cell": f"{r['key']} {N}", "opcord": L(pick), "never": L(base), "always": L(g(X, "comp")),
                    "fixed_s2": L(min(s2) if s2 else None),
                    "four_s2": L(g("S2", "comp") if N >= 512 else g("S2", "orig")),
                    "four_base": L(g(r["baseline_split"], "comp") if N >= 512 else base)})
    summary = {}
    for k in ("opcord", "never", "always", "fixed_s2", "four_s2", "four_base"):
        v = [x[k] for x in out if x[k] is not None]
        summary[k] = {"n": len(v), "median": st.median(v), "max": max(v),
                      "max_cell": max((x for x in out if x[k] is not None), key=lambda x: x[k])["cell"]}
    return out, summary


def decode(ab):
    base = "decode-rename/decode-dev-2026-10-24/run/"
    out = []
    for t in MOD:
        for P in (2048, 16384, 30208, 28800):
            p = f"{base}P{P}/{t}/ab.json"
            if p not in ab.files:
                continue
            pt = ab.json(p)["points"][str(P)]["ms_tok"]
            off, on = st.median(pt["baseline"]), st.median(pt["treatment"])
            # the ABBA windows pair by index (each repetition times both arms back to back)
            _, lo, hi = ratio_ci(pt["baseline"], pt["treatment"])
            out.append({"llm": NAME[t], "key": t, "P": P, "off_ms": off, "on_ms": on, "gain": off / on,
                        "lo": lo, "hi": hi, "reps": len(pt["baseline"])})
    return out


def absolute(ab):
    """D1, one batch: FastFlowLM 1.0.8's server prefill timer, the original program on S2, and OPCORD's pick."""
    R = "ab/results/d1-2026-10-25/"
    tag = {"1b": "llama3_2_1b", "8b": "llama3_1_8b", "qwen": "qwen3_4b", "lfm2": "lfm2_1_2b", "gemma": "gemma3_4b"}
    picks = dict(((l.split()[0], int(l.split()[1])), l.split()[2])
                 for l in ab.files[R + "picks.txt"].decode().splitlines() if l.strip())
    rows = []
    for t in ("1b", "lfm2", "qwen", "gemma", "8b"):
        f = ab.json(R + f"run/{t}/flm-ttft/{tag[t]}.json")
        dj = ab.json(R + f"run/{t}/flm-decode/{tag[t]}.json")
        for N in (128, 1024, 4096, 16384):
            flm = st.median(x["server_ttft_ms"] for x in f["reps"][f"scratch-{N}"])
            vals = {}
            for p in ab.glob(R + f"run/{t}/ab-*/ab-{N}.json"):
                j = ab.json(p)
                for a in ("orig", "comp"):
                    if a in j["median_ms"]:
                        vals[a] = j["median_ms"][a]
            rows.append({"llm": NAME[t], "key": t, "N": N, "flm_ms": flm, "orig_s2_ms": vals.get("orig"),
                         "opcord_ms": vals.get("comp"), "pick_split": picks.get((t, N))})
        for P in (2048, 16384):
            fl = st.median(x["server_ms_tok"] for x in dj["reps"][f"decode-{P}"])
            pt = ab.json(R + f"run/{t}/dec-P{P}/ab.json")["points"][str(P)]["ms_tok"]
            rows.append({"llm": NAME[t], "key": t, "P": P, "flm_ms_tok": fl, "off_ms_tok": st.median(pt["baseline"]),
                         "on_ms_tok": st.median(pt["treatment"])})
    return rows


def fig1(ab):
    j = ab.json("prefill-overlap/ml-timeline/fig1-2026-10-25/run/1b-N/ab-4096.json")
    k = kept(j)
    arms = list(k)
    o = next(a for a in arms if a.startswith("orig"))
    c = next(a for a in arms if a.startswith("comp"))
    g, lo, hi = ratio_ci(k[o], k[c])
    return {"arms": arms, "orig_ms": st.median(k[o]), "comp_ms": st.median(k[c]), "gain": g, "lo": lo, "hi": hi,
            "kept": len(k[o])}


def fmt(x, nd=2):
    """Rounded half up, as the text states values (1.625 -> 1.63)."""
    from decimal import Decimal, ROUND_HALF_UP
    return str(Decimal(repr(x)).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def main():
    ab = Tree(AMD_NPU, AMD_NPU_PIN, "ab/results")
    for extra in ("decode-rename/decode-dev-2026-10-24/run", "prefill-overlap/ml-timeline/fig1-2026-10-25/run"):
        ab.files.update(Tree(AMD_NPU, AMD_NPU_PIN, extra).files)
    cells, med = prefill(ab)
    ch, chs = choice(cells, med)
    dec = decode(ab)
    absr = absolute(ab)
    f1 = fig1(ab)
    dc = json.loads(subprocess.run(["git", "-C", str(COSCHED), "show", f"{DECOMP[0]}:{DECOMP[1]}"],
                                   capture_output=True, check=True, text=True).stdout)

    src = {"amd-npu": AMD_NPU_PIN, "aie-cosched (census workspace)": DECOMP[0]}
    (DATA / "prefill-cells.json").write_text(json.dumps({"source": src, "cells": cells}, indent=1))
    (DATA / "decode-cells.json").write_text(json.dumps({"source": src, "cells": dec}, indent=1))
    (DATA / "choice.json").write_text(json.dumps({"source": src, "cells": ch, "summary": chs}, indent=1))
    (DATA / "absolute.json").write_text(json.dumps({"source": src, "rows": absr, "fig1": f1}, indent=1))

    m = {}
    long_ = [c for c in cells if not c.get("unpriced") and c["N"] >= 1024]
    m["PrefillGainLo"], m["PrefillGainHi"] = fmt(min(c["gain"] for c in long_)), fmt(max(c["gain"] for c in long_))
    m["PrefillCells"] = str(len(long_))
    short = [c for c in cells if not c.get("unpriced") and c["N"] <= 512]
    m["ShortGainLo"], m["ShortGainHi"] = fmt(min(c["gain"] for c in short)), fmt(max(c["gain"] for c in short))
    d30 = [d for d in dec if d["P"] in (30208, 28800)]
    d16 = [d for d in dec if d["P"] == 16384]
    m["DecodeGainLo"], m["DecodeGainHi"] = fmt(min(d["gain"] for d in d30)), fmt(max(d["gain"] for d in d30))
    m["DecodeMidLo"], m["DecodeMidHi"] = fmt(min(d["gain"] for d in d16)), fmt(max(d["gain"] for d in d16))
    gem = [100 * (d["gain"] - 1) for d in dec if d["key"] == "gemma"]
    m["DecodeGemmaLo"], m["DecodeGemmaHi"] = fmt(min(gem), 1), fmt(max(gem), 1)
    m["FigOneGain"] = fmt(f1["gain"])
    # absolute standing, 1K-16K
    rat = [r["flm_ms"] / r["opcord_ms"] for r in absr if r.get("N", 0) >= 1024]
    m["AbsGainLo"], m["AbsGainHi"] = fmt(min(rat), 1), fmt(max(rat), 1)
    slow = [r for r in absr if r.get("N") == 16384 and r["orig_s2_ms"] > r["flm_ms"]]
    m["AbsOrigSlower"] = {4: "four", 5: "all five", 3: "three"}.get(len(slow), str(len(slow)))
    close = [100 * (r["on_ms_tok"] / r["flm_ms_tok"] - 1) for r in absr if r.get("P") == 16384 and r["key"] in ("1b", "8b")]
    m["AbsDecodeClosePct"] = str(math.ceil(max(close)))  # "within" this many percent
    # choice table
    lab = {"opcord": "Opcord", "never": "Never", "always": "Always", "fixed_s2": "FixedSTwo", "four_s2": "FourSTwo",
           "four_base": "FourBase"}
    for k, v in chs.items():
        m[f"Choice{lab[k]}Med"] = f"{v['median']:.1f}"
        m[f"Choice{lab[k]}Max"] = f"{v['max']:.1f}"
    m["ChoiceCells"] = str(chs["opcord"]["n"])
    # where the gain comes from (decomposition, the development grids on S2)
    f1c = dc["Figure 1's cell (1B 4096 S2)"] if isinstance(dc["Figure 1's cell (1B 4096 S2)"], dict) else None
    one = [c for c in dc["cells"] if c["model"] == MOD["1b"] and c["N"] == 4096 and c["split"] == "S2"][0]
    m["DecompAlt"] = fmt(one["(1) alternation orig / stream"])
    m["DecompOverlap"] = fmt(one["(2) overlap factor"])
    m["DecompHost"] = fmt(one["(3) host / dispatch factor"])
    m["DecompTotal"] = fmt(one["gain orig / comp"])
    m["DecompOverlapShare"] = f"{100 * dc['overlap share of stream - comp, median over cells']:.0f}" \
        if not isinstance(dc["overlap share of stream - comp, median over cells"], dict) else \
        f"{100 * list(dc['overlap share of stream - comp, median over cells'].values())[0]:.0f}"
    # Gemma3-4B's attention has no wait between its columns to alternate (1.0005), so it is stated apart
    s2_16 = [c for c in dc["cells"] if c["split"] == "S2" and c["N"] == 16384 and c["model"] != MOD["gemma"]]
    alt = [c["(1) alternation orig / stream"] for c in s2_16]
    m["StreamSTwoLo"], m["StreamSTwoHi"] = fmt(min(alt)), fmt(max(alt))
    # the composer's share at the picks: stream / comp at the pick's split where both were measured
    sh = []
    for c in cells:
        if c.get("unpriced") or c["N"] < 1024 or c["pick_arm"] != "comp":
            continue
        s, k = c["measured"].get(f"stream@{c['pick_split']}"), c["measured"].get(f"comp@{c['pick_split']}")
        if s and k:
            sh.append(s / k)
    m["ComposerShareLo"], m["ComposerShareHi"] = fmt(min(sh)), fmt(max(sh))

    # the event model's frozen form on the 70 development cells: error on the original-to-composed ratio
    fa = ab.json("ab/results/comps4-2026-10-24/formA2_seventy.json")
    err = [abs(r["dev"] - 1) for r in fa]
    mis = [abs(r["measured"] - 1) for r in fa if (r["measured"] > 1) != (r["measured"] * r["dev"] > 1)]
    m["AccCells"] = str(len(fa))
    m["AccDiffMed"], m["AccDiffMax"] = fmt(100 * st.median(err), 1), fmt(100 * max(err), 1)
    m["AccWithinFive"] = str(sum(e <= 0.05 for e in err))
    m["AccMisorderMax"] = fmt(100 * max(mis), 1)
    m["ChoiceFourBaseCells"] = str(chs["four_base"]["n"])

    lines = ["% Generated by figs/paper_numbers.py; do not edit. Sources: amd-npu " + AMD_NPU_PIN + ", census workspace "
             + DECOMP[0] + "."]
    for k, v in m.items():
        lines.append(f"\\newcommand{{\\{k}}}{{{v}}}")
    TEX.write_text("\n".join(lines) + "\n")
    for k, v in m.items():
        print(f"{k:22} {v}")
    print("choice", json.dumps(chs, indent=0))


if __name__ == "__main__":
    sys.exit(main())
