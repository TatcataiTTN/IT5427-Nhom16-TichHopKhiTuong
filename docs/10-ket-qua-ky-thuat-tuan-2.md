# Kết quả kỹ thuật Tuần 2 — nháp nội dung cho báo cáo tiến độ 20/10

Tài liệu này gộp số liệu thật từ pipeline đã chạy (`ingestion/`, `warehouse/`), dùng làm nguồn cho
3 mục "Viết phần ... cho báo cáo tiến độ" (TV1 #10, TV2 #10, TV3 #10 trong `docs/03`). Toàn bộ số
liệu lấy trực tiếp từ lần chạy `warehouse/build_warehouse.py` + `warehouse/spark_analytics.py`
ngày 10/10/2026 — không ước lượng.

---

## 1. Ingestion (phần TV1)

| Nguồn | Số bản ghi thật | Phạm vi |
|---|---|---|
| GHCN-Daily | 655.164 | 41 trạm (10 VN + 31 ĐNA ưu tiên), toàn lịch sử tới 2025 |
| NOAA ISD/Global Hourly | 358.273 | 26 trạm (10 VN + 16 ĐNA ưu tiên), năm 2024 |
| Open-Meteo Historical | 52.704 | 6 điểm đại diện, năm 2024, tần suất giờ |
| ERA5 (ARCO, nội suy Bilinear) | 8.136 | 113 trạm, 3 ngày (15-17/6/2021), 4 biến |
| NASA POWER | 2.196 | 6 điểm đại diện, năm 2024, tần suất ngày |
| **Tổng** | **1.076.473** | |

**Vướng mắc đã gặp và đã xử lý:**
- Phát hiện lỗi tải Open-Meteo sai trường (`surface_pressure` thay vì `pressure_msl` theo đúng mapping GAV) — đã sửa và tải lại.
- Phát hiện khác biệt hệ mã trạm: GHCN và ISD dùng 2 ID namespace khác nhau cho cùng vị trí vật lý (GHCN dùng mã dạng `VMM00048820`, ISD dùng `USAF+WBAN` dạng số) — nghĩa là **chưa thể tự động coi 2 trạm có cùng toạ độ là "cùng 1 thực thể"** nếu chỉ so khớp ID. Đây là bài toán Entity Resolution thật cần xử lý thêm (so khớp theo khoảng cách toạ độ, không phải so khớp ID) — ghi nhận làm việc cần làm ở Tuần 3.
- Dữ liệu ERA5 mới dừng ở subset 3 ngày (không phải 5 năm đầy đủ) — quyết định phạm vi do giới hạn thời gian/băng thông, xem `docs/09-viec-ban-can-tu-lam.md` mục 5.

## 2. Schema & Warehousing (phần TV2)

**Kiến trúc đã triển khai thật:**
- Mediated Schema `WeatherObs` (15 cột) — `ingestion/parsers.py`
- Dimension `Location` (119 vị trí: 113 trạm + 6 điểm) — `warehouse/location.py`, referential integrity đã test: **100% khớp** (0 location_id mồ côi)
- ETL end-to-end qua Spark, partition theo `year/source` — `warehouse/build_warehouse.py`, **88 partition thật**, đếm vào=ra khớp 100% (1.076.473 = 1.076.473)
- Survivorship (ISD/GHCN > ERA5 > Open-Meteo > NASA_POWER) — `warehouse/survivorship.py`, đã test với dữ liệu overlap thật (GHCN vs ERA5, 15-17/6/2021): GHCN thắng đúng ở hầu hết trường hợp, fallback đúng về ERA5 khi GHCN thiếu dữ liệu

**Dung lượng thực tế vs ước lượng ban đầu:**

| | Ước lượng ban đầu (đề cương) | Thực tế đã lưu (10/10/2026) | Giải thích chênh lệch |
|---|---|---|---|
| Tổng dung lượng | ~35 GB (chủ yếu ERA5 full 5 năm) | 29 MB (warehouse Parquet, partition) | Chưa tải ERA5 full 5 năm — mới có subset 3 ngày để chứng minh pipeline. Khi tải đủ 5 năm, dự kiến tiệm cận ước lượng gốc (xem mục 3) |
| GHCN+ISD+POWER+Open-Meteo (phần đã tải đủ) | ~70 MB (ước lượng đề cương) | ~64 MB thô (CSV/JSON gốc), 29MB sau nén Parquet | Khớp hợp lý, Parquet nén tốt hơn CSV/JSON thô |

**Phát hiện benchmark quan trọng (trung thực, không che giấu kết quả không như kỳ vọng):**
Benchmark đọc `year=2024, source=ISD` (358.273 dòng) — **partition KHÔNG nhanh hơn ở quy mô dữ liệu hiện tại**:
- Có partition: 0.381s | Không partition: 0.173s → **partition chậm hơn ~2.2x**
- Dung lượng: có partition 29MB (88 thư mục nhỏ) vs không partition 8.5MB (1 file) — **partition tốn thêm dung lượng ~3.4x**

Nguyên nhân: ở quy mô ~1 triệu dòng, dữ liệu đủ nhỏ để Spark quét toàn bộ cực nhanh; overhead liệt kê 88 thư mục partition + nhiều file nhỏ (small-file problem) vượt quá lợi ích "partition pruning". **Lợi ích partition chỉ rõ rệt khi dữ liệu đủ lớn** (dự kiến sau khi tải ERA5 full 5 năm, ~35GB) — cần benchmark lại ở quy mô đó trước khi kết luận partition key year/source có tối ưu hay không.

## 3. Distributed Computing (phần TV3)

**Môi trường Spark:** PySpark 4.2.0, local mode (`local[*]`, 14 core). Phát hiện & khắc phục: PySpark 4.x yêu cầu Java 17+, máy có Java 11 mặc định gây lỗi `UnsupportedClassVersionError` — đã ghi quy trình khắc phục vào README.

**Ma trận tương quan giữa các biến khí tượng** (tính thật trên 1.076.473 dòng, `warehouse/spark_analytics.py`):

| | temp_c | rh_pct | precip_mm | wind_speed_ms | pressure_msl_hpa |
|---|---|---|---|---|---|
| temp_c | +1.00 | +0.11 | -0.07 | +0.16 | +0.06 |
| rh_pct | +0.11 | +1.00 | -0.16 | +0.57 | +0.43 |
| precip_mm | -0.07 | -0.16 | +1.00 | -0.10 | -0.07 |
| wind_speed_ms | +0.16 | +0.57 | -0.10 | +1.00 | +0.51 |
| pressure_msl_hpa | +0.06 | +0.43 | -0.07 | +0.51 | +1.00 |

Kiểm thử đạt: đường chéo = 1.0, ma trận đối xứng. Tương quan gió-áp suất (+0.51) và gió-độ ẩm (+0.57) hợp lý về mặt khí tượng (gió mạnh thường đi kèm hệ thống áp thấp/mưa).

**Kiểm tra data skew:** 88 partition, partition lớn nhất (`year=2024, source=ISD`) chiếm 33.28% tổng dữ liệu — **dưới ngưỡng 50%, đạt yêu cầu**. Nguyên nhân: ISD năm 2024 có tần suất 30 phút/lần trong khi GHCN là tần suất ngày, trải trên nhiều năm — mất cân bằng tự nhiên theo tần suất nguồn, không phải lỗi thiết kế partition.

**Chưa làm (ghi nhận trung thực):** Docker Compose Spark cluster nhiều node, Kafka Streaming, PINN training loop (Clausius-Clapeyron mới ở dạng công thức trực tiếp, chưa phải physics loss trong vòng lặp huấn luyện) — xem trạng thái đầy đủ tại `docs/03-ke-hoach-160-tasks.md`.

## 4. Rà soát rủi ro — cập nhật sau Tuần 2 (phần TV4)

Bổ sung các rủi ro MỚI phát hiện khi chạy pipeline thật, cộng thêm bảng rủi ro gốc ở `report/main.tex` Chương 7:

| Rủi ro mới | Mức ảnh hưởng | Phương án dự phòng |
|---|---|---|
| Docker Desktop không khởi động được tự động trên máy TV3+TV4, chặn Spark cluster nhiều node + Kafka | Trung bình | Đã viết sẵn + validate cú pháp `docker-compose.spark.yml` và `docker-compose.kafka.yml` — chỉ cần Docker Desktop chạy là triển khai được ngay. Trong lúc chờ, toàn bộ pipeline vẫn chạy tốt ở `local[*]` (đã verify 1.076.473 dòng) |
| GHCN và ISD dùng 2 hệ mã trạm độc lập cho cùng vị trí vật lý — chưa thể so sánh trực tiếp 2 nguồn trạm với nhau qua `location_id` | Trung bình-Cao | Cần thêm bước Entity Resolution dựa trên khoảng cách toạ độ (không phải so khớp ID) ở Tuần 3 — đã ghi nhận rõ trong `docs/11` mục 1 |
| Partition theo `year/source` làm CHẬM truy vấn và TỐN dung lượng hơn ở quy mô dữ liệu hiện tại (~1 triệu dòng) | Thấp (hiện tại), có thể tăng nếu không xử lý trước khi mở rộng ERA5 full 5 năm | Giữ nguyên partition key, benchmark lại khi dữ liệu đạt quy mô ~35GB (ERA5 full) — khả năng cao lợi ích sẽ rõ ràng hơn ở quy mô đó, đúng bản chất kỹ thuật của partition pruning |
| Khối lượng công việc TV3+TV4 (PINN, Spark, Dashboard, Kafka) vẫn là phần nặng nhất còn lại dù đã tự động hoá nhiều | Cao (đã nêu từ đầu `docs/03`) | Đã ưu tiên đúng thứ tự khuyến nghị: Spark batch + Dashboard (lõi bắt buộc) đã xong trước; PINN/Kafka làm sau — khớp đúng chiến lược giảm tải đã thống nhất |

---

*Nguồn số liệu: chạy thật `warehouse/build_warehouse.py` và `warehouse/spark_analytics.py` lúc 10/10/2026. Tái lập bằng cách chạy lại 2 script này (xem README mục 6b).*
