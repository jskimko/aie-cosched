#!/usr/bin/env python3
"""The paper's schematic figures (not data plots), drawn as line art in make_figs.py's style.

  FIGS_OUT=paper/fig .venv/bin/python figs/diagrams.py

Outputs:
  framework.pdf  OPCORD's components over a compiled design, full width: inputs, analysis, checked rewrites, event
                 model, output
  arch.pdf  the XDNA 2 NPU as the paper uses it: host, hardware context, the CP's in-order instruction stream, the
            array of shim, memory and compute tiles over DRAM, and one compute tile and one shim tile magnified
  rewrites.pdf  OPCORD's three rewrites (composer, stream pass, loop pass), each before and after, full width
  intro.pdf  Figure 1, full width: (a) the NPU, the in-order CP feeding every column; (b) the CP's issue order in one
             layer of AIR's prefill, original against OPCORD; (c) the measured timeline (data/fig1-intervals-1b.json)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_figs as _m  # noqa: E402  (style, palette, OUT)
from make_figs import (ATTN, ATTN_FILL, COLUMN, FS_LABEL, FS_NOTE, FS_TICK, GEMM, GEMM_FILL, GRAY, INK, OURS,  # noqa: E402
                       OURS_TINT, OUT, plt, save)
import numpy as np  # noqa: E402
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle, Wedge  # noqa: E402

MIST, STONE = "#E4E4E4", "#707070"
# the fill steps of attention and the GEMMs, for the column groups of the default configuration
ATTN_PASTEL, GEMM_PASTEL = ATTN_FILL, GEMM_FILL
FS, FS_TITLE = FS_NOTE, FS_TICK  # the diagrams (Figures 2 and 4) take the type scale one step down


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
    """The host submits dispatches to a hardware context, whose CP executes each dispatch's instruction stream in
    order: an issue pushes a BD into a shim DMA's task queue and returns at once, a synchronization blocks the CP until
    a transfer completes. The array runs data-driven: each compute tile's DMA follows a chain of BDs, and locks hand
    each buffer between its producer and its consumer. The compute tiles are tinted by the column group that the
    original prefill's default configuration gives them: attention on columns 0 and 7, the GEMMs on columns 1-6. One
    compute tile and the shim tile of column 7 are drawn larger at the right."""
    W, H = COLUMN - 0.04, 1.88
    fig, ax = _canvas(W, H)
    # ---- the submission path along the top: host -> hardware context -> CP -> its instruction stream
    ty, th = 1.64, 0.2
    _box(ax, 0.02, ty, 0.34, th, "Host", fc=MIST)
    _box(ax, 0.48, ty, 0.66, th, "Hardware context")
    _box(ax, 1.26, ty, 0.30, th, "CP")
    _arrow(ax, (0.36, ty + th / 2), (0.48, ty + th / 2))
    _arrow(ax, (1.14, ty + th / 2), (1.26, ty + th / 2))
    kinds = "iisiiis"  # issue, issue, synchronize, ...
    cw, sx = 0.085, 1.66
    for k, kind in enumerate(kinds):  # contiguous equal cells; a mid-gray rule between every pair, on dark and light alike
        ax.add_patch(Rectangle((sx + k * cw, ty + 0.02), cw, th - 0.04, facecolor=INK if kind == "i" else MIST,
                               edgecolor="none", zorder=3))
    for k in range(1, len(kinds)):
        ax.plot([sx + k * cw] * 2, [ty + 0.02, ty + th - 0.02], color=STONE, lw=0.5, zorder=4)
    ax.add_patch(Rectangle((sx, ty + 0.02), len(kinds) * cw, th - 0.04, fill=False, edgecolor=INK, linewidth=0.4,
                           zorder=5))
    _arrow(ax, (1.56, ty + th / 2), (sx, ty + th / 2))
    lx = sx + len(kinds) * cw + 0.08
    for y, fc, label in ((ty + 0.145, INK, "Issue, returns"), (ty + 0.055, MIST, "Synchronization, blocks")):
        ax.add_patch(Rectangle((lx, y - 0.03), 0.06, 0.06, facecolor=fc, edgecolor=INK, linewidth=0.3, zorder=3))
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
    # the default configuration's column groups, labelled above the array, the GEMMs' span clear of the tiles
    top = ys[5] + t
    gy = top + 0.085
    for c in (0, 7):
        ax.text(xs[c] + t / 2, gy, "Attn.", ha="center", va="center_baseline", fontsize=FS)
    ax.text((xs[1] + xs[6] + t) / 2, gy, "GEMMs", ha="center", va="center_baseline", fontsize=FS)
    by = top + 0.03
    ax.plot([xs[1], xs[1], xs[6] + t, xs[6] + t], [by - 0.012, by, by, by - 0.012], color=INK, lw=0.4, zorder=3,
            solid_joinstyle="miter")
    for r, label in ((0, "Shim"), (1, "Memory")):
        ax.text(x0 - 0.05, ys[r] + t / 2, label, ha="right", va="center_baseline", fontsize=FS)
    ax.text(x0 - 0.05, (ys[2] + ys[5] + t) / 2, "Compute", ha="right", va="center_baseline", fontsize=FS)
    dram_y, dram_h = 0.03, 0.2
    _box(ax, x0, dram_y, W - x0 - 0.01, dram_h, "DRAM, shared with the host", fc=MIST)
    for x in xs:
        ax.add_patch(FancyArrowPatch((x + t / 2, y0), (x + t / 2, dram_y + dram_h),
                                     arrowstyle="<|-|>,head_length=1.8,head_width=1.0", color=INK, linewidth=0.4,
                                     shrinkA=0, shrinkB=0))
    # an issue pushes a BD into a shim DMA's task queue: from the stream's second issue down beside the array
    ix = sx + 1.5 * cw  # the stream's second issue, which lies clear of the array's right edge
    vx = ix
    ax.plot([vx, vx, xs[-1] + t + 0.03], [ty + 0.02, ys[0] + t / 2, ys[0] + t / 2], color=INK, lw=0.6,
            solid_capstyle="butt", solid_joinstyle="miter", zorder=9)  # one path, so the corner is mitred
    _arrow(ax, (xs[-1] + t + 0.04, ys[0] + t / 2), (xs[-1] + t, ys[0] + t / 2))
    ax.text(ix + 0.05, 1.52, "Issue: push a BD to a shim task queue", ha="left", va="center_baseline",
            fontsize=FS)
    # ---- the two outlined tiles of column 7, drawn larger
    cx0, cx1 = vx + 0.10, W - 0.01
    panels = (("Compute tile", ys[4], 0.78, 1.38), ("Shim tile", ys[0], 0.30, 0.66))
    for name, ty0, py0, py1 in panels:
        _box(ax, cx0, py0, cx1 - cx0, py1 - py0, fc="white", lw=0.5, z=4)
        ax.text(cx0 + 0.05, py1 - 0.07, name, ha="left", va="center_baseline", fontsize=FS_TITLE, zorder=6,
                fontweight="bold")
        for yy, py in ((ty0 + t, py1), (ty0, py0)):  # zoom lines from the tile's corners to the panel's
            ax.plot([xs[-1] + t, cx0], [yy, py], color=STONE, lw=0.35, linestyle=(0, (1, 1.2)), zorder=1)
    px, bx = cx0 + 0.06, cx0 + 0.50
    # compute tile: the core reads and writes buffers in local memory, each guarded by a lock
    _box(ax, px, 1.04, 0.30, 0.16, "Core", z=5)
    for k in range(3):
        _box(ax, bx + k * 0.15, 1.10, 0.11, 0.10, fc=MIST, lw=0.4, z=5)
        ax.add_patch(Rectangle((bx + k * 0.15 + 0.035, 1.025), 0.04, 0.04, facecolor=INK, edgecolor=INK, lw=0.4,
                               zorder=6))
    ax.add_patch(FancyArrowPatch((px + 0.30, 1.15), (bx, 1.15), arrowstyle="<|-|>,head_length=1.6,head_width=0.9",
                                 color=INK, linewidth=0.4, shrinkA=0, shrinkB=0, zorder=6))
    ax.text(bx + 3 * 0.15, 1.15, "Buffers", ha="left", va="center_baseline", fontsize=FS, zorder=6)
    ax.text(bx + 3 * 0.15, 1.045, "Locks", ha="left", va="center_baseline", fontsize=FS, zorder=6)
    # compute tile: the DMA's BDs form a chain, each naming the next; the chain is configuration, not a runtime exchange
    _box(ax, px, 0.83, 0.30, 0.13, "DMA", z=5)
    for k in range(3):
        _box(ax, bx + k * 0.15, 0.855, 0.09, 0.08, fc=GRAY, lw=0.4, z=5)
        if k:
            _arrow(ax, (bx + (k - 1) * 0.15 + 0.09, 0.895), (bx + k * 0.15, 0.895), lw=0.4)
    ax.text(bx + 3 * 0.15, 0.895, "BD chain", ha="left", va="center_baseline", fontsize=FS, zorder=6)
    # shim tile: pushed BDs wait in the DMA's task queue, which feeds the DMA
    _box(ax, px, 0.36, 0.30, 0.13, "DMA", z=5)
    for k in range(3):
        _box(ax, bx + k * 0.11, 0.385, 0.09, 0.08, fc=GRAY, lw=0.4, z=5)
    _arrow(ax, (bx, 0.425), (px + 0.30, 0.425), lw=0.4)
    ax.text(bx + 3 * 0.11 + 0.02, 0.425, "Task queue", ha="left", va="center_baseline", fontsize=FS, zorder=6)
    fig.savefig(OUT / "arch.pdf", metadata={"CreationDate": None})
    plt.close(fig)


MAGENTA = OURS  # ours, as in the data figures


def _strip(ax, x, y, kinds, cw=0.075, h=0.10, z=5):
    """An instruction stream, drawn as in the architecture figure: one framed block of contiguous equal cells, issues
    dark and synchronizations light, left to right in execution order, a mid-gray rule between every pair."""
    for k, kind in enumerate(kinds):
        ax.add_patch(Rectangle((x + k * cw, y), cw, h, facecolor=INK if kind == "i" else MIST, edgecolor="none",
                               zorder=z))
    for k in range(1, len(kinds)):
        ax.plot([x + k * cw] * 2, [y, y + h], color=STONE, lw=0.5, zorder=z + 1)
    ax.add_patch(Rectangle((x, y), len(kinds) * cw, h, fill=False, edgecolor=INK, linewidth=0.4, zorder=z + 2))
    return x + len(kinds) * cw


def _stage(ax, x, y, w, h, title, ours=True):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=OURS_TINT if ours else "white", edgecolor=MAGENTA if ours else INK,
                           linewidth=0.7 if ours else 0.5, zorder=1))
    ax.text(x + w / 2, y + h - 0.075, title, ha="center", va="center_baseline", fontsize=FS_TITLE, zorder=6)


def _doc(ax, x, y, w=0.1125, h=0.15, z=5):
    """A program: a page with a folded corner and three text lines; (x, y) is its lower left. The fold and the lines
    scale with the page (drawn first at 0.12 by 0.16)."""
    s = h / 0.16
    f = 0.04 * s
    ax.add_patch(Polygon([(x, y), (x + w, y), (x + w, y + h - f), (x + w - f, y + h), (x, y + h)], closed=True,
                         facecolor="white", edgecolor=INK, linewidth=0.45, joinstyle="miter", zorder=z))
    ax.plot([x + w - f, x + w - f, x + w], [y + h, y + h - f, y + h - f], color=INK, lw=0.45, zorder=z + 1)
    for k in range(3):
        ly = y + h - (0.065 + k * 0.035) * s
        ax.plot([x + 0.025 * s, x + w - (0.025 if k else 0.05) * s], [ly, ly], color=INK, lw=0.4, zorder=z + 1)


def _bars(ax, x, y, z=5):
    """Operator probes: three bars of different heights on a baseline; (x, y) is the baseline's left end."""
    for k, h in enumerate((0.07, 0.12, 0.05)):
        ax.add_patch(Rectangle((x + k * 0.045, y), 0.032, h, facecolor=GRAY, edgecolor=INK, linewidth=0.35, zorder=z))
    ax.plot([x - 0.01, x + 0.14], [y, y], color=INK, lw=0.45, zorder=z + 1)


def _tokens(ax, x, y, n=5, cw=0.036, z=5):
    """A prompt: a row of token cells, at the pitch of the instruction streams; (x, y) is the row's lower left."""
    for k in range(n):
        ax.add_patch(Rectangle((x + k * cw, y), cw - 0.006, 0.048, facecolor="white", edgecolor=INK,
                               linewidth=0.35, zorder=z))


def _lanes(ax, x, y, z=5):
    """A priced schedule: two lanes of bars over time; (x, y) is the lower lane's left end."""
    for lane, bars in ((0.0, ((0.0, 0.10), (0.12, 0.14))), (0.075, ((0.0, 0.17), (0.19, 0.06)))):
        for x0, w in bars:
            ax.add_patch(Rectangle((x + x0, y + lane), w, 0.05, facecolor=GRAY, edgecolor=INK, linewidth=0.35,
                                   zorder=z))


def _cross(ax, cx, cy, r=0.045, z=5):
    """A refusal: a cross in a circle; (cx, cy) is its center."""
    ax.add_patch(plt.Circle((cx, cy), r, facecolor="white", edgecolor=INK, linewidth=0.45, zorder=z))
    d = r * 0.5
    for sgn in (1, -1):
        ax.plot([cx - d, cx + d], [cy - sgn * d, cy + sgn * d], color=INK, lw=0.6, zorder=z + 1)


def fig_framework():
    """OPCORD's components over a design its stack has already compiled, full width:
    the analysis reads the design and the host program into a dependence graph whose edges are true, name or order
    dependences, with legality conditions and a bound per false order; the composer and the stream pass reorder issue
    and the loop pass renames buffers into rings, each behind its checker; the event model prices each candidate order
    and split per prompt length from the probes, for prefill; the runtime package runs the result on the design's own
    hardware context, or the checkers refuse with a reason. On closed binaries OPCORD reads and bounds, and replays only
    rewrites that leave the host program as it is.

    Items inside a stage are told apart as the rewrites are: each item (or group) has a thin box, with its icon at
    left."""
    W, H = _m.WIDE - 0.04, 1.48
    fig, ax = _canvas(W, H)
    fs = FS
    top, bot = H - 0.02, 0.30  # the panels' common top and bottom; the probe rail runs beneath them
    # One grid for every panel: items inset `ins` from the panel's sides and `ins + 0.01` from its bottom; each item's
    # content inset `pad` from its sides. The panels' widths follow their widest content, measured as typeset, and the
    # gaps share what is left, with a 0.02 margin at either side.
    ins, pad = 0.07, 0.06
    lab = 0.029, 0.046  # a 6 pt label's TeX box above and below its anchor (va="center_baseline")
    renderer = fig._get_renderer()

    def tw(*labels):  # the widest label's typeset width, in inches
        def one(text):
            t = ax.text(0, 0, text, fontsize=fs)
            w = t.get_window_extent(renderer=renderer).width / fig.dpi
            t.remove()
            return w
        return max(one(t) for t in labels)
    ev_lines = ("Order and configuration", "per prompt length")
    out_label = "Rewritten design"
    rew = ((1.20, "Composer", "Reorder across operators"), (0.86, "Stream pass", "Reorder within a stream"),
           (0.48, "Loop pass", "Rename into rings"))
    what_x = 0.09 + tw(*(n for _, n, _ in rew)) + 0.10  # the description column, from the checkmark's center
    wi = 2 * (ins + pad) + 0.216 + 0.07 + tw("Compiled design", "Host program", "Operator probes", "Prompt length")
    wa = 2 * (ins + pad) + max(0.03 + 0.86 + 0.12 + tw("True", "Name", "Order"),
                               tw("Dependence graph", "Legality conditions", "Bound per false dependence"))
    wr = 2 * (ins + pad) + 0.04 + what_x + tw(*(w for _, _, w in rew))
    we = 2 * (ins + pad) + max(0.36, tw(*ev_lines))  # the lanes are 0.36 wide
    wo = 2 * (ins + pad) + max(5 * 0.075, tw(out_label, "Refusal"))  # the strip: five cells of 0.075
    gap = (W - 0.04 - wi - wa - wr - we - wo) / 4
    xi = 0.02
    xa = xi + wi + gap
    xr = xa + wa + gap
    xe = xr + wr + gap
    xo = xe + we + gap
    reach = (0.33 - 0.20) / 72  # an arrowhead's ink stops 0.33 pt short of its end; a 0.4 pt item edge is 0.2 pt deep

    def item(x, y0, y1, w):  # one item's (or group's) frame
        _box(ax, x, y0, w, y1 - y0, fc="white", lw=0.4, z=3)

    # ---- inputs: the design and its host program, then the probes and the prompt length (the event model's inputs)
    _stage(ax, xi, bot, wi, top - bot, "Inputs", ours=False)
    bx, bw = xi + ins, wi - 2 * ins
    ic = bx + pad + 0.108  # the icon column's center (the strips, six cells of 0.036, fill it)
    tx = bx + pad + 0.216 + 0.07  # the label column
    item(bx, 1.02, 1.30, bw)
    for k, kinds in enumerate(("iisiis", "isiiis")):
        _strip(ax, ic - 0.108, 1.1775 - k * 0.11, kinds, cw=0.036, h=0.075)
    ax.text(tx, 1.16, "Compiled design", ha="left", va="center_baseline", fontsize=fs, zorder=6)
    item(bx, 0.78, 0.98, bw)
    _doc(ax, ic - 0.1125 / 2, 0.805)
    ax.text(tx, 0.88, "Host program", ha="left", va="center_baseline", fontsize=fs, zorder=6)
    gy0 = 0.38  # the probes group's bottom, where the rail to the event model starts
    item(bx, gy0, 0.74, bw)
    py = 0.655, 0.455  # the probes' and the prompt length's lines, at the analysis rows' 0.20 pitch
    _bars(ax, ic - 0.065, py[0] - 0.06)
    _tokens(ax, ic - 0.087, py[1] - 0.024)
    for y, label in zip(py, ("Operator probes", "Prompt length")):
        ax.text(tx, y, label, ha="left", va="center_baseline", fontsize=fs, zorder=6)
    # ---- the analysis: dependence graph, legality, bound
    _stage(ax, xa, bot, wa, top - bot, "Analysis")
    ax0, aw = xa + ins, wa - 2 * ins
    item(ax0, 0.78, 1.30, aw)
    ox, oy = ax0 + pad + 0.03, 0.97
    nodes = {"a": (0.0, 0.26), "b": (0.0, 0.03), "c": (0.26, 0.25), "d": (0.26, 0.02), "e": (0.52, 0.26),
             "f": (0.52, 0.03), "g": (0.69, 0.145)}
    nodes = {k: (ox + x, oy + y) for k, (x, y) in nodes.items()}
    edges = (("a", "c", "true"), ("b", "d", "true"), ("c", "e", "true"), ("d", "f", "true"), ("e", "g", "true"),
             ("a", "d", "order"), ("c", "f", "order"), ("b", "c", "name"), ("f", "g", "name"))
    style = {"true": dict(color=INK, ls="-"), "name": dict(color=INK, ls=(0, (3, 1.5))),
             "order": dict(color=INK, ls=(0, (1, 1.2)))}  # magenta is reserved for ours
    for u, v, kind in edges:
        (x1, y1_), (x2, y2) = nodes[u], nodes[v]
        ax.plot([x1, x2], [y1_, y2], lw=0.7, zorder=4, **style[kind])
    for x, y in nodes.values():
        ax.add_patch(plt.Circle((x, y), 0.03, facecolor="white", edgecolor=INK, linewidth=0.5, zorder=5))
    for k, (kind, label) in enumerate((("true", "True"), ("name", "Name"), ("order", "Order"))):
        lx, ly = ox + 0.86, 1.23 - k * 0.11
        ax.plot([lx, lx + 0.09], [ly, ly], lw=0.7, zorder=4, **style[kind])
        ax.text(lx + 0.12, ly, label, ha="left", va="center_baseline", fontsize=fs, zorder=6)
    ax.text(ox - 0.03, 0.87, "Dependence graph", ha="left", va="center_baseline", fontsize=fs, zorder=6)
    rows_a = ((0.66, "Legality conditions"), (0.46, "Bound per false dependence"))
    for y, label in rows_a:
        item(ax0, y - 0.08, y + 0.08, aw)
        ax.text(ox - 0.03, y, label, ha="left", va="center_baseline", fontsize=fs, zorder=6)
    # ---- the rewrites, each behind its checker; rows on the other panels' top and bottom, the loop pass set apart
    _stage(ax, xr, bot, wr, top - bot, "Checked rewrites")
    rx0, rw = xr + ins, wr - 2 * ins
    ck = rx0 + pad + 0.04  # the checkmark's center (its TeX box is 0.08 wide)
    for y, name, what in rew:
        _box(ax, rx0, y - 0.10, rw, 0.20, fc="white", lw=0.4, z=3)
        ax.text(ck, y, r"\checkmark", ha="center", va="center_baseline", fontsize=FS_TITLE, color=MAGENTA, zorder=5)
        ax.text(ck + 0.09, y, name, ha="left", va="center_baseline", fontsize=fs, fontweight="bold", zorder=5)
        ax.text(ck + what_x, y, what, ha="left", va="center_baseline", fontsize=fs, zorder=5)
    # ---- the event model, prefill only: one item, a priced schedule over its label, centered in the item
    be = 0.57
    _stage(ax, xe, be, we, top - be, "Event model")
    ey0 = be + ins + 0.01
    item(xe + ins, ey0, 1.30, we - 2 * ins)
    ex = xe + ins + pad
    em = (1.30 - ey0 - (0.125 + 0.05 + 0.12 * (len(ev_lines) - 1) + sum(lab))) / 2  # lanes, a gap, lines at 0.12
    _lanes(ax, ex, 1.30 - em - 0.125)
    for k, label in enumerate(ev_lines):
        ax.text(ex, 1.30 - em - 0.175 - lab[0] - k * 0.12, label, ha="left", va="center_baseline", fontsize=fs,
                zorder=6)
    # ---- output: a refusal, or the rewritten design, which both priced prefill and decode's rings reach; each item's
    # icon above its label, the column centered on the strip, the widest content
    _stage(ax, xo, bot, wo, top - bot, "Output", ours=False)
    oi, ow = xo + ins, wo - 2 * ins
    oc = oi + pad  # the column's left
    item(oi, 1.02, 1.30, ow)
    _cross(ax, oc + 0.045, 1.16)  # the glyph and its label on one line, centered in the item
    ax.text(oc + 0.13, 1.16, "Refusal", ha="left", va="center_baseline", fontsize=fs, zorder=6)
    item(oi, 0.38, 0.96, ow)
    om = (0.58 - (0.09 + 0.05 + sum(lab))) / 2
    _strip(ax, oc, 0.96 - om - 0.09, "iiiss", cw=0.075, h=0.09)
    ax.text(oc, 0.96 - om - 0.14 - lab[0], out_label, ha="left", va="center_baseline", fontsize=fs, zorder=6)
    # ---- flows
    _arrow(ax, (xi + wi, 1.0), (xa, 1.0))
    _arrow(ax, (xa + wa, 1.0), (xr, 1.0))
    for y, _, _ in rew[:2]:
        _arrow(ax, (rx0 + rw, y), (xe, y))
    _arrow(ax, (xe + we, 0.80), (oi + reach, 0.80))
    # decode: the loop pass's rings go straight to the output, passing under the probe rail with a break, so the
    # two do not read as joined
    _arrow(ax, (rx0 + rw, rew[2][0]), (oi + reach, rew[2][0]), z=3)
    # the probes and the prompt length feed the event model along a rail beneath the panels, from their own group's
    # icon column, centered in the band below the panels and under the event model
    ry, rx = bot / 2, xe + we / 2
    ax.add_patch(Rectangle((rx - 0.04, rew[2][0] - 0.02), 0.08, 0.04, facecolor="white", edgecolor="none", zorder=4))
    ax.plot([ic, ic, rx, rx], [gy0, ry, ry, ry + 0.05], color=INK, lw=0.6, solid_joinstyle="miter", solid_capstyle="butt", zorder=2)
    _arrow(ax, (rx, ry), (rx, be))
    fig.savefig(OUT / "framework.pdf", metadata={"CreationDate": None})
    plt.close(fig)


ATTN_LIGHT = "#F1E7D3"  # attention's lightest step (OKLCH L 0.93), for decode's transfers beside its compute


def fig_rewrites():
    """OPCORD's three rewrites, each before and after, with illustrative durations; in each "before" lane the waiting work
    starts where the work it waits on ends, which is the false dependence.
    (a) Composer: two dispatches in turn (the GEMMs wait for attention's dispatch to finish), then one dispatch that
        issues both groups' work before any wait.
    (b) Stream pass: inside attention's stream, column 7's segment waits behind the CP's synchronization on column 0,
        then the columns' segments alternate so both run at once.
    (c) Loop pass: with one buffer per role, block i+1's transfer waits for block i's compute to release the buffer;
        with a two-slot ring it fills the other slot (compute is 0.71 of the transfer, as measured in decode)."""
    fig, axes = plt.subplots(2, 3, figsize=(_m.WIDE, 1.05), sharex="col", gridspec_kw=dict(wspace=0.42, hspace=0.62))

    def lanes(ax, rows, labels, end, waits=()):
        for y, bars, color in rows:
            for t0, d, text in bars:
                ax.broken_barh([(t0, d)], (y - 0.32, 0.64), facecolors=color, edgecolor=INK, linewidth=0.4)
                if text:
                    ax.text(t0 + d / 2, y, text, ha="center", va="center_baseline", fontsize=FS_NOTE)
        ax.axvline(end, color="black", linewidth=0.5, linestyle=(0, (4, 2)))
        ax.set_xlim(0, end * 1.04)  # the bars start at the axis
        ax.set_yticks([1, 0], labels)
        ax.set_ylim(-0.55, 1.55)
        ax.tick_params(left=False, right=False, top=False, bottom=False)
        ax.set_xticks([])
        for side in ("top", "right", "bottom"):
            ax.spines[side].set_visible(False)
    a, g = 3.0, 2.6  # (a) attention and the GEMMs
    lanes(axes[0, 0], [(1, [(0, a, "")], ATTN_FILL), (0, [(a, g, "")], GEMM_FILL)], ["Attention", "GEMMs"], a + g,
          [(a, 0.68, 0.32)])
    lanes(axes[1, 0], [(1, [(0, a, "")], ATTN_FILL), (0, [(0, g, "")], GEMM_FILL)], ["Attention", "GEMMs"], a + g)
    s = 1.2  # (b) one segment per column
    lanes(axes[0, 1], [(1, [(0, s, "1"), (2 * s, s, "2")], ATTN_FILL), (0, [(s, s, "1"), (3 * s, s, "2")], ATTN_FILL)],
          ["Column 0", "Column 7"], 4 * s, [(s, 0.68, 0.32), (3 * s, 0.68, 0.32)])
    lanes(axes[1, 1], [(1, [(0, s, "1"), (s, s, "2")], ATTN_FILL), (0, [(0, s, "1"), (s, s, "2")], ATTN_FILL)],
          ["Column 0", "Column 7"], 4 * s)
    t, c = 1.0, 0.71  # (c) a block's transfer and compute
    lanes(axes[0, 2], [(1, [(k * (t + c), t, f"{k}") for k in range(3)], ATTN_LIGHT),
                       (0, [(k * (t + c) + t, c, f"{k}") for k in range(3)], ATTN_FILL)],
          ["Transfer", "Compute"], 3 * (t + c), [(k * (t + c) + t + c, 0.32, 0.68) for k in range(2)])
    lanes(axes[1, 2], [(1, [(k * t, t, f"{k}") for k in range(3)], ATTN_LIGHT),
                       (0, [((k + 1) * t, c, f"{k}") for k in range(3)], ATTN_FILL)], ["Transfer", "Compute"], 3 * (t + c))
    for j, title in enumerate(("(a) Composer", "(b) Stream pass", "(c) Loop pass")):
        axes[0, j].set_title(title, pad=13, loc="left")
    for j in range(3):
        for i, label in enumerate(("Before", "After")):
            axes[i, j].text(0.0, 1.03, label, transform=axes[i, j].transAxes, fontsize=FS_TICK, va="bottom")
    fig.supxlabel("Time (illustrative)", y=-0.05)
    save(fig, "rewrites.pdf", width=_m.WIDE, metadata={"CreationDate": None})
    plt.close(fig)


def fig_intro():
    """Figure 1, full width.
    (a) The host submits to the in-order CP, which issues the work of every column; the compute tiles are tinted by
        the column group of AIR's prefill on S2 (attention on columns 0 and 7, the GEMMs on 1-6), and one column is
        outlined.
    (b) The CP's issue order in one layer at 4,096 tokens (32 chunks). Original: AIR's host loop (mlir-air
        fused_prefill/dense.py:206-221) issues attention for every chunk, one dispatch each with its own waits, before
        the O-projection of chunk 0, which reads only chunk 0's attention. OPCORD: one composed dispatch of the plan the
        timeline ran (1b-4096-planner.npz, opcord d6caf8b; layer 0's seventh dispatch holds attention on chunk 3, the
        O-projection of chunk 0 and the QKV GEMMs of chunks 17-18) issues both groups before its first wait and awaits
        attention's output only at its end.
    (c) The measured timeline of Figure 1 before the split into panels: the median-TTFT run of each arm, Llama-3.2-1B,
        4,096 tokens, S2, time normalized to the original's TTFT."""
    H = 1.80
    fig = plt.figure(figsize=(_m.WIDE, H))

    def box(ax, x, y, w, h, text=None, fc="white", lw=0.5):
        _box(ax, x, y, w, h, text, fc=fc, lw=lw, fs=FS_NOTE)
    # ---- (a) the NPU
    W = 2.05
    axa = fig.add_axes([0.0, 0.0, W / _m.WIDE, 1.0])
    axa.set_xlim(0, W)
    axa.set_ylim(0, H)
    axa.set_aspect("equal")
    axa.axis("off")
    axa.text(0.02, H - 0.08, r"(a) XDNA~2 NPU", fontsize=FS_LABEL, va="center_baseline")
    t, g, x0, y0 = 0.15, 0.035, 0.42, 0.26
    th = t * 0.62
    xs = [x0 + c * (t + g) for c in range(8)]
    ys = [y0 + r * (th + 0.02) for r in range(6)]
    mid = (xs[0] + xs[-1] + t) / 2  # the CP over the array's middle, so its line drops straight onto the bus
    cy, ch, cw = 1.38, 0.17, 0.62
    box(axa, mid - cw / 2, cy, cw, ch, "In-order CP")
    box(axa, mid - cw / 2 - 0.58, cy, 0.40, ch, "Host", fc=MIST)
    _arrow(axa, (mid - cw / 2 - 0.18, cy + ch / 2), (mid - cw / 2, cy + ch / 2))
    for c, x in enumerate(xs):
        group = ATTN_FILL if c in (0, 7) else GEMM_FILL
        for r, y in enumerate(ys):
            box(axa, x, y, t, th, fc=GRAY if r == 0 else MIST if r == 1 else group, lw=0.35)
    top = ys[-1] + th
    bus = top + 0.10
    axa.plot([mid, mid], [cy, bus], color=INK, lw=0.6, solid_capstyle="butt")
    axa.plot([xs[0] + t / 2, xs[-1] + t / 2], [bus, bus], color=INK, lw=0.6, solid_capstyle="butt")
    for x in xs:
        _arrow(axa, (x + t / 2, bus), (x + t / 2, top + 0.005), lw=0.45)
    c = 2  # one column, outlined and named under the array
    axa.add_patch(Rectangle((xs[c] - 0.012, ys[0] - 0.012), t + 0.024, top - ys[0] + 0.024, fill=False,
                            edgecolor=INK, lw=0.6, ls=(0, (2, 1.2)), zorder=6))
    axa.text(xs[c] + t / 2, y0 - 0.085, "Column", ha="center", fontsize=FS_NOTE, va="center_baseline")
    for yy, label in ((ys[0] + th / 2, "Shim"), (ys[1] + th / 2, "Memory"), ((ys[2] + top) / 2, "Compute")):
        axa.text(x0 - 0.04, yy, label, ha="right", va="center_baseline", fontsize=FS_NOTE)
    for k, (fc, label) in enumerate(((ATTN_FILL, "Attention"), (GEMM_FILL, "GEMMs"))):  # the column groups' key
        kx = xs[4] + k * 0.52
        axa.add_patch(Rectangle((kx, y0 - 0.115), 0.07, 0.06, facecolor=fc, edgecolor=INK, lw=0.35))
        axa.text(kx + 0.10, y0 - 0.085, label, fontsize=FS_NOTE, va="center_baseline")
    # ---- (b) the CP's issue order
    W2 = 2.05
    axb = fig.add_axes([2.25 / _m.WIDE, 0.0, W2 / _m.WIDE, 1.0])
    axb.set_xlim(0, W2)
    axb.set_ylim(0, H)
    axb.axis("off")
    axb.text(0.0, H - 0.08, "(b) Issue order in one layer", fontsize=FS_LABEL, va="center_baseline")

    def instr(y, kind, text):
        fc = {"A": ATTN_FILL, "G": GEMM_FILL, "W": "white"}[kind]
        axb.add_patch(Rectangle((0.05, y - 0.055), 1.75, 0.11, facecolor=fc, edgecolor=INK, linewidth=0.35,
                                linestyle="-" if kind != "W" else (0, (1.5, 1)), zorder=3))
        axb.text(0.09, y, text, fontsize=FS_NOTE, va="center_baseline", ha="left", zorder=4)
    y = H - 0.27
    axb.text(0.05, y, "Original (one operator per dispatch)", fontsize=FS_NOTE, va="center_baseline")
    y -= 0.14
    for kind, text in (("A", "Issue attention, chunk 0"), ("W", "Wait for attention, chunk 0"), (None, r"$\vdots$"),
                       ("A", "Issue attention, chunk 31"), ("W", "Wait for attention, chunk 31"),
                       ("G", "Issue O-projection, chunk 0")):
        if kind is None:
            axb.text(0.40, y - 0.005, text, fontsize=FS_NOTE, va="center", ha="center")
            y -= 0.13
            continue
        instr(y, kind, text)
        y -= 0.125
    y -= 0.06
    axb.text(0.05, y, "OPCORD (one composed dispatch)", fontsize=FS_NOTE, va="center_baseline")
    y -= 0.14
    for kind, text in (("A", r"Issue attention, chunk $i$"), ("G", "Issue and await GEMMs of other chunks"),
                       ("W", r"Wait for attention, chunk $i$")):
        instr(y, kind, text)
        y -= 0.125
    # ---- (c) the measured timeline
    d = json.loads((_m.DATA / "fig1-intervals-1b.json").read_text())["arms"]
    base = d["ship"]["ttft_ms"]
    x0c, wc = 4.85 / _m.WIDE, 1.90 / _m.WIDE
    for k, (arm, name) in enumerate((("ship", "Original"), ("comp", "OPCORD"))):
        ax = fig.add_axes([x0c, 0.56 - k * 0.38, wc, 0.24])
        a = d[arm]
        groups = {}
        for yy, grp, color in ((2, "A", _m.ATTN_BAR), (1, "G", _m.GEMM_BAR)):
            spans = _m._merge(a["outstanding"][grp])
            groups[grp] = spans
            ax.broken_barh([(s / base, (e - s) / base) for s, e in spans], (yy - 0.32, 0.64), facecolors=color,
                           edgecolor="none")
        both = sum(e - s for s, e in _m._intersect(groups["A"], groups["G"]))  # checked against the record
        assert abs(both - a["both_outstanding_ms"]) < 1e-3, (arm, both, a["both_outstanding_ms"])
        ax.axvline(a["ttft_ms"] / base, color="black", lw=0.6, ls=(0, (4, 2)))
        ax.text(a["ttft_ms"] / base + 0.01, 1.5, rf"TTFT {a['ttft_ms'] / base:.2f}", fontsize=FS_NOTE, va="center")
        ax.set_title(name, pad=1.5, loc="left", fontsize=FS_TICK)
        ax.set_yticks([2, 1], ["Attention", "GEMMs"])
        ax.set_ylim(0.45, 2.55)
        ax.set_xlim(0, 1.22)  # room for the TTFT label inside the panel
        ax.tick_params(axis="y", length=0)
        ax.tick_params(axis="x", top=False)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        if k == 0:
            ax.set_xticklabels([])
        else:
            ax.set_xlabel("Normalized time", labelpad=1, fontsize=FS_TICK)
    fig.text(x0c - 0.075, 0.95, "(c) Measured prefill", fontsize=FS_LABEL, va="center_baseline")
    save(fig, "intro.pdf", width=_m.WIDE, metadata={"CreationDate": None})  # cropped to the text width
    plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fig_arch()
    fig_framework()
    fig_rewrites()
    fig_intro()
