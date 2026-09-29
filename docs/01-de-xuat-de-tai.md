# Đề xuất đề tài Project — IT5427 Tích hợp và xử lý dữ liệu lớn

## Hệ thống tích hợp và xử lý dữ liệu khí tượng đa nguồn phục vụ phát hiện dị thường khí hậu và hỗ trợ ra quyết định trong nông nghiệp, năng lượng, vận hành UAV khu vực Đông Nam Á

**Nhóm:** 16 (4 thành viên — xem đội hình đầy đủ tại `README.md` gốc repo) · **Giảng viên:** TS. Vũ Tuyết Trinh
**Hướng thực hiện:** Direction 1 — Xây dựng kiến trúc big data có tích hợp và xử lý dữ liệu, kèm dashboard phân tích
**Deadline liên quan:** Danh sách nhóm 26/9 (đã nộp) · Đề xuất đề tài 5/10 · Báo cáo tiến độ 20/10 · Test 27/10 · Báo cáo cuối kỳ 8/11 (Chủ nhật, cả ngày)

---

## 1. Bản chất vấn đề

Đồ án IT5427 yêu cầu xây một hệ thống hoàn chỉnh (Direction 1) thỏa mãn 3V–5V, giải quyết dị biệt (heterogeneity) giữa các nguồn độc lập để đưa về mediated schema, có dashboard và mô hình phân tích/AI giải quyết bài toán thực tế.

Với dữ liệu **thời tiết quá khứ**, bài toán chuyển từ xử lý độ trễ thời gian thực sang **tích hợp không-thời gian (Spatio-Temporal Integration)** giữa dữ liệu lưới vệ tinh/tái phân tích đa chiều và dữ liệu chuỗi thời gian rời rạc tại trạm mặt đất — đây là dạng dị biệt cấu trúc sâu hơn nhiều so với việc ghép 2 bảng CSV thông thường.

## 2. Mô tả phạm vi

Xây dựng mediated schema tích hợp dữ liệu tái phân tích khí quyển ERA5 (toàn cầu/khu vực) với dữ liệu quan trắc trạm bề mặt NOAA ISD/GHCN và dữ liệu bức xạ NASA POWER (+ Open-Meteo làm nguồn đối chiếu), tạo thành **một kho dữ liệu khí tượng đã chuẩn hoá (standardized weather warehouse)** làm nền tảng dùng lại được cho nhiều bài toán phân tích sau này. Trên kho dữ liệu này, nhóm triển khai:

- **Phát hiện dị thường khí hậu** (climate anomaly detection): điểm/khoảng thời gian có giá trị nhiệt độ, lượng mưa, bức xạ lệch bất thường so với phân bố lịch sử cùng khu vực/mùa vụ.
- **Hỗ trợ ra quyết định ứng dụng**: thống kê phục vụ nông nghiệp (dự báo điều kiện canh tác theo mùa) và năng lượng tái tạo (ước lượng tiềm năng bức xạ mặt trời/gió theo khu vực); khuyến nghị khung giờ/khu vực bay UAV an toàn dựa trên tốc độ gió và lượng mưa dự kiến.
- Sử dụng Apache Spark để xử lý dữ liệu phân tán, kết hợp mô hình vật lý/PINN (tuỳ chọn) để đánh giá các chỉ số khí quyển, trực quan hóa toàn bộ trên Dashboard.

> Ảnh vệ tinh quan sát Trái Đất/khí tượng (SAR, quang học) được liệt kê như **nguồn dữ liệu mở rộng tùy chọn** (xem `02-nguon-du-lieu.md`, mục H) — không nằm trong lõi 160 tác vụ để đảm bảo tiến độ, chỉ bổ sung nếu nhóm còn dư thời gian sau khi hoàn thiện 4 nguồn lõi.

---

## 3. Nguồn dữ liệu lõi (đã chốt — 100% miễn phí)

| Nguồn | Bản chất dữ liệu | Độ phân giải | Định dạng & Kích thước | Phương thức truy xuất / Tải |
|---|---|---|---|---|
| **Copernicus ERA5** (ECMWF) | Tái phân tích khí quyển (kết hợp mô hình số + quan sát vệ tinh/mặt đất toàn cầu), 1940–nay | 0.25°×0.25° (~28km), 1 giờ/lần, nhiều tầng áp suất khí quyển | NetCDF4/GRIB2 (mảng đa chiều n-D). Kích thước gốc hàng trăm TB | Thư viện Python `cdsapi` gọi REST API tự động, batch download theo script, cắt bounding box (VD: Đông Dương/Đông Nam Á). Cần tài khoản CDS (miễn phí) |
| **NOAA ISD/GHCN** (NCEI) | Quan sát chuỗi thời gian từ hơn 14.000 trạm khí tượng bề mặt toàn cầu | Điểm, 1–3 giờ/lần, lịch sử hàng chục năm | CSV/Fixed-width ASCII, vài chục–hàng trăm GB nén | AWS Open Data `s3://noaa-ghcn-pds/` (không cần key, AWS CLI) hoặc FTP/HTTP NCEI |
| **NASA POWER** | Thông lượng bức xạ mặt trời, thông số bề mặt/khí quyển tổng hợp từ vệ tinh | 0.5°×0.5°, giờ/ngày | JSON/CSV | REST API công khai `power.larc.nasa.gov/api`, không cần xác thực phức tạp |
| **Open-Meteo Historical** | Dữ liệu thời tiết lịch sử nội suy từ nhiều mô hình mở (ERA5, DWD, NOAA) | Điểm/lưới khu vực, theo giờ | JSON/Parquet | REST API, không cần API key |

**Thách thức cốt lõi:** ghép dữ liệu dạng lưới (ô ~28km×28km) với dữ liệu điểm (tọa độ chính xác 1 trạm) sinh xung đột cấu trúc không giải quyết được bằng phép JOIN thông thường — cần nội suy không gian (Kriging/Bilinear). Xử lý NetCDF đa chiều nhiều năm nếu không có chiến lược chunking/quản lý VRAM hợp lý sẽ làm tràn bộ nhớ và đánh sập pipeline.

---

## 4. Tính toán định lượng tiêu chuẩn 5V

| Thuộc tính 5V | Cách thức định lượng và kỹ thuật chứng minh | Đánh giá |
|---|---|---|
| **Volume** | Lưới ERA5: 5 tầng áp suất × 6 biến khí tượng × 24h/ngày × 365 ngày × 5 năm (2019–2024) = 1.314.000 mảng dữ liệu. Vùng Đông Dương (20°×15°, lưới 0.25° ≈ 4.800 ô), mỗi mảng float32 ~19.2KB → **~25GB**. Mở rộng phạm vi/biến → dễ đạt **~1.5–2 TB** nhị phân thô. Dữ liệu NOAA: 500 trạm × 10 năm → hàng trăm triệu bản ghi dạng bảng, vượt ngưỡng xử lý Excel/MySQL đơn lẻ, bắt buộc HDFS/Parquet + Spark | **Đạt** |
| **Variety** | Cú pháp: NetCDF4/HDF5 (mảng nhị phân tự mô tả) vs CSV/ASCII (bảng phân tách dấu cách) vs JSON (phân cấp lồng nhau). Cấu trúc: dữ liệu lưới liên tục (gridded spatio-temporal array) đối đầu trực tiếp với chuỗi thời gian rời rạc tại điểm (point time-series). Ngữ nghĩa: đơn vị nhiệt độ (°C/K/°F), áp suất (hPa/Pa/mmHg), chuẩn thời gian (UTC vs Local) | **Đạt tuyệt đối** |
| **Velocity** | Dữ liệu lịch sử là tĩnh (batch). Áp dụng kiến trúc **Replay Streaming Pipeline**: module Python đọc file lịch sử, bắn vào Apache Kafka với tần suất đẩy nhanh (VD: mô phỏng 10 năm dữ liệu chạy trong 30 phút), Spark Streaming hứng luồng tính cửa sổ trượt (Tumbling/Sliding Window) | **Đạt (qua cơ chế giả lập luồng)** |
| **Veracity** | Dữ liệu trạm NOAA chứa nhiều giá trị mất mát (`-9999`, null), cảm biến bị trôi giá trị (sensor drift); dữ liệu vệ tinh ERA5 có sai số làm mịn mô hình hóa ở địa hình phức tạp. Cần thuật toán lọc nhiễu, chuẩn hóa ngoại lai (outlier detection), đánh giá độ tin cậy nguồn | **Đạt** |
| **Value** | Cung cấp mediated view hợp nhất cho phép: (1) phát hiện dị thường khí hậu theo khu vực/thời điểm, (2) hỗ trợ nông nghiệp và năng lượng tái tạo (ước lượng tiềm năng bức xạ/gió), (3) khuyến nghị khung giờ bay UAV an toàn dựa trên gió/mưa dự kiến, (4) kho dữ liệu chuẩn hoá làm nền cho các phân tích khí hậu tiếp theo | **Đạt** |

---

## 5. Các yếu tố thời tiết cấu thành & kỹ thuật xử lý

### 5.1. Nhóm biến

1. **Nhiệt động lực học:** Nhiệt độ không khí (T), Nhiệt độ điểm sương (T_d), Áp suất khí quyển bề mặt và trên cao (P)
2. **Độ ẩm và thủy văn:** Độ ẩm tương đối (RH), Lượng mưa tích lũy (R), Độ ẩm riêng (q)
3. **Động lực học chất lưu:** Vận tốc gió thành phần u (Tây–Đông), v (Nam–Bắc), gió giật (wind gust)
4. **Bức xạ và tương tác bề mặt:** Bức xạ mặt trời sóng ngắn (solar irradiance/DNI), độ che phủ mây, nồng độ sol khí (AOD)

### 5.2. Xử lý riêng biệt từng yếu tố (Data Profiling & Preprocessing)

- **Chuẩn hóa đơn vị/thang đo**: T → Kelvin, P → Pascal, tốc độ gió → m/s
- **Xử lý khuyết thiếu (missing-value policy)** — khác nhau theo bản chất biến:
  - Nhiệt độ, áp suất: nội suy bậc nhất (linear) hoặc spline theo trục thời gian (biến thiên liên tục)
  - Lượng mưa, bức xạ: **không** nội suy tuyến tính thông thường — áp dụng zero-fill khi độ che phủ mây = 0, hoặc mô hình phân phối xác suất Markov Chain
- **Liên kết không gian (spatial interpolation/schema alignment)**: chuyển dữ liệu trạm điểm (x, y) sang cùng hệ quy chiếu lưới ERA5 bằng Kriging hoặc Bilinear Spline Interpolation, phục vụ Record Linkage

### 5.3. Tích hợp bằng mô hình vật lý (Physics-Informed Integration — điểm nhấn học thuật, có thể giản lược nếu thiếu thời gian)

Dùng định luật bảo toàn để ràng buộc các yếu tố dữ liệu rời rạc, không cho mô hình học máy sinh kết quả phi logic:

1. **Clausius-Clapeyron** — ràng buộc giữa áp suất hơi bão hòa (e_s), nhiệt độ (T) và độ ẩm tương đối (RH), dùng để đối soát tính nhất quán giữa 3 nguồn (data fusion & veracity check):

$$e_s(T) = 611.2 \times \exp\left(\frac{17.67(T - 273.15)}{T - 29.65}\right), \quad RH = \frac{e}{e_s(T)} \times 100$$

2. **Navier-Stokes rút gọn 2D** (tầng bề mặt) — ràng buộc gradient áp suất (∇P) với biến thiên trường gió (u, v) và lực Coriolis (f):

$$\frac{\partial u}{\partial t} + u\frac{\partial u}{\partial x} + v\frac{\partial u}{\partial y} - fv = -\frac{1}{\rho}\frac{\partial P}{\partial x}$$

3. **PINN (Physics-Informed Neural Networks)**:
   - Data Loss: $\mathcal{L}_{\text{data}} = \frac{1}{N}\sum \Vert y_{\text{pred}} - y_{\text{true}} \Vert^2$ (so với dữ liệu thực nghiệm ERA5/NOAA đã làm sạch)
   - Physics Loss: $\mathcal{L}_{\text{physics}} = \Vert \text{Residue(Navier-Stokes)} \Vert^2 + \Vert \text{Residue(Clausius-Clapeyron)} \Vert^2$
   - Tổng: $\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{data}} + \lambda \mathcal{L}_{\text{physics}}$ (λ là siêu tham số cân bằng)

> **Phương án lùi**: nếu nhóm chưa tự tin với PyTorch/autograd/phương trình vi phân, có thể thay PINN bằng mô hình hồi quy khí hậu thông thường (Spark MLlib) — vẫn đáp ứng đủ yêu cầu môn học, PINN chỉ là điểm cộng chứ không bắt buộc.

---

## 6. Kiến trúc hệ thống

```
Nguồn: ERA5 (cdsapi) · NOAA ISD/GHCN (AWS S3) · NASA POWER (REST) · Open-Meteo (REST)
        │
        ▼
   Raw Zone (NetCDF/GRIB2, CSV, JSON thô)
        │
        ▼
  Chuẩn hoá đơn vị/thời gian + Missing-value policy theo từng biến (TV1)
        │
        ▼
  Spatial Interpolation (Kriging/Bilinear) — gán trạm điểm vào ô lưới ERA5 (TV2)
        │
        ▼
  Mediated Schema Warehouse — Parquet, partition Year/Month/Region (TV2)
        │
   ┌────┴─────────────────┐
   ▼                      ▼
Batch Analytics       Kafka Replay Streaming → Spark Structured Streaming (TV1/TV3)
(Spark SQL, MLlib)          │
   │                        ▼
   └──────► PINN training/inference (Data Loss + Physics Loss) (TV3)
                             │
                             ▼
              Dashboard: bản đồ nhiệt, time-series trạm,
              cảnh báo dị thường khí hậu, panel khuyến nghị bay UAV,
              thống kê hỗ trợ nông nghiệp/năng lượng (TV4)
```

---

## 7. Phân công 4 thành viên

| TV | Họ tên | Vai trò | Trọng tâm | Công việc chính theo mốc |
|---|---|---|---|---|
| **TV1** | Ngô Văn Quang | Ingestion Lead | Syntactic/Format Heterogeneity | 26/9–5/10: script tải ERA5 (cdsapi)/NOAA (S3)/POWER (REST). 6/10–20/10: parser NetCDF/CSV, chuẩn hóa UTC + đơn vị, Kafka producer replay. 21/10–8/11: ổn định pipeline, tối ưu I/O, đóng gói Docker |
| **TV2** | Nguyễn Cao Lương | Schema Lead | Structural/Semantic Heterogeneity, Entity Resolution | 26/9–5/10: thiết kế Mediated Schema (GAV/LAV), ERD. 6/10–20/10: warehouse Parquet partition Year/Month/Region, Kriging/Bilinear interpolation, Record Linkage trạm↔lưới, Survivorship rules. 21/10–8/11: tối ưu Spark SQL, cross-validation sai số nội suy, Data Quality Report |
| **TV3** | *(cần bổ sung)* | Spark/PINN Lead | Scalable Processing, PINN | 26/9–5/10: dựng Spark (Docker Compose multi-node). 6/10–20/10: transformation tính correlation, chuẩn bị tensor cho PINN, Spark Streaming windowing. 21/10–8/11: huấn luyện PINN (data loss + physics loss), benchmark hiệu năng, pipeline inference |
| **TV4** | Trương Tuấn Nghĩa | Dashboard/PM Lead | Visualization, PM | 26/9–5/10: roadmap, template đề cương, board quản lý việc. 6/10–20/10: dashboard (Streamlit/Superset) heatmap không gian + time-series trạm, tích hợp dữ liệu thật. 21/10–8/11: tích hợp kết quả PINN, panel cảnh báo bất thường khí hậu, tổng hợp báo cáo/slide bảo vệ |

> Bổ sung tên thành viên thứ 4 (TV3) trước khi nộp đề cương ngày 5/10.

---

## 8. Timeline chi tiết — 160 tác vụ (10 tác vụ/người/tuần × 4 tuần)

Kế hoạch đầy đủ theo từng tuần/ngày/tiêu chí kiểm thử (Definition of Done) cho cả 4 thành viên nằm trong file `Ke-hoach-160-tasks.md` cùng thư mục này. Tóm tắt 4 mốc lớn:

| Tuần | Khoảng thời gian | Mốc kết thúc | Trọng tâm |
|---|---|---|---|
| 1 | 26/9 – 5/10 | **Nộp đề cương (5/10)** | Setup tài khoản/API, script tải mẫu, thiết kế schema nháp (ERD), dựng môi trường Spark local, roadmap + template đề cương |
| 2 | 6/10 – 19/10 | **Báo cáo tiến độ (20/10)** | Tải batch đầy đủ 4 nguồn, parser + chuẩn hóa, Mediated Schema chính thức trên Spark SQL, cụm Spark Docker multi-node, Kafka streaming cơ bản, dashboard khung có dữ liệu thật |
| 3 | 20/10 – 2/11 | Hội tụ hệ thống (2/11) | Mở rộng dữ liệu theo phản hồi, xử lý outlier/sensor drift, Record Linkage quy mô đầy đủ + cross-validation, huấn luyện PINN baseline + v2 (Navier-Stokes), tối ưu data skew, dashboard nâng cấp (time slider, panel cảnh báo bất thường khí hậu) |
| 4 | 3/11 – 8/11 | **Báo cáo cuối kỳ (8/11)** | Data freeze, README tái lập, demo trực tiếp từng phần, Q&A phản biện dự kiến, dry-run, nộp & bảo vệ |

---

## 9. Công nghệ dự kiến

- **Thu thập**: Python (`cdsapi`, `requests`, AWS CLI/`boto3`)
- **Xử lý mảng đa chiều**: `xarray`, `dask` (chunking), `netCDF4`
- **Nội suy không gian**: `pykrige`, `scipy.interpolate`
- **Lưu trữ**: Parquet partition Year/Month/Region (local hoặc HDFS/MinIO giả lập)
- **Xử lý phân tán**: Apache Spark (PySpark) — Spark SQL, Spark Structured Streaming, Spark MLlib
- **Streaming giả lập**: Apache Kafka (replay pipeline)
- **Mô hình vật lý-ML**: PyTorch + DeepXDE hoặc custom physics loss (tuỳ chọn, có phương án lùi về MLlib)
- **Dashboard**: Streamlit / Apache Superset / Grafana
- **Hạ tầng**: Docker Compose (Spark cluster giả lập nhiều node, Kafka, dashboard)

---

## 10. Câu hỏi phản biện cần chuẩn bị trước

1. Việc ánh xạ dữ liệu trạm NOAA (tọa độ điểm không đồng đều) vào ô lưới ERA5 (0.25°) bằng nội suy có thể tạo "ảo giác chính xác" ở vùng địa hình chia cắt phức tạp — nhóm có cơ chế kiểm chuẩn (cross-validation, leave-one-station-out) nào để đo sai số này?
2. Trên hạ tầng phần cứng giới hạn của sinh viên, chiến lược phân chia partition (theo không gian hay thời gian) sẽ thiết kế thế nào để tránh data skew giữa các node tính toán khi thực hiện Record Linkage?
3. Khi nhúng phương trình vật lý vào hàm mất mát, nhóm cân bằng trọng số λ giữa Data Loss (nhiều sai số đo lường thực tế) và Physics Loss (mang tính lý tưởng hóa) như thế nào?

---

## 11. Rủi ro & phương án dự phòng

- **Tràn VRAM/RAM khi xử lý NetCDF đa chiều**: chunking bằng `xarray` + `dask`, giới hạn bounding box/số biến ở giai đoạn đầu, tăng dần theo phản hồi báo cáo tiến độ
- **PINN quá khó nếu nhóm chưa quen PyTorch/toán vi phân**: có phương án lùi về mô hình hồi quy MLlib thường, vẫn đủ đáp ứng yêu cầu môn học — chỉ làm PINN nếu TV3 tự tin
- **Data skew khi partition theo khu vực**: theo dõi phân bố qua Spark UI từ sớm (tuần 2), repartition lại theo kết quả benchmark tuần 3
- **Đăng ký tài khoản CDS/Earthdata mất thời gian xử lý**: đăng ký ngay từ tuần 1, ưu tiên các nguồn không cần key trước (ERA5-AWS Zarr, NOAA AWS, NASA POWER, Open-Meteo) nếu tài khoản CDS chưa duyệt kịp

---

## Tài liệu liên quan trong thư mục này

- `03-ke-hoach-160-tasks.md` — kế hoạch chi tiết 160 tác vụ theo tuần/ngày, có tiêu chí kiểm thử (Definition of Done) cho từng vai trò
- `02-nguon-du-lieu.md` — 24 nguồn dữ liệu khí tượng/khí hậu miễn phí mở rộng (bao gồm mục H: ảnh vệ tinh SAR/quang học/khí tượng tuỳ chọn), dùng để làm giàu Variety/Veracity nếu nhóm còn dư sức sau khi làm chắc 4 nguồn lõi ở trên
- `04-ghi-chu-phan-tich.md` — phân tích hai mặt + câu hỏi phản biện chuẩn bị trước
