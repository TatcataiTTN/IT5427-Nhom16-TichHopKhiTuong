#!/usr/bin/env python3
"""
3 phân tích Spark trên warehouse thật (docs/03 Tuần 2, TV3 #3 + #9, TV2 #7):
  1. Ma trận tương quan giữa các biến khí tượng (TV3 #3)
  2. Kiểm tra phân bố partition (data skew) (TV3 #9)
  3. Benchmark hiệu năng đọc có/không partition (TV2 #7)

Chạy:
  python3 warehouse/spark_analytics.py   (can JAVA_HOME tro toi JDK 17/21, xem README)
"""
import os
import time

WAREHOUSE = os.path.join(os.path.dirname(__file__), "output", "weatherobs.parquet")
FLAT_COPY = os.path.join(os.path.dirname(__file__), "output", "weatherobs_flat_nopartition.parquet")


def main():
    import numpy as np
    from pyspark.sql import SparkSession
    import pyspark.sql.functions as F

    spark = (SparkSession.builder.appName("Nhom16-spark-analytics").master("local[*]")
             .config("spark.sql.session.timeZone", "UTC").config("spark.driver.memory", "4g").getOrCreate())
    df = spark.read.parquet(WAREHOUSE)
    df.cache()
    n = df.count()
    print(f"Warehouse: {n:,} dong\n")

    # ---------------- 1. Ma tran tuong quan ----------------
    print("== 1/3: Ma tran tuong quan giua cac bien khi tuong ==")
    num_cols = ["temp_c", "rh_pct", "precip_mm", "wind_speed_ms", "pressure_msl_hpa"]
    # Tuong quan Pearson TUNG CAP, chi tren dong co du ca 2 bien (pairwise deletion).
    # KHONG fill NaN = 0: moi nguon thieu bien khac nhau (ERA5 khong co RH, ISD khong co mua,
    # NASA POWER khong co ap suat MSL), fill 0 se tao tuong quan gia do "cung bi thieu".
    k = len(num_cols)
    corr_matrix = np.eye(k)
    pair_n = np.zeros((k, k), dtype=int)
    for i in range(k):
        for j in range(i + 1, k):
            pair = df.select(num_cols[i], num_cols[j]).na.drop()
            corr_matrix[i, j] = corr_matrix[j, i] = pair.stat.corr(num_cols[i], num_cols[j])
            pair_n[i, j] = pair_n[j, i] = pair.count()

    print("Bien:", num_cols)
    for i, row in enumerate(corr_matrix):
        print(f"  {num_cols[i]:20s}", [f"{v:+.2f}" for v in row])
    print(f"So dong dung cho moi cap: {pair_n[np.triu_indices(k, 1)].min():,} -> "
          f"{pair_n[np.triu_indices(k, 1)].max():,}")
    diag_ok = all(abs(corr_matrix[i][i] - 1.0) < 1e-6 for i in range(k))
    sym_ok = np.allclose(corr_matrix, corr_matrix.T)
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
    # Ghi lai 1 ban KHONG partition tu CHINH warehouse hien tai (ghi de moi lan chay de 2 ban
    # luon cung du lieu — neu chi ghi khi chua co, se so voi ban cu sau khi warehouse thay doi)
    df.write.mode("overwrite").parquet(FLAT_COPY)

    query_year, query_source = 2024, "ISD"

    def timed_count(path, repeats=5):
        """Chay 1 lan lam nong (JIT/cache metadata cua JVM) roi lay trung vi cua nhieu lan do."""
        q = lambda: spark.read.parquet(path).filter(
            (F.col("year") == query_year) & (F.col("source") == query_source)).count()
        rows = q()
        times = []
        for _ in range(repeats):
            t0 = time.time()
            q()
            times.append(time.time() - t0)
        return rows, sorted(times)[len(times) // 2]

    r1, t_partitioned = timed_count(WAREHOUSE)
    r2, t_flat = timed_count(FLAT_COPY)

    print(f"Truy van: year={query_year}, source={query_source} (trung vi 5 lan, sau 1 lan lam nong)")
    print(f"  CO partition (partitionBy year,source):    {t_partitioned:.3f}s, {r1:,} dong")
    print(f"  KHONG partition (doc toan bo roi loc):     {t_flat:.3f}s, {r2:,} dong")
    assert r1 == r2, "LOI: 2 cach doc cho ra so dong khac nhau!"
    ratio = t_flat / t_partitioned if t_partitioned > 0 else float("inf")
    if ratio >= 1:
        print(f"  -> Partition nhanh hon {ratio:.1f}x (partition pruning: chi doc thu muc "
              f"year={query_year}/source={query_source}/ thay vi quet toan bo {n:,} dong)")
    else:
        print(f"  -> Partition CHAM hon {1 / ratio:.1f}x (chi phi liet ke nhieu thu muc partition "
              f"lon hon loi ich pruning o quy mo du lieu nay)")

    spark.stop()


if __name__ == "__main__":
    main()
