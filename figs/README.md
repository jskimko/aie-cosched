# figs

`make_figs.py` turns the measurements in `data/` into the paper's data figures and generated table rows
(`paper/fig/`, or `FIGS_OUT`). Labels are typeset by LaTeX, so a TeX installation with `newtx` is needed.

```sh
python3 -m venv .venv && .venv/bin/pip install -r figs/requirements.txt
sh paper/figs.sh
```

## Provenance

Every file in `data/` is a byte copy from the measurement repository `amd-npu` at
`a0ee2edf44e04455695f11b2d597ca930d7ce35a` (tag `composer-v1.1`). Each is unchanged from the commit that first added it:

| `data/` | source path | first committed | what it is |
|---|---|---|---|
| `e2-decomp.txt` | `prefill-e2/decomp.txt` | `e3acc8a` | the existing Llama-3.2-1B prefill: TTFT and each operator alone, at 512 / 2,048 / 4,096 tokens |
| `pairs-1.json` | `prefill-overlap/ovl/ovl.json` | `8f13e05` | one attention and one GEMM operator, alone, in sequence, and interleaved (6 pairs) |
| `pairs-2.json` | `prefill-overlap/ovl2/ovl.json` | `8f13e05` | as above, 4 pairs (one repeats a pair of `pairs-1`) |
| `pairs-3.json` | `prefill-overlap/ovl4/ovl.json` | `17f7ec3` | as above plus two queued commands and attention's columns alternated, 7 pairs (one repeat) |
| `component-model.json` | `prefill-overlap/v1/component_model.json` | `6735c61` | the event model's measured parameters and its fit and held-out predictions |

The labs that record how each was measured are in the author's notes (`lab-prefill-device`, `lab-prefill-overlap`).
Where a pair was measured in more than one batch, the figures keep its first measurement.
