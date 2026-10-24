#!/usr/bin/env python3
"""Headline data: TTFT of the fastest existing schedule and of OPCORD per LLM and cell, from the split sweep.

Reads the split-sweep result files from the amd-npu bare at the pinned commits below (git show, no checkout) and writes
data/headline.json. For each LLM and cell (scratch 2,048 and 4,096; appends 4,096 + 4,096 and 16,384 + 4,096):
- existing: the lowest median over every measured split of the shipped order and of the shipped order with
  attention's columns alternated ("shipar"), i.e. the fastest existing schedule measured;
- opcord: the lowest median over every measured split of the composed schedule;
- the ratio of the two medians, and its range from the reps (existing min / OPCORD max to existing max / OPCORD min).
"""
import json
import statistics
import subprocess
from pathlib import Path

BARE = Path.home() / "git" / "amd-npu.git"
SWEEP = "prefill-overlap/split-sweep"
# (commit, path under SWEEP, split label); each file holds cfg -> cell -> arm -> reps (ms)
SOURCES = {
    "Llama-3.2-1B": [("ba9f6f8", "llama32_1b_q4nx/w1/shipar-S2.json", "S2"),
                     ("ba9f6f8", "llama32_1b_q4nx/w1/shipar-S4.json", "S4")],
    "Qwen3-4B": [("ba9f6f8", "qwen3_4b_q4nx/w1/shipar-S2.json", "S2"),
                 ("ba9f6f8", "qwen3_4b_q4nx/w1/shipar-S4.json", "S4")],
    "Llama-3.1-8B": [("f336942b", "llama31_8b_q4nx/w1/shipar-S2.json", "S2"),
                     ("f336942b", "llama31_8b_q4nx/w1/shipar-S4.json", "S4"),
                     ("f5a5f11", "llama31_8b_q4nx/run-S4.json", "S4")],
    "Gemma3-4B": [("08a56cd", "gemma3_4b_q4nx/run-S1.json", "S1"),
                  ("08a56cd", "gemma3_4b_q4nx/run-S2.json", "S2"),
                  ("08a56cd", "gemma3_4b_q4nx/run-S4.json", "S4"),
                  ("08a56cd", "gemma3_4b_q4nx/shipar-S2.json", "S2")],
    "LFM2-1.2B": [("838a2220", "lfm2_1_2b_q4nx/rerun-2026-10-22/run-S1.json", "S1"),
                  ("838a2220", "lfm2_1_2b_q4nx/rerun-2026-10-22/run-S2.json", "S2"),
                  ("838a2220", "lfm2_1_2b_q4nx/rerun-2026-10-22/run-S4.json", "S4"),
                  ("838a2220", "lfm2_1_2b_q4nx/rerun-2026-10-22/shipar-S2.json", "S2")],
}
CELLS = ("scratch:0:2048", "scratch:0:4096", "append:4096:4096", "append:16384:4096")
EXISTING, OURS = ("ship", "shipar"), ("comp",)


def load(commit, path):
    out = subprocess.run(["git", "-C", str(BARE), "show", f"{commit}:{SWEEP}/{path}"], capture_output=True, text=True,
                         check=True).stdout
    return json.loads(out)["cfg"]


def best(candidates):
    """The (median, reps, label) with the lowest median."""
    return min(candidates, key=lambda c: c[0])


def main():
    rows = {}
    for llm, files in SOURCES.items():
        arms = {}  # cell -> list of (median, reps, label) per kind
        for commit, path, split in files:
            for cell, by_arm in load(commit, path).items():
                if cell not in CELLS:
                    continue
                for arm, reps in by_arm.items():
                    if arm in EXISTING or arm in OURS:
                        kind = "opcord" if arm in OURS else "existing"
                        arms.setdefault(cell, {}).setdefault(kind, []).append(
                            (statistics.median(reps), reps, f"{arm}@{split}", commit))
        rows[llm] = {}
        for cell in CELLS:
            if cell not in arms or not {"existing", "opcord"} <= set(arms[cell]):
                continue
            e, o = best(arms[cell]["existing"]), best(arms[cell]["opcord"])
            rows[llm][cell] = {
                "existing_ms": e[0], "existing_arm": e[2], "existing_commit": e[3],
                "opcord_ms": o[0], "opcord_arm": o[2], "opcord_commit": o[3],
                "ratio": e[0] / o[0], "ratio_lo": min(e[1]) / max(o[1]), "ratio_hi": max(e[1]) / min(o[1]),
                "reps": [len(e[1]), len(o[1])],
            }
    out = Path(__file__).parent / "data" / "headline.json"
    out.write_text(json.dumps({"source": {llm: files for llm, files in SOURCES.items()}, "cells": rows}, indent=1))
    for llm, cells in rows.items():
        print(llm, {c.split(":", 1)[1]: (round(v["ratio"], 3), v["existing_arm"], v["opcord_arm"]) for c, v in cells.items()})


if __name__ == "__main__":
    main()
