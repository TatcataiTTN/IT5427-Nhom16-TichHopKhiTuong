#!/usr/bin/env python3
"""
Xu ly data skew thuc te (docs/03 Tuan 3, TV2 #6 + TV3 #7): thu them "month" vao partition key
(year/source -> year/month/source) de giam skew cua partition lon nhat (year=2024,source=ISD,
33,28% - gan nguong 50% da dat Tuan 2 nhung van cao).

Chay:
  JAVA_HOME=$(brew --prefix openjdk@17)/libexec/openjdk.jdk/Contents/Home \
    python3 warehouse/skew_repartition_analysis.py
"""
import os

WAREHOUSE = os.path.join(os.path.dirname(__file__), "output", "weatherobs.parquet")


def main():
    from pyspark.sql import SparkSession
    import pyspark.sql.functions as F

    spark = SparkSession.builder.appName("Nhom16-skew-repartition").master("local[*]").getOrCreate()
    df = spark.read.parquet(WAREHOUSE).withColumn("month", F.month("timestamp_utc"))
    total = df.count()
    print(f"Tong so dong: {total:,}\n")

    print("== Partition HIEN TAI (year/source, 88 partition) ==")
    g1 = df.groupBy("year", "source").count().toPandas()
    g1["pct"] = g1["count"] / total * 100
    max1 = g1["pct"].max()
    print(f"So partition: {len(g1)} | Partition lon nhat: {max1:.2f}% "
          f"({g1.loc[g1['pct'].idxmax(), 'year']}, {g1.loc[g1['pct'].idxmax(), 'source']})")

    print("\n== Partition THU NGHIEM (them 'month': year/month/source) ==")
    g2 = df.groupBy("year", "month", "source").count().toPandas()
    g2["pct"] = g2["count"] / total * 100
    max2 = g2["pct"].max()
    print(f"So partition: {len(g2)} | Partition lon nhat: {max2:.2f}%")

    skew_improvement_pct = (max1 - max2) / max1 * 100
    file_count_increase_x = len(g2) / len(g1)

    print(f"\n--- Danh gia danh doi (trade-off), bao cao trung thuc ---")
    print(f"Giam skew: {max1:.2f}% -> {max2:.2f}% (giam {skew_improvement_pct:.1f}%, "
          f"{'DAT' if max2 < 30 else 'CHUA DAT'} nguong <30% yeu cau)")
    print(f"Nhung so partition tang {file_count_increase_x:.1f}x ({len(g1)} -> {len(g2)}) - "
          f"lam nang them van de 'small-file problem' da ghi nhan o docs/10 muc 2 (partition "
          f"nhieu thu muc nho da lam cham truy van ~2,2 lan o muc 88 partition). Them 'month' giam "
          f"skew that nhung co the lam van de do CHAM HON, khong phai nhanh hon.")
    print(f"\nKhuyen nghi: KHONG doi partition key ngay bay gio - skew hien tai (33,28%) van duoi "
          f"nguong an toan 50% da thong nhat Tuan 2; doi key se can benchmark lai ca 2 chieu (skew "
          f"VA toc do doc) truoc khi ap dung, uu tien lam khi du lieu du lon de loi ich partition "
          f"pruning that su vuot qua overhead (ERA5 full 5 nam).")

    print(f"\nPASS (phan tich hoan tat, {len(g1)} vs {len(g2)} partition da so sanh)")
    spark.stop()


if __name__ == "__main__":
    main()
