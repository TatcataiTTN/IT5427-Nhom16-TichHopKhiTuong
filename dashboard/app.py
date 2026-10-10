"""
Dashboard proof-of-concept — đọc TRỰC TIẾP warehouse Parquet thật (không mock),
đúng tiêu chí docs/03-ke-hoach-160-tasks.md Tuần 2 TV4 #1 + #5:
"App Streamlit chạy local, kết nối lấy được dữ liệu mẫu" + "hiển thị dữ liệu thật".

Chạy: streamlit run dashboard/app.py
(cần chạy warehouse/build_warehouse.py trước để sinh warehouse/output/weatherobs.parquet)
"""
import os

import pandas as pd
import streamlit as st

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

st.subheader("3. Bản đồ phân bố trạm (cần ghép toạ độ — xem Việc còn lại)")
st.info(
    "Bản đồ heatmap ERA5 + toạ độ trạm (docs/03 Tuần 2, TV4 #3) **chưa làm** — cần bảng "
    "`Location(location_id, lat, lon, ...)` join vào warehouse này trước. Toạ độ trạm đã có sẵn "
    "trong `reference/*.csv`, phần còn thiếu là bước join + phần ERA5 grid vào Mediated Schema "
    "(hiện ERA5 mới dừng ở subset NetCDF riêng, chưa hợp nhất vào warehouse điểm)."
)
