# Hỏi đáp dự kiến: bảo vệ cuối kỳ IT5427, Nhóm 16

Đi kèm slide `final-defense.pdf` và kịch bản `kich-ban-bao-ve.md`. Gồm 32 câu, chia 5 nhóm:

- [A. Đặc trưng dữ liệu và xử lý](#a-đặc-trưng-dữ-liệu-và-xử-lý-cô-hỏi-nhiều-nhất): cô quan tâm nhất, ai cũng cần nắm
- [B. Tích hợp](#b-tích-hợp-khái-niệm-môn-học): GAV, Entity Resolution, Survivorship
- [C. Big data và Spark](#c-big-data-và-spark)
- [D. Phân tích và mô hình](#d-phân-tích-và-mô-hình)
- [E. Câu hỏi về nhóm](#e-câu-hỏi-về-nhóm)

**Cách trả lời:** một câu kết luận trước, rồi số liệu, rồi mở slide nếu cần. Câu nào nhóm chưa làm thì nói thẳng là
chưa làm, đừng đoán. Số trang là trang trong `final-defense.pdf` (bài chính trang 1–31, Phụ lục trang 32–53).

**Lưu ý:** `docs/15-qa-bao-ve.md` là bản cũ, nhiều số đã lỗi thời (RMSE 1,02 °C trên 104 cặp, skew 33,28 %).
Dùng file này.

---

## A. Đặc trưng dữ liệu và xử lý (cô hỏi nhiều nhất)

**A1. Dữ liệu thiếu xử lý thế nào? Sao không nội suy hay điền trung bình?**

Nhóm giữ NULL, không điền. Lý do: phần lớn chỗ thiếu là do nguồn không đo biến đó (GHCN không đo gió, độ ẩm), điền
vào là bịa số. Chỗ thiếu thật thì chọn nguồn khác qua Survivorship. Khi tổng hợp phải đủ ngưỡng: tháng mưa ≥ 90% số
ngày, năm nhiệt độ ≥ 80%. Nhóm từng thay NULL bằng 0 và ra tương quan giả 0,57. Slide 12.

**A2. Thiếu mưa và mưa bằng 0 khác nhau thế nào, xử lý ra sao?**

GHCN chỉ có số liệu mưa ở 58,7% số ngày; trong số đó 57,1% là 0 mm. Ngày không báo cáo giữ NULL, ngày 0 mm giữ 0.
Mưa không nội suy. SPI và tổng mưa tháng chỉ tính khi tháng đủ 90% số ngày. Chưa làm: dashboard chưa phân biệt
"khô thật" và "thiếu" khi hiển thị.

**A3. Ngưỡng giới hạn vật lý (−10…50 °C, gió 0…75 m/s…) lấy ở đâu? Có loại nhầm dữ liệu cực đoan thật không?**

Ngưỡng đặt rộng, chỉ để bắt giá trị không thể xảy ra, không phải để bắt cực đoan. Kiểm chứng: sau tầng 1 (cờ QC của
NOAA) thì 0 giá trị vi phạm, kể cả trong đợt nắng nóng và bão Yagi. Cực đoan thật được xử lý ở tầng sau bằng đối
chứng, không phải bằng ngưỡng. Slide 13.

**A4. Vì sao gắn cờ chứ không xoá bản ghi lỗi?**

Để truy vết được (provenance) và để bước sau tự quyết. Giá trị lỗi được đặt NULL, lý do ghi vào `qc_flag` (ví dụ
`ISD_QC:SLP=2`, `JUMP:temp_c`), còn bản ghi vẫn giữ các biến khác đúng. Xoá cả dòng sẽ mất luôn các biến không lỗi.

**A5. Vì sao IQR mà không dùng Z-score để phát hiện outlier?**

Z-score bị "masking": chính outlier làm độ lệch chuẩn phình ra. Thử trên dữ liệu mô phỏng N(25,2) với 5 outlier, std
từ 2,0 lên 72,2, Z-score chỉ bắt 1/5, IQR bắt 5/5. Phụ lục trang 40.

**A6. Nhưng phát hiện dị thường lại dùng z-score, có mâu thuẫn không?**

Hai việc khác nhau. IQR dùng cho chất lượng dữ liệu trên chuỗi thô có thể lẫn lỗi. z ở phần dị thường tính so với
khí hậu nền 1991–2020 theo ngày trong năm, trên dữ liệu đã qua QC; mục đích là đo một ngày lệch bao nhiêu so với bình
thường, không phải tìm lỗi.

**A7. IQR gắn cờ mưa tới 15–16%, có quá nhiều không?**

Mưa lệch phải mạnh, phần lớn ngày gần 0, nên ngưỡng Tukey hẹp và ngày mưa lớn bị gắn cờ. Đây chỉ là gắn cờ, không
xoá; nhiều giá trị là mưa lớn có thật. Số liệu: `docs/13` (GHCN 16,18%, ERA5 15,03%).

**A8. Đơn vị: làm sao đảm bảo đổi đúng? Nếu nguồn đổi đơn vị thì sao?**

Đọc đơn vị từ metadata của nguồn (`hourly_units` của Open-Meteo, `fill_value` của NASA POWER, thuộc tính NetCDF của
ERA5) chứ không viết cứng; mỗi phép đổi có test. Nếu nguồn đổi đơn vị mà metadata đổi theo thì parser tự đổi; nếu
metadata không đổi thì test sẽ không bắt được. Đây là phần schema drift nhóm chưa xử lý đầy đủ.

**A9. 22,7% bản ghi ISD trùng lặp nhưng chỉ bỏ 393.155 dòng (11,3%)?**

22,7% là tỷ lệ bản ghi nằm trong nhóm trùng. Mỗi cặp trùng giữ lại 1 dòng nên chỉ bỏ khoảng một nửa. Khi gộp, nhóm
ưu tiên METAR rồi SYNOP và lấy giá trị không rỗng, vì METAR hay thiếu áp suất mực biển còn SYNOP có. ISD từ 3.464.430
còn 3.071.275 dòng.

**A10. Vì sao ISD thiếu áp suất mực biển tới 81,1%?**

Phần lớn bản tin ISD là METAR, chỉ có altimeter setting (QNH), không có áp suất mực biển. QNH lệch áp suất mực biển
theo độ cao trạm (−0,4 hPa trạm thấp, +1,5 hPa trạm cao) nên nhóm không dùng thay. Áp suất trạm thì có tách ra cột
áp suất bề mặt.

**A11. Ranh giới ngày GHCN chưa xử lý thì ảnh hưởng thế nào?**

Ngày GHCN là ngày địa phương, lệch 7–8 giờ so với ngày UTC của ERA5. Ảnh hưởng nhiều nhất là mưa, vì mưa tích luỹ
theo cửa sổ 24 giờ; đây là một phần lý do xung đột mưa cao. Cách sửa: dịch cửa sổ 24 giờ theo múi giờ trạm khi ghép.
Nhóm ghi rõ là hạn chế.

**A12. Trôi cảm biến phát hiện thế nào? Sao chưa hiệu chỉnh?**

Lấy chuỗi chênh lệch trạm − ERA5 theo tháng. Khí hậu thật có ở cả hai nên triệt tiêu, phần còn lại là lỗi điểm đo.
Trôi dần dùng Mann-Kendall và độ dốc Sen, nhảy bậc dùng Pettitt. Gắn cờ 4/80 chuỗi, rõ nhất là áp suất Phnom Penh
nhảy −2,6 hPa từ 11/2022. Tiêm lỗi nhân tạo vào 76 chuỗi ổn định: bắt 100% ca trôi, 95–98% ca nhảy bậc. Hiệu chỉnh
cần hồ sơ lịch sử trạm để biết nguyên nhân, nhóm chưa có. Phụ lục trang 46.

**A13. Gió 2 m quy về 10 m thế nào?**

Nhóm tải trực tiếp biến `WS10M` của NASA POWER. Với file cũ chỉ có `WS2M`, dùng hồ sơ gió logarit với độ nhám 0,1 m,
hệ số 0,651, khớp tỷ số 0,650 do chính NASA tính.

## B. Tích hợp (khái niệm môn học)

**B1. Vì sao chọn GAV mà không phải LAV?**

Có đúng 5 nguồn cố định, mỗi nguồn ánh xạ vào `WeatherObs` bằng một view. GAV trả lời truy vấn chỉ cần khai triển
view. Đổi lại, thêm nguồn mới phải sửa định nghĩa view; với 5 nguồn cố định thì chấp nhận được. LAV dễ thêm nguồn
nhưng phải viết lại truy vấn và chỉ trả được certain answers.

**B2. Vì sao chọn data warehouse mà không tích hợp ảo (virtual)?**

Nguồn chậm và không ổn định: hàng đợi CDS có lúc chờ hơn 1 giờ, ERA5 thô 22 GB. Phân tích dị thường quét 977 nghìn
ngày-trạm và lặp nhiều lần. Dữ liệu lịch sử, không cần cập nhật tức thời. Nên vật chất hoá vào kho rồi tính là hợp lý.

**B3. Entity Resolution chỉ dựa trên khoảng cách có đủ không? Precision/recall 100% trên 15 cặp có đáng tin?**

Với trạm khí tượng, toạ độ là thuộc tính mạnh nhất: nhiều cặp trùng đúng 0 km. Nhưng 15 cặp có nhãn là mẫu nhỏ; 7/22
cặp tìm được không có mã WMO để kiểm chứng độc lập. 4 trạm không khớp đều không trùng mã WMO với trạm GHCN nào, một
trạm có 5 chữ số đầu trùng nhưng cách 100,9 km. Nhóm nói rõ đây là giới hạn.

**B4. Sao không dùng blocking?**

Chỉ 26 × 41 = 1.066 cặp, so hết còn nhanh. Blocking (ví dụ LSH) cần khi lên toàn cầu: GHCN hơn 14.000 trạm thì số
cặp lên hàng trăm triệu. Phụ lục trang 53.

**B5. Hạng nguồn trong Survivorship dựa vào đâu? Ngưỡng xung đột chọn thế nào?**

Trạm đo trực tiếp và có cờ QC nên hạng 1; ERA5 có đồng hoá số liệu quan trắc; Open-Meteo nội suy lại từ ERA5;
NASA POWER lưới thô nhất 0,5°. Ngưỡng đặt trước theo biên độ tự nhiên của từng biến: áp suất 2%, nhiệt độ 10%, mưa
50%.

**B6. Mưa xung đột 91,6% thì giá trị mưa trong kho có dùng được không?**

Xung đột cao chủ yếu vì mỗi nguồn tích luỹ mưa theo cửa sổ khác nhau (GHCN 24 giờ kết thúc buổi sáng giờ địa phương,
ERA5 tổng theo giờ UTC), cộng với lệch ranh giới ngày GHCN. Giá trị lấy theo hạng nguồn và có cờ xung đột để người
dùng biết. Các phân tích mưa trên slide tính theo từng nguồn: SPI trên trạm GHCN, mưa cực đoan Yagi theo từng cặp
trạm–nguồn.

**B7. Open-Meteo không độc lập với ERA5, vậy tích hợp vào làm gì?**

Nó có độ ẩm và áp suất mực biển theo giờ ở các điểm đại diện, dùng được khi nguồn khác thiếu (hạng 3). Nhưng nhóm
không tính Open-Meteo là một xác nhận độc lập khi đối chứng dị thường. Phụ lục trang 34.

**B8. Provenance: nhìn một giá trị trong kho có biết nó từ đâu không?**

Có. Mỗi bản ghi có cột `source`; bảng hợp giải có cột nguồn được chọn và cờ xung đột cho từng biến; `qc_flag` ghi lý
do giá trị bị đặt NULL; `temp_def` ghi cách tính nhiệt độ ngày.

## C. Big data và Spark

**C1. Kho chỉ 303 MB, vừa RAM một máy, sao gọi là dữ liệu lớn và cần Spark?**

Đúng, kho sau tích hợp nhỏ. Volume nằm ở bước nạp: ERA5 thô 22 GB, nếu lấy qua kênh ARCO phải tải khoảng 1 TB. Nhóm
đo thẳng: ở quy mô này DuckDB nhanh hơn Spark 7,3–8,4 lần. Spark dùng để có pipeline mở rộng được cho toàn bộ lưới
ERA5, không phải vì kho hiện tại vượt RAM.

**C2. Velocity: dữ liệu lịch sử thì streaming có ý nghĩa gì?**

Nhóm nói rõ là mô phỏng: phát lại dữ liệu theo thứ tự thời gian qua Kafka. Giá trị là chứng minh pipeline streaming
cho kết quả đúng bằng batch, 179/179 cảnh báo khớp. Về nguyên tắc, nối nguồn thời gian thực thì chỉ cần thay
producer; nhóm chưa thử.

**C3. 69,4% đo thế nào? Có công bằng không?**

Cùng một truy vấn, trung bình 3 lần chạy, so với và không có `cache()`. Hạn chế: AQE của Spark 4 để mặc định, có tự
gộp shuffle partition, nhóm chưa tách riêng ảnh hưởng này. Phụ lục trang 52.

**C4. Kafka 1 broker, 1 partition thì có gì sai không?**

Chạy đúng nhưng không chịu lỗi, và Spark chỉ đọc bằng 1 task dù có 2 worker. Lên nhiều máy cần RF ≥ 3 và nhiều
partition. Phụ lục trang 52.

**C5. Partition chậm hơn không partition sao vẫn giữ?**

Ở 9 triệu bản ghi trên ổ cục bộ, Parquet đã bỏ qua dữ liệu nhờ thống kê min/max của row-group, nên partition không
giúp được thêm. Partition pruning có lợi khi dữ liệu lớn hơn nhiều hoặc nằm trên S3/GCS, nơi mỗi lần đọc file tốn
kém. Phụ lục trang 42.

## D. Phân tích và mô hình

**D1. Khí hậu nền chỉ từ GHCN 1991–2020, các nguồn ngắn hơn (ERA5 5 năm) thì sao?**

Tỷ lệ ngày z ≥ 2 trên slide tính trên 34 trạm GHCN với nền 1991–2020. ERA5 và ISD chỉ có 5–10 năm, ngắn hơn chuẩn
30 năm của WMO; nhóm ghi đây là giới hạn (Phụ lục trang 52), cùng với 15.938 ca chưa có đối chứng.

**D2. Ngưỡng |z| ≥ 2 có phải tuỳ tiện không?**

z ≥ 2 nghĩa là lệch hơn 2 độ lệch chuẩn so với bình thường, cỡ 2–3% số ngày nếu phân bố gần chuẩn. Nền 1991–2020 đo
được 1,2% số ngày, năm 2024 lên 11,2%. Đợt nóng dùng chỉ số TG90p theo chuẩn ETCCDI.

**D3. PINN không tốt hơn baseline thì đưa vào làm gì?**

Báo cáo đúng kết quả. Chênh lệch khoảng 1% trên 22 trạm, một seed, chưa đủ kết luận. Physics loss giảm mạnh khi tăng
λ (0,53 xuống 0,011), tức trường gió dự đoán thoả ràng buộc vật lý hơn. Kết quả tái lập tới 4 chữ số thập phân nhờ
cố định seed.

**D4. Bilinear sao không dùng Kriging?**

Kriging cần ước lượng variogram, đòi hỏi trạm đủ dày; 113 trạm trên 9 nước là thưa. Bilinear đã kiểm chứng RMSE
nhiệt độ 1,14 °C trên 108.542 cặp. Nơi lệch nhiều nhất là trạm cao (1,42 °C), cần hiệu chỉnh độ cao hơn là đổi phương
pháp nội suy.

## E. Câu hỏi về nhóm

**E1. Mỗi người làm phần nào?**

Quang: thu thập 5 nguồn, QC, sửa lỗi pipeline. Lương: Mediated Schema, Entity Resolution, Survivorship. Nghĩa: môi
trường Spark/Docker, Kafka, streaming, PINN, tối ưu, dashboard. Phụ lục trang 50–51.

**E2. Có demo được không?**

Theo thông báo 15/11 thì không demo trực tiếp. Cụm Docker và `pytest` chạy được ngay nếu cô yêu cầu.
