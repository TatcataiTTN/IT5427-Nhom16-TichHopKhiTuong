#!/usr/bin/env python3
"""
Tải ERA5 đầy đủ (docs/03 Tuần 2 TV1 #1): bounding box ĐNA, 5 năm (2020–2024), tần suất giờ,
9 biến bề mặt = 8 biến theo GAV mapping ở docs/06 + surface_solar_radiation_downwards
(bức xạ TẠI BỀ MẶT — đúng đại lượng để đối chiếu với NASA POWER ALLSKY_SFC_SW_DWN và
Open-Meteo shortwave_radiation; toa_incident_solar_radiation là bức xạ ở ĐỈNH khí quyển).

Nguồn: ARCO-ERA5 (Google Cloud, miễn phí, không cần tài khoản). Mỗi chunk Zarr là 1 giờ toàn cầu
(1 × 721 × 1440), nên phải tải cả chunk toàn cầu rồi cắt bbox — lượng tải về lớn hơn nhiều
so với dung lượng lưu (chỉ giữ phần bbox, nén zlib).

Output: data_samples/era5_full/<bien>/<YYYY-MM>.nc  — mỗi file 1 biến × 1 tháng.
Chạy lại được: file tháng nào đã có thì bỏ qua (resume sau khi ngắt).

Chạy:
  python3 scripts/download_era5_full.py                       # mặc định 2020-01 → 2024-12, 9 biến
  python3 scripts/download_era5_full.py --start 2024-01 --end 2024-03 --vars 2m_temperature
  python3 scripts/download_era5_full.py --workers 32          # số luồng tải song song
"""
import argparse
import os
import sys
import time

import numpy as np
import pandas as pd
import xarray as xr

ARCO_URL = "gcs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3"
OUT = os.path.join(os.path.dirname(__file__), "..", "data_samples", "era5_full")
BBOX = {"lat_min": -11, "lat_max": 23, "lon_min": 92, "lon_max": 141}  # khớp batch_download_week2.py

VARIABLES = [
    "2m_temperature",
    "total_precipitation",
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
    "surface_pressure",
    "mean_sea_level_pressure",
    "toa_incident_solar_radiation",
    "total_cloud_cover",
    "surface_solar_radiation_downwards",
]


def month_range(start, end):
    return [p.strftime("%Y-%m") for p in pd.period_range(start, end, freq="M")]


def download_month(ds, var, month, workers):
    outdir = os.path.join(OUT, var)
    os.makedirs(outdir, exist_ok=True)
    fp = os.path.join(outdir, f"{month}.nc")
    if os.path.exists(fp):
        return fp, "skip", 0.0

    t0 = time.time()
    first = pd.Timestamp(f"{month}-01")
    last = first + pd.offsets.MonthEnd(0) + pd.Timedelta(hours=23)
    sub = ds[var].sel(
        time=slice(first, last),
        latitude=slice(BBOX["lat_max"], BBOX["lat_min"]),
        longitude=slice(BBOX["lon_min"], BBOX["lon_max"]),
    )
    import dask
    with dask.config.set(scheduler="threads", num_workers=workers):
        sub = sub.load()

    n_expected = int((last - first) / pd.Timedelta(hours=1)) + 1
    if sub.sizes["time"] != n_expected or bool(np.isnan(sub.values).all()):
        raise RuntimeError(f"{var} {month}: {sub.sizes['time']}/{n_expected} giờ hoặc toàn NaN")

    # Ghi ra file tạm rồi đổi tên — tránh để lại file hỏng nếu bị ngắt giữa chừng
    tmp = fp + ".part"
    sub.astype("float32").to_dataset(name=var).to_netcdf(
        tmp, encoding={var: {"zlib": True, "complevel": 4}})
    os.replace(tmp, fp)
    return fp, "ok", time.time() - t0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2020-01")
    parser.add_argument("--end", default="2024-12")
    parser.add_argument("--vars", nargs="+", default=VARIABLES)
    parser.add_argument("--workers", type=int, default=32)
    args = parser.parse_args()

    ds = xr.open_zarr(ARCO_URL, storage_options={"token": "anon"}, chunks={"time": 1})
    months = month_range(args.start, args.end)
    total = len(months) * len(args.vars)
    print(f"ERA5: {len(args.vars)} biến × {len(months)} tháng = {total} file -> {os.path.abspath(OUT)}")

    done, failed, t_start = 0, [], time.time()
    for month in months:
        for var in args.vars:
            done += 1
            try:
                fp, status, secs = download_month(ds, var, month, args.workers)
                size = os.path.getsize(fp) / 2**20
                print(f"[{done}/{total}] {month} {var}: {status} {size:.1f}MB {secs:.0f}s", flush=True)
            except Exception as e:
                failed.append((month, var, str(e)))
                print(f"[{done}/{total}] {month} {var}: LOI {e}", flush=True)

    print(f"\nXONG trong {(time.time() - t_start) / 3600:.2f} giờ. Lỗi: {len(failed)}")
    for f in failed:
        print("  ", f)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
