# Kế hoạch chi tiết 160 tác vụ — IT5427, Nhóm 16

**Đề tài:** Hệ thống tích hợp và xử lý dữ liệu khí tượng đa nguồn phục vụ phát hiện dị thường khí hậu và hỗ trợ ra quyết định đa ngành khu vực Đông Nam Á
**Nguồn dữ liệu:** ERA5 (Copernicus CDS) · NOAA ISD/GHCN (AWS S3) · NASA POWER · Open-Meteo Historical
**Thời lượng:** 4 tuần (26/9 – 8/11/2026) · 4 thành viên · 10 tác vụ/người/tuần = **160 tác vụ**
**Mốc lớn:** 26/9 Chốt nhóm → 5/10 Nộp đề cương → 20/10 Báo cáo tiến độ → 27/10 Test → 8/11 Báo cáo cuối kỳ

**Vai trò:**
- **TV1 — Ingestion Lead (Ngô Văn Quang, 20251243M):** Thu thập & làm sạch dữ liệu đa nguồn (Syntactic/Format Heterogeneity)
- **TV2 — Schema Lead (Nguyễn Cao Lương, 20251244M):** Lược đồ trung gian & kho dữ liệu (Structural/Semantic Heterogeneity, Entity Resolution)
- **TV3 — Spark/PINN Lead (cần bổ sung tên):** Tính toán phân tán & mô hình vật lý-học máy (Scalable Processing, PINN)
- **TV4 — Dashboard/PM Lead (Trương Tuấn Nghĩa, 20251196M):** Trực quan hoá, quản trị chất lượng & điều phối dự án

> Ghi chú: cột **Kiểm thử** là điều kiện xác nhận "Done" (Definition of Done) — mỗi tác vụ chỉ tick hoàn thành khi vượt qua kiểm thử tương ứng. Bổ sung tên thành viên TV3 trước khi nộp đề cương 5/10.

---

## Tuần 1 (26/9 – 5/10) — Khởi động & Đề cương
**Mốc:** Nộp đề cương đề tài 5/10

### TV1 — Ingestion Lead

| # | Nhiệm vụ | Deadline | Yêu cầu cần đạt | Kiểm thử |
|---|---|---|---|---|
| 1 | Họp nhóm chốt vai trò, kênh liên lạc (Discord/Slack), repo Git chung | 26/9 | Biên bản họp ghi rõ 4 vai trò, link repo, kênh chat | Cả 4 thành viên xác nhận truy cập được repo và kênh chat |
| 2 | Đăng ký Copernicus CDS, lấy CDS API key, đọc tài liệu ERA5 | 27/9 | Có API key hoạt động, file `.cdsapirc` cấu hình đúng | Chạy `cdsapi.Client()` không báo lỗi xác thực |
| 3 | Kiểm tra quyền truy cập AWS S3 `noaa-ghcn-pds` (public) | 28/9 | Liệt kê được bucket không cần credential | `aws s3 ls s3://noaa-ghcn-pds/ --no-sign-request` trả về danh sách |
| 4 | Test REST API NASA POWER và Open-Meteo Historical | 29/9 | Gọi thành công cả 2 API, nhận HTTP 200 | `curl` trả JSON hợp lệ cho cả 2 endpoint với 1 toạ độ mẫu |
| 5 | Script tải mẫu ERA5 (1 ngày, 1 biến, vùng nhỏ) bằng `cdsapi` | 30/9 | File NetCDF4 tải về, mở được bằng `xarray.open_dataset` | `python download_sample.py` chạy xong, file `.nc` > 0 byte, đọc được |
| 6 | Script tải mẫu CSV NOAA ISD qua AWS CLI cho 5 trạm ĐNA | 1/10 | 5 file CSV tải về đúng trạm đã chọn | Đếm số dòng > 0 mỗi file, cột khớp schema ISD gốc |
| 7 | Script gọi NASA POWER lấy dữ liệu mẫu JSON cho 1 toạ độ | 2/10 | JSON parse được thành DataFrame pandas | `pd.json_normalize()` không lỗi, có đủ các biến khí tượng yêu cầu |
| 8 | Bảng đối chiếu 3 nguồn: field, đơn vị, tần suất, độ phân giải | 3/10 | Bảng Markdown/Excel liệt kê đủ field trùng khớp giữa nguồn | TV2 review và xác nhận đủ dữ liệu để map sang schema trung gian |
| 9 | Soạn mục "Data Sources & Volume" cho đề cương | 4/10 | Đoạn văn mô tả nguồn + bảng ước lượng dung lượng (~1.5–2 TB) | TV4 review nội dung khớp định dạng đề cương |
| 10 | Review & nộp đề cương đề tài cùng nhóm | 5/10 | Đề cương hoàn chỉnh, đúng template, xuất PDF | Nộp thành công trên hệ thống của học phần trước 23:59 5/10 |

### TV2 — Schema Lead

| # | Nhiệm vụ | Deadline | Yêu cầu cần đạt | Kiểm thử |
|---|---|---|---|---|
| 1 | Nghiên cứu Mediated Schema / GAV vs LAV cho lưới vs điểm | 26/9 | Ghi chú so sánh 2 hướng tiếp cận, chọn hướng áp dụng | Trình bày được lý do lựa chọn trong buổi họp nhóm |
| 2 | Vẽ ERD nháp: fact table thời tiết + dimension trạm/khu vực/thời gian | 27/9 | Sơ đồ ERD (draw.io/dbdiagram) có ≥ 1 fact + 3 dimension | File ERD export PNG/PDF, review nhóm không phát sinh thiếu bảng |
| 3 | Liệt kê trường cần hợp nhất: T, P, RH, wind u/v, precip, radiation, cloud, AOD | 28/9 | Bảng field: tên, kiểu dữ liệu, đơn vị chuẩn, nguồn gốc | Đối chiếu khớp 100% với bảng đối chiếu 3 nguồn của TV1 |
| 4 | Nghiên cứu Parquet & chiến lược partition Year/Month/Region | 29/9 | Tài liệu ngắn giải thích lý do chọn partition key | Test ghi/đọc thử 1 bảng Parquet có partition bằng PySpark |
| 5 | Dựng môi trường local: PySpark + Parquet + Jupyter | 30/9 | Notebook chạy được lệnh Spark cơ bản (`spark.range(10).show()`) | Notebook chạy không lỗi trên máy TV2 và 1 máy khác trong nhóm |
| 6 | Chốt convention đặt tên bảng/cột, chuẩn thời gian UTC | 1/10 | Văn bản naming convention (snake_case, prefix theo domain) | Cả nhóm áp dụng thống nhất khi review code tuần sau |
| 7 | So sánh Kriging vs Bilinear Interpolation, chọn thư viện | 2/10 | Bảng so sánh ưu/nhược, quyết định dùng `pykrige`/`scipy` | Cài thử thư viện, chạy ví dụ nội suy trên tập toy data thành công |
| 8 | Viết tài liệu "Data Model Design v0" (ERD + giải thích) | 3/10 | File `.md` mô tả đầy đủ schema, đính kèm ERD | TV3, TV4 review và không có câu hỏi mở về cấu trúc bảng |
| 9 | Đóng góp mục "System Architecture" cho đề cương | 4/10 | Sơ đồ kiến trúc tổng thể pipeline (ingest → warehouse → model → dashboard) | TV4 review nội dung khớp định dạng đề cương |
| 10 | Review & nộp đề cương đề tài cùng nhóm | 5/10 | Phần schema/kiến trúc trong đề cương chính xác, nhất quán | Nộp thành công cùng nhóm trước 23:59 5/10 |

### TV3 — Spark/PINN Lead

| # | Nhiệm vụ | Deadline | Yêu cầu cần đạt | Kiểm thử |
|---|---|---|---|---|
| 1 | Cài Apache Spark local standalone, kiểm tra Java/Scala | 26/9 | `spark-shell` khởi động thành công | `spark.version` trả đúng version đã cài, không lỗi JVM |
| 2 | Khảo sát tài nguyên phần cứng nhóm, lên kế hoạch cluster Docker Compose | 27/9 | Bảng RAM/CPU 4 máy, file `docker-compose.yml` nháp | `docker compose config` không báo lỗi cú pháp |
| 3 | Đọc 2–3 paper nền tảng PINN (Raissi et al. 2019) & ví dụ khí tượng | 28/9 | Tóm tắt 1 trang: ý tưởng loss vật lý, ứng dụng khí tượng | Trình bày tóm tắt trong buổi họp nhóm, TV4 xác nhận đủ rõ |
| 4 | Liệt kê phương trình vật lý dùng: Clausius-Clapeyron, Navier-Stokes rút gọn | 29/9 | Văn bản công thức + đơn vị chuẩn cho từng biến | TV2 xác nhận đơn vị khớp với schema đã định nghĩa |
| 5 | Khảo sát framework PINN (DeepXDE/PyTorch custom loss), chọn công cụ | 30/9 | Quyết định công cụ + lý do, cài đặt thành công | Chạy ví dụ PINN mẫu (1D heat equation) không lỗi |
| 6 | Notebook thử Spark đọc 1 file NetCDF mẫu bằng `xarray` → Spark DataFrame | 1/10 | Notebook convert thành công, hiển thị schema DataFrame | `df.printSchema()` khớp số biến trong file NetCDF gốc |
| 7 | Ước lượng VRAM/RAM cần cho huấn luyện PINN theo kích thước dữ liệu dự kiến | 2/10 | Bảng ước lượng theo batch size, số điểm lưới | Con số hợp lý so với phần cứng thực tế của nhóm (không âm/vô lý) |
| 8 | Thiết kế sơ bộ kiến trúc Replay Streaming (Kafka producer) | 3/10 | Sơ đồ luồng: file lịch sử → producer → topic → consumer | TV1 xác nhận khớp với dữ liệu sẽ sinh ra từ pipeline ingest |
| 9 | Đóng góp mục "Computing Infrastructure & Big Data Techniques" cho đề cương | 4/10 | Đoạn mô tả Spark, Kafka, PINN trong đề cương | TV4 review nội dung khớp định dạng đề cương |
| 10 | Review & nộp đề cương đề tài cùng nhóm | 5/10 | Phần hạ tầng tính toán chính xác, khả thi | Nộp thành công cùng nhóm trước 23:59 5/10 |

### TV4 — Dashboard/PM Lead

| # | Nhiệm vụ | Deadline | Yêu cầu cần đạt | Kiểm thử |
|---|---|---|---|---|
| 1 | Lập roadmap tổng thể khớp mốc 26/9–5/10–20/10–8/11 | 26/9 | Gantt chart/roadmap file, có buffer trước mỗi mốc | Cả nhóm xác nhận roadmap khả thi trong buổi họp |
| 2 | Soạn mẫu đề cương theo template môn học | 27/9 | File template đúng cấu trúc: Title, Objectives, Data, Volume, Team | Đối chiếu đủ mục theo yêu cầu đề cương của học phần |
| 3 | Tổng hợp input 3 thành viên để hoàn thiện bản đề cương | 28/9 | Bản đề cương v0.5 tổng hợp đủ nội dung 3 phần | Không còn mục "TBD"/thiếu nội dung |
| 4 | So sánh Streamlit vs Grafana vs Apache Superset | 29/9 | Bảng so sánh khả năng kết nối Spark/Parquet, độ khó cài đặt | Quyết định công cụ cuối cùng, cài thử "Hello World" thành công |
| 5 | Dựng khung repo GitHub: cấu trúc thư mục, README, CONTRIBUTING | 30/9 | Repo có `/ingestion /warehouse /model /dashboard`, README rõ ràng | `git clone` về máy khác, cấu trúc hiển thị đúng như thiết kế |
| 6 | Thiết lập board quản lý việc, import 160 tác vụ | 1/10 | Board GitHub Projects/Trello có đủ 160 thẻ, gán đúng người | Đếm số thẻ = 160, mỗi thẻ có assignee + deadline |
| 7 | Vẽ bounding box khu vực nghiên cứu trên bản đồ | 2/10 | Toạ độ bounding box (lat/lon min-max) xác định rõ | TV1/TV3 dùng bounding box này tải dữ liệu thử không lỗi |
| 8 | Soạn checklist tiêu chí 5V đính kèm đề cương | 3/10 | Bảng 5V với số liệu ước lượng cụ thể (như bản nháp đã có) | TV1–3 xác nhận số liệu khớp với dữ liệu thực tế dự kiến |
| 9 | Rà soát, format đề cương theo yêu cầu nộp, xuất PDF | 4/10 | File PDF đúng font/margin theo quy định học phần | Mở file PDF không lỗi định dạng, đủ số trang quy định |
| 10 | Nộp đề cương đúng hạn và thông báo cả nhóm | 5/10 | Biên nhận nộp bài (email/hệ thống) | Có xác nhận nộp thành công trước 23:59 5/10 |

---

## Tuần 2 (6/10 – 19/10) — Xây dựng nền tảng
**Mốc:** Báo cáo tiến độ 20/10

### TV1 — Ingestion Lead

| # | Nhiệm vụ | Deadline | Yêu cầu cần đạt | Kiểm thử |
|---|---|---|---|---|
| 1 | Script batch tải ERA5 đầy đủ (bounding box, 5 năm, 6 biến) | 7/10 | Toàn bộ dữ liệu ERA5 theo phạm vi đã chốt tải về đủ | So khớp số file/số ngày với lịch 5 năm, không thiếu tháng nào |
| 2 | Script tải toàn bộ NOAA ISD cho danh sách trạm mục tiêu | 8/10 | CSV đủ cho toàn bộ trạm trong danh sách, 10 năm | Đếm số trạm tải được / tổng số trạm mục tiêu ≥ 95% |
| 3 | Script tải NASA POWER cho lưới điểm tương ứng khu vực | 9/10 | Dữ liệu POWER phủ đủ bounding box đã chọn | So sánh phạm vi toạ độ tải về với bounding box gốc |
| 4 | Script tải Open-Meteo Historical làm nguồn đối chiếu chéo | 10/10 | Dữ liệu Open-Meteo cùng khoảng thời gian với ERA5 | Số ngày dữ liệu Open-Meteo = số ngày ERA5 tương ứng |
| 5 | Module parser NetCDF4/GRIB2 bằng `xarray` → DataFrame chuẩn | 12/10 | Hàm `parse_era5()` trả DataFrame đúng cột đã định nghĩa | Unit test: input file mẫu → output đúng shape & tên cột |
| 6 | Module parser CSV/Fixed-width NOAA ISD, xử lý mã lỗi -9999/NaN | 13/10 | Hàm `parse_isd()` loại bỏ/đánh dấu giá trị lỗi | Unit test: input chứa `-9999` → output là NaN, không crash |
| 7 | Chuẩn hoá thời gian: mọi timestamp về UTC ISO8601 | 15/10 | Toàn bộ 3 nguồn có cột `timestamp_utc` thống nhất | Kiểm tra ngẫu nhiên 10 bản ghi mỗi nguồn, timezone đúng UTC |
| 8 | Chuẩn hoá đơn vị: T→K, P→Pa, gió→m/s | 16/10 | Giá trị sau chuẩn hoá nằm trong khoảng vật lý hợp lý | So sánh trước/sau: T ~ 250–320K, P ~ 90.000–105.000 Pa |
| 9 | Kafka producer đọc dữ liệu lịch sử, publish theo topic riêng | 18/10 | Producer chạy được, publish message vào đúng topic | `kafka-console-consumer` nhận được message đúng định dạng JSON |
| 10 | Viết phần Ingestion cho báo cáo tiến độ | 19/10 | Slide/đoạn báo cáo: khối lượng đã tải, vướng mắc, số liệu | TV4 review nội dung sẵn sàng đưa vào slide chung |

### TV2 — Schema Lead

| # | Nhiệm vụ | Deadline | Yêu cầu cần đạt | Kiểm thử |
|---|---|---|---|---|
| 1 | Hoàn thiện Mediated Schema chính thức (fact + dimension, khoá ngoại) | 7/10 | Script DDL tạo đầy đủ bảng, ràng buộc khoá | Chạy script tạo schema trên Spark SQL không lỗi |
| 2 | Triển khai schema trên Spark SQL/Hive Metastore, bảng Parquet có partition | 8/10 | Bảng thực tế tồn tại, partition theo Year/Month/Region | `SHOW PARTITIONS` trả đúng số partition kỳ vọng |
| 3 | ETL Transform: map dữ liệu chuẩn hoá từ TV1 vào schema trung gian | 9/10 | Job ETL chạy end-to-end từ dữ liệu thô → bảng warehouse | Đếm số bản ghi input ≈ output (trừ phần bị loại do lỗi) |
| 4 | Cài thuật toán nội suy không gian (Kriging/Bilinear) gán trạm vào ô lưới | 10/10 | Hàm nội suy trả giá trị hợp lý tại vị trí trạm | So sánh giá trị nội suy với giá trị lưới lân cận, sai lệch < ngưỡng |
| 5 | Record Linkage: join dữ liệu trạm với ô lưới theo khoá không gian-thời gian | 12/10 | Bảng kết quả join có đủ cột từ cả 2 nguồn | Kiểm tra không có bản ghi trùng lặp/khoá null |
| 6 | Thiết lập quy tắc Survivorship khi giá trị xung đột giữa nguồn | 13/10 | Văn bản quy tắc ưu tiên (VD: ERA5 > POWER khi lệch > X%) | Test case xung đột giả lập, hàm chọn đúng giá trị theo quy tắc |
| 7 | Tối ưu Partitioning theo Năm/Tháng/Khu vực, kiểm tra hiệu năng đọc/ghi | 15/10 | Thời gian query giảm rõ rệt so với bảng không partition | Benchmark trước/sau, ghi lại thời gian (giây) |
| 8 | Unit test kiểm tra toàn vẹn schema (referential integrity, kiểu dữ liệu) | 16/10 | Bộ test tự động cho các ràng buộc chính | `pytest` chạy pass 100% test case |
| 9 | Đo dung lượng thực tế đã lưu, đối chiếu ước lượng 5V ban đầu | 18/10 | Bảng so sánh dung lượng ước tính vs thực tế | Chênh lệch được giải thích rõ nguyên nhân (nếu có) |
| 10 | Viết phần Schema & Warehousing cho báo cáo tiến độ | 19/10 | Slide/đoạn báo cáo: kiến trúc, số liệu, khó khăn | TV4 review nội dung sẵn sàng đưa vào slide chung |

### TV3 — Spark/PINN Lead

| # | Nhiệm vụ | Deadline | Yêu cầu cần đạt | Kiểm thử |
|---|---|---|---|---|
| 1 | Dựng cụm Spark giả lập nhiều node bằng Docker Compose (driver + 2–3 worker) | 7/10 | Cluster khởi động đủ số node, UI Spark truy cập được | Spark Master UI hiển thị đủ số worker đã cấu hình |
| 2 | Kết nối Spark Streaming với Kafka topic từ TV1, xử lý windowing cơ bản | 8/10 | Job Streaming chạy, tính được aggregate theo cửa sổ thời gian | Console output hiển thị kết quả window đúng chu kỳ đã set |
| 3 | Spark transformation tính ma trận tương quan giữa các biến khí tượng | 9/10 | Ma trận correlation xuất ra đúng kích thước n×n | Giá trị đường chéo = 1.0, ma trận đối xứng |
| 4 | Pipeline tiền xử lý dữ liệu đầu vào cho PINN (chuẩn hoá, tensor hoá) | 10/10 | Hàm trả tensor đúng shape (batch, features) | Unit test: input DataFrame mẫu → output tensor đúng dtype/shape |
| 5 | Cài framework huấn luyện (PyTorch + DeepXDE/custom loss) | 12/10 | Môi trường train chạy được ví dụ tối thiểu | Script `train_demo.py` chạy hết 1 epoch không lỗi |
| 6 | Cài Clausius-Clapeyron làm physics loss thử nghiệm trên tập nhỏ | 13/10 | Hàm loss trả giá trị số thực không NaN | Loss giảm dần qua vài epoch trên tập nhỏ |
| 7 | Cài Navier-Stokes 2D rút gọn làm ràng buộc bổ sung, kiểm tra autograd | 15/10 | Gradient tính được qua `autograd` không lỗi | `loss.backward()` chạy thành công, gradient ≠ None |
| 8 | Benchmark Spark: thời gian xử lý, RAM/Core tiêu thụ trên tập mẫu | 16/10 | Bảng số liệu benchmark (thời gian, RAM, số core) | Số liệu ghi lại từ Spark UI/`time` command, có log lưu trữ |
| 9 | Kiểm tra phân bố partition theo trạm/khu vực để phát hiện data skew | 18/10 | Biểu đồ phân bố số bản ghi theo partition | Không có partition nào chiếm > 50% tổng dữ liệu (nếu có, ghi nhận để xử lý tuần 3) |
| 10 | Viết phần Distributed Computing & Physics ML cho báo cáo tiến độ | 19/10 | Slide/đoạn báo cáo: kiến trúc Spark, kết quả PINN sơ bộ | TV4 review nội dung sẵn sàng đưa vào slide chung |

### TV4 — Dashboard/PM Lead

| # | Nhiệm vụ | Deadline | Yêu cầu cần đạt | Kiểm thử |
|---|---|---|---|---|
| 1 | Dựng khung Dashboard (Streamlit) kết nối thử Parquet/Spark qua Thrift Server | 7/10 | App Streamlit chạy local, kết nối lấy được dữ liệu mẫu | `streamlit run app.py` mở trình duyệt, hiển thị bảng dữ liệu |
| 2 | Wireframe Dashboard: bản đồ nhiệt, biểu đồ chuỗi thời gian, panel cảnh báo | 8/10 | File wireframe (Figma/draw.io) đủ 3 khu vực chính | Cả nhóm review, thống nhất bố cục trước khi code |
| 3 | Xây component bản đồ nhiệt không gian (heatmap) hiển thị lưới ERA5 cơ bản | 9/10 | Heatmap hiển thị đúng vùng bounding box đã chọn | Kiểm tra bằng mắt: vùng nóng/lạnh khớp dữ liệu mẫu đã biết |
| 4 | Xây component biểu đồ chuỗi thời gian cho trạm quan trắc | 10/10 | Line chart interactive, chọn được trạm từ dropdown | Đổi trạm → biểu đồ cập nhật đúng dữ liệu trạm đó |
| 5 | Tích hợp một phần dữ liệu thật vào Dashboard để demo tiến độ | 12/10 | Dashboard hiển thị dữ liệu thật (không còn mock) | Chạy demo trước nhóm, không lỗi runtime |
| 6 | Thu thập cập nhật tiến độ từ 3 thành viên, tổng hợp số liệu hoàn thành | 13/10 | Bảng tổng hợp % hoàn thành theo từng mảng | Số liệu khớp với board quản lý việc (GitHub Projects) |
| 7 | Soạn slide báo cáo tiến độ (vấn đề, tiến độ, khó khăn, kế hoạch tiếp) | 15/10 | Bộ slide 8–12 trang theo mẫu học phần | Cả nhóm review, không thiếu phần nào theo yêu cầu báo cáo |
| 8 | Rà soát rủi ro dự án (data skew, VRAM, độ trễ tải) và phương án dự phòng | 16/10 | Bảng rủi ro: mức độ, xác suất, phương án giảm thiểu | Mỗi rủi ro có ít nhất 1 phương án cụ thể, khả thi |
| 9 | Diễn tập thuyết trình báo cáo tiến độ trong nhóm | 18/10 | Buổi diễn tập ghi lại thời gian trình bày từng phần | Tổng thời gian khớp giới hạn báo cáo, không vượt quá |
| 10 | Trình bày báo cáo tiến độ trước lớp/giảng viên | 20/10 | Trình bày đúng hạn, đủ nội dung | Giảng viên xác nhận đã nhận báo cáo, không bị nhắc nhở thiếu |

---

## Tuần 3 (20/10 – 2/11) — Phát triển sâu
**Mốc:** Chuẩn bị hội tụ hệ thống trước tuần hoàn thiện

### TV1 — Ingestion Lead

| # | Nhiệm vụ | Deadline | Yêu cầu cần đạt | Kiểm thử |
|---|---|---|---|---|
| 1 | Mở rộng phạm vi ERA5 (thêm biến/tầng áp suất) theo phản hồi báo cáo tiến độ | 21/10 | Dữ liệu bổ sung tải về đủ theo yêu cầu mới | Đối chiếu danh sách biến mới với phản hồi giảng viên |
| 2 | Veracity: phát hiện & lọc outlier bằng z-score/IQR cho dữ liệu trạm | 22/10 | Hàm `detect_outliers()` gắn cờ bản ghi bất thường | Test với dữ liệu giả lập có outlier rõ ràng, hàm phát hiện đúng ≥ 90% |
| 3 | Xây thuật toán phát hiện sensor drift theo thời gian | 23/10 | Biểu đồ/độ đo phát hiện trạm có xu hướng lệch dần | So sánh với ít nhất 1 trạm biết trước có vấn đề (nếu có) hoặc mô phỏng |
| 4 | Hoàn thiện missing-value policy riêng từng biến (linear/spline vs zero-fill/Markov) | 24/10 | Hàm xử lý missing áp dụng đúng chiến lược theo loại biến | Unit test cho từng loại biến, kết quả không còn NaN không mong muốn |
| 5 | Đóng gói Docker cho toàn bộ pipeline thu thập | 26/10 | `Dockerfile` + `docker-compose.yml` build thành công | `docker compose up` chạy pipeline end-to-end không lỗi |
| 6 | Tối ưu I/O: tải song song (multiprocessing/async) để giảm thời gian ingest | 27/10 | Thời gian tải giảm rõ rệt so với bản tuần tự | Benchmark thời gian trước/sau, ghi lại số liệu cụ thể |
| 7 | Cơ chế retry & logging cho pipeline (lỗi mạng, timeout API) | 29/10 | Pipeline tự retry khi lỗi, log ghi đầy đủ | Giả lập lỗi mạng (ngắt kết nối), pipeline retry và ghi log đúng |
| 8 | Kiểm tra pipeline chạy ổn định end-to-end trên toàn bộ 5 năm dữ liệu | 30/10 | Chạy full pipeline không crash, dữ liệu đầu ra đầy đủ | Log chạy hoàn tất, số bản ghi đầu ra khớp kỳ vọng |
| 9 | Đối chiếu chéo Open-Meteo với ERA5/NOAA để đánh giá độ tin cậy nguồn | 1/11 | Báo cáo sai lệch trung bình giữa các nguồn | RMSE/MAE tính được và nằm trong ngưỡng chấp nhận đã thống nhất |
| 10 | Cập nhật tài liệu kỹ thuật Ingestion (data dictionary, hướng dẫn chạy) | 2/11 | File `docs/ingestion.md` đầy đủ, có ví dụ chạy | Thành viên khác làm theo hướng dẫn chạy được pipeline không hỏi thêm |

### TV2 — Schema Lead

| # | Nhiệm vụ | Deadline | Yêu cầu cần đạt | Kiểm thử |
|---|---|---|---|---|
| 1 | Tối ưu câu truy vấn Spark SQL trên toàn bộ warehouse (query plan, cache) | 21/10 | Thời gian truy vấn chính giảm so với baseline | So sánh `EXPLAIN` trước/sau, thời gian chạy giảm ≥ 30% |
| 2 | Hoàn thiện Record Linkage quy mô đầy đủ (toàn bộ trạm & lưới) | 22/10 | Bảng linkage phủ 100% trạm trong danh sách mục tiêu | Đếm số trạm đã linkage / tổng số trạm = 100% (hoặc ghi rõ ngoại lệ) |
| 3 | Xây cơ chế kiểm chuẩn (cross-validation) sai số nội suy không gian | 23/10 | Script leave-one-station-out cross-validation chạy được | Kết quả xuất ra bảng RMSE/MAE cho từng trạm test |
| 4 | Đo RMSE/MAE nội suy Kriging tại vùng địa hình phức tạp | 24/10 | Bảng số liệu sai số theo từng vùng địa hình | Số liệu có nguồn gốc rõ ràng, lưu vào báo cáo Data Quality |
| 5 | Audit & xử lý xung đột đơn vị/ngữ nghĩa còn sót trong schema | 26/10 | Danh sách xung đột đã phát hiện và đã fix | Chạy lại unit test toàn vẹn schema (tuần 2, #8), pass 100% |
| 6 | Tối ưu chiến lược partition để giảm data skew (phối hợp TV3) | 27/10 | Partition mới cân bằng hơn theo báo cáo skew của TV3 | Phân bố dữ liệu theo partition không còn lệch > 30% |
| 7 | Thiết lập data lineage/versioning cơ bản cho warehouse | 29/10 | Ghi lại lịch sử thay đổi schema/dữ liệu (changelog) | File `CHANGELOG.md` cập nhật đầy đủ theo mốc thời gian |
| 8 | Viết Data Quality Report (tỷ lệ missing, outlier, độ phủ không gian-thời gian) | 30/10 | Báo cáo có số liệu định lượng cụ thể, biểu đồ minh hoạ | TV4 review, số liệu nhất quán với báo cáo của TV1 |
| 9 | Hỗ trợ TV3 chuẩn bị tập train/test cho PINN (split theo thời gian/khu vực) | 1/11 | Bộ dữ liệu train/test tách rõ, không rò rỉ dữ liệu (data leakage) | TV3 xác nhận nhận đủ dữ liệu đúng định dạng để huấn luyện |
| 10 | Cập nhật tài liệu kỹ thuật Schema & Warehousing | 2/11 | File `docs/warehouse.md` đầy đủ, có ví dụ query | Thành viên khác chạy được ví dụ query theo hướng dẫn |

### TV3 — Spark/PINN Lead

| # | Nhiệm vụ | Deadline | Yêu cầu cần đạt | Kiểm thử |
|---|---|---|---|---|
| 1 | Huấn luyện PINN baseline: Data Loss + Physics Loss (Clausius-Clapeyron) | 21/10 | Mô hình huấn luyện hội tụ, loss giảm ổn định | Biểu đồ loss curve giảm dần, không NaN/Inf |
| 2 | Thêm ràng buộc Navier-Stokes rút gọn vào loss, huấn luyện phiên bản 2 | 22/10 | Mô hình v2 huấn luyện xong, loss tổng hội tụ | So sánh loss v1 vs v2, ghi nhận cải thiện hoặc đánh đổi |
| 3 | Thử nhiều giá trị λ cân bằng Data/Physics Loss, ghi log kết quả | 23/10 | Bảng kết quả ≥ 3 giá trị λ khác nhau | Chọn được λ tối ưu dựa trên metric validation |
| 4 | So sánh PINN vs baseline hồi quy thuần (không ràng buộc vật lý) | 24/10 | Bảng so sánh metric (RMSE/MAE) giữa 2 mô hình | PINN có kết quả tốt hơn hoặc giải thích được lý do nếu không |
| 5 | Tối ưu VRAM: chunking/batching dữ liệu đa chiều khi huấn luyện | 26/10 | Huấn luyện chạy được với batch size hợp lý, không OOM | Theo dõi `nvidia-smi`/RAM, không tràn bộ nhớ trong 1 epoch đầy đủ |
| 6 | Đo hiệu năng tính toán phân tán (thời gian, RAM/Core) trên tập đầy đủ | 27/10 | Bảng benchmark chính thức trên toàn bộ dữ liệu | Số liệu ghi lại có timestamp, tái lập được khi chạy lại |
| 7 | Xử lý data skew thực tế (repartition theo khu vực/thời gian) | 29/10 | Partition sau xử lý cân bằng hơn (theo báo cáo tuần 2, #9) | Đo lại phân bố, không còn partition lệch nghiêm trọng |
| 8 | Xây pipeline inference: chạy mô hình đã huấn luyện trên tập test | 30/10 | Script `infer.py` sinh kết quả dự báo từ checkpoint | Chạy trên tập test, output đúng shape, không lỗi |
| 9 | Chuẩn bị output mô hình (dự báo, chỉ số bất thường) để đẩy sang Dashboard | 1/11 | File/API xuất kết quả ở định dạng TV4 dùng được (CSV/Parquet/API) | TV4 xác nhận đọc được dữ liệu từ nguồn TV3 cung cấp |
| 10 | Cập nhật tài liệu kỹ thuật Physics ML (kiến trúc, kết quả huấn luyện) | 2/11 | File `docs/model.md` đầy đủ công thức, kết quả, hướng dẫn chạy | Thành viên khác chạy lại được `infer.py` theo hướng dẫn |

### TV4 — Dashboard/PM Lead

| # | Nhiệm vụ | Deadline | Yêu cầu cần đạt | Kiểm thử |
|---|---|---|---|---|
| 1 | Nâng cấp Dashboard: bản đồ nhiệt động có time slider cho toàn khu vực | 21/10 | Time slider kéo được, bản đồ cập nhật theo thời gian chọn | Kéo slider qua 3 mốc thời gian, bản đồ đổi dữ liệu tương ứng |
| 2 | Tích hợp kết quả PINN vào Dashboard (dự báo, residual, bản đồ bất thường) | 22/10 | Panel hiển thị output từ TV3, không còn dữ liệu mock | Dashboard hiển thị đúng kết quả từ file/API của TV3 |
| 3 | Xây panel cảnh báo bất thường khí tượng (ngưỡng, màu theo mức độ) | 23/10 | Panel đổi màu theo mức độ vượt ngưỡng đã định nghĩa | Test với dữ liệu giả lập vượt ngưỡng, panel hiển thị đúng màu cảnh báo |
| 4 | Xây panel so sánh giá trị khí tượng giữa các nguồn (ERA5 vs NOAA vs Open-Meteo) theo trạm/khu vực | 24/10 | Panel hiển thị song song kết quả 3 nguồn cho cùng 1 điểm/khoảng thời gian | Kết quả tính tay đối chiếu với kết quả trên Dashboard khớp nhau |
| 5 | Tối ưu hiệu năng Dashboard (caching truy vấn, giảm độ trễ tải) | 26/10 | Thời gian tải trang giảm rõ rệt so với bản trước | Đo thời gian load trước/sau, ghi lại số liệu (giây) |
| 6 | Kiểm thử Dashboard trên nhiều kích thước màn hình, sửa lỗi UI | 27/10 | Dashboard hiển thị đúng trên desktop, tablet, mobile | Test bằng DevTools responsive mode ở 3 kích thước, không vỡ layout |
| 7 | Tổng hợp kết quả kỹ thuật từ 3 thành viên chuẩn bị báo cáo cuối kỳ | 29/10 | Tài liệu tổng hợp có đủ nội dung 3 mảng | Không thiếu phần nào so với outline báo cáo cuối kỳ |
| 8 | Soạn khung outline slide báo cáo cuối kỳ (Action Title/logic Minto) | 30/10 | Outline slide có tiêu đề dạng khẳng định (Action Title) | Mỗi slide có 1 kết luận rõ ràng, không phải nhãn dán chủ đề |
| 9 | Rà soát hệ thống end-to-end, lập danh sách lỗi/thiếu sót cần hoàn thiện | 1/11 | Danh sách bug/issue trên GitHub Projects | Mỗi issue có mô tả, mức độ ưu tiên, người phụ trách |
| 10 | Cập nhật kế hoạch quản trị chất lượng & tiến độ chung | 2/11 | Báo cáo % hoàn thành 160 tác vụ tính đến thời điểm này | Số liệu khớp với board quản lý việc |

---

## Tuần 4 (3/11 – 8/11) — Hoàn thiện & Bảo vệ
**Mốc:** Nộp & bảo vệ báo cáo cuối kỳ 8/11

### TV1 — Ingestion Lead

| # | Nhiệm vụ | Deadline | Yêu cầu cần đạt | Kiểm thử |
|---|---|---|---|---|
| 1 | Khắc phục lỗi ingestion còn tồn đọng từ tuần trước (regression fix) | 3/11 | Toàn bộ issue liên quan ingestion đã đóng | Danh sách issue ingestion trên board = 0 open |
| 2 | Chốt phiên bản dữ liệu cuối cùng (data freeze) đảm bảo nhất quán | 3/11 | Dữ liệu không thay đổi thêm sau mốc này | Gắn tag/version cho dataset cuối cùng (VD: `data-v1.0-final`) |
| 3 | Viết README hướng dẫn cài đặt & chạy pipeline ingestion từ đầu | 4/11 | README có đủ bước cài đặt, chạy, kết quả mong đợi | Một thành viên khác làm theo README chạy được, không hỏi thêm |
| 4 | Chuẩn bị demo trực tiếp: chạy pipeline ingestion + Kafka streaming replay | 4/11 | Demo chạy trơn tru trong ≤ 5 phút | Chạy thử demo 2 lần liên tiếp không lỗi |
| 5 | Chốt số liệu 5V thực tế đạt được (Volume/Variety) để đưa vào báo cáo | 5/11 | Bảng số liệu cuối cùng, có nguồn dẫn chứng | Số liệu khớp với dữ liệu đã freeze ở #2 |
| 6 | Hỗ trợ dựng slide "Kiến trúc Ingestion & Xử lý dị biệt cú pháp" | 5/11 | Slide có sơ đồ pipeline + số liệu minh hoạ | TV4 xác nhận slide đạt chuẩn Action Title |
| 7 | Kiểm tra bảo mật/license dữ liệu, đảm bảo tuân thủ điều khoản nguồn mở | 6/11 | Danh sách nguồn dữ liệu kèm giấy phép sử dụng | Không nguồn nào vi phạm điều khoản sử dụng phi thương mại/học thuật |
| 8 | Viết câu trả lời dự kiến cho phản biện về ingestion/veracity | 6/11 | Văn bản Q&A ≥ 3 câu hỏi/trả lời dự kiến | Cả nhóm review, câu trả lời logic, có số liệu hỗ trợ |
| 9 | Diễn tập trình bày phần của mình trong buổi bảo vệ | 7/11 | Trình bày trong đúng thời lượng được phân bổ | Đo thời gian thực tế, không vượt quá giới hạn |
| 10 | Tham gia buổi bảo vệ báo cáo cuối kỳ | 8/11 | Có mặt, trình bày đúng phần phụ trách | Giảng viên/hội đồng xác nhận đã trình bày |

### TV2 — Schema Lead

| # | Nhiệm vụ | Deadline | Yêu cầu cần đạt | Kiểm thử |
|---|---|---|---|---|
| 1 | Hoàn thiện & chốt phiên bản cuối schema + warehouse (freeze cấu trúc) | 3/11 | Không thay đổi DDL sau mốc này | Gắn tag `schema-v1.0-final` trên repo |
| 2 | Viết Data Dictionary đầy đủ (bảng/cột/đơn vị/nguồn gốc) | 3/11 | File `data_dictionary.md`/Excel liệt kê 100% cột | Đối chiếu số cột trong tài liệu = số cột thực tế trong warehouse |
| 3 | Chuẩn bị demo Spark SQL minh hoạ Record Linkage & Survivorship | 4/11 | Câu query demo chạy trả kết quả đúng, dễ hiểu | Chạy demo 2 lần liên tiếp không lỗi, kết quả nhất quán |
| 4 | Tổng hợp kết quả kiểm chuẩn sai số nội suy (bảng số liệu, biểu đồ) | 4/11 | Biểu đồ/bảng RMSE/MAE hoàn chỉnh cho báo cáo | TV4 xác nhận số liệu sẵn sàng đưa vào slide |
| 5 | Hỗ trợ dựng slide "Mediated Schema & Entity Resolution" | 5/11 | Slide có ERD + số liệu Record Linkage | TV4 xác nhận slide đạt chuẩn Action Title |
| 6 | Viết câu trả lời dự kiến cho phản biện về "ảo giác chính xác" khi nội suy | 5/11 | Văn bản trả lời có dẫn chứng số liệu cross-validation | Cả nhóm review, trả lời trực tiếp đúng trọng tâm câu hỏi gốc |
| 7 | Rà soát nhất quán dữ liệu lần cuối trước khi đóng băng (data freeze) | 6/11 | Không còn xung đột schema/dữ liệu phát hiện được | Chạy lại toàn bộ unit test schema, pass 100% |
| 8 | Đóng gói script/warehouse kèm hướng dẫn tái lập để nộp báo cáo | 6/11 | File nén/archive kèm README tái lập | Giải nén trên máy khác, chạy lại theo hướng dẫn thành công |
| 9 | Diễn tập trình bày phần của mình trong buổi bảo vệ | 7/11 | Trình bày trong đúng thời lượng được phân bổ | Đo thời gian thực tế, không vượt quá giới hạn |
| 10 | Tham gia buổi bảo vệ báo cáo cuối kỳ | 8/11 | Có mặt, trình bày đúng phần phụ trách | Giảng viên/hội đồng xác nhận đã trình bày |

### TV3 — Spark/PINN Lead

| # | Nhiệm vụ | Deadline | Yêu cầu cần đạt | Kiểm thử |
|---|---|---|---|---|
| 1 | Chốt phiên bản PINN cuối cùng, lưu checkpoint & kết quả đánh giá | 3/11 | File checkpoint `.pt`/`.pth` cùng file metric cuối cùng | Load lại checkpoint, chạy inference cho kết quả giống lần huấn luyện |
| 2 | Tổng hợp bảng benchmark hiệu năng tính toán phân tán chính thức | 3/11 | Bảng số liệu thời gian/RAM/Core hoàn chỉnh cho báo cáo | TV4 xác nhận số liệu sẵn sàng đưa vào slide |
| 3 | Chuẩn bị demo trực tiếp: chạy inference mô hình + hiển thị kết quả | 4/11 | Demo chạy trong ≤ 3 phút, có kết quả trực quan | Chạy thử demo 2 lần liên tiếp không lỗi |
| 4 | Viết câu trả lời dự kiến cho phản biện về partition/data skew | 4/11 | Văn bản trả lời có số liệu skew trước/sau xử lý | Cả nhóm review, trả lời trực tiếp đúng trọng tâm câu hỏi gốc |
| 5 | Hỗ trợ dựng slide "Physics-Informed Integration & Distributed Computing" | 5/11 | Slide có công thức, kiến trúc mô hình, kết quả benchmark | TV4 xác nhận slide đạt chuẩn Action Title |
| 6 | Viết tài liệu kỹ thuật mô hình (kiến trúc, phương trình, siêu tham số) | 5/11 | File `docs/model.md` cập nhật đầy đủ phiên bản cuối | Thành viên khác đọc hiểu được kiến trúc mà không cần hỏi thêm |
| 7 | Kiểm tra khả năng tái lập: seed, `environment.yml`/`requirements.txt` | 6/11 | Môi trường cài lại từ file cấu hình, huấn luyện lại cho kết quả tương tự | Cài trên máy sạch (venv mới), chạy `train.py` không lỗi thiếu thư viện |
| 8 | Đóng gói notebook/code huấn luyện kèm báo cáo | 6/11 | Archive code + checkpoint + hướng dẫn chạy | Giải nén trên máy khác, chạy lại theo hướng dẫn thành công |
| 9 | Diễn tập trình bày phần của mình trong buổi bảo vệ | 7/11 | Trình bày trong đúng thời lượng được phân bổ | Đo thời gian thực tế, không vượt quá giới hạn |
| 10 | Tham gia buổi bảo vệ báo cáo cuối kỳ | 8/11 | Có mặt, trình bày đúng phần phụ trách | Giảng viên/hội đồng xác nhận đã trình bày |

### TV4 — Dashboard/PM Lead

| # | Nhiệm vụ | Deadline | Yêu cầu cần đạt | Kiểm thử |
|---|---|---|---|---|
| 1 | Hoàn thiện Dashboard phiên bản cuối (giao diện, hiệu năng, dữ liệu mới nhất) | 3/11 | Dashboard chạy ổn định với dữ liệu đã freeze | Chạy Dashboard liên tục 15 phút không crash |
| 2 | Tổng hợp báo cáo kỹ thuật từ 4 thành viên thành báo cáo cuối kỳ hoàn chỉnh | 3/11 | File báo cáo đầy đủ theo mẫu học phần | Đối chiếu đủ mục theo yêu cầu báo cáo cuối kỳ |
| 3 | Thiết kế & hoàn thiện slide thuyết trình bảo vệ cho cả nhóm | 4/11 | Bộ slide hoàn chỉnh, nhất quán phong cách | Cả nhóm review lần cuối, không còn góp ý lớn |
| 4 | Chuẩn bị kịch bản demo tổng thể (thứ tự trình bày, phân công demo) | 4/11 | Văn bản kịch bản có mốc thời gian từng phần | Tổng thời gian kịch bản khớp giới hạn buổi bảo vệ |
| 5 | Tổ chức buổi chạy thử toàn bộ (dry-run) trước ngày bảo vệ | 5/11 | Dry-run chạy hết kịch bản, ghi nhận vấn đề phát sinh | Không có lỗi kỹ thuật nghiêm trọng trong dry-run |
| 6 | Chuẩn bị bộ câu hỏi phản biện dự kiến + đáp án cho cả nhóm | 5/11 | Tài liệu tổng hợp Q&A từ cả 4 thành viên | Có ít nhất 8 cặp câu hỏi/trả lời bao phủ các mảng |
| 7 | Kiểm tra định dạng nộp bài theo yêu cầu học phần (PDF, deadline, kênh nộp) | 6/11 | File nộp đúng định dạng, đúng dung lượng cho phép | Thử tải lên hệ thống nộp bài (nếu có sandbox) hoặc đối chiếu quy định |
| 8 | Làm video/backup demo phòng lỗi kỹ thuật khi trình bày trực tiếp | 6/11 | Video demo hoàn chỉnh, phát lại được không lỗi | Phát thử video trên máy trình bày thực tế, âm thanh/hình ảnh ổn |
| 9 | Điều phối buổi bảo vệ, quản lý thời gian trình bày từng thành viên | 7/11 | Lịch trình bày chi tiết theo phút cho từng thành viên | Cả nhóm xác nhận đã nắm rõ thứ tự và thời gian |
| 10 | Nộp báo cáo cuối kỳ và trình bày bảo vệ trước hội đồng | 8/11 | Nộp đúng hạn, trình bày đầy đủ nội dung | Biên nhận nộp bài + xác nhận của hội đồng sau buổi bảo vệ |

---

## Tổng kết

| Tuần | Số tác vụ | Mốc kết thúc |
|---|---|---|
| Tuần 1 | 40 (10 × 4) | Nộp đề cương — 5/10 |
| Tuần 2 | 40 (10 × 4) | Báo cáo tiến độ — 20/10 |
| Tuần 3 | 40 (10 × 4) | Hội tụ hệ thống — 2/11 |
| Tuần 4 | 40 (10 × 4) | Báo cáo cuối kỳ — 8/11 |
| **Tổng** | **160** | |
