#!/usr/bin/env python3
"""
Phát hiện dị thường khí hậu THEO LUỒNG: Spark Structured Streaming đọc bản ghi từ Kafka, đối chiếu
từng bản ghi với khí hậu nền đã tính sẵn (batch, warehouse/anomaly_detection.py) và phát cảnh báo
ngay trong micro-batch — kết hợp Replay Streaming (Kafka) với phát hiện dị thường (batch).

Luồng:
  ingestion/kafka_producer.py --source GHCN --start ... --end ... --topic <topic>
      -> Kafka -> Spark readStream (maxOffsetsPerTrigger: phát dần để cảnh báo xuất hiện theo thời gian)
      -> foreachBatch: join tĩnh với climatology.parquet theo (vị trí, nguồn, ngày-trong-năm)
      -> z = (nhiệt độ − TB nền) / ĐLC nền; |z| >= 2 -> cảnh báo
      -> console + warehouse/output/stream_alerts.parquet
Dùng nguồn GHCN (bản ghi theo ngày, nền chuẩn WMO 1991–2020) nên mỗi bản ghi so trực tiếp được với
khí hậu nền theo ngày, không cần gom cửa sổ.

Chạy (cần Kafka broker + climatology.parquet):
  python3 ingestion/kafka_producer.py --source GHCN --start 2024-04-01 --end 2024-05-15 --limit 0 \\
      --topic weatherobs.ghcn.replay
  python3 warehouse/spark_streaming_anomaly.py --topic weatherobs.ghcn.replay --duration 60
"""
import argparse
import os
import shutil
import sys
import tempfile
import time

# Tránh SparkContext phân giải hostname ra IP LAN (lỗi môi trường đã gặp, xem spark_streaming_consumer.py)
os.environ.setdefault("SPARK_LOCAL_IP", "127.0.0.1")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

OUT = os.path.join(os.path.dirname(__file__), "output")
CLIMATOLOGY = os.path.join(OUT, "climatology.parquet")
ALERTS = os.path.join(OUT, "stream_alerts.parquet")
Z_ALERT = 2.0


def score_batch(batch, clim):
    """Micro-batch (bản ghi GHCN đã parse) -> bảng có z và mức cảnh báo. Hàm thuần Spark, dùng lại
    được cho DataFrame tĩnh (test) lẫn micro-batch của luồng."""
    from pyspark.sql import functions as F
    from warehouse.anomaly_detection import spark_doy
    b = (batch.filter(F.col("temp_c").isNotNull())
         .withColumn("date", F.to_date(F.substring("timestamp_utc", 1, 10)))
         .withColumn("doy", spark_doy("date")))
    c = clim.filter(F.col("var") == "temp_mean").select("location_id", "source", "doy", "clim_mean", "clim_std", "clim_p90")
    z = (F.col("temp_c") - F.col("clim_mean")) / F.col("clim_std")
    return (b.join(F.broadcast(c), ["location_id", "source", "doy"], "inner")
            .withColumn("z", z)
            .withColumn("muc", F.when(F.abs(F.col("z")) >= 3, "cuc_doan")
                        .when(F.abs(F.col("z")) >= Z_ALERT, "bat_thuong").otherwise("binh_thuong"))
            .select("location_id", "source", "date", "temp_c", "clim_mean", "clim_p90", "z", "muc"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap", default="localhost:9092")
    parser.add_argument("--topic", default="weatherobs.ghcn.replay")
    parser.add_argument("--duration", type=int, default=60, help="Giây chạy trước khi dừng (demo)")
    parser.add_argument("--per-batch", type=int, default=150, help="Số message tối đa mỗi micro-batch")
    parser.add_argument("--output", default=ALERTS)
    args = parser.parse_args()

    if not os.path.exists(CLIMATOLOGY):
        sys.exit("Chua co climatology.parquet - chay truoc: python3 warehouse/anomaly_detection.py")

    import pyspark
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as F
    from pyspark.sql.types import DoubleType, StringType, StructField, StructType

    spark = (SparkSession.builder.appName("Nhom16-streaming-anomaly").master("local[*]")
             .config("spark.jars.packages", f"org.apache.spark:spark-sql-kafka-0-10_2.13:{pyspark.__version__}")
             .config("spark.sql.session.timeZone", "UTC")
             .config("spark.sql.shuffle.partitions", "4")
             .getOrCreate())
    spark.sparkContext.setLogLevel("WARN")
    clim = spark.read.parquet(CLIMATOLOGY).cache()
    clim.count()

    schema = StructType([StructField("location_id", StringType()), StructField("timestamp_utc", StringType()),
                         StructField("source", StringType()), StructField("temp_c", DoubleType())])
    stream = (spark.readStream.format("kafka")
              .option("kafka.bootstrap.servers", args.bootstrap)
              .option("subscribe", args.topic)
              .option("startingOffsets", "earliest")
              .option("maxOffsetsPerTrigger", args.per_batch)
              .load()
              .select(F.from_json(F.col("value").cast("string"), schema).alias("d")).select("d.*"))

    shutil.rmtree(args.output, ignore_errors=True)
    totals = {"records": 0, "alerts": 0, "batches": 0}

    def handle(batch, batch_id):
        scored = score_batch(batch, clim).cache()
        n = scored.count()
        alerts = scored.filter(F.col("muc") != "binh_thuong")
        n_alert = alerts.count()
        totals["records"] += n
        totals["alerts"] += n_alert
        totals["batches"] += 1
        if n == 0:
            return
        days = scored.agg(F.min("date"), F.max("date")).first()
        print(f"[batch {batch_id}] {n} ban ghi ({days[0]} -> {days[1]}) | {n_alert} canh bao "
              f"| luy ke {totals['alerts']}/{totals['records']}", flush=True)
        if n_alert:
            alerts.withColumn("batch_id", F.lit(batch_id)).withColumn("phat_hien_luc", F.current_timestamp()) \
                .write.mode("append").parquet(args.output)
            for r in alerts.orderBy(F.desc(F.abs("z"))).limit(3).collect():
                print(f"    CANH BAO {r['muc']:<10} {r['location_id']} {r['date']}: {r['temp_c']:.1f}°C "
                      f"(nen {r['clim_mean']:.1f}°C, z = {r['z']:+.2f})", flush=True)
        scored.unpersist()

    ckpt = tempfile.mkdtemp(prefix="nhom16-stream-anomaly-")
    query = (stream.writeStream.foreachBatch(handle).option("checkpointLocation", ckpt)
             .trigger(processingTime="3 seconds").start())
    print(f"Streaming phat hien di thuong: topic '{args.topic}', {args.per_batch} message/micro-batch, "
          f"dung sau {args.duration}s...", flush=True)
    t0 = time.time()
    query.awaitTermination(timeout=args.duration)
    query.stop()
    shutil.rmtree(ckpt, ignore_errors=True)
    print(f"\nXONG sau {time.time() - t0:.0f}s: {totals['batches']} micro-batch, {totals['records']} ban ghi, "
          f"{totals['alerts']} canh bao -> {args.output}")
    if totals["records"] > 0:
        print("PASS")
    spark.stop()


if __name__ == "__main__":
    main()
