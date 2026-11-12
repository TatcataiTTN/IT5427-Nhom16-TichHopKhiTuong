"""
Ve bieu do thoi gian truy van theo kich thuoc du lieu (1x/2x/4x/8x) x 4 cau hinh
(Spark local[1], local[4], local[*], DuckDB), tu ket qua that o
warehouse/output/scale_benchmark_result.json (sinh boi warehouse/scale_benchmark.py).

Chay: python3 warehouse/plot_scale_benchmark.py
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

IN_JSON = os.path.join(os.path.dirname(__file__), "output", "scale_benchmark_result.json")
OUT_PNG = os.path.join(os.path.dirname(__file__), "..", "report", "figures", "scale_benchmark.png")

SERIES = [
    ("spark_local[1]", "Spark local[1] (1 core)", "#AA1E1E", "o"),
    ("spark_local[4]", "Spark local[4] (4 core)", "#C85A14", "s"),
    ("spark_local[*]", "Spark local[*] (14 core)", "#1E783C", "^"),
    ("duckdb", "DuckDB (đơn máy)", "#003C71", "D"),
]


def main():
    with open(IN_JSON) as f:
        data = json.load(f)
    n_base = data["n_base_ghcn"]
    results = data["results"]
    multipliers = sorted(int(k) for k in results.keys())
    sizes = [n_base * m for m in multipliers]

    fig, ax = plt.subplots(figsize=(6.3, 4.2), dpi=200)
    for key, label, color, marker in SERIES:
        medians = [results[str(m)][key]["median"] for m in multipliers]
        lo = [results[str(m)][key]["median"] - results[str(m)][key]["min"] for m in multipliers]
        hi = [results[str(m)][key]["max"] - results[str(m)][key]["median"] for m in multipliers]
        ax.errorbar(sizes, medians, yerr=[lo, hi], label=label, color=color, marker=marker,
                    markersize=5, linewidth=1.4, capsize=3)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Số dòng GHCN (nhân bản 1x/2x/4x/8x, thang log)")
    ax.set_ylabel("Thời gian truy vấn trung vị, 5 lần chạy (s, thang log)")
    ax.set_title("Thời gian truy vấn nhiệt độ TB theo trạm/tháng: Spark và DuckDB")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.2f}M" if x >= 1e6 else f"{x/1e3:.0f}K"))
    ax.grid(True, which="both", linestyle=":", linewidth=0.5, alpha=0.6)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2, fontsize=8, frameon=False)
    fig.tight_layout()
    os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
    fig.savefig(OUT_PNG, bbox_inches="tight")
    print(f"Wrote {OUT_PNG}")

    # In bang speedup Spark local[*] vs DuckDB de dua vao bao cao
    print("\nTy le thoi gian Spark local[*] / DuckDB theo kich thuoc:")
    for m in multipliers:
        t_spark = results[str(m)]["spark_local[*]"]["median"]
        t_duck = results[str(m)]["duckdb"]["median"]
        print(f"  {m}x ({n_base*m:,} dong): Spark {t_spark:.3f}s / DuckDB {t_duck:.3f}s "
              f"-> DuckDB nhanh hon {t_spark/t_duck:.1f} lan")


if __name__ == "__main__":
    main()
