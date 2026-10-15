# aie-cosched

Co-scheduling concurrent work on an AMD AI Engine array (XDNA 2 NPU) through its one in-order command processor.

| Directory | Contents |
|---|---|
| `figs/` | The measurements the paper plots (copied with their provenance) and the script that plots them |
| `paper/` | The paper's LaTeX source (excluded from a public release) |

The composer and its measurement harness currently live in the measurement repository (`amd-npu`, tags
`composer-v1`, `composer-v1.1`); the artifact moves here for release.

## Paper

From `paper/`, the build is one watcher:

```sh
latexmk -pdf -pvc -view=none -outdir=build -synctex=1 -interaction=nonstopmode -file-line-error main.tex
```

Figures: `sh paper/figs.sh` (see `figs/README.md`).
