# Kết quả kỹ thuật Tuần 3-4 — tiếp nối docs/10, dữ liệu thật

Chạy thật ngày 09/11/2026, tiếp nối trực tiếp `docs/10-ket-qua-ky-thuat-tuan-2.md`. Không ước
lượng — mọi số liệu lấy từ chạy lại các script liệt kê bên dưới.

## 1. Entity Resolution GHCN ↔ ISD — gap Tuần 2 đã giải quyết

`warehouse/entity_resolution.py` — Haversine nearest-neighbor, ngưỡng 5km:

| Chỉ số | Giá trị thật |
|---|---|
| Trạm GHCN | 87 |
| Trạm ISD | 26 |
| Cặp khớp được | **22/26 (84,6%)** |
| Khoảng cách trung bình | 0,53 km |
| Khoảng cách min/max | 0,000 km / 2,757 km |

Nhiều cặp khớp tại khoảng cách **0,000km** — cùng tọa độ WMO gốc, xác nhận đây đúng là 1 trạm vật
lý được 2 cơ quan gán 2 mã khác nhau, không phải trùng hợp ngẫu nhiên.

## 2. Cross-validation nội suy không gian (TV2 #3-4)

`warehouse/validate_interpolation.py` — so ERA5-Bilinear-nội-suy-vào-tọa-độ-trạm với giá trị trạm
thật, cùng ngày. Chạy lại 09/11/2026 trên warehouse đầy đủ (ERA5 2020–2024): 108.542 cặp nhiệt độ,
61 trạm (bản trước trên ERA5 3 ngày: 104 cặp, 35 trạm — RMSE nhiệt độ 1,02°C, mưa 10,98mm):

| Biến | Số cặp | RMSE | MAE |
|---|---|---|---|
| `temp_c` | 108.542 | 1,14°C | 0,85°C |
| `wind_speed_ms` | 47.139 | 1,02 m/s | 0,75 m/s |
| `precip_mm` | 30.567 | 19,83mm | 7,75mm |

Theo tercile độ cao: RMSE nhiệt độ 0,99 / 0,94 / **1,42**°C (thấp → cao) — nhóm trạm cao nhất sai số
lớn nhất, đúng kỳ vọng vật lý (lưới ERA5 0,25° không bắt được hiệu ứng địa hình chi tiết).

## 3. Veracity — phát hiện outlier (TV1 #2)

`ingestion/veracity.py` — tiêm 5 outlier cực đoan vào dữ liệu N(25, 2):

| Phương pháp | Phát hiện |
|---|---|
| Z-score (threshold=3) | **1/5 (20%)** — bị "masking effect" |
| IQR (k=1.5) | **5/5 (100%)** |

Phát hiện thống kê thật: outlier càng cực đoan càng tự làm std phình to, che giấu chính nó trong
phép đo Z-score. Đã chọn IQR làm chỉ số chính trong `warehouse/data_quality_report.py`.

## 4. PINN v2 — trường gió thật + so sánh baseline (TV3 #1-4)

`model/pinn_wind_field_v2.py` — 113 trạm ERA5 thật (gió trung bình 15–17/6/2021; script lọc đúng cửa sổ này nên tái lập được trên warehouse đầy đủ 5 năm), chia 91 train / 22 test, quét λ:

| λ | Test RMSE | Test MAE |
|---|---|---|
| 0,0 (baseline) | **1,0447** | 0,7429 |
| 0,01 | 1,0889 | 0,7648 |
| 0,1 | 1,0826 | 0,7661 |
| 1,0 | 1,1227 | 0,7927 |

**Kết quả trung thực**: baseline hồi quy thuần thắng về RMSE ở quy mô dữ liệu này (1 snapshot
không-thời-gian, 113 điểm) — PINN không vượt trội. Đã verify tái lập được: venv hoàn toàn mới,
cài lại từ `requirements.txt`, chạy lại cho RMSE giống hệt tới 4 chữ số thập phân.

## 5. Spark SQL query optimization (TV2 #1)

`warehouse/query_optimization.py` — EXPLAIN + cache() trên truy vấn tổng hợp nhiệt độ theo
(location, tháng), nguồn GHCN:

| | Baseline (không cache) | Sau tối ưu (cache) |
|---|---|---|
| Thời gian trung bình (3 lần chạy) | 0,371s | 0,118s |
| **Cải thiện** | | **68,1%** (vượt ngưỡng 30% yêu cầu) |

(Chạy lại 09/11/2026 trên warehouse 9.348.470 bản ghi; bản trước trên 1.076.473 bản ghi: 0,990s → 0,523s, 47,1%.)

## 6. Data skew — repartition thử nghiệm (TV2 #6, TV3 #7)

`warehouse/skew_repartition_analysis.py` — thử thêm `month` vào partition key:

| Partition key | Số partition | Partition lớn nhất |
|---|---|---|
| `year/source` (hiện tại) | 109 | 10,62% (2020, ERA5) |
| `year/month/source` (thử nghiệm) | 1.306 | 0,90% |

(Chạy lại 09/11/2026 trên warehouse đầy đủ; bản trước trên 1.076.473 dòng: 88 → 1.043 partition,
33,28% → 3,04%.)

**Trade-off trung thực**: skew giảm 91,5% nhưng số partition tăng 12 lần — làm nặng thêm vấn đề
"small-file" đã ghi nhận ở `docs/10`. Đo lại công bằng trên 9,3 triệu dòng, partition hiện tại vẫn
chậm hơn 1,5–2,4 lần so với không partition (Parquet tự bỏ qua row-group nhờ thống kê min/max).
**Khuyến nghị: giữ nguyên** partition key hiện tại.

## 7. Data Quality Report (TV2 #8)

`warehouse/data_quality_report.py` → `docs/13-data-quality-report.md` — tỷ lệ missing/outlier/độ
phủ thật theo từng nguồn trên 9.348.470 dòng (chạy lại 09/11/2026 trên warehouse đầy đủ). Phát hiện đáng chú ý: GHCN 100% missing ở
`rh_pct`/`wind_speed_ms`/`pressure_msl_hpa` — giới hạn cấu trúc nguồn (GHCN-Daily chỉ báo cáo
TMAX/TMIN/PRCP), không phải lỗi pipeline.

## 8. Dashboard — 3 panel mới (TV4 #2-4)

`dashboard/app.py` — đã verify thật qua Chrome (chụp màn hình, 0 lỗi console):
- **So sánh nguồn**: NASA_POWER vs OPEN_METEO, 6 điểm, 2020–2024 (overlap thật) — RMSE hiển thị
  trực tiếp (ví dụ Hà Nội: RMSE temp_c ≈ 1,78°C).
- **Cảnh báo bất thường**: IQR trên dữ liệu thật, màu theo mức độ (🟢/🟡/🔴 theo % outlier).
- **Output PINN**: bản đồ residual + bảng pred vs obs từng trạm, đọc trực tiếp
  `warehouse/output/pinn_wind_field_output.parquet`.

## 9. Spark Structured Streaming + Kafka — test live thành công (09/11/2026, cập nhật)

Sau khi Docker Desktop lên được (người dùng tự mở lại thủ công), đã test live thành công:
`warehouse/spark_streaming_consumer.py` đọc topic Kafka thật (`weatherobs.ghcn`), tính
`avg_temp_c` theo cửa sổ trượt 1 phút/30 giây cho từng trạm, console hiển thị đúng kết quả qua
nhiều batch liên tiếp.

Trong lúc chạy live lần đầu, phát hiện + sửa 2 bug thật (không phải lỗi logic nghiệp vụ, mà lỗi
môi trường/tương thích phiên bản):
1. **Lỗi mạng khởi tạo SparkContext**: `local[*]` SparkSession thất bại do Spark tự phân giải
   hostname máy ra địa chỉ IP LAN thật (`192.168.1.168`) thay vì `localhost`, khiến driver/executor
   nội bộ không giao tiếp được (`BlockManagerId.executorId()` null). Nhiều khả năng do mạng ảo
   của Docker Desktop (vpnkit/gVisor) vừa khởi động lại làm thay đổi route mạng trên máy host. Sửa
   bằng biến môi trường `SPARK_LOCAL_IP=127.0.0.1` (đã thêm `os.environ.setdefault(...)` ngay
   trong script để tự áp dụng, không bắt buộc người dùng nhớ set tay).
2. **Lỗi tương thích phiên bản connector Kafka**: script ban đầu ghim cứng
   `spark-sql-kafka-0-10_2.13:4.0.0`, nhưng máy thật chạy PySpark 4.2.0 — không tương thích nhị
   phân, lỗi `NoSuchMethodError: SerializedOffset.<init>`. Sửa bằng lấy version tự động từ
   `pyspark.__version__` thay vì ghim cứng.

Có test tự động đi kèm (`tests/test_spark_jobs.py::test_spark_structured_streaming_reads_kafka_and_windows_real_data`,
tự `skip` nếu Kafka broker không chạy).

---
*Tái lập: chạy lại từng script liệt kê ở mỗi mục. Toàn bộ có unit test đi kèm trong `tests/`
(38 test nhanh pass, không tính 5 test "slow" cần huấn luyện/Spark thật).*
