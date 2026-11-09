import pandas as pd
import pytest

from warehouse.entity_resolution import haversine_km, resolve_entities


def test_haversine_same_point_is_zero():
    assert haversine_km(21.0, 105.8, 21.0, 105.8) == pytest.approx(0.0, abs=1e-9)


def test_haversine_known_distance_hanoi_hcmc():
    # Ha Noi -> TP.HCM thuc te ~1140-1160km duong chim bay (khoang cach Haversine)
    d = haversine_km(21.0285, 105.8542, 10.7769, 106.7009)
    assert 1100 < d < 1200


def test_resolve_entities_matches_exact_coincident_stations():
    loc = pd.DataFrame([
        {"location_id": "VMM00048820", "lat": 21.221, "lon": 105.807, "type": "station"},
        {"location_id": "48820099999", "lat": 21.221, "lon": 105.807, "type": "station"},
    ])
    result = resolve_entities(loc, threshold_km=5.0)
    assert len(result) == 1
    assert result.iloc[0]["ghcn_id"] == "VMM00048820"
    assert result.iloc[0]["isd_id"] == "48820099999"
    assert result.iloc[0]["distance_km"] == pytest.approx(0.0, abs=1e-6)


def test_resolve_entities_respects_threshold():
    loc = pd.DataFrame([
        {"location_id": "VMM00048820", "lat": 21.0, "lon": 105.0, "type": "station"},
        {"location_id": "48820099999", "lat": 25.0, "lon": 110.0, "type": "station"},  # >500km
    ])
    result = resolve_entities(loc, threshold_km=5.0)
    assert len(result) == 0


def test_resolve_entities_is_one_to_one_no_duplicate_isd():
    # 2 tram GHCN deu gan 1 tram ISD duy nhat -> chi 1 trong 2 duoc khop, khong dung lai ISD
    loc = pd.DataFrame([
        {"location_id": "VMA00000001", "lat": 21.000, "lon": 105.000, "type": "station"},
        {"location_id": "VMA00000002", "lat": 21.001, "lon": 105.001, "type": "station"},
        {"location_id": "48000099999", "lat": 21.000, "lon": 105.000, "type": "station"},
    ])
    result = resolve_entities(loc, threshold_km=5.0)
    assert len(result) == 1
    assert result["isd_id"].nunique() == len(result)


def test_resolve_entities_ignores_points_only_stations():
    loc = pd.DataFrame([
        {"location_id": "hanoi", "lat": 21.0285, "lon": 105.8542, "type": "point"},
        {"location_id": "48820099999", "lat": 21.0285, "lon": 105.8542, "type": "station"},
    ])
    result = resolve_entities(loc, threshold_km=5.0)
    assert len(result) == 0  # "hanoi" khong phai GHCN station (khong bat dau bang chu cai dang ma tram)
