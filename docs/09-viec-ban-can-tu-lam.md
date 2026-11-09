# Việc chỉ bạn (hoặc nhóm) mới làm được — không tự động hoá được

Cập nhật: 09/11/2026. Lọc từ kế hoạch 160 tác vụ (`03-ke-hoach-160-tasks.md`) — mọi việc tự động hoá
được (code, test, tải dữ liệu, viết tài liệu kỹ thuật, soạn slide/báo cáo) đã làm xong trong repo.
Danh sách dưới đây là phần còn lại: cần tài khoản cá nhân, quyết định của nhóm, hoặc hành động con
người (họp, nộp bài, thuyết trình) mà không ai làm thay được.

---

## 0. KHẨN CẤP NHẤT — xác nhận trạng thái nộp bài thật với giảng viên

**Hôm nay đã là 09/11/2026 — nghĩa là đã qua CẢ BA mốc chính thức của học phần**: nộp đề cương
(5/10), báo cáo tiến độ (20/10), và báo cáo cuối kỳ (8/11, qua 1 ngày). Tôi không có cách nào xác
nhận được liệu nhóm đã thực sự nộp bài/trình bày ở 3 mốc này hay chưa — đây là việc **chỉ bạn biết
và chỉ bạn (hoặc nhóm) làm được**.

**Cần làm ngay**: liên hệ TS. Vũ Tuyết Trinh để xác nhận:
1. Đã nộp đề cương (5/10) và báo cáo tiến độ (20/10) chưa — nếu chưa, hỏi rõ có bị trừ điểm/gia hạn không.
2. Báo cáo cuối kỳ (8/11) đã nộp/bảo vệ chưa — nếu chưa và vẫn còn cơ hội, mọi tài liệu kỹ thuật đã
   sẵn sàng (xem mục 1 bên dưới); nếu đã quá hạn hẳn, cần hỏi phương án xử lý (nộp muộn có điểm trừ,
   hay cơ hội khác).

Đây là việc ưu tiên cao nhất — mọi thứ khác trong file này chỉ có ý nghĩa nếu vẫn còn cơ hội nộp/sửa.

## 1. Tài liệu đã chuẩn bị sẵn cho báo cáo cuối kỳ — bạn cần tự xem lại trước khi dùng

| File | Nội dung |
|---|---|
| `report/final-report.pdf` | Báo cáo cuối kỳ đầy đủ (30 trang), có chương "Kết quả thực nghiệm" mới với toàn bộ số liệu thật |
| `slides/final-defense.pdf` | Slide bảo vệ cuối kỳ (21 trang), Action Title + số liệu thật, đã verify từng trang bằng mắt |
| `docs/14-ket-qua-ky-thuat-tuan-3-4.md` | Tổng hợp kỹ thuật Tuần 3-4 (nguồn cho báo cáo/slide) |
| `docs/15-qa-bao-ve.md` | 8 câu hỏi phản biện dự kiến + đáp án có số liệu dẫn chứng |

**Đây đều là bản nháp tự động, chưa qua mắt người** — bạn cần tự đọc lại, đặc biệt kiểm tra: số liệu
có khớp với những gì Quang/Lương thực sự làm không (xem mục 3), thời lượng trình bày có hợp lý
không, câu chữ có cần chỉnh cho tự nhiên hơn không.

## 2. ĐÃ XONG — Docker Desktop đã mở lại, Spark Streaming test live thành công

~~Mở Docker Desktop thủ công~~ — bạn đã mở giúp, daemon lên lại được. Đã test ngay sau đó:
Spark Structured Streaming đọc Kafka thật, tính đúng `avg_temp_c` theo cửa sổ trượt 1 phút/30s.
Phát hiện + sửa 2 bug môi trường thật trong lúc chạy live (hostname tự phân giải sai IP, version
connector Kafka không khớp PySpark cài thật) — chi tiết tại `docs/14` mục 9. **Không còn việc gì
cần bạn làm cho mục này.**

## 3. Việc nhóm — vẫn cần xác nhận thật từ Quang & Lương

| # | Việc | Vì sao không tự động hoá được |
|---|---|---|
| 1 | **Thu thập tiến độ thật từ Ngô Văn Quang (TV1) và Nguyễn Cao Lương (TV2)** | Tôi chỉ hỗ trợ được phần TV3+TV4 (vai trò của bạn). Phần TV1/TV2 trong `docs/03`/`docs/14` được đánh dấu trạng thái dựa trên code tôi tự làm thay, **không phản ánh việc Quang/Lương tự làm riêng phần của họ** — cần hỏi lại 2 bạn trực tiếp trước khi dùng số liệu này báo cáo trước hội đồng |
| 2 | **Diễn tập + phân công trình bày trong nhóm** | Hành động phối hợp con người — tôi không thể đại diện cả 3 thành viên |

## 4. Quyết định còn tồn đọng (có thể không còn cấp thiết nếu đã qua hạn)

| # | Quyết định | Khuyến nghị |
|---|---|---|
| 3 | Tải ERA5 full 5 năm (~35GB, nhiều giờ) hay giữ subset 3 ngày hiện tại | Nếu vẫn còn cơ hội nộp/sửa báo cáo: nên làm nếu có thời gian, cải thiện đáng kể Chương "Kết quả" và cho phép benchmark lại partition ở quy mô thật. Nếu đã nộp xong: không cần nữa |
| 4 | GitHub Projects board hay dùng thẳng bảng trạng thái `docs/03` | Token vẫn thiếu quyền `project` (`gh auth refresh -s project -s read:project`). Bảng trong `docs/03`/`docs/14` đã đủ chi tiết để dùng thay thế, khuyến nghị không cần làm thêm |

---

## Những gì đã tự động hoá đầy đủ (không cần bạn làm gì thêm)

Toàn bộ pipeline kỹ thuật: kiểm chứng + tải dữ liệu 9 nước ĐNA, ETL (`ingestion/`, `warehouse/`),
Entity Resolution GHCN↔ISD, cross-validation nội suy, Spark SQL optimization, 2 mô hình PINN thật,
Dashboard 6 panel (đã verify qua browser), Data Quality Report, Spark cluster 3 node + Kafka broker
và Structured Streaming windowing (verify live thật 09/11), 44 test tự động, toàn bộ tài liệu kỹ thuật (`docs/ingestion.md`,
`docs/warehouse.md`, `docs/model.md`, `data_dictionary.md`, `CHANGELOG.md`, `requirements.txt`),
báo cáo cuối kỳ và slide bảo vệ. Xem chi tiết tại `docs/03-ke-hoach-160-tasks.md` (cột "Trạng thái")
và `docs/14-ket-qua-ky-thuat-tuan-3-4.md`.
