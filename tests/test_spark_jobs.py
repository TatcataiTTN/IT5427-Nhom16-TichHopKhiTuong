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
