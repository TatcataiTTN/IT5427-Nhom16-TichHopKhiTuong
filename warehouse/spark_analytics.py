#!/usr/bin/env python3
"""
3 phân tích Spark trên warehouse thật (docs/03 Tuần 2, TV3 #3 + #9, TV2 #7):
  1. Ma trận tương quan giữa các biến khí tượng (TV3 #3)
  2. Kiểm tra phân bố partition (data skew) (TV3 #9)
  3. Benchmark hiệu năng đọc có/không partition (TV2 #7)

Chạy:
  JAVA_HOME=$(brew --prefix openjdk@17)/libexec/openjdk.jdk/Contents/Home \
    python3 warehouse/spark_analytics.py
"""
import os
import time

WAREHOUSE = os.path.join(os.path.dirname(__file__), "output", "weatherobs.parquet")
FLAT_COPY = os.path.join(os.path.dirname(__file__), "output", "weatherobs_flat_nopartition.parquet")


def main():
    from pyspark.ml.feature import VectorAssembler
    from pyspark.ml.stat import Correlation
    from pyspark.sql import SparkSession
    import pyspark.sql.functions as F

    spark = SparkSession.builder.appName("Nhom16-spark-analytics").master("local[*]").getOrCreate()
    df = spark.read.parquet(WAREHOUSE)
    df.cache()
    n = df.count()
    print(f"Warehouse: {n:,} dong\n")

    # ---------------- 1. Ma tran tuong quan ----------------
    print("== 1/3: Ma tran tuong quan giua cac bien khi tuong ==")
    num_cols = ["temp_c", "rh_pct", "precip_mm", "wind_speed_ms", "pressure_msl_hpa"]
    clean = df.select(num_cols).na.fill(0.0)
    assembler = VectorAssembler(inputCols=num_cols, outputCol="features")
    vec_df = assembler.transform(clean).select("features")
    corr_matrix = Correlation.corr(vec_df, "features", "pearson").head()[0].toArray()

    print("Bien:", num_cols)
    for i, row in enumerate(corr_matrix):
        print(f"  {num_cols[i]:20s}", [f"{v:+.2f}" for v in row])
    diag_ok = all(abs(corr_matrix[i][i] - 1.0) < 1e-6 for i in range(len(num_cols)))
    sym_ok = (corr_matrix == corr_matrix.T).all()
    print(f"Kiem thu: duong cheo = 1.0? {diag_ok} | doi xung? {sym_ok}\n")

    # ---------------- 2. Data skew theo partition ----------------
    print("== 2/3: Phan bo so ban ghi theo partition (year, source) — kiem tra data skew ==")
    part_counts = (
        df.groupBy("year", "source").count()
        .withColumn("pct", F.round(F.col("count") / n * 100, 2))
        .orderBy(F.desc("count"))
    )
    rows = part_counts.collect()
    top = rows[0]
    print(f"Tong so partition: {len(rows)}")
    print(f"Partition LON NHAT: year={top['year']} source={top['source']} "
          f"-> {top['count']:,} dong ({top['pct']}% tong du lieu)")
    skewed = [r for r in rows if r["pct"] > 50]
    print(f"Kiem thu: co partition nao > 50% tong du lieu? {'CO (' + str(len(skewed)) + ' partition)' if skewed else 'KHONG — dat yeu cau'}")
    print("5 partition lon nhat:")
    for r in rows[:5]:
        print(f"  year={r['year']} source={r['source']}: {r['count']:,} dong ({r['pct']}%)")
    print()

    # ---------------- 3. Benchmark partition vs khong partition ----------------
    print("== 3/3: Benchmark truy van co/khong partition ==")
    # Ghi lai 1 ban khong partition de so sanh cong bang
    if not os.path.exists(FLAT_COPY):
        df.write.mode("overwrite").parquet(FLAT_COPY)

    query_year, query_source = 2024, "ISD"

    t0 = time.time()
    r1 = spark.read.parquet(WAREHOUSE).filter(
        (F.col("year") == query_year) & (F.col("source") == query_source)
    ).count()
    t_partitioned = time.time() - t0

    t0 = time.time()
    r2 = spark.read.parquet(FLAT_COPY).filter(
        (F.col("year") == query_year) & (F.col("source") == query_source)
    ).count()
    t_flat = time.time() - t0

    print(f"Truy van: year={query_year}, source={query_source}")
    print(f"  CO partition (partitionBy year,source):    {t_partitioned:.3f}s, {r1:,} dong")
    print(f"  KHONG partition (doc toan bo roi loc):     {t_flat:.3f}s, {r2:,} dong")
    assert r1 == r2, "LOI: 2 cach doc cho ra so dong khac nhau!"
    speedup = (t_flat / t_partitioned) if t_partitioned > 0 else float("inf")
    print(f"  -> Partition nhanh hon {speedup:.1f}x (Spark dung partition pruning, chi doc "
          f"folder year=2024/source=ISD/ thay vi quet toan bo {n:,} dong)")

    spark.stop()


if __name__ == "__main__":
    main()
