"""
Bảng Location (dimension) — docs/06 mục 2: Location(location_id, lat, lon, elevation_m,
type, country). Gộp từ reference/*.csv (GHCN/ISD station lists) + toạ độ điểm cố định
dùng cho NASA POWER/Open-Meteo trong scripts/batch_download_week2.py.
"""
import os

import pandas as pd

REF = os.path.join(os.path.dirname(__file__), "..", "reference")

# Phải khớp CHÍNH XÁC với điểm toạ độ trong scripts/batch_download_week2.py
# (NASA POWER + Open-Meteo dùng chung 1 bộ điểm, location_id = tên điểm)
POINT_LOCATIONS = {
    "hanoi": (21.0285, 105.8542, None, "Vietnam"),
    "hcmc": (10.7769, 106.7009, None, "Vietnam"),
    "jakarta": (-6.2088, 106.8456, None, "Indonesia"),
    "bangkok": (13.7563, 100.5018, None, "Thailand"),
    "manila": (14.5995, 120.9842, None, "Philippines"),
    "kuala_lumpur": (3.1390, 101.6869, None, "Malaysia"),
}


def _load_ghcn(filename, country_col=None):
    df = pd.read_csv(os.path.join(REF, filename))
    out = pd.DataFrame({
        "location_id": df["ID"],
        "lat": df["LAT"],
        "lon": df["LON"],
        "elevation_m": df["ELEV"],
        "type": "station",
        "country": df[country_col] if country_col else None,
    })
    return out


def _load_isd(filename, country_col=None):
    df = pd.read_csv(os.path.join(REF, filename))
    out = pd.DataFrame({
        "location_id": df["USAF"].astype(str) + df["WBAN"].astype(str),
        "lat": df["LAT"],
        "lon": df["LON"],
        "elevation_m": df["ELEV(M)"],
        "type": "station",
        "country": df[country_col] if country_col else None,
    })
    return out


def build_location_table() -> pd.DataFrame:
    frames = [
        _load_ghcn("ghcn_stations_vietnam_full.csv"),
        _load_ghcn("ghcn_stations_sea_priority.csv", country_col="country"),
        _load_isd("isd_stations_vietnam_active.csv"),
        _load_isd("isd_stations_sea_priority.csv", country_col="country"),
    ]
    # Việt Nam không có cột country riêng trong 2 file *_vietnam_* -> gán cứng
    frames[0]["country"] = "Vietnam"
    frames[2]["country"] = "Vietnam"

    for name, (lat, lon, elev, country) in POINT_LOCATIONS.items():
        frames.append(pd.DataFrame([{
            "location_id": name, "lat": lat, "lon": lon,
            "elevation_m": elev, "type": "point", "country": country,
        }]))

    frames = [f for f in frames if not f.empty]
    loc = pd.concat(frames, ignore_index=True)
    loc = loc.drop_duplicates(subset="location_id", keep="first").reset_index(drop=True)
    return loc


if __name__ == "__main__":
    loc = build_location_table()
    print(f"Tong so location: {len(loc)}")
    print(loc["type"].value_counts())
    print(loc["country"].value_counts())
    out_path = os.path.join(os.path.dirname(__file__), "output", "location.parquet")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    loc.to_parquet(out_path, index=False)
    print(f"Da ghi: {out_path}")
