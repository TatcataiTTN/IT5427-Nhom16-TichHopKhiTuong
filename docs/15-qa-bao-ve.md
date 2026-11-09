# Câu hỏi phản biện dự kiến + đáp án (docs/03 Tuần 4: TV1 #8, TV2 #6, TV3 #4, TV4 #6)

Tổng hợp 1 file duy nhất (thay vì 4 file rời của từng vai trò) — mỗi câu đều có số liệu thật dẫn
chứng, không trả lời chung chung.

## Ingestion / Veracity (TV1)

**Q1. Vì sao không dùng Z-score làm phương pháp phát hiện outlier chính, dù đây là chuẩn phổ biến
hơn?**
A: Đã test thật: tiêm 5 outlier cực đoan vào dữ liệu N(25,2), Z-score (threshold=3) chỉ phát hiện
được 1/5 (20%) do "masking effect" — chính outlier cực đoan làm std phình to (2,0 → 72,2), khiến
ngưỡng 3×std quá rộng để bắt được chúng. IQR (dựa trên tứ phân vị, bền vững hơn với outlier) phát
hiện đủ 5/5 (100%). Xem `ingestion/veracity.py`.

**Q2. GHCN-Daily có 100% missing ở `rh_pct`/`wind_speed_ms` — đây có phải lỗi parser không?**
A: Không. GHCN-Daily về bản chất chỉ báo cáo TMAX/TMIN/PRCP (đôi khi TAVG) — không có trường độ
ẩm/gió trong nguồn gốc. Đây là giới hạn cấu trúc của nguồn dữ liệu, đã verify bằng cách đọc trực
tiếp file GHCN gốc, không phải lỗi `ingestion/parsers.py::parse_ghcn()`.

## Schema / Nội suy không gian — "ảo giác chính xác" (TV2)

**Q3. Nội suy Bilinear từ ERA5 có đáng tin cậy để thay thế trạm thật không?**
A: Đã cross-validate thật: so ERA5-nội-suy-vào-tọa-độ-trạm với giá trị trạm thật đo được (104 cặp,
35 trạm) — RMSE nhiệt độ 1,02°C (chấp nhận được), nhưng RMSE mưa 10,98mm (kém — reanalysis luôn yếu
ở biến mưa, đúng với y văn trích trong `docs/12`). **Kết luận: KHÔNG nên dùng ERA5 nội suy thay thế
trạm thật cho biến mưa**, chỉ dùng cho nhiệt độ ở nơi thiếu trạm. Số liệu: `docs/14` mục 2.

**Q4. GHCN và ISD được tích hợp bằng ID trạm chung hay toạ độ?**
A: Không có ID chung — đây là gap đã phát hiện ở Tuần 2. Đã giải quyết bằng Entity Resolution dựa
trên khoảng cách Haversine (ngưỡng 5km, nearest-neighbor 1-1): khớp được 22/26 cặp (84,6%), khoảng
cách trung bình 0,53km, nhiều cặp khớp chính xác tại 0,000km (cùng tọa độ WMO gốc — xác nhận đây
đúng là 1 thực thể vật lý). Xem `warehouse/entity_resolution.py`.

## Partition / Data Skew (TV3)

**Q5. Tại sao không dùng Kriging thay vì Bilinear cho nội suy không gian — Kriging không chính xác
hơn sao?**
A: Quyết định có chủ đích (xem bảng so sánh `docs/11`): Kriging cần ước lượng variogram thực nghiệm
— tốn thời gian tính toán và yêu cầu mật độ trạm đủ dày để variogram ổn định, trong khi nhóm có
quy mô 113 trạm trên vùng rộng (9 nước ĐNA, mật độ thưa). Bilinear đơn giản hơn, đã verify RMSE hợp
lý (1,02°C). Kriging được ghi nhận làm phương án dự phòng nếu cần độ chính xác cao hơn ở vùng địa
hình phức tạp — đã đo RMSE theo tercile độ cao để biết trước mức độ cần cải thiện.

**Q6. Đã thử giảm partition skew — vì sao không áp dụng ngay?**
A: Thử nghiệm thật: thêm `month` vào partition key giảm skew 33,28%→3,04% (giảm 90,9%), nhưng số
partition tăng 11,9 lần (88→1.043) — làm nặng thêm vấn đề "small-file" đã phát hiện ở Tuần 2
(partition hiện tại đã chậm hơn 2,2 lần so với không partition, ở quy mô ~1 triệu dòng). Thêm
partition sẽ khiến vấn đề này NẶNG HƠN, không nhẹ hơn. Quyết định: giữ nguyên, benchmark lại khi dữ
liệu đạt quy mô đủ lớn (ERA5 full 5 năm, ~35GB) để lợi ích partition pruning thật sự vượt overhead.

## PINN / Physics-Informed ML (TV3)

**Q7. PINN có tốt hơn mô hình hồi quy thường không? Nếu không thì PINN có ý nghĩa gì?**
A: Đã so sánh trung thực: trên bài toán trường gió thật (113 trạm ERA5), PINN (λ=0,1) có test
RMSE=1,0826, baseline hồi quy thuần (λ=0) có RMSE=1,0447 — **baseline thắng về MSE thuần** ở quy mô
dữ liệu này. Nguyên nhân: bài toán chỉ có 1 snapshot không-thời-gian (không có chiều thời gian),
ràng buộc continuity (Navier-Stokes rút gọn) cần nhiều điểm lưới dày đặc/chuỗi thời gian mới thể
hiện lợi thế rõ. Giá trị thực của physics loss ở quy mô này là đảm bảo TÍNH HỢP LÝ VẬT LÝ (bảo toàn
khối lượng xấp xỉ), không phải tối ưu RMSE — một trade-off có thật, không phải PINN "thất bại".

**Q8. Kết quả PINN có tái lập được không, hay chỉ đúng 1 lần chạy may mắn?**
A: Đã verify thật trên máy sạch: venv hoàn toàn mới, cài lại từ `requirements.txt` (không dùng môi
trường cũ), chạy lại `model/pinn_wind_field_v2.py` — RMSE giống hệt tới 4 chữ số thập phân so với
lần chạy gốc, nhờ `torch.manual_seed(0)` cố định.

---
*Mỗi câu trả lời dẫn chứng bằng script/file thật, có thể demo lại trực tiếp khi hội đồng yêu cầu.*
