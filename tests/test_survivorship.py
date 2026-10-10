"""
Test Survivorship rule bằng test case xung đột giả lập (đúng tiêu chí kiểm thử
docs/03-ke-hoach-160-tasks.md Tuần 2, TV2 #6: "Test case xung đột giả lập, hàm
chọn đúng giá trị theo quy tắc").

Chạy: pytest tests/test_survivorship.py -v
"""
import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from warehouse.survivorship import resolve_survivorship


def _row(location_id, ts, source, **values):
    base = {
        "location_id": location_id, "timestamp_utc": pd.Timestamp(ts, tz="UTC"), "source": source,
        "temp_c": None, "rh_pct": None, "dewpoint_c": None, "precip_mm": None,
        "wind_speed_ms": None, "wind_dir_deg": None, "pressure_surface_hpa": None,
        "pressure_msl_hpa": None, "solar_rad_wm2": None, "cloud_cover_pct": None,
        "soil_temp_c": None, "soil_moist_m3m3": None,
    }
    base.update(values)
    return base


def test_station_wins_over_model_when_no_conflict():
    """ISD (tram that) va NASA_POWER (mo hinh) do gan giong nhau -> ISD phai thang (hang 1)."""
    df = pd.DataFrame([
        _row("ST001", "2024-06-01T06:00:00", "ISD", temp_c=30.0),
        _row("ST001", "2024-06-01T06:00:00", "NASA_POWER", temp_c=30.5),
    ])
    out = resolve_survivorship(df)
    assert len(out) == 1
    assert out.iloc[0]["temp_c"] == 30.0
    assert out.iloc[0]["temp_c_source_used"] == "ISD"
    assert out.iloc[0]["temp_c_conflict"] == False  # noqa: E712 (gia tri gan giong nhau)


def test_conflict_flag_raised_when_sources_disagree_strongly():
    """ISD=25C vs NASA_POWER=35C (lech >10%) -> phai gan co conflict=True, van uu tien ISD."""
    df = pd.DataFrame([
        _row("ST002", "2024-06-01T06:00:00", "ISD", temp_c=25.0),
        _row("ST002", "2024-06-01T06:00:00", "NASA_POWER", temp_c=35.0),
    ])
    out = resolve_survivorship(df)
    assert out.iloc[0]["temp_c"] == 25.0  # van chon ISD du co xung dot
    assert out.iloc[0]["temp_c_source_used"] == "ISD"
    assert out.iloc[0]["temp_c_conflict"] == True  # noqa: E712


def test_priority_order_era5_beats_openmeteo_beats_power():
    df = pd.DataFrame([
        _row("ST003", "2024-06-01T00:00:00", "NASA_POWER", rh_pct=60.0),
        _row("ST003", "2024-06-01T00:00:00", "OPEN_METEO", rh_pct=65.0),
        _row("ST003", "2024-06-01T00:00:00", "ERA5", rh_pct=63.0),
    ])
    out = resolve_survivorship(df)
    assert out.iloc[0]["rh_pct"] == 63.0
    assert out.iloc[0]["rh_pct_source_used"] == "ERA5"


def test_fallback_to_lower_priority_when_higher_priority_missing():
    """Neu ISD khong co gia tri (NaN) cho 1 truong, phai rot xuong nguon hang thap hon."""
    df = pd.DataFrame([
        _row("ST004", "2024-06-01T00:00:00", "ISD", temp_c=None, solar_rad_wm2=None),
        _row("ST004", "2024-06-01T00:00:00", "NASA_POWER", temp_c=28.0, solar_rad_wm2=210.0),
    ])
    out = resolve_survivorship(df)
    assert out.iloc[0]["temp_c"] == 28.0
    assert out.iloc[0]["temp_c_source_used"] == "NASA_POWER"


def test_pressure_surface_and_msl_never_mixed():
    """pressure_surface_hpa (POWER) va pressure_msl_hpa (Open-Meteo/ISD) la 2 dai luong
    khac nhau -- survivorship phai xu ly doc lap, khong bao gio gop/so sanh cheo."""
    df = pd.DataFrame([
        _row("ST005", "2024-06-01T00:00:00", "NASA_POWER", pressure_surface_hpa=1005.0),
        _row("ST005", "2024-06-01T00:00:00", "ISD", pressure_msl_hpa=1012.0),
    ])
    out = resolve_survivorship(df)
    row = out.iloc[0]
    assert row["pressure_surface_hpa"] == 1005.0
    assert row["pressure_msl_hpa"] == 1012.0
    assert row["pressure_surface_hpa_source_used"] == "NASA_POWER"
    assert row["pressure_msl_hpa_source_used"] == "ISD"


def test_multiple_locations_and_days_grouped_independently():
    df = pd.DataFrame([
        _row("ST006", "2024-06-01T00:00:00", "ISD", temp_c=20.0),
        _row("ST006", "2024-06-02T00:00:00", "ISD", temp_c=22.0),
        _row("ST007", "2024-06-01T00:00:00", "ISD", temp_c=31.0),
    ])
    out = resolve_survivorship(df)
    assert len(out) == 3
    assert set(out["location_id"]) == {"ST006", "ST007"}


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
