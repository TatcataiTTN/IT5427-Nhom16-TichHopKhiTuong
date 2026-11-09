import os

import pytest

from warehouse.validate_interpolation import _mae, _rmse, cross_validate

WAREHOUSE_EXISTS = os.path.exists(
    os.path.join(os.path.dirname(__file__), "..", "warehouse", "output", "weatherobs.parquet")
)


def test_rmse_zero_for_identical_series():
    import pandas as pd
    s = pd.Series([1.0, 2.0, 3.0])
    assert _rmse(s, s) == pytest.approx(0.0)
    assert _mae(s, s) == pytest.approx(0.0)


def test_rmse_known_value():
    import pandas as pd
    a = pd.Series([0.0, 0.0])
    b = pd.Series([3.0, 4.0])
    assert _rmse(a, b) == pytest.approx((3**2 + 4**2) ** 0.5 / (2 ** 0.5))
    assert _mae(a, b) == pytest.approx(3.5)


@pytest.mark.skipif(not WAREHOUSE_EXISTS, reason="warehouse/output/weatherobs.parquet chua duoc build")
def test_cross_validate_runs_on_real_warehouse_and_finds_overlap():
    results = cross_validate()
    assert results["n_pairs"] > 0
    assert "temp_c" in results["overall"]
    if results["overall"]["temp_c"]:
        # ERA5 bilinear vs tram that: sai so nhiet do hop ly phai duoi 5 do C (khong phai loi logic)
        assert results["overall"]["temp_c"]["rmse"] < 5.0
