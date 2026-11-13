"""
Chay that resolve_survivorship() (warehouse/survivorship.py) tren toan bo kho WeatherObs
va GHI RA mot bang da hop giai that -- tra loi dung cau hoi phan bien: "sau Survivorship,
bang nao chua gia tri thang? truy van 1 vi tri/1 ngay tra ve may dong?" (1 dong/vi_tri/ngay,
khong phai 5 dong theo tung nguon nhu WeatherObs goc).

Doi chieu: ty le xung dot in ra o day phai khop voi warehouse/survivorship_conflict_by_source.py
(da cong bo trong bao cao, Bang survivorship-conflict) vi ca hai dung chung buoc gop-truoc-theo-
nguon-ngay va chung nguong CONFLICT_THRESHOLD_PCT.

Chay: python3 warehouse/survivorship_resolve.py
Output: warehouse/output/weatherobs_fused.parquet (1 dong/location_id/ngay, cac cot <bien>,
        <bien>_source_used, <bien>_conflict cho 6 bien da cong bo trong bao cao)
"""
import os

import pandas as pd

from survivorship import CONFLICT_THRESHOLD_PCT, resolve_survivorship

OUT = os.path.join(os.path.dirname(__file__), "output")
WAREHOUSE = os.path.join(OUT, "weatherobs.parquet")
REPORTED_COLS = ["temp_c", "rh_pct", "precip_mm", "wind_speed_ms",
                  "pressure_surface_hpa", "pressure_msl_hpa"]
# nhom co >=2 nguon that cho tung bien, da cong bo trong Bang~\ref{tab:survivorship-conflict}
# (warehouse/survivorship_conflict_by_source.py) -- dung lam mau so doi chieu, vi cot
# "<bien>_conflict" cua resolve_survivorship() luon la True/False (khong NaN) ke ca khi
# chi co 1 nguon, nen khong dung lai de dem "bao nhieu ngay co >=2 nguon".
REPORTED_MULTI_SOURCE_GROUPS = {
    "temp_c": 119_504, "rh_pct": 10_962, "precip_mm": 41_529,
    "wind_speed_ms": 58_101, "pressure_surface_hpa": 33_921, "pressure_msl_hpa": 37_479,
}


def main():
    print("== Doc warehouse ==")
    needed = ["location_id", "timestamp_utc", "source"] + REPORTED_COLS
    df = pd.read_parquet(WAREHOUSE, columns=needed)
    print(f"  {len(df):,} dong tho, {df['source'].nunique()} nguon")

    print("\n== Chay resolve_survivorship() that (gop truoc theo nguon/ngay, roi chon theo hang) ==")
    fused = resolve_survivorship(df)
    print(f"  {len(fused):,} dong da hop giai (1 dong/location_id/ngay)")

    print("\n== Doi chieu ty le xung dot voi Bang da cong bo trong bao cao ==")
    for col in REPORTED_COLS:
        has_val = fused[fused[col].notna()]
        n_resolved = len(has_val)
        n_conflict = int(has_val[col + "_conflict"].sum())
        n_multi_reported = REPORTED_MULTI_SOURCE_GROUPS[col]
        pct = 100 * n_conflict / n_multi_reported if n_multi_reported else 0.0
        print(f"  {col}: {n_resolved:,} ngay co gia tri da hop giai (gom ca ngay chi 1 nguon) | "
              f"xung dot: {n_conflict:,} / {n_multi_reported:,} nhom >=2 nguon that = {pct:.1f}%")

    out_path = os.path.join(OUT, "weatherobs_fused.parquet")
    fused.to_parquet(out_path, index=False)
    print(f"\nDa ghi: {out_path}")

    print("\n== Vi du tra loi cau hoi phan bien: 1 vi tri/1 ngay tra ve may dong? ==")
    sample_loc = fused["location_id"].iloc[0]
    sample_day = fused[fused["location_id"] == sample_loc]["day"].iloc[0]
    one = fused[(fused["location_id"] == sample_loc) & (fused["day"] == sample_day)]
    print(f"  Truy van (location_id={sample_loc}, day={sample_day}): {len(one)} dong (dung 1 dong)")
    print(one[["location_id", "day"] + REPORTED_COLS +
              [c + "_source_used" for c in REPORTED_COLS]].to_string(index=False))


if __name__ == "__main__":
    main()
