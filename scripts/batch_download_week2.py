#!/usr/bin/env python3
"""
Batch tải dữ liệu thật (quy mô lớn hơn sample) cho 4 nguồn lõi — Tuần 2.
Chạy: python3 scripts/batch_download_week2.py
Output: data_samples/batch_week2/
"""
import json
import os
import time
import urllib.request
import csv
import io

OUT = os.path.join(os.path.dirname(__file__), "..", "data_samples", "batch_week2")
os.makedirs(OUT, exist_ok=True)

BBOX = {"lat_min": -11, "lat_max": 23, "lon_min": 92, "lon_max": 141}

UA = "Mozilla/5.0 (Nhom16-IT5427-HUST research script)"


def http_get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


# ---------- 1. GHCN-Daily: toàn lịch sử, danh sách trạm truyền vào ----------
STATIONS_VN_GHCN = [
    "VMM00048820",  # Noi Bai
    "VM000048900",  # Tan Son Hoa / HCM
    "VMM00048855",  # Da Nang
    "VMM00048845",  # Vinh
    "VMM00048887",  # Phan Thiet
    "VMM00048917",  # Phu Quoc
    "VMM00048808",  # Cao Bang
    "VMM00048806",  # Son La
    "VMM00048826",  # Phu Lien (Hai Phong)
    "VMM00048914",  # Ca Mau
]


def download_ghcn_batch(stations=None, subdir="ghcn_daily"):
    stations = stations or STATIONS_VN_GHCN
    outdir = os.path.join(OUT, subdir)
    os.makedirs(outdir, exist_ok=True)
    results = []
    for sid in stations:
        url = f"https://noaa-ghcn-pds.s3.amazonaws.com/csv/by_station/{sid}.csv"
        fp = os.path.join(outdir, f"{sid}.csv")
        try:
            t0 = time.time()
            data = http_get(url, timeout=60)
            with open(fp, "wb") as f:
                f.write(data)
            nrows = data.count(b"\n")
            results.append({"station": sid, "ok": True, "rows": nrows,
                             "size_kb": round(len(data) / 1024, 1),
                             "secs": round(time.time() - t0, 2)})
        except Exception as e:
            results.append({"station": sid, "ok": False, "error": str(e)})
        time.sleep(0.3)
    return results


def download_ghcn_sea_priority_batch():
    """31 trạm ưu tiên 8 nước ĐNA còn lại (không tính VN, đã tải riêng)."""
    ref_path = os.path.join(os.path.dirname(__file__), "..", "reference",
                             "ghcn_stations_sea_priority.csv")
    stations = []
    with open(ref_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            stations.append(row["ID"])
    return download_ghcn_batch(stations, subdir="ghcn_daily_sea_priority")


# ---------- 2. NOAA ISD / Global Hourly: năm truyền vào, danh sách trạm truyền vào ----------
def download_isd_batch(stations, subdir, year="2024"):
    """stations: list of (usaf, wban, name) tuples"""
    outdir = os.path.join(OUT, subdir)
    os.makedirs(outdir, exist_ok=True)
    results = []
    for usaf, wban, name in stations:
        sid = f"{usaf}{wban}"
        url = f"https://noaa-global-hourly-pds.s3.amazonaws.com/{year}/{sid}.csv"
        fp = os.path.join(outdir, f"{sid}.csv")
        try:
            t0 = time.time()
            data = http_get(url, timeout=60)
            with open(fp, "wb") as f:
                f.write(data)
            nrows = data.count(b"\n")
            results.append({"station": sid, "name": name, "ok": True, "rows": nrows,
                             "size_kb": round(len(data) / 1024, 1),
                             "secs": round(time.time() - t0, 2)})
        except Exception as e:
            results.append({"station": sid, "name": name, "ok": False, "error": str(e)})
        time.sleep(0.3)
    return results


def _load_isd_stations(ref_filename):
    ref_path = os.path.join(os.path.dirname(__file__), "..", "reference", ref_filename)
    stations = []
    with open(ref_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name = row.get("STATION NAME") or row.get("STATION_NAME") or ""
            stations.append((row["USAF"], row["WBAN"], name))
    return stations


def download_isd_vn_batch():
    stations = _load_isd_stations("isd_stations_vietnam_active.csv")
    return download_isd_batch(stations, subdir="isd_global_hourly_2024", year="2024")


def download_isd_sea_priority_batch():
    """16 trạm ưu tiên 8 nước ĐNA còn lại."""
    stations = _load_isd_stations("isd_stations_sea_priority.csv")
    return download_isd_batch(stations, subdir="isd_global_hourly_2024_sea_priority", year="2024")


# ---------- 3. NASA POWER: 6 toạ độ đại diện ĐNA, 1 năm (2024), daily ----------
def download_nasa_power_batch():
    points = {
        "hanoi": (21.0285, 105.8542),
        "hcmc": (10.7769, 106.7009),
        "jakarta": (-6.2088, 106.8456),
        "bangkok": (13.7563, 100.5018),
        "manila": (14.5995, 120.9842),
        "kuala_lumpur": (3.1390, 101.6869),
    }
    outdir = os.path.join(OUT, "nasa_power_2024")
    os.makedirs(outdir, exist_ok=True)
    params = "T2M,RH2M,PRECTOTCORR,WS2M,ALLSKY_SFC_SW_DWN,PS"
    results = []
    for name, (lat, lon) in points.items():
        url = (f"https://power.larc.nasa.gov/api/temporal/daily/point?"
               f"parameters={params}&community=AG&longitude={lon}&latitude={lat}"
               f"&start=20240101&end=20241231&format=JSON")
        fp = os.path.join(outdir, f"{name}.json")
        try:
            t0 = time.time()
            data = http_get(url, timeout=60)
            with open(fp, "wb") as f:
                f.write(data)
            parsed = json.loads(data)
            n_days = len(parsed["properties"]["parameter"]["T2M"])
            results.append({"point": name, "ok": True, "days": n_days,
                             "size_kb": round(len(data) / 1024, 1),
                             "secs": round(time.time() - t0, 2)})
        except Exception as e:
            results.append({"point": name, "ok": False, "error": str(e)})
        time.sleep(0.5)
    return results


# ---------- 4. Open-Meteo Historical: 6 toạ độ, 1 năm (2024), hourly ----------
def download_openmeteo_batch():
    points = {
        "hanoi": (21.0285, 105.8542),
        "hcmc": (10.7769, 106.7009),
        "jakarta": (-6.2088, 106.8456),
        "bangkok": (13.7563, 100.5018),
        "manila": (14.5995, 120.9842),
        "kuala_lumpur": (3.1390, 101.6869),
    }
    outdir = os.path.join(OUT, "openmeteo_2024")
    os.makedirs(outdir, exist_ok=True)
    hourly_vars = "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,surface_pressure,shortwave_radiation"
    results = []
    for name, (lat, lon) in points.items():
        url = (f"https://archive-api.open-meteo.com/v1/archive?"
               f"latitude={lat}&longitude={lon}&start_date=2024-01-01&end_date=2024-12-31"
               f"&hourly={hourly_vars}&timezone=UTC")
        fp = os.path.join(outdir, f"{name}.json")
        try:
            t0 = time.time()
            data = http_get(url, timeout=60)
            with open(fp, "wb") as f:
                f.write(data)
            parsed = json.loads(data)
            n_hours = len(parsed["hourly"]["time"])
            results.append({"point": name, "ok": True, "hours": n_hours,
                             "size_kb": round(len(data) / 1024, 1),
                             "secs": round(time.time() - t0, 2)})
        except Exception as e:
            results.append({"point": name, "ok": False, "error": str(e)})
        time.sleep(0.5)
    return results


# ---------- 5. ERA5 ARCO (Zarr, Google Cloud, miễn phí) — subset thật qua bbox ĐNA ----------
def download_era5_arco_subset():
    import xarray as xr
    outdir = os.path.join(OUT, "era5_arco")
    os.makedirs(outdir, exist_ok=True)
    result = {"ok": False}
    try:
        t0 = time.time()
        ds = xr.open_zarr(
            "gcs://gcp-public-data-arco-era5/ar/1959-2022-full_37-1h-0p25deg-chunk-1.zarr-v2",
            storage_options={"token": "anon"}, chunks=None,
        )
        sub = ds[["2m_temperature", "10m_u_component_of_wind", "10m_v_component_of_wind",
                   "total_precipitation"]].sel(
            time=slice("2021-06-15", "2021-06-17"),
            latitude=slice(BBOX["lat_max"], BBOX["lat_min"]),
            longitude=slice(BBOX["lon_min"], BBOX["lon_max"]),
        )
        sub = sub.load()
        fp = os.path.join(outdir, "era5_sea_2022-01-01_to_03.nc")
        sub.to_netcdf(fp)
        size_mb = os.path.getsize(fp) / (1024 * 1024)
        result = {"ok": True, "secs": round(time.time() - t0, 2),
                   "shape": {k: list(v.shape) for k, v in sub.data_vars.items()},
                   "size_mb": round(size_mb, 2), "file": fp}
    except Exception as e:
        result = {"ok": False, "error": str(e)}
    return result


def run_full():
    report = {}
    print("== 1/5: GHCN-Daily (10 trạm VN, toàn lịch sử) ==")
    report["ghcn_daily"] = download_ghcn_batch()
    print(json.dumps(report["ghcn_daily"], ensure_ascii=False, indent=2))

    print("== 2/5: NOAA ISD Global Hourly (10 trạm VN, năm 2024) ==")
    report["isd_2024"] = download_isd_vn_batch()
    print(json.dumps(report["isd_2024"], ensure_ascii=False, indent=2))

    print("== 3/5: NASA POWER (6 điểm, năm 2024, daily) ==")
    report["nasa_power_2024"] = download_nasa_power_batch()
    print(json.dumps(report["nasa_power_2024"], ensure_ascii=False, indent=2))

    print("== 4/5: Open-Meteo Historical (6 điểm, năm 2024, hourly) ==")
    report["openmeteo_2024"] = download_openmeteo_batch()
    print(json.dumps(report["openmeteo_2024"], ensure_ascii=False, indent=2))

    print("== 5/5: ERA5 ARCO (Zarr GCS, subset bbox ĐNA, 3 ngày) ==")
    report["era5_arco"] = download_era5_arco_subset()
    print(json.dumps(report["era5_arco"], ensure_ascii=False, indent=2))
    return report


def run_sea_priority():
    """Mở rộng GHCN + ISD ra 8 nước ĐNA còn lại (ngoài VN)."""
    report = {}
    print("== 1/2: GHCN-Daily (31 trạm ưu tiên, 8 nước ĐNA, toàn lịch sử) ==")
    report["ghcn_daily_sea_priority"] = download_ghcn_sea_priority_batch()
    print(json.dumps(report["ghcn_daily_sea_priority"], ensure_ascii=False, indent=2))

    print("== 2/2: NOAA ISD Global Hourly (16 trạm ưu tiên, 8 nước ĐNA, năm 2024) ==")
    report["isd_2024_sea_priority"] = download_isd_sea_priority_batch()
    print(json.dumps(report["isd_2024_sea_priority"], ensure_ascii=False, indent=2))
    return report


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    report_path = os.path.join(OUT, "batch_report.json")
    existing = {}
    if os.path.exists(report_path):
        with open(report_path, encoding="utf-8") as f:
            existing = json.load(f)

    if mode == "sea-priority":
        new_report = run_sea_priority()
    else:
        new_report = run_full()

    existing.update(new_report)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    print(f"\n== XONG (mode={mode}). Báo cáo đầy đủ: data_samples/batch_week2/batch_report.json ==")
