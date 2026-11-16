# Tài liệu kỹ thuật — Ingestion (TV1)

(docs/03 Tuần 3 TV1 #10 "Cập nhật tài liệu kỹ thuật Ingestion")

## 1. Các script chính

| Script | Việc làm |
|---|---|
| `scripts/batch_download_week2.py` | Tải batch thật GHCN/ISD/NASA POWER/Open-Meteo/ERA5 cho 9 nước ĐNA |
| `ingestion/parsers.py` | PIVOT (GHCN long→wide), PARSE (ISD packed fields) → Mediated Schema `WeatherObs` |
| `ingestion/veracity.py` | Phát hiện outlier (Z-score + IQR) |
| `ingestion/kafka_producer.py` | Replay dữ liệu lịch sử từ warehouse Parquet vào Kafka topic |

## 2. Chạy pipeline từ đầu

```bash
# 1. Tải dữ liệu thô (ghi vào data_samples/batch_week2/, không commit lên git)
python3 scripts/batch_download_week2.py sea-priority

# 2. Build warehouse (gọi parsers.py cho từng nguồn + Spark ghi Parquet)
export JAVA_HOME=$(brew --prefix openjdk@17)/libexec/openjdk.jdk/Contents/Home
python3 warehouse/build_warehouse.py

# 3. (Tuỳ chọn) Replay qua Kafka — cần docker compose -f docker-compose.kafka.yml up -d trước
python3 ingestion/kafka_producer.py --limit 100 --speed 0
```

Kết quả mong đợi: `warehouse/output/weatherobs.parquet` chứa 1.076.473 bản ghi (số liệu lần
chạy 10/10/2026 — có thể khác nếu chạy lại do GHCN near-real-time cập nhật liên tục).

## 3. Veracity — phát hiện outlier

`ingestion/veracity.py` cung cấp `detect_outliers(df, column)` dùng cả Z-score (threshold=3) và
IQR (k=1.5). **Phát hiện quan trọng khi test**: Z-score bị "masking effect" — outlier càng cực
đoan càng tự làm std phình to, che giấu chính nó (ví dụ: tiêm [80, -60, 95, -999, 70] vào dữ liệu
~N(25,2), Z-score chỉ bắt được 1/5, IQR bắt đủ 5/5). **Khuyến nghị: dùng IQR làm chỉ số chính**,
Z-score chỉ tham khảo bổ sung. Outlier chỉ được gắn cờ (`{col}_outlier_iqr`), không tự động xoá —
một phần "outlier" thống kê là hiện tượng thời tiết cực đoan có thật (bão, nắng nóng kỷ lục).

## 4. Chính sách xử lý missing-value theo từng loại biến

| Biến | Chiến lược | Lý do |
|---|---|---|
| `temp_c`, `rh_pct`, `pressure_*_hpa` | Không nội suy thời gian — giữ `NaN`, để Survivorship tự chọn nguồn khác có giá trị | Đây là biến liên tục biến đổi chậm, nhưng mỗi nguồn có tần suất khác nhau (GHCN=ngày, ISD=giờ) — nội suy ngang nguồn dễ tạo artefact. Survivorship (ưu tiên ISD/GHCN > ERA5 > Open-Meteo > POWER) đã đóng vai trò "fill" hợp lý hơn nội suy mù |
| `precip_mm` | `NaN` nghĩa là "không có dữ liệu", **không** suy ra = 0 | GHCN/ISD: thiếu bản ghi mưa không có nghĩa là không mưa — nhầm lẫn này là lỗi phổ biến khi xử lý dữ liệu mưa trạm |
| `soil_temp_c`, `soil_moist_m3m3` | Giữ `NaN` toàn bộ (không có nguồn nào trong 5 nguồn hiện tại cung cấp đủ tin cậy) | Đã ghi nhận ở `docs/06` — cột tồn tại trong Mediated Schema cho tương lai (ERA5-Land), chưa có dữ liệu thật |

Không dùng linear/spline interpolation theo thời gian cho bất kỳ biến nào ở mức ingestion — quyết
định có chủ đích để tránh tạo dữ liệu giả trước khi qua Survivorship (nội suy "ảo giác chính xác"
là 1 rủi ro đã ghi nhận ở `docs/11`).

## 5. Đối chiếu chéo Open-Meteo vs ERA5/NOAA (độ tin cậy nguồn)

Open-Meteo Historical thực chất là lớp bao đóng gói lại ERA5 (đã xác nhận ở `docs/12`), nên về mặt
lý thuyết 2 nguồn phải gần như trùng khớp hoàn toàn trong vùng ERA5 có dữ liệu (chỉ chênh do khác
phương pháp hiệu chỉnh/nội suy nội bộ của Open-Meteo). Do phạm vi ERA5 hiện tại trong warehouse chỉ
có 3 ngày (15–17/6/2021) trong khi Open-Meteo có cả năm 2024, 2 nguồn không có đủ overlap thời gian
để tính RMSE/MAE có ý nghĩa thống kê ở bản build hiện tại — việc này phụ thuộc quyết định tải ERA5
full 5 năm (xem `docs/09` mục 2). Khi overlap đủ, dùng lại `warehouse/validate_interpolation.py`
(đổi `source.isin(["GHCN","ISD"])` thành `source == "OPEN_METEO"`) để tính.

## 6. Giấy phép dữ liệu (License)

| Nguồn | Giấy phép | Ràng buộc |
|---|---|---|
| NOAA GHCN-Daily, ISD | Public Domain (US Government work) | Không hạn chế |
| NASA POWER | Public Domain | Không hạn chế |
| ERA5 (ARCO, Copernicus) | Copernicus License (CC BY 4.0-like) | Phải ghi rõ nguồn khi công bố |
| Open-Meteo | CC BY 4.0 (dữ liệu), AGPLv3 (code) | Phải ghi nguồn |
| CHIRPS | Public Domain (tác giả đã từ bỏ bản quyền) | Không hạn chế |
| Natural Earth (boundaries) | Public Domain | Không hạn chế |

Không có nguồn nào trong 5 nguồn lõi vi phạm điều khoản sử dụng học thuật/phi thương mại.
