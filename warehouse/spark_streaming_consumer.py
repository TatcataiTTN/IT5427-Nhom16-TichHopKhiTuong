#!/usr/bin/env python3
"""
Spark Structured Streaming doc tu Kafka topic va tinh aggregate theo cua so thoi gian
(docs/03 Tuan 2 TV3 #2 + TV1 #9). Da chay LIVE thanh cong that 09/11/2026 sau khi Docker Desktop
len duoc lan thu 2 - xem docs/14 muc cap nhat cho bang ket qua window that.

Doc topic "weatherobs.ghcn" (ghi boi ingestion/kafka_producer.py), tinh nhiet do trung binh
theo cua so 1 phut truot moi 30 giay (tumbling/sliding window tren processing time, vi du lieu
"replay" khong co watermark thuc te dang tin cay).

CAN: Kafka broker + 1 topic co du lieu that truoc khi chay (xem docker-compose.kafka.yml +
ingestion/kafka_producer.py). Can goi JAR connector Kafka cho Spark (tu dong tai qua --packages,
da tu dong khop dung version PySpark dang cai de tranh NoSuchMethodError).

2 bug moi that da gap + sua khi chay live lan dau (09/11/2026):
  1. SparkContext local[*] that bai khi khoi tao do Spark tu phan giai hostname ra IP LAN that
     (vd 192.168.1.168) thay vi localhost - rat co the do mang ao cua Docker Desktop (vpnkit/
     gVisor) vua khoi dong lai gay xung dot route. Sua bang bien moi truong SPARK_LOCAL_IP=127.0.0.1.
  2. Kafka connector ghim cung version "4.0.0" nhung may that chay PySpark 4.2.0 -> binary
     khong tuong thich, loi "NoSuchMethodError: SerializedOffset.<init>". Sua bang cach lay
     version PySpark dang cai that (pyspark.__version__) thay vi ghim cung so.

Chay:
  JAVA_HOME=$(brew --prefix openjdk@17)/libexec/openjdk.jdk/Contents/Home \
  SPARK_LOCAL_IP=127.0.0.1 \
    python3 warehouse/spark_streaming_consumer.py --topic weatherobs.ghcn --duration 30
"""
import argparse
import os

# Fallback neu nguoi dung quen set env var: tranh loi SparkContext khoi tao that bai do
# hostname resolve ra IP LAN that thay vi localhost (xem docstring, bug that da gap 09/11/2026).
os.environ.setdefault("SPARK_LOCAL_IP", "127.0.0.1")

SCHEMA_FIELDS = [
    "location_id", "timestamp_utc", "temp_c", "rh_pct", "dewpoint_c", "precip_mm",
    "wind_speed_ms", "wind_dir_deg", "pressure_surface_hpa", "pressure_msl_hpa",
    "solar_rad_wm2", "cloud_cover_pct", "soil_temp_c", "soil_moist_m3m3", "year", "source",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap", default="localhost:9092")
    parser.add_argument("--topic", default="weatherobs.ghcn")
    parser.add_argument("--duration", type=int, default=30, help="Giay chay streaming truoc khi dung (demo)")
    args = parser.parse_args()

    from pyspark.sql import SparkSession
    from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType
    import pyspark.sql.functions as F

    import pyspark
    spark_version = pyspark.__version__  # connector phai KHOP dung version PySpark dang cai
    # (vd Spark 4.0.0 vs 4.2.0 khong tuong thich nhi phan -- da tung gap NoSuchMethodError
    # tren SerializedOffset khi ghim cung 4.0.0 trong luc may that chay PySpark 4.2.0)
    spark = (
        SparkSession.builder.appName("Nhom16-streaming-windowing")
        .master("local[*]")
        .config("spark.jars.packages", f"org.apache.spark:spark-sql-kafka-0-10_2.13:{spark_version}")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    schema = StructType([
        StructField("location_id", StringType()),
        StructField("timestamp_utc", StringType()),
        StructField("temp_c", DoubleType()),
        StructField("rh_pct", DoubleType()),
        StructField("dewpoint_c", DoubleType()),
        StructField("precip_mm", DoubleType()),
        StructField("wind_speed_ms", DoubleType()),
        StructField("wind_dir_deg", DoubleType()),
        StructField("pressure_surface_hpa", DoubleType()),
        StructField("pressure_msl_hpa", DoubleType()),
        StructField("solar_rad_wm2", DoubleType()),
        StructField("cloud_cover_pct", DoubleType()),
        StructField("soil_temp_c", DoubleType()),
        StructField("soil_moist_m3m3", DoubleType()),
        StructField("year", IntegerType()),
        StructField("source", StringType()),
    ])

    raw = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", args.bootstrap)
        .option("subscribe", args.topic)
        .option("startingOffsets", "earliest")
        .load()
    )

    parsed = raw.select(F.from_json(F.col("value").cast("string"), schema).alias("data")).select("data.*")
    parsed = parsed.withColumn("event_time", F.current_timestamp())  # processing-time window (replay khong co watermark goc dang tin cay)

    windowed = (
        parsed.groupBy(F.window("event_time", "1 minute", "30 seconds"), "location_id")
        .agg(F.avg("temp_c").alias("avg_temp_c"), F.count("*").alias("n_messages"))
    )

    query = (
        windowed.writeStream.outputMode("update")
        .format("console")
        .option("truncate", False)
        .trigger(processingTime="5 seconds")
        .start()
    )

    print(f"Streaming dang chay, doc topic '{args.topic}', se tu dung sau {args.duration}s (demo)...")
    query.awaitTermination(timeout=args.duration)
    query.stop()
    print("PASS — streaming da chay va dung dung theo thoi gian demo, xem output cua so o tren.")
    spark.stop()


if __name__ == "__main__":
    main()
