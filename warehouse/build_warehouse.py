#!/usr/bin/env python3
"""
ETL end-to-end: dữ liệu thô (data_samples/batch_week2/) -> Mediated Schema (ingestion/parsers.py)
-> bảng Parquet partition theo year/source trên Spark (docs/03 Tuần 2, TV2 #2-3).

Chạy (cần Java 17+, xem README muc 6b):
  JAVA_HOME=$(brew --prefix openjdk@17)/libexec/openjdk.jdk/Contents/Home \
    python3 warehouse/build_warehouse.py

Output: warehouse/output/weatherobs.parquet/year=<Y>/source=<S>/*.parquet (local, gitignored)
"""
import glob
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ingestion.parsers import parse_ghcn, parse_isd, parse_nasa_power, parse_openmeteo
from warehouse.interpolation import bilinear_interpolate_era5
from warehouse.location import build_location_table

DATA = os.path.join(os.path.dirname(__file__), "..", "data_samples", "batch_week2")
OUT = os.path.join(os.path.dirname(__file__), "output")
ERA5_NC = os.path.join(DATA, "era5_arco", "era5_sea_2022-01-01_to_03.nc")


def load_all_point_sources() -> pd.DataFrame:
    frames = []

    for subdir in ("ghcn_daily", "ghcn_daily_sea_priority"):
        for fp in sorted(glob.glob(os.path.join(DATA, subdir, "*.csv"))):
            try:
                frames.append(parse_ghcn(fp))
            except Exception as e:
                print(f"  [BO QUA] {fp}: {e}")

    for subdir in ("isd_global_hourly_2024", "isd_global_hourly_2024_sea_priority"):
        for fp in sorted(glob.glob(os.path.join(DATA, subdir, "*.csv"))):
            try:
                frames.append(parse_isd(fp))
            except Exception as e:
                print(f"  [BO QUA] {fp}: {e}")

    for fp in sorted(glob.glob(os.path.join(DATA, "nasa_power_2024", "*.json"))):
        loc = os.path.splitext(os.path.basename(fp))[0]
        frames.append(parse_nasa_power(fp, loc))

    for fp in sorted(glob.glob(os.path.join(DATA, "openmeteo_2024", "*.json"))):
        loc = os.path.splitext(os.path.basename(fp))[0]
        frames.append(parse_openmeteo(fp, loc))

    if os.path.exists(ERA5_NC):
        locations = build_location_table()
        stations_only = locations[locations["type"] == "station"]
        era5_df = bilinear_interpolate_era5(ERA5_NC, stations_only)
        if not era5_df.empty:
            frames.append(era5_df)
            print(f"  ERA5 (noi suy Bilinear vao {era5_df['location_id'].nunique()} tram): "
                  f"{len(era5_df):,} dong")

    return pd.concat(frames, ignore_index=True)


def main():
    print("== Buoc 1/3: Parse tat ca nguon diem (GHCN, ISD, NASA POWER, Open-Meteo) ==")
    df = load_all_point_sources()
    print(f"Tong so ban ghi sau parse: {len(df):,}")
    print(df["source"].value_counts().to_string())

    n_before = len(df)
    df = df.dropna(subset=["timestamp_utc", "location_id"])
    n_after = len(df)
    print(f"Loai bo ban ghi thieu khoa chinh: {n_before - n_after} (con lai {n_after:,})")

    df["year"] = df["timestamp_utc"].dt.year

    print("\n== Buoc 2/3: Ghi Parquet qua Spark, partition theo year/source ==")
    from pyspark.sql import SparkSession
    spark = SparkSession.builder.appName("Nhom16-warehouse-build").master("local[*]").getOrCreate()

    sdf = spark.createDataFrame(df)
    out_path = os.path.join(OUT, "weatherobs.parquet")
    sdf.write.mode("overwrite").partitionBy("year", "source").parquet(out_path)
    print(f"Da ghi: {out_path}")

    print("\n== Buoc 3/3: Doc lai kiem tra (dung Spark SQL) ==")
    back = spark.read.parquet(out_path)
    n_read = back.count()
    print(f"So dong doc lai: {n_read:,} (ky vong = {n_after:,}) -> {'KHOP' if n_read == n_after else 'LECH!'}")

    print("\nSHOW PARTITIONS (mau 10 dong dau):")
    partitions = sorted({
        (row["year"], row["source"])
        for row in back.select("year", "source").distinct().collect()
    })
    for p in partitions[:10]:
        print(f"  year={p[0]} source={p[1]}")
    print(f"  ... tong {len(partitions)} partition")

    back.groupBy("source").count().orderBy("source").show()
    spark.stop()
    print("\n== XONG. Warehouse san sang tai warehouse/output/weatherobs.parquet ==")


if __name__ == "__main__":
    main()
