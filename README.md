# Hệ thống tích hợp và xử lý dữ liệu khí tượng đa nguồn phục vụ phát hiện dị thường khí hậu và hỗ trợ ra quyết định đa ngành khu vực Đông Nam Á

**Học phần:** IT5427 — Tích hợp và xử lý dữ liệu lớn
**Giảng viên:** TS. Vũ Tuyết Trinh — Trường Công nghệ Thông tin và Truyền thông, Đại học Bách khoa Hà Nội
**Nhóm:** 16 · **Hướng thực hiện:** Direction 1 — Xây dựng kiến trúc big data có tích hợp và xử lý dữ liệu, kèm dashboard phân tích
**Trạng thái:** Đang triển khai · Repo tạm để **private** trong quá trình làm đồ án

---

## 1. Tóm tắt đề tài

Xây dựng một hệ thống tích hợp dữ liệu khí tượng lịch sử từ nhiều nguồn mở có bản chất khác nhau — dữ liệu tái phân tích dạng lưới toàn cầu (ERA5), dữ liệu quan trắc trạm mặt đất (NOAA ISD/GHCN), và dữ liệu bức xạ vệ tinh (NASA POWER) — đưa về một lược đồ trung gian (mediated schema) thống nhất, tạo thành **kho dữ liệu khí tượng đã chuẩn hoá** làm nền cho các phân tích sau này. Trên kho dữ liệu này, hệ thống thực hiện **phát hiện dị thường khí hậu** theo khu vực/thời điểm và cung cấp thống kê hỗ trợ ra quyết định cho **nông nghiệp, năng lượng tái tạo, và vận hành UAV an toàn** (khuyến nghị khung giờ bay dựa trên gió/mưa), xử lý bằng Apache Spark (batch và streaming giả lập), trực quan hoá kết quả trên dashboard.

Bài toán tích hợp cốt lõi là xử lý dị biệt không-thời gian (**Spatio-Temporal Heterogeneity**) giữa dữ liệu lưới liên tục và dữ liệu điểm rời rạc — đây là dạng dị biệt cấu trúc sâu hơn nhiều so với việc ghép các bảng có cùng định dạng, và là lý do đề tài này bám sát trực tiếp các nội dung lý thuyết cốt lõi của học phần: Schema Alignment, Record Linkage/Entity Resolution, Sources Profiling, Batch vs. Streaming Integration, Governance & Schema Drift.

> **Về tên gọi:** đề tài chủ động dùng "khí hậu"/"dữ liệu khí tượng lịch sử" thay vì "vi khí hậu" (microclimate) — vi khí hậu chỉ quy mô không gian rất nhỏ (mét–km, ví dụ trong một thung lũng/tán rừng), trong khi dữ liệu của nhóm (lưới ERA5 ~28km/ô + trạm điểm) ở quy mô khu vực. Xem lý do chi tiết tại `docs/04-ghi-chu-phan-tich.md`.

## 2. Đội hình dự án

| Vai trò | Họ tên | MSSV | Email | Trọng tâm |
|---|---|---|---|---|
| **TV1 — Ingestion Lead** | Ngô Văn Quang | 20251243M | Quang.NV251243M@sis.hust.edu.vn | Thu thập & làm sạch dữ liệu đa nguồn (Syntactic/Format Heterogeneity) |
| **TV2 — Schema Lead** | Nguyễn Cao Lương | 20251244M | Luong.NC251244M@sis.hust.edu.vn | Lược đồ trung gian & kho dữ liệu (Structural/Semantic Heterogeneity, Entity Resolution) |
| **TV3 — Spark/PINN Lead** *+* **TV4 — Dashboard/PM Lead** (kiêm nhiệm cả 2 vai trò) | Trương Tuấn Nghĩa | 20251196M | Nghia.TT251196M@sis.hust.edu.vn | Tính toán phân tán & mô hình vật lý-học máy (Scalable Processing, PINN) **+** Trực quan hoá, quản trị chất lượng & điều phối dự án |

> **Đã xác nhận:** nhóm 16 thực tế chỉ có **3 thành viên**. Trương Tuấn Nghĩa đảm nhiệm gộp cả TV3 và TV4. Vì đây là khối lượng công việc lớn cho 1 người (Spark/PINN + Dashboard/PM), khuyến nghị:
> - **Ưu tiên phần lõi trước, PINN là điểm cộng có thể bỏ nếu thiếu thời gian** (đã có sẵn "phương án lùi" trong `docs/01-de-xuat-de-tai.md` mục 5.3 — dùng hồi quy MLlib thường thay PINN).
> - Vai trò "điều phối dự án" (PM) của TV4 nên làm **gọn nhẹ** (chỉ cần roadmap + board quản lý việc), dồn thời gian chính cho phần kỹ thuật (Spark + Dashboard).
> - Xem `docs/03-ke-hoach-160-tasks.md` để biết chi tiết task theo từng tuần của vai trò gộp này (TV3+TV4 = 20 tác vụ/tuần thay vì 10/tuần như 2 bạn còn lại).

## 3. Mốc thời gian (bám lịch học IT5427)

| Mốc | Ngày | Trạng thái |
|---|---|---|
| Chốt danh sách nhóm | 26/9 | ✅ Đã qua |
| **Nộp đề xuất đề tài** | **5/10** | ⏳ Sắp tới |
| Báo cáo tiến độ | 20/10 | Chưa tới |
| Test (trên lớp) | 27/10 | Chưa tới |
| **Báo cáo cuối kỳ** | **8/11 (Chủ nhật, cả ngày)** | Chưa tới |

## 4. Cấu trúc repo

```
.
├── README.md                          — file này: tổng quan, đội hình, mốc thời gian
└── docs/
    ├── 01-de-xuat-de-tai.md           — đề xuất đề tài đầy đủ (nộp 5/10): lý do chọn, nguồn dữ liệu lõi,
    │                                     3V–5V, kiến trúc hệ thống, phân công, timeline, công nghệ, rủi ro
    ├── 02-nguon-du-lieu.md            — danh sách mở rộng nguồn dữ liệu khí tượng/khí hậu miễn phí,
    │                                     gợi ý phối hợp theo mục tiêu nghiên cứu (đã kiểm chứng + đính chính, xem 05)
    ├── 03-ke-hoach-160-tasks.md       — kế hoạch chi tiết 160 tác vụ (4 tuần × 4 vai trò × 10 tác vụ),
    │                                     mỗi tác vụ có deadline, yêu cầu cần đạt, tiêu chí kiểm thử (Definition of Done)
    ├── 04-ghi-chu-phan-tich.md        — ghi chú phân tích hai mặt + câu hỏi phản biện chuẩn bị trước
    ├── 05-bao-cao-kiem-tra-nguon-du-lieu.md  — báo cáo kiểm tra THẬT từng nguồn (tải mẫu, validate), phát hiện
    │                                     & sửa lỗi so với tài liệu ban đầu (ERA5-AWS, Himawari, OpenAQ...)
    ├── 06-truong-du-lieu-va-tich-hop.md      — trường dữ liệu thật của từng nguồn, Mediated Schema (GAV),
    │                                     khoảng trùng lặp cần Survivorship, khoảng trống vật lý cần PINN
    ├── 07-bang-va-giai-phap-tich-hop.md      — bảng ánh xạ trường tổng hợp + 7 giải pháp tích hợp có code mẫu
    │                                     (GAV union, PIVOT, PARSE, Survivorship, derive vật lý, spatial+PINN)
    └── 08-danh-sach-tram-quan-trac.md         — danh sách trạm GHCN/ISD thật đã lọc cho toàn Đông Nam Á,
                                          kèm các "bẫy" mã quốc gia (VM/VN, BX/BS) phát hiện được khi lọc
```

Script kiểm tra nguồn dữ liệu thật: `scripts/check_data_sources.py` (chạy `python3 scripts/check_data_sources.py`, kết quả lưu ở `data_samples/`).
Danh sách trạm quan trắc dùng thẳng trong code: `reference/*.csv` (xem `docs/08-danh-sach-tram-quan-trac.md`).

Khi triển khai code (crawler/ingestion, ETL, Spark job, mô hình, dashboard), tạo thêm các thư mục `ingestion/`, `warehouse/`, `model/`, `dashboard/` ở gốc repo theo đúng kiến trúc mô tả trong `docs/01-de-xuat-de-tai.md`.

## 5. Nguồn dữ liệu lõi

| Nguồn | Vai trò | Truy cập |
|---|---|---|
| **Copernicus ERA5** (ECMWF) | Dữ liệu lưới tái phân tích khí quyển toàn cầu, 1940–nay | `cdsapi` (Python), cần tài khoản CDS miễn phí |
| **NOAA ISD/GHCN** (NCEI) | Dữ liệu quan trắc trạm mặt đất, >14.000 trạm toàn cầu | AWS S3 `s3://noaa-ghcn-pds/`, không cần key |
| **NASA POWER** | Bức xạ mặt trời & thông số bề mặt/khí quyển từ vệ tinh | REST API công khai, không cần xác thực |
| **Open-Meteo Historical** | Nguồn đối chiếu chéo, nội suy từ ERA5/DWD/NOAA | REST API, không cần key |

Chi tiết đầy đủ 24 nguồn (bao gồm các nguồn mở rộng để làm giàu Variety/Veracity) xem tại `docs/02-nguon-du-lieu.md`.

## 6. Công nghệ dự kiến

Python (`cdsapi`, `xarray`, `dask`, `pykrige`) · Apache Spark (PySpark: SQL, Structured Streaming, MLlib) · Apache Kafka (replay streaming giả lập) · Parquet (partition Year/Month/Region) · PyTorch + DeepXDE (PINN, tuỳ chọn) · Streamlit/Apache Superset (dashboard) · Docker Compose (hạ tầng).

## 6b. Môi trường phát triển — đã kiểm chứng thật (10/10/2026)

Mỗi thành viên nên tự kiểm tra máy mình theo danh sách dưới (lệnh kiểm tra kèm theo). Đã test thật trên máy TV3+TV4 (macOS, Python 3.12 Anaconda):

**Bắt buộc, cần cài nếu chưa có:**
- Python ≥ 3.10 + pip. `python3 --version`
- `pip install pyspark pandas xarray s3fs zarr gcsfs geopandas rioxarray pykrige boto3`
- **Java 17 hoặc 21** (⚠️ không phải Java 11!) — PySpark 4.x yêu cầu Java 17+, còn Java 11 sẽ báo lỗi `UnsupportedClassVersionError`. Cài bằng `brew install openjdk@17`, sau đó **luôn set `JAVA_HOME` trỏ đúng bản 17/21 trước khi chạy Spark**, vì máy có thể có sẵn Java 11 làm mặc định:
  ```bash
  # macOS + Homebrew — ĐÃ TEST THẬT, dùng lệnh này (không dùng java_home -v 17,
  # lệnh đó có thể âm thầm trả về Java 11 nếu openjdk@17 chưa symlink hệ thống):
  export JAVA_HOME=$(brew --prefix openjdk@17)/libexec/openjdk.jdk/Contents/Home
  # Linux: export JAVA_HOME tới thư mục cài JDK 17/21 (vd update-alternatives --config java)
  ```
  Kiểm tra nhanh: `JAVA_HOME=$(brew --prefix openjdk@17)/libexec/openjdk.jdk/Contents/Home python3 scripts/check_spark_env.py` — đã test thật, in ra "Môi trường Spark sẵn sàng."
- Git ≥ 2.x

**Tuỳ chọn, cài khi tới task tương ứng:**
- `pip install cdsapi` — chỉ cần nếu dùng kênh CDS chính thức (có tài khoản). Không bắt buộc vì nhóm dùng ARCO-ERA5 (Google Cloud, miễn phí, không cần key).
- `pip install planetary-computer` — dự phòng nếu ARCO-ERA5/CDS đều gặp sự cố.
- `pip install kafka-python` + Docker (chạy Kafka broker local) — cho task Replay Streaming (TV3, Tuần 2-3).
- `pip install torch` — cho PINN (TV3, tuỳ chọn nâng cao).
- `pip install streamlit` — cho Dashboard (TV4).
- Docker + Docker Compose — nếu dựng cluster Spark nhiều node thay vì `local[*]`.

**Đã verify end-to-end thật** (không chỉ cài đặt, mà chạy thử): `SparkSession` khởi động → đọc CSV GHCN-Daily thật (44.560 dòng, trạm Nội Bài) → ghi Parquet → đọc lại → số dòng khớp 100%. Script mẫu: xem `scripts/batch_download_week2.py` để biết cách tải dữ liệu thật trước khi thử Spark.

## 7. Cách sử dụng repo này

1. Đọc `docs/01-de-xuat-de-tai.md` trước — đây là tài liệu tổng hợp đầy đủ nhất, dùng làm bản nộp đề xuất đề tài ngày 5/10.
2. Theo dõi tiến độ theo `docs/03-ke-hoach-160-tasks.md` — mỗi thành viên tick tác vụ của mình theo tuần, đối chiếu tiêu chí kiểm thử trước khi đánh dấu hoàn thành.
3. Khi cần mở rộng nguồn dữ liệu hoặc đối chiếu chéo, tra `docs/02-nguon-du-lieu.md`.
4. Trước khi báo cáo tiến độ/bảo vệ, ôn lại `docs/04-ghi-chu-phan-tich.md` để chuẩn bị trả lời phản biện.
