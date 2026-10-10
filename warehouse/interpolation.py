"""
Nội suy không gian ERA5 (lưới) -> vị trí trạm (điểm) bằng Bilinear Interpolation
(docs/06 mục 4a: "thuần tuý bài toán nội suy không gian, không cần PINN").

Đây cũng CHÍNH LÀ bước Record Linkage trạm<->lưới theo khoá không gian-thời gian
(docs/03 Tuần 2, TV2 #5): kết quả nội suy được gán vào đúng location_id của trạm,
cho phép Survivorship (warehouse/survivorship.py) so sánh trực tiếp ERA5 vs trạm
tại CÙNG MỘT vị trí.
"""
import numpy as np
import pandas as pd
import xarray as xr


def bilinear_interpolate_era5(nc_path: str, stations: pd.DataFrame) -> pd.DataFrame:
    """
    nc_path: file NetCDF ERA5 ARCO subset (vars: 2m_temperature [K], 10m_u/v_component_of_wind
             [m/s], total_precipitation [m]).
    stations: DataFrame co cot location_id, lat, lon (vd warehouse/location.py, loc da
              nam trong bounding box cua file nc).

    Tra ve WeatherObs DataFrame (source='ERA5'), 1 dong/location_id/timestamp, gia tri
    da noi suy song tuyen tinh tu 4 o luoi gan nhat + da doi don vi (K->C, m->mm,
    u,v -> speed/direction theo docs/06 muc 2 cong thuc GAV cho ERA5).
    """
    ds = xr.open_dataset(nc_path)
    lat_min, lat_max = float(ds.latitude.min()), float(ds.latitude.max())
    lon_min, lon_max = float(ds.longitude.min()), float(ds.longitude.max())

    in_bbox = stations[
        (stations["lat"] >= lat_min) & (stations["lat"] <= lat_max) &
        (stations["lon"] >= lon_min) & (stations["lon"] <= lon_max)
    ].dropna(subset=["lat", "lon"])

    rows = []
    for _, st in in_bbox.iterrows():
        pt = ds.interp(latitude=st["lat"], longitude=st["lon"], method="linear")
        temp_c = pt["2m_temperature"].values - 273.15
        u = pt["10m_u_component_of_wind"].values
        v = pt["10m_v_component_of_wind"].values
        wind_speed = np.sqrt(u**2 + v**2)
        # Quy uoc khi tuong: huong gio la huong GIO THOI TU, 0=Bac, tang theo chieu kim dong ho
        wind_dir = (np.degrees(np.arctan2(-u, -v))) % 360
        precip_mm = pt["total_precipitation"].values * 1000.0

        sub = pd.DataFrame({
            "location_id": st["location_id"],
            "timestamp_utc": pd.to_datetime(ds.time.values, utc=True),
            "source": "ERA5",
            "temp_c": temp_c,
            "rh_pct": np.nan,
            "dewpoint_c": np.nan,
            "precip_mm": precip_mm,
            "wind_speed_ms": wind_speed,
            "wind_dir_deg": wind_dir,
            "pressure_surface_hpa": np.nan,
            "pressure_msl_hpa": np.nan,
            "solar_rad_wm2": np.nan,
            "cloud_cover_pct": np.nan,
            "soil_temp_c": np.nan,
            "soil_moist_m3m3": np.nan,
        })
        rows.append(sub)

    ds.close()
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from warehouse.location import build_location_table

    nc_path = os.path.join(
        os.path.dirname(__file__), "..", "data_samples", "batch_week2",
        "era5_arco", "era5_sea_2022-01-01_to_03.nc",
    )
    loc = build_location_table()
    stations_only = loc[loc["type"] == "station"]
    print(f"So tram trong bounding box de noi suy: kiem tra tren {len(stations_only)} tram ung vien")

    out = bilinear_interpolate_era5(nc_path, stations_only)
    print(f"Ket qua noi suy: {len(out):,} dong ({out['location_id'].nunique()} tram x "
          f"{out['timestamp_utc'].nunique()} moc gio)")
    print(out.head(3).to_string())
    print("\nKiem tra vat ly: temp_c min/max =", out["temp_c"].min(), out["temp_c"].max())
    print("wind_speed_ms min/max =", out["wind_speed_ms"].min(), out["wind_speed_ms"].max())
