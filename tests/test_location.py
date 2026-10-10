"""
Test bảng Location + referential integrity với warehouse (docs/03 Tuần 2, TV2 #8).
Chạy: pytest tests/test_location.py -v
(Cần chạy warehouse/build_warehouse.py trước để sinh warehouse/output/*.parquet)
"""
import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from warehouse.location import build_location_table

WAREHOUSE = os.path.join(os.path.dirname(__file__), "..", "warehouse", "output", "weatherobs.parquet")


def test_location_table_no_duplicate_ids():
    loc = build_location_table()
    assert loc["location_id"].is_unique


def test_location_table_lat_lon_physical_range():
    loc = build_location_table()
    assert (loc["lat"] >= -11).all() and (loc["lat"] <= 23).all()
    assert (loc["lon"] >= 92).all() and (loc["lon"] <= 141).all()


def test_location_table_covers_9_sea_countries():
    loc = build_location_table()
    expected = {"Vietnam", "Thailand", "Indonesia", "Malaysia", "Philippines",
                "Myanmar", "Cambodia", "Laos", "Brunei"}
    assert expected.issubset(set(loc["country"].dropna().unique()))


@pytest.mark.skipif(not os.path.exists(WAREHOUSE), reason="Chua chay warehouse/build_warehouse.py")
def test_referential_integrity_all_warehouse_locations_exist():
    """Moi location_id trong warehouse PHAI co trong bang Location (foreign key check)."""
    wh = pd.read_parquet(WAREHOUSE, columns=["location_id"])
    loc = build_location_table()
    missing = set(wh["location_id"].unique()) - set(loc["location_id"].unique())
    assert not missing, f"location_id trong warehouse nhung khong co trong Location: {missing}"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
