#!/usr/bin/env python3
"""Figures exclusive to paper-min, drawn with figs/make_figs.py's style and data (that script and paper/ stay frozen).

Outputs (into this directory):
  choice-a.pdf   panel (a) of figs/make_figs.py fig_choice alone: the event model's error per development cell

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
    a.set_title("Event model", pad=4)
    fig.delaxes(b)
    m.save(fig, "choice-a.pdf")
    plt.close(fig)


if __name__ == "__main__":
    fig_choice_a()
