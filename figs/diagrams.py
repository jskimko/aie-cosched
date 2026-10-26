#!/usr/bin/env python3
"""The paper's schematic figures (not data plots), drawn as line art in make_figs.py's style.

  FIGS_OUT=paper/fig .venv/bin/python figs/diagrams.py

Outputs:
  framework.pdf  OPCORD's components over a compiled design, full width: inputs, analysis, checked rewrites, event
                 model, output
  arch.pdf  the XDNA 2 NPU as the paper uses it: host, hardware context, the CP's in-order instruction stream, the
            array of shim, memory and compute tiles over DRAM, and one compute tile and one shim tile magnified
  rewrites.pdf  what the loop pass does: its two-slot ring on decode attention's block loop, against one buffer per role
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_figs as _m  # noqa: E402  (style, palette, OUT)
from make_figs import COLUMN, GRAY, INK, ORANGE, OUT, plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, Rectangle  # noqa: E402

MIST, STONE = "#E4E4E4", "#707070"
# pastel steps of make_figs' ORANGE (attention) and BLUE (GEMMs), for the column groups of the default split
ATTN_PASTEL, GEMM_PASTEL = "#F5BC9C", "#B6CAF7"
FS = 6  # label size, pt


def _canvas(w, h):
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def _box(ax, x, y, w, h, text=None, fc="white", lw=0.5, z=2, fs=FS, ha="center"):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fc, edgecolor=INK, linewidth=lw, zorder=z))
    if text:
        tx = x + w / 2 if ha == "center" else x + 0.03
        ax.text(tx, y + h / 2, text, ha=ha, va="center_baseline", fontsize=fs, zorder=z + 1)


def _arrow(ax, p, q, z=10, lw=0.6, ls="-"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>,head_length=2.2,head_width=1.2", color=INK, linewidth=lw,
                                 linestyle=ls, zorder=z, shrinkA=0, shrinkB=0))


def fig_arch():
    """The host submits commands to a hardware context, whose CP executes each command's instruction stream in order:
    an issue pushes a BD into a shim tile's DMA queue and returns at once, a synchronization blocks the CP until a
    transfer completes. The array runs data-driven: each tile's DMA moves blocks between local memory and the stream
    switch along a chain of BDs, and locks hand each buffer between its producer and its consumer. The compute tiles
    are tinted by the column group that the existing prefill's default split gives them: attention on columns 0 and 7,
    the GEMMs on columns 1-6."""
    W, H = COLUMN - 0.04, 1.86
    fig, ax = _canvas(W, H)
    # ---- the submission path along the top: host -> hardware context -> CP -> its instruction stream
    ty, th = 1.62, 0.2
    _box(ax, 0.02, ty, 0.38, th, "Host", fc=MIST)
    _box(ax, 0.52, ty, 0.62, th, "Hardware context", fs=FS - 0.5)
    _box(ax, 1.26, ty, 0.30, th, "CP")
    _arrow(ax, (0.40, ty + th / 2), (0.52, ty + th / 2))
    _arrow(ax, (1.14, ty + th / 2), (1.26, ty + th / 2))
    kinds = "iisiiis"  # issue, issue, synchronize, ...
    cw, sx = 0.085, 1.66
    for k, kind in enumerate(kinds):
        ax.add_patch(Rectangle((sx + k * cw, ty + 0.02), cw, th - 0.04, facecolor=INK if kind == "i" else MIST,
                               edgecolor="white", linewidth=0.6, zorder=3))
    ax.add_patch(Rectangle((sx, ty + 0.02), len(kinds) * cw, th - 0.04, fill=False, edgecolor=INK, linewidth=0.4,
                           zorder=4))
    _arrow(ax, (1.56, ty + th / 2), (sx, ty + th / 2))
    lx = sx + len(kinds) * cw + 0.08
    for y, fc, label in ((ty + 0.145, INK, "issue, returns"), (ty + 0.055, MIST, "synchronization, blocks")):
        ax.add_patch(Rectangle((lx, y - 0.03), 0.06, 0.06, facecolor=fc, edgecolor=INK, linewidth=0.4, zorder=3))
        ax.text(lx + 0.09, y, label, ha="left", va="center_baseline", fontsize=FS)
    # ---- the array: 8 columns of a shim tile, a memory tile and 4 compute tiles, over DRAM
    t, g, x0, y0 = 0.125, 0.03, 0.50, 0.40
    xs = [x0 + c * (t + g) for c in range(8)]
    ys = [y0 + r * (t + g) for r in range(6)]
    fills = [GRAY, MIST] + ["white"] * 4
    for c, x in enumerate(xs):
        group = ATTN_PASTEL if c in (0, 7) else GEMM_PASTEL
        for r, y in enumerate(ys):
            _box(ax, x, y, t, t, fc=fills[r] if r < 2 else group, lw=0.4)
    # the default split's column groups, labelled above the array
    gy = ys[5] + t + 0.045
    for c in (0, 7):
        ax.text(xs[c] + t / 2, gy, "Attn.", ha="center", va="center_baseline", fontsize=FS - 0.5)
    ax.text((xs[1] + xs[6] + t) / 2, gy, "GEMMs", ha="center", va="center_baseline", fontsize=FS - 0.5)
    ax.plot([xs[1], xs[6] + t], [gy - 0.035, gy - 0.035], color=INK, lw=0.4, zorder=3)
    for r, label in ((0, "Shim"), (1, "Memory")):
        ax.text(x0 - 0.05, ys[r] + t / 2, label, ha="right", va="center_baseline", fontsize=FS)
    ax.text(x0 - 0.05, (ys[2] + ys[5] + t) / 2, "Compute", ha="right", va="center_baseline", fontsize=FS)
    dram_y, dram_h = 0.03, 0.2
    _box(ax, x0, dram_y, W - x0 - 0.01, dram_h, "DRAM, shared with the host", fc=MIST)
    for x in xs:
        ax.add_patch(FancyArrowPatch((x + t / 2, y0), (x + t / 2, dram_y + dram_h),
                                     arrowstyle="<|-|>,head_length=1.8,head_width=1.0", color=INK, linewidth=0.4,
                                     shrinkA=0, shrinkB=0))
    # an issue pushes a BD into a shim tile's DMA queue: from the stream's second issue down beside the array
    vx = xs[-1] + t + 0.085
    ix = sx + 1.5 * cw
    ax.plot([ix, ix, vx], [ty + 0.02, 1.46, 1.46], color=INK, lw=0.6, solid_joinstyle="miter", zorder=9)
    ax.plot([vx, vx], [1.46, ys[0] + t / 2], color=INK, lw=0.6, zorder=9)
    _arrow(ax, (vx, ys[0] + t / 2), (xs[-1] + t, ys[0] + t / 2))
    ax.text(ix + 0.05, 1.50, "issue: push a BD to a shim DMA queue", ha="left", va="center_baseline", fontsize=FS)
    # ---- magnified: one compute tile (column 7, row 4) and one shim tile, with connectors from the grid
    cx0, cx1 = vx + 0.10, W - 0.01
    panels = (("Compute tile", ys[4], 0.78, 1.36), ("Shim tile", ys[0], 0.30, 0.66))
    for name, ty0, py0, py1 in panels:
        _box(ax, cx0, py0, cx1 - cx0, py1 - py0, fc="white", lw=0.5, z=4)
        ax.text(cx0 + 0.05, py1 - 0.07, name, ha="left", va="center_baseline", fontsize=FS, zorder=6,
                fontweight="bold")
        for yy, py in ((ty0 + t, py1), (ty0, py0)):
            ax.plot([xs[-1] + t, cx0], [yy, py], color=STONE, lw=0.35, linestyle=(0, (1, 1.2)), zorder=1)
    # compute tile: core, local-memory buffers with their locks, and a DMA following a BD chain
    px = cx0 + 0.06
    _box(ax, px, 1.02, 0.30, 0.16, "Core", z=5)
    bx = px + 0.44
    for k in range(3):
        _box(ax, bx + k * 0.15, 1.10, 0.11, 0.10, fc=MIST, lw=0.4, z=5)
        ax.add_patch(Rectangle((bx + k * 0.15 + 0.035, 1.025), 0.04, 0.04, facecolor=INK, edgecolor=INK, lw=0.4,
                               zorder=6))
    ax.text(bx + 3 * 0.15, 1.045, "locks", ha="left", va="center_baseline", fontsize=FS, zorder=6)
    _arrow(ax, (px + 0.30, 1.15), (bx, 1.15), lw=0.4)
    ax.text(bx + 3 * 0.15, 1.15, "buffers", ha="left", va="center_baseline", fontsize=FS, zorder=6)
    _box(ax, px, 0.83, 0.30, 0.13, "DMA", z=5)
    for k in range(3):
        _box(ax, bx + k * 0.15, 0.855, 0.11, 0.08, fc=GRAY, lw=0.4, z=5)
        if k:
            _arrow(ax, (bx + (k - 1) * 0.15 + 0.11, 0.895), (bx + k * 0.15, 0.895), lw=0.4)
    ax.text(bx + 3 * 0.15, 0.895, "BD chain", ha="left", va="center_baseline", fontsize=FS, zorder=6)
    _arrow(ax, (px + 0.30, 0.895), (bx, 0.895), lw=0.4)
    # shim tile: a DMA working through its queue of pushed BDs, to and from DRAM
    _box(ax, px, 0.36, 0.30, 0.13, "DMA", z=5)
    for k in range(3):
        _box(ax, bx + k * 0.12, 0.385, 0.09, 0.08, fc=GRAY, lw=0.4, z=5)
    ax.text(bx + 3 * 0.12 + 0.01, 0.425, "BD queue", ha="left", va="center_baseline", fontsize=FS, zorder=6)
    _arrow(ax, (bx, 0.425), (px + 0.30, 0.425), lw=0.4)
    fig.savefig(OUT / "arch.pdf", metadata={"CreationDate": None})
    plt.close(fig)


MAGENTA = "#D04A8A"  # ours, as in the data figures


def _strip(ax, x, y, kinds, cw=0.075, h=0.10, z=5):
    """An instruction stream: issues dark, synchronizations light, left to right in execution order."""
    for k, kind in enumerate(kinds):
        ax.add_patch(Rectangle((x + k * cw, y), cw, h, facecolor=INK if kind == "i" else MIST, edgecolor="white",
                               linewidth=0.5, zorder=z))
    ax.add_patch(Rectangle((x, y), len(kinds) * cw, h, fill=False, edgecolor=INK, linewidth=0.4, zorder=z + 1))
    return x + len(kinds) * cw


def _stage(ax, x, y, w, h, title, ours=True):
    ax.add_patch(Rectangle((x, y), w, h, facecolor="#FBF1F6" if ours else "white", edgecolor=MAGENTA if ours else INK,
                           linewidth=0.7 if ours else 0.5, zorder=1))
    ax.text(x + w / 2, y + h - 0.075, title, ha="center", va="center_baseline", fontsize=FS, zorder=6)


def fig_framework():
    """OPCORD's components over a design its stack has already compiled, full width:
    the analysis reads the design and the host program into a dependence graph whose edges are true, name or order
    dependences, with legality conditions and a bound per false order; the composer and the stream pass reorder issue
    and the loop pass renames buffers into rings, each behind its checker; the event model prices each candidate order
    and split per prompt length from the probes, for prefill; the runtime package runs the result on the design's own
    hardware context, or the checkers refuse with a reason. On closed binaries OPCORD reads and bounds, and replays only
    rewrites that leave the host program as it is."""
    W, H = _m.WIDE - 0.04, 1.48
    fig, ax = _canvas(W, H)
    fs = FS + 0.5
    top, bot = H - 0.02, 0.30  # the panels' common top and bottom; the probe rail runs beneath them
    # ---- inputs
    xi, wi = 0.02, 1.08
    _stage(ax, xi, bot, wi, top - bot, "Inputs", ours=False)
    for k, kinds in enumerate(("iisiis", "isiiis", "iiisis")):
        _strip(ax, xi + 0.08, 1.20 - k * 0.13, kinds, cw=0.048, h=0.09)
    ax.text(xi + 0.08 + 6 * 0.048 + 0.04, 1.11, "compiled design,\nopen or closed", ha="left", va="center", fontsize=fs,
            linespacing=1.1)
    rows_in = ((0.80, "host program"), (0.60, "operator probes"), (0.42, "prompt length"))
    for y, label in rows_in:
        ax.text(xi + 0.08, y, label, ha="left", va="center_baseline", fontsize=fs)
    # ---- the analysis: dependence graph, legality, bound
    xa, wa = 1.26, 1.52
    _stage(ax, xa, bot, wa, top - bot, "Analysis")
    ox, oy = xa + 0.10, 0.92
    nodes = {"a": (0.0, 0.30), "b": (0.0, 0.04), "c": (0.28, 0.28), "d": (0.28, 0.02), "e": (0.56, 0.30),
             "f": (0.56, 0.04), "g": (0.74, 0.17)}
    nodes = {k: (ox + x, oy + y) for k, (x, y) in nodes.items()}
    edges = (("a", "c", "true"), ("b", "d", "true"), ("c", "e", "true"), ("d", "f", "true"), ("e", "g", "true"),
             ("a", "d", "order"), ("c", "f", "order"), ("b", "c", "name"), ("f", "g", "name"))
    style = {"true": dict(color=INK, ls="-"), "name": dict(color=INK, ls=(0, (3, 1.5))),
             "order": dict(color=INK, ls=(0, (1, 1.2)))}  # magenta is reserved for ours
    for u, v, kind in edges:
        (x1, y1_), (x2, y2) = nodes[u], nodes[v]
        ax.plot([x1, x2], [y1_, y2], lw=0.7, zorder=3, **style[kind])
    for x, y in nodes.values():
        ax.add_patch(plt.Circle((x, y), 0.033, facecolor="white", edgecolor=INK, linewidth=0.5, zorder=4))
    for k, (kind, label) in enumerate((("true", "true"), ("name", "name"), ("order", "order"))):
        lx, ly = ox + 0.92, 1.24 - k * 0.11
        ax.plot([lx, lx + 0.09], [ly, ly], lw=0.7, zorder=3, **style[kind])
        ax.text(lx + 0.12, ly, label, ha="left", va="center_baseline", fontsize=fs - 0.5)
    for y, label in ((0.70, "dependence graph over every agent"), (0.56, "legality conditions"),
                     (0.42, "a bound per false order")):
        ax.text(xa + 0.10, y, label, ha="left", va="center_baseline", fontsize=fs)
    # ---- the rewrites, each behind its checker
    xr, wr = 2.96, 1.80
    _stage(ax, xr, bot, wr, top - bot, "Rewrites, each behind a checker")
    rew = ((1.16, "Composer", "reorder across operators"), (0.86, "Stream pass", "reorder within a stream"),
           (0.50, "Loop pass", "rename into rings"))
    for y, name, what in rew:
        _box(ax, xr + 0.08, y - 0.10, wr - 0.16, 0.20, fc="white", lw=0.4, z=3)
        ax.text(xr + 0.17, y, r"\checkmark", ha="center", va="center_baseline", fontsize=fs + 1, color=MAGENTA,
                zorder=5)
        ax.text(xr + 0.26, y, name, ha="left", va="center_baseline", fontsize=fs, fontweight="bold", zorder=5)
        ax.text(xr + 0.82, y, what, ha="left", va="center_baseline", fontsize=fs, zorder=5)
    # ---- the event model, prefill only
    xe, we, be = 4.94, 0.88, 0.57
    _stage(ax, xe, be, we, top - be, "Event model")
    for lane, bars in ((1.17, ((xe + 0.08, 0.20), (xe + 0.32, 0.28))), (1.02, ((xe + 0.08, 0.36), (xe + 0.48, 0.16)))):
        for x0, w in bars:
            ax.add_patch(Rectangle((x0, lane), w, 0.09, facecolor=GRAY, edgecolor="white", linewidth=0.5, zorder=3))
    for k, label in enumerate(("order and", "configuration", "per prompt length")):
        ax.text(xe + 0.08, 0.91 - k * 0.12, label, ha="left", va="center_baseline", fontsize=fs)
    # ---- output
    xo = 5.98
    wo = W - xo
    _stage(ax, xo, bot, wo, top - bot, "Output", ours=False)
    _strip(ax, xo + 0.07, 1.16, "iiiss", cw=0.075, h=0.09)
    for k, label in enumerate(("rewritten design", "on its own", "hardware context,", "or a refusal", "with its reason")):
        ax.text(xo + 0.07, 0.98 - k * 0.12, label, ha="left", va="center_baseline", fontsize=fs)
    # ---- flows
    _arrow(ax, (xi + wi, 1.0), (xa, 1.0))
    _arrow(ax, (xa + wa, 1.0), (xr, 1.0))
    for y, _, _ in rew[:2]:
        _arrow(ax, (xr + wr - 0.08, y), (xe, y))
    _arrow(ax, (xe + we, 1.10), (xo, 1.10))
    _arrow(ax, (xr + wr - 0.08, rew[2][0]), (xo, rew[2][0]))  # decode: the loop pass's rings go straight to the output
    # the probes and the prompt length feed the event model along a rail beneath the panels
    ry, rx = 0.15, xe + we / 2
    ax.plot([xi + wi / 2, xi + wi / 2, rx], [bot, ry, ry], color=INK, lw=0.6, solid_joinstyle="miter", zorder=2)
    _arrow(ax, (rx, ry), (rx, be))
    ax.text(xa + 0.10, ry + 0.06, "probes, prompt length", ha="left", va="center_baseline", fontsize=fs - 0.5)
    fig.savefig(OUT / "framework.pdf", metadata={"CreationDate": None})
    plt.close(fig)


def fig_rewrites():
    """What the loop pass does to decode attention's block loop, in fig_order's vocabulary, with illustrative durations:
    with one buffer per role, block i+1's transfer waits until block i's compute releases the buffer; with a two-slot
    ring, block i+1's transfer fills the other slot while block i computes. A dotted arrow marks each such wait, a false
    order. Attention's transfers are drawn in the pastel step of its compute's ORANGE, as in the architecture figure."""
    T, C, NB = 1.0, 0.71, 3  # a block's transfer and compute (compute is 0.71 of the transfer, as measured in decode), blocks
    loop = {
        "ex": dict(tr=[(k * (T + C), T) for k in range(NB)], co=[(k * (T + C) + T, C) for k in range(NB)],
                   end=NB * (T + C)),
        "rw": dict(tr=[(k * T, T) for k in range(NB)], co=[((k + 1) * T, C) for k in range(NB)], end=NB * T + C),
    }
    fig, axes = plt.subplots(1, 2, figsize=(COLUMN, 0.98), sharex=True, sharey=True, gridspec_kw=dict(wspace=0.06))

    def wait(ax, x, y0, y1):  # a dotted shaft with a solid head, vertical from y0 to y1
        ax.plot([x, x], [y0, y1], color=INK, linewidth=0.6, linestyle=(0, (1, 1.2)), zorder=10)
        ax.add_patch(FancyArrowPatch((x, y1 + 0.02 * (y0 - y1)), (x, y1), arrowstyle="-|>,head_length=2.2,head_width=1.2",
                                     color=INK, linewidth=0.6, shrinkA=0, shrinkB=0, zorder=10))
    labels = (r"$i$", r"$i{+}1$", r"$i{+}2$")
    for col, (key, title) in enumerate((("ex", "One buffer per role"), ("rw", "Loop pass, two-slot ring"))):
        ax, d = axes[col], loop[key]
        for k, (t0, w) in enumerate(d["tr"]):
            ax.broken_barh([(t0, w)], (1.0 - 0.32, 0.64), facecolors=ATTN_PASTEL, edgecolor=INK, linewidth=0.4)
            ax.text(t0 + w / 2, 1.0, labels[k], ha="center", va="center_baseline", fontsize=FS)
            if key == "rw":
                ax.text(t0 + w / 2, 1.0 + 0.52, f"slot {k % 2}", ha="center", va="center_baseline", fontsize=FS - 0.5)
        for k, (t0, w) in enumerate(d["co"]):
            ax.broken_barh([(t0, w)], (-0.32, 0.64), facecolors=ORANGE, edgecolor=INK, linewidth=0.4)
            ax.text(t0 + w / 2, 0.0, labels[k], ha="center", va="center_baseline", fontsize=FS)
            if key == "ex" and k + 1 < NB:  # block k's compute releases the buffer block k+1's transfer fills
                wait(ax, t0 + w, 0.32, 1.0 - 0.32)
        ax.set_yticks([1.0, 0.0], ("Transfer", "Compute"))
        ax.set_ylim(-0.6, 1.75)
        ax.axvline(d["end"] + 0.06, color="black", linewidth=0.5, linestyle=(0, (4, 2)))  # clear of the last box
        ax.set_xlim(-0.1, max(v["end"] for v in loop.values()) + 0.25)
        ax.set_title(title, fontsize=7, pad=2, loc="left")
        ax.tick_params(left=False, right=False, top=False, bottom=False, labelleft=col == 0)
        ax.set_xticks([])
        for side in ("top", "right", "bottom"):
            ax.spines[side].set_visible(False)
    handles = [plt.Line2D([], [], color=INK, linewidth=0.6, linestyle=(0, (1, 1.2)))]
    fig.legend(handles, ["false order"], loc="lower right", bbox_to_anchor=(0.99, -0.13), handlelength=1.2)
    fig.supxlabel("Time (illustrative)", fontsize=8, y=-0.06)
    fig.savefig(OUT / "rewrites.pdf", metadata={"CreationDate": None})
    plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fig_arch()
    fig_framework()
    fig_rewrites()
