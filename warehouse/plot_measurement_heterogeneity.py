"""
Bang "do do khong dong nhat" (measurement heterogeneity) giua 4 nguon diem — phan con lai cua phan
hoi giang vien ben canh missing/outlier (xem plot_data_quality.py). Doc truc tiep tu
ingestion/parsers.py (PHYSICAL_RANGES, TEMP_DEF_*, cac phep quy doi don vi/dinh nghia THAT trong
parse_ghcn/parse_isd/parse_nasa_power/parse_openmeteo) — khong bia.

Chay: python3 warehouse/plot_measurement_heterogeneity.py
"""
import os
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT_PNG = os.path.join(os.path.dirname(__file__), "..", "report", "figures", "measurement_heterogeneity.png")

BLUE, ORANGE, MAGENTA, YELLOW = "#2a78d6", "#eb6834", "#e87ba4", "#c98500"

# (nguon, van de do khong dong nhat, xu ly bat buoc, mau)
ROWS = [
    ("GHCN", "Định dạng LONG: 1 dòng/1 biến/1 ngày (TMAX, TMIN, TAVG, PRCP là các dòng riêng)",
     "PIVOT bắt buộc thành 1 dòng/ngày trước khi dùng được", BLUE),
    ("GHCN", "DATA_VALUE ở đơn vị phần mười: nhiệt độ 1/10°C, mưa 1/10mm",
     "Chia 10 để ra đơn vị chuẩn", BLUE),
    ("GHCN", "\"Nhiệt độ ngày\" = TAVG (TB giờ quan trắc) hoặc (TMAX+TMIN)/2 khi thiếu TAVG — "
     "2 định nghĩa khác nhau trộn trong cùng 1 cột", "Gắn nhãn temp_def phân biệt TAVG / TMAX_TMIN_MID, "
     "không trộn vào 1 chuỗi xu hướng", BLUE),
    ("GHCN", "DATE là ngày quan trắc theo GIỜ ĐỊA PHƯƠNG, không phải UTC",
     "Gán 00:00 UTC theo quy ước — lệch múi giờ thật so với nguồn giờ UTC khác", BLUE),
    ("NOAA ISD", "Trường NÉN nhiều giá trị con trong 1 cột, dạng chuỗi \"a,b,c,...\" "
     "(TMP, DEW, SLP, MA1, WND)", "Phải TÁCH từng sub-field theo đúng vị trí + mã QC riêng", ORANGE),
    ("NOAA ISD", "Đơn vị gốc dạng phần mười cho nhiệt độ/điểm sương/áp suất/tốc độ gió",
     "Chia 10 theo từng trường (scale riêng mỗi field)", ORANGE),
    ("NOAA ISD", "Không có sẵn cột độ ẩm tương đối (RH%)",
     "Tự tính từ nhiệt độ + điểm sương bằng công thức Clausius-Clapeyron (suy luận vật lý, "
     "không phải nội suy)", ORANGE),
    ("NOAA ISD", "1 quan trắc có thể gửi TRÙNG lặp qua 2 loại bản tin (METAR FM-15 và SYNOP FM-12) "
     "cùng trạm, cùng thời điểm", "Khử trùng: ưu tiên FM-15, rồi FM-12, rồi loại khác", ORANGE),
    ("NOAA ISD", "Có cả áp suất mực biển (SLP) và áp suất bề mặt trạm (MA1) — dễ nhầm lẫn với "
     "altimeter/QNH trong cùng trường MA1", "Chỉ lấy đúng áp suất bề mặt thật từ MA1; KHÔNG dùng "
     "altimeter thay SLP (lệch theo độ cao trạm: −0,4 đến +1,5 hPa)", ORANGE),
    ("NASA POWER", "Áp suất PS ở đơn vị kPa (các nguồn khác dùng hPa)",
     "Nhân 10 để ra hPa", MAGENTA),
    ("NASA POWER", "Bức xạ mặt trời ở đơn vị MJ/m²/ngày (các nguồn khác dùng W/m²)",
     "Đổi đơn vị: × 10⁶ / 86400", MAGENTA),
    ("NASA POWER", "Gió: file cũ chỉ có WS2M (đo ở độ cao 2m), file mới có WS10M (10m) — không cùng "
     "độ cao đo với các nguồn khác", "Ưu tiên WS10M; thiếu thì quy đổi WS2M→10m bằng hồ sơ gió "
     "logarit + gắn cờ WIND_2M_TO_10M", MAGENTA),
    ("NASA POWER", "Giá trị thiếu dùng sentinel số −999.0 (không phải NULL/NaN chuẩn)",
     "Đọc fill_value thật từ header JSON rồi thay bằng NaN (không hard-code −999)", MAGENTA),
    ("NASA POWER", "\"Nhiệt độ ngày\" là trung bình ngày của sản phẩm vệ tinh/mô hình (khác bản chất "
     "với giá trị tức thời đo tại trạm)", "Gắn nhãn temp_def = DAILY_MEAN, tách biệt khỏi INST/TAVG", MAGENTA),
    ("Open-Meteo", "Đơn vị tốc độ gió trả về THAY ĐỔI theo thiết lập API gọi (km/h mặc định, hoặc "
     "m/s, mph, knot)", "Đọc field hourly_units để biết đúng đơn vị trước khi quy đổi — không được "
     "giả định cố định 1 đơn vị", YELLOW),
]
COL_LABELS = ["Nguồn", "Đặc trưng gây không đồng nhất", "Yêu cầu xử lý bắt buộc"]
COL_W = [0.115, 0.455, 0.43]
WRAP_CHARS = [13, 62, 58]
FONT = 8.7
LINE_H = 1.0
ROW_PAD = 0.62
HEADER_H = 1.25
NAVY = "#003C71"


def wrap_cell(text, width):
    lines = []
    for para in text.split("\n"):
        lines.extend(textwrap.wrap(para, width=width) or [""])
    return lines


def main():
    rows_wrapped = []
    for src, issue, fix, color in ROWS:
        cells = [wrap_cell(t, w) for t, w in zip([src, issue, fix], WRAP_CHARS)]
        n_lines = max(len(c) for c in cells)
        rows_wrapped.append((cells, n_lines, color))

    row_heights = [n * LINE_H + ROW_PAD for _, n, _ in rows_wrapped]
    total_h = HEADER_H + sum(row_heights)
    fig, ax = plt.subplots(figsize=(13.5, total_h * 0.40), dpi=200)
    ax.axis("off")

    xs = [0.0]
    for w in COL_W:
        xs.append(xs[-1] + w)

    ax.add_patch(plt.Rectangle((0, total_h - HEADER_H), 1.0, HEADER_H, facecolor=NAVY, edgecolor="none"))
    for i, lab in enumerate(COL_LABELS):
        ax.text(xs[i] + 0.008, total_h - HEADER_H / 2, lab, va="center", ha="left",
                fontsize=10.5, fontweight="bold", color="white")

    y_cursor = total_h - HEADER_H
    last_src = None
    for r_idx, ((cells, n_lines, color), rh) in enumerate(zip(rows_wrapped, row_heights)):
        y_cursor -= rh
        bg = "#F2F2F2" if r_idx % 2 == 0 else "white"
        ax.add_patch(plt.Rectangle((0, y_cursor), 1.0, rh, facecolor=bg, edgecolor="#D8D8D8", linewidth=0.6))
        ax.add_patch(plt.Rectangle((0, y_cursor), 0.010, rh, facecolor=color, edgecolor="none"))
        y_mid = y_cursor + rh / 2
        for i, lines in enumerate(cells):
            if i == 0:
                if ROWS[r_idx][0] == last_src:
                    continue  # chi in ten nguon o dong dau tien cua nhom, tranh lap lai roi mat
            block = "\n".join(lines)
            ax.text(xs[i] + 0.012, y_mid, block, va="center", ha="left",
                    fontsize=FONT, color="#1A1A1A", linespacing=1.3,
                    fontweight=("bold" if i == 0 else "normal"))
        last_src = ROWS[r_idx][0]

    ax.add_patch(plt.Rectangle((0, 0), 1.0, total_h, facecolor="none", edgecolor="#B0B0B0", linewidth=0.9))
    for x in xs[1:-1]:
        ax.plot([x, x], [0, total_h], color="#D8D8D8", linewidth=0.6)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, total_h)
    ax.set_title("Đo lường không đồng nhất giữa 4 nguồn điểm: đặc trưng và yêu cầu xử lý bắt buộc\n"
                "(đọc trực tiếp từ ingestion/parsers.py — không khái quát hoá)",
                fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
    fig.savefig(OUT_PNG, bbox_inches="tight", facecolor="white")
    print(f"Wrote {OUT_PNG}")


if __name__ == "__main__":
    main()
