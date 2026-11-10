#!/usr/bin/env python3
"""
Tải đầy đủ các nguồn dạng điểm theo phạm vi đề cương (docs/03 Tuần 2 TV1 #2, #4):
  - NOAA ISD/Global Hourly: 26 trạm (10 VN + 16 ĐNA ưu tiên), 10 năm 2015–2024
  - Open-Meteo Historical: 6 điểm, 5 năm 2020–2024 (cùng khoảng thời gian với ERA5 full)
  - NASA POWER: 6 điểm, 5 năm 2020–2024, daily
GHCN-Daily đã là toàn lịch sử trong batch_download_week2.py nên không tải lại.

Output: data_samples/full/{isd/<năm>, openmeteo, nasa_power}/...
Chạy lại được: file đã có thì bỏ qua.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from batch_download_week2 import _load_isd_stations, http_get  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "data_samples", "full")
ISD_YEARS = range(2015, 2025)
POINT_START, POINT_END = "2020-01-01", "2024-12-31"
POINTS = {
    "hanoi": (21.0285, 105.8542),
    "hcmc": (10.7769, 106.7009),
    "jakarta": (-6.2088, 106.8456),
    "bangkok": (13.7563, 100.5018),
    "manila": (14.5995, 120.9842),
    "kuala_lumpur": (3.1390, 101.6869),
}


def fetch(url, fp, timeout=120, retries=3):
    """Tải về fp (ghi file tạm rồi đổi tên). Trả (status, size_bytes). 404 -> 'missing'."""
    if os.path.exists(fp):
        return "skip", os.path.getsize(fp)
    for attempt in range(retries):
        try:
            data = http_get(url, timeout=timeout)
            with open(fp + ".part", "wb") as f:
                f.write(data)
            os.replace(fp + ".part", fp)
            return "ok", len(data)
        except Exception as e:
            if "404" in str(e):
                return "missing", 0
            if attempt == retries - 1:
                return f"error: {e}", 0
            time.sleep(5 * (attempt + 1))


def download_isd():
    stations = (_load_isd_stations("isd_stations_vietnam_active.csv")
                + _load_isd_stations("isd_stations_sea_priority.csv"))
    report = []
    for year in ISD_YEARS:
        outdir = os.path.join(OUT, "isd", str(year))
        os.makedirs(outdir, exist_ok=True)
        for usaf, wban, name in stations:
            sid = f"{usaf}{wban}"
            url = f"https://noaa-global-hourly-pds.s3.amazonaws.com/{year}/{sid}.csv"
            status, size = fetch(url, os.path.join(outdir, f"{sid}.csv"))
            report.append({"year": year, "station": sid, "name": name, "status": status,
                           "size_kb": round(size / 1024, 1)})
            print(f"ISD {year} {sid} {name[:25]:25s} {status} {size / 2**20:.1f}MB", flush=True)
            time.sleep(0.2)
    return report


def download_openmeteo():
    outdir = os.path.join(OUT, "openmeteo")
    os.makedirs(outdir, exist_ok=True)
    hourly_vars = ("temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,"
                   "wind_direction_10m,pressure_msl,shortwave_radiation")
    report = []
    for name, (lat, lon) in POINTS.items():
        url = (f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}"
               f"&start_date={POINT_START}&end_date={POINT_END}&hourly={hourly_vars}&timezone=UTC")
        status, size = fetch(url, os.path.join(outdir, f"{name}.json"))
        report.append({"point": name, "status": status, "size_kb": round(size / 1024, 1)})
        print(f"Open-Meteo {name}: {status} {size / 2**20:.1f}MB", flush=True)
        time.sleep(2)  # API miễn phí giới hạn tần suất
    return report


def download_nasa_power():
    outdir = os.path.join(OUT, "nasa_power")
    os.makedirs(outdir, exist_ok=True)
    params = "T2M,RH2M,PRECTOTCORR,WS2M,WS10M,ALLSKY_SFC_SW_DWN,PS"  # WS10M: gió 10 m như các nguồn khác (docs/17)
    start, end = POINT_START.replace("-", ""), POINT_END.replace("-", "")
    report = []
    for name, (lat, lon) in POINTS.items():
        url = (f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters={params}"
               f"&community=AG&longitude={lon}&latitude={lat}&start={start}&end={end}&format=JSON")
        status, size = fetch(url, os.path.join(outdir, f"{name}.json"), timeout=300)
        report.append({"point": name, "status": status, "size_kb": round(size / 1024, 1)})
        print(f"NASA POWER {name}: {status} {size / 2**20:.1f}MB", flush=True)
        time.sleep(1)
    return report


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    report = {"openmeteo": download_openmeteo(), "nasa_power": download_nasa_power(),
              "isd": download_isd()}
    with open(os.path.join(OUT, "download_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    bad = [r for part in report.values() for r in part if r["status"].startswith("error")]
    print(f"\nXONG. Lỗi: {len(bad)}. Báo cáo: data_samples/full/download_report.json")
