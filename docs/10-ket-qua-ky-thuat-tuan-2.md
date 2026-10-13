# Kết quả kỹ thuật Tuần 2 — nháp nội dung cho báo cáo tiến độ 20/10

Tài liệu này gộp số liệu thật từ pipeline đã chạy (`ingestion/`, `warehouse/`), dùng làm nguồn cho
3 mục "Viết phần ... cho báo cáo tiến độ" (TV1 #10, TV2 #10, TV3 #10 trong `docs/03`). Toàn bộ số
liệu lấy trực tiếp từ lần chạy `warehouse/build_warehouse.py` + `warehouse/spark_analytics.py`
trên **bộ dữ liệu đầy đủ** ngày 13/10/2026 — không ước lượng.

> Lịch sử: bản 10/10/2026 chạy trên bộ mẫu nhỏ (1.076.473 bản ghi, ERA5 3 ngày). Bản này thay thế
> hoàn toàn sau khi tải đủ dữ liệu theo phạm vi đề cương (ERA5 5 năm, ISD 10 năm). Bộ mẫu nhỏ vẫn
> build lại được bằng `python3 warehouse/build_warehouse.py --dataset week2`.

---

## 1. Ingestion (phần TV1)

| Nguồn | Số bản ghi trong warehouse | Phạm vi | Dữ liệu thô |
|---|---|---|---|
| ERA5 (ARCO, nội suy Bilinear vào trạm) | 4.954.824 | 113 trạm × 43.848 giờ (2020–2024), 9 biến | 22 GB (540 file NetCDF, lưới 137×197 ô vùng ĐNA) |
| NOAA ISD/Global Hourly | 3.464.430 | 26 trạm (10 VN + 16 ĐNA ưu tiên), 10 năm 2015–2024 | 1,3 GB CSV (258/260 file) |
| GHCN-Daily | 655.166 | 41 trạm (10 VN + 31 ĐNA ưu tiên), toàn lịch sử 1943–2026 | 63 MB CSV |
| Open-Meteo Historical | 263.088 | 6 điểm đại diện, 5 năm 2020–2024, tần suất giờ | 13 MB JSON |
| NASA POWER | 10.962 | 6 điểm đại diện, 5 năm 2020–2024, tần suất ngày | 1 MB JSON |
| **Tổng** | **9.348.470** | 119 vị trí, 5 nguồn | **~23,4 GB** |

**Kiểm chứng đầy đủ ERA5 (tiêu chí TV1 #1 "không thiếu tháng nào"):** 540/540 file (9 biến × 60
tháng), mỗi biến đủ 43.848/43.848 giờ (kể cả 2 năm nhuận 2020, 2024), 0% NaN. Khoảng giá trị hợp lý
vật lý: nhiệt độ −0,4 → 46°C; áp suất mực nước biển thấp nhất 932 hPa và gió ~40 m/s (tâm bão);
mưa giờ lớn nhất 77 mm.

**Vướng mắc đã gặp và đã xử lý:**
- **Băng thông là nút thắt của ERA5, không phải số luồng.** Mỗi chunk ARCO-ERA5 là 1 giờ *toàn cầu*
  (721×1440), nên để lấy vùng ĐNA vẫn phải tải cả chunk: ~1,8 GB tải về cho mỗi tháng-biến dù chỉ giữ
  ~40 MB → tổng ~1 TB lưu lượng mạng, ~24 giờ ở ~10 MB/s. Tăng từ 32 lên 128 luồng không nhanh hơn.
  Phương án thay thế (CDS cắt bbox phía server, chỉ ~25 GB) cần tài khoản + xếp hàng — nhóm chọn ARCO.
  Script `scripts/download_era5_full.py` tải theo tháng, ghi qua file tạm, chạy lại được sau khi ngắt
  (đã thực tế bị khởi động lại máy 1 lần giữa chừng, chạy lại không mất dữ liệu).
- **Lỗi đơn vị gió Open-Meteo (đã sửa):** API trả `wind_speed_10m` theo **km/h** (`hourly_units`),
  parser cũ ghi thẳng vào cột `wind_speed_ms` → gió Open-Meteo bị **phóng đại 3,6 lần** trong warehouse
  cũ. Parser giờ đọc `hourly_units` và quy đổi, có unit test riêng.
- **Bức xạ ERA5 — chọn đúng đại lượng vật lý:** GAV mapping ban đầu (docs/06) dùng
  `toa_incident_solar_radiation` = bức xạ ở **đỉnh khí quyển**, trong khi NASA POWER
  (`ALLSKY_SFC_SW_DWN`) và Open-Meteo (`shortwave_radiation`) là bức xạ **tại bề mặt**. Đã tải thêm
  `surface_solar_radiation_downwards` và dùng nó cho cột `solar_rad_wm2` (J/m² tích luỹ giờ ÷ 3600 → W/m²).
- **Khoảng trống dữ liệu thật trong nguồn:** ISD trạm Cát Bi (Hải Phòng) không có dữ liệu 2015–2016
  trên NOAA (HTTP 404) — đây là đặc điểm nguồn, không phải lỗi tải.
- Phát hiện lỗi tải Open-Meteo sai trường (`surface_pressure` thay vì `pressure_msl`) — đã sửa từ trước.
- GHCN và ISD dùng 2 ID namespace khác nhau cho cùng vị trí vật lý (`VMM00048820` vs `USAF+WBAN`) —
  **chưa thể coi 2 trạm cùng toạ độ là "cùng 1 thực thể"** nếu chỉ so khớp ID. Bài toán Entity
  Resolution theo khoảng cách toạ độ — việc Tuần 3.

## 2. Schema & Warehousing (phần TV2)

**Kiến trúc đã triển khai thật:**
- Mediated Schema `WeatherObs` (15 cột) — `ingestion/parsers.py`
- Dimension `Location` (119 vị trí: 113 trạm + 6 điểm) — `warehouse/location.py`, referential integrity đã test: **100% khớp**
- Nội suy ERA5 lưới → trạm (`warehouse/interpolation.py::interpolate_era5_month`): vector hoá, nội suy
  cả 113 trạm trong 1 lần gọi/tháng (~2,5 s/tháng), kết quả khớp tuyệt đối với cách nội suy từng trạm cũ
- ETL end-to-end qua Spark, partition theo `year/source` — `warehouse/build_warehouse.py`:
  **109 partition**, đếm vào = ra khớp 100% (9.348.470 = 9.348.470), chạy hết **2 phút 26 giây**, RAM
  đỉnh ~0,5 GB (parse từng nguồn → Parquet tạm → Spark đọc và ghi partition, không dồn ~10 triệu dòng
  qua `createDataFrame` trên driver)
- Survivorship (ISD/GHCN > ERA5 > Open-Meteo > NASA_POWER) — `warehouse/survivorship.py`

**Dung lượng thực tế vs ước lượng ban đầu:**

| | Ước lượng (đề cương) | Thực tế (13/10/2026) | Giải thích |
|---|---|---|---|
| ERA5 | ~34,8 GB (8 biến, 5 năm) | 22 GB (9 biến, 5 năm, NetCDF nén zlib) | Khớp bậc độ lớn; nén zlib giảm ~40% so với float32 thô |
| Các nguồn điểm | < 100 MB | 1,4 GB | ISD mở rộng từ 1 năm lên 10 năm, 26 trạm |
| Warehouse Parquet | — | 303 MB | Warehouse chỉ giữ ERA5 **tại 113 vị trí trạm** (sau nội suy), không giữ cả lưới — lưới đầy đủ nằm ở Raw Zone |

**Benchmark partition (đo lại công bằng trên dữ liệu đầy đủ):** trung vị 5 lần chạy sau 1 lần làm
nóng JVM, so với bản sao không partition ghi từ **chính** warehouse hiện tại:

| Truy vấn | Có partition | Không partition | Kết quả |
|---|---|---|---|
| Đếm ISD năm 2024 | 0,173 s | 0,080 s | partition chậm hơn 2,2× |
| Trung bình nhiệt độ ISD 2024 | 0,222 s | 0,093 s | chậm hơn 2,4× |
| Trung bình theo tháng/trạm ERA5 2024 | 0,299 s | 0,202 s | chậm hơn 1,5× |
| Tổng mưa theo năm/trạm GHCN 1991–2000 | 0,185 s | 0,106 s | chậm hơn 1,7× |

**Kết luận trung thực: ở quy mô 9,3 triệu dòng / 303 MB, partition `year/source` vẫn KHÔNG nhanh
hơn.** Nguyên nhân: bản không partition vẫn được Parquet lọc hiệu quả nhờ **thống kê min/max theo
row-group** (dữ liệu được ghi theo cụm nguồn/năm nên Spark bỏ qua được hầu hết row-group không liên
quan), trong khi 109 thư mục partition phát sinh chi phí liệt kê file. Lợi ích partition pruning chỉ
rõ ở quy mô lớn hơn nhiều hoặc khi lưu trên object storage (S3/GCS) nơi mỗi lần liệt kê/đọc file tốn
độ trễ mạng. *Lưu ý: bản 10/10 có lỗi benchmark — bản sao không partition chỉ được ghi một lần nên về
sau so warehouse mới với bản sao cũ; script đã sửa để ghi lại mỗi lần chạy.*

## 3. Distributed Computing (phần TV3)

**Môi trường Spark:** PySpark 4.2.0. Chạy được cả `local[*]` và **cụm Docker thật** (`apache/spark:4.2.0`,
1 master + 2 worker × 2 core, đã gửi job từ host chạy xong trên cụm). Kafka broker (`apache/kafka:3.7.0`)
chạy thật, producer replay 500/500 message JSON hợp lệ.

**Ma trận tương quan Pearson** (tính thật trên warehouse đầy đủ, **từng cặp biến, chỉ trên dòng có
đủ cả 2 biến** — từ 274.050 đến 8.662.032 dòng tuỳ cặp):

| | temp_c | rh_pct | precip_mm | wind_speed_ms | pressure_msl_hpa |
|---|---|---|---|---|---|
| temp_c | +1.00 | −0.60 | −0.01 | +0.12 | −0.61 |
| rh_pct | −0.60 | +1.00 | +0.10 | −0.30 | +0.04 |
| precip_mm | −0.01 | +0.10 | +1.00 | +0.08 | −0.11 |
| wind_speed_ms | +0.12 | −0.30 | +0.08 | +1.00 | +0.05 |
| pressure_msl_hpa | −0.61 | +0.04 | −0.11 | +0.05 | +1.00 |

Hai tương quan mạnh đều đúng vật lý: **nhiệt độ – độ ẩm tương đối −0,60** (chu kỳ ngày: trời nóng thì
RH giảm vì áp suất hơi bão hoà tăng theo Clausius-Clapeyron) và **nhiệt độ – áp suất −0,61** (mùa
nóng ứng với áp thấp nóng lục địa, mùa lạnh ứng với áp cao lạnh). Mưa tương quan yếu với mọi biến —
khớp nhận định Veracity thấp của mưa đối lưu ở docs/06.

*Đính chính bản 10/10:* ma trận cũ (gió–độ ẩm +0,57, gió–áp suất +0,51) là **tương quan giả** do
script thay NaN bằng 0 trước khi tính — mỗi nguồn thiếu biến khác nhau (ERA5 không có RH, ISD không có
mưa, NASA POWER không có áp suất MSL) nên các cột "cùng bị thiếu" bị coi là cùng bằng 0. Đã sửa sang
tương quan từng cặp (pairwise deletion).

**Kiểm tra data skew:** 109 partition, partition lớn nhất (`year=2020, source=ERA5`) chiếm **10,62%**
tổng dữ liệu — dưới ngưỡng 50%, đạt yêu cầu. ERA5 phân bố đều theo năm (~990 nghìn dòng/năm) nên 5
partition lớn nhất đều là ERA5 với tỷ lệ gần như bằng nhau.

**Dashboard với dữ liệu đầy đủ:** nạp 9,3 triệu bản ghi lần đầu ~3,7 s; đã thêm cache bảng trung bình
theo ngày → đổi ngày/trạm còn ~0,6 s (trước đó ~4 s mỗi lần kéo thanh trượt).

**Chưa làm (ghi nhận trung thực):** Spark Structured Streaming consumer cho Kafka, PINN training
loop, **phát hiện dị thường khí hậu** và các panel hỗ trợ quyết định (UAV/nông nghiệp/năng lượng) —
xem trạng thái đầy đủ tại `docs/03-ke-hoach-160-tasks.md`.

## 4. Rà soát rủi ro — cập nhật sau Tuần 2 (phần TV4)

| Rủi ro | Mức ảnh hưởng | Trạng thái / phương án |
|---|---|---|
| Docker không chạy được, chặn Spark cluster + Kafka | — | **Đã giải quyết 13/10**: chạy thật trên Docker Engine (Linux). Image Bitnami đã bị gỡ khỏi Docker Hub → đổi sang image chính thức `apache/*` |
| GHCN và ISD dùng 2 hệ mã trạm độc lập cho cùng vị trí vật lý | Trung bình-Cao | Entity Resolution theo khoảng cách toạ độ ở Tuần 3 (`docs/11` mục 1) |
| Partition `year/source` chậm hơn ở quy mô hiện tại (đã đo lại trên 9,3 triệu dòng) | Thấp | Giữ partition (đúng thiết kế cho quy mô lớn hơn/object storage), trình bày kết quả đo thật trong báo cáo |
| Tải lại ERA5 tốn ~1 TB lưu lượng, ~24 giờ | Trung bình | Dữ liệu thô không nằm trong git — chia sẻ thư mục `data_samples/` (hoặc chỉ `warehouse/output/`, 303 MB) cho thành viên khác thay vì tải lại |
| Khối lượng TV3+TV4 (PINN, Streaming, Dashboard, dị thường) vẫn là phần nặng nhất | Cao | Phần phát hiện dị thường có thể chuyển một phần sang TV1 (gần với outlier detection Tuần 3) |

---

*Nguồn số liệu: chạy thật `warehouse/build_warehouse.py` và `warehouse/spark_analytics.py` lúc 13/10/2026 trên máy
Linux của TV1 (12 core, Ubuntu 24.04). Tái lập: tải dữ liệu bằng `scripts/download_era5_full.py` +
`scripts/download_full_points.py`, rồi chạy lại 2 script trên (xem README).*
