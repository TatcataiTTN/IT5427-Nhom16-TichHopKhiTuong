#!/usr/bin/env python3
"""
Tai ERA5 qua Copernicus CDS (cdsapi) — cat vung Dong Nam A o PHIA SERVER (MARS backend), khac voi
scripts/download_era5_full.py (ARCO-ERA5/GCS) phai tai nguyen chunk toan cau roi cat o may minh
(~55 lan du du lieu, xem phan tich thuc te da lam trong session). Output GIONG HET duong dan/ten file
cua ban ARCO (data_samples/era5_full/<bien>/<YYYY-MM>.nc) de warehouse/interpolation.py dung duoc
ma KHONG can sua gi — file CDS tai ve se duoc doi ten bien + doi 'valid_time' -> 'time' + bo 'expver'
cho khop dinh dang ARCO (da kiem tra that tren 1 file mau, xem ghi chu CDS_SHORTNAME ben duoi).

Mot request = 1 bien x 1 nam (toi da, gop thang de giam so request — CDS gioi han "cost" moi
request, 1 bien x 1 nam x bbox nho nay con rat xa gioi han). Chi xin NHUNG THANG con thieu (da
tai qua ARCO thi bo qua), tranh ton quota CDS cho phan da co.

Chay:
  python3 scripts/download_era5_cds.py                      # tat ca bien, 2020-2024
  python3 scripts/download_era5_cds.py --vars 2m_temperature --years 2020
"""
import argparse
import os
import sys
import time

import cdsapi
import numpy as np
import pandas as pd
import xarray as xr

OUT = os.path.join(os.path.dirname(__file__), "..", "data_samples", "era5_full")
RAW_CACHE = os.path.join(os.path.dirname(__file__), "..", "data_samples", "era5_cds_raw")
BBOX_AREA = [23, 92, -11, 141]  # North, West, South, East — khop BBOX trong download_era5_full.py

VARIABLES = [
    "2m_temperature", "total_precipitation", "10m_u_component_of_wind",
    "10m_v_component_of_wind", "surface_pressure", "mean_sea_level_pressure",
    "toa_incident_solar_radiation", "total_cloud_cover", "surface_solar_radiation_downwards",
]
# Ten bien ngan ECMWF/GRIB that su nam trong file CDS tra ve (da kiem chung thuc te voi t2m)
CDS_SHORTNAME = {
    "2m_temperature": "t2m", "total_precipitation": "tp", "10m_u_component_of_wind": "u10",
    "10m_v_component_of_wind": "v10", "surface_pressure": "sp", "mean_sea_level_pressure": "msl",
    "toa_incident_solar_radiation": "tisr", "total_cloud_cover": "tcc",
    "surface_solar_radiation_downwards": "ssrd",
}


def missing_months(var, year):
    """Thang nao cua (var, year) CHUA co file — chi xin CDS phan con thieu."""
    out = []
    for m in range(1, 13):
        month_key = f"{year}-{m:02d}"
        fp = os.path.join(OUT, var, f"{month_key}.nc")
        if not os.path.exists(fp):
            out.append((m, month_key))
    return out


def fetch_year(var, year, months_needed, client):
    outdir_raw = os.path.join(RAW_CACHE, var)
    os.makedirs(outdir_raw, exist_ok=True)
    raw_fp = os.path.join(outdir_raw, f"{year}.nc")

    if not os.path.exists(raw_fp):
        t0 = time.time()
        print(f"  Gui request CDS: {var} {year}, thang {[m for m, _ in months_needed]} ...", flush=True)
        client.retrieve(
            "reanalysis-era5-single-levels",
            {
                "product_type": "reanalysis",
                "variable": var,
                "year": str(year),
                "month": [f"{m:02d}" for m, _ in months_needed],
                "day": [f"{d:02d}" for d in range(1, 32)],
                "time": [f"{h:02d}:00" for h in range(24)],
                "area": BBOX_AREA,
                "data_format": "netcdf",
            },
            raw_fp,
        )
        print(f"  -> xong trong {time.time()-t0:.0f}s, {os.path.getsize(raw_fp)/2**20:.1f}MB", flush=True)

    ds = xr.open_dataset(raw_fp)
    short = CDS_SHORTNAME[var]
    da = ds[short].rename(var)
    if "valid_time" in da.dims or "valid_time" in da.coords:
        da = da.rename({"valid_time": "time"})
    if "expver" in da.coords:
        da = da.drop_vars("expver")
    if "number" in da.coords:
        da = da.drop_vars("number")

    outdir = os.path.join(OUT, var)
    os.makedirs(outdir, exist_ok=True)
    for m, month_key in months_needed:
        fp = os.path.join(outdir, f"{month_key}.nc")
        if os.path.exists(fp):
            continue
        sub = da.sel(time=da["time"].dt.month == m)
        n_expected = int((pd.Timestamp(f"{year}-{m:02d}-01") + pd.offsets.MonthEnd(0)
                          + pd.Timedelta(hours=23) - pd.Timestamp(f"{year}-{m:02d}-01")) / pd.Timedelta(hours=1)) + 1
        if sub.sizes["time"] != n_expected:
            print(f"  CANH BAO {var} {month_key}: {sub.sizes['time']}/{n_expected} gio — van luu, kiem tra lai sau",
                 flush=True)
        tmp = fp + ".part"
        sub.astype("float32").to_dataset(name=var).to_netcdf(
            tmp, encoding={var: {"zlib": True, "complevel": 4}})
        os.replace(tmp, fp)
        print(f"  [{var}] {month_key}: ok {os.path.getsize(fp)/2**20:.1f}MB", flush=True)
    ds.close()


def load_client(keyfile):
    """keyfile=None -> dung ~/.cdsapirc mac dinh. keyfile=duong dan -> doc url/key tu file do
    (vd scripts/cds_account2.key), de chay nhieu tai khoan CDS song song khong giam vao nhau."""
    if keyfile is None:
        return cdsapi.Client()
    cfg = {}
    with open(keyfile) as f:
        for line in f:
            if ":" in line:
                k, v = line.split(":", 1)
                cfg[k.strip()] = v.strip()
    return cdsapi.Client(url=cfg["url"], key=cfg["key"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vars", nargs="+", default=VARIABLES)
    parser.add_argument("--years", nargs="+", type=int, default=[2020, 2021, 2022, 2023, 2024])
    parser.add_argument("--keyfile", default=None,
                        help="File chua url/key CDS rieng (vd scripts/cds_account2.key); "
                             "mac dinh dung ~/.cdsapirc")
    parser.add_argument("--reverse", action="store_true",
                        help="Duyet danh sach (bien, nam) theo chieu nguoc — de chay song song voi "
                             "1 tien trinh khac (tai khoan CDS khac) di tu dau len ma khong giam viec")
    args = parser.parse_args()

    tasks = [(var, year) for var in args.vars for year in args.years]
    if args.reverse:
        tasks = list(reversed(tasks))

    client = load_client(args.keyfile)
    total_reqs = 0
    for var, year in tasks:
        need = missing_months(var, year)
        if not need:
            print(f"[{var} {year}] du 12 thang roi, bo qua")
            continue
        total_reqs += 1
        print(f"[{var} {year}] thieu {len(need)} thang -> gui 1 request CDS")
        try:
            fetch_year(var, year, need, client)
        except Exception as e:
            print(f"  LOI {var} {year}: {e}", flush=True)
    print(f"\nXONG. Da gui {total_reqs} request CDS.")


if __name__ == "__main__":
    main()
