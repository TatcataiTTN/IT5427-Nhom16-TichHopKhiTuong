"""
Ve bang tong hop: cac loai di thuong khi hau da trien khai thuc te trong warehouse/anomaly_detection.py,
warehouse/climate_trends.py, warehouse/sensor_drift.py — moi loai di kem bien dau vao, tieu chuan/nguong
dung de phat hien, va nguon du lieu cung cap. Khong bia so lieu — doc truc tiep tu hang so trong code
(BASELINES, Z_ANOMALY/Z_EXTREME, HEATWAVE_MIN_DAYS, WET_DAY_MM, DRIFT_PER_YEAR, STEP, MIN_YEARS, ALPHA).

Do chieu cao hang tinh dong theo so dong chu sau khi wrap (tranh chong chu), chay:
  python3 warehouse/plot_anomaly_standards.py
"""
import os
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT_PNG = os.path.join(os.path.dirname(__file__), "..", "report", "figures", "anomaly_types_standards.png")

NAVY, GREEN, RED, ORANGE, GRAY, BLUE = "#003C71", "#1E783C", "#AA1E1E", "#C85A14", "#5A5A5A", "#1E6E8C"

# (nhóm, loại dị thường, biến đầu vào, tiêu chuẩn / ngưỡng, nguồn dữ liệu, màu)
ROWS = [
    ("Nhiệt độ", "Bất thường / cực đoan nhiệt độ", "temp_mean (TB ngày)",
     "z = (x − μ) / σ, nền trượt ±15 ngày; |z| ≥ 2 bất thường, |z| ≥ 3 cực đoan",
     "GHCN, ISD, ERA5, Open-Meteo, NASA POWER", RED),
    ("Nhiệt độ", "Đợt nóng (Heatwave)", "temp_mean liên tiếp nhiều ngày",
     "ETCCDI TG90p: từ 3 ngày liên tiếp có temp_mean > bách phân vị 90 của nền",
     "5 nguồn trên (qua lớp z-score)", RED),
    ("Áp suất", "Bất thường áp suất mặt biển (bão, áp thấp)", "pmsl_min (thấp nhất trong ngày)",
     "Cùng công thức z-score như nhiệt độ (nền trượt ±15 ngày)",
     "GHCN, ISD, ERA5, Open-Meteo, NASA POWER", NAVY),
    ("Mưa", "Mưa lớn / mưa cực đoan (từng ngày)", "precip_sum, chỉ tính ngày ướt (≥ 1mm)",
     "ETCCDI: vượt bách phân vị 95 = mưa lớn, vượt 99 = cực đoan (ngưỡng riêng từng trạm/nguồn)",
     "GHCN, ISD, ERA5, Open-Meteo, NASA POWER", BLUE),
    ("Mưa", "Chỉ số mưa cực đoan theo năm", "PRCPTOT, Rx1day, R95p, R99p, R95pTOT%",
     "Chỉ số ETCCDI chuẩn, chỉ tính năm có ≥ 90% số ngày có dữ liệu mưa",
     "Theo từng cặp trạm − nguồn", BLUE),
    ("Mưa", "Hạn hán (SPI-1 / SPI-3)", "Tổng lượng mưa tháng và 3-tháng",
     "SPI (McKee và cs. 1993): khớp phân phối Gamma trên nền khí hậu chuẩn WMO 1991-2020",
     "GHCN (cần chuỗi mưa tháng đủ dài)", BLUE),
    ("Xu hướng", "Xu hướng khí hậu dài hạn", "Nhiệt TB năm, PRCPTOT năm, Rx1day năm",
     "Kiểm định Mann-Kendall (p < 0,05) + độ dốc Sen (đơn vị/thập kỷ); cần ≥ 30 năm dữ liệu",
     "GHCN", GREEN),
    ("Veracity", "Trôi cảm biến (sensor drift)", "Bias tháng = giá trị trạm − ERA5 nội suy cùng vị trí",
     "Mann-Kendall + Sen (trôi dần theo thời gian) hoặc Pettitt 1979 (nhảy bậc đột ngột); "
     "chỉ gắn cờ khi vừa có ý nghĩa thống kê (p<0,05) VỪA đủ lớn vật lý "
     "(≥ 0,3°C/năm hoặc bước ≥ 0,5°C cho nhiệt; ≥ 0,5 hPa/năm hoặc bước ≥ 1,0 hPa cho áp suất)",
     "GHCN / ISD, đối chiếu với ERA5", ORANGE),
    ("Xác nhận chéo", "Phân loại độ tin cậy của dị thường tại trạm", "z tại trạm so với z ERA5 cùng vị trí/ngày, "
     "và tỷ lệ trạm lân cận (bán kính ≤ 200km, loại trạm trùng vị trí < 5km) đồng thuận",
     "4 nhãn: xác_nhận_khí_hậu / nghi_lỗi_dữ_liệu / dị_thường_cục_bộ / không_đối_chứng",
     "GHCN, ISD đối chiếu ERA5 + trạm lân cận", GRAY),
]

COL_LABELS = ["Nhóm", "Loại dị thường", "Biến đầu vào", "Tiêu chuẩn / ngưỡng phát hiện", "Nguồn dữ liệu"]
COL_W = [0.085, 0.175, 0.205, 0.335, 0.20]
WRAP_CHARS = [9, 18, 21, 35, 21]  # tuned cho fig_w=6.1in (khung chu bao cao), kiem bang render that
FONT = 8.6
LINE_H = 1.0      # 1 don vi truc y / dong chu
ROW_PAD = 0.65    # le tren+duoi cho moi hang (don vi truc y)
HEADER_H = 1.3


def wrap_cell(text, width):
    lines = []
    for para in text.split("\n"):
        lines.extend(textwrap.wrap(para, width=width) or [""])
    return lines


def main():
    rows_wrapped = []
    for grp, name, var, std, src, color in ROWS:
        cells = [wrap_cell(t, w) for t, w in zip([grp, name, var, std, src], WRAP_CHARS)]
        n_lines = max(len(c) for c in cells)
        rows_wrapped.append((cells, n_lines, color))

    row_heights = [n * LINE_H + ROW_PAD for _, n, _ in rows_wrapped]
    total_h = HEADER_H + sum(row_heights)

    fig_w = 6.1
    fig_h = total_h * 0.40
    print(f"DEBUG total_h={total_h:.2f} fig_h={fig_h:.2f}")
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=300)
    ax.axis("off")

    xs = [0.0]
    for w in COL_W:
        xs.append(xs[-1] + w)

    # Header
    ax.add_patch(plt.Rectangle((0, total_h - HEADER_H), 1.0, HEADER_H, facecolor=NAVY, edgecolor="none"))
    for i, lab in enumerate(COL_LABELS):
        ax.text(xs[i] + 0.008, total_h - HEADER_H / 2, lab, va="center", ha="left",
                fontsize=7.8, fontweight="bold", color="white")

    y_cursor = total_h - HEADER_H
    for r_idx, ((cells, n_lines, color), rh) in enumerate(zip(rows_wrapped, row_heights)):
        y_cursor -= rh
        bg = "#F2F2F2" if r_idx % 2 == 0 else "white"
        ax.add_patch(plt.Rectangle((0, y_cursor), 1.0, rh, facecolor=bg, edgecolor="#D8D8D8", linewidth=0.6))
        ax.add_patch(plt.Rectangle((0, y_cursor), 0.010, rh, facecolor=color, edgecolor="none"))
        y_mid = y_cursor + rh / 2
        for i, lines in enumerate(cells):
            block = "\n".join(lines)
            ax.text(xs[i] + 0.012, y_mid, block, va="center", ha="left",
                    fontsize=FONT, color="#1A1A1A", linespacing=1.35,
                    fontweight=("bold" if i == 1 else "normal"))

    ax.add_patch(plt.Rectangle((0, 0), 1.0, total_h, facecolor="none", edgecolor="#B0B0B0", linewidth=0.9))
    for x in xs[1:-1]:
        ax.plot([x, x], [0, total_h], color="#D8D8D8", linewidth=0.6)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, total_h)
    ax.set_title("Các loại dị thường khí hậu đã triển khai: tiêu chuẩn phát hiện\nvà nguồn dữ liệu",
                 fontsize=9.5, fontweight="bold", pad=10)
    fig.tight_layout()
    os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
    fig.savefig(OUT_PNG, bbox_inches="tight", pad_inches=0.04, facecolor="white")
    print(f"Wrote {OUT_PNG}")


if __name__ == "__main__":
    main()
