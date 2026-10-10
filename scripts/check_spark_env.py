#!/usr/bin/env python3
"""
Kiểm tra môi trường Spark cục bộ thật (không phải chỉ import).

Chạy (macOS + Homebrew, PySpark 4.x cần Java 17+, KHÔNG dùng Java 11):
  JAVA_HOME=$(brew --prefix openjdk@17)/libexec/openjdk.jdk/Contents/Home python3 scripts/check_spark_env.py

Lưu ý: `/usr/libexec/java_home -v 17` có thể ÂM THẦM trả về bản Java 11 nếu
openjdk@17 cài qua brew nhưng chưa symlink vào /Library/Java/JavaVirtualMachines
(brew cài openjdk@17 ở dạng keg-only). Dùng `brew --prefix openjdk@17` cho chắc,
hoặc symlink 1 lần: sudo ln -sfn $(brew --prefix openjdk@17)/libexec/openjdk.jdk \
/Library/Java/JavaVirtualMachines/openjdk-17.jdk (sau đó mới dùng java_home -v 17 được).
(Linux: export JAVA_HOME tới thư mục JDK 17/21 trước khi chạy)
"""
import sys

try:
    from pyspark.sql import SparkSession
except ImportError:
    print("LOI: chua cai pyspark. Chay: pip install pyspark")
    sys.exit(1)

try:
    spark = SparkSession.builder.appName("Nhom16-env-check").master("local[*]").getOrCreate()
except Exception as e:
    print(f"LOI khi khoi dong Spark: {e}")
    print("Goi y: PySpark 4.x can Java 17+. Kiem tra: java -version")
    print("Neu may co nhieu ban Java, set JAVA_HOME truoc khi chay script nay.")
    sys.exit(1)

n = spark.range(1000).count()
print(f"OK: Spark {spark.version} khoi dong thanh cong, spark.range(1000).count() = {n}")

df = spark.createDataFrame([(1, "test"), (2, "ok")], ["id", "value"])
df.write.mode("overwrite").parquet("/tmp/nhom16_spark_check.parquet")
back = spark.read.parquet("/tmp/nhom16_spark_check.parquet")
print(f"OK: Parquet roundtrip, {back.count()} dong (ky vong 2)")

spark.stop()
print("\n== Moi truong Spark san sang. ==")
