"""
Dac trung du lieu & yeu cau xu ly THAT (phan hoi giang vien: "missing? out of range? do do khong
dong nhat?") — thay cho khung "di thuong khi hau" truoc do, dung dung trong tam Veracity/Variety.

Nguon so lieu — KHONG bia:
  - % missing, % outlier (IQR) theo (bien, nguon): warehouse/data_quality_report.py chay that tren
    warehouse/output/weatherobs.parquet (kho hien tai, 4.000.489 dong).
  - So dong bi gan co QC that (RANGE/JUMP/GHCN_Q/ISD_QC) tu chinh cot qc_flag trong warehouse.
  - Bang don vi/dinh nghia khong dong nhat: doc truc tiep tu ingestion/parsers.py (PHYSICAL_RANGES,
    TEMP_DEF_*, cac phep quy doi don vi that trong parse_nasa_power/parse_openmeteo/parse_isd).

Chay: python3 warehouse/plot_data_quality.py
"""
import os
import sys
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ingestion.veracity import detect_outliers_iqr

OUT = os.path.join(os.path.dirname(__file__), "..", "report", "figures")
WAREHOUSE = os.path.join(os.path.dirname(__file__), "output", "weatherobs.parquet")

SRC_COLOR = {"GHCN": "#2a78d6", "ISD": "#eb6834", "ERA5": "#1baf7a",
            "OPEN_METEO": "#eda100", "NASA_POWER": "#e87ba4"}
SRC_ORDER = ["GHCN", "ISD", "NASA_POWER", "OPEN_METEO"]
VARS = ["temp_c", "rh_pct", "precip_mm", "wind_speed_ms", "pressure_msl_hpa"]
VAR_LABEL = {"temp_c": "Nhiệt độ", "rh_pct": "Độ ẩm", "precip_mm": "Lượng mưa",
            "wind_speed_ms": "Tốc độ gió", "pressure_msl_hpa": "Áp suất MSL"}


def grouped_bar(pct_table, title, ylabel, out_png, note):
    note_lines = textwrap.wrap(note, width=92)
    fig_h = 3.0 + 0.16 * len(note_lines)
    fig, ax = plt.subplots(figsize=(6.1, fig_h), dpi=300)
    n_src = len(SRC_ORDER)
    width = 0.8 / n_src
    x = np.arange(len(VARS))
    for i, src in enumerate(SRC_ORDER):
        vals = [pct_table.get((v, src), np.nan) for v in VARS]
        xi = x + (i - (n_src - 1) / 2) * width
        bars = ax.bar(xi, vals, width=width * 0.92, color=SRC_COLOR[src], label=src,
                      edgecolor="white", linewidth=0.6)
        for xb, v in zip(xi, vals):
            if v is not None and not (isinstance(v, float) and np.isnan(v)):
                ax.text(xb, v + 1.3, f"{v:.1f}", ha="center", va="bottom", fontsize=6.3,
                       rotation=90 if v > 20 else 0, color="#1A1A1A")
    ax.set_xticks(x)
    ax.set_xticklabels([VAR_LABEL[v] for v in VARS], fontsize=9)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_ylim(0, 108)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle=":", linewidth=0.5, alpha=0.6)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=4, fontsize=7.3, frameon=False,
             columnspacing=1.0, handletextpad=0.4)
    ax.set_title(title, fontsize=10, fontweight="bold", pad=10)
    fig.tight_layout()
    bottom_margin = 0.20 + 0.045 * len(note_lines)
    fig.subplots_adjust(bottom=bottom_margin, top=0.84, left=0.145)
    fig.text(0.5, 0.012, "\n".join(note_lines), ha="center", va="bottom", fontsize=6.3,
             color="#5A5A5A", style="italic")
    fig.savefig(out_png, facecolor="white")
    print(f"Wrote {out_png}")


def plot_qc_flags(out_png):
    df = pd.read_parquet(WAREHOUSE, columns=["source", "qc_flag"])
    flagged = df[df["qc_flag"].notna()]
    rows = []
    for src, qc in zip(flagged["source"], flagged["qc_flag"]):
        for part in qc.split(";"):
            rows.append((src, part.split(":")[0]))
    tally = pd.DataFrame(rows, columns=["source", "flag_type"])
    pivot = tally.groupby(["flag_type", "source"]).size().unstack(fill_value=0)
    flag_label = {"GHCN_Q": "Cờ QC gốc của GHCN\n(Q_FLAG: outlier/inconsistent/gap...)",
                 "ISD_QC": "Cờ QC gốc của ISD\n(mã 2/3/6/7: nghi ngờ/sai)",
                 "JUMP": "Nhảy giá trị phi vật lý\n(>10°C/giờ hoặc >10hPa/3giờ)",
                 "RANGE": "Ngoài khoảng vật lý\n(PHYSICAL_RANGES)"}
    order = [f for f in ["GHCN_Q", "ISD_QC", "JUMP", "RANGE"] if f in pivot.index]
    pivot = pivot.loc[order]

    fig, ax = plt.subplots(figsize=(5.2, 3.4), dpi=300)
    y = np.arange(len(order))
    left = np.zeros(len(order))
    for src in SRC_ORDER:
        if src not in pivot.columns:
            continue
        vals = pivot[src].values.astype(float)
        if vals.sum() == 0:
            continue
        ax.barh(y, vals, left=left, color=SRC_COLOR[src], label=src, height=0.55,
               edgecolor="white", linewidth=0.8)
        left += vals
    totals = pivot.sum(axis=1).values
    for yi, total in zip(y, totals):
        ax.text(total + totals.max() * 0.025, yi, f"{total:,}", va="center", fontsize=8,
               fontweight="bold")
    ax.set_xlim(0, totals.max() * 1.20)
    ax.set_yticks(y)
    ax.set_yticklabels([flag_label.get(f, f) for f in order], fontsize=7.3)
    ax.invert_yaxis()
    n_total = len(df)
    n_flagged = len(flagged)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.grid(axis="x", linestyle=":", linewidth=0.5, alpha=0.6)
    ax.legend(loc="lower right", fontsize=7, frameon=False)
    fig.tight_layout(rect=[0, 0.09, 1, 0.84])
    fig.suptitle("Số lần can thiệp QC thật trong pipeline nạp dữ liệu\n"
                "(giá trị bị đặt NaN + gắn cờ lý do, KHÔNG xoá dòng)",
                fontsize=8.3, fontweight="bold", y=0.985)
    fig.text(0.5, 0.012, f"Số dòng bị gắn cờ (trên tổng {n_total:,} dòng — chỉ {n_flagged:,} dòng, "
             f"{100*n_flagged/n_total:.2f}%)", ha="center", va="bottom", fontsize=7)
    fig.savefig(out_png, facecolor="white")
    print(f"Wrote {out_png}")


def main():
    os.makedirs(OUT, exist_ok=True)
    df = pd.read_parquet(WAREHOUSE, columns=["source"] + VARS)

    missing, outlier = {}, {}
    for src, g in df.groupby("source", observed=True):
        for v in VARS:
            missing[(v, src)] = round(g[v].isna().mean() * 100, 1)
            n_valid = g[v].notna().sum()
            if n_valid > 0:
                outlier[(v, src)] = round(detect_outliers_iqr(g[v]).sum() / n_valid * 100, 1)

    grouped_bar(missing, "Tỷ lệ MISSING theo biến và nguồn dữ liệu (%)",
               "% bản ghi NULL / không thu thập biến này",
               os.path.join(OUT, "data_quality_missing_pct.png"),
               "VD: GHCN không đo độ ẩm/gió/áp suất (100% missing cấu trúc) — không phải lỗi, "
               "GHCN-Daily chỉ công bố nhiệt độ + mưa. ISD/NASA POWER không đo lượng mưa/áp suất MSL tương ứng.")
    grouped_bar(outlier, "Tỷ lệ OUTLIER (IQR, Tukey's fences) theo biến và nguồn (%)",
               "% giá trị không null bị gắn cờ outlier",
               os.path.join(OUT, "data_quality_outlier_pct.png"),
               "Chỉ gắn cờ tham khảo, KHÔNG tự xoá — một phần là hiện tượng thời tiết cực đoan thật "
               "(bão, mưa lớn), không phải lỗi cảm biến (xem ingestion/veracity.py).")
    plot_qc_flags(os.path.join(OUT, "data_quality_qc_flags.png"))


if __name__ == "__main__":
    main()
