"""
Parser cho 4 nguồn điểm (GHCN-Daily, NOAA ISD, NASA POWER, Open-Meteo) ->
Mediated Schema WeatherObs đã thiết kế ở docs/06-truong-du-lieu-va-tich-hop.md mục 2.

Cột chuẩn đầu ra (mọi hàm parse_* đều trả đúng tập cột này, NaN nếu nguồn không có):
    location_id, timestamp_utc, source,
    temp_c, rh_pct, dewpoint_c,
    precip_mm, wind_speed_ms, wind_dir_deg,
    pressure_surface_hpa, pressure_msl_hpa,
    solar_rad_wm2, cloud_cover_pct, soil_temp_c, soil_moist_m3m3,
    temp_def, qc_flag

Mọi giá trị số đã chuẩn hoá đơn vị thật (không phải giá trị thô trong file gốc). Kiểm soát chất lượng
theo docs/17 mục 3 (tầng 1–4): giá trị bị chính nguồn đánh dấu lỗi QC hoặc ngoài khoảng vật lý được đặt
NaN; lý do ghi vào `qc_flag` (nhiều lý do nối bằng ";"); dòng KHÔNG bị xoá. Nhảy giá trị phi vật lý chỉ
gắn cờ (không biết điểm nào trong 2 điểm liền nhau là điểm sai).
"""
import json

import numpy as np
import pandas as pd

WEATHEROBS_COLUMNS = [
    "location_id", "timestamp_utc", "source",
    "temp_c", "rh_pct", "dewpoint_c",
    "precip_mm", "wind_speed_ms", "wind_dir_deg",
    "pressure_surface_hpa", "pressure_msl_hpa",
    "solar_rad_wm2", "cloud_cover_pct", "soil_temp_c", "soil_moist_m3m3",
    "temp_def", "qc_flag",
]
TEXT_COLUMNS = ["location_id", "source", "temp_def", "qc_flag"]
NUMERIC_COLUMNS = [c for c in WEATHEROBS_COLUMNS if c not in TEXT_COLUMNS and c != "timestamp_utc"]

# Định nghĩa nhiệt độ (docs/17 mục 5): không trộn trong cùng một chuỗi xu hướng
TEMP_DEF_INSTANT = "INST"            # giá trị tức thời theo giờ (ISD, ERA5, Open-Meteo)
TEMP_DEF_DAILY_MEAN = "DAILY_MEAN"   # trung bình ngày của sản phẩm (NASA POWER)
TEMP_DEF_TAVG = "TAVG"               # GHCN TAVG (trung bình các giờ quan trắc)
TEMP_DEF_MIDRANGE = "TMAX_TMIN_MID"  # GHCN (TMAX + TMIN) / 2 khi thiếu TAVG

# Giới hạn vật lý cho Đông Nam Á (biên ngoài theo kỷ lục thế giới / khu vực) — docs/17 mục 3, tầng 2
PHYSICAL_RANGES = {
    "temp_c": (-10, 50), "dewpoint_c": (-30, 35), "rh_pct": (0, 100), "precip_mm": (0, 600),
    "wind_speed_ms": (0, 75), "wind_dir_deg": (0, 360), "pressure_msl_hpa": (870, 1085),
    "pressure_surface_hpa": (600, 1085), "solar_rad_wm2": (0, 1400), "cloud_cover_pct": (0, 100),
}
# Tầng 4 — nhảy giá trị phi vật lý ở cùng trạm: (ngưỡng thay đổi, cửa sổ giờ). Áp suất MSL ngoài tâm bão hiếm
# khi đổi quá vài hPa/giờ; ví dụ thật: ISD Phnom Penh 3/7/2023 nhảy 1028,6 -> 1053,6 hPa trong 3 giờ (đã "qua QC").
JUMP_LIMITS = {"temp_c": (10.0, 1.0), "pressure_msl_hpa": (10.0, 3.0)}
ISD_BAD_QC = {"2", "3", "6", "7"}       # ISD: 2/6 nghi ngờ, 3/7 sai (1, 5 = qua QC; 0, 4 = qua giới hạn thô)
ISD_REPORT_PRIORITY = {"FM-15": 0, "FM-12": 1}  # khi trùng (trạm, thời điểm): METAR rồi SYNOP rồi loại khác
WIND_Z0_M = 0.1                          # độ nhám bề mặt cho hồ sơ gió logarit khi phải quy 2 m -> 10 m


def _empty_weatherobs() -> pd.DataFrame:
    return pd.DataFrame({c: pd.Series(dtype="object") for c in WEATHEROBS_COLUMNS})


def _finalize(out: pd.DataFrame) -> pd.DataFrame:
    for c in WEATHEROBS_COLUMNS:
        if c not in out.columns:
            out[c] = np.nan
    if "qc_flag" in out:
        out["qc_flag"] = out["qc_flag"].replace("", np.nan)
    return out[WEATHEROBS_COLUMNS].reset_index(drop=True)


def add_flag(flags: pd.Series, mask, text: str) -> pd.Series:
    """Nối thêm `text` vào cờ của các dòng có mask True (cờ cách nhau bằng ';')."""
    mask = pd.Series(mask, index=flags.index).fillna(False).astype(bool)
    if not mask.any():
        return flags
    cur = flags.where(flags.notna(), "")
    new = cur.where(~mask, np.where(cur == "", text, cur + ";" + text))
    return new.replace("", np.nan)


def apply_range_checks(out: pd.DataFrame) -> pd.DataFrame:
    """Tầng 2: giá trị ngoài khoảng vật lý -> NaN + cờ RANGE:<cột>."""
    if "qc_flag" not in out:
        out["qc_flag"] = np.nan
    for col, (lo, hi) in PHYSICAL_RANGES.items():
        if col not in out:
            continue
        v = pd.to_numeric(out[col], errors="coerce")
        bad = v.notna() & ((v < lo) | (v > hi))
        if bad.any():
            out["qc_flag"] = add_flag(out["qc_flag"], bad, f"RANGE:{col}")
            out.loc[bad, col] = np.nan
    return out


def flag_jumps(out: pd.DataFrame, limits: dict = None) -> pd.DataFrame:
    """Tầng 4: biến đổi > ngưỡng trong <= cửa sổ giờ giữa 2 quan trắc liên tiếp (có giá trị) ở cùng trạm
    -> cờ JUMP:<cột> ở cả 2 điểm (giữ giá trị — không biết điểm nào sai)."""
    limits = JUMP_LIMITS if limits is None else limits
    for col, (max_change, window_h) in limits.items():
        if col not in out:
            continue
        o = out[["location_id", "timestamp_utc", col]].dropna().sort_values(["location_id", "timestamp_utc"])
        same = o["location_id"].eq(o["location_id"].shift())
        dt_h = o["timestamp_utc"].diff().dt.total_seconds() / 3600
        jump = same & (dt_h <= window_h) & (o[col].diff().abs() > max_change)
        both = (jump | jump.shift(-1, fill_value=False)).reindex(out.index, fill_value=False)
        out["qc_flag"] = add_flag(out["qc_flag"], both, f"JUMP:{col}")
    return out


# ---------------------------------------------------------------------------
# GHCN-Daily: dạng "long" (1 dòng/1 biến/1 ngày) -> PIVOT bắt buộc (docs/06 mục 2)
# ---------------------------------------------------------------------------
def parse_ghcn(filepath: str) -> pd.DataFrame:
    """ID,DATE,ELEMENT,DATA_VALUE,M_FLAG,Q_FLAG,S_FLAG,OBS_TIME
    DATA_VALUE của TMAX/TMIN/TAVG tính bằng 1/10 độ C, PRCP tính bằng 1/10 mm (chuẩn GHCN).
    Q_FLAG khác rỗng = giá trị KHÔNG qua kiểm soát chất lượng của NOAA (O outlier, I không nhất quán,
    G khoảng trống, D trùng, K lặp giá trị...) -> bỏ giá trị, ghi cờ GHCN_Q:<ELEMENT>=<mã>.
    Lưu ý (docs/17 mục 6): DATE là ngày quan trắc theo GIỜ ĐỊA PHƯƠNG, được gán 00:00 UTC.
    """
    raw = pd.read_csv(filepath, dtype={"ID": str, "DATE": str, "Q_FLAG": str})
    if raw.empty:
        return _empty_weatherobs()

    station_id = raw["ID"].iloc[0]
    failed = raw["Q_FLAG"].notna() & raw["ELEMENT"].isin(["TAVG", "TMAX", "TMIN", "PRCP"])
    flags_by_date = (raw[failed].assign(f="GHCN_Q:" + raw["ELEMENT"] + "=" + raw["Q_FLAG"])
                     .groupby("DATE")["f"].agg(";".join))
    raw.loc[failed, "DATA_VALUE"] = np.nan
    pivot = raw.pivot_table(index="DATE", columns="ELEMENT", values="DATA_VALUE", aggfunc="first", dropna=False)

    out = pd.DataFrame(index=pivot.index)
    out["location_id"] = station_id
    out["timestamp_utc"] = pd.to_datetime(pivot.index, format="%Y%m%d", utc=True)
    out["source"] = "GHCN"
    tavg = pivot["TAVG"] / 10.0 if "TAVG" in pivot else pd.Series(np.nan, index=pivot.index)
    mid = ((pivot["TMAX"] + pivot["TMIN"]) / 2.0 / 10.0 if {"TMAX", "TMIN"} <= set(pivot.columns)
           else pd.Series(np.nan, index=pivot.index))
    out["temp_c"] = tavg.where(tavg.notna(), mid)
    out["temp_def"] = np.where(tavg.notna(), TEMP_DEF_TAVG, np.where(mid.notna(), TEMP_DEF_MIDRANGE, None))
    out["precip_mm"] = (pivot["PRCP"] / 10.0) if "PRCP" in pivot else np.nan
    out["qc_flag"] = flags_by_date.reindex(pivot.index)
    return _finalize(apply_range_checks(out))


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


def _isd_component(series: pd.Series, idx: int, qc_idx: int, missing: set, scale: float):
    """Trả (giá trị, mã QC) của một thành phần trong trường nén ISD, dạng vector."""
    parts = series.fillna("").astype(str).str.split(",", expand=True)
    if parts.shape[1] <= max(idx, qc_idx):
        nan = pd.Series(np.nan, index=series.index)
        return nan, pd.Series(None, index=series.index, dtype=object)
    num = pd.to_numeric(parts[idx], errors="coerce")
    num = num.where(~num.isin(missing)) / scale
    return num, parts[qc_idx]


def parse_isd(filepath: str) -> pd.DataFrame:
    """WND='dir,dirQC,type,speed_tenths_ms,speedQC' (missing dir=999, speed=9999)
    TMP='temp_tenths_C,QC' (missing=+9999)
    DEW='dewpoint_tenths_C,QC' (missing=+9999)
    SLP='pressure_tenths_hPa,QC' (missing=99999)
    MA1='altimeter_tenths_hPa,QC,station_pressure_tenths_hPa,QC' (missing=99999) — chỉ lấy áp suất
        trạm (áp suất bề mặt thật); KHÔNG dùng altimeter/QNH thay SLP vì lệch SLP theo độ cao trạm
        (-0,4 hPa trạm thấp, +1,5 hPa trạm cao — docs/17 mục 5).
    Mã QC thành phần 2/3/6/7 -> bỏ giá trị, cờ ISD_QC:<trường>=<mã>.
    Bản tin trùng (cùng trạm, cùng thời điểm; METAR FM-15 và SYNOP FM-12 gửi cùng quan trắc) -> gộp
    thành 1 dòng, lấy giá trị không rỗng đầu tiên theo thứ tự ưu tiên FM-15, FM-12, loại khác.
    """
    raw = pd.read_csv(filepath, dtype=str, low_memory=False)
    if raw.empty:
        return _empty_weatherobs()

    out = pd.DataFrame(index=raw.index)
    out["location_id"] = raw["STATION"]
    out["timestamp_utc"] = pd.to_datetime(raw["DATE"], utc=True)
    out["source"] = "ISD"
    out["temp_def"] = TEMP_DEF_INSTANT
    out["qc_flag"] = np.nan

    def take(field, col, idx, qc_idx, missing, scale):
        if field not in raw:
            out[col] = np.nan
            return
        val, qc = _isd_component(raw[field], idx, qc_idx, missing, scale)
        bad = val.notna() & qc.isin(ISD_BAD_QC)
        for code in sorted(qc[bad].unique()):
            out["qc_flag"] = add_flag(out["qc_flag"], bad & (qc == code), f"ISD_QC:{col}={code}")
        out[col] = val.where(~bad)

    take("TMP", "temp_c", 0, 1, {9999}, 10)
    take("DEW", "dewpoint_c", 0, 1, {9999}, 10)
    take("SLP", "pressure_msl_hpa", 0, 1, {99999}, 10)
    take("MA1", "pressure_surface_hpa", 2, 3, {99999}, 10)
    take("WND", "wind_dir_deg", 0, 1, {999}, 1)
    take("WND", "wind_speed_ms", 3, 4, {9999}, 10)

    # Khử trùng (trạm, thời điểm): first() lấy giá trị không rỗng đầu tiên theo thứ tự ưu tiên bản tin
    prio = raw["REPORT_TYPE"].map(ISD_REPORT_PRIORITY).fillna(9) if "REPORT_TYPE" in raw else 0
    out = out.assign(_prio=prio).sort_values(["location_id", "timestamp_utc", "_prio"]).drop(columns="_prio")
    keys = ["location_id", "timestamp_utc"]
    num_cols = ["temp_c", "dewpoint_c", "pressure_msl_hpa", "pressure_surface_hpa", "wind_dir_deg", "wind_speed_ms"]
    merged = out.groupby(keys, sort=False)[num_cols + ["source", "temp_def"]].first()
    flagged = out.dropna(subset=["qc_flag"])  # chỉ gộp cờ ở số ít dòng có cờ (tránh lambda trên mọi nhóm)
    if len(flagged):
        merged["qc_flag"] = flagged.groupby(keys)["qc_flag"].agg(
            lambda s: ";".join(sorted(set(";".join(s).split(";")))))
    else:
        merged["qc_flag"] = np.nan
    out = merged.reset_index()

    # RH% suy từ Dew Point bằng Clausius-Clapeyron thật (không phải nội suy — xem docs/06 mục 4b)
    out["rh_pct"] = clausius_clapeyron_rh(out["temp_c"], out["dewpoint_c"])
    out = apply_range_checks(out)
    out = flag_jumps(out)
    return _finalize(out)


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


def wind_2m_to_10m(ws_2m, z0: float = WIND_Z0_M):
    """Quy tốc độ gió đo ở 2 m về 10 m theo hồ sơ gió logarit (khí quyển trung tính):
    u(10) = u(2) · ln(10 / z0) / ln(2 / z0)."""
    return ws_2m * np.log(10 / z0) / np.log(2 / z0)


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
    out["temp_def"] = TEMP_DEF_DAILY_MEAN
    out["qc_flag"] = np.nan

    def col(name):
        if name not in params:
            return np.nan
        s = pd.Series(params[name])
        return s.replace(fill, np.nan)

    out["temp_c"] = col("T2M")
    out["rh_pct"] = col("RH2M")
    out["dewpoint_c"] = col("T2MDEW")
    out["precip_mm"] = col("PRECTOTCORR")
    # Gió ở 10 m như các nguồn khác (docs/17 mục 5): ưu tiên WS10M; file cũ chỉ có WS2M (gió 2 m, chỉ
    # bằng ~0,71 lần gió 10 m đo thật) thì quy đổi theo hồ sơ logarit và gắn cờ
    if "WS10M" in params:
        out["wind_speed_ms"] = col("WS10M")
    elif "WS2M" in params:
        out["wind_speed_ms"] = wind_2m_to_10m(col("WS2M"))
        out["qc_flag"] = add_flag(out["qc_flag"], out["wind_speed_ms"].notna(), "WIND_2M_TO_10M")
    out["pressure_surface_hpa"] = col("PS") * 10.0 if "PS" in params else np.nan  # kPa -> hPa
    out["solar_rad_wm2"] = col("ALLSKY_SFC_SW_DWN") * 1e6 / 86400.0 if "ALLSKY_SFC_SW_DWN" in params else np.nan  # MJ/m2/day -> W/m2
    return _finalize(apply_range_checks(out))


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
    out["temp_def"] = TEMP_DEF_INSTANT
    out["qc_flag"] = np.nan

    def col(name):
        return pd.Series(hourly[name], dtype="float64") if name in hourly else np.nan

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
    return _finalize(apply_range_checks(out))
