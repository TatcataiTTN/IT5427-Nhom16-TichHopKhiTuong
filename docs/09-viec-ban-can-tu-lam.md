# Việc chỉ bạn (hoặc nhóm) mới làm được — không tự động hoá được

Cập nhật: 10/11/2026 (đã merge PR #2 của Ngô Văn Quang — xem mục 2b). Lọc từ kế hoạch 160 tác vụ
(`03-ke-hoach-160-tasks.md`) — mọi việc tự động hoá được (code, test, tải dữ liệu, viết tài liệu kỹ
thuật, soạn slide/báo cáo) đã làm xong trong repo. Danh sách dưới đây là phần còn lại: cần tài khoản
cá nhân, quyết định của nhóm, hoặc hành động con người (họp, nộp bài, thuyết trình) mà không ai làm
thay được.

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
| `report/final-report.pdf` | Báo cáo cuối kỳ đầy đủ (35 trang sau merge PR #2), có chương "Kết quả thực nghiệm" và "Phát hiện dị thường khí hậu" mới với toàn bộ số liệu thật trên 9,3 triệu bản ghi |
| `slides/final-defense.pdf` | Slide bảo vệ cuối kỳ (31 trang sau merge PR #2), Action Title + số liệu thật |
| `docs/14-ket-qua-ky-thuat-tuan-3-4.md` | Tổng hợp kỹ thuật Tuần 3-4 (nguồn cho báo cáo/slide) |
| `docs/15-qa-bao-ve.md` | 8 câu hỏi phản biện dự kiến + đáp án có số liệu dẫn chứng |
| `docs/16-phat-hien-di-thuong-khi-hau.md` | Mới (từ PR #2): phát hiện dị thường khí hậu — z-score theo khí hậu nền, đợt nóng, SPI, trôi cảm biến |

**Lưu ý**: trang 31/slide và 35/report là số sau khi merge PR #2 (10/11) — KHÔNG phải số bạn đã xem
nếu đã xem bản PDF trước đó. Nếu đã nộp/trình bày bản cũ (30 trang/21 slide) cho giảng viên trước khi
merge, cần tự quyết định có gửi lại bản mới hay không (xem mục 0).

**Đây đều là bản nháp tự động, chưa qua mắt người** — bạn cần tự đọc lại, đặc biệt kiểm tra: số liệu
có khớp với những gì Quang/Lương thực sự làm không (xem mục 3), thời lượng trình bày có hợp lý
không, câu chữ có cần chỉnh cho tự nhiên hơn không.

## 2. ĐÃ XONG — Docker Desktop đã mở lại, Spark Streaming test live thành công

~~Mở Docker Desktop thủ công~~ — bạn đã mở giúp, daemon lên lại được. Đã test ngay sau đó:
Spark Structured Streaming đọc Kafka thật, tính đúng `avg_temp_c` theo cửa sổ trượt 1 phút/30s.
Phát hiện + sửa 2 bug môi trường thật trong lúc chạy live (hostname tự phân giải sai IP, version
connector Kafka không khớp PySpark cài thật) — chi tiết tại `docs/14` mục 9. **Không còn việc gì
cần bạn làm cho mục này.**

## 2b. ĐÃ XONG (10/11) — merge PR #2 của Ngô Văn Quang vào master

Quang mở Issue #1 báo lỗi thật trong `model/pinn_wind_field_v2.py` (trung bình cộng hướng gió theo
độ — sai vì là đại lượng vòng tròn) và PR #2 với khối lượng việc rất lớn, tự làm **độc lập**, không
qua tôi:
- Tải đầy đủ ERA5 5 năm (2020–2024) + mở rộng ISD/Open-Meteo/NASA POWER, build lại warehouse từ
  1.076.473 lên **9.348.470 bản ghi**.
- Sửa 4 bug dữ liệu thật: gió Open-Meteo bị phóng đại 3,6 lần (km/h ghi nhầm thành m/s), ma trận
  tương quan giả (fill NaN=0 trước khi tính), benchmark partition bị đảo chiều do ghi đệm không công
  bằng, biến bức xạ ERA5 dùng sai tầng khí quyển.
- Thêm khung kiểm soát chất lượng ở Ingestion (cờ QC theo nguồn, giới hạn vật lý, phát hiện nhảy giá
  trị, khử trùng bản tin ISD).
- Thêm toàn bộ nhóm tính năng phát hiện dị thường khí hậu: z-score theo khí hậu nền WMO 1991–2020,
  đợt nóng ETCCDI, SPI-1/SPI-3, mưa cực đoan, xu hướng dài hạn Mann-Kendall/Sen, trôi cảm biến, dị
  thường theo luồng Kafka→Spark Streaming — xác nhận được với sự kiện thật (bão Yagi, nắng nóng
  4-5/2024, hạn Mekong 2019–2020).
- Chuyển Docker sang image chính thức `apache/kafka:3.7.0`, `apache/spark:4.2.0` (bitnamilegacy đã bị
  gỡ khỏi Docker Hub) — đã chạy thật cụm 1 master + 2 worker + Kafka với image mới sau merge.

**Tôi đã**: review diff (không chỉ tin mô tả PR), xác nhận lại 4 bug trên bằng mắt là sửa đúng; sửa
tiếp bug #2 còn lại trong Issue #1 (trung bình vector (u,v) đúng, không trung bình cộng độ) ở cả
`master` và nhánh PR; merge PR #2 vào `master` (3 conflict: file PINN đã merge sạch về logic, 2 file
PDF build lại); chạy lại `pytest` (83 test, 76 nhanh pass, 4 PINN slow pass); dựng lại cụm Docker
bằng image `apache/*` mới và chạy lại test Spark Streaming + Kafka thật để xác nhận không chỉ tin lời
Quang. Chi tiết: `docs/14` mục cập nhật 10/11, comment trên Issue #1/PR #2.

**Tôi KHÔNG tự verify được** (cần dữ liệu ERA5 5 năm ~23GB không có trên máy): số RMSE nội suy
108.542 cặp, % cải thiện cache Spark, % giảm skew, và các số liệu dị thường khí hậu cụ thể — các số
này lấy nguyên từ PR của Quang, tin tưởng dựa trên mô tả phương pháp luận (đã review code, hợp lý)
nhưng **chưa tự chạy lại để xác nhận bằng số**. Nếu cần độ tin cậy cao hơn trước khi bảo vệ, nên tự
chạy lại `warehouse/build_warehouse.py --dataset full` (cần tải ~23GB, vài giờ) hoặc hỏi Quang demo
trực tiếp.

## 3. Việc nhóm — vẫn cần xác nhận thật từ Quang & Lương

| # | Việc | Vì sao không tự động hoá được |
|---|---|---|
| 1 | **Thu thập tiến độ thật từ Nguyễn Cao Lương (TV2)** | Phần của Quang (TV1) giờ đã có bằng chứng độc lập rất mạnh (PR #2, xem mục 2b) — không còn là vấn đề. Phần TV2 trong `docs/03`/`docs/14` vẫn đang dựa trên code tôi làm thay, cần hỏi Lương trực tiếp trước khi báo cáo trước hội đồng |
| 2 | **Diễn tập + phân công trình bày trong nhóm** | Hành động phối hợp con người — tôi không thể đại diện cả 3 thành viên |

## 4. Quyết định còn tồn đọng (có thể không còn cấp thiết nếu đã qua hạn)

| # | Quyết định | Tình trạng |
|---|---|---|
| 3 | Tải ERA5 full 5 năm hay giữ subset 3 ngày | **ĐÃ XONG** — Quang tải đủ trong PR #2, đã merge (mục 2b) |
| 4 | Docker `apache/*` hay `bitnamilegacy/*` | **ĐÃ XONG** — chốt `apache/*` (bitnamilegacy bị gỡ khỏi Docker Hub), đã verify thật sau merge |
| 5 | GitHub Projects board hay dùng thẳng bảng trạng thái `docs/03` | Token vẫn thiếu quyền `project` (`gh auth refresh -s project -s read:project`). Bảng trong `docs/03`/`docs/14` đã đủ chi tiết để dùng thay thế, khuyến nghị không cần làm thêm |

---

## Những gì đã tự động hoá đầy đủ (không cần bạn làm gì thêm)

Toàn bộ pipeline kỹ thuật: kiểm chứng + tải dữ liệu đầy đủ 9 nước ĐNA (9,3 triệu bản ghi, 5 năm ERA5),
ETL (`ingestion/`, `warehouse/`), kiểm soát chất lượng theo tầng, Entity Resolution GHCN↔ISD,
cross-validation nội suy, Spark SQL optimization, phát hiện dị thường khí hậu (z-score/ETCCDI/SPI/
trôi cảm biến/streaming), 2 mô hình PINN thật, Dashboard (đã verify qua browser), Data Quality
Report, Spark cluster 3 node + Kafka broker (image `apache/*`) và Structured Streaming windowing
(verify live thật), 83 test tự động (76 nhanh + 7 slow), toàn bộ tài liệu kỹ thuật
(`docs/ingestion.md`, `docs/warehouse.md`, `docs/model.md`, `docs/16`, `docs/17`,
`data_dictionary.md`, `CHANGELOG.md`, `requirements.txt`), báo cáo cuối kỳ (35 trang) và slide bảo vệ
(31 trang). Xem chi tiết tại `docs/03-ke-hoach-160-tasks.md` (cột "Trạng thái") và
`docs/14-ket-qua-ky-thuat-tuan-3-4.md`.
