"""
Unit test cho warehouse/anomaly_detection.py — kiểm thử các hàm thuần trên dữ liệu tổng hợp có đáp án
biết trước (z-score, đợt nóng, SPI, xác nhận chéo đa nguồn).

Chạy: pytest tests/test_anomaly.py -v
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from warehouse.anomaly_detection import (
    anomaly_flag,
    classify_cross_source,
    doy365,
    heatwave_events,
    spi_from_totals,
)


# ---------------------------- Ngày-trong-năm ----------------------------
def test_doy365_aligns_leap_and_normal_years():
    d = pd.Series(pd.to_datetime(["2023-03-01", "2024-03-01", "2024-02-29", "2024-02-28", "2024-12-31"]))
    assert doy365(d).tolist() == [60, 60, 59, 59, 365]


# ---------------------------- Phân loại z ----------------------------
def test_anomaly_flag_thresholds():
    z = pd.Series([0.0, 1.99, 2.0, -2.5, 3.0, -4.0])
    assert list(anomaly_flag(z)) == ["binh_thuong", "binh_thuong", "bat_thuong", "bat_thuong", "cuc_doan", "cuc_doan"]


# ---------------------------- Đợt nóng ----------------------------
def _series(temps, start="2024-04-01", p90=30.0, loc="A"):
    dates = pd.date_range(start, periods=len(temps), freq="D")
    return pd.DataFrame({"location_id": loc, "source": "GHCN", "date": dates.date,
                         "temp_mean": temps, "clim_p90": p90})


def test_heatwave_needs_three_consecutive_hot_days():
    df = _series([31, 31, 29, 31, 31, 31, 29])  # đợt 2 ngày (không đủ) + đợt 3 ngày
    ev = heatwave_events(df)
    assert len(ev) == 1
    assert str(ev.loc[0, "start"]) == "2024-04-04" and ev.loc[0, "days"] == 3


def test_heatwave_bridges_single_missing_day_but_not_cool_day():
    # 2 ngày nóng, 1 ngày THIẾU dữ liệu, 2 ngày nóng -> 1 đợt 4 ngày nóng, dài 5 ngày theo lịch
    df = _series([31, 31, np.nan, 31, 31])
    ev = heatwave_events(df)
    assert len(ev) == 1 and ev.loc[0, "days"] == 4 and ev.loc[0, "span_days"] == 5
    # Cùng mẫu nhưng ngày giữa CÓ dữ liệu và mát -> đứt thành 2 đợt 2 ngày -> không có đợt nào đủ 3 ngày
    assert heatwave_events(_series([31, 31, 28, 31, 31])).empty


def test_heatwave_does_not_join_different_stations():
    df = pd.concat([_series([31, 31]), _series([31, 31], start="2024-04-03", loc="B")])
    assert heatwave_events(df).empty


# ---------------------------- SPI ----------------------------
def test_spi_on_gamma_sample_is_standard_normal():
    rng = np.random.default_rng(0)
    base = pd.Series(rng.gamma(shape=2.0, scale=50.0, size=3000))
    spi = spi_from_totals(base, base)
    assert abs(spi.mean()) < 0.05 and abs(spi.std() - 1) < 0.05


def test_spi_sign_and_zero_rain_handling():
    rng = np.random.default_rng(1)
    vals = rng.gamma(2.0, 50.0, size=40)
    vals[:8] = 0.0  # 20% tháng không mưa
    base = pd.Series(vals)
    spi = spi_from_totals(pd.Series([0.0, float(np.median(vals[8:])), 600.0]), base)
    assert spi.iloc[0] < -0.5          # tháng không mưa -> khô
    assert spi.iloc[2] > 2             # tháng mưa rất nhiều -> ẩm bất thường
    assert spi.iloc[0] < spi.iloc[1] < spi.iloc[2]


def test_spi_requires_enough_baseline_years():
    assert spi_from_totals(pd.Series([10.0]), pd.Series([5.0] * 10)).isna().all()


# ---------------------------- Xác nhận chéo trạm vs ERA5 ----------------------------
def test_classify_cross_source():
    z_st = pd.Series([2.5, 3.5, -3.2, 2.2, 2.4])
    z_e5 = pd.Series([1.8, 0.1, 1.5, 0.6, np.nan])
    assert list(classify_cross_source(z_st, z_e5)) == [
        "xac_nhan_khi_hau",   # cùng chiều, ERA5 cũng lệch rõ
        "nghi_loi_du_lieu",   # trạm cực đoan, ERA5 bình thường
        "nghi_loi_du_lieu",   # trạm cực đoan lạnh, ERA5 ngược chiều
        "chua_xac_dinh",      # trạm bất thường vừa, ERA5 lệch nhẹ
        "khong_co_era5",
    ]
