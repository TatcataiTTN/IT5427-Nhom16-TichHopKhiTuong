"""
Sinh Data Quality Report that tu warehouse (docs/03 Tuan 3, TV2 #8): ty le missing, outlier,
do phu khong gian-thoi gian theo tung nguon. In ra terminal + ghi docs/13-data-quality-report.md.

Chay: python3 warehouse/data_quality_report.py
"""
import os
import sys
from datetime import date

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ingestion.veracity import detect_outliers_iqr

ROOT = os.path.join(os.path.dirname(__file__), "..")
WAREHOUSE = os.path.join(ROOT, "warehouse", "output", "weatherobs.parquet")
OUT_MD = os.path.join(ROOT, "docs", "13-data-quality-report.md")

CORE_VARS = ["temp_c", "rh_pct", "precip_mm", "wind_speed_ms", "pressure_msl_hpa"]


def missing_rate_by_source(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for source, g in df.groupby("source"):
        row = {"source": source, "n_records": len(g)}
        for col in CORE_VARS:
            row[f"{col}_missing_pct"] = round(g[col].isna().mean() * 100, 1)
        rows.append(row)
    return pd.DataFrame(rows).sort_values("n_records", ascending=False)


def outlier_rate_by_source(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for source, g in df.groupby("source"):
        row = {"source": source}
        for col in CORE_VARS:
            flags = detect_outliers_iqr(g[col])
            n_valid = g[col].notna().sum()
            row[f"{col}_outlier_pct"] = round(flags.sum() / n_valid * 100, 2) if n_valid > 0 else None
        rows.append(row)
    return pd.DataFrame(rows)


def spatiotemporal_coverage(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for source, g in df.groupby("source"):
        dates = pd.to_datetime(g["timestamp_utc"])
        rows.append({
            "source": source,
            "n_locations": g["location_id"].nunique(),
            "date_min": dates.min().date().isoformat(),
            "date_max": dates.max().date().isoformat(),
            "n_days_span": (dates.max() - dates.min()).days + 1,
        })
    return pd.DataFrame(rows)


def main():
    df = pd.read_parquet(WAREHOUSE)
    print(f"Tong so ban ghi: {len(df)}")

    missing = missing_rate_by_source(df)
    outliers = outlier_rate_by_source(df)
    coverage = spatiotemporal_coverage(df)

    print("\n=== Ty le MISSING theo nguon (%) ===")
    print(missing.to_string(index=False))
    print("\n=== Ty le OUTLIER (IQR) theo nguon (%, tren so ban ghi khong null) ===")
    print(outliers.to_string(index=False))
    print("\n=== Do phu khong gian-thoi gian theo nguon ===")
    print(coverage.to_string(index=False))

    lines = [
        "# Data Quality Report (TV2 #8, Tuần 3)",
        "",
        f"Sinh tự động từ `warehouse/data_quality_report.py`, chạy thật trên "
        f"`warehouse/output/weatherobs.parquet` ngày {date.today().isoformat()}. "
        f"Tổng {len(df):,} bản ghi.",
        "",
        "## 1. Tỷ lệ Missing theo nguồn (%)",
        "",
        missing.to_markdown(index=False),
        "",
        "## 2. Tỷ lệ Outlier (IQR, Tukey's fences) theo nguồn (%, trên số bản ghi không null)",
        "",
        outliers.to_markdown(index=False),
        "",
        "Lưu ý phương pháp: dùng IQR thay vì Z-score làm chỉ số chính vì IQR bền vững hơn với "
        "outlier cực đoan (xem `ingestion/veracity.py` — Z-score bị hiệu ứng \"masking\": outlier "
        "cực đoan tự làm std phình to, che giấu chính nó). Outlier ở đây chỉ được GẮN CỜ, không tự "
        "động xoá — một số giá trị \"outlier\" thống kê là hiện tượng thời tiết cực đoan có thật "
        "(bão, đợt nắng nóng), không phải lỗi dữ liệu.",
        "",
        "## 3. Độ phủ không gian-thời gian theo nguồn",
        "",
        coverage.to_markdown(index=False),
        "",
    ]
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nDa ghi: {OUT_MD}")
    print("PASS")


if __name__ == "__main__":
    main()
