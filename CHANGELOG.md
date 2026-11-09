# CHANGELOG

(docs/03 Tuần 3 TV2 #7 "Thiết lập data lineage/versioning cơ bản cho warehouse") — sinh từ lịch sử
commit thật (`git log`), không viết tay tách rời khỏi lịch sử thật.

## [Tuần 3-4] 2026-11-09

### Added
- `warehouse/entity_resolution.py` — Entity Resolution GHCN↔ISD bằng khoảng cách Haversine, giải
  quyết gap đã biết (2 hệ mã trạm độc lập). Kết quả: 22/26 cặp khớp trong ngưỡng 5km.
- `warehouse/validate_interpolation.py` — Cross-validation ERA5 Bilinear vs trạm thật (RMSE
  temp_c=1,02°C, precip_mm=10,98mm), breakdown theo tercile độ cao.
- `ingestion/veracity.py` — Outlier detection Z-score + IQR. Phát hiện hiệu ứng masking của
  Z-score với outlier cực đoan.
- `model/pinn_wind_field_v2.py` — PINN v2 trường gió thật (continuity Navier-Stokes), quét λ,
  so sánh trung thực PINN vs baseline hồi quy thuần.
- `warehouse/data_quality_report.py` → `docs/13-data-quality-report.md` — báo cáo chất lượng
  dữ liệu tự động (missing/outlier/độ phủ theo nguồn).
- `docs/ingestion.md`, `docs/warehouse.md`, `docs/model.md`, `data_dictionary.md`,
  `requirements.txt` — tài liệu kỹ thuật đầy đủ cho từng mảng.

## [Tuần 2] 2026-10-20

### Fixed
- Tag Docker `bitnami/spark:3.5`/`bitnami/kafka:3.7` bị Bitnami rút khỏi Docker Hub → đổi sang
  `bitnamilegacy`.
- Producer Kafka xuất `NaN` thay vì `null` trong JSON (không hợp chuẩn) → sửa.

### Added
- Spark cluster 3 node + Kafka broker chạy thật, verify qua `spark-submit` + `kafka-console-consumer`.
- `slides/progress-report.tex` — slide báo cáo tiến độ 21 trang.

## [Tuần 2] 2026-10-11

### Added
- `warehouse/location.py` — dimension Location, 119 vị trí, referential integrity 100%.
- `warehouse/interpolation.py` — nội suy Bilinear ERA5 vào 113 trạm.
- `warehouse/spark_analytics.py` — ma trận tương quan, data skew, benchmark partition (phát hiện
  partition chậm hơn ở quy mô hiện tại — ghi nhận trung thực).
- 3 script PINN thật: `model/train_demo.py`, `model/pinn_rh_from_dewpoint.py`,
  `model/navier_stokes_autograd_check.py`.
- `docker-compose.spark.yml`, `docker-compose.kafka.yml`, `ingestion/kafka_producer.py`.

## [Tuần 2] 2026-10-10

### Added
- `ingestion/parsers.py` — Mediated Schema `WeatherObs`, PIVOT (GHCN) + PARSE (ISD).
- `warehouse/survivorship.py` — Record Linkage/conflict resolution theo ưu tiên nguồn.
- `warehouse/build_warehouse.py` — ETL end-to-end qua Spark, 1.076.473 bản ghi.
- `dashboard/app.py` — Streamlit dashboard proof-of-concept.
- Rà soát trạng thái thật 80 tác vụ Tuần 1-2 theo đúng tiêu chí Kiểm thử gốc.

## [Tuần 1-2] 2026-09-29 – 2026-10-10

### Added
- Khởi tạo repo, đề xuất đề tài, kế hoạch 160 tác vụ, báo cáo đề xuất (`report/main.tex`), slide
  đề cương (`slides/main.tex`).
- Kiểm tra thực tế toàn bộ nguồn dữ liệu (9/9), phát hiện ARCO-ERA5/Planetary Computer miễn phí,
  sửa lỗi ERA5-AWS Requester-Pays, OpenAQ API v1/v2 khai tử.
- Danh sách trạm quan trắc thật GHCN+ISD cho 9 nước Đông Nam Á (119 vị trí).

### Fixed
- Lỗi mã quốc gia trong ISD (`VM`/`VN` cho Việt Nam, `BX` không phải `BS` cho Brunei).
- Open-Meteo tải nhầm `surface_pressure` thay vì `pressure_msl` theo đúng mapping GAV.

---
*Dữ liệu nguồn: `git log --reverse`. Mỗi mục gắn với 1 hoặc nhiều commit thật, xem chi tiết bằng
`git log --oneline`.*
