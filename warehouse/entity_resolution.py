"""
Entity Resolution GHCN <-> ISD (docs/03 Tuan 3, TV2 #2 "Hoan thien Record Linkage quy mo day du";
gap da ghi nhan tai docs/10 muc 1 va docs/11 muc 1): GHCN va ISD dung 2 he ma tram doc lap cho
cung 1 vi tri vat ly -> khong the so khop qua location_id, phai so khop theo khoang cach toa do.

Thuat toan: Haversine distance, nearest-neighbor 1-1 (moi tram GHCN khop voi toi da 1 tram ISD
gan nhat trong nguong), khong dung thu vien ngoai (geopy) de giu dependency gon.
"""
import math
import os

import pandas as pd

EARTH_RADIUS_KM = 6371.0088
# Nguong khop: 2 tram cung 1 vi tri vat ly (vd san bay) thuong lech <1km do lam tron toa do
# khac nhau giua 2 co quan nguon (GHCN vs ISD). 5km du chat de tranh khop nham 2 tram gan nhau
# thuc su khac nhau (VD 2 tram do trong cung 1 thanh pho lon).
MATCH_THRESHOLD_KM = 5.0


def haversine_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def _split_by_source(loc: pd.DataFrame):
    stations = loc[loc["type"] == "station"].copy()
    is_ghcn = stations["location_id"].str.match(r"^[A-Za-z]")
    ghcn = stations[is_ghcn].reset_index(drop=True)
    isd = stations[~is_ghcn].reset_index(drop=True)
    return ghcn, isd


def resolve_entities(loc: pd.DataFrame, threshold_km: float = MATCH_THRESHOLD_KM) -> pd.DataFrame:
    """Tra ve DataFrame: 1 dong / cap (ghcn_id, isd_id) khop nhau, kem distance_km.
    Nearest-neighbor 1-1: moi tram GHCN chi khop voi 1 tram ISD gan nhat (neu trong nguong),
    va 1 tram ISD khong duoc dung lai cho 2 tram GHCN khac nhau (tranh khop trung).
    """
    ghcn, isd = _split_by_source(loc)
    matches = []
    used_isd = set()

    for _, g in ghcn.iterrows():
        best_dist = None
        best_isd_id = None
        for _, i in isd.iterrows():
            if i["location_id"] in used_isd:
                continue
            d = haversine_km(g["lat"], g["lon"], i["lat"], i["lon"])
            if d <= threshold_km and (best_dist is None or d < best_dist):
                best_dist = d
                best_isd_id = i["location_id"]
        if best_isd_id is not None:
            used_isd.add(best_isd_id)
            matches.append({
                "entity_id": f"ENT_{len(matches) + 1:03d}",
                "ghcn_id": g["location_id"],
                "isd_id": best_isd_id,
                "distance_km": round(best_dist, 3),
                "lat": g["lat"],
                "lon": g["lon"],
            })

    return pd.DataFrame(matches, columns=["entity_id", "ghcn_id", "isd_id", "distance_km", "lat", "lon"])


if __name__ == "__main__":
    loc_path = os.path.join(os.path.dirname(__file__), "output", "location.parquet")
    loc = pd.read_parquet(loc_path)
    ghcn, isd = _split_by_source(loc)
    print(f"GHCN: {len(ghcn)} tram | ISD: {len(isd)} tram")

    result = resolve_entities(loc)
    print(f"Da khop duoc {len(result)} cap GHCN<->ISD (nguong {MATCH_THRESHOLD_KM}km)")
    if len(result) > 0:
        print(result.to_string(index=False))
        print(f"Khoang cach trung binh: {result['distance_km'].mean():.3f} km, "
              f"max: {result['distance_km'].max():.3f} km, min: {result['distance_km'].min():.3f} km")

    unmatched_ghcn = len(ghcn) - len(result)
    unmatched_isd = len(isd) - len(result)
    print(f"GHCN khong khop duoc tram ISD nao trong nguong: {unmatched_ghcn}/{len(ghcn)}")
    print(f"ISD khong khop duoc tram GHCN nao trong nguong: {unmatched_isd}/{len(isd)}")

    out_path = os.path.join(os.path.dirname(__file__), "output", "entity_resolution.parquet")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    result.to_parquet(out_path, index=False)
    print(f"Da ghi: {out_path}")
    print("PASS" if len(result) >= 0 else "FAIL")
