# -*- coding: utf-8 -*-
"""Sơ đồ luồng code thật của project IT5427 Nhóm 16 (tích hợp dữ liệu khí tượng đa nguồn Đông Nam Á).
Nguồn: thứ tự lệnh thật trong README.md muc 'Chay toan bo' + khao sat cay thu muc that ngay 15/11/2026."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lib import Page, write, PAL, FS

OUT = pathlib.Path(__file__).resolve().parent.parent

FLOWX, FLOWW = 24, 230
CARDX, CARDW = 270, 533


def cards2(p, x, y, w, items, size=15):
    """Nhu cards() trong lib.py nhung tra ve y cuoi cung (de xep hang chinh xac, khong doan)."""
    cpl = max(20, int((w - 24) / (size * FS * 0.52)))
    for title, body, role in items:
        lines = sum(max(1, -(-len(l) // cpl)) for l in body.split('\n'))
        bh = 16 + int(lines * size * FS * 1.38)
        p.bar(x, y, w, 34, title, size + 1, PAL[role][3])
        p.box(x, y + 34, w, bh, body, role, size, False, 'rect', 'left')
        y += 34 + bh + 12
    return y


def arrow_down(p, x, y1, y2):
    p.line(x, y1, x, y2, color='#4B5563')
    p.add('', 'endArrow=block;endFill=1;html=1;strokeColor=#4B5563;strokeWidth=2;', x - 1, y2 - 1, 2, 2)


def write_multi(pages, path):
    parts = []
    for pg in pages:
        pg.finish()
        parts.append(f'<diagram name="{pg.name}" id="d_{pg.name}">{pg.xml()}</diagram>')
    open(path, 'w', encoding='utf-8').write('<mxfile host="app.diagrams.net">' + ''.join(parts) + '</mxfile>')


def row(p, y, label, role, cardlist, lsize=18):
    """Ve 1 hang: khoi luong chinh ben trai (cao bang dung chieu cao cards ben phai) + cards; tra ve y ke tiep."""
    y_end = cards2(p, CARDX, y, CARDW, cardlist, size=15)
    h = y_end - 16 - y  # bo khoang cach duoi cung cua card cuoi
    p.box(FLOWX, y, FLOWW, h, label, role, lsize, True)
    y2 = y_end + 34
    arrow_down(p, FLOWX + FLOWW // 2, y + h, y2)
    return y2


def a00():
    """Trang 1: tong quan 7 tang, moi tang 1 dong ngan + ngon ngu/nen tang, khong chi tiet file."""
    p = Page('1-tong-quan', 'Tổng quan luồng code — Nhóm 16, IT5427')
    p.a4(landscape=False)
    p.text(24, 58, p.W - 48, 24, 'Tích hợp dữ liệu khí tượng đa nguồn Đông Nam Á · 7 tầng xử lý theo đúng thứ tự chạy thật trong README.md', 13, '#555555', 'left')

    stages = [
        ('A. Thu thập dữ liệu thô', 'scripts/ — Python 3 + Bash (CDS API, retry)', 'blue'),
        ('B. Chuẩn hoá & kiểm tra chất lượng (QC)', 'ingestion/ — Python + Pandas', 'yellow'),
        ('C. Lược đồ chung (GAV) & kho Parquet', 'warehouse/ — PySpark 4.2.0 (Java 17)', 'yellow'),
        ('D. Tích hợp: Entity Resolution + Survivorship', 'warehouse/ — Python + Pandas/NumPy', 'yellow'),
        ('E. Phân tích thống kê & mô hình PINN', 'warehouse/ — PySpark+DuckDB · model/ — PyTorch', 'yellow'),
        ('F. Luồng thời gian thực (phát lại lịch sử)', 'Kafka + Spark Structured Streaming, Docker', 'red'),
        ('G. Phục vụ & tài liệu', 'dashboard/ — Streamlit · report/, slides/ — LaTeX', 'purple'),
    ]
    x, w = 24, p.W - 48
    y = 100
    bh = 92
    for i, (title, sub, role) in enumerate(stages):
        p.box(x, y, w, bh, title, role, 21, True, align='left')
        p.text(x + 24, y + 54, w - 48, 30, sub, 15, PAL[role][2], 'left')
        y2 = y + bh + 34
        if i < len(stages) - 1:
            arrow_down(p, x + 70, y + bh, y2)
        y = y2
    p.box(x, y - 20, w, 62, 'Kiểm thử xuyên suốt mọi tầng: tests/ — pytest (13 file)   ·   Chi tiết từng tầng: xem trang 2 và 3', 'orange', 15, False, 'rect', 'left')
    return p


def a01():
    p = Page('2-chi-tiet-A-D', 'Chi tiết mã nguồn (1/2): Thu thập → Tích hợp — Nhóm 16, IT5427')
    p.a4(landscape=False)
    p.text(24, 58, p.W - 48, 28, 'Tầng A–D · mỗi khối ghi tên file script thật + ngôn ngữ/nền tảng · tiếp theo ở trang 3', 13, '#555555', 'left')

    y = 96

    y = row(p, y, 'A. Thu thập\ndữ liệu thô', 'blue', [
        ('scripts/ — Python 3 + Bash', 'batch_download_week2.py (GHCN/ISD: mẫu + toàn lịch sử)\n'
         'download_full_points.py (ISD 10 năm, NASA/Open-Meteo 5 năm)\n'
         'download_era5_cds.py, download_era5_full.py (CDS API)\n'
         'era5_autoresume.sh (Bash, tự chạy lại khi đứt mạng)\n'
         'resource_guard.py (chặn chạy khi RAM/đĩa sắp cạn)', 'blue'),
    ])

    y = row(p, y, 'B. Chuẩn hoá\n& kiểm tra\nchất lượng', 'yellow', [
        ('ingestion/ — Python + Pandas', 'parsers.py: parse_ghcn, parse_isd, parse_nasa_power,\nparse_openmeteo\n'
         'veracity.py: detect_outliers_iqr/zscore (QC tầng 5)\n'
         'warehouse/interpolation.py: ERA5 → Bilinear vào trạm', 'yellow'),
    ])

    y = row(p, y, 'C. Lược đồ\nchung & kho\nParquet', 'yellow', [
        ('warehouse/ — Python + PySpark 4.2.0 (Java 17)', 'location.py → output/location.parquet (119 vị trí)\n'
         'build_warehouse.py (GAV) → weatherobs.parquet\n'
         '8.955.313 dòng, 109 partition year/source', 'yellow'),
    ])

    y = row(p, y, 'D. Tích hợp:\nEntity\nResolution +\nSurvivorship', 'yellow', [
        ('warehouse/ — Python + Pandas/NumPy', 'entity_resolution.py, er_precision_recall.py\n(Haversine, 22/26 trạm)\n'
         'survivorship.py, survivorship_resolve.py,\nsurvivorship_conflict_by_source.py\n'
         '→ weatherobs_fused.parquet (856.452 dòng)', 'yellow'),
    ])

    p.box(24, y - 10, p.W - 48, 34, 'Tiếp theo ở trang 3: Phân tích & mô hình PINN → Streaming → Phục vụ & tài liệu', 'orange', 13, False, 'rect', 'left')
    return p


def a02():
    p = Page('3-chi-tiet-E-G', 'Chi tiết mã nguồn (2/2): Phân tích → Phục vụ — Nhóm 16, IT5427')
    p.a4(landscape=False)
    p.text(24, 58, p.W - 48, 28, 'Tầng E–G · tiếp theo trang 2 (A–D) · mỗi khối ghi tên file script thật + ngôn ngữ/nền tảng', 13, '#555555', 'left')

    y = 96

    y = row(p, y, 'E. Phân tích\n& mô hình\nPINN', 'yellow', [
        ('warehouse/ — PySpark + DuckDB + Python', 'anomaly_detection.py (z-score, SPI, mưa cực đoan)\n'
         'climate_trends.py (Mann-Kendall+Sen) · sensor_drift.py\n'
         'eda_pca.py · spark_analytics.py, query_optimization.py\n'
         'scale_benchmark.py, skew_repartition_analysis.py', 'yellow'),
        ('model/ — Python + PyTorch', 'pinn_wind_field_v2.py (PINN trường gió)\n'
         'pinn_rh_from_dewpoint.py, navier_stokes_autograd_check.py', 'purple'),
    ])

    y = row(p, y, 'F. Luồng\nthời gian\nthực (phát lại\nlịch sử)', 'red', [
        ('ingestion/+warehouse/ — Kafka + Spark Streaming', 'kafka_producer.py (replay → topic weatherobs.<nguồn>)\n'
         'spark_streaming_consumer.py, spark_streaming_anomaly.py\n'
         '179/179 cảnh báo khớp đúng kết quả batch', 'red'),
        ('Docker — docker-compose.kafka.yml, .spark.yml', '1 broker Kafka (KRaft) + 1 master/2 worker Spark', 'orange'),
    ])

    y = row(p, y, 'G. Phục vụ\n& tài liệu', 'purple', [
        ('dashboard/app.py — Python + Streamlit', '10 panel, đọc trực tiếp Parquet, cache ~0,6s/lượt', 'purple'),
        ('report/, slides/ — LaTeX (XeLaTeX/LuaLaTeX)', 'final-report.tex (66 trang)\n'
         'final-defense.tex (53 trang, Beamer)\n'
         'plot_*.py (matplotlib) sinh hình cho báo cáo', 'purple'),
    ])

    p.box(24, y - 10, p.W - 48, 58, 'Kiểm thử xuyên suốt mọi tầng: tests/ — pytest (13 file: parsers, veracity,\n'
          'entity_resolution, survivorship, sensor_drift, anomaly, climate_trends, model_pinn, spark_jobs...)',
          'orange', 13, False, 'rect', 'left')

    return p


if __name__ == '__main__':
    out = OUT / 'kien-truc-ma-nguon.drawio'
    write_multi([a00(), a01(), a02()], str(out))
    print('wrote', out)
