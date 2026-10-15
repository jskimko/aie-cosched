#!/usr/bin/env python3
"""The paper's data figures and generated table rows, from the measurements in figs/data/ (sources: figs/README.md).

Outputs (into FIGS_OUT, default paper/fig):
  busy.pdf         TTFT of the existing Llama-3.2-1B prefill split into device-busy time per operator class and the rest
  pairs.pdf        one attention and one GEMM operator: queued, in sequence in one command, and interleaved in one command
  params-rows.tex  rows of the event model's parameter table
"""
import json
import os
import re
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = Path(os.environ.get("FIGS_OUT", ROOT.parent / "paper" / "fig"))

# IEEEtran sets Times; the figures use the same fonts through LaTeX.
plt.rcParams.update({
    "text.usetex": True,
    "text.latex.preamble": r"\usepackage{newtxtext}\usepackage{newtxmath}",
    "font.family": "serif",
    "font.size": 8,
    "axes.linewidth": 0.5,
    "lines.linewidth": 0.8,
    "lines.markersize": 3,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "xtick.major.width": 0.5,
    "ytick.major.width": 0.5,
    "xtick.major.size": 2.5,
    "ytick.major.size": 2.5,
    "legend.frameon": False,
    "legend.fontsize": 7,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.01,
})
COLUMN = 3.5  # IEEEtran column width, inches

# IBM's color-blind-safe palette, softened; each series keeps its color and marker in every figure.
BLUE, PURPLE, MAGENTA, ORANGE, GOLD = "#6E95F0", "#8770E0", "#D04A8A", "#EB7A3A", "#F0B840"
GRAY = "#B0B0B0"
INK = "#262626"  # existing schedules: near-black


def e2_decomposition():
    """Per prompt length: TTFT and device-busy time of the GEMMs, attention, and the LM head (ms).

    Parsed from prefill-e2's own decomposition (decomp.txt); busy = isolated time - dispatch floor."""
    text = (DATA / "e2-decomp.txt").read_text()
    out = {}
    for block in re.split(r"\n(?=n=)", text.strip()):
        head = re.search(r"n=(\d+) C=(\d+) cap=[\d.]+ floor=(\d+)us \| TTFT ([\d.]+) ms .* S-busy ([\d.]+) ms", block)
        gemm = re.search(r"per-chunk-per-layer GEMM: device [\d.]+ ms \(busy ([\d.]+)\)", block)
        attn = re.search(r"attn total ([\d.]+) ms", block)
        lm = re.search(r"LM [\d.]+ ms \(busy ([\d.]+)", block)
        n, chunks, floor_us, ttft, busy = (float(x) for x in head.groups())
        layers = 16
        g = float(gemm.group(1)) * layers * chunks
        a = float(attn.group(1)) - layers * chunks * floor_us / 1000  # attention total is device time: one dispatch per chunk-layer
        m = float(lm.group(1))
        assert abs(g + a + m - busy) / busy < 0.01, f"n={n}: parts {g + a + m:.1f} vs busy {busy:.1f}"
        out[int(n)] = {"ttft": ttft, "gemm": g, "attn": a, "lm": m}
    return out


def fig_busy():
    d = e2_decomposition()
    ns = sorted(d)
    fig, ax = plt.subplots(figsize=(COLUMN, 1.25))
    parts = [("gemm", "GEMMs (columns 1--6)", BLUE, None),
             ("lm", "LM head (columns 1--6)", PURPLE, None),
             ("attn", "Attention (columns 0, 7)", ORANGE, None),
             ("rest", "Host and dispatch", GRAY, None)]
    y = range(len(ns))
    left = [0.0] * len(ns)
    for key, label, color, _ in parts:
        w = [(d[n]["ttft"] - d[n]["gemm"] - d[n]["attn"] - d[n]["lm"] if key == "rest" else d[n][key]) / d[n]["ttft"]
             for n in ns]
        ax.barh(y, w, left=left, color=color, edgecolor="black", linewidth=0.4, height=0.6, label=label)
        left = [a + b for a, b in zip(left, w)]
    ax.set_yticks(list(y), [f"{n:,}" for n in ns])
    ax.set_ylabel("Prompt tokens")
    ax.set_xlabel("Share of TTFT")
    ax.set_xlim(0, 1)
    ax.invert_yaxis()
    ax.legend(ncol=2, loc="lower center", bbox_to_anchor=(0.5, 1.0), handlelength=1.2, columnspacing=1.0)
    fig.savefig(OUT / "busy.pdf")
    plt.close(fig)


def pair_medians():
    """Unique (chunk, GEMM) pairs; a pair measured again in a later batch keeps its first measurement."""
    seen, rows = set(), []
    for f in ("pairs-1.json", "pairs-2.json", "pairs-3.json"):
        for p in json.loads((DATA / f).read_text())["pairs"]:
            key = (p["c"], p["gemm"])
            arms = p["arms"]
            assert all(all(a["ok"]) for a in arms.values()), f"{f} {key}: a gated run failed"
            if key in seen:
                continue
            seen.add(key)
            rows.append({k: statistics.median(v["ms"]) for k, v in arms.items()})
    return rows


def fig_pairs():
    rows = pair_medians()
    fig, ax = plt.subplots(figsize=(COLUMN, 1.5))
    x = [min(r["A"], r["G"]) / max(r["A"], r["G"]) for r in rows]
    lo, hi = 0.0, 1.0
    ax.plot([lo, hi], [1 + lo, 1 + hi], color="black", linewidth=0.5, linestyle=(0, (4, 2)), label="Sum of the two alone")
    ax.plot([lo, hi], [1, 1], color="black", linewidth=0.5, linestyle=(0, (1, 1.5)), label="Longer of the two alone")
    q = [(xi, r["Q"] / max(r["A"], r["G"])) for xi, r in zip(x, rows) if "Q" in r]
    ax.plot([a for a, _ in q], [b for _, b in q], linestyle="none", marker="s", markerfacecolor="none",
            markeredgecolor=INK, markeredgewidth=0.7, label="Two commands, queued")
    ax.plot(x, [r["S2"] / max(r["A"], r["G"]) for r in rows], linestyle="none", marker="^", color=INK,
            label="One command, in sequence")
    ax.plot(x, [r["C"] / max(r["A"], r["G"]) for r in rows], linestyle="none", marker="o", color=MAGENTA,
            label="One command, both issued first")
    ax.set_xlim(lo, hi)
    ax.set_ylim(0.9, 2.05)
    ax.set_xlabel("Shorter operator alone, normalized to the longer")
    ax.set_ylabel("Normalized time")
    ax.legend(ncol=2, loc="lower center", bbox_to_anchor=(0.5, 1.0), handlelength=1.6, columnspacing=1.0)
    fig.savefig(OUT / "pairs.pdf")
    plt.close(fig)


def params_rows():
    p = json.loads((DATA / "component-model.json").read_text())["params"]
    us = lambda v: f"{v * 1000:.0f}\\us"  # noqa: E731  (parameters are stored in ms)
    sb, post = p["stage_busy"], p["post"]
    stages = ("qkv", "o", "gate", "up", "down")
    rows = [
        ("GEMM busy (QKV, O, gate, up, down)", "Device", " / ".join(f"{sb[s]:.2f}" for s in stages) + "\\ms"),
        ("Attention busy at chunk $c$", "Device", f"${p['attn'][0]:.3f} + {p['attn'][1]:.3f}\\,c$\\ms"),
        ("Gap per additional GEMM $\\gamma$", "Device", us(p["gamma"])),
        ("Overlap cost $\\beta$", "Device", f"{p['beta']:.2f}"),
        ("Boundary cost $\\epsilon$ (attention, GEMM only)", "Host", f"{us(p['eps']['attn'])} / {us(p['eps']['gemm'])}"),
        ("Issue cost (attention, GEMM only)", "Host", f"{us(p['issue']['attn'])} / {us(p['issue']['gemm'])}"),
        ("Post cost (QKV, attention, O)", "Host", " / ".join(f"{post[s]:.2f}" for s in ("qkv", "attn", "o")) + "\\ms"),
        ("Post cost (gate, up, down)", "Host", " / ".join(f"{post[s]:.2f}" for s in ("gate", "up", "down")) + "\\ms"),
        ("Head and tail", "Host", f"{p['headtail']:.1f}\\ms"),
    ]
    # The closing rule is part of the file: a rule after \input inside a tabular is a misplaced \noalign.
    (OUT / "params-rows.tex").write_text(
        "% SOURCE: generated by figs/make_figs.py from figs/data/component-model.json; do not edit.\n"
        + "".join(f"{a} & {b} & {c} \\\\\n" for a, b, c in rows) + "\\bottomrule\n")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fig_busy()
    fig_pairs()
    params_rows()
