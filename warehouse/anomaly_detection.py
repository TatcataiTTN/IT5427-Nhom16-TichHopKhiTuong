#!/usr/bin/env python3
"""
Phát hiện dị thường khí hậu trên warehouse WeatherObs (mục tiêu chính của đề tài, docs/01 mục 2).

Phương pháp (chuẩn khí tượng, không tự đặt ngưỡng tuỳ ý):
  1. Tổng hợp theo ngày bằng Spark (~9 triệu dòng -> ~1 triệu ngày-trạm). Ngày của nguồn đo theo
     giờ chỉ hợp lệ khi phủ đủ 4 khối 6 giờ (tránh lệch theo chu kỳ ngày đêm khi thiếu quan trắc đêm).
  2. Khí hậu nền (climatology) theo (vị trí, nguồn, ngày-trong-năm) với cửa sổ trượt ±15 ngày, tính
     bằng Spark: trung bình, độ lệch chuẩn, bách phân vị 90. Giai đoạn nền:
       GHCN 1991–2020 (chuẩn khí hậu WMO); ISD 2015–2024; ERA5/Open-Meteo/NASA POWER 2020–2024
     (nền ngắn < 30 năm được gắn cờ `nen_ngan` — năm cần đánh giá nằm trong chính giai đoạn nền).
  3. Dị thường chuẩn hoá z = (x − trung bình nền) / độ lệch chuẩn nền; |z| ≥ 2 bất thường, ≥ 3 cực đoan.
  4. Đợt nóng: ≥ 3 ngày liên tiếp nhiệt độ trung bình ngày > bách phân vị 90 của nền
     (chỉ số TG90p của ETCCDI/WMO, gom thành đợt).
  5. SPI-1 / SPI-3 (Standardized Precipitation Index, McKee 1993) cho trạm GHCN: khớp phân bố gamma
     theo từng tháng trên nền 1991–2020, xử lý riêng xác suất tháng không mưa.
  6. Xác nhận chéo đa nguồn: dị thường tại trạm (GHCN/ISD) được đối chiếu với ERA5 nội suy tại CÙNG vị
     trí, cùng ngày -> phân biệt dị thường khí hậu thật với nghi lỗi dữ liệu/cảm biến.

Chạy:  python3 warehouse/anomaly_detection.py      (cần JAVA_HOME trỏ JDK 17/21, xem README)
Output (warehouse/output/, gitignored):
  weather_daily.parquet, anomaly_daily.parquet, heatwave_events.parquet, spi_monthly.parquet,
  anomaly_summary.json (số liệu kiểm chứng với sự kiện thật)
"""
import json
import os

import numpy as np
import pandas as pd

OUT = os.path.join(os.path.dirname(__file__), "output")
WAREHOUSE = os.path.join(OUT, "weatherobs.parquet")

BASELINES = {  # nguồn -> (năm đầu, năm cuối) của giai đoạn nền
    "GHCN": (1991, 2020),
    "ISD": (2015, 2024),
    "ERA5": (2020, 2024),
    "OPEN_METEO": (2020, 2024),
    "NASA_POWER": (2020, 2024),
}
SHORT_BASELINE_YEARS = 30   # WMO: chuẩn khí hậu cần 30 năm
WINDOW = 15                 # cửa sổ ±15 ngày quanh ngày-trong-năm
MIN_CLIM_N = 100            # số ngày tối thiểu trong cửa sổ nền để tin được thống kê
Z_ANOMALY, Z_EXTREME = 2.0, 3.0
HEATWAVE_MIN_DAYS = 3
HOURLY_SOURCES = ("ISD", "ERA5", "OPEN_METEO")
NEIGHBOR_RADIUS_KM = 200    # bán kính tìm trạm lân cận (mạng trạm ĐNA thưa: 43/61 trạm có >= 1 láng giềng)
SAME_SITE_KM = 5            # dưới ngưỡng này coi là CÙNG trạm vật lý (cặp GHCN<->ISD của Entity Resolution)
DAILY_VARS = ["temp_mean", "pmsl_min"]  # biến tính dị thường chuẩn hoá (xấp xỉ phân bố chuẩn)


# ----------------------------------------------------------------------------------------------
# Hàm thuần (pandas/numpy) — có unit test ở tests/test_anomaly.py
# ----------------------------------------------------------------------------------------------
def doy365(dates: pd.Series) -> pd.Series:
    """Ngày-trong-năm 1..365; 29/2 gộp vào 28/2 để năm nhuận và năm thường thẳng hàng."""
    d = pd.to_datetime(dates)
    doy = d.dt.dayofyear
    after_feb = d.dt.is_leap_year & (d.dt.month > 2)
    return (doy - after_feb.astype(int)).where(~(d.dt.is_leap_year & (d.dt.month == 2) & (d.dt.day == 29)), 59)


def anomaly_flag(z: pd.Series) -> pd.Series:
    a = z.abs()
    return np.select([a >= Z_EXTREME, a >= Z_ANOMALY], ["cuc_doan", "bat_thuong"], "binh_thuong")


def heatwave_events(df: pd.DataFrame, min_days: int = HEATWAVE_MIN_DAYS, max_gap: int = 1) -> pd.DataFrame:
    """df: location_id, source, date, temp_mean, clim_p90. Trả các đợt có ≥ min_days ngày nóng
    (temp_mean > clim_p90) liên tiếp theo lịch. Chỉ một ngày CÓ dữ liệu mà không nóng mới làm đứt đợt;
    khoảng THIẾU dữ liệu ≤ max_gap ngày giữa 2 ngày nóng được nối qua (thiếu số liệu ≠ trời mát —
    vd GHCN thiếu 1/5/2024 ở nhiều trạm giữa đợt nắng nóng). `days` = số ngày nóng thật, `span_days`
    = độ dài đợt theo lịch (gồm cả ngày thiếu dữ liệu được nối)."""
    cols = ["location_id", "source", "start", "end", "days", "span_days", "max_excess_c"]
    obs = df.dropna(subset=["temp_mean", "clim_p90"]).sort_values(["location_id", "source", "date"]).copy()
    if obs.empty:
        return pd.DataFrame(columns=cols)
    obs["date"] = pd.to_datetime(obs["date"])
    obs["hot"] = obs["temp_mean"] > obs["clim_p90"]
    same_series = (obs["location_id"] == obs["location_id"].shift()) & (obs["source"] == obs["source"].shift())
    gap = obs["date"].diff().dt.days
    # Đợt mới bắt đầu ở mỗi ngày nóng mà ngày CÓ dữ liệu liền trước (cùng chuỗi) không nóng hoặc cách quá xa
    starts = obs["hot"] & ~(same_series & obs["hot"].shift(fill_value=False) & (gap <= max_gap + 1))
    obs["run"] = starts.cumsum().where(obs["hot"])
    hot = obs[obs["hot"]].copy()
    if hot.empty:
        return pd.DataFrame(columns=cols)
    hot["excess"] = hot["temp_mean"] - hot["clim_p90"]
    ev = hot.groupby("run").agg(location_id=("location_id", "first"), source=("source", "first"),
                                start=("date", "min"), end=("date", "max"), days=("date", "size"),
                                max_excess_c=("excess", "max"))
    ev["span_days"] = (ev["end"] - ev["start"]).dt.days + 1
    ev["start"], ev["end"] = ev["start"].dt.date, ev["end"].dt.date
    return ev[ev["days"] >= min_days][cols].reset_index(drop=True)


def spi_from_totals(totals: pd.Series, baseline: pd.Series) -> pd.Series:
    """SPI cho 1 trạm × 1 tháng-lịch: khớp gamma (floc=0) trên các tổng mưa > 0 của giai đoạn nền,
    H(x) = q + (1−q)·G(x) với q = tỷ lệ tổng mưa bằng 0, SPI = Φ⁻¹(H)."""
    from scipy import stats
    base = baseline.dropna()
    pos = base[base > 0]
    if len(base) < 20 or len(pos) < 10:
        return pd.Series(np.nan, index=totals.index)
    q = 1 - len(pos) / len(base)
    a, _, scale = stats.gamma.fit(pos, floc=0)
    h = q + (1 - q) * stats.gamma.cdf(totals.clip(lower=0), a, loc=0, scale=scale)
    return pd.Series(stats.norm.ppf(np.clip(h, 1e-6, 1 - 1e-6)), index=totals.index).where(totals.notna())


WET_DAY_MM = 1.0        # ETCCDI: ngày ướt khi lượng mưa ≥ 1 mm
MIN_WET_DAYS = 100      # số ngày ướt tối thiểu trong nền để ước lượng p95/p99 tin cậy
MIN_YEAR_COVERAGE = 0.9 # chỉ số năm chỉ tính khi ≥ 90% số ngày có số liệu mưa


def wet_day_percentiles(daily: pd.DataFrame, baselines: dict = None) -> pd.DataFrame:
    """Ngưỡng mưa lớn theo ETCCDI: bách phân vị 95/99 của các NGÀY ƯỚT (≥ 1 mm) trong giai đoạn nền,
    theo (vị trí, nguồn). Không theo mùa — đúng định nghĩa R95p/R99p của ETCCDI."""
    baselines = baselines or BASELINES
    d = daily.dropna(subset=["precip_sum"])
    year = pd.to_datetime(d["date"]).dt.year
    in_base = pd.Series(False, index=d.index)
    for src, (y0, y1) in baselines.items():
        in_base |= (d["source"] == src) & year.between(y0, y1)
    wet = d[in_base & (d["precip_sum"] >= WET_DAY_MM)]
    p = wet.groupby(["location_id", "source"])["precip_sum"].agg(
        p95=lambda s: s.quantile(0.95), p99=lambda s: s.quantile(0.99), n_wet="size").reset_index()
    return p[p["n_wet"] >= MIN_WET_DAYS]


def precip_extreme_flag(precip: pd.Series, p95: pd.Series, p99: pd.Series) -> pd.Series:
    return pd.Series(np.select([precip > p99, precip > p95], ["mua_cuc_doan", "mua_lon"], "binh_thuong"),
                     index=precip.index)


def precip_annual_indices(daily: pd.DataFrame, pct: pd.DataFrame) -> pd.DataFrame:
    """Chỉ số ETCCDI theo năm: PRCPTOT (tổng mưa ngày ướt), Rx1day (mưa ngày lớn nhất),
    R95p/R99p (tổng mưa của các ngày vượt p95/p99), R95pTOT (% đóng góp của mưa lớn).
    Năm thiếu > 10% số ngày có số liệu mưa bị bỏ (Rx1day/R95p sẽ bị đánh giá thấp)."""
    d = daily.dropna(subset=["precip_sum"]).merge(pct, on=["location_id", "source"], how="inner")
    d["year"] = pd.to_datetime(d["date"]).dt.year
    wet = d["precip_sum"] >= WET_DAY_MM
    d["wet_precip"] = d["precip_sum"].where(wet, 0.0)
    d["r95"] = d["precip_sum"].where(wet & (d["precip_sum"] > d["p95"]), 0.0)
    d["r99"] = d["precip_sum"].where(wet & (d["precip_sum"] > d["p99"]), 0.0)
    out = d.groupby(["location_id", "source", "year"]).agg(
        n_days=("precip_sum", "size"), PRCPTOT=("wet_precip", "sum"), Rx1day=("precip_sum", "max"),
        R95p=("r95", "sum"), R99p=("r99", "sum")).reset_index()
    days_in_year = np.where(pd.to_datetime(out["year"].astype(str) + "-12-31").dt.is_leap_year, 366, 365)
    out = out[out["n_days"] >= MIN_YEAR_COVERAGE * days_in_year].copy()
    out["R95pTOT_pct"] = (100 * out["R95p"] / out["PRCPTOT"].where(out["PRCPTOT"] > 0)).round(1)
    return out


def haversine_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(a))


def neighbor_pairs(stations: pd.DataFrame, radius_km: float = NEIGHBOR_RADIUS_KM,
                   same_site_km: float = SAME_SITE_KM) -> pd.DataFrame:
    """Cặp (trạm, trạm lân cận) cách nhau trong (same_site_km, radius_km]. Bỏ các cặp gần hơn same_site_km:
    đó là cùng một trạm vật lý được GHCN và ISD gán 2 mã (cùng cảm biến) — không phải bằng chứng độc lập."""
    s = stations[["location_id", "lat", "lon"]].dropna().drop_duplicates("location_id").reset_index(drop=True)
    d = haversine_km(s["lat"].values[:, None], s["lon"].values[:, None], s["lat"].values[None], s["lon"].values[None])
    i, j = np.where((d > same_site_km) & (d <= radius_km))
    return pd.DataFrame({"location_id": s["location_id"].values[i], "nb_id": s["location_id"].values[j],
                         "dist_km": d[i, j]})


def neighbor_support(anoms: pd.DataFrame, z_all: pd.DataFrame, pairs: pd.DataFrame) -> pd.DataFrame:
    """Với mỗi dị thường (location_id, date, var, z), đếm trạm lân cận có số liệu cùng ngày, cùng biến
    (n_lan_can) và tỷ lệ lân cận lệch CÙNG chiều với |z| >= 1 (ty_le_lan_can_dong_y)."""
    nb = (anoms[["location_id", "date", "var", "z"]].reset_index()
          .merge(pairs, on="location_id")
          .merge(z_all.rename(columns={"location_id": "nb_id", "z": "z_nb"}), on=["nb_id", "date", "var"]))
    nb = nb.dropna(subset=["z_nb"]).drop_duplicates(["index", "nb_id"])
    nb["agree"] = (np.sign(nb["z_nb"]) == np.sign(nb["z"])) & (nb["z_nb"].abs() >= 1.0)
    agg = nb.groupby("index").agg(n_lan_can=("nb_id", "size"), ty_le_lan_can_dong_y=("agree", "mean"))
    out = pd.DataFrame(index=anoms.index)
    out["n_lan_can"] = agg["n_lan_can"].reindex(anoms.index).fillna(0).astype(int)
    out["ty_le_lan_can_dong_y"] = agg["ty_le_lan_can_dong_y"].reindex(anoms.index)
    return out


def classify_combined(z_station: pd.Series, z_era5: pd.Series, n_nb: pd.Series, frac_nb: pd.Series) -> pd.Series:
    """Phân loại dị thường tại trạm theo 2 nguồn đối chứng độc lập: ERA5 cùng vị trí và trạm lân cận.
      xac_nhan_khi_hau  — ERA5 cùng chiều (|z| >= 1) HOẶC >= 50% trạm lân cận cùng chiều (|z| >= 1)
      nghi_loi_du_lieu  — trạm cực đoan (|z| >= 3), có ít nhất 1 đối chứng, và MỌI đối chứng hiện có đều
                          không ủng hộ (ERA5 |z| < 0,5 hoặc ngược chiều; < 20% lân cận cùng chiều)
      di_thuong_cuc_bo  — có đối chứng nhưng chỉ ủng hộ yếu (hiện tượng cục bộ, đối chứng không bắt được)
      khong_doi_chung   — không có ERA5 (trước 2020) lẫn trạm lân cận cùng ngày"""
    has_e5, has_nb = z_era5.notna(), n_nb > 0
    same = np.sign(z_station) == np.sign(z_era5)
    e5_agree = has_e5 & same & (z_era5.abs() >= 1.0)
    e5_reject = has_e5 & ((z_era5.abs() < 0.5) | ~same)
    nb_agree = has_nb & (frac_nb >= 0.5)
    nb_reject = has_nb & (frac_nb < 0.2)
    extreme = z_station.abs() >= Z_EXTREME
    return pd.Series(np.select(
        [~has_e5 & ~has_nb,
         e5_agree | nb_agree,
         extreme & (e5_reject | ~has_e5) & (nb_reject | ~has_nb)],
        ["khong_doi_chung", "xac_nhan_khi_hau", "nghi_loi_du_lieu"], "di_thuong_cuc_bo"), index=z_station.index)


def classify_cross_source(z_station: pd.Series, z_era5: pd.Series) -> pd.Series:
    """Phân loại dị thường tại trạm theo ERA5 cùng vị trí/ngày:
      khong_co_era5     — ERA5 không có ngày đó (ERA5 chỉ có 2020–2024)
      xac_nhan_khi_hau  — ERA5 cùng chiều và |z_ERA5| ≥ 1 -> tín hiệu khí hậu thật trên diện rộng
      nghi_loi_du_lieu  — trạm cực đoan (|z| ≥ 3) nhưng ERA5 gần bình thường (|z| < 0,5) hoặc ngược chiều
      chua_xac_dinh     — còn lại (dị thường cục bộ, ERA5 ~28 km có thể không bắt được)"""
    same_sign = np.sign(z_station) == np.sign(z_era5)
    return pd.Series(np.select(
        [z_era5.isna(),
         same_sign & (z_era5.abs() >= 1.0),
         (z_station.abs() >= Z_EXTREME) & ((z_era5.abs() < 0.5) | ~same_sign)],
        ["khong_co_era5", "xac_nhan_khi_hau", "nghi_loi_du_lieu"], "chua_xac_dinh"), index=z_station.index)


# ----------------------------------------------------------------------------------------------
# Bước Spark
# ----------------------------------------------------------------------------------------------
def spark_doy(date_col: str = "date"):
    """Ngày-trong-năm 1..365 trong Spark (29/2 gộp vào 28/2) — khớp doy365() và dùng chung cho
    batch lẫn streaming (warehouse/spark_streaming_anomaly.py)."""
    from pyspark.sql import functions as F
    d = F.col(date_col)
    leap_after_feb = (F.month(d) > 2) & (F.year(d) % 4 == 0)
    return F.when((F.month(d) == 2) & (F.dayofmonth(d) == 29), 59).otherwise(
        F.dayofyear(d) - F.when(leap_after_feb, 1).otherwise(0))


def build_daily(spark):
    """WeatherObs (giờ/ngày, nhiều nguồn) -> 1 dòng/(vị trí, nguồn, ngày)."""
    from pyspark.sql import functions as F
    df = spark.read.parquet(WAREHOUSE).withColumn("date", F.to_date("timestamp_utc"))
    block = F.floor(F.hour("timestamp_utc") / 6)
    daily = df.groupBy("location_id", "source", "date").agg(
        F.avg("temp_c").alias("temp_mean"),
        F.count("temp_c").alias("n_temp"),
        F.countDistinct(F.when(F.col("temp_c").isNotNull(), block)).alias("temp_blocks"),
        F.sum("precip_mm").alias("precip_sum"),
        F.count("precip_mm").alias("n_precip"),
        F.max("wind_speed_ms").alias("wind_max"),
        F.min("pressure_msl_hpa").alias("pmsl_min"),
    )
    hourly = F.col("source").isin(*HOURLY_SOURCES)
    # Ngày theo giờ: đủ 4 khối 6 giờ + ≥ 8 quan trắc (ISD) / ≥ 20 giờ (ERA5, Open-Meteo)
    temp_ok = F.when(hourly, (F.col("temp_blocks") == 4) &
                     (F.col("n_temp") >= F.when(F.col("source") == "ISD", 8).otherwise(20))).otherwise(F.col("n_temp") >= 1)
    precip_ok = F.when(F.col("source").isin("ERA5", "OPEN_METEO"), F.col("n_precip") >= 20) \
        .otherwise(F.col("n_precip") >= 1)
    return (daily
            .withColumn("temp_mean", F.when(temp_ok, F.col("temp_mean")))
            .withColumn("precip_sum", F.when(precip_ok & ~(F.col("source") == "ISD"), F.col("precip_sum")))
            .withColumn("year", F.year("date"))
            .withColumn("month", F.month("date"))
            .drop("temp_blocks"))


def build_climatology(spark, daily, var):
    """Khí hậu nền theo (vị trí, nguồn, ngày-trong-năm 1..365), cửa sổ ±WINDOW ngày, trên giai đoạn nền
    của từng nguồn. Nhân mỗi ngày nền thành 2·WINDOW+1 bản ghi lệch ngày rồi groupBy — chạy phân tán."""
    from pyspark.sql import functions as F
    cond = None
    for src, (y0, y1) in BASELINES.items():
        c = (F.col("source") == src) & F.col("year").between(y0, y1)
        cond = c if cond is None else cond | c
    leap_shift = F.when(F.expr("month(date) > 2 AND (year(date) % 4 = 0)"), 1).otherwise(0)
    base = (daily.filter(cond & F.col(var).isNotNull())
            .withColumn("doy", F.when(F.expr("month(date) = 2 AND day(date) = 29"), 59)
                        .otherwise(F.dayofyear("date") - leap_shift))
            .withColumn("off", F.explode(F.sequence(F.lit(-WINDOW), F.lit(WINDOW))))
            .withColumn("doy", F.pmod(F.col("doy") - 1 + F.col("off"), F.lit(365)) + 1))
    return base.groupBy("location_id", "source", "doy").agg(
        F.avg(var).alias("clim_mean"),
        F.stddev(var).alias("clim_std"),
        F.percentile_approx(var, 0.9, 1000).alias("clim_p90"),
        F.count(var).alias("clim_n"),
    ).filter(F.col("clim_n") >= MIN_CLIM_N)


# ----------------------------------------------------------------------------------------------
# Kiểm chứng với sự kiện thật
# ----------------------------------------------------------------------------------------------
def validate_events(anom: pd.DataFrame, events: pd.DataFrame, spi: pd.DataFrame, loc: pd.DataFrame,
                    precip_ext: pd.DataFrame = None) -> dict:
    names = loc.set_index("location_id")["name"].to_dict() if "name" in loc else {}
    country = loc.set_index("location_id")["country"].to_dict()
    out = {}

    # 1) Nắng nóng tháng 4–5/2024 (GHCN, nền WMO 1991–2020)
    t = anom[(anom["source"] == "GHCN") & (anom["var"] == "temp_mean") & anom["z"].notna()].copy()
    t["date"] = pd.to_datetime(t["date"])
    apr = t[(t["date"] >= "2024-04-01") & (t["date"] <= "2024-05-15")]
    ref = t[(t["date"].dt.month.isin([4, 5])) & (t["date"].dt.year.between(1991, 2020))]
    hw = events[(events["source"] == "GHCN") & (pd.to_datetime(events["start"]) <= "2024-05-15")
                & (pd.to_datetime(events["end"]) >= "2024-04-01")]
    top = apr.nlargest(8, "z")
    out["nang_nong_4_5_2024"] = {
        "so_tram": int(apr["location_id"].nunique()),
        "ty_le_ngay_z_ge_2": round(float((apr["z"] >= 2).mean()), 3),
        "ty_le_ngay_z_ge_2_cung_ky_1991_2020": round(float((ref["z"] >= 2).mean()), 3),
        "z_trung_binh": round(float(apr["z"].mean()), 2),
        "so_tram_co_dot_nong": int(hw["location_id"].nunique()),
        # So sánh từng năm: 2024 phải nổi bật hẳn — chứng tỏ bắt được sự kiện thật chứ không chỉ xu hướng ấm lên
        "ty_le_ngay_z_ge_2_thang_4_5_theo_nam": t[t["date"].dt.month.isin([4, 5]) & (t["date"].dt.year >= 2010)]
            .groupby(t["date"].dt.year)["z"].apply(lambda z: round(float((z >= 2).mean()), 3)).to_dict(),
        "dot_nong_dai_nhat": hw.nlargest(5, "days")[["location_id", "start", "end", "days", "span_days"]]
            .assign(country=lambda x: x["location_id"].map(country)).astype(str).to_dict("records"),
        "ngay_nong_bat_thuong_nhat": top[["location_id", "date", "value", "clim_mean", "z"]]
            .assign(country=lambda x: x["location_id"].map(country), date=lambda x: x["date"].dt.date)
            .round(2).astype(str).to_dict("records"),
    }

    # 2) Bão Yagi 6–8/9/2024: áp suất thấp bất thường (ERA5) tại trạm miền Bắc Việt Nam
    p = anom[(anom["source"] == "ERA5") & (anom["var"] == "pmsl_min") & anom["z"].notna()].copy()
    p["date"] = pd.to_datetime(p["date"])
    north_vn = loc[(loc["country"].astype(str).str.contains("Viet", case=False)) & (loc["lat"] > 20)]["location_id"]
    yagi = p[p["location_id"].isin(north_vn) & p["date"].between("2024-09-06", "2024-09-08")]
    out["bao_yagi_9_2024"] = {
        "so_tram_mien_bac_vn": int(yagi["location_id"].nunique()),
        "ap_suat_thap_nhat_hpa": round(float(yagi["value"].min()), 1) if len(yagi) else None,
        "z_thap_nhat": round(float(yagi["z"].min()), 2) if len(yagi) else None,
        "ty_le_tram_z_le_-3": round(float((yagi.groupby("location_id")["z"].min() <= -3).mean()), 2) if len(yagi) else None,
    }

    # 3) Hạn Mekong 2019–2020: SPI-3 trạm Thái Lan / Campuchia / Nam Việt Nam
    s = spi.copy()
    mekong = loc[loc["country"].astype(str).str.contains("Thai|Cambod", case=False)
                 | (loc["country"].astype(str).str.contains("Viet", case=False) & (loc["lat"] < 12))]["location_id"]
    dry = s[s["location_id"].isin(mekong) & s["period"].between("2019-06", "2020-05") & s["spi3"].notna()]
    clim = s[s["location_id"].isin(mekong) & s["spi3"].notna()]
    out["han_mekong_2019_2020"] = {
        "so_tram": int(dry["location_id"].nunique()),
        "spi3_trung_binh": round(float(dry["spi3"].mean()), 2) if len(dry) else None,
        "ty_le_thang_han_spi3_le_-1": round(float((dry["spi3"] <= -1).mean()), 3) if len(dry) else None,
        "ty_le_thang_han_toan_chuoi": round(float((clim["spi3"] <= -1).mean()), 3) if len(clim) else None,
    }

    # 4) Mưa cực đoan do bão Yagi 6–11/9/2024 tại miền Bắc Việt Nam (so với ngưỡng p99 ngày ướt của chính trạm)
    if precip_ext is not None and len(precip_ext):
        r = precip_ext.copy()
        r["date"] = pd.to_datetime(r["date"])
        yr = r[r["location_id"].isin(north_vn) & r["date"].between("2024-09-06", "2024-09-11")]
        top = yr.sort_values("ratio_p99", ascending=False).drop_duplicates(["location_id", "source"])
        out["mua_bao_yagi_9_2024"] = {
            "so_cap_tram_nguon_vuot_p99": int((top["precip_sum"] > top["p99"]).sum()),
            "so_cap_tram_nguon": int(len(top)),
            "lon_nhat": top.head(6)[["location_id", "source", "date", "precip_sum", "p99", "ratio_p99", "rank_in_record"]]
                .assign(date=lambda x: x["date"].dt.date).round(1).astype(str).to_dict("records"),
        }
    return out


def main():
    import sys
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as F
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from warehouse.location import build_location_table

    spark = (SparkSession.builder.appName("Nhom16-anomaly").master("local[*]")
             .config("spark.sql.session.timeZone", "UTC").config("spark.driver.memory", "4g").getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")

    print("== 1/6: Tong hop theo ngay (Spark) ==")
    daily = build_daily(spark).cache()
    daily.write.mode("overwrite").parquet(os.path.join(OUT, "weather_daily.parquet"))
    print(f"  {daily.count():,} ngay-vi-tri-nguon")

    print("== 2/6: Khi hau nen ±15 ngay + di thuong chuan hoa (Spark) ==")
    doy_col = spark_doy("date")
    parts, clims = [], []
    for var in DAILY_VARS:
        clim = build_climatology(spark, daily, var).cache()
        clims.append(clim.withColumn("var", F.lit(var)))
        a = (daily.filter(F.col(var).isNotNull()).withColumn("doy", doy_col)
             .join(clim, ["location_id", "source", "doy"], "inner")
             .select("location_id", "source", "date", F.lit(var).alias("var"), F.col(var).alias("value"),
                     "clim_mean", "clim_std", "clim_p90", "clim_n"))
        parts.append(a.toPandas())
    anom = pd.concat(parts, ignore_index=True)
    # Lưu khí hậu nền để luồng streaming đối chiếu từng bản ghi mới (warehouse/spark_streaming_anomaly.py)
    clims[0].unionByName(clims[1]).write.mode("overwrite").parquet(os.path.join(OUT, "climatology.parquet"))
    anom["z"] = (anom["value"] - anom["clim_mean"]) / anom["clim_std"].where(anom["clim_std"] > 0)
    anom["flag"] = anomaly_flag(anom["z"])
    anom["nen_ngan"] = anom["source"].map(lambda s: BASELINES[s][1] - BASELINES[s][0] + 1 < SHORT_BASELINE_YEARS)
    print(f"  {len(anom):,} gia tri co khi hau nen | bat thuong: {(anom.flag == 'bat_thuong').sum():,} "
          f"| cuc doan: {(anom.flag == 'cuc_doan').sum():,}")

    print("== 3/6: Xac nhan cheo tram vs ERA5 cung vi tri/ngay ==")
    era5 = anom[anom["source"] == "ERA5"][["location_id", "date", "var", "z"]].rename(columns={"z": "z_era5"})
    anom = anom.merge(era5, on=["location_id", "date", "var"], how="left")
    anom.loc[anom["source"] == "ERA5", "z_era5"] = np.nan
    station = anom["source"].isin(["GHCN", "ISD"]) & (anom["flag"] != "binh_thuong")
    anom["xac_nhan"] = None
    anom.loc[station, "xac_nhan"] = classify_cross_source(anom.loc[station, "z"], anom.loc[station, "z_era5"])
    print("  Chi doi chieu ERA5:\n  " + anom.loc[station, "xac_nhan"].value_counts().to_string().replace("\n", "\n  "))
    # Them doi chung thu 2: tram lan can (GHCN/ISD khac tram vat ly, trong ban kinh NEIGHBOR_RADIUS_KM)
    loc_tbl = build_location_table()
    st_ids = anom.loc[anom["source"].isin(["GHCN", "ISD"]), "location_id"].unique()
    pairs = neighbor_pairs(loc_tbl[loc_tbl["location_id"].isin(st_ids)])
    z_all = anom.loc[anom["source"].isin(["GHCN", "ISD"]), ["location_id", "date", "var", "z"]].dropna()
    z_all = z_all.groupby(["location_id", "date", "var"], as_index=False)["z"].mean()
    sup = neighbor_support(anom.loc[station], z_all, pairs)
    anom["n_lan_can"] = 0
    anom["ty_le_lan_can_dong_y"] = np.nan
    anom.loc[station, ["n_lan_can", "ty_le_lan_can_dong_y"]] = sup[["n_lan_can", "ty_le_lan_can_dong_y"]]
    anom["xac_nhan_tong_hop"] = None
    anom.loc[station, "xac_nhan_tong_hop"] = classify_combined(
        anom.loc[station, "z"], anom.loc[station, "z_era5"], anom.loc[station, "n_lan_can"],
        anom.loc[station, "ty_le_lan_can_dong_y"])
    print(f"  {len(pairs)} cap tram lan can (<= {NEIGHBOR_RADIUS_KM} km, bo cung tram vat ly < {SAME_SITE_KM} km)")
    print("  ERA5 + tram lan can:\n  " + anom.loc[station, "xac_nhan_tong_hop"].value_counts().to_string().replace("\n", "\n  "))
    anom.to_parquet(os.path.join(OUT, "anomaly_daily.parquet"), index=False)

    print("== 4/6: Dot nong (>= 3 ngay lien tiep > bach phan vi 90) ==")
    t = anom[anom["var"] == "temp_mean"].rename(columns={"value": "temp_mean"})
    events = heatwave_events(t)
    events.to_parquet(os.path.join(OUT, "heatwave_events.parquet"), index=False)
    print(f"  {len(events):,} dot nong | {events['location_id'].nunique()} vi tri")

    print("== 5/6: SPI-1 / SPI-3 (tram GHCN, nen 1991-2020) ==")
    g = daily.filter((F.col("source") == "GHCN")).groupBy("location_id", "year", "month").agg(
        F.sum("precip_sum").alias("precip"), F.count("precip_sum").alias("n_days")).toPandas()
    g["days_in_month"] = pd.to_datetime(dict(year=g.year, month=g.month, day=1)).dt.days_in_month
    g.loc[g["n_days"] < 0.9 * g["days_in_month"], "precip"] = np.nan  # tháng thiếu > 10% ngày -> bỏ
    g = g.sort_values(["location_id", "year", "month"])
    rows = []
    for loc_id, s in g.groupby("location_id"):
        idx = pd.PeriodIndex(pd.to_datetime(dict(year=s.year, month=s.month, day=1)), freq="M")
        s = s.set_index(idx)[["precip"]].reindex(pd.period_range(idx.min(), idx.max(), freq="M"))
        s["p3"] = s["precip"].rolling(3, min_periods=3).sum()
        s["spi1"], s["spi3"] = np.nan, np.nan
        for m in range(1, 13):
            sel = s.index.month == m
            base = s.index.year.to_series(index=s.index).between(*BASELINES["GHCN"]) & sel
            s.loc[sel, "spi1"] = spi_from_totals(s.loc[sel, "precip"], s.loc[base, "precip"]).values
            s.loc[sel, "spi3"] = spi_from_totals(s.loc[sel, "p3"], s.loc[base, "p3"]).values
        s["location_id"] = loc_id
        s["period"] = s.index.astype(str)
        rows.append(s.reset_index(drop=True))
    spi = pd.concat(rows, ignore_index=True)
    spi = spi[spi["spi1"].notna() | spi["spi3"].notna()]
    spi.to_parquet(os.path.join(OUT, "spi_monthly.parquet"), index=False)
    print(f"  {spi['location_id'].nunique()} tram co SPI | {len(spi):,} thang")

    print("== 6/6: Mua cuc doan ETCCDI (p95/p99 ngay uot, Rx1day, R95p) ==")
    dp = daily.select("location_id", "source", "date", "precip_sum").filter(F.col("precip_sum").isNotNull()).toPandas()
    pct = wet_day_percentiles(dp)
    ext = dp.merge(pct, on=["location_id", "source"], how="inner")
    # Hạng của ngày trong toàn bộ chuỗi của trạm (1 = ngày mưa lớn nhất từng ghi nhận ở nguồn đó)
    ext["rank_in_record"] = ext.groupby(["location_id", "source"])["precip_sum"].rank(ascending=False, method="min").astype(int)
    ext["flag"] = precip_extreme_flag(ext["precip_sum"], ext["p95"], ext["p99"])
    ext["ratio_p99"] = ext["precip_sum"] / ext["p99"]
    precip_ext = ext[ext["flag"] != "binh_thuong"].reset_index(drop=True)
    precip_ext.to_parquet(os.path.join(OUT, "precip_extremes_daily.parquet"), index=False)
    indices = precip_annual_indices(dp, pct)
    indices.to_parquet(os.path.join(OUT, "precip_indices_annual.parquet"), index=False)
    print(f"  {len(pct)} vi tri-nguon co nguong | mua lon: {(precip_ext.flag == 'mua_lon').sum():,} ngay "
          f"| mua cuc doan: {(precip_ext.flag == 'mua_cuc_doan').sum():,} ngay | {len(indices):,} nam-vi-tri co chi so")

    print("\n== Kiem chung voi su kien that ==")
    summary = validate_events(anom, events, spi, build_location_table(), precip_ext)
    summary["tong_quan"] = {
        "ngay_vi_tri_nguon": int(daily.count()),
        "gia_tri_co_nen": int(len(anom)),
        "bat_thuong": int((anom.flag == "bat_thuong").sum()),
        "cuc_doan": int((anom.flag == "cuc_doan").sum()),
        "xac_nhan_cheo": anom.loc[station, "xac_nhan"].value_counts().to_dict(),
        "xac_nhan_tong_hop": anom.loc[station, "xac_nhan_tong_hop"].value_counts().to_dict(),
        "dot_nong": int(len(events)),
        "ngay_mua_cuc_doan_vuot_p99": int((precip_ext.flag == "mua_cuc_doan").sum()),
    }
    with open(os.path.join(OUT, "anomaly_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(json.dumps({k: v for k, v in summary.items() if k != "tong_quan"}, ensure_ascii=False, indent=2, default=str))
    spark.stop()


if __name__ == "__main__":
    main()
