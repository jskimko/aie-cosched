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

# The MLSys template sets Times; the figures use Times through LaTeX as well.
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
COLUMN = 3.25  # MLSys column width, inches

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
    style = {"ship": (INK, "^", "Existing"), "shipar": (INK, "s", "Alternated"),
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
        ("(a) One command, operators in turn", serial_attn, serial_gemm, serial_cp, A + 3 * G),
        ("(b) One command, every group's work issued before any wait",
         serial_attn, [(i * G, G) for i in range(3)], ours_cp, max(A, 3 * G)),
    ]
    fig, axes = plt.subplots(2, 1, figsize=(COLUMN, 1.85))
    span = max(p[4] for p in panels)
    for ax, (title, attn, gemm, cp, end) in zip(axes, panels):
        for color, bars, y in ((ORANGE, attn, 1.0), (BLUE, gemm, 0.0)):
            ax.broken_barh([(t0, d) for t0, d in bars], (y - 0.32, 0.64),
                           facecolors=color, edgecolor=INK, linewidth=0.4)
        for t0, d, kind in cp:
            ax.broken_barh([(t0, d)], (-1.32, 0.5), facecolors=INK if kind == 0 else GRAY,
                           edgecolor=INK, linewidth=0.3)
        ax.axvline(end, color="black", linewidth=0.5, linestyle=(0, (4, 2)))
        ax.set_yticks([1.0, 0.0, -1.07], ["Attn.", "GEMMs", "CP"])
        ax.set_ylim(-1.75, 1.6)
        ax.set_xlim(-0.1, span + 0.5)
        ax.set_title(title, fontsize=7, pad=2, loc="left")
        ax.tick_params(left=False, right=False, top=False, bottom=False)
        ax.set_xticks([])
        for side in ("top", "right", "bottom"):
            ax.spines[side].set_visible(False)
    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=INK, edgecolor=INK, linewidth=0.3),
               plt.Rectangle((0, 0), 1, 1, facecolor=GRAY, edgecolor=INK, linewidth=0.3)]
    axes[0].legend(handles, ["CP issuing", "CP blocked on a synchronization"], ncol=2,
                   loc="lower center", bbox_to_anchor=(0.5, 1.28), handlelength=1.2, columnspacing=1.0)
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
def fig_decode():
    """Decode time per token against the cached context, baseline against our loop pass, per model.

    Both arms emit bit-identical logits at every point. The fitted slope per position is annotated, because
    what the renaming removes is the part of each position's cost that waited on the previous block."""
    panels = [("Llama-3.2-1B", "decode-1b.json", MAGENTA, "o"),
              ("Qwen3-4B", "decode-qwen.json", MAGENTA, "o")]  # one encoding per series in every panel
    fig, axes = plt.subplots(1, 2, figsize=(COLUMN, 1.6), sharex=True)
    for ax, (model, name, color, marker) in zip(axes, panels):
        d = json.loads((DATA / name).read_text())
        pts = sorted((int(p), v) for p, v in d["points"].items())
        # 32,517 repeats 32,512 as the reproduction point; the figure keeps the first.
        seen, keep = set(), []
        for p, v in pts:
            if any(abs(p - q) < 64 for q in seen):
                continue
            seen.add(p)
            keep.append((p, v))
        x = [p for p, _ in keep]
        ax.plot(x, [v["census_ms_tok"] for _, v in keep], color=INK, marker=marker, linestyle=(0, (4, 2)),
                markerfacecolor="white", label="Existing")
        ax.plot(x, [v["R_ms_tok"] for _, v in keep], color=color, marker=marker, label="Renamed")
        for p, v in keep[-1:]:
            ax.annotate(f"${v['census_ms_tok'] / v['R_ms_tok']:.2f}\\times$",
                        (p, v["R_ms_tok"]), textcoords="offset points", xytext=(1, -13),
                        ha="right", fontsize=7, color=color)
        slope = d["R_fit"]["slope_us_per_pos"]
        base = d["census_fit"]["slope_us_per_pos"]
        ax.set_title(model, fontsize=7, pad=2, loc="left")
        ax.text(0.03, 0.97, f"{base:.2f} to {slope:.2f}\\,$\\mu$s/pos.",
                transform=ax.transAxes, fontsize=6.5, va="top")
        ax.set_xlabel("Cached context, tokens")
        ax.set_ylim(0, None)
        ax.set_xticks([0, 16384, 32768], ["0", "16k", "32k"])
    axes[0].set_ylabel("ms per token")
    axes[1].legend(ncol=1, loc="lower right", handlelength=1.8)
    fig.savefig(OUT / "decode.pdf")
    plt.close(fig)


def fig_schedules():
    """TTFT by split for the three schedules, one panel per model, at the cell every model shares.

    The shipped arm and the hand-alternated one differ only where attention has two columns to alternate;
    the composed arm is below both at every split, and which split is fastest is a property of the model."""
    d = json.loads((DATA / "accuracy.json").read_text())
    rows = d["claimed"] + d["reported"]
    cell = "append:8192:4096"
    models = [("llama32_1b_q4nx", "Llama-3.2-1B"), ("qwen3_4b_q4nx", "Qwen3-4B"),
              ("gemma3_4b_q4nx", "Gemma3-4B"), ("llama31_8b_q4nx", "Llama-3.1-8B")]
    series = [("ship", "Existing", INK, "^", (0, (1, 1.5))),
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
    arms = (("ship", "Existing"), ("comp", "OPCORD"))
    rows = (("A", "Attention", ORANGE), ("G", "GEMMs", BLUE))
    fig, axes = plt.subplots(2, 1, figsize=(COLUMN, 1.45), sharex=True)
    base = d["ship"]["ttft_ms"]
    for ax, (arm, name) in zip(axes, arms):
        a = d[arm]
        groups = {g: _merge(a["outstanding"][g]) for g, _, _ in rows}
        for y, (g, label, color) in zip((3, 2), rows):
            ax.broken_barh([(s, e - s) for s, e in groups[g]], (y - 0.32, 0.64), facecolors=color, edgecolor="none")
        both = _intersect(groups["A"], groups["G"])
        ax.broken_barh([(s, e - s) for s, e in both], (1 - 0.32, 0.64), facecolors=INK, edgecolor="none")
        overlap = sum(e - s for s, e in both)
        assert abs(overlap - a["both_outstanding_ms"]) < 1e-3, (arm, overlap, a["both_outstanding_ms"])
        ttft = a["ttft_ms"]
        ax.axvline(ttft, color="black", linewidth=0.6, linestyle=(0, (4, 2)))
        gain = "" if arm == "ship" else rf", ${base / ttft:.2f}\times$"
        ax.text(ttft + 15, 2.5, rf"TTFT {ttft / 1000:.2f}\,s{gain}", ha="left", va="center", fontsize=6.5)
        ax.text(ttft + 15, 1, rf"{overlap:.0f}\,ms", ha="left", va="center", fontsize=6.5)
        ax.set_title(name, fontsize=7, pad=2, loc="left")
        ax.set_yticks([3, 2, 1], ["Attention", "GEMMs", "Both"], fontsize=6.5)
        ax.set_ylim(0.45, 3.55)
        ax.tick_params(axis="y", length=0, left=False, right=False)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.tick_params(axis="x", top=False)
    axes[-1].set_xlim(0, 2150)
    axes[-1].set_xlabel("Time into the prefill (ms)", labelpad=1)
    fig.tight_layout(pad=0.2, h_pad=0.3)
    fig.savefig(OUT / "timeline.pdf")
    plt.close(fig)


WIDE = 6.75  # MLSys two-column width, inches
MAGENTA_PASTEL = "#EBA8C8"  # pastel step of MAGENTA, for the first size in each panel


def fig_headline():
    """Headline: OPCORD's TTFT speedup over the fastest existing schedule measured, per LLM, from scratch and on appends.

    One source for all five LLMs, the split sweep (figs/headline_data.py -> data/headline.json): existing = the lowest
    median of the shipped order and the shipped order with attention's columns alternated over every measured split;
    OPCORD = the lowest median of the composed schedule over every measured split. Whiskers span the reps' range."""
    d = json.loads((DATA / "headline.json").read_text())["cells"]
    llms = list(d)
    panels = (("From scratch", (("scratch:0:2048", "2K tokens"), ("scratch:0:4096", "4K tokens"))),
              ("Append of 4K tokens", (("append:4096:4096", "to 4K cached"), ("append:16384:4096", "to 16K cached"))))
    fig, axes = plt.subplots(1, 2, figsize=(WIDE, 1.7), sharey=True)
    width = 0.36
    for ax, (title, cells) in zip(axes, panels):
        for k, ((cell, label), color) in enumerate(zip(cells, (MAGENTA_PASTEL, MAGENTA))):
            xs, ys, lo, hi = [], [], [], []
            for i, llm in enumerate(llms):
                c = d[llm].get(cell)
                if c is None:
                    continue
                x = i + (k - 0.5) * width
                xs.append(x); ys.append(c["ratio"]); lo.append(c["ratio"] - c["ratio_lo"]); hi.append(c["ratio_hi"] - c["ratio"])
                ax.text(x, c["ratio_hi"] + 0.02, c["opcord_arm"].split("@")[1].replace("S", "$S_") + "$",
                        ha="center", va="bottom", fontsize=5.5)
            ax.bar(xs, ys, width=width, color=color, edgecolor="none", label=label, zorder=2)
            ax.errorbar(xs, ys, yerr=[lo, hi], fmt="none", ecolor=INK, elinewidth=0.5, capsize=1.2, zorder=3)
        ax.axhline(1.0, color="black", linewidth=0.6)
        ax.set_xticks(range(len(llms)), llms, fontsize=6.5)
        ax.set_title(title, fontsize=7, pad=2, loc="left")
        ax.legend(frameon=False, fontsize=6, loc="upper right", ncol=2, handlelength=1.0, columnspacing=0.8)
    axes[0].set_ylabel("TTFT speedup", labelpad=2)
    axes[0].set_ylim(0.9, 1.72)
    fig.tight_layout(pad=0.2, w_pad=0.6)
    fig.savefig(OUT / "headline.pdf")
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
    params_rows()
