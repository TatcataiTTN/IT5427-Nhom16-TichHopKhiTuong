"""
Thi nghiem mo rong quy mo (docs huong dan 15-11, uu tien 9): do thoi gian truy van dai dien
(trung binh nhiet do theo location_id/thang, nguon GHCN -- cung truy van voi query_optimization.py)
theo 1x/2x/4x/8x kich thuoc du lieu (NHAN BAN that, ghi ro) va theo so core Spark (local[1], local[4],
local[*]), cong them DuckDB lam baseline don may. Moi cau hinh: 1 lan lam nong + 5 lan do, bao cao
trung vi va khoang min-max. Tinh speedup = T(local[1]) / T(local[n]) va hieu suat = speedup / n.

Chay (can JDK 17):
  JAVA_HOME=$(brew --prefix openjdk@17)/libexec/openjdk.jdk/Contents/Home \
    python3 warehouse/scale_benchmark.py
"""
import json
import os
import statistics
import time

import duckdb

WAREHOUSE = os.path.join(os.path.dirname(__file__), "output", "weatherobs.parquet")
OUT_JSON = os.path.join(os.path.dirname(__file__), "output", "scale_benchmark_result.json")
MULTIPLIERS = [1, 2, 4, 8]
N_RUNS = 5


def build_replicated_view(multiplier: int):
    """Tra ve 1 duckdb relation GHCN da nhan ban `multiplier` lan (them cot replica lam khoa gia
    de khong bi coi la ban ghi trung khi groupby, nhung KHONG doi gia tri -- chi nhan ban hang)."""
    base = f"""
    SELECT location_id, timestamp_utc, temp_c
    FROM read_parquet('{WAREHOUSE}/**/*.parquet', hive_partitioning=1)
    WHERE source = 'GHCN'
    """
    if multiplier == 1:
        return base
    parts = [f"SELECT *, {k} AS replica FROM ({base})" for k in range(multiplier)]
    return " UNION ALL ".join(parts)


def time_duckdb(multiplier: int):
    query = f"""
    SELECT location_id, month(timestamp_utc) AS month, avg(temp_c) AS avg_temp_c, count(*) AS n
    FROM ({build_replicated_view(multiplier)})
    GROUP BY location_id, month
    """
    con = duckdb.connect()
    con.execute(query).fetchall()  # warm-up (cache he dieu hanh cho file Parquet)
    times = []
    for _ in range(N_RUNS):
        t0 = time.time()
        con.execute(query).fetchall()
        times.append(time.time() - t0)
    return times


def time_spark(multiplier: int, master: str):
    from pyspark.sql import SparkSession
    import pyspark.sql.functions as F

    spark = (
        SparkSession.builder.appName(f"Nhom16-scale-{multiplier}x-{master}")
        .master(master)
        .config("spark.driver.memory", "4g")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    df = spark.read.parquet(WAREHOUSE).filter(F.col("source") == "GHCN")
    if multiplier > 1:
        df = df.select("location_id", "timestamp_utc", "temp_c")
        replicas = [df] * multiplier
        full = replicas[0]
        for r in replicas[1:]:
            full = full.unionAll(r)
        df = full

    def run_query():
        return (
            df.withColumn("month", F.month("timestamp_utc"))
            .groupBy("location_id", "month")
            .agg(F.avg("temp_c").alias("avg_temp_c"), F.count("*").alias("n"))
        )

    run_query().collect()  # warm-up
    times = []
    for _ in range(N_RUNS):
        t0 = time.time()
        run_query().collect()
        times.append(time.time() - t0)
    spark.stop()
    return times


def summarize(times):
    return {
        "runs": [round(t, 4) for t in times],
        "median": round(statistics.median(times), 4),
        "min": round(min(times), 4),
        "max": round(max(times), 4),
    }


def main():
    results = {}
    n_base = duckdb.sql(
        f"SELECT count(*) FROM read_parquet('{WAREHOUSE}/**/*.parquet', hive_partitioning=1) WHERE source='GHCN'"
    ).fetchall()[0][0]
    print(f"Kich thuoc GHCN goc (1x): {n_base:,} dong")

    for m in MULTIPLIERS:
        print(f"\n=== {m}x ({n_base * m:,} dong, nhan ban) ===")
        results[m] = {}

        for master in ["local[1]", "local[4]", "local[*]"]:
            t = time_spark(m, master)
            results[m][f"spark_{master}"] = summarize(t)
            print(f"Spark {master}: {summarize(t)}")

        t = time_duckdb(m)
        results[m]["duckdb"] = summarize(t)
        print(f"DuckDB: {summarize(t)}")

    # speedup / hieu suat Spark theo so core, tren moi muc du lieu
    for m in MULTIPLIERS:
        t1 = results[m]["spark_local[1]"]["median"]
        for master, n_cores in [("spark_local[4]", 4), ("spark_local[*]", 14)]:
            tn = results[m][master]["median"]
            speedup = t1 / tn if tn > 0 else float("nan")
            results[m][master]["speedup_vs_1core"] = round(speedup, 2)
            results[m][master]["efficiency"] = round(speedup / n_cores, 3)

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump({"n_base_ghcn": n_base, "results": results}, f, indent=2, ensure_ascii=False)
    print(f"\nDa ghi {OUT_JSON}")


if __name__ == "__main__":
    main()
