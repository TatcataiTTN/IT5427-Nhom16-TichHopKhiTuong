# Tích hợp và xử lý dữ liệu khí tượng đa nguồn phục vụ phát hiện dị thường khí hậu khu vực Đông Nam Á

**Học phần:** IT5427 Tích hợp và xử lý dữ liệu lớn, Đại học Bách khoa Hà Nội · **Giảng viên:** TS. Vũ Tuyết Trinh
**Nhóm 16** · **Trạng thái:** hoàn thành, bản nộp cuối kỳ (11/2026)

## Bản cuối

| Sản phẩm | Tệp | Ghi chú |
|---|---|---|
| Báo cáo | [`report/final-report.pdf`](report/final-report.pdf) (57 trang), nguồn `report/final-report.tex` | XeLaTeX; hình trong `report/figures/` |
| Slide bảo vệ | [`slides/final-defense.pdf`](slides/final-defense.pdf) (66 trang: bài chính 1–34, phụ lục 35–66), nguồn `slides/final-defense.tex` | XeLaTeX, theme `beamerthemeHUST.sty` |
| Mã nguồn | `ingestion/`, `warehouse/`, `model/`, `dashboard/`, `viz/` | 122 test trong `tests/` |

## Thành viên nhóm

| Thành viên | MSSV | Phụ trách |
|---|---|---|
| Ngô Văn Quang | 20251243M | Thu thập, làm sạch, kiểm soát chất lượng dữ liệu đa nguồn |
| Nguyễn Cao Lương | 20251244M | Lược đồ trung gian (GAV), Entity Resolution, Survivorship |
| Trương Tuấn Nghĩa | 20251196M | Spark batch/streaming, phát hiện dị thường, PINN, dashboard |

## Kết quả chính

- **Kho dữ liệu:** 8.955.313 bản ghi từ 5 nguồn (ERA5, NOAA ISD, GHCN-Daily, NASA POWER, Open-Meteo), 119 vị trí,
  9 nước ASEAN, lưu Parquet theo `year/source`. ERA5 tải đủ 540/540 tệp (9 biến, 2020–2024, theo giờ).
- **Tích hợp:** lược đồ chung `WeatherObs` theo GAV; Entity Resolution ghép 22/26 trạm ISD với GHCN (precision,
  recall 100% trên nhãn số WMO); Survivorship sinh 856.452 dòng hợp nhất theo thứ tự ưu tiên nguồn. Thêm mô hình
  Fellegi–Sunter, luật phủ quyết và liên kết trạm với lưới ERA5 thay vì gộp.
- **Phát hiện dị thường (cửa sổ 2020–2024):** 22.446 giá trị gắn cờ theo z-score trên khí hậu nền; 93,3% ca tại
  trạm được ERA5 hoặc trạm lân cận xác nhận. Bắt đúng nắng nóng 4–5/2024 và bão Yagi 9/2024. Đợt nóng ETCCDI, SPI,
  mưa cực đoan, xu hướng dài hạn (25/27 trạm ấm lên, trung vị +0,21 °C/thập kỷ), trôi cảm biến.
- **Streaming:** Kafka + Spark Structured Streaming phát lại đợt nóng 2024, 179/179 cảnh báo khớp kết quả batch.
- **Tối ưu Spark:** `cache()` giảm 69,4% thời gian truy vấn đại diện (ngưỡng đặt ra 30%).
- **PINN:** phủ 2/12 trường (độ ẩm từ điểm sương, trường gió 2D có ràng buộc liên tục); điền được gió tại điểm thiếu
  số liệu (RMSE 1,0577 so với hồi quy thuần 1,0473) và đánh dấu 4/113 vị trí gió lệch trường vật lý.
- **Dashboard:** Streamlit 10 panel đọc trực tiếp kho Parquet.

## Cấu trúc repo

```
ingestion/    parsers.py (5 nguồn -> WeatherObs, PIVOT/PARSE, chuẩn hoá đơn vị, QC 4 tầng), veracity.py,
              kafka_producer.py (phát lại dữ liệu lịch sử vào Kafka)
warehouse/    location.py, build_warehouse.py, entity_resolution.py, er_fellegi_sunter.py, station_grid_link.py,
              survivorship*.py, interpolation.py, anomaly_detection.py, climate_trends.py, sensor_drift.py,
              spark_streaming_anomaly.py, query_optimization.py, skew_repartition_analysis.py, eda_pca.py,
              data_quality_report.py, plot_*.py (sinh hình cho báo cáo)
model/        pinn_rh_from_dewpoint.py, pinn_wind_field_v2.py, navier_stokes_autograd_check.py, train_demo.py
dashboard/    app.py (Streamlit)
viz/          bản đồ gió/mưa và bề mặt phần dư PINN dạng HTML
scripts/      tải dữ liệu (download_era5_full.py, download_era5_cds.py, download_full_points.py,
              batch_download_week2.py, check_data_sources.py), check_spark_env.py,
              mo_demo_bao_ve.sh và demo/ (6 kịch bản demo)
reference/    danh sách trạm GHCN/ISD Đông Nam Á dùng trực tiếp trong code
data_samples/ mẫu dữ liệu và toạ độ điểm NASA POWER/Open-Meteo mà pipeline đọc
tests/        122 test (pytest), gồm test Spark và Kafka
report/       final-report.tex/.pdf, figures/
slides/       final-defense.tex/.pdf, beamerthemeHUST.sty, images/, Makefile, make_notes.py
archived/     tài liệu trong quá trình làm (xem cuối trang)
```

## Chạy lại

Yêu cầu: Python 3.12 (đã kiểm chứng với Anaconda), **Java 17 hoặc 21** (PySpark 4.2 không chạy với Java 11),
Docker cho Kafka/cụm Spark. Cài thư viện: `pip install -r requirements.txt`.

```bash
export JAVA_HOME=$(brew --prefix openjdk@17)/libexec/openjdk.jdk/Contents/Home   # macOS; Ubuntu: /usr/lib/jvm/java-17-openjdk-amd64

# Dữ liệu: tải bộ đã build sẵn (~435 MB) hoặc tải lại từ nguồn gốc
gh release download data-v2.0-full && tar -xzf warehouse-full.tar.gz && tar -xzf raw-points.tar.gz
# python3 scripts/batch_download_week2.py full && python3 scripts/batch_download_week2.py sea-priority
# python3 scripts/download_full_points.py && python3 scripts/download_era5_full.py   # ERA5 khoảng 22 GB

python3 warehouse/location.py && python3 warehouse/build_warehouse.py   # kho Parquet 8.955.313 bản ghi
python3 warehouse/entity_resolution.py && python3 warehouse/er_fellegi_sunter.py && python3 warehouse/station_grid_link.py
python3 warehouse/anomaly_detection.py && python3 warehouse/climate_trends.py && python3 warehouse/sensor_drift.py
python3 warehouse/query_optimization.py && python3 model/pinn_wind_field_v2.py
python3 -m pytest tests/ -q                                              # 122 test
streamlit run dashboard/app.py                                           # http://localhost:8501

# Streaming (cần Docker)
docker compose -f docker-compose.kafka.yml up -d
python3 ingestion/kafka_producer.py --source GHCN --start 2024-04-01 --end 2024-05-15 --limit 0 --topic weatherobs.ghcn.replay
python3 warehouse/spark_streaming_anomaly.py --topic weatherobs.ghcn.replay --duration 60
```

Mở toàn bộ môi trường demo (slide, báo cáo, mã nguồn, dashboard, 6 kịch bản demo) bằng một lệnh:
`bash scripts/mo_demo_bao_ve.sh`. Các kịch bản lẻ nằm trong `scripts/demo/` và tự chọn JDK 17.

Dựng lại tài liệu: `cd report && xelatex final-report.tex` (2 lần); `cd slides && make` (bản trình chiếu) hoặc
`make notes` (bản có lời nói, đọc kịch bản từ `archived/slides/kich-ban-bao-ve.md`).

## Nguồn dữ liệu

| Nguồn | Loại | Phạm vi dùng | Truy cập |
|---|---|---|---|
| ERA5 (ECMWF/Copernicus) | Lưới tái phân tích 0,25° | 2020–2024, theo giờ, 9 biến | ARCO-ERA5 (Google Cloud) và CDS API |
| NOAA ISD | Trạm, theo giờ | 2015–2024 | NOAA, không cần khoá |
| GHCN-Daily | Trạm, theo ngày | 1943–2026 (nền khí hậu 1991–2020) | AWS S3 `noaa-ghcn-pds`, không cần khoá |
| NASA POWER | Điểm, theo ngày | 2020–2024 | REST API công khai |
| Open-Meteo Historical | Điểm, theo giờ | 2020–2024 | REST API công khai |

Khoá CDS (nếu dùng kênh CDS) đọc từ `~/.cdsapirc` trên máy, không lưu trong repo.

## Thư mục `archived/`

Tài liệu tạo ra trong quá trình làm, giữ lại để tra cứu, không phải sản phẩm nộp:
`archived/docs/` (đề xuất, kế hoạch 160 tác vụ, ghi chú phân tích, báo cáo kỹ thuật từng tuần, kịch bản demo),
`archived/slides/` (kịch bản thuyết trình, hỏi đáp, bản slide có lời nói, slide đề xuất và báo cáo tiến độ),
`archived/report/` (báo cáo đề xuất), `archived/scripts/` (script phụ trợ khi tải ERA5),
`archived/CHANGELOG.md`, `archived/data_dictionary.md`.
