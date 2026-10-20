# Việc chỉ bạn (hoặc nhóm) mới làm được — không tự động hoá được

Cập nhật: 20/10/2026. Đây là danh sách lọc ra từ toàn bộ kế hoạch 160 tác vụ (`03-ke-hoach-160-tasks.md`)
— mọi việc có thể tự động hoá (code, test, tải dữ liệu, viết tài liệu kỹ thuật) đã được làm hoặc đang
được làm trực tiếp trong repo. Danh sách dưới đây là phần còn lại: cần tài khoản cá nhân, quyết định
của nhóm, hoặc hành động con người (họp, nộp bài, thuyết trình) mà không ai làm thay được.

---

## 0. ĐÃ XONG (20/10/2026) — Docker Desktop đã lên, cụm Spark + Kafka đã chạy thật

~~Mở Docker Desktop thủ công~~ — Docker daemon đã chạy. Đã tự verify thật ngay sau đó:
- Pull lại image: tag cũ `bitnami/spark:3.5`/`bitnami/kafka:3.7` đã bị **Bitnami rút khỏi Docker Hub**
  (chính sách mới 2025) — đã đổi `docker-compose.spark.yml`/`docker-compose.kafka.yml` sang
  `bitnamilegacy/spark:4.0.0` / `bitnamilegacy/kafka:4.0.0-debian-12-r10` (ảnh đông băng còn miễn phí).
- Spark cluster: `curl localhost:8080/json/` báo `aliveworkers: 2`, đã `spark-submit` 1 job thật
  (tổng 0..999999) chạy phân tán trên worker, kết quả đúng.
- Kafka: producer publish 70 message JSON thật vào topic `weatherobs.ghcn`, `kafka-console-consumer`
  đọc lại đúng. Phát hiện + sửa 1 bug thật: producer xuất `NaN` (không hợp JSON chuẩn) cho giá trị
  thiếu, đã sửa thành `null`.

**Không còn việc gì cần bạn làm cho mục này.**

## 1. Việc gấp — liên quan mốc đã/sắp tới hạn

| # | Việc | Vì sao không tự động hoá được | Mức ưu tiên |
|---|---|---|---|
| 1 | **Xác nhận đã nộp đề cương đề tài (hạn 5/10) chưa** | Đây là hành động nộp bài trên hệ thống học phần — tôi không có quyền truy cập hệ thống đó. **Lưu ý: hôm nay đã là 10/10, quá hạn 5 ngày** — nếu nhóm chưa nộp, cần liên hệ giảng viên TS. Vũ Tuyết Trinh ngay để biết có bị trừ điểm/gia hạn không. File PDF đã sẵn sàng tại `report/main.pdf`. | 🔴 Khẩn cấp |
| 2 | **Họp nhóm xác nhận lại vai trò, kênh liên lạc** với Ngô Văn Quang (TV1) và Nguyễn Cao Lương (TV2) | Cần sự đồng ý/xác nhận thật của 2 thành viên còn lại — tôi không thể đại diện họ. | 🔴 Khẩn cấp |
| 3 | **Thu thập tiến độ thật từ Quang & Lương** cho phần việc TV1 (Ingestion) và TV2 (Schema) — xem họ đã làm được gì trong 10 tác vụ/tuần của mình | Tôi chỉ hỗ trợ được phần TV3+TV4 (vai trò của bạn, Trương Tuấn Nghĩa). Phần TV1/TV2 trong `docs/03` tôi đánh dấu trạng thái dựa trên **code tôi tự làm thay**, không phản ánh việc Quang/Lương đã tự làm riêng phần của họ chưa — cần hỏi lại 2 bạn trực tiếp. | 🔴 Khẩn cấp |

## 2. Quyết định cần bạn (hoặc cả nhóm) chốt

| # | Quyết định | Lựa chọn | Khuyến nghị |
|---|---|---|---|
| 4 | **Có cần đăng ký tài khoản Copernicus CDS không?** | (a) Không cần — dùng ARCO-ERA5 (đã verify, miễn phí, không đăng ký) làm nguồn chính | (a) — đã đủ dùng, tiết kiệm thời gian. Chỉ đăng ký CDS nếu giảng viên yêu cầu trích dẫn nguồn "chính thức" | Dùng (a) |
| 5 | **Tải ERA5 full 5 năm hay giữ subset nhỏ?** | Full 5 năm × 8 biến × vùng ĐNA ước tính **~35GB**, mất nhiều giờ tải + cần ổ đĩa trống tương ứng | Cần bạn xác nhận: (1) máy có đủ ~40GB trống không, (2) mạng có ổn định để chạy tải nền nhiều giờ không. Tôi có thể chạy nền nếu bạn đồng ý | Chờ xác nhận |
| 6 | **Có làm Kafka Streaming thật không, hay bỏ qua?** | `docs/03` đã khuyến nghị: nếu quá tải, ưu tiên bỏ Kafka/PINN trước, giữ Spark batch + Dashboard | Bạn là người duy nhất biết mình còn bao nhiêu thời gian thực tế — quyết định giữ/bỏ Kafka ảnh hưởng trực tiếp khối lượng Tuần 2-3 | Chờ quyết định |
| 7 | **GitHub Projects board hay dùng thẳng bảng trạng thái trong `docs/03`?** | Thử dùng `gh project` để tự tạo board nhưng **token GitHub hiện thiếu quyền `project`** | Chạy lệnh sau rồi làm theo hướng dẫn trên trình duyệt để cấp quyền: `gh auth refresh -s project -s read:project`. Sau đó báo tôi, tôi sẽ tạo board + import 160 thẻ tự động. Nếu không muốn tốn công, bảng trạng thái có sẵn trong `docs/03-ke-hoach-160-tasks.md` đã đủ dùng thay thế | Bạn chọn |

## 3. Đăng ký tài khoản — chỉ cần nếu mở rộng ngoài 4 nguồn lõi

Không bắt buộc cho lõi đề tài (4 nguồn chính đều không cần đăng ký). Chỉ cần nếu muốn mở rộng:

| # | Tài khoản | Cần cho | Miễn phí? |
|---|---|---|---|
| 8 | NASA Earthdata (`urs.earthdata.nasa.gov`) | GPM IMERG (mưa vệ tinh độ phân giải cao hơn CHIRPS), MERRA-2 | Có |
| 9 | Google Earth Engine (`earthengine.google.com`) | Nếu muốn dùng catalog tiền xử lý sẵn thay vì tự ghép nguồn | Có (non-commercial) |
| 10 | NCAR RDA (`rda.ucar.edu`) | JRA-55 (đối chiếu chéo ERA5 — không bắt buộc) | Có |

## 4. Hành động con người cuối tuần 2 (18-20/10) — không ai làm thay được

| # | Việc | Ngày |
|---|---|---|
| 11 | Diễn tập thuyết trình báo cáo tiến độ trong nhóm | 18/10 |
| 12 | **Trình bày báo cáo tiến độ trước lớp/giảng viên — HÔM NAY** | 20/10 |

**Đã chuẩn bị sẵn cho mục 12**: `slides/progress-report.tex` — bộ slide 21 trang (build sạch bằng
XeLaTeX, `slides/progress-report.pdf`) tổng hợp số liệu thật từ `docs/10` (1.076.473 bản ghi,
ma trận tương quan, 3 kỹ thuật PINN hội tụ, phát hiện partition chậm hơn, Kafka+Spark cluster chạy
thật ngay hôm nay) + tiến độ 52/80 tác vụ Tuần 1-2. **Bạn cần tự xem lại nội dung trước khi trình
bày** — đây là nháp tự động, chưa qua mắt người, có thể cần chỉnh câu chữ/thời lượng cho khớp
giới hạn báo cáo thật của lớp.

---

## Những gì đã được tự động hoá đầy đủ (không cần bạn làm gì thêm)

Để đối chiếu — các việc **đã xong, không cần bạn lặp lại**: toàn bộ kiểm chứng nguồn dữ liệu, tải batch
9 nước ĐNA, pipeline ETL (`ingestion/`, `warehouse/`), dashboard proof-of-concept, 18+ unit test, báo cáo
đề xuất dự án (LaTeX), slide, môi trường Spark/PySpark cục bộ. Xem chi tiết trạng thái từng tác vụ tại
`docs/03-ke-hoach-160-tasks.md` (cột "Trạng thái").
