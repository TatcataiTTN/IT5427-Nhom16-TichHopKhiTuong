"""
Unit test cho warehouse/climate_trends.py — Mann-Kendall + độ dốc Sen trên chuỗi tổng hợp có đáp án.

Chạy: pytest tests/test_climate_trends.py -v
"""
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from warehouse.climate_trends import annual_temperature, mann_kendall, sens_slope, trend_table


def test_mann_kendall_small_example_by_hand():
    # x = [1, 3, 2, 4]: các cặp (i<j) dấu: +,+,+,-,+,+ -> S = 4; Var(S) = 4*3*13/18
    mk = mann_kendall([1, 3, 2, 4])
    assert mk["S"] == 4
    assert abs(mk["var_S"] - 4 * 3 * 13 / 18) < 1e-12


def test_mann_kendall_tie_correction_reduces_variance():
    no_ties, ties = mann_kendall([1, 2, 3, 4, 5, 6]), mann_kendall([1, 2, 2, 2, 5, 6])
    assert ties["var_S"] < no_ties["var_S"]


def test_mann_kendall_detects_trend_and_not_noise():
    rng = np.random.default_rng(0)
    years = np.arange(1975, 2025)
    warming = 25 + 0.02 * (years - 1975) + rng.normal(0, 0.2, len(years))
    assert mann_kendall(warming)["p"] < 0.05 and mann_kendall(warming)["Z"] > 0
    assert mann_kendall(rng.normal(25, 0.5, len(years)))["p"] > 0.05


def test_sens_slope_matches_scipy_theilslopes_and_is_robust_to_outlier():
    rng = np.random.default_rng(1)
    t = np.arange(50, dtype=float)
    x = 0.03 * t + rng.normal(0, 0.1, 50)
    x[10] = 100.0  # outlier cực đoan
    assert abs(sens_slope(t, x) - stats.theilslopes(x, t)[0]) < 1e-12
    assert abs(sens_slope(t, x) - 0.03) < 0.01   # bình phương tối thiểu sẽ bị outlier kéo lệch


def test_trend_table_requires_min_years_and_scales_per_decade():
    years = np.arange(1975, 2025)
    annual = pd.DataFrame({"location_id": "A", "source": "GHCN", "year": years, "t": 25 + 0.02 * (years - 1975)})
    tt = trend_table(annual, ["t"], min_years=30, periods={"all": (None, None)})
    assert len(tt) == 1 and tt.loc[0, "trend"] == "tang"
    assert abs(tt.loc[0, "sen_slope_per_decade"] - 0.2) < 1e-9
    assert trend_table(annual.head(20), ["t"], min_years=30, periods={"all": (None, None)}).empty


def test_annual_temperature_drops_incomplete_years():
    dates = pd.date_range("2020-01-01", "2021-12-31", freq="D")
    d = pd.DataFrame({"location_id": "A", "source": "GHCN", "date": dates, "temp_mean": 25.0})
    d = d[~((d["date"].dt.year == 2021) & (d["date"].dt.month <= 6))]   # 2021 chỉ còn ~50% ngày
    a = annual_temperature(d)
    assert a["year"].tolist() == [2020]
