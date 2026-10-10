"""
Survivorship rule — quyết định giá trị "thắng" khi nhiều nguồn cùng đo 1 đại lượng
tại cùng vị trí/thời điểm. Áp dụng đúng bảng ưu tiên ở report/main.tex Mục 3.3 và
docs/06-truong-du-lieu-va-tich-hop.md Mục 3:

    Hạng 1 (cao nhất): ISD, GHCN   -- do truc tiep tai diem, co co QC
    Hạng 2:            ERA5        -- dong hoa quan trac that + mo hinh
    Hạng 3:            OPEN_METEO  -- noi suy phai sinh tu ERA5
    Hạng 4 (thap nhat): NASA_POWER -- ve tinh/MERRA-2, do phan giai tho nhat

Lưu ý QUAN TRỌNG (docs/06 mục 3): pressure_surface_hpa và pressure_msl_hpa là
HAI đại lượng vật lý khác nhau -- survivorship áp dụng ĐỘC LẬP cho từng cột,
không bao giờ trộn 2 cột này lại với nhau.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

SOURCE_PRIORITY = {
    "ISD": 1,
    "GHCN": 1,
    "ERA5": 2,
    "OPEN_METEO": 3,
    "NASA_POWER": 4,
}

# Nguong % lech coi la "xung dot" can gan co (conflict flag) - ap dung tren cac
# cot co ban chat lien tuc/so sanh duoc truc tiep (khong ap dung cho wind_dir_deg).
CONFLICT_THRESHOLD_PCT = {
    "temp_c": 10.0,       # >10% lech nhiet do (Kelvin-equivalent) coi la xung dot
    "rh_pct": 20.0,
    "precip_mm": 50.0,    # mua doi luu nhiet doi bien thien manh (docs/06 muc 3)
    "wind_speed_ms": 30.0,
    "pressure_surface_hpa": 2.0,
    "pressure_msl_hpa": 2.0,
    "solar_rad_wm2": 30.0,
}

VALUE_COLUMNS = [
    "temp_c", "rh_pct", "dewpoint_c", "precip_mm", "wind_speed_ms", "wind_dir_deg",
    "pressure_surface_hpa", "pressure_msl_hpa", "solar_rad_wm2", "cloud_cover_pct",
    "soil_temp_c", "soil_moist_m3m3",
]


def resolve_survivorship(df: pd.DataFrame, time_tolerance: str = "30min") -> pd.DataFrame:
    """
    Input: WeatherObs DataFrame nhieu nguon (co the cung location_id/thoi diem gan nhau
           tu cac nguon khac nhau).
    Output: 1 dong/location_id/thoi_diem_lam_tron, moi cot gia tri la gia tri "thang"
            theo survivorship + cot <field>_conflict (bool) + <field>_source_used.

    Don gian hoa thuc te: group theo (location_id, timestamp lam tron ve gio) vi cac
    nguon co tan suat khac nhau (GHCN/POWER = ngay, ISD/Open-Meteo = gio).
    """
    work = df.copy()
    work["priority"] = work["source"].map(SOURCE_PRIORITY).fillna(99)
    work["time_bucket"] = work["timestamp_utc"].dt.floor("D")  # gop theo ngay de so sanh da nguon

    out_rows = []
    for (loc, t), group in work.groupby(["location_id", "time_bucket"]):
        row = {"location_id": loc, "timestamp_utc": t}
        for col in VALUE_COLUMNS:
            candidates = group[["source", "priority", col]].dropna(subset=[col])
            if candidates.empty:
                row[col] = np.nan
                row[f"{col}_source_used"] = None
                row[f"{col}_conflict"] = False
                continue
            candidates = candidates.sort_values("priority")
            winner = candidates.iloc[0]
            row[col] = winner[col]
            row[f"{col}_source_used"] = winner["source"]

            conflict = False
            if col in CONFLICT_THRESHOLD_PCT and len(candidates) > 1:
                vals = candidates[col].to_numpy(dtype=float)
                spread_pct = (vals.max() - vals.min()) / (abs(winner[col]) + 1e-6) * 100.0
                conflict = spread_pct > CONFLICT_THRESHOLD_PCT[col]
            row[f"{col}_conflict"] = conflict
        out_rows.append(row)

    return pd.DataFrame(out_rows).sort_values(["location_id", "timestamp_utc"]).reset_index(drop=True)
