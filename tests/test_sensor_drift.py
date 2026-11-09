"""
Unit test cho warehouse/sensor_drift.py — kiểm định Pettitt, phát hiện trôi/nhảy bậc trên chuỗi bias
tổng hợp (tiêu chí docs/03 Tuần 3 TV1 #3: so với trạm biết trước có vấn đề hoặc mô phỏng).

Chạy: pytest tests/test_sensor_drift.py -v
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from warehouse.sensor_drift import detect_drift, monthly_bias, pettitt_test


def _bias(values, start="2015-01", loc="S1", source="ISD"):
    months = pd.period_range(start, periods=len(values), freq="M")
    return pd.DataFrame({"location_id": loc, "source": source, "month": months, "bias": values})


def test_pettitt_finds_step_position():
    rng = np.random.default_rng(0)
    x = np.concatenate([rng.normal(0, 0.2, 40), rng.normal(1.5, 0.2, 40)])
    r = pettitt_test(x)
    assert r["p"] < 0.01 and abs(r["cp"] - 39) <= 1


def test_pettitt_no_step_in_noise():
    assert pettitt_test(np.random.default_rng(1).normal(0, 1, 80))["p"] > 0.05


def test_detect_drift_flags_step_drift_and_stable():
    rng = np.random.default_rng(2)
    noise = rng.normal(0, 0.15, 72)
    stable = detect_drift(_bias(noise), "temp_mean")
    step = detect_drift(_bias(noise + np.where(np.arange(72) >= 36, 1.0, 0)), "temp_mean")
    drift = detect_drift(_bias(noise + 0.6 * np.arange(72) / 12), "temp_mean")
    assert stable["flag"].iloc[0] == "on_dinh"
    assert step["flag"].iloc[0] in ("nhay_bac", "troi_dan") and step["change_month"].iloc[0] == "2018-01"
    assert drift["flag"].iloc[0] == "troi_dan" and abs(drift["drift_per_year"].iloc[0] - 0.6) < 0.1


def test_detect_drift_ignores_statistically_significant_but_tiny_changes():
    # Bước 0,1°C rất rõ về thống kê (nhiễu nhỏ) nhưng dưới ngưỡng vật lý 0,5°C -> không gắn cờ
    x = np.concatenate([np.full(36, 0.0), np.full(36, 0.1)]) + np.random.default_rng(3).normal(0, 0.01, 72)
    assert detect_drift(_bias(x), "temp_mean")["flag"].iloc[0] == "on_dinh"


def test_monthly_bias_pairs_station_with_era5_same_location_and_day():
    dates = pd.date_range("2020-01-01", "2020-01-31", freq="D")
    st = pd.DataFrame({"location_id": "S1", "source": "ISD", "date": dates, "temp_mean": 30.0})
    e5 = pd.DataFrame({"location_id": "S1", "source": "ERA5", "date": dates, "temp_mean": 28.5})
    other = pd.DataFrame({"location_id": "S2", "source": "ERA5", "date": dates, "temp_mean": 0.0})
    b = monthly_bias(pd.concat([st, e5, other]), "temp_mean")
    assert len(b) == 1 and abs(b["bias"].iloc[0] - 1.5) < 1e-12 and b["n_days"].iloc[0] == 31
