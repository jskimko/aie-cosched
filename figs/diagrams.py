#!/usr/bin/env python3
"""The paper's schematic figures (not data plots), drawn as line art in make_figs.py's style.

  FIGS_OUT=paper/fig .venv/bin/python figs/diagrams.py

Outputs:
  framework.pdf  OPCORD's pipeline over a compiled design: graph, prices, checked rewrites, output
  arch.pdf  the XDNA 2 NPU as the paper uses it: host, hardware context, the CP's in-order instruction stream, the
            array of shim, memory and compute tiles over DRAM, and one compute tile and one shim tile magnified
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_figs as _m  # noqa: E402  (style, palette, OUT)
from make_figs import COLUMN, GRAY, INK, OUT, plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, Rectangle  # noqa: E402

MIST, STONE = "#E4E4E4", "#707070"
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
    switch along a chain of BDs, and locks hand each buffer between its producer and its consumer."""
    W, H = COLUMN - 0.04, 1.86
    fig, ax = _canvas(W, H)
    # ---- the submission path along the top: host -> hardware context -> CP -> its instruction stream
    ty, th = 1.62, 0.2
    _box(ax, 0.02, ty, 0.38, th, "Host", fc=MIST)
    _box(ax, 0.52, ty, 0.62, th, "HW context")
    _box(ax, 1.26, ty, 0.30, th, "CP")
    _arrow(ax, (0.40, ty + th / 2), (0.52, ty + th / 2))
    _arrow(ax, (1.14, ty + th / 2), (1.26, ty + th / 2))
    kinds = "iisiiis"  # issue, issue, synchronize, ...
    cw, sx = 0.1, 1.66
    for k, kind in enumerate(kinds):
        ax.add_patch(Rectangle((sx + k * cw, ty + 0.02), cw, th - 0.04, facecolor=INK if kind == "i" else MIST,
                               edgecolor="white", linewidth=0.6, zorder=3))
    ax.add_patch(Rectangle((sx, ty + 0.02), len(kinds) * cw, th - 0.04, fill=False, edgecolor=INK, linewidth=0.4,
                           zorder=4))
    _arrow(ax, (1.56, ty + th / 2), (sx, ty + th / 2))
    lx = sx + len(kinds) * cw + 0.08
    for y, fc, label in ((ty + 0.145, INK, "issue, returns"), (ty + 0.055, MIST, "synchronize, blocks")):
        ax.add_patch(Rectangle((lx, y - 0.03), 0.06, 0.06, facecolor=fc, edgecolor=INK, linewidth=0.4, zorder=3))
        ax.text(lx + 0.09, y, label, ha="left", va="center_baseline", fontsize=FS)
    # ---- the array: 8 columns of a shim tile, a memory tile and 4 compute tiles, over DRAM
    t, g, x0, y0 = 0.125, 0.03, 0.50, 0.40
    xs = [x0 + c * (t + g) for c in range(8)]
    ys = [y0 + r * (t + g) for r in range(6)]
    fills = [GRAY, MIST] + ["white"] * 4
    for x in xs:
        for r, y in enumerate(ys):
            _box(ax, x, y, t, t, fc=fills[r], lw=0.4)
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
    """OPCORD as a pipeline over a design its stack has already compiled: read its instruction streams into a dependence
    graph whose edges are true, name or order dependences; price candidate schedules from per-operator probes; reorder
    issue and rename buffers, each rewrite admitted only by a legality check; emit the rewritten design or refuse."""
    W, H = COLUMN - 0.04, 1.62
    fig, ax = _canvas(W, H)
    # ---- row 1: compiled design -> dependence graph -> event model
    y1, h1 = 0.88, 0.70
    _stage(ax, 0.02, y1, 0.86, h1, "Compiled design", ours=False)
    for k, kinds in enumerate(("iisiis", "isiiis", "iiisis")):
        _strip(ax, 0.10, y1 + 0.42 - k * 0.14, kinds)
    _stage(ax, 1.08, y1, 1.0, h1, "Dependence graph")
    nodes = {"a": (1.22, 1.32), "b": (1.22, 1.06), "c": (1.50, 1.30), "d": (1.50, 1.04), "e": (1.78, 1.32),
             "f": (1.78, 1.06), "g": (1.96, 1.19)}
    edges = (("a", "c", "true"), ("b", "d", "true"), ("c", "e", "true"), ("d", "f", "true"), ("e", "g", "true"),
             ("a", "d", "order"), ("c", "f", "order"), ("b", "c", "name"), ("f", "g", "name"))
    style = {"true": dict(color=INK, ls="-"), "name": dict(color=MAGENTA, ls=(0, (3, 1.5))),
             "order": dict(color=MAGENTA, ls=(0, (1, 1.2)))}
    for u, v, kind in edges:
        (x1, y1_), (x2, y2) = nodes[u], nodes[v]
        ax.plot([x1, x2], [y1_, y2], lw=0.7, zorder=3, **style[kind])
    for x, y in nodes.values():
        ax.add_patch(plt.Circle((x, y), 0.033, facecolor="white", edgecolor=INK, linewidth=0.5, zorder=4))
    _stage(ax, 2.28, y1, W - 2.30, h1, "Event model")
    # two lanes of operators, the bound as a dashed line; the probes come from each operator alone
    for lane, bars in ((1.30, ((2.36, 0.22), (2.62, 0.30))), (1.12, ((2.36, 0.40), (2.80, 0.18)))):
        for x0, w in bars:
            ax.add_patch(Rectangle((x0, lane), w, 0.10, facecolor=GRAY, edgecolor="white", linewidth=0.5, zorder=3))
    ax.plot([3.02, 3.02], [1.06, 1.46], color=INK, lw=0.6, linestyle=(0, (2, 1.2)), zorder=4)
    ax.text(3.0, 0.98, "bound", ha="right", va="center_baseline", fontsize=FS - 0.5)
    _arrow(ax, (0.88, y1 + h1 / 2), (1.08, y1 + h1 / 2))
    _arrow(ax, (2.08, y1 + h1 / 2), (2.28, y1 + h1 / 2))
    # ---- row 2: the two rewrites, each behind a legality check, and what comes out
    y2, h2 = 0.04, 0.70
    _stage(ax, 0.02, y2, 2.06, h2, "Rewrite, each checked for legality")
    # reorder issue: issue every group's work before any synchronization
    xa = _strip(ax, 0.10, y2 + 0.38, "isis", cw=0.09)
    _arrow(ax, (xa + 0.04, y2 + 0.43), (xa + 0.24, y2 + 0.43), lw=0.5)
    ax.text(xa + 0.14, y2 + 0.50, r"\checkmark", ha="center", va="center_baseline", fontsize=FS + 1, color=MAGENTA)
    _strip(ax, xa + 0.28, y2 + 0.38, "iiss", cw=0.09)
    ax.text(0.10, y2 + 0.27, "reorder issue", ha="left", va="center_baseline", fontsize=FS)
    # rename: one buffer per role becomes a ring of two
    bx = 1.24
    _box(ax, bx, y2 + 0.36, 0.14, 0.14, fc=MIST, lw=0.5, z=4)
    _arrow(ax, (bx + 0.18, y2 + 0.43), (bx + 0.38, y2 + 0.43), lw=0.5)
    ax.text(bx + 0.28, y2 + 0.50, r"\checkmark", ha="center", va="center_baseline", fontsize=FS + 1, color=MAGENTA)
    _box(ax, bx + 0.42, y2 + 0.36, 0.14, 0.14, fc=MIST, lw=0.5, z=4)
    _box(ax, bx + 0.58, y2 + 0.36, 0.14, 0.14, fc=MIST, lw=0.5, z=4)
    ax.add_patch(FancyArrowPatch((bx + 0.70, y2 + 0.52), (bx + 0.44, y2 + 0.52), connectionstyle="arc3,rad=0.5",
                                 arrowstyle="-|>,head_length=1.8,head_width=1.0", color=INK, linewidth=0.5, zorder=5))
    ax.text(bx, y2 + 0.27, "rename into a ring", ha="left", va="center_baseline", fontsize=FS)
    _stage(ax, 2.28, y2, W - 2.30, h2, "Output", ours=False)
    _strip(ax, 2.36, y2 + 0.40, "iiiss", cw=0.075)
    ax.text(2.36, y2 + 0.28, "rewritten design", ha="left", va="center_baseline", fontsize=FS)
    ax.text(2.36, y2 + 0.16, "or a refusal", ha="left", va="center_baseline", fontsize=FS)
    ax.text(2.36, y2 + 0.07, "with its reason", ha="left", va="center_baseline", fontsize=FS)
    _arrow(ax, (2.08, y2 + h2 / 2), (2.28, y2 + h2 / 2))
    # the graph and the model drive the rewrites
    _arrow(ax, (1.58, y1), (1.58, y2 + h2))
    ax.plot([2.65, 2.65, 1.95], [y1, y1 - 0.07, y1 - 0.07], color=INK, lw=0.6, zorder=2)
    _arrow(ax, (1.95, y1 - 0.07), (1.95, y2 + h2))
    # legend for the graph's edges
    lg_y = y1 + 0.08
    for k, (kind, label) in enumerate((("true", "true"), ("name", "name"), ("order", "order"))):
        x = 1.12 + k * 0.30
        ax.plot([x, x + 0.09], [lg_y, lg_y], lw=0.7, zorder=3, **style[kind])
        ax.text(x + 0.11, lg_y, label, ha="left", va="center_baseline", fontsize=FS - 0.5)
    fig.savefig(OUT / "framework.pdf", metadata={"CreationDate": None})
    plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fig_arch()
    fig_framework()
