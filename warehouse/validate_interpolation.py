"""
Kiem chuan (cross-validation) sai so noi suy khong gian ERA5 Bilinear (docs/03 Tuan 3,
TV2 #3 "leave-one-station-out cross-validation" + #4 "RMSE/MAE theo vung dia hinh phuc tap").

Vi noi suy dung la Bilinear tren luoi ERA5 (khong phai Kriging hoi quy tu chinh cac tram), "leave
one out" dung nghia o day la: so sanh gia tri ERA5-noi-suy-vao-toa-do-tram voi gia tri THAT tram
do duoc (GHCN/ISD) cung thoi diem, cung location_id -- tram "bi bo lai" khong duoc dung lam input
cho noi suy (Bilinear chi doc luoi ERA5, khong biet tram), dung lam tap kiem chung doc lap.

Phan vung "dia hinh phuc tap" dung proxy do cao (elevation_m) tu bang Location: tam vi phan theo
tercile (thap/trung binh/cao) vi nhom chua co du lieu do do doc (terrain ruggedness) rieng.
"""
import os

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
WAREHOUSE = os.path.join(ROOT, "warehouse", "output", "weatherobs.parquet")
LOCATION = os.path.join(ROOT, "warehouse", "output", "location.parquet")

VARS_TO_VALIDATE = ["temp_c", "wind_speed_ms", "precip_mm"]


def _rmse(a, b):
    return float(np.sqrt(np.mean((a - b) ** 2)))


def _mae(a, b):
    return float(np.mean(np.abs(a - b)))


def cross_validate(warehouse_path=WAREHOUSE, location_path=LOCATION) -> dict:
    df = pd.read_parquet(warehouse_path)
    df["date"] = pd.to_datetime(df["timestamp_utc"]).dt.date

    era5 = df[df["source"] == "ERA5"].copy()
    station = df[df["source"].isin(["GHCN", "ISD"])].copy()

    # Gop theo location_id + ngay (ERA5 subset chi co 15-17/6/2021, tan suat ~3h;
    # lay trung binh ngay cho ca 2 phia de so sanh cung don vi thoi gian).
    era5_daily = era5.groupby(["location_id", "date"])[VARS_TO_VALIDATE].mean().reset_index()
    station_daily = station.groupby(["location_id", "date"])[VARS_TO_VALIDATE].mean().reset_index()

    merged = era5_daily.merge(station_daily, on=["location_id", "date"], suffixes=("_era5", "_obs"))

    loc = pd.read_parquet(location_path)[["location_id", "elevation_m"]]
    merged = merged.merge(loc, on="location_id", how="left")

    results = {"n_pairs": len(merged), "n_stations": merged["location_id"].nunique(), "overall": {}, "by_elevation_tercile": {}}

    for var in VARS_TO_VALIDATE:
        a = merged[f"{var}_era5"].dropna()
        b = merged[f"{var}_obs"]
        pair = merged[[f"{var}_era5", f"{var}_obs"]].dropna()
        if len(pair) == 0:
            results["overall"][var] = None
            continue
        results["overall"][var] = {
            "n": len(pair),
            "rmse": round(_rmse(pair[f"{var}_era5"], pair[f"{var}_obs"]), 3),
            "mae": round(_mae(pair[f"{var}_era5"], pair[f"{var}_obs"]), 3),
        }

    valid_elev = merged.dropna(subset=["elevation_m"])
    if len(valid_elev) >= 3:
        terciles = pd.qcut(valid_elev["elevation_m"], q=min(3, valid_elev["elevation_m"].nunique()), duplicates="drop")
        valid_elev = valid_elev.assign(elev_group=terciles.astype(str))
        for group, gdf in valid_elev.groupby("elev_group"):
            group_result = {}
            for var in VARS_TO_VALIDATE:
                pair = gdf[[f"{var}_era5", f"{var}_obs"]].dropna()
                if len(pair) == 0:
                    continue
                group_result[var] = {
                    "n": len(pair),
                    "rmse": round(_rmse(pair[f"{var}_era5"], pair[f"{var}_obs"]), 3),
                    "mae": round(_mae(pair[f"{var}_era5"], pair[f"{var}_obs"]), 3),
                }
            results["by_elevation_tercile"][group] = group_result

    return results


if __name__ == "__main__":
    results = cross_validate()
    print(f"So cap (location_id, ngay) co ca ERA5 va tram that trung nhau: {results['n_pairs']}")
    print(f"So tram co du lieu kiem chung: {results['n_stations']}")
    print("\n--- RMSE/MAE tong the (ERA5 Bilinear vs tram that) ---")
    for var, stat in results["overall"].items():
        if stat:
            print(f"  {var}: n={stat['n']}, RMSE={stat['rmse']}, MAE={stat['mae']}")
        else:
            print(f"  {var}: khong co cap du lieu de so sanh")
    print("\n--- RMSE/MAE theo tercile do cao (proxy dia hinh) ---")
    for group, stat in results["by_elevation_tercile"].items():
        print(f"  Nhom do cao {group}:")
        for var, s in stat.items():
            print(f"    {var}: n={s['n']}, RMSE={s['rmse']}, MAE={s['mae']}")

    if results["n_pairs"] > 0:
        print("\nPASS")
    else:
        print("\nKHONG CO DU LIEU TRUNG (ERA5 subset hien chi 15-17/6/2021, co the khong trung ngay nao voi tram that con du lieu day du)")
