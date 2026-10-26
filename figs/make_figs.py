#!/usr/bin/env python3
"""The paper's data figures and generated table rows, from the measurements in figs/data/ (sources: figs/README.md).

Outputs (into FIGS_OUT, default paper/fig):
  busy.pdf         TTFT of the existing Llama-3.2-1B prefill split into device-busy time per operator class and the rest
  pairs.pdf        one attention and one GEMM operator: queued, in sequence in one command, and interleaved in one command
  outstanding.pdf  per column group, the CP's blocked time and the time its work was outstanding, existing against composed
  accuracy.pdf     predicted against measured TTFT, with the tolerance committed before the runs
  bound.pdf        distance to the lower bound per cell, measured and as predicted before the runs
  decode.pdf       decode time per token against the cached context, baseline against our loop pass
  timeline.pdf     Figure 1: per column group, work outstanding and the CP blocked, existing against OPCORD
  schedules.pdf    TTFT by split for the three schedules, one panel per model
  choice.pdf       (a) the event model's error per development cell, (b) each choice rule's loss per cell
  vs-flm.pdf       TTFT speedup over FLM's current release, AIR's original and AIR with OPCORD
  synthetic.pdf    the composed order's speedup over the original on three synthetic builds, against the chunks
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

# Type sizes in pt as printed: every paper figure is saved at the width it prints at (save() below), so these are the
# sizes on the page. Axis labels and panel titles; tick labels, legends and category labels; annotations on the data.
# The diagrams in diagrams.py take the scale one step down (titles FS_TICK, labels FS_NOTE).
FS_LABEL, FS_TICK, FS_NOTE = 8, 7, 6

# The MLSys template sets Times; the figures use Times through LaTeX as well.
plt.rcParams.update({
    "text.usetex": True,
    "text.latex.preamble": r"\usepackage{newtxtext}\usepackage{newtxmath}",
    "font.family": "serif",
    "font.size": FS_LABEL,
    "axes.titlesize": FS_LABEL,
    "figure.labelsize": FS_LABEL,  # fig.supxlabel
    "xtick.labelsize": FS_TICK,
    "ytick.labelsize": FS_TICK,
    "legend.title_fontsize": FS_TICK,
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
    "legend.fontsize": FS_TICK,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.01,
})
COLUMN = 3.25  # MLSys column width, inches
WIDE = 6.75  # MLSys two-column width, inches


def save(fig, name, width=COLUMN, relayout=None, **kw):
    """Save fig so that its tight crop is `width` inches wide, the width the paper prints it at, which keeps every
    type size at its printed size. The canvas width is adjusted until the crop matches; relayout re-runs the figure's
    own tight_layout after each change."""
    pad = plt.rcParams["savefig.pad_inches"]
    for _ in range(6):
        if relayout:
            relayout()
        fig.draw_without_rendering()
        w = fig.get_tightbbox().width + 2 * pad
        if abs(w - width) < 0.002:
            break
        fw, fh = fig.get_size_inches()
        fig.set_size_inches(fw + width - w, fh)
    fig.savefig(OUT / name, **kw)

# The paper's own palette, built in OKLCH and checked under deuteranopia, protanopia and tritanopia (the pairs that
# share a figure stay apart): ours violet; attention sand and the GEMMs teal, each with a pastel fill step for areas.
# Each series keeps its color and marker in every figure.
OURS, OURS_TINT = "#714CA6", "#F3EFFB"  # OKLCH (0.50, 0.14, 300); the tint fills our stages in the overview
ATTN, ATTN_FILL = "#DBB970", "#E2CFA8"  # OKLCH (0.80, 0.10, 85), fill at L 0.86
GEMM, GEMM_FILL = "#4E9397", "#B5D9DB"  # OKLCH (0.62, 0.07, 200), fill at L 0.86
ATTN_BAR, GEMM_BAR = "#DDC084", "#83BDC0"  # between the fill and the line step, for the measured timeline's bars
STONE = "#707070"  # neutral mid gray: both groups busy
BLUE, MAGENTA, ORANGE = GEMM, OURS, ATTN  # the names the older figure functions use
PURPLE, GOLD = "#8770E0", "#F0B840"  # used only by figures outside the paper
GRAY = "#B0B0B0"
MIST = "#E4E4E4"  # synchronizations, as in the architecture figure (diagrams.py)
INK = "#262626"  # original schedules: near-black


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


def fig_outstanding():
    """Per column group, how long the CP was blocked on it and how long its work was outstanding (ms).

    The existing order and the composed one, on a 4,096-token prefill of Llama-3.2-1B, from the CP's own
    record timers. Where a group's outstanding time equals the time the CP spent blocked on it, the CP was
    blocked for as long as that group had work, so the two groups took turns."""
    d = json.loads((DATA / "timeline-1b.json").read_text())
    arms = (("shipar", "Alternated baseline"), ("comp", "Composed"))
    fig, axes = plt.subplots(1, 2, figsize=(COLUMN, 1.45), sharex=True)
    for ax, (arm, title) in zip(axes, arms):
        pg = d["per_group"][arm]
        ttft = d["ttft_ms"][arm]["R"]
        ys = [1, 0]  # attention on top, GEMMs below
        for y, g in zip(ys, ("A", "G")):
            out = statistics.median(r["outstanding_ms"] for r in pg[g]["reps"].values())
            blk = statistics.median(r["blocked_ms"] for r in pg[g]["reps"].values())
            first = y == 1 and arm == "shipar"
            # The outstanding bar is outlined so that it stays visible where it equals the blocked bar,
            # which is itself the point of the left panel.
            ax.barh(y, out, height=0.52, color=GRAY, edgecolor=INK, linewidth=0.4, zorder=2,
                    label="Work outstanding" if first else None)
            ax.barh(y, blk, height=0.52, color=INK, edgecolor="none", zorder=3,
                    label="CP blocked on it" if first else None)
        ax.axvline(ttft, color="black", linewidth=0.5, linestyle=(0, (4, 2)), zorder=4)
        ax.annotate(rf"TTFT {ttft / 1000:.2f}\,s", (ttft, -0.62), ha="right", va="bottom", fontsize=6)
        ax.set_yticks(ys, ["Attention", "GEMMs"])
        ax.set_ylim(-0.7, 1.5)
        ax.set_xlim(0, 1750)
        ax.set_xticks([0, 500, 1000, 1500])
        ax.set_title(title, fontsize=8, pad=3)
        ax.tick_params(left=False)
    axes[0].set_xlabel("Time (ms)", x=1.08)
    axes[1].tick_params(labelleft=False)
    axes[0].legend(ncol=2, loc="lower center", bbox_to_anchor=(1.08, 1.22), handlelength=1.2, columnspacing=1.0)
    fig.savefig(OUT / "outstanding.pdf")
    plt.close(fig)


def fig_accuracy():
    """Predicted against measured TTFT, for the cells the registration scored and for the arms reported beside them.

    The band is the tolerance committed before the runs. Existing schedules are drawn in ink and the composed
    one in color, as elsewhere."""
    d = json.loads((DATA / "accuracy.json").read_text())
    tol = d["tolerance"]
    fig, ax = plt.subplots(figsize=(COLUMN, 1.85))
    lo, hi = 1.0, 17.0  # seconds
    ax.plot([lo, hi], [lo, hi], color="black", linewidth=0.5, zorder=1)
    ax.fill_between([lo, hi], [lo * (1 - tol), hi * (1 - tol)], [lo * (1 + tol), hi * (1 + tol)],
                    color=GRAY, alpha=0.35, linewidth=0, zorder=0,
                    label=rf"Band, $\pm${tol * 100:.1f}\%")
    style = {"ship": (INK, "^", "Original"), "shipar": (INK, "s", "Alternated"),
             "comp": (MAGENTA, "o", "Composed")}
    for sched, (color, marker, label) in style.items():
        for rows, claimed in ((d["reported"], False), (d["claimed"], True)):
            pts = [(r["meas"] / 1000, r["pred"] / 1000) for r in rows if r["sched"] == sched]
            if not pts:
                continue
            ax.plot([a for a, _ in pts], [b for _, b in pts], linestyle="none", marker=marker,
                    color=color, markerfacecolor=color if claimed else "none",
                    markeredgecolor=color, markeredgewidth=0.7,
                    label=label if not claimed else None)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ticks = [1, 2, 5, 10]
    ax.set_xticks(ticks, [str(t) for t in ticks])
    ax.set_yticks(ticks, [str(t) for t in ticks])
    ax.set_xlabel("Measured TTFT (s)")
    ax.set_ylabel("Predicted TTFT (s)")
    ax.legend(ncol=2, loc="lower center", bbox_to_anchor=(0.5, 1.0), handlelength=1.6, columnspacing=1.0)
    fig.savefig(OUT / "accuracy.pdf")
    plt.close(fig)


def fig_bound():
    """Distance to the lower bound per append, measured and as the event model prices it."""
    d = json.loads((DATA / "bound.json").read_text())
    cells = d["cells"]
    # Short labels must stay distinct: two of the four models are 4B.
    names = {"llama32_1b_q4nx": "Llama 1B", "qwen3_4b_q4nx": "Qwen 4B",
             "gemma3_4b_q4nx": "Gemma 4B", "llama31_8b_q4nx": "Llama 8B"}
    short = {"append:2048:4096": "2k+4k", "append:8192:4096": "8k+4k", "append:12288:2048": "12k+2k"}
    order = list(names)
    cells = sorted(cells, key=lambda c: (order.index(c["model"]), list(short).index(c["cell"])))
    y = list(range(len(cells)))[::-1]
    fig, ax = plt.subplots(figsize=(COLUMN, 2.3))
    for yi, c in zip(y, cells):
        ax.plot([c["r_pred"]], [yi], marker="|", markersize=5, color=INK, markeredgewidth=0.8, zorder=3,
                label="Event model" if yi == y[0] else None)
        ax.plot([c["r_meas"]], [yi], marker="o", markersize=3, color=MAGENTA, zorder=4,
                label="Measured" if yi == y[0] else None)
        ax.plot([min(c["r_pred"], c["r_meas"]), max(c["r_pred"], c["r_meas"])], [yi, yi],
                color=GRAY, linewidth=0.8, zorder=2)
    labels = [f"{names[c['model']]} {short[c['cell']]}" for c in cells]
    assert len(set(labels)) == len(labels), "model short names collide"
    ax.set_yticks(y, labels)
    ax.set_ylim(-0.8, len(cells) - 0.2)
    ax.set_xlim(1.0, 1.75)
    ax.set_xlabel("Measured TTFT / lower bound")
    ax.tick_params(left=False)
    ax.legend(ncol=2, loc="lower center", bbox_to_anchor=(0.5, 1.0), handlelength=1.4, columnspacing=1.0)
    fig.savefig(OUT / "bound.pdf")
    plt.close(fig)


def fig_order():
    """Schematic: the same operators under two issue orders within one command, with what the CP is doing beneath each.

    Durations are illustrative, not measured; the figure shows the mechanism, and the measured version of the
    same effect is Figure~\\ref{fig:outstanding}. An issue returns at once, so it is drawn narrow; a
    synchronization blocks the CP until the transfer it names completes."""
    A, G, ISS = 3.0, 2.0, 0.22  # attention, each of three GEMMs, and the width of an issue
    serial_attn = [(0.0, A)]
    serial_gemm = [(A + i * G, G) for i in range(3)]
    # CP lane: (start, width, kind), kind 0 = issue (returns at once), 1 = blocked on a synchronization.
    serial_cp, t = [], 0.0
    for dur in (A, G, G, G):
        serial_cp += [(t, ISS, 0), (t + ISS, dur - ISS, 1)]
        t += dur
    ours_cp = [(i * ISS, ISS, 0) for i in range(4)]
    ours_cp += [(4 * ISS, max(A, 3 * G) - 4 * ISS, 1)]
    panels = [
        ("(a) One dispatch, operators in turn", serial_attn, serial_gemm, serial_cp, A + 3 * G),
        ("(b) One dispatch, every group's work issued before any wait",
         serial_attn, [(i * G, G) for i in range(3)], ours_cp, max(A, 3 * G)),
    ]
    fig, axes = plt.subplots(2, 1, figsize=(COLUMN, 1.85))
    span = max(p[4] for p in panels)
    for ax, (title, attn, gemm, cp, end) in zip(axes, panels):
        for color, bars, y in ((ORANGE, attn, 1.0), (BLUE, gemm, 0.0)):
            ax.broken_barh([(t0, d) for t0, d in bars], (y - 0.32, 0.64),
                           facecolors=color, edgecolor=INK, linewidth=0.4)
        for t0, d, kind in cp:
            ax.broken_barh([(t0, d)], (-1.32, 0.5), facecolors=INK if kind == 0 else MIST,
                           edgecolor=INK, linewidth=0.3)
        ax.axvline(end, color="black", linewidth=0.5, linestyle=(0, (4, 2)))
        ax.set_yticks([1.0, 0.0, -1.07], ["Attention", "GEMMs", "CP"])
        ax.set_ylim(-1.75, 1.6)
        ax.set_xlim(-0.1, span + 0.5)
        ax.set_title(title, fontsize=7, pad=2, loc="left")
        ax.tick_params(left=False, right=False, top=False, bottom=False)
        ax.set_xticks([])
        for side in ("top", "right", "bottom"):
            ax.spines[side].set_visible(False)
    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=INK, edgecolor=INK, linewidth=0.3),
               plt.Rectangle((0, 0), 1, 1, facecolor=MIST, edgecolor=INK, linewidth=0.3)]
    axes[0].legend(handles, ["CP issuing", "CP blocked on a synchronization"], ncol=2,
                   loc="lower center", bbox_to_anchor=(0.5, 1.12), handlelength=1.2, columnspacing=1.0)
    axes[-1].set_xlabel("Time (illustrative)", labelpad=1)
    fig.savefig(OUT / "order.pdf")
    plt.close(fig)


def fig_turns():
    """Whole-turn speedup against the faster shipped split, by append size, per model and cached context.

    A turn is its append plus 250 decoded tokens and excludes the KV handoff on both models. The shaded band
    spans the 25th to 90th percentile of the new tokens per agent step in the traces, with the median marked."""
    d = json.loads((DATA / "turns.json").read_text())
    pct = d["append_percentiles"]["claude"]
    fig, ax = plt.subplots(figsize=(COLUMN, 1.8))
    ax.axvspan(pct[0], pct[2], color=GRAY, alpha=0.3, linewidth=0, zorder=0,
               label="Traces, 25th--90th percentile")
    ax.axvline(pct[1], color=INK, linewidth=0.5, linestyle=(0, (1, 1.5)), zorder=1, label="Median step")
    styles = {"Llama-3.2-1B": (MAGENTA, "o"), "Qwen3-4B": (BLUE, "s")}
    dashes = {"4096": (0, (1, 1.5)), "16384": (0, ()), "28672": (0, (4, 2))}
    for model, ctxs in d["models"].items():
        color, marker = styles[model]
        for L, cells in sorted(ctxs.items(), key=lambda kv: int(kv[0])):
            pts = sorted((int(n), v["bvb"]) for n, v in cells.items())
            ax.plot([a for a, _ in pts], [b for _, b in pts], marker=marker, color=color,
                    linestyle=dashes[L], markersize=2.5, label=None)
    ax.axhline(1.0, color="black", linewidth=0.5, zorder=1)
    ax.set_xscale("log")
    ax.set_xticks([512, 1024, 4096], ["512", "1k", "4k"])
    ax.set_xlim(380, 9000)
    ax.set_ylim(0.98, 1.42)
    ax.set_xlabel("New tokens in the step")
    ax.set_ylabel("Turn speedup")
    handles = [plt.Line2D([], [], color=c, marker=m, markersize=2.5, linestyle="-") for c, m in styles.values()]
    handles += [plt.Line2D([], [], color=INK, linestyle=dashes[L]) for L in ("4096", "16384", "28672")]
    labels = list(styles) + ["4k context", "16k context", "28k context"]
    ax.legend(handles, labels, ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.0),
              handlelength=1.5, columnspacing=0.9)
    fig.savefig(OUT / "turns.pdf")
    plt.close(fig)


def params_rows():
    p = json.loads((DATA / "component-model.json").read_text())["params"]
    us = lambda v: f"{v * 1000:.0f}\\us"  # noqa: E731  (parameters are stored in ms)
    sb, post = p["stage_busy"], p["post"]
    stages = ("qkv", "o", "gate", "up", "down")
    groups = [
        ("Device", [
            ("GEMM busy (QKV, O, gate, up, down)", " / ".join(f"{sb[s]:.2f}" for s in stages) + "\\ms"),
            ("Attention busy at chunk $c$", f"${p['attn'][0]:.3f} + {p['attn'][1]:.3f}\\,c$\\ms"),
            ("Gap per additional GEMM $\\gamma$", us(p["gamma"])),
            ("Overlap cost $\\beta$", f"{p['beta']:.2f}"),
        ]),
        ("Host", [
            ("Boundary cost $\\epsilon$ (attention, GEMM only)", f"{us(p['eps']['attn'])} / {us(p['eps']['gemm'])}"),
            ("Issue cost (attention, GEMM only)", f"{us(p['issue']['attn'])} / {us(p['issue']['gemm'])}"),
            ("Post cost (QKV, attention, O)", " / ".join(f"{post[s]:.2f}" for s in ("qkv", "attn", "o")) + "\\ms"),
            ("Post cost (gate, up, down)", " / ".join(f"{post[s]:.2f}" for s in ("gate", "up", "down")) + "\\ms"),
            ("Head and tail", f"{p['headtail']:.1f}\\ms"),
        ]),
    ]
    body = ""
    for i, (name, rows) in enumerate(groups):
        body += ("\\midrule\n" if i else "") + f"\\textit{{{name}}} & \\\\\n"
        body += "".join(f"{a} & {b} \\\\\n" for a, b in rows)
    # The closing rule is part of the file: a rule after \input inside a tabular is a misplaced \noalign.
    (OUT / "params-rows.tex").write_text(
        "% SOURCE: generated by figs/make_figs.py from figs/data/component-model.json; do not edit.\n"
        + body + "\\bottomrule\n")
def fig_schedules():
    """TTFT by split for the three schedules, one panel per model, at the cell every model shares.

    The shipped arm and the hand-alternated one differ only where attention has two columns to alternate;
    the composed arm is below both at every split, and which split is fastest is a property of the model."""
    d = json.loads((DATA / "accuracy.json").read_text())
    rows = d["claimed"] + d["reported"]
    cell = "append:8192:4096"
    models = [("llama32_1b_q4nx", "Llama-3.2-1B"), ("qwen3_4b_q4nx", "Qwen3-4B"),
              ("gemma3_4b_q4nx", "Gemma3-4B"), ("llama31_8b_q4nx", "Llama-3.1-8B")]
    series = [("ship", "Original", INK, "^", (0, (1, 1.5))),
              ("shipar", "Alternated", GRAY, "s", (0, (4, 2))),
              ("comp", "Composed", MAGENTA, "o", (0, ()))]
    fig, axes = plt.subplots(2, 2, figsize=(COLUMN, 2.6))
    for ax, (key, label) in zip(axes.flat, models):
        at = {(r["sched"], r["split"]): r["meas"] for r in rows
              if r["model"] == key and r["cell"] == cell}
        splits = sorted({sp for _, sp in at}, key=lambda s: int(s[1:]))
        for sched, _, color, marker, dash in series:
            y = [at[(sched, sp)] / 1000 for sp in splits]
            ax.plot(range(len(splits)), y, color=color, marker=marker, linestyle=dash,
                    markerfacecolor="white" if sched != "comp" else color, markersize=2.5)
        ax.set_xticks(range(len(splits)), [f"$S_{sp[1:]}$" for sp in splits])
        ax.set_xlim(-0.3, len(splits) - 0.7)
        ax.set_title(label, fontsize=7, pad=2)
        ax.tick_params(labelsize=7)
    for ax in axes[:, 0]:
        ax.set_ylabel("TTFT (s)")
    handles = [plt.Line2D([], [], color=c, marker=m, linestyle=ds, markersize=2.5,
                          markerfacecolor="white" if k != "comp" else c) for k, _, c, m, ds in series]
    fig.legend(handles, [l for _, l, _, _, _ in series], ncol=3, loc="lower center",
               bbox_to_anchor=(0.5, 0.99), handlelength=1.8, columnspacing=1.0)
    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / "schedules.pdf")
    plt.close(fig)


def _merge(iv):
    out = []
    for s, e in sorted(iv):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


def _intersect(a, b):
    out, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        s, e = max(a[i][0], b[j][0]), min(a[i][1], b[j][1])
        if e > s:
            out.append((s, e))
        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1
    return out


def fig_timeline():
    """Figure 1: when each column group had work outstanding over one prefill, and when both did, existing against OPCORD.

    Llama-3.2-1B, a 4,096-token prompt on the two-column split, the median-TTFT run of each arm, from the CP's own record
    timers: the unmodified existing program and the composed order. The exact intervals are drawn, unmerged, and the
    third lane is their intersection, so the overlap the figure shows is the overlap the data holds; it is checked
    against the reader's own both-outstanding total."""
    d = json.loads((DATA / "fig1-intervals-1b.json").read_text())["arms"]
    arms = (("ship", "Original"), ("comp", "OPCORD"))
    rows = (("A", "Attention", ATTN_BAR), ("G", "GEMMs", GEMM_BAR))
    fig, axes = plt.subplots(2, 1, figsize=(COLUMN, 1.15), sharex=True)
    base = d["ship"]["ttft_ms"]  # time is drawn relative to the original's TTFT

    def rel(spans):
        return [(s / base, (e - s) / base) for s, e in spans]
    for ax, (arm, name) in zip(axes, arms):
        a = d[arm]
        groups = {g: _merge(a["outstanding"][g]) for g, _, _ in rows}
        for y, (g, label, color) in zip((2, 1), rows):
            ax.broken_barh(rel(groups[g]), (y - 0.32, 0.64), facecolors=color, edgecolor="none")
        both = _intersect(groups["A"], groups["G"])  # checked against the record, not drawn
        overlap = sum(e - s for s, e in both)
        assert abs(overlap - a["both_outstanding_ms"]) < 1e-3, (arm, overlap, a["both_outstanding_ms"])
        ttft = a["ttft_ms"]
        ax.axvline(ttft / base, color="black", linewidth=0.6, linestyle=(0, (4, 2)))
        ax.text(ttft / base + 0.008, 1.5, rf"{ttft / base:.2f}", ha="left", va="center", fontsize=FS_NOTE)
        ax.set_title(name, pad=2, loc="left")
        ax.set_yticks([2, 1], ["Attention", "GEMMs"])
        ax.set_ylim(0.45, 2.55)
        ax.tick_params(axis="y", length=0, left=False, right=False)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.tick_params(axis="x", top=False)
    axes[-1].set_xlim(0, 1.12)
    axes[-1].set_xlabel("Normalized time (original TTFT = 1)", labelpad=1)
    save(fig, "timeline.pdf", relayout=lambda: fig.tight_layout(pad=0.2, h_pad=0.3))
    plt.close(fig)


# light steps of OURS, so the near-black error bars stay visible on every bar
SPLIT_COLOR = {"S1": "#E8DFFD", "S2": "#CEBEEF", "S4": "#AE97D9"}
LLMS = ("Llama-3.2-1B", "LFM2-1.2B", "Qwen3-4B", "Gemma3-4B", "Llama-3.1-8B")


def fig_headline():
    """Headline: OPCORD's TTFT speedup over the baseline at every power-of-two prompt length, one panel per LLM.

    data/prefill-cells.json (figs/paper_numbers.py): baseline = the original program on the fastest supported split
    measured, OPCORD = the event model's pick as measured; whiskers are the 95% interval where the two ran paired (or
    chained through a paired version); the shade gives the split the pick runs on."""
    cells = json.loads((DATA / "prefill-cells.json").read_text())["cells"]
    lengths = [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768]
    labels = ["128", "256", "512", "1K", "2K", "4K", "8K", "16K", "32K"]
    fig, axes = plt.subplots(1, len(LLMS), figsize=(WIDE, 1.45), sharey=True)
    for ax, llm in zip(axes, LLMS):
        at = {c["N"]: c for c in cells if c["llm"] == llm}
        for i, n in enumerate(lengths):
            c = at.get(n)
            if c is None or c.get("unpriced"):
                continue
            ax.bar(i, c["gain"] - 1.0, bottom=1.0, width=0.72, color=SPLIT_COLOR[c["pick_split"]], edgecolor="none",
                   zorder=2)
            # a cap at the value, so a pick that keeps the original order (exactly 1) still shows its split
            ax.plot([i - 0.36, i + 0.36], [c["gain"]] * 2, color=SPLIT_COLOR[c["pick_split"]], linewidth=1.4,
                    solid_capstyle="butt", zorder=2)
            if c.get("lo") is None:
                # the baseline and the pick ran in different batches with no shared version: no interval
                ax.text(i, c["gain"] + 0.01, r"$\dagger$", ha="center", va="bottom", fontsize=FS_NOTE)
            elif c["hi"] > c["lo"]:
                ax.errorbar(i, c["gain"], yerr=[[c["gain"] - c["lo"]], [c["hi"] - c["gain"]]], fmt="none",
                            ecolor=INK, elinewidth=0.5, capsize=1.0, zorder=3)
        ax.axhline(1.0, color="black", linewidth=0.5, zorder=4)
        ax.set_xticks(range(len(lengths)), [lb if k % 2 == 0 else "" for k, lb in enumerate(labels)])
        ax.set_xlim(-0.6, len(lengths) - 0.4)
        ax.tick_params(axis="x", length=0, pad=1.5)
        ax.set_title(llm, pad=2)
    axes[0].set_ylabel("TTFT speedup", labelpad=2)
    axes[0].set_ylim(0.9, 1.72)
    handles = [plt.Rectangle((0, 0), 1, 1, color=SPLIT_COLOR[s]) for s in ("S1", "S2", "S4")]
    axes[0].legend(handles, ["$S_1$", "$S_2$", "$S_4$"], title="Configuration", loc="upper left", handlelength=0.9,
                   handletextpad=0.4, borderaxespad=0.2, labelspacing=0.2)
    fig.supxlabel("Prompt length (tokens)", y=-0.02)
    save(fig, "headline.pdf", width=WIDE, relayout=lambda: fig.tight_layout(pad=0.2, w_pad=0.3))
    plt.close(fig)


# Our color for every LLM's gain from OPCORD, the LLMs told apart by marker and line style.
DECODE_STYLE = {"Llama-3.2-1B": ("o", "full", (0, ())), "LFM2-1.2B": ("s", "none", (0, ())),
                "Qwen3-4B": ("^", "full", (0, (4, 1.5))), "Llama-3.1-8B": ("D", "none", (0, (4, 1.5))),
                "Gemma3-4B": ("v", "full", (0, (1, 1.2)))}


def fig_decode():
    """Decode: the loop pass's speedup in time per token over the unmodified decode design against the cached context.

    data/decode-cells.json (figs/paper_numbers.py): one development batch, 5 ABBA repetitions of 256 greedy tokens per
    point, logits bit-identical; the last context is 30,208 tokens (28,800 on Qwen3-4B, its design's window)."""
    cells = json.loads((DATA / "decode-cells.json").read_text())["cells"]
    fig, ax = plt.subplots(figsize=(COLUMN, 1.3))
    order = ("Llama-3.2-1B", "LFM2-1.2B", "Qwen3-4B", "Llama-3.1-8B", "Gemma3-4B")
    for llm in order:
        pts = sorted((c["P"], c) for c in cells if c["llm"] == llm)
        marker, fill, dash = DECODE_STYLE[llm]
        xs, ys = [p / 1024 for p, _ in pts], [c["gain"] for _, c in pts]
        ax.errorbar(xs, ys, yerr=[[c["gain"] - c["lo"] for _, c in pts], [c["hi"] - c["gain"] for _, c in pts]],
                    fmt="none", ecolor=INK, elinewidth=0.5, capsize=1.0)
        ax.plot(xs, ys, color=OURS, marker=marker, markersize=2.6, linestyle=dash, linewidth=0.7,
                markerfacecolor=OURS if fill == "full" else "white", markeredgewidth=0.6, label=llm)
    ax.axhline(1.0, color="black", linewidth=0.5)
    ax.set_xlabel("Cached context (K tokens)", labelpad=1)
    ax.set_ylabel("Decode speedup", labelpad=2)
    ax.set_xticks([0, 8, 16, 24, 32])
    ax.set_xlim(0, 32)
    ax.set_ylim(0.95, 1.45)
    ax.legend(loc="upper left", ncol=2, handlelength=1.6, columnspacing=0.8, labelspacing=0.2)
    save(fig, "decode.pdf")
    plt.close(fig)


# Three synthetic builds told apart by marker, in our color as in the decode figure.
SYNTH_STYLE = {"synth_ag_d1024_i768": ("Light GEMMs", "o", "full", (0, ())),
               "synth_ag_d2048_i2304": ("Medium GEMMs", "s", "none", (0, (4, 1.5))),
               "synth_ag_d2048_i12288": ("Heavy GEMMs", "^", "full", (0, (1, 1.2)))}


def fig_synthetic():
    """The synthetic sweep: the composed order's TTFT speedup over the original order against the prompt length in
    128-token chunks, for three two-layer builds of MLIR-AIR's fused prefill that keep attention fixed and vary the
    GEMMs' work. data/synthetic.json: the repeat-position ratio, median with its 95% interval."""
    cells = json.loads((DATA / "synthetic.json").read_text())
    fig, ax = plt.subplots(figsize=(COLUMN, 1.5))
    for model, (label, marker, fill, dash) in SYNTH_STYLE.items():
        pts = sorted((c["C"], c["repeat"]) for c in cells if c["model"] == model)
        xs = [c for c, _ in pts]
        med, lo, hi = ([r[k] for _, r in pts] for k in range(3))
        ax.errorbar(xs, med, yerr=[[m - l for m, l in zip(med, lo)], [h - m for m, h in zip(med, hi)]], fmt="none",
                    ecolor=INK, elinewidth=0.5, capsize=1.0)
        ax.plot(xs, med, color=OURS, marker=marker, markersize=2.6, linestyle=dash, linewidth=0.7,
                markerfacecolor=OURS if fill == "full" else "white", markeredgewidth=0.6, label=label)
    ax.axhline(1.0, color="black", linewidth=0.5)
    ax.set_xscale("log", base=2)
    ax.set_xticks([1, 2, 4, 8, 16, 32], ["1", "2", "4", "8", "16", "32"])
    ax.minorticks_off()
    ax.set_xlabel("Prompt length (128-token chunks)", labelpad=1)
    ax.set_ylabel("TTFT speedup", labelpad=2)
    ax.set_ylim(0.8, 1.8)
    ax.legend(loc="upper left", handlelength=1.6, labelspacing=0.2)
    save(fig, "synthetic.pdf")
    plt.close(fig)


KEY_LLM = {"llama32_1b": "Llama-3.2-1B", "lfm2_1_2b": "LFM2-1.2B", "qwen3_4b": "Qwen3-4B", "gemma3_4b": "Gemma3-4B",
           "llama31_8b": "Llama-3.1-8B"}
CHOICE_RULES = (("opcord", "OPCORD"), ("always", "Always reorder"), ("fixed_s2", "Always $S_2$"),
                ("four_base", "Reorder if $C \\ge 4$"))


def fig_choice():
    """(a) The event model's error on each development cell's original-to-composed ratio against that ratio, and
    (b) each choice rule's worst loss against the fastest measured choice.

    data/accuracy-cells.json (the frozen form's 70 development cells) and data/choice.json (the 59 priced cells).
    "Never reorder" is left out of (b): its loss is the headline gain forgone, which Figure 6 shows."""
    rows = json.loads((DATA / "accuracy-cells.json").read_text())
    fig, (a, b) = plt.subplots(2, 1, figsize=(COLUMN, 2.8), gridspec_kw=dict(height_ratios=[1.35, 0.85], hspace=0.62))
    a.axhspan(-5, 5, color="#EDEDED", zorder=0, linewidth=0)
    for key, llm in KEY_LLM.items():
        rs = [r for r in rows if r["model"].startswith(key)]
        marker, fill, _ = DECODE_STYLE[llm]
        a.plot([r["measured"] for r in rs], [(r["dev"] - 1) * 100 for r in rs], linestyle="none", marker=marker,
               markersize=2.8, color=INK, markerfacecolor=INK if fill == "full" else "white", markeredgewidth=0.6,
               label=llm)
    a.axhline(0, color="black", linewidth=0.5)
    a.set_xscale("log", base=2)
    a.set_xticks([1, 1.25, 1.5, 2], ["1.0", "1.25", "1.5", "2.0"])
    a.minorticks_off()
    a.set_xlabel("Measured TTFT speedup of the composed order", labelpad=1)
    a.set_ylabel(r"Prediction error (\%)", labelpad=1)
    a.set_ylim(-24, 8)  # room below the band for the legend
    a.legend(loc="lower left", ncol=2, handletextpad=0.2, columnspacing=0.6, labelspacing=0.15)
    a.set_title("(a) Event model", pad=3)
    cells = json.loads((DATA / "choice.json").read_text())["cells"]
    labels = []
    for i, (key, label) in enumerate(CHOICE_RULES):  # each rule's worst loss
        v = [c[key] for c in cells if c.get(key) is not None]
        worst = max(v)
        b.barh(i, worst, height=0.6, color=OURS if key == "opcord" else GRAY, edgecolor="none")
        b.text(worst + 1.5, i, f"{worst:.1f}", ha="left", va="center", fontsize=FS_NOTE)
        labels.append(label)
    b.set_xlim(0, 110)
    b.set_xticks([0, 25, 50, 75, 100])
    b.set_ylim(len(CHOICE_RULES) - 0.5, -0.5)
    b.set_yticks(range(len(CHOICE_RULES)), labels)
    b.tick_params(axis="y", length=0)
    b.set_xlabel(r"Worst loss (\%)", labelpad=1)
    b.set_title("(b) Choice of order and configuration", pad=3)
    save(fig, "choice.pdf")
    plt.close(fig)


def fig_vs_flm():
    """TTFT speedup over FLM's current release at 1K, 4K and 16K tokens: AIR's original program on its default
    configuration, and the same design under OPCORD. data/absolute.json (D1, one batch)."""
    rows = json.loads((DATA / "absolute.json").read_text())["rows"]
    fig, ax = plt.subplots(figsize=(COLUMN, 1.25))
    x, ticks, labels = 0.0, [], []
    for llm in LLMS:
        rs = sorted((r for r in rows if r["llm"] == llm and r.get("N") in (1024, 4096, 16384)), key=lambda r: r["N"])
        x0 = x
        for r in rs:
            o, p = r["flm_ms"] / r["orig_s2_ms"], r["flm_ms"] / r["opcord_ms"]
            ax.plot([x, x], [o, p], color=GRAY, linewidth=0.6, zorder=1)
            ax.plot(x, o, marker="s", markersize=2.8, color=INK, markerfacecolor="white", markeredgewidth=0.6, zorder=2)
            ax.plot(x, p, marker="o", markersize=3.0, color=OURS, markeredgewidth=0, zorder=3)
            ticks.append(x)
            labels.append({1024: "1K", 4096: "4K", 16384: "16K"}[r["N"]])
            x += 1.2
        ax.text((x0 + x - 1.2) / 2, 2.6, llm, ha="center", va="bottom", fontsize=FS_NOTE)
        x += 0.8
    ax.axhline(1.0, color="black", linewidth=0.5)
    ax.set_yscale("log", base=2)
    ax.set_yticks([0.5, 1, 2], ["0.5", "1", "2"])
    ax.minorticks_off()
    ax.set_ylim(0.45, 3.4)
    ax.set_xticks(ticks, labels)
    ax.tick_params(axis="x", length=0, pad=1.5)
    ax.set_ylabel("TTFT speedup", labelpad=1)
    handles = [plt.Line2D([], [], marker="s", markersize=2.8, color=INK, markerfacecolor="white", linestyle="none",
                          markeredgewidth=0.6),
               plt.Line2D([], [], marker="o", markersize=3, color=OURS, linestyle="none", markeredgewidth=0)]
    ax.legend(handles, [r"AIR, $S_2$", "AIR with OPCORD"], loc="upper center", bbox_to_anchor=(0.5, -0.13),
              handletextpad=0.2, ncol=2)
    save(fig, "vs-flm.pdf")
    plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fig_busy()
    fig_pairs()
    fig_outstanding()
    fig_accuracy()
    fig_bound()
    fig_order()
    fig_turns()
    fig_decode()
    fig_schedules()
    fig_timeline()
    fig_headline()
    fig_synthetic()
    fig_choice()
    fig_vs_flm()
    params_rows()
