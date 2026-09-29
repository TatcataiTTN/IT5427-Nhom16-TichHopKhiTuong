# Hệ thống tích hợp và xử lý dữ liệu khí tượng đa nguồn phục vụ mô phỏng và dự báo vi khí hậu khu vực Đông Nam Á

**Học phần:** IT5427 — Tích hợp và xử lý dữ liệu lớn
**Giảng viên:** TS. Vũ Tuyết Trinh — Trường Công nghệ Thông tin và Truyền thông, Đại học Bách khoa Hà Nội
**Nhóm:** 16 · **Hướng thực hiện:** Direction 1 — Xây dựng kiến trúc big data có tích hợp và xử lý dữ liệu, kèm dashboard phân tích
**Trạng thái:** Đang triển khai · Repo tạm để **private** trong quá trình làm đồ án

---

## 1. Tóm tắt đề tài

Xây dựng một hệ thống tích hợp dữ liệu khí tượng lịch sử từ nhiều nguồn mở có bản chất khác nhau — dữ liệu tái phân tích dạng lưới toàn cầu (ERA5), dữ liệu quan trắc trạm mặt đất (NOAA ISD/GHCN), và dữ liệu bức xạ vệ tinh (NASA POWER) — đưa về một lược đồ trung gian (mediated schema) thống nhất, xử lý bằng Apache Spark (batch và streaming giả lập), phục vụ mô phỏng và dự báo vi khí hậu khu vực Đông Nam Á, trực quan hoá kết quả trên dashboard.

Bài toán tích hợp cốt lõi là xử lý dị biệt không-thời gian (**Spatio-Temporal Heterogeneity**) giữa dữ liệu lưới liên tục và dữ liệu điểm rời rạc — đây là dạng dị biệt cấu trúc sâu hơn nhiều so với việc ghép các bảng có cùng định dạng, và là lý do đề tài này bám sát trực tiếp các nội dung lý thuyết cốt lõi của học phần: Schema Alignment, Record Linkage/Entity Resolution, Sources Profiling, Batch vs. Streaming Integration, Governance & Schema Drift.

## 2. Đội hình dự án

| Vai trò | Họ tên | MSSV | Email | Trọng tâm |
|---|---|---|---|---|
| **TV1 — Ingestion Lead** | Ngô Văn Quang | 20251243M | Quang.NV251243M@sis.hust.edu.vn | Thu thập & làm sạch dữ liệu đa nguồn (Syntactic/Format Heterogeneity) |
| **TV2 — Schema Lead** | Nguyễn Cao Lương | 20251244M | Luong.NC251244M@sis.hust.edu.vn | Lược đồ trung gian & kho dữ liệu (Structural/Semantic Heterogeneity, Entity Resolution) |
| **TV3 — Spark/PINN Lead** | *(cần bổ sung)* | | | Tính toán phân tán & mô hình vật lý-học máy (Scalable Processing, PINN) |
| **TV4 — Dashboard/PM Lead** | Trương Tuấn Nghĩa | 20251196M | Nghia.TT251196M@sis.hust.edu.vn | Trực quan hoá, quản trị chất lượng & điều phối dự án |

> **Cần nhóm xác nhận:** danh sách gốc của lớp mới ghi 3/4 thành viên nhóm 16 (thiếu 1 dòng). Bổ sung tên/MSSV/email thành viên thứ 4 vào bảng trên (và vào `docs/03-ke-hoach-160-tasks.md`) trước khi nộp đề cương ngày 5/10. Phân vai trong bảng là đề xuất ban đầu — nhóm có thể hoán đổi TV1–TV4 theo thế mạnh thực tế của từng người, miễn giữ đủ 4 mảng trách nhiệm.

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
    ├── 02-nguon-du-lieu.md            — danh sách mở rộng 24 nguồn dữ liệu khí tượng/khí hậu miễn phí,
    │                                     gợi ý phối hợp theo mục tiêu nghiên cứu
    ├── 03-ke-hoach-160-tasks.md       — kế hoạch chi tiết 160 tác vụ (4 tuần × 4 thành viên × 10 tác vụ),
    │                                     mỗi tác vụ có deadline, yêu cầu cần đạt, tiêu chí kiểm thử (Definition of Done)
    └── 04-ghi-chu-phan-tich.md        — ghi chú phân tích hai mặt + câu hỏi phản biện chuẩn bị trước
```

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

## 7. Cách sử dụng repo này

1. Đọc `docs/01-de-xuat-de-tai.md` trước — đây là tài liệu tổng hợp đầy đủ nhất, dùng làm bản nộp đề xuất đề tài ngày 5/10.
2. Theo dõi tiến độ theo `docs/03-ke-hoach-160-tasks.md` — mỗi thành viên tick tác vụ của mình theo tuần, đối chiếu tiêu chí kiểm thử trước khi đánh dấu hoàn thành.
3. Khi cần mở rộng nguồn dữ liệu hoặc đối chiếu chéo, tra `docs/02-nguon-du-lieu.md`.
4. Trước khi báo cáo tiến độ/bảo vệ, ôn lại `docs/04-ghi-chu-phan-tich.md` để chuẩn bị trả lời phản biện.
