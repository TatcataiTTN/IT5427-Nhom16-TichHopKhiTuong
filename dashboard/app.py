"""
Dashboard proof-of-concept — đọc TRỰC TIẾP warehouse Parquet thật (không mock),
đúng tiêu chí docs/03-ke-hoach-160-tasks.md Tuần 2 TV4 #1 + #5:
"App Streamlit chạy local, kết nối lấy được dữ liệu mẫu" + "hiển thị dữ liệu thật".

Chạy: streamlit run dashboard/app.py
(cần chạy warehouse/build_warehouse.py trước để sinh warehouse/output/weatherobs.parquet)
"""
import os
import sys

import numpy as np
import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from warehouse.location import build_location_table
from ingestion.veracity import detect_outliers_iqr

WAREHOUSE = os.path.join(os.path.dirname(__file__), "..", "warehouse", "output", "weatherobs.parquet")
PINN_OUTPUT = os.path.join(os.path.dirname(__file__), "..", "warehouse", "output", "pinn_wind_field_output.parquet")

st.set_page_config(page_title="Nhóm 16 — Dashboard Khí tượng ĐNA", layout="wide")
st.title("Dashboard Khí tượng Đông Nam Á — Nhóm 16, IT5427")
st.caption("Đọc trực tiếp warehouse Parquet thật (Mediated Schema WeatherObs), không phải dữ liệu mẫu/mock.")


@st.cache_data
def load_warehouse():
    import pyarrow.parquet as pq
    if not os.path.exists(WAREHOUSE):
        return None
    df = pd.read_parquet(WAREHOUSE)
    df["location_id"] = df["location_id"].astype("category")  # loc theo tram nhanh hon tren ~10 trieu dong
    return df


@st.cache_data
def daily_means(_df):
    """Trung binh theo (vi tri, ngay) — tinh 1 lan, dung cho ban do + time slider (khong quet lai ca warehouse moi lan keo)."""
    cols = ["temp_c", "rh_pct", "precip_mm", "wind_speed_ms"]
    d = _df[["location_id", "timestamp_utc"] + cols].copy()
    d["date"] = d["timestamp_utc"].dt.date
    return d.groupby(["location_id", "date"], observed=True)[cols].mean().reset_index()


@st.cache_data
def source_summary(_df):
    return _df.groupby("source").agg(
        so_ban_ghi=("location_id", "count"),
        so_tram=("location_id", "nunique"),
        temp_tb=("temp_c", "mean"),
    ).round(2)


df = load_warehouse()

if df is None:
    st.error(
        "Chưa tìm thấy warehouse. Chạy trước:\n\n"
        "`python3 warehouse/build_warehouse.py` (JAVA_HOME trỏ tới JDK 17/21, xem README)"
    )
    st.stop()

st.success(f"Đã nạp {len(df):,} bản ghi thật từ warehouse, {df['location_id'].nunique()} trạm/điểm, "
           f"{df['source'].nunique()} nguồn ({', '.join(sorted(df['source'].unique()))}).")

col1, col2, col3 = st.columns(3)
col1.metric("Tổng bản ghi", f"{len(df):,}")
col2.metric("Số trạm/điểm", df["location_id"].nunique())
col3.metric("Khoảng thời gian", f"{df['timestamp_utc'].min().date()} → {df['timestamp_utc'].max().date()}")

st.divider()

st.subheader("1. Chọn trạm/điểm để xem chuỗi thời gian")
station = st.selectbox("Trạm/điểm", sorted(df["location_id"].unique()))
station_df = df[df["location_id"] == station].sort_values("timestamp_utc")
if station_df["source"].nunique() > 1:
    # 1 vi tri co the co nhieu nguon (vd tram ISD + ERA5 noi suy) -> cho chon nguon de khong ve chong len nhau
    src = st.selectbox("Nguồn", sorted(station_df["source"].unique()))
    station_df = station_df[station_df["source"] == src]

variable = st.selectbox(
    "Biến khí tượng",
    ["temp_c", "rh_pct", "precip_mm", "wind_speed_ms", "pressure_surface_hpa", "pressure_msl_hpa"],
)
chart_df = station_df[["timestamp_utc", variable]].dropna().set_index("timestamp_utc")
if chart_df.empty:
    st.warning(f"Trạm {station} không có dữ liệu cho biến {variable}.")
else:
    st.line_chart(chart_df)

st.divider()

st.subheader("2. Tổng hợp theo nguồn")
st.dataframe(source_summary(df), width="stretch")

st.divider()

st.subheader("3. Bản đồ phân bố trạm + giá trị theo biến/thời điểm")


@st.cache_data
def load_location():
    return build_location_table()


loc = load_location()
map_variable = st.selectbox(
    "Biến hiển thị trên bản đồ", ["temp_c", "rh_pct", "precip_mm", "wind_speed_ms"], key="map_var",
)
daily = daily_means(df)
available_dates = sorted(daily["date"].unique())
# Mac dinh chon ngay co du lieu day du (GHCN gan-thoi-gian-thuc thuong tre vai thang voi TMAX/TMIN,
# chi co PRCP truoc) -- uu tien 2024-06-15 (co du 5 nguon that) neu co, khong thi lay giua danh sach.
import datetime as _dt
_default_date = _dt.date(2024, 6, 15)
default_date = _default_date if _default_date in available_dates else available_dates[len(available_dates) // 2]
map_date = st.select_slider("Chọn ngày (time slider)", options=available_dates, value=default_date)

day_agg = daily.loc[daily["date"] == map_date, ["location_id", map_variable]].copy()
day_agg["location_id"] = day_agg["location_id"].astype(str)
map_df = day_agg.merge(loc[["location_id", "lat", "lon"]], on="location_id", how="inner").dropna(
    subset=["lat", "lon", map_variable]
)

if map_df.empty:
    st.warning(f"Không có dữ liệu {map_variable} cho ngày {map_date}.")
else:
    st.caption(
        f"{len(map_df)} vị trí có dữ liệu {map_variable} vào {map_date} "
        f"(kéo thanh trượt phía trên để đổi ngày)."
    )
    st.map(map_df.rename(columns={"lat": "latitude", "lon": "longitude"}), size=20000)
    st.dataframe(map_df.sort_values(map_variable, ascending=False).head(10), width="stretch")

st.divider()

st.subheader("4. So sánh giá trị khí tượng giữa các nguồn (cùng điểm, cùng thời gian)")
st.caption(
    "NASA POWER và Open-Meteo cùng phủ 6 điểm đại diện, 2020–2024 — đủ overlap thật để so sánh "
    "trực tiếp (ERA5 nội suy vào vị trí trạm, GHCN/ISD khác điểm nên không đưa vào panel này)."
)
compare_sources = ["NASA_POWER", "OPEN_METEO"]
compare_df = df[df["source"].isin(compare_sources)]
compare_points = sorted(compare_df["location_id"].unique())
if compare_points:
    cmp_point = st.selectbox("Điểm so sánh", compare_points, key="cmp_point")
    cmp_var = st.selectbox("Biến so sánh", ["temp_c", "precip_mm"], key="cmp_var")
    cmp_pivot = (
        compare_df[compare_df["location_id"] == cmp_point]
        .pivot_table(index=compare_df["timestamp_utc"].dt.date, columns="source", values=cmp_var, aggfunc="mean")
    )
    cmp_pivot = cmp_pivot.reindex(columns=[c for c in compare_sources if c in cmp_pivot.columns])
    if cmp_pivot.dropna(how="all").empty:
        st.warning(f"Không có dữ liệu {cmp_var} để so sánh tại {cmp_point}.")
    else:
        st.line_chart(cmp_pivot)
        diff = (cmp_pivot[compare_sources[0]] - cmp_pivot[compare_sources[1]]).dropna()
        if len(diff) > 0:
            rmse = (diff ** 2).mean() ** 0.5
            st.metric(f"RMSE giữa {compare_sources[0]} và {compare_sources[1]} ({cmp_var})", f"{rmse:.3f}")
else:
    st.info("Chưa có dữ liệu NASA_POWER/OPEN_METEO trong warehouse.")

st.divider()

st.subheader("5. Panel cảnh báo bất thường khí tượng (IQR, gắn cờ tự động)")
st.caption(
    "Dùng IQR (bền vững hơn Z-score với outlier cực đoan — xem ingestion/veracity.py) để gắn cờ "
    "giá trị bất thường thật trong warehouse, không phải dữ liệu giả lập."
)
alert_var = st.selectbox("Biến kiểm tra bất thường", ["temp_c", "precip_mm", "wind_speed_ms"], key="alert_var")
alert_source = st.selectbox("Nguồn", sorted(df["source"].unique()), key="alert_source")
alert_df = df[df["source"] == alert_source][["location_id", "timestamp_utc", alert_var]].dropna()
if len(alert_df) >= 4:
    flags = detect_outliers_iqr(alert_df[alert_var])
    alert_df = alert_df.assign(is_outlier=flags)
    n_alerts = int(flags.sum())
    pct = n_alerts / len(alert_df) * 100
    if pct > 10:
        st.error(f"🔴 {n_alerts} bản ghi bất thường ({pct:.1f}%) — tỷ lệ CAO, cần rà soát nguồn")
    elif pct > 2:
        st.warning(f"🟡 {n_alerts} bản ghi bất thường ({pct:.1f}%) — mức trung bình")
    else:
        st.success(f"🟢 {n_alerts} bản ghi bất thường ({pct:.1f}%) — mức thấp, bình thường")
    if n_alerts > 0:
        st.dataframe(
            alert_df[alert_df["is_outlier"]].sort_values(alert_var, ascending=False).head(20),
            width="stretch",
        )
else:
    st.info("Không đủ dữ liệu để kiểm tra bất thường cho lựa chọn này.")

st.divider()

st.subheader("6. Output PINN — trường gió (u,v) dự đoán vs quan trắc thật")
if os.path.exists(PINN_OUTPUT):
    pinn_df = pd.read_parquet(PINN_OUTPUT)
    st.caption(
        f"Từ `model/pinn_wind_field_v2.py` (λ={pinn_df['lambda_used'].iloc[0]}), {len(pinn_df)} trạm, "
        f"residual |pred-obs| trung bình {pinn_df['residual_ms'].mean():.3f} m/s."
    )
    pinn_map = pinn_df.rename(columns={"lat": "latitude", "lon": "longitude"})[
        ["latitude", "longitude", "residual_ms"]
    ]
    st.map(pinn_map, size="residual_ms")
    st.dataframe(
        pinn_df[["location_id", "u_obs_ms", "v_obs_ms", "u_pred_ms", "v_pred_ms", "residual_ms"]]
        .sort_values("residual_ms", ascending=False)
        .head(10),
        width="stretch",
    )
else:
    st.info("Chưa có output PINN — chạy `python3 model/pinn_wind_field_v2.py` trước.")

st.divider()

# ------------------------------------------------------------------------------------------------
# 7. Dị thường khí hậu (warehouse/anomaly_detection.py)
# ------------------------------------------------------------------------------------------------
st.subheader("7. Dị thường khí hậu")
ANOM_DIR = os.path.join(os.path.dirname(WAREHOUSE))


@st.cache_data
def load_anomaly():
    paths = {k: os.path.join(ANOM_DIR, f"{k}.parquet") for k in ("anomaly_daily", "heatwave_events", "spi_monthly")}
    if not all(os.path.exists(p) for p in paths.values()):
        return None
    import json
    out = {k: pd.read_parquet(p) for k, p in paths.items()}
    out["anomaly_daily"]["date"] = pd.to_datetime(out["anomaly_daily"]["date"]).dt.date
    with open(os.path.join(ANOM_DIR, "anomaly_summary.json"), encoding="utf-8") as f:
        out["summary"] = json.load(f)
    # Kết quả bổ sung (có thể chưa chạy): mưa cực đoan, xu hướng, trôi cảm biến, cảnh báo luồng
    for k in ("precip_extremes_daily", "precip_indices_annual", "climate_trends", "annual_series",
              "sensor_drift", "bias_monthly", "stream_alerts"):
        fp = os.path.join(ANOM_DIR, f"{k}.parquet")
        out[k] = pd.read_parquet(fp) if os.path.exists(fp) else None
    return out


anom = load_anomaly()
if anom is None:
    st.info("Chưa có kết quả dị thường. Chạy trước: `python3 warehouse/anomaly_detection.py`")
    st.stop()

summ = anom["summary"]
hot = summ["nang_nong_4_5_2024"]
m1, m2, m3, m4 = st.columns(4)
m1.metric("Ngày nóng bất thường (z ≥ 2), 4–5/2024", f"{hot['ty_le_ngay_z_ge_2']:.1%}",
          f"gấp {hot['ty_le_ngay_z_ge_2'] / hot['ty_le_ngay_z_ge_2_cung_ky_1991_2020']:.0f}× cùng kỳ 1991–2020",
          delta_color="inverse")
m2.metric("Đợt nóng dài nhất 2024", f"{max(int(e['days']) for e in hot['dot_nong_dai_nhat'])} ngày")
m2.caption(f"{hot['so_tram_co_dot_nong']}/{hot['so_tram']} trạm có đợt nóng trong 4–5/2024")
yagi_hpa = summ["bao_yagi_9_2024"]["ap_suat_thap_nhat_hpa"]
m3.metric("Bão Yagi 9/2024 — áp suất ERA5", f"{yagi_hpa} hPa" if yagi_hpa is not None else "Chưa có dữ liệu")
m3.caption(f"z = {summ['bao_yagi_9_2024']['z_thap_nhat']} so với nền 2020–2024 (miền Bắc Việt Nam)"
           if yagi_hpa is not None else "Không có bản ghi áp suất ERA5 khớp phạm vi lọc hiện tại")
cross = summ["tong_quan"]["xac_nhan_cheo"]
m4.metric("Dị thường trạm được ERA5 xác nhận", f"{cross.get('xac_nhan_khi_hau', 0):,}")
m4.caption(f"{cross.get('nghi_loi_du_lieu', 0)} trường hợp nghi lỗi dữ liệu (trạm cực đoan, ERA5 bình thường)")
st.caption("z = (giá trị − trung bình khí hậu nền) / độ lệch chuẩn nền, theo trạm và ngày-trong-năm (cửa sổ ±15 ngày). "
           "Nền GHCN 1991–2020 (chuẩn WMO); ISD 2015–2024, ERA5 2020–2024 là nền ngắn. "
           "|z| ≥ 2 bất thường, ≥ 3 cực đoan.")

st.markdown("**Tỷ lệ ngày nóng bất thường (z ≥ 2) trong tháng 4–5 theo năm — trạm GHCN**")
by_year = pd.Series(hot["ty_le_ngay_z_ge_2_thang_4_5_theo_nam"]).rename("Tỷ lệ ngày z ≥ 2")
by_year.index = by_year.index.astype(str)
st.bar_chart(by_year, color="#e34948", height=220)

VAR_LABEL = {"temp_mean": "Nhiệt độ trung bình ngày", "pmsl_min": "Áp suất mực nước biển thấp nhất ngày"}
a_daily = anom["anomaly_daily"]
c1, c2, c3 = st.columns([2, 1, 3])
a_var = c1.selectbox("Biến", list(VAR_LABEL), format_func=VAR_LABEL.get, key="anom_var")
a_sources = sorted(a_daily.loc[a_daily["var"] == a_var, "source"].unique())
a_src = c2.selectbox("Nguồn", a_sources, index=a_sources.index("GHCN") if "GHCN" in a_sources
                     else a_sources.index("ERA5") if "ERA5" in a_sources else 0, key="anom_src")
sel = a_daily[(a_daily["var"] == a_var) & (a_daily["source"] == a_src) & a_daily["z"].notna()]
a_dates = sorted(sel["date"].unique())
want = _dt.date(2024, 4, 30) if a_var == "temp_mean" else _dt.date(2024, 9, 7)
a_date = c3.select_slider("Ngày", options=a_dates, value=want if want in a_dates else a_dates[-1], key="anom_date")

day = sel[sel["date"] == a_date].merge(loc[["location_id", "lat", "lon", "country"]], on="location_id")


def diverging_rgba(z):
    """Thang phân kỳ xanh (âm) — xám (0) — đỏ (dương), bão hoà ở |z| = 3."""
    neg, mid, pos = np.array([42, 120, 214]), np.array([240, 239, 236]), np.array([227, 73, 72])
    t = np.clip(np.asarray(z, dtype=float) / 3.0, -1, 1)[:, None]
    rgb = np.where(t < 0, mid + (neg - mid) * -t, mid + (pos - mid) * t)
    return [list(map(int, c)) + [220] for c in rgb]


if day.empty:
    st.warning("Không có dữ liệu cho lựa chọn này.")
else:
    day = day.assign(color=diverging_rgba(day["z"]))
    st.map(day.rename(columns={"lat": "latitude", "lon": "longitude"}), color="color", size=40000, zoom=4)
    st.caption(f"{len(day)} vị trí · màu: xanh = thấp hơn bình thường, xám = bình thường, đỏ = cao hơn "
               f"(đậm nhất ở |z| ≥ 3). Bảng dưới liệt kê các vị trí lệch nhiều nhất.")
    show = day.reindex(day["z"].abs().sort_values(ascending=False).index).head(15)
    cols = ["location_id", "country", "value", "clim_mean", "z", "flag", "xac_nhan_tong_hop", "n_lan_can"]
    st.dataframe(show[[c for c in cols if c in show.columns]]
                 .rename(columns={"value": "giá trị", "clim_mean": "trung bình nền",
                                  "xac_nhan_tong_hop": "xác nhận (ERA5 + trạm lân cận)", "n_lan_can": "số trạm lân cận"}).round(2),
                 width="stretch", hide_index=True)

st.markdown("**Đợt nóng** (≥ 3 ngày liên tiếp vượt bách phân vị 90 của nền)")
ev = anom["heatwave_events"].copy()
ev["year"] = pd.to_datetime(ev["start"]).dt.year
e1, e2 = st.columns(2)
ev_src = e1.selectbox("Nguồn", sorted(ev["source"].unique()), index=sorted(ev["source"].unique()).index("GHCN"), key="ev_src")
ev_years = sorted(ev.loc[ev["source"] == ev_src, "year"].unique(), reverse=True)
ev_year = e2.selectbox("Năm", ev_years, index=ev_years.index(2024) if 2024 in ev_years else 0, key="ev_year")
ev_show = ev[(ev["source"] == ev_src) & (ev["year"] == ev_year)].merge(loc[["location_id", "country"]], on="location_id")
st.dataframe(ev_show.sort_values("days", ascending=False)
             [["location_id", "country", "start", "end", "days", "span_days", "max_excess_c"]]
             .rename(columns={"days": "số ngày nóng", "span_days": "độ dài (ngày)", "max_excess_c": "vượt p90 tối đa (°C)"})
             .round(2), width="stretch", hide_index=True)

st.markdown("**Chỉ số hạn/ẩm SPI-3** (trạm GHCN, nền 1991–2020; ≤ −1 hạn, ≤ −2 hạn nặng, ≥ +1 ẩm bất thường)")
spi = anom["spi_monthly"]
spi_loc = st.selectbox("Trạm", sorted(spi["location_id"].unique()), key="spi_loc")
spi_s = spi[(spi["location_id"] == spi_loc) & spi["spi3"].notna()].set_index("period")["spi3"].rename("SPI-3")
spi_s = spi_s.loc["2010":]
# Giữ đủ mọi tháng trên trục (tháng thiếu dữ liệu để trống) — không nén thời gian khi có khoảng trống
if not spi_s.empty:
    spi_s = spi_s.reindex(pd.period_range(spi_s.index.min(), spi_s.index.max(), freq="M").astype(str))
st.bar_chart(spi_s, color="#2a78d6", height=240)
st.caption("Tháng để trống = thiếu dữ liệu mưa (> 10% số ngày không có số liệu).")


pe = anom["precip_extremes_daily"]
if pe is not None:
    st.markdown("**Mưa cực đoan** (ETCCDI: vượt bách phân vị 95 / 99 của các ngày ướt ≥ 1 mm; hạng 1 = ngày mưa lớn nhất từng ghi ở nguồn đó)")
    p1, p2 = st.columns([1, 3])
    pe_day = p1.date_input("Ngày", value=_dt.date(2024, 9, 7), key="pe_day")
    pe_show = pe[pd.to_datetime(pe["date"]).dt.date == pe_day].merge(loc[["location_id", "country"]], on="location_id")
    if pe_show.empty:
        p2.info("Không có trạm nào vượt p95 vào ngày này.")
    else:
        p2.dataframe(pe_show.sort_values("ratio_p99", ascending=False)
                     [["location_id", "country", "source", "precip_sum", "p95", "p99", "ratio_p99", "rank_in_record", "flag"]]
                     .rename(columns={"precip_sum": "mưa (mm)", "ratio_p99": "gấp p99", "rank_in_record": "hạng"}).round(1),
                     width="stretch", hide_index=True)

# ------------------------------------------------------------------------------------------------
# 8. Xu hướng khí hậu dài hạn (warehouse/climate_trends.py)
# ------------------------------------------------------------------------------------------------
trends, series = anom["climate_trends"], anom["annual_series"]
if trends is not None and series is not None:
    st.divider()
    st.subheader("8. Xu hướng khí hậu dài hạn (Mann-Kendall + độ dốc Sen)")
    tt = trends[(trends["var"] == "temp_mean_year") & (trends["period"] == "1975_2024")]
    k1, k2 = st.columns(2)
    k1.metric("Trạm ấm lên có ý nghĩa (p < 0,05), 1975–2024", f"{(tt['trend'] == 'tang').sum()}/{len(tt)}")
    k2.metric("Tốc độ ấm lên trung vị", f"{tt['sen_slope_per_decade'].median():+.2f} °C/thập kỷ")
    tmap = tt.dropna(subset=["lat", "lon"]).assign(color=lambda x: diverging_rgba(x["sen_slope_per_decade"] / 0.4 * 3))
    st.map(tmap.rename(columns={"lat": "latitude", "lon": "longitude"}), color="color", size=40000, zoom=4)
    st.caption("Màu: đỏ = ấm lên (đậm nhất ở ≥ +0,4 °C/thập kỷ), xám = không đổi, xanh = lạnh đi. "
               "Chuỗi GHCN, năm hợp lệ khi ≥ 80% ngày có số liệu, tối thiểu 30 năm.")
    t_loc = st.selectbox("Trạm", tt.sort_values("sen_slope_per_decade", ascending=False)["location_id"].tolist(), key="trend_loc")
    import altair as alt
    s_one = series[series["location_id"] == t_loc].dropna(subset=["temp_mean_year"])[["year", "temp_mean_year"]]
    # Giữ đủ mọi năm trên trục; năm thiếu số liệu để trống (đường đứt), không nối thẳng qua khoảng trống
    s_one = s_one.set_index("year").reindex(range(int(s_one["year"].min()), int(s_one["year"].max()) + 1)) \
        .rename_axis("year").reset_index()
    row = tt[tt["location_id"] == t_loc].iloc[0]
    # Đường xu hướng Sen đi qua trung vị (chuẩn Theil-Sen): y = median(y) + slope·(năm − median(năm))
    sl = row["sen_slope_per_decade"] / 10
    s_one["xu_huong"] = s_one["temp_mean_year"].median() + sl * (s_one["year"] - s_one["year"].median())
    base = alt.Chart(s_one).encode(x=alt.X("year:Q", title=None, axis=alt.Axis(format="d")))
    line = base.mark_line(color="#e34948", strokeWidth=2, point=alt.OverlayMarkDef(size=18, color="#e34948")).encode(
        y=alt.Y("temp_mean_year:Q", title="°C", scale=alt.Scale(zero=False)),
        tooltip=[alt.Tooltip("year:Q", format="d", title="Năm"), alt.Tooltip("temp_mean_year:Q", format=".2f", title="°C")])
    trend_line = base.mark_line(color="#6b6b6b", strokeDash=[5, 4], strokeWidth=1.5).encode(y="xu_huong:Q")
    st.altair_chart((line + trend_line).properties(height=230), use_container_width=True)
    st.caption(f"Nhiệt độ trung bình năm tại {t_loc} (đỏ; năm thiếu số liệu để trống) và đường xu hướng Sen (xám nét đứt): "
               f"{row['sen_slope_per_decade']:+.2f} °C/thập kỷ, p = {row['mk_p']:.3g}.")
    st.dataframe(tt.sort_values("sen_slope_per_decade", ascending=False)
                 [["location_id", "country", "year_from", "year_to", "n_years", "sen_slope_per_decade", "mk_p", "trend"]]
                 .rename(columns={"sen_slope_per_decade": "°C/thập kỷ", "mk_p": "p (Mann-Kendall)"}).round(3),
                 width="stretch", hide_index=True)

# ------------------------------------------------------------------------------------------------
# 9. Trôi cảm biến (warehouse/sensor_drift.py)
# ------------------------------------------------------------------------------------------------
drift, bias = anom["sensor_drift"], anom["bias_monthly"]
if drift is not None and bias is not None:
    st.divider()
    st.subheader("9. Phát hiện trôi cảm biến (chênh lệch trạm − ERA5 theo tháng)")
    st.caption("Biến động khí hậu thật có ở cả trạm và ERA5 nên bị triệt tiêu trong chênh lệch; phần còn lại là "
               "lỗi cảm biến/điểm đo. Trôi dần: Mann-Kendall + độ dốc Sen; nhảy bậc: kiểm định Pettitt.")
    flagged = drift[drift["flag"] != "on_dinh"].sort_values("drift_per_year", key=lambda x: x.abs(), ascending=False)
    st.dataframe(flagged[["location_id", "country", "source", "var", "flag", "drift_per_year", "change_month", "step", "step_pettitt_p"]]
                 .rename(columns={"drift_per_year": "trôi /năm", "change_month": "điểm gãy", "step": "bước nhảy",
                                  "step_pettitt_p": "p (Pettitt)"}).round(3), width="stretch", hide_index=True)
    opts = (flagged["location_id"] + " | " + flagged["source"] + " | " + flagged["var"]).tolist() or \
        (drift["location_id"] + " | " + drift["source"] + " | " + drift["var"]).tolist()[:1]
    pick = st.selectbox("Chuỗi chênh lệch", opts, key="drift_pick")
    d_loc, d_src, d_var = pick.split(" | ")
    b_one = bias[(bias["location_id"] == d_loc) & (bias["source"] == d_src) & (bias["var"] == d_var)].set_index("month")["bias"]
    st.line_chart(b_one.rename(f"Trạm − ERA5 ({d_var})"), color="#2a78d6", height=220)

# ------------------------------------------------------------------------------------------------
# 10. Cảnh báo theo luồng (warehouse/spark_streaming_anomaly.py)
# ------------------------------------------------------------------------------------------------
alerts_s = anom["stream_alerts"]
st.divider()
st.subheader("10. Cảnh báo dị thường theo luồng (Kafka → Spark Structured Streaming)")
if alerts_s is None:
    st.info("Chưa có cảnh báo luồng. Chạy: `python3 ingestion/kafka_producer.py --source GHCN --start 2024-04-01 "
            "--end 2024-05-15 --limit 0 --topic weatherobs.ghcn.replay` rồi `python3 warehouse/spark_streaming_anomaly.py`.")
else:
    a1, a2 = st.columns(2)
    a1.metric("Cảnh báo phát ra", f"{len(alerts_s):,}")
    a2.metric("Số micro-batch có cảnh báo", f"{alerts_s['batch_id'].nunique()}")
    per_day = alerts_s.assign(date=pd.to_datetime(alerts_s["date"])).groupby("date").size().rename("Số cảnh báo")
    st.bar_chart(per_day, color="#e34948", height=200)
    st.dataframe(alerts_s.sort_values(["batch_id", "z"], ascending=[True, False])
                 [["batch_id", "location_id", "date", "temp_c", "clim_mean", "z", "muc"]].round(2),
                 width="stretch", hide_index=True)
