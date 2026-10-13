"""
Parser cho 4 nguồn điểm (GHCN-Daily, NOAA ISD, NASA POWER, Open-Meteo) ->
Mediated Schema WeatherObs đã thiết kế ở docs/06-truong-du-lieu-va-tich-hop.md mục 2.

Cột chuẩn đầu ra (mọi hàm parse_* đều trả đúng tập cột này, NaN nếu nguồn không có):
    location_id, timestamp_utc, source,
    temp_c, rh_pct, dewpoint_c,
    precip_mm, wind_speed_ms, wind_dir_deg,
    pressure_surface_hpa, pressure_msl_hpa,
    solar_rad_wm2, cloud_cover_pct, soil_temp_c, soil_moist_m3m3

Mọi giá trị số đã chuẩn hoá đơn vị thật (không phải giá trị thô trong file gốc).
"""
import json
import math
import os

import numpy as np
import pandas as pd

WEATHEROBS_COLUMNS = [
    "location_id", "timestamp_utc", "source",
    "temp_c", "rh_pct", "dewpoint_c",
    "precip_mm", "wind_speed_ms", "wind_dir_deg",
    "pressure_surface_hpa", "pressure_msl_hpa",
    "solar_rad_wm2", "cloud_cover_pct", "soil_temp_c", "soil_moist_m3m3",
]


def _empty_weatherobs() -> pd.DataFrame:
    return pd.DataFrame({c: pd.Series(dtype="object") for c in WEATHEROBS_COLUMNS})


# ---------------------------------------------------------------------------
# GHCN-Daily: dạng "long" (1 dòng/1 biến/1 ngày) -> PIVOT bắt buộc (docs/06 mục 2)
# ---------------------------------------------------------------------------
def parse_ghcn(filepath: str) -> pd.DataFrame:
    """ID,DATE,ELEMENT,DATA_VALUE,M_FLAG,Q_FLAG,S_FLAG,OBS_TIME
    DATA_VALUE của TMAX/TMIN/TAVG tính bằng 1/10 độ C, PRCP tính bằng 1/10 mm (chuẩn GHCN).
    """
    raw = pd.read_csv(filepath, dtype={"ID": str, "DATE": str})
    if raw.empty:
        return _empty_weatherobs()

    station_id = raw["ID"].iloc[0]
    pivot = raw.pivot_table(index="DATE", columns="ELEMENT", values="DATA_VALUE", aggfunc="first")

    out = pd.DataFrame(index=pivot.index)
    out["location_id"] = station_id
    out["timestamp_utc"] = pd.to_datetime(pivot.index, format="%Y%m%d", utc=True)
    out["source"] = "GHCN"
    if "TAVG" in pivot:
        out["temp_c"] = pivot["TAVG"] / 10.0
    elif "TMAX" in pivot and "TMIN" in pivot:
        out["temp_c"] = (pivot["TMAX"] + pivot["TMIN"]) / 2.0 / 10.0
    else:
        out["temp_c"] = np.nan
    out["precip_mm"] = (pivot["PRCP"] / 10.0) if "PRCP" in pivot else np.nan

    for c in WEATHEROBS_COLUMNS:
        if c not in out.columns:
            out[c] = np.nan
    return out[WEATHEROBS_COLUMNS].reset_index(drop=True)


# ---------------------------------------------------------------------------
# NOAA ISD / Global Hourly: trường "nén" nhiều sub-field -> PARSE bắt buộc (docs/06 mục 2)
# ---------------------------------------------------------------------------
def _parse_isd_packed(value, missing_codes, scale, idx=0):
    """Tách 1 sub-field từ chuỗi nén dạng 'a,b,c,...', trả NaN nếu field = mã missing."""
    if pd.isna(value):
        return np.nan
    parts = str(value).split(",")
    if idx >= len(parts):
        return np.nan
    field = parts[idx]
    try:
        num = int(field)
    except ValueError:
        return np.nan
    if num in missing_codes:
        return np.nan
    return num / scale


def parse_isd(filepath: str) -> pd.DataFrame:
    """WND='dir,dirQC,type,speed_tenths_ms,speedQC' (missing dir=999, speed=9999)
    TMP='temp_tenths_C,QC' (missing=+9999)
    DEW='dewpoint_tenths_C,QC' (missing=+9999)
    SLP='pressure_tenths_hPa,QC' (missing=99999)
    """
    raw = pd.read_csv(filepath, dtype={"STATION": str}, low_memory=False)
    if raw.empty:
        return _empty_weatherobs()

    out = pd.DataFrame(index=raw.index)
    out["location_id"] = raw["STATION"]
    out["timestamp_utc"] = pd.to_datetime(raw["DATE"], utc=True)
    out["source"] = "ISD"

    out["temp_c"] = raw["TMP"].apply(lambda v: _parse_isd_packed(v, {9999}, 10, idx=0))
    out["dewpoint_c"] = raw["DEW"].apply(lambda v: _parse_isd_packed(v, {9999}, 10, idx=0))
    out["pressure_msl_hpa"] = raw["SLP"].apply(lambda v: _parse_isd_packed(v, {99999}, 10, idx=0))
    out["wind_dir_deg"] = raw["WND"].apply(lambda v: _parse_isd_packed(v, {999}, 1, idx=0))
    out["wind_speed_ms"] = raw["WND"].apply(lambda v: _parse_isd_packed(v, {9999}, 10, idx=3))

    # RH% suy từ Dew Point bằng Clausius-Clapeyron thật (không phải nội suy — xem docs/06 mục 4b)
    out["rh_pct"] = clausius_clapeyron_rh(out["temp_c"], out["dewpoint_c"])

    for c in WEATHEROBS_COLUMNS:
        if c not in out.columns:
            out[c] = np.nan
    return out[WEATHEROBS_COLUMNS].reset_index(drop=True)


def clausius_clapeyron_rh(temp_c: pd.Series, dewpoint_c: pd.Series) -> pd.Series:
    """RH% = e(Td) / es(T) * 100, es theo công thức Clausius-Clapeyron (docs/06 mục 4b,
    và report/main.tex mục 3.4): es(T) = 6.112 * exp(17.67*T / (T+243.5)) [hPa], T theo độ C."""
    def es(t):
        return 6.112 * np.exp(17.67 * t / (t + 243.5))
    e_actual = es(dewpoint_c)
    e_sat = es(temp_c)
    with np.errstate(divide="ignore", invalid="ignore"):
        rh = (e_actual / e_sat) * 100.0
    return rh.clip(lower=0, upper=100)


# ---------------------------------------------------------------------------
# NASA POWER: JSON wide, fill_value=-999.0 (đã xác nhận thật trong header JSON)
# ---------------------------------------------------------------------------
def parse_nasa_power(filepath: str, location_id: str) -> pd.DataFrame:
    with open(filepath, encoding="utf-8") as f:
        d = json.load(f)
    fill = d.get("header", {}).get("fill_value", -999.0)
    params = d["properties"]["parameter"]

    dates = list(next(iter(params.values())).keys())
    out = pd.DataFrame(index=dates)
    out["location_id"] = location_id
    out["timestamp_utc"] = pd.to_datetime(dates, format="%Y%m%d", utc=True)
    out["source"] = "NASA_POWER"

    def col(name):
        if name not in params:
            return np.nan
        s = pd.Series(params[name])
        return s.replace(fill, np.nan)

    out["temp_c"] = col("T2M")
    out["rh_pct"] = col("RH2M")
    out["dewpoint_c"] = col("T2MDEW")
    out["precip_mm"] = col("PRECTOTCORR")
    out["wind_speed_ms"] = col("WS2M")
    out["pressure_surface_hpa"] = col("PS") * 10.0 if "PS" in params else np.nan  # kPa -> hPa
    out["solar_rad_wm2"] = col("ALLSKY_SFC_SW_DWN") * 1e6 / 86400.0 if "ALLSKY_SFC_SW_DWN" in params else np.nan  # MJ/m2/day -> W/m2

    for c in WEATHEROBS_COLUMNS:
        if c not in out.columns:
            out[c] = np.nan
    return out[WEATHEROBS_COLUMNS].reset_index(drop=True)


# ---------------------------------------------------------------------------
# Open-Meteo Historical: JSON wide, hourly arrays song song theo index
# ---------------------------------------------------------------------------
def parse_openmeteo(filepath: str, location_id: str) -> pd.DataFrame:
    with open(filepath, encoding="utf-8") as f:
        d = json.load(f)
    hourly = d["hourly"]
    times = hourly["time"]

    out = pd.DataFrame(index=range(len(times)))
    out["location_id"] = location_id
    out["timestamp_utc"] = pd.to_datetime(times, utc=True)
    out["source"] = "OPEN_METEO"

    def col(name):
        return pd.Series(hourly[name]) if name in hourly else np.nan

    out["temp_c"] = col("temperature_2m")
    out["rh_pct"] = col("relative_humidity_2m")
    out["precip_mm"] = col("precipitation")
    # Open-Meteo mặc định trả gió theo km/h (hourly_units) -> phải đổi sang m/s
    wind_unit = d.get("hourly_units", {}).get("wind_speed_10m", "km/h")
    wind_factor = {"km/h": 1 / 3.6, "m/s": 1.0, "mp/h": 0.44704, "kn": 0.514444}[wind_unit]
    out["wind_speed_ms"] = col("wind_speed_10m") * wind_factor
    out["wind_dir_deg"] = col("wind_direction_10m")
    out["pressure_msl_hpa"] = col("pressure_msl")
    out["solar_rad_wm2"] = col("shortwave_radiation")

    for c in WEATHEROBS_COLUMNS:
        if c not in out.columns:
            out[c] = np.nan
    return out[WEATHEROBS_COLUMNS].reset_index(drop=True)
