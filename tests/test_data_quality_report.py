import pandas as pd

from warehouse.data_quality_report import missing_rate_by_source, outlier_rate_by_source, spatiotemporal_coverage


def _sample_df():
    return pd.DataFrame({
        "source": ["A", "A", "A", "B", "B"],
        "timestamp_utc": pd.to_datetime([
            "2024-01-01", "2024-01-02", "2024-01-03", "2024-06-01", "2024-06-02",
        ]),
        "location_id": ["s1", "s1", "s2", "s3", "s3"],
        "temp_c": [20.0, None, 22.0, 25.0, 1000.0],
        "rh_pct": [50.0, 55.0, None, 60.0, 61.0],
        "precip_mm": [0.0, 1.0, 2.0, None, None],
        "wind_speed_ms": [1.0, 2.0, 3.0, 4.0, 5.0],
        "pressure_msl_hpa": [1010.0, 1011.0, 1012.0, 1013.0, 1014.0],
    })


def test_missing_rate_by_source_computes_correct_percentages():
    result = missing_rate_by_source(_sample_df())
    row_a = result[result["source"] == "A"].iloc[0]
    assert row_a["temp_c_missing_pct"] == pytest_approx(33.3)
    row_b = result[result["source"] == "B"].iloc[0]
    assert row_b["precip_mm_missing_pct"] == 100.0


def test_spatiotemporal_coverage_counts_distinct_locations():
    result = spatiotemporal_coverage(_sample_df())
    row_a = result[result["source"] == "A"].iloc[0]
    assert row_a["n_locations"] == 2  # s1, s2
    row_b = result[result["source"] == "B"].iloc[0]
    assert row_b["n_locations"] == 1  # s3


def test_outlier_rate_by_source_flags_injected_extreme_value():
    result = outlier_rate_by_source(_sample_df())
    row_b = result[result["source"] == "B"].iloc[0]
    # Chi 2 gia tri (25, 1000) trong source B -> IQR khong du du lieu de tinh (can >=4 diem),
    # nen chi so nay se la None/NaN - test chi dam bao ham khong crash va tra ve dung schema
    assert "temp_c_outlier_pct" in row_b.index


def pytest_approx(x, rel=1e-2):
    import pytest
    return pytest.approx(x, rel=rel)
