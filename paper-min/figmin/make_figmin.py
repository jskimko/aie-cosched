#!/usr/bin/env python3
"""Figures exclusive to paper-min, drawn with figs/make_figs.py's style and data (that script and paper/ stay frozen).

Outputs (into this directory):
  choice-a.pdf   panel (a) of figs/make_figs.py fig_choice alone: the event model's error per development cell
  choice-len.pdf the composed order's speedup against the prompt length per development cell, measured and predicted

Run with the figure venv: aie-cosched/.venv/bin/python make_figmin.py [path to aie-cosched/figs]
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIGS = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/home/kimko/aie2p-gmk/aie-cosched-paper-0/aie-cosched/figs")
sys.path.insert(0, str(FIGS))
import make_figs as m  # noqa: E402

plt, json = m.plt, m.json
m.OUT = HERE


@m.type_scale(m.CHOICE_SCALE)
def fig_choice_a():
    """Panel (a) of make_figs.fig_choice, drawn by the same lines on the same two-row grid so that its axes keep their
    size; the panel (b) axes are removed before saving, and the panel letter goes with them."""
    rows = json.loads((m.DATA / "accuracy-cells.json").read_text())
    fig, (a, b) = plt.subplots(2, 1, figsize=(m.COLUMN, 2.8), gridspec_kw=dict(height_ratios=[1.35, 0.85], hspace=0.62))
    a.axhspan(-5, 5, color="#EDEDED", zorder=0, linewidth=0)
    for key, llm in m.KEY_LLM.items():
        rs = [r for r in rows if r["model"].startswith(key)]
        marker, fill, _ = m.DECODE_STYLE[llm]
        a.plot([r["measured"] for r in rs], [(r["dev"] - 1) * 100 for r in rs], linestyle="none", marker=marker,
               markersize=2.8, color=m.INK, markerfacecolor=m.INK if fill == "full" else "white", markeredgewidth=0.6,
               label=llm)
    a.axhline(0, color="black", linewidth=0.5)
    a.set_xscale("log", base=2)
    a.set_xticks([1, 1.25, 1.5, 2], ["1.0", "1.25", "1.5", "2.0"])
    a.minorticks_off()
    a.set_xlabel("Measured speedup of the composed order", labelpad=1)
    a.set_ylabel(r"Prediction error (\%)", labelpad=1)
    a.set_ylim(-24, 8)  # room below the band for the legend
    a.legend(loc="lower left", ncol=2, handletextpad=0.2, columnspacing=0.6, labelspacing=0.15)
    fig.delaxes(b)
    m.save(fig, "choice-a.pdf")
    plt.close(fig)


@m.type_scale(m.CHOICE_SCALE)
def fig_choice_len():
    """The composed order's speedup over the original against the prompt length on the development cells of
    data/accuracy-cells.json, measured (marker, filled on S2) and as the event model predicts (violet dash, measured
    times its 'dev' = predicted / measured), at choice-a.pdf's size. Each LLM is offset slightly in length so that the
    five stay apart."""
    rows = json.loads((m.DATA / "accuracy-cells.json").read_text())
    fig, a = plt.subplots(figsize=(m.COLUMN, 1.316))
    offsets = dict(zip(m.KEY_LLM, (-0.24, -0.12, 0.0, 0.12, 0.24)))  # octaves
    handles = []
    for key, llm in m.KEY_LLM.items():
        rs = sorted((r for r in rows if r["model"].startswith(key)), key=lambda r: r["N"])
        marker, _, _ = m.DECODE_STYLE[llm]
        xs = [r["N"] * 2 ** offsets[key] for r in rs]
        meas = [r["measured"] for r in rs]
        pred = [r["measured"] * r["dev"] for r in rs]
        a.vlines(xs, meas, pred, color=m.OURS, linewidth=0.5, zorder=2)
        a.plot(xs, pred, linestyle="none", marker="_", markersize=3.2, markeredgewidth=0.8, color=m.OURS, zorder=3)
        for x, y, r in zip(xs, meas, rs):
            a.plot([x], [y], linestyle="none", marker=marker, markersize=2.6, color=m.INK, markeredgewidth=0.5,
                   markerfacecolor=m.INK if r["split"] == "S2" else "white", zorder=4)
        handles.append(plt.Line2D([], [], linestyle="none", marker=marker, markersize=2.6, color=m.INK,
                                  markeredgewidth=0.5, markerfacecolor=m.INK, label=llm))
    handles.append(plt.Line2D([], [], linestyle="none", marker="_", markersize=3.2, markeredgewidth=0.8,
                              color=m.OURS, label="Predicted"))
    a.axhline(1, color="black", linewidth=0.5, zorder=1)
    a.set_xscale("log", base=2)
    a.set_xticks([128, 512, 2048, 8192, 32768], ["128", "512", "2K", "8K", "32K"])
    a.minorticks_off()
    a.set_xlim(128 * 2 ** -0.6, 32768 * 2 ** 0.6)
    a.set_ylim(0.85, 2.25)
    a.set_yticks([1.0, 1.5, 2.0], ["1.0", "1.5", "2.0"])
    a.set_xlabel("Prompt length (tokens)", labelpad=1)
    a.set_ylabel(r"Speedup ($\times$)", labelpad=1)
    a.legend(handles=handles, loc="upper left", ncol=2, handletextpad=0.1, columnspacing=0.5, labelspacing=0.15,
             borderaxespad=0.2)
    m.save(fig, "choice-len.pdf")
    plt.close(fig)


if __name__ == "__main__":
    fig_choice_a()
    fig_choice_len()
