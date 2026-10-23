# figs

`make_figs.py` turns the measurements in `data/` into the paper's data figures and generated table rows
(`paper/fig/`, or `FIGS_OUT`). Labels are typeset by LaTeX, so a TeX installation with `newtx` is needed.

```sh
python3 -m venv .venv && .venv/bin/pip install -r figs/requirements.txt
sh paper/figs.sh
```

## Where the data comes from

The files in this table are byte copies from the measurement repository `amd-npu`, each unchanged from the commit named in
its row. The first five are also present at `a0ee2edf44e04455695f11b2d597ca930d7ce35a` (tag `composer-v1.1`); the two
`decode-*.json` files postdate that tag and exist only from their own commits (`a6bc94b6`, `455740b1`):

| `data/` | source path | first committed | what it is |
|---|---|---|---|
| `e2-decomp.txt` | `prefill-e2/decomp.txt` | `e3acc8a` | the existing Llama-3.2-1B prefill: TTFT and each operator alone, at 512 / 2,048 / 4,096 tokens |
| `pairs-1.json` | `prefill-overlap/ovl/ovl.json` | `8f13e05` | one attention and one GEMM operator, alone, in sequence, and interleaved (6 pairs) |
| `pairs-2.json` | `prefill-overlap/ovl2/ovl.json` | `8f13e05` | as above, 4 pairs (one repeats a pair of `pairs-1`) |
| `pairs-3.json` | `prefill-overlap/ovl4/ovl.json` | `17f7ec3` | as above plus two queued commands and attention's columns alternated, 7 pairs (one repeat) |
| `component-model.json` | `prefill-overlap/v1/component_model.json` | `6735c61` | the event model's measured parameters, its fit, and the predictions scored on cells it was not fitted on |
| `decode-1b.json` | `decode-rename/gate-R/1b-2026-10-21/gate-1b.json` | `a6bc94b6` | Llama-3.2-1B decode per token at six context lengths, shipped against the renamed loop |
| `decode-qwen.json` | `decode-rename/gate-R/qwen-2026-10-21/gate-qwen.json` | `455740b1` | the same for Qwen3-4B, at four context lengths |

Four further files are not byte copies but extracts, each recording its own source in an `about` and a
`source` field, which is the provenance to trust over this table:

| `data/` | extracted from | what it is |
|---|---|---|
| `accuracy.json` | `78ec55b7` `prefill-overlap/cp-predict/score-2026-10-21.json` | predicted against measured TTFT, the scored cells separated from the arms reported beside them |
| `bound.json` | the same score file | the distance to the lower bound per cell, measured and as predicted before the runs |
| `timeline-1b.json` | `57621ff4` `prefill-overlap/ml-timeline/hold-2/report/report-1b.json` | per column group, the CP's blocked time and the time its work was outstanding |
| `turns.json` | `c61445da` `turn-w3-1b.json` and `171082f6` `turn-w3-qwen.json` | whole turns by append size and cached context, ratios re-derived here from the per-rep wall times |

The labs that record how each was measured are in the author's notes (`lab-prefill-device`, `lab-prefill-overlap`,
`lab-split-sweep`, `lab-agent-step`, `lab-decode-long-context`).
Where a pair was measured in more than one batch, the figures keep its first measurement.
