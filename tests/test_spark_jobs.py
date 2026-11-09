"""
Smoke test cho cac script Spark that (chay subprocess, can JAVA_HOME Java 17+ - xem README
muc 6b). Danh dau "slow" vi moi test khoi dong 1 SparkSession that.

Chay: pytest tests/test_spark_jobs.py -v -m slow
"""
import os
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
pytestmark = pytest.mark.slow

WAREHOUSE_EXISTS = os.path.exists(os.path.join(ROOT, "warehouse", "output", "weatherobs.parquet"))


def _java17_home():
    brew = shutil.which("brew")
    if not brew:
        return None
    try:
        prefix = subprocess.run([brew, "--prefix", "openjdk@17"], capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return None
    candidate = os.path.join(prefix, "libexec", "openjdk.jdk", "Contents", "Home")
    return candidate if os.path.isdir(candidate) else None


def _run_spark_script(script, timeout=180):
    env = os.environ.copy()
    java_home = _java17_home()
    if java_home:
        env["JAVA_HOME"] = java_home
    return subprocess.run(
        [sys.executable, os.path.join(ROOT, script)],
        capture_output=True, text=True, timeout=timeout, cwd=ROOT, env=env,
    )


@pytest.mark.skipif(not WAREHOUSE_EXISTS, reason="warehouse/output/weatherobs.parquet chua duoc build")
def test_query_optimization_cache_speeds_up_and_passes_threshold():
    r = _run_spark_script("warehouse/query_optimization.py")
    assert r.returncode == 0, f"Script loi:\n{r.stdout[-3000:]}\n{r.stderr[-3000:]}"
    assert "PASS" in r.stdout or "KET QUA THAT" in r.stdout


def _kafka_broker_reachable(host="localhost", port=9092, timeout=2):
    import socket
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


@pytest.mark.skipif(not WAREHOUSE_EXISTS, reason="warehouse/output/weatherobs.parquet chua duoc build")
@pytest.mark.skipif(not _kafka_broker_reachable(), reason="Kafka broker khong chay (docker compose -f docker-compose.kafka.yml up -d)")
def test_spark_structured_streaming_reads_kafka_and_windows_real_data():
    # Phat du lieu that vao topic truoc khi doc streaming
    produce = subprocess.run(
        [sys.executable, os.path.join(ROOT, "ingestion", "kafka_producer.py"), "--limit", "30", "--speed", "0"],
        capture_output=True, text=True, timeout=30, cwd=ROOT,
    )
    assert produce.returncode == 0, f"Producer loi:\n{produce.stdout}\n{produce.stderr}"

    env = os.environ.copy()
    java_home = _java17_home()
    if java_home:
        env["JAVA_HOME"] = java_home
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "warehouse", "spark_streaming_consumer.py"), "--topic", "weatherobs.ghcn", "--duration", "15"],
        capture_output=True, text=True, timeout=60, cwd=ROOT, env=env,
    )
    assert r.returncode == 0, f"Script loi:\n{r.stdout[-3000:]}\n{r.stderr[-3000:]}"
    assert "PASS" in r.stdout
    assert "avg_temp_c" in r.stdout, "Khong thay cot ket qua window trong output"


CLIMATOLOGY_EXISTS = os.path.exists(os.path.join(ROOT, "warehouse", "output", "climatology.parquet"))


@pytest.mark.skipif(not (WAREHOUSE_EXISTS and CLIMATOLOGY_EXISTS),
                    reason="can warehouse + climatology.parquet (chay warehouse/anomaly_detection.py)")
@pytest.mark.skipif(not _kafka_broker_reachable(), reason="Kafka broker khong chay (docker compose -f docker-compose.kafka.yml up -d)")
def test_streaming_anomaly_detects_april_2024_heat_like_batch(tmp_path):
    import uuid
    import pandas as pd
    topic = f"weatherobs.test.{uuid.uuid4().hex[:8]}"  # topic moi -> khong lan offset cu
    produce = subprocess.run(
        [sys.executable, os.path.join(ROOT, "ingestion", "kafka_producer.py"), "--source", "GHCN",
         "--start", "2024-04-28", "--end", "2024-04-30", "--limit", "0", "--topic", topic],
        capture_output=True, text=True, timeout=120, cwd=ROOT,
    )
    assert produce.returncode == 0, f"Producer loi:\n{produce.stdout}\n{produce.stderr}"

    env = os.environ.copy()
    java_home = _java17_home()
    if java_home:
        env["JAVA_HOME"] = java_home
    out = tmp_path / "alerts.parquet"
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "warehouse", "spark_streaming_anomaly.py"), "--topic", topic,
         "--duration", "40", "--output", str(out)],
        capture_output=True, text=True, timeout=180, cwd=ROOT, env=env,
    )
    assert r.returncode == 0, f"Script loi:\n{r.stdout[-3000:]}\n{r.stderr[-3000:]}"
    assert "PASS" in r.stdout
    alerts = pd.read_parquet(out)
    hit = alerts[(alerts["location_id"] == "THW00041018") & (alerts["date"].astype(str) == "2024-04-30")]
    assert len(hit) == 1 and hit["z"].iloc[0] > 3, "Phai bat duoc ngay nong cuc doan 30/4/2024 (z ~ +3,5)"
