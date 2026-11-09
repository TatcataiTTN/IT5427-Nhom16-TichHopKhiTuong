#!/usr/bin/env python3
"""
ETL end-to-end: dữ liệu thô -> Mediated Schema (ingestion/parsers.py)
-> bảng Parquet partition theo year/source trên Spark (docs/03 Tuần 2, TV2 #2-3).

Hai bộ dữ liệu đầu vào (chọn bằng --dataset):
  full   (mặc định) — dữ liệu đầy đủ theo đề cương:
         GHCN toàn lịch sử (data_samples/batch_week2/ghcn_daily*),
         ISD 10 năm + Open-Meteo/NASA POWER 5 năm (data_samples/full/, scripts/download_full_points.py),
         ERA5 5 năm × 9 biến (data_samples/era5_full/, scripts/download_era5_full.py)
  week2  — bộ mẫu nhỏ Tuần 2 (data_samples/batch_week2/, scripts/batch_download_week2.py)

Cách ghi: mỗi nguồn được parse rồi ghi ra Parquet tạm (warehouse/output/_staging/), sau đó
Spark đọc toàn bộ staging và ghi lại có partition — tránh đẩy ~10 triệu dòng pandas qua
createDataFrame trên driver.

Chạy (cần Java 17+, xem README muc 6b):
  python3 warehouse/build_warehouse.py                  # full
  python3 warehouse/build_warehouse.py --dataset week2  # bộ mẫu nhỏ

Output: warehouse/output/weatherobs.parquet/year=<Y>/source=<S>/*.parquet (local, gitignored)
"""
import argparse
import glob
import os
import shutil
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ingestion.parsers import NUMERIC_COLUMNS, WEATHEROBS_COLUMNS, parse_ghcn, parse_isd, parse_nasa_power, parse_openmeteo
from warehouse.interpolation import bilinear_interpolate_era5, interpolate_era5_month
from warehouse.location import build_location_table

ROOT = os.path.join(os.path.dirname(__file__), "..", "data_samples")
WEEK2 = os.path.join(ROOT, "batch_week2")
FULL = os.path.join(ROOT, "full")
ERA5_FULL = os.path.join(ROOT, "era5_full")
OUT = os.path.join(os.path.dirname(__file__), "output")
STAGING = os.path.join(OUT, "_staging")


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Ép kiểu thống nhất để mọi file staging có cùng schema Parquet."""
    df = df[WEATHEROBS_COLUMNS].dropna(subset=["timestamp_utc", "location_id"]).copy()
    df["location_id"] = df["location_id"].astype(str)
    df["source"] = df["source"].astype(str)
    for c in ("temp_def", "qc_flag"):
        df[c] = df[c].astype("string")
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True).astype("datetime64[us, UTC]")
    for c in NUMERIC_COLUMNS:
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("float64")
    return df


class Staging:
    def __init__(self):
        shutil.rmtree(STAGING, ignore_errors=True)
        os.makedirs(STAGING)
        self.counts = {}
        self.n_files = 0

    def add(self, df: pd.DataFrame, source: str):
        if df is None or df.empty:
            return
        df = _normalize(df)
        df.to_parquet(os.path.join(STAGING, f"{self.n_files:05d}.parquet"), index=False)
        self.n_files += 1
        self.counts[source] = self.counts.get(source, 0) + len(df)


def _parse_files(paths, parser, staging, source, batch=20):
    """Parse nhiều file, gộp theo lô để staging không có hàng nghìn file nhỏ."""
    frames = []
    for fp in paths:
        try:
            frames.append(parser(fp))
        except Exception as e:
            print(f"  [BO QUA] {fp}: {e}")
        if len(frames) >= batch:
            staging.add(pd.concat(frames, ignore_index=True), source)
            frames = []
    if frames:
        staging.add(pd.concat(frames, ignore_index=True), source)
    print(f"  {source}: {staging.counts.get(source, 0):,} dong tu {len(paths)} file")


def _points(dirpath, parser):
    return [(fp, os.path.splitext(os.path.basename(fp))[0])
            for fp in sorted(glob.glob(os.path.join(dirpath, "*.json")))]


def stage_all_sources(dataset: str) -> Staging:
    staging = Staging()
    stations = build_location_table()
    stations = stations[stations["type"] == "station"]

    ghcn = sorted(glob.glob(os.path.join(WEEK2, "ghcn_daily", "*.csv"))
                  + glob.glob(os.path.join(WEEK2, "ghcn_daily_sea_priority", "*.csv")))
    _parse_files(ghcn, parse_ghcn, staging, "GHCN")

    if dataset == "full":
        isd = sorted(glob.glob(os.path.join(FULL, "isd", "*", "*.csv")))
        om_dir, nasa_dir = os.path.join(FULL, "openmeteo"), os.path.join(FULL, "nasa_power")
    else:
        isd = sorted(glob.glob(os.path.join(WEEK2, "isd_global_hourly_2024", "*.csv"))
                     + glob.glob(os.path.join(WEEK2, "isd_global_hourly_2024_sea_priority", "*.csv")))
        om_dir, nasa_dir = os.path.join(WEEK2, "openmeteo_2024"), os.path.join(WEEK2, "nasa_power_2024")
    _parse_files(isd, parse_isd, staging, "ISD")

    for fp, loc in _points(om_dir, parse_openmeteo):
        staging.add(parse_openmeteo(fp, loc), "OPEN_METEO")
    for fp, loc in _points(nasa_dir, parse_nasa_power):
        staging.add(parse_nasa_power(fp, loc), "NASA_POWER")
    print(f"  OPEN_METEO: {staging.counts.get('OPEN_METEO', 0):,} dong | "
          f"NASA_POWER: {staging.counts.get('NASA_POWER', 0):,} dong")

    if dataset == "full":
        months = sorted({os.path.splitext(os.path.basename(p))[0]
                         for p in glob.glob(os.path.join(ERA5_FULL, "2m_temperature", "*.nc"))})
        for month in months:
            staging.add(interpolate_era5_month(ERA5_FULL, month, stations), "ERA5")
        print(f"  ERA5: {staging.counts.get('ERA5', 0):,} dong ({len(months)} thang, noi suy Bilinear vao tram)")
    else:
        nc = os.path.join(WEEK2, "era5_arco", "era5_sea_2022-01-01_to_03.nc")
        if os.path.exists(nc):
            staging.add(bilinear_interpolate_era5(nc, stations), "ERA5")
            print(f"  ERA5: {staging.counts.get('ERA5', 0):,} dong (subset 3 ngay)")
    return staging


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["full", "week2"],
                        default="full" if os.path.isdir(ERA5_FULL) and os.path.isdir(FULL) else "week2")
    args = parser.parse_args()

    print(f"== Buoc 1/3: Parse tat ca nguon -> Mediated Schema (dataset={args.dataset}) ==")
    staging = stage_all_sources(args.dataset)
    n_expected = sum(staging.counts.values())
    print(f"Tong so ban ghi sau parse: {n_expected:,}")
    for src, n in sorted(staging.counts.items(), key=lambda kv: -kv[1]):
        print(f"{src:12s}{n:>12,}")

    print("\n== Buoc 2/3: Ghi Parquet qua Spark, partition theo year/source ==")
    from pyspark.sql import SparkSession, functions as F
    spark = (SparkSession.builder.appName("Nhom16-warehouse-build").master("local[*]")
             .config("spark.sql.session.timeZone", "UTC")
             .config("spark.driver.memory", "4g")
             .getOrCreate())

    sdf = spark.read.parquet(STAGING).withColumn("year", F.year("timestamp_utc"))
    out_path = os.path.join(OUT, "weatherobs.parquet")
    sdf.repartition("year", "source").write.mode("overwrite").partitionBy("year", "source").parquet(out_path)
    print(f"Da ghi: {out_path}")

    print("\n== Buoc 3/3: Doc lai kiem tra (dung Spark SQL) ==")
    back = spark.read.parquet(out_path)
    n_read = back.count()
    print(f"So dong doc lai: {n_read:,} (ky vong = {n_expected:,}) -> {'KHOP' if n_read == n_expected else 'LECH!'}")

    partitions = sorted({(r["year"], r["source"]) for r in back.select("year", "source").distinct().collect()})
    print(f"Tong {len(partitions)} partition (year, source); nam {partitions[0][0]} -> {partitions[-1][0]}")
    back.groupBy("source").agg(F.count("*").alias("so_dong"), F.countDistinct("location_id").alias("so_vi_tri"),
                               F.min("timestamp_utc").alias("tu"), F.max("timestamp_utc").alias("den")) \
        .orderBy("source").show(truncate=False)
    spark.stop()
    shutil.rmtree(STAGING, ignore_errors=True)
    print("\n== XONG. Warehouse san sang tai warehouse/output/weatherobs.parquet ==")


if __name__ == "__main__":
    main()
