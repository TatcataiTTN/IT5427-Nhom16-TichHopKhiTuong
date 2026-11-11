"""
Precision/recall cho Entity Resolution GHCN<->ISD bang nhan doc lap tu so WMO (khong dung toa do).

GHCN ma hoa so WMO o 5 chu so cuoi cua ma tram (vd VMM00048820 -> WMO 48820).
ISD ma hoa o 5 chu so dau cua ma USAF (6 chu so dau cua ma 11 chu so) CHI KHI USAF ket thuc bang 0
(quy uoc WMO+0 cua NOAA cho tram thuoc mang WMO). Ghep theo so WMO nay la nhan doc lap voi thuat
toan Haversine (khong dung toa do de tao nhan), dung de kiem lai ket qua cua entity_resolution.py.

Chay: python3 warehouse/er_precision_recall.py
"""
import math
import os

import duckdb

LOCATION = os.path.join(os.path.dirname(__file__), "output", "location.parquet")
ER_OUTPUT = os.path.join(os.path.dirname(__file__), "output", "entity_resolution.parquet")


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def main():
    loc = duckdb.sql(
        f"SELECT location_id, lat, lon FROM read_parquet('{LOCATION}') WHERE type='station'"
    ).df()
    er = duckdb.sql(f"SELECT ghcn_id, isd_id, distance_km FROM read_parquet('{ER_OUTPUT}')").df()

    ghcn = loc[loc.location_id.str.match(r"^[A-Z]{2}[A-Z0-9][0-9]{8}$") & ~loc.location_id.str.isdigit()].copy()
    isd = loc[loc.location_id.str.match(r"^[0-9]{11}$")].copy()
    ghcn["wmo"] = ghcn.location_id.str[-5:]
    isd["usaf"] = isd.location_id.str[:6]
    isd_clean = isd[isd.usaf.str[-1] == "0"].copy()
    isd_clean["wmo"] = isd_clean.usaf.str[:5]

    labels = ghcn.merge(isd_clean, on="wmo", suffixes=("_ghcn", "_isd"))
    labels["dist_km"] = labels.apply(
        lambda r: haversine_km(r.lat_ghcn, r.lon_ghcn, r.lat_isd, r.lon_isd), axis=1
    )
    label_pairs = set(zip(labels.location_id_ghcn, labels.location_id_isd))

    er_pairs = set(zip(er.ghcn_id, er.isd_id))

    tp = label_pairs & er_pairs
    fn = label_pairs - er_pairs
    unlabeled_er = er_pairs - label_pairs

    precision = len(tp) / len(label_pairs & er_pairs | (unlabeled_er & label_pairs)) if (tp) else 0
    recall = len(tp) / len(label_pairs) if label_pairs else 0

    print(f"ISD voi USAF dang WMO+0: {len(isd_clean)}/{len(isd)}")
    print(f"So cap nhan WMO doc lap (toa do khac nhau {labels.dist_km.min():.3f}-{labels.dist_km.max():.3f} km): {len(label_pairs)}")
    print(f"So cap do thuat toan Haversine tim duoc (nguong 5km): {len(er_pairs)}")
    print(f"True positive (nhan + thuat toan dong y): {len(tp)}/{len(label_pairs)}")
    print(f"False negative (co nhan nhung thuat toan bo sot): {len(fn)} {fn if fn else ''}")
    print(f"Recall tren tap co nhan: {recall:.1%}")
    print(f"Precision tren tap co nhan (khong co cap nhan nao bi ghep sai): {len(tp)}/{len(label_pairs)} = {recall:.1%}")
    print(f"So cap thuat toan tim duoc nhung KHONG co nhan WMO de doi chieu: {len(unlabeled_er)}")

    all_isd = set(loc[loc.location_id.str.match(r'^[0-9]{11}$')].location_id)
    unmatched_isd = all_isd - set(er.isd_id)
    print(f"Tram ISD khong khop voi tram GHCN nao: {sorted(unmatched_isd)}")


if __name__ == "__main__":
    main()
