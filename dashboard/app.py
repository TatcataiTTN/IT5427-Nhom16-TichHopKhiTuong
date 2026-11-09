"""
Dashboard proof-of-concept — đọc TRỰC TIẾP warehouse Parquet thật (không mock),
đúng tiêu chí docs/03-ke-hoach-160-tasks.md Tuần 2 TV4 #1 + #5:
"App Streamlit chạy local, kết nối lấy được dữ liệu mẫu" + "hiển thị dữ liệu thật".

Chạy: streamlit run dashboard/app.py
(cần chạy warehouse/build_warehouse.py trước để sinh warehouse/output/weatherobs.parquet)
"""
import os
import sys

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
    return df


df = load_warehouse()

if df is None:
    st.error(
        "Chưa tìm thấy warehouse. Chạy trước:\n\n"
        "`JAVA_HOME=$(brew --prefix openjdk@17)/libexec/openjdk.jdk/Contents/Home "
        "python3 warehouse/build_warehouse.py`"
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
agg = df.groupby("source").agg(
    so_ban_ghi=("location_id", "count"),
    so_tram=("location_id", "nunique"),
    temp_tb=("temp_c", "mean"),
).round(2)
st.dataframe(agg, use_container_width=True)

st.divider()

st.subheader("3. Bản đồ phân bố trạm + giá trị theo biến/thời điểm")


@st.cache_data
def load_location():
    return build_location_table()


loc = load_location()
map_variable = st.selectbox(
    "Biến hiển thị trên bản đồ", ["temp_c", "rh_pct", "precip_mm", "wind_speed_ms"], key="map_var",
)
available_dates = sorted(df["timestamp_utc"].dt.date.unique())
# Mac dinh chon ngay co du lieu day du (GHCN gan-thoi-gian-thuc thuong tre vai thang voi TMAX/TMIN,
# chi co PRCP truoc) -- uu tien 2024-06-15 (co du 5 nguon that) neu co, khong thi lay giua danh sach.
import datetime as _dt
_default_date = _dt.date(2024, 6, 15)
default_date = _default_date if _default_date in available_dates else available_dates[len(available_dates) // 2]
map_date = st.select_slider("Chọn ngày (time slider)", options=available_dates, value=default_date)

day_df = df[df["timestamp_utc"].dt.date == map_date]
day_agg = day_df.groupby("location_id")[map_variable].mean().reset_index()
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
    st.dataframe(map_df.sort_values(map_variable, ascending=False).head(10), use_container_width=True)

st.divider()

st.subheader("4. So sánh giá trị khí tượng giữa các nguồn (cùng điểm, cùng thời gian)")
st.caption(
    "NASA POWER và Open-Meteo cùng phủ 6 điểm đại diện, cả năm 2024 — đủ overlap thật để so sánh "
    "trực tiếp (ERA5 hiện chỉ có 3 ngày 2021, GHCN/ISD khác điểm nên không đưa vào panel này)."
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
            use_container_width=True,
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
        use_container_width=True,
    )
else:
    st.info("Chưa có output PINN — chạy `python3 model/pinn_wind_field_v2.py` trước.")
