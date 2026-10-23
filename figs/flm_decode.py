"""Decode per token: MLIR-AIR's design after our loop pass (R) against FastFlowLM on the same weights.

Like-for-like rules, fixed before computing:
  * both sides are time per generated token over a greedy decode that starts at a cached context of L positions
    (FastFlowLM: its engine's decoding_duration / completion_tokens, median of 5 requests; ours: wall time over
    250 tokens / 250, median of 3 runs), on the same quantized weight files;
  * the context is matched on L. FastFlowLM's measured L_actual is used, and our time at that L comes from our own
    measured point when one exists there, else from our fitted line T0 + c * L over our measured points (the fit the
    decode figure annotates). Each value says which;
  * ratio = ours / FastFlowLM, so a value below 1 means our renamed decode is faster;
  * the two sides were measured in different batches (different days), which this file records and does not
    correct for.

Usage: python3 -I figs/flm_decode.py <flm results.json> <decode-1b.json> <decode-qwen.json> <out.json>
"""
import json
import sys

PAIRS = (("llama3_2_1b", "llama32_1b_q4nx", 2), ("qwen3_4b", "qwen3_4b_q4nx", 3))


def ours_at(dec, L):
    pts = {int(k): v for k, v in dec["points"].items()}
    if L in pts:
        return pts[L]["R_ms_tok"], "measured"
    fit = dec["R_fit"]
    how = "fit" if L <= max(pts) else "extrapolated beyond our window"
    return fit["intercept_ms"] + fit["slope_us_per_pos"] * L / 1000.0, how


def main(flm_path, dec1b_path, decq_path, out_path):
    flm = json.load(open(flm_path))
    decs = (json.load(open(dec1b_path)), json.load(open(decq_path)))
    rows = []
    for flm_name, ours_name, idx in PAIRS:
        dec = decs[idx - 2]
        assert dec["model"] == ours_name, (dec["model"], ours_name)
        for cell, m in sorted(flm["models"][flm_name]["decode"].items(), key=lambda kv: int(kv[0])):
            L = int(m["L_actual"])
            ours, how = ours_at(dec, L)
            census_fit = dec["census_fit"]
            shipped = census_fit["intercept_ms"] + census_fit["slope_us_per_pos"] * L / 1000.0
            rows.append({
                "model": ours_name, "L": L, "flm_ms_tok": m["median_ms"], "flm_reps": m["n_valid"],
                "ours_R_ms_tok": ours, "ours_source": how, "shipped_fit_ms_tok": shipped,
                "ratio_ours_over_flm": ours / m["median_ms"], "ratio_shipped_over_flm": shipped / m["median_ms"],
            })
    out = {"about": __doc__.split("\n\n")[0], "inputs": [flm_path, dec1b_path, decq_path], "rows": rows,
           "cross_batch": True}
    json.dump(out, open(out_path, "w"), indent=1)
    for r in rows:
        print(f"{r['model']:16} L={r['L']:6}  FLM {r['flm_ms_tok']:8.2f}  ours {r['ours_R_ms_tok']:8.2f} "
              f"({r['ours_source']})  ours/FLM {r['ratio_ours_over_flm']:.3f}  shipped/FLM "
              f"{r['ratio_shipped_over_flm']:.3f}")


if __name__ == "__main__":
    main(*sys.argv[1:5])
