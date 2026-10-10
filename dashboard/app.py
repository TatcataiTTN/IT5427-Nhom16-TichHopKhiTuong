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

WAREHOUSE = os.path.join(os.path.dirname(__file__), "..", "warehouse", "output", "weatherobs.parquet")

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
