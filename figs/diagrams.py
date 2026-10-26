#!/usr/bin/env python3
"""The paper's schematic figures (not data plots), drawn as line art in make_figs.py's style.

  FIGS_OUT=paper/fig .venv/bin/python figs/diagrams.py

Outputs:
  framework.pdf  OPCORD's components over a compiled design, full width: inputs, analysis, checked rewrites, event
                 model, output
  arch.pdf  the XDNA 2 NPU as the paper uses it: host, hardware context, the CP's in-order instruction stream, the
            array of shim, memory and compute tiles over DRAM, and one compute tile and one shim tile magnified
  rewrites.pdf  OPCORD's three rewrites (composer, stream pass, loop pass), each before and after, full width
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_figs as _m  # noqa: E402  (style, palette, OUT)
from make_figs import ATTN, ATTN_FILL, COLUMN, GEMM, GEMM_FILL, GRAY, INK, OURS, OURS_TINT, OUT, plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, Rectangle  # noqa: E402

MIST, STONE = "#E4E4E4", "#707070"
# the fill steps of attention and the GEMMs, for the column groups of the default configuration
ATTN_PASTEL, GEMM_PASTEL = ATTN_FILL, GEMM_FILL
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
    """The host submits dispatches to a hardware context, whose CP executes each dispatch's instruction stream in
    order: an issue pushes a BD into a shim DMA's task queue and returns at once, a synchronization blocks the CP until
    a transfer completes. The array runs data-driven: each compute tile's DMA follows a chain of BDs, and locks hand
    each buffer between its producer and its consumer. The compute tiles are tinted by the column group that the
    original prefill's default configuration gives them: attention on columns 0 and 7, the GEMMs on columns 1-6. The two
    outlined tiles of column 7 are drawn larger at the right."""
    W, H = COLUMN - 0.04, 1.88
    fig, ax = _canvas(W, H)
    # ---- the submission path along the top: host -> hardware context -> CP -> its instruction stream
    ty, th = 1.64, 0.2
    _box(ax, 0.02, ty, 0.38, th, "Host", fc=MIST)
    _box(ax, 0.52, ty, 0.62, th, "Hardware context", fs=FS - 0.5)
    _box(ax, 1.26, ty, 0.30, th, "CP")
    _arrow(ax, (0.40, ty + th / 2), (0.52, ty + th / 2))
    _arrow(ax, (1.14, ty + th / 2), (1.26, ty + th / 2))
    kinds = "iisiiis"  # issue, issue, synchronize, ...
    cw, sx = 0.085, 1.66
    for k, kind in enumerate(kinds):  # equal, separate cells, so each instruction reads as one unit
        ax.add_patch(Rectangle((sx + k * cw + 0.006, ty + 0.02), cw - 0.012, th - 0.04,
                               facecolor=INK if kind == "i" else MIST, edgecolor=INK, linewidth=0.3, zorder=3))
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
    for r in (0, 4):  # the two tiles drawn larger at the right
        ax.add_patch(Rectangle((xs[-1], ys[r]), t, t, fill=False, edgecolor=INK, linewidth=1.0, zorder=4))
    # the default configuration's column groups, labelled above the array, the GEMMs' span clear of the tiles
    top = ys[5] + t
    gy = top + 0.085
    for c in (0, 7):
        ax.text(xs[c] + t / 2, gy, "Attn.", ha="center", va="center_baseline", fontsize=FS - 0.5)
    ax.text((xs[1] + xs[6] + t) / 2, gy, "GEMMs", ha="center", va="center_baseline", fontsize=FS - 0.5)
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
    vx = xs[-1] + t + 0.085
    ix = sx + 1.5 * cw
    ax.plot([ix, ix, vx, vx], [ty + 0.02, 1.48, 1.48, ys[0] + t / 2], color=INK, lw=0.6, solid_joinstyle="miter",
            zorder=9)
    _arrow(ax, (vx, ys[0] + t / 2), (xs[-1] + t, ys[0] + t / 2))
    ax.text(ix + 0.05, 1.52, "Issue: push a BD to a shim task queue", ha="left", va="center_baseline",
            fontsize=FS)
    # ---- the two outlined tiles of column 7, drawn larger
    cx0, cx1 = vx + 0.10, W - 0.01
    panels = (("Compute tile", 0.78, 1.38), ("Shim tile", 0.30, 0.66))
    for name, py0, py1 in panels:
        _box(ax, cx0, py0, cx1 - cx0, py1 - py0, fc="white", lw=0.5, z=4)
        ax.text(cx0 + 0.05, py1 - 0.07, name, ha="left", va="center_baseline", fontsize=FS, zorder=6,
                fontweight="bold")
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
    # compute tile: the DMA follows a chain of BDs, each naming the next
    _box(ax, px, 0.83, 0.30, 0.13, "DMA", z=5)
    for k in range(3):
        _box(ax, bx + k * 0.15, 0.855, 0.09, 0.08, fc=GRAY, lw=0.4, z=5)
        if k:
            _arrow(ax, (bx + (k - 1) * 0.15 + 0.09, 0.895), (bx + k * 0.15, 0.895), lw=0.4)
    ax.plot([px + 0.30, bx], [0.895, 0.895], color=INK, lw=0.4, zorder=5)
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
    """An instruction stream: issues dark, synchronizations light, left to right in execution order."""
    for k, kind in enumerate(kinds):
        ax.add_patch(Rectangle((x + k * cw + 0.004, y), cw - 0.008, h, facecolor=INK if kind == "i" else MIST,
                               edgecolor=INK, linewidth=0.3, zorder=z))
    return x + len(kinds) * cw


def _stage(ax, x, y, w, h, title, ours=True):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=OURS_TINT if ours else "white", edgecolor=MAGENTA if ours else INK,
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
    ax.text(xi + 0.08 + 6 * 0.048 + 0.04, 1.11, "Compiled design,\nopen or closed", ha="left", va="center", fontsize=fs,
            linespacing=1.1)
    rows_in = ((0.80, "Host program"), (0.60, "Operator probes"), (0.42, "Prompt length"))
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
    for k, (kind, label) in enumerate((("true", "True"), ("name", "Name"), ("order", "Order"))):
        lx, ly = ox + 0.92, 1.24 - k * 0.11
        ax.plot([lx, lx + 0.09], [ly, ly], lw=0.7, zorder=3, **style[kind])
        ax.text(lx + 0.12, ly, label, ha="left", va="center_baseline", fontsize=fs - 0.5)
    for y, label in ((0.70, "Dependence graph over every agent"), (0.56, "Legality conditions"),
                     (0.42, "A bound per false dependence")):
        ax.text(xa + 0.10, y, label, ha="left", va="center_baseline", fontsize=fs)
    # ---- the rewrites, each behind its checker
    xr, wr = 2.96, 1.80
    _stage(ax, xr, bot, wr, top - bot, "Rewrites, each behind a checker")
    rew = ((1.16, "Composer", "Reorder across operators"), (0.86, "Stream pass", "Reorder within a stream"),
           (0.50, "Loop pass", "Rename into rings"))
    for y, name, what in rew:
        _box(ax, xr + 0.08, y - 0.10, wr - 0.16, 0.20, fc="white", lw=0.4, z=3)
        ax.text(xr + 0.17, y, r"\checkmark", ha="center", va="center_baseline", fontsize=fs + 1, color=MAGENTA,
                zorder=5)
        ax.text(xr + 0.26, y, name, ha="left", va="center_baseline", fontsize=fs, fontweight="bold", zorder=5)
        ax.text(xr + 0.76, y, what, ha="left", va="center_baseline", fontsize=fs, zorder=5)
    # ---- the event model, prefill only
    xe, we, be = 4.94, 0.88, 0.57
    _stage(ax, xe, be, we, top - be, "Event model")
    for lane, bars in ((1.17, ((xe + 0.08, 0.20), (xe + 0.32, 0.28))), (1.02, ((xe + 0.08, 0.36), (xe + 0.48, 0.16)))):
        for x0, w in bars:
            ax.add_patch(Rectangle((x0, lane), w, 0.09, facecolor=GRAY, edgecolor="white", linewidth=0.5, zorder=3))
    for k, label in enumerate(("Order and", "configuration", "per prompt length")):
        ax.text(xe + 0.08, 0.91 - k * 0.12, label, ha="left", va="center_baseline", fontsize=fs)
    # ---- output
    xo = 5.98
    wo = W - xo
    _stage(ax, xo, bot, wo, top - bot, "Output", ours=False)
    _strip(ax, xo + 0.07, 1.16, "iiiss", cw=0.075, h=0.09)
    for k, label in enumerate(("Rewritten design", "on its own", "hardware context,", "or a refusal", "with its reason")):
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
    ax.text(xa + 0.10, ry + 0.06, "Probes, prompt length", ha="left", va="center_baseline", fontsize=fs - 0.5)
    fig.savefig(OUT / "framework.pdf", metadata={"CreationDate": None})
    plt.close(fig)


ATTN_LIGHT = "#F1E7D3"  # attention's lightest step (OKLCH L 0.93), for decode's transfers beside its compute


def fig_rewrites():
    """OPCORD's three rewrites, each before and after, with illustrative durations; a dotted arrow marks each false
    dependence, which ends where work waits on work whose results it does not use.
    (a) Composer: two dispatches in turn (the GEMMs wait for attention's dispatch to finish), then one dispatch that
        issues both groups' work before any wait.
    (b) Stream pass: inside attention's stream, column 7's segment waits behind the CP's synchronization on column 0,
        then the columns' segments alternate so both run at once.
    (c) Loop pass: with one buffer per role, block i+1's transfer waits for block i's compute to release the buffer;
        with a two-slot ring it fills the other slot (compute is 0.71 of the transfer, as measured in decode)."""
    fig, axes = plt.subplots(2, 3, figsize=(_m.WIDE, 1.38), sharex="col", gridspec_kw=dict(wspace=0.42, hspace=0.5))

    def lanes(ax, rows, labels, end, waits=()):
        for y, bars, color in rows:
            for t0, d, text in bars:
                ax.broken_barh([(t0, d)], (y - 0.32, 0.64), facecolors=color, edgecolor=INK, linewidth=0.4)
                if text:
                    ax.text(t0 + d / 2, y, text, ha="center", va="center_baseline", fontsize=FS - 0.5)
        for x, y0, y1 in waits:  # a dotted shaft with a solid head, from y0 to y1
            ax.plot([x, x], [y0, y1], color=INK, linewidth=0.6, linestyle=(0, (1, 1.2)), zorder=10)
            ax.add_patch(FancyArrowPatch((x, y1 + 0.05 * (y0 - y1)), (x, y1),
                                         arrowstyle="-|>,head_length=2.0,head_width=1.1", color=INK, linewidth=0.6,
                                         shrinkA=0, shrinkB=0, zorder=10))
        ax.axvline(end, color="black", linewidth=0.5, linestyle=(0, (4, 2)))
        ax.set_yticks([1, 0], labels, fontsize=FS)
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
        axes[0, j].set_title(title, fontsize=7, pad=13, loc="left")
    for j in range(3):
        for i, label in enumerate(("Before", "After")):
            axes[i, j].text(0.0, 1.03, label, transform=axes[i, j].transAxes, fontsize=FS, va="bottom")
    handles = [plt.Line2D([], [], color=INK, linewidth=0.6, linestyle=(0, (1, 1.2)))]
    fig.legend(handles, ["False dependence"], loc="lower right", bbox_to_anchor=(0.99, -0.07), handlelength=1.2)
    fig.supxlabel("Time (illustrative)", fontsize=7, y=-0.05)
    fig.savefig(OUT / "rewrites.pdf", metadata={"CreationDate": None})
    plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fig_arch()
    fig_framework()
    fig_rewrites()
