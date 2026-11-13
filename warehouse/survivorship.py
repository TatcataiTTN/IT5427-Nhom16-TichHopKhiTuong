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


def resolve_survivorship(df: pd.DataFrame) -> pd.DataFrame:
    """
    Input: WeatherObs DataFrame nhieu nguon (cung location_id, nhieu ban ghi/ngay tu
           cac nguon co tan suat khac nhau -- GHCN/NASA_POWER theo ngay, ISD/Open-Meteo
           theo gio, ERA5 theo gio).
    Output: 1 dong/location_id/ngay, moi cot gia tri la gia tri "thang" theo survivorship
            + cot <field>_source_used + cot <field>_conflict (bool).

    Sua loi phuong phap cua ban dau (xem docstring warehouse/survivorship_conflict_by_source.py):
    PHAI gop ve 1 gia tri trung binh/nguon/ngay TRUOC khi so sanh giua cac nguon, neu khong bien
    thien tu nhien trong ngay cua 1 nguon tan suat gio (vd nhiet do sang-trua cua ISD) se bi tinh
    nham thanh "xung dot giua cac nguon". Day la ham DUY NHAT sinh gia tri da hop giai (dung de
    kiem tra "Survivorship co that su sinh ra ban ghi da hop nhat khong") -- warehouse/
    survivorship_conflict_by_source.py chi dung de doi chieu ty le % tong hop, khong ghi ra bang.
    """
    cols = [c for c in VALUE_COLUMNS if c in df.columns]
    work = df.copy()
    work["day"] = work["timestamp_utc"].dt.floor("D")
    per_source_day = (work.groupby(["location_id", "day", "source"], observed=True)[cols]
                       .mean().reset_index())
    per_source_day["priority"] = per_source_day["source"].map(SOURCE_PRIORITY).fillna(99)

    # Vector hoa theo tung cot (khong lap Python qua tung nhom (location_id, day) -- voi hang
    # tram nghin nhom se rat cham). Voi moi cot: sap theo priority roi lay dong dau moi nhom
    # (= nguon thang), cong voi max/min cua cot trong nhom de tinh % xung dot.
    result = None
    for col in cols:
        sub = per_source_day.dropna(subset=[col])[["location_id", "day", "source", "priority", col]]
        if sub.empty:
            continue
        g = sub.groupby(["location_id", "day"], observed=True)
        winner = (sub.sort_values(["location_id", "day", "priority"])
                  .groupby(["location_id", "day"], observed=True).first())
        agg = g[col].agg(["max", "min", "size"])
        piece = winner.join(agg, rsuffix="_agg").reset_index()
        spread_pct = (piece["max"] - piece["min"]) / (piece[col].abs() + 1e-6) * 100.0
        conflict = (piece["size"] > 1) & (spread_pct > CONFLICT_THRESHOLD_PCT.get(col, np.inf))
        piece = piece[["location_id", "day", col, "source"]].assign(**{f"{col}_conflict": conflict})
        piece = piece.rename(columns={"source": f"{col}_source_used"})
        result = piece if result is None else result.merge(
            piece, on=["location_id", "day"], how="outer")

    if result is None:
        return pd.DataFrame(columns=["location_id", "day"])
    return result.sort_values(["location_id", "day"]).reset_index(drop=True)
