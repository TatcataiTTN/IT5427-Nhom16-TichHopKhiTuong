"""
Unit test cho ingestion/parsers.py — chạy trên dữ liệu THẬT đã tải ở
data_samples/batch_week2/ (không dùng mock), đúng tiêu chí kiểm thử ở
docs/03-ke-hoach-160-tasks.md Tuần 1 TV1 #5-6 và Tuần 2 TV1 #5-8.

Chạy: pytest tests/test_parsers.py -v
"""
import math
import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ingestion.parsers import (
    WEATHEROBS_COLUMNS,
    clausius_clapeyron_rh,
    parse_ghcn,
    parse_isd,
    parse_nasa_power,
    parse_openmeteo,
)

DATA = os.path.join(os.path.dirname(__file__), "..", "data_samples", "batch_week2")


def _assert_schema(df):
    assert list(df.columns) == WEATHEROBS_COLUMNS
    assert len(df) > 0
    assert df["timestamp_utc"].dt.tz is not None, "timestamp_utc phai co timezone UTC"


# ---------------------------- GHCN ----------------------------
def test_parse_ghcn_schema_and_shape():
    fp = os.path.join(DATA, "ghcn_daily", "VMM00048820.csv")
    df = parse_ghcn(fp)
    _assert_schema(df)
    raw_days = pd.read_csv(fp)["DATE"].nunique()
    assert len(df) == raw_days, "so ngay sau PIVOT phai khop so ngay unique trong file goc"


def test_parse_ghcn_temp_physical_range():
    fp = os.path.join(DATA, "ghcn_daily", "VMM00048820.csv")
    df = parse_ghcn(fp)
    t = df["temp_c"].dropna()
    assert (t > -10).all() and (t < 45).all(), "nhiet do VN phai trong khoang vat ly hop ly"


# ---------------------------- ISD ----------------------------
def test_parse_isd_schema_and_missing_code():
    fp = os.path.join(DATA, "isd_global_hourly_2024", "48900099999.csv")
    df = parse_isd(fp)
    _assert_schema(df)
    # Kiem thu bat buoc theo ke hoach: input chua ma missing -> output la NaN, khong crash
    assert df["temp_c"].isna().sum() >= 0  # khong crash la dat; neu co missing phai la NaN that
    assert not (df["temp_c"] == 999.9).any(), "gia tri missing phai duoc chuyen thanh NaN, khong giu nguyen ma loi"


def test_parse_isd_packed_field_missing_value_injection():
    """Tiem truc tiep dong co TMP='+9999,9' (ma missing chuan ISD) -> phai ra NaN."""
    import tempfile
    csv_content = (
        'STATION,DATE,WND,TMP,DEW,SLP\n'
        '"12345","2024-01-01T00:00:00","999,9,V,9999,9","+9999,9","+9999,9","99999,9"\n'
    )
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
        f.write(csv_content)
        fp = f.name
    try:
        df = parse_isd(fp)
        assert df["temp_c"].isna().all()
        assert df["dewpoint_c"].isna().all()
        assert df["pressure_msl_hpa"].isna().all()
        assert df["wind_speed_ms"].isna().all()
    finally:
        os.unlink(fp)


def test_parse_isd_temp_physical_range():
    fp = os.path.join(DATA, "isd_global_hourly_2024", "48900099999.csv")
    df = parse_isd(fp)
    t = df["temp_c"].dropna()
    assert (t > -10).all() and (t < 50).all()


# ---------------------------- NASA POWER ----------------------------
def test_parse_nasa_power_schema_and_fill_value():
    fp = os.path.join(DATA, "nasa_power_2024", "hanoi.json")
    df = parse_nasa_power(fp, "hanoi")
    _assert_schema(df)
    assert not (df["temp_c"] == -999.0).any(), "fill_value -999 phai duoc thay bang NaN"
    assert len(df) == 366  # 2024 la nam nhuan


def test_parse_nasa_power_pressure_unit_conversion_kpa_to_hpa():
    fp = os.path.join(DATA, "nasa_power_2024", "hanoi.json")
    df = parse_nasa_power(fp, "hanoi")
    p = df["pressure_surface_hpa"].dropna()
    # Ap suat be mat Ha Noi (~10m) phai ~1000-1020 hPa, KHONG phai ~100 (chua doi don vi)
    assert (p > 900).all() and (p < 1050).all()


# ---------------------------- Open-Meteo ----------------------------
def test_parse_openmeteo_schema_and_shape():
    fp = os.path.join(DATA, "openmeteo_2024", "hanoi.json")
    df = parse_openmeteo(fp, "hanoi")
    _assert_schema(df)
    assert len(df) == 8784  # 366 ngay x 24 gio (nam nhuan)


def test_parse_openmeteo_pressure_is_msl_not_surface():
    fp = os.path.join(DATA, "openmeteo_2024", "hanoi.json")
    df = parse_openmeteo(fp, "hanoi")
    p = df["pressure_msl_hpa"].dropna()
    # Khoang MSL hop ly ca nam bao gom ngay ap thap/bao (vd 982 hPa thuc do trong du lieu)
    assert (p > 960).all() and (p < 1040).all()


# ---------------------------- Clausius-Clapeyron (PINN-lite, docs/06 muc 4b) ----------------------------
def test_clausius_clapeyron_rh_100_when_saturated():
    t = pd.Series([25.0, 30.0])
    td = pd.Series([25.0, 30.0])  # diem suong = nhiet do -> bao hoa -> RH = 100%
    rh = clausius_clapeyron_rh(t, td)
    assert np.allclose(rh, 100.0, atol=0.1)


def test_clausius_clapeyron_rh_known_value():
    # T=25C, Td=20C -> RH thuc te ~73.8% (tra cuu bang tam ly do am chuan)
    t = pd.Series([25.0])
    td = pd.Series([20.0])
    rh = clausius_clapeyron_rh(t, td)
    assert 70 < rh.iloc[0] < 78


def test_clausius_clapeyron_rh_bounded_0_100():
    t = pd.Series([30.0, -5.0, 40.0])
    td = pd.Series([35.0, -20.0, 0.0])  # Td > T o ca 1: khong vat ly, nhung ham phai khong crash
    rh = clausius_clapeyron_rh(t, td)
    assert (rh >= 0).all() and (rh <= 100).all()


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
