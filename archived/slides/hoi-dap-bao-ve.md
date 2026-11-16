# Hỏi đáp dự kiến: bảo vệ cuối kỳ IT5427, Nhóm 16

Đi kèm slide `final-defense.pdf` và kịch bản `kich-ban-bao-ve.md`. Gồm 93 câu, chia 8 nhóm:

- [A. Đặc trưng dữ liệu và xử lý](#a-đặc-trưng-dữ-liệu-và-xử-lý-cô-hỏi-nhiều-nhất): cô quan tâm nhất, ai cũng cần nắm
- [B. Tích hợp](#b-tích-hợp-khái-niệm-môn-học): GAV, Entity Resolution, Survivorship
- [C. Big data và Spark](#c-big-data-và-spark)
- [D. Phân tích và mô hình](#d-phân-tích-và-mô-hình)
- [E. Câu hỏi về nhóm](#e-câu-hỏi-về-nhóm)
- [F. Phụ lục, trang 35–66](#f-phụ-lục-trang-3465-ai-hiểu-chínhphụ-xem-bảng-đầu-kich-ban-bao-vemd): 25 câu riêng cho các trang chỉ mở khi bị hỏi
- [G. Kiểm chứng tích hợp — đúng kiểu câu cô hay hỏi](#g-kiểm-chứng-tích-hợp--đúng-kiểu-câu-cô-hay-hỏi): 28 câu, soạn
  từ ghi chép thật buổi bảo vệ Nhóm 15 (cô hỏi rất sâu về nguồn dữ liệu, ghép theo khoá hay theo thứ tự, luật ưu
  tiên, log đối chiếu) — áp đúng kiểu câu đó vào dữ liệu của nhóm mình
- [H. Cửa sổ 2020–2024, Fellegi–Sunter và liên kết trạm–lưới](#h-cửa-sổ-20202024-fellegisunter-và-liên-kết-trạmlưới): 8 câu
  cùng kiểu G cho các phần mới thêm (Phụ lục trang 61–66)

**Cách trả lời:** một câu kết luận trước, rồi số liệu, rồi mở slide nếu cần. Câu nào nhóm chưa làm thì nói thẳng là
chưa làm, đừng đoán. Số trang là trang trong `final-defense.pdf` (bài chính trang 1–34, Phụ lục trang 35–66).

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
từ 2,0 lên 72,2, Z-score chỉ bắt 1/5, IQR bắt 5/5. Phụ lục trang 43.

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
cần hồ sơ lịch sử trạm để biết nguyên nhân, nhóm chưa có. Phụ lục trang 49.

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
cặp lên hàng trăm triệu. Phụ lục trang 56.

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
không tính Open-Meteo là một xác nhận độc lập khi đối chứng dị thường. Phụ lục trang 37.

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
gộp shuffle partition, nhóm chưa tách riêng ảnh hưởng này. Phụ lục trang 55.

**C4. Kafka 1 broker, 1 partition thì có gì sai không?**

Chạy đúng nhưng không chịu lỗi, và Spark chỉ đọc bằng 1 task dù có 2 worker. Lên nhiều máy cần RF ≥ 3 và nhiều
partition. Phụ lục trang 55.

**C5. Partition chậm hơn không partition sao vẫn giữ?**

Ở 9 triệu bản ghi trên ổ cục bộ, Parquet đã bỏ qua dữ liệu nhờ thống kê min/max của row-group, nên partition không
giúp được thêm. Partition pruning có lợi khi dữ liệu lớn hơn nhiều hoặc nằm trên S3/GCS, nơi mỗi lần đọc file tốn
kém. Phụ lục trang 45.

## D. Phân tích và mô hình

**D1. Khí hậu nền chỉ từ GHCN 1991–2020, các nguồn ngắn hơn (ERA5 5 năm) thì sao?**

Tỷ lệ ngày z ≥ 2 trên slide tính trên 34 trạm GHCN với nền 1991–2020. ERA5 và ISD chỉ có 5–10 năm, ngắn hơn chuẩn
30 năm của WMO; nhóm ghi đây là giới hạn (Phụ lục trang 55). Kết quả chỉ báo cho 2020–2024, khi luôn có ERA5 để
đối chứng: 0 ca thiếu đối chứng trong cửa sổ này.

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
trường Spark/Docker, Kafka, streaming, PINN, tối ưu, dashboard. Phụ lục trang 53–54.

**E2. Có demo được không?**

Theo thông báo 15/11 thì không demo trực tiếp. Cụm Docker và `pytest` chạy được ngay nếu cô yêu cầu.

## F. Phụ lục, trang 35–66 (ai hiểu chính/phụ: xem bảng đầu `kich-ban-bao-ve.md`)

**F1. Bảng 6 mức dị biệt ở slide 36 lấy từ đâu, áp dụng đúng vào 5 nguồn ra sao?**

Lấy từ 6 mức xung đột dữ liệu trong bài giảng Buổi 2: hệ thống, cú pháp, lược đồ, ngữ nghĩa, định danh, chất
lượng. Mỗi mức có ví dụ thật: hệ thống là 3 kiểu giao thức khác nhau (REST API, CSV trên S3, CDS API/Zarr); lược
đồ là GHCN dạng long còn 4 nguồn kia dạng wide; định danh là GHCN/ISD gán 2 mã khác nhau cho cùng một trạm, xử
lý bằng Entity Resolution ở phần 4.

**F2. Trong 5 nguồn, nguồn nào không độc lập với nguồn khác? Ảnh hưởng gì tới kết luận dị thường?**

Open-Meteo là lớp trung gian, nội suy lại từ ERA5/ICON/GFS nên không độc lập với ERA5. Khi đối chứng dị thường
khí hậu, nhóm chỉ dùng ERA5 và trạm lân cận làm hai nguồn đối chứng độc lập, không tính Open-Meteo là xác nhận
thứ ba. Phụ lục trang 37.

**F3. 119 vị trí gồm những gì, vì sao phân bố không đều giữa 9 nước?**

113 trạm quan trắc thật (GHCN, ISD) cộng 6 điểm lưới (NASA POWER, Open-Meteo). Không đều vì nhóm chỉ lấy vị trí
có đủ nguồn lõi kiểm chứng được; Singapore và Timor-Leste nằm trong bbox nhưng không có trạm nào nhóm chọn được.
Phụ lục trang 38.

**F4. Vì sao từ 23 GB dữ liệu thô chỉ còn 303 MB Parquet sau tích hợp? Có mất thông tin không?**

Phần lớn 23 GB là ERA5 dạng lưới NetCDF cho toàn vùng; sau khi nội suy Bilinear về đúng 113 toạ độ trạm thì chỉ
giữ giá trị tại các điểm cần dùng, không giữ cả lưới. Parquet nén theo cột cũng nhỏ hơn CSV/NetCDF thô nhiều lần.
Không mất thông tin cần cho bài toán, vì chỉ cần giá trị tại vị trí trạm.

**F5. Cho một ví dụ cụ thể dữ liệu thô bị lỗi trước khi chuẩn hoá?**

Bản tin ISD trạm 48097099999 ngày 1/1/2024 ghi `SLP="99999,9"`, là mã "không đo" của NOAA; đọc thẳng sẽ thành áp
suất 9.999,9 hPa, một giá trị không thể có trong thực tế. Sau chuẩn hoá, cột `pressure_msl_hpa` được đặt NULL.
Phụ lục trang 40.

**F6. Vì sao không dùng kênh ARCO để tải ERA5 nhanh hơn?**

Kênh ARCO chia theo chunk 1 giờ cho toàn cầu, nên lấy vùng Đông Nam Á 22 GB vẫn phải tải khoảng 1 TB dữ liệu
toàn cầu trước, mất khoảng 27,8 giờ ở 10 MB/s. Nhóm chọn tải qua CDS API, cắt vùng ngay phía máy chủ, dù phải
xếp hàng đợi (có lúc hơn 1 giờ) nên chạy song song 2 tài khoản để bù. Phụ lục trang 41.

**F7. QC chỉ can thiệp 0,09% số bản ghi thì có đáng tin không, có bỏ sót lỗi không?**

0,09% là can thiệp ở tầng 1–2 (cờ QC gốc và giới hạn vật lý), chạy ngay khi nạp. Lỗi tinh vi hơn — bước nhảy bất
thường, lệch so với ERA5, trôi cảm biến dài hạn — được bắt ở tầng 4–7 sau khi đã tích hợp, không nằm trong
0,09% này. Phụ lục trang 42.

**F8. Lỗi tương quan giả gió–độ ẩm 0,57 đã sửa thế nào, số đúng là bao nhiêu?**

Lỗi gốc là thay NaN bằng 0 trước khi tính tương quan, trong khi mỗi nguồn thiếu biến khác nhau nên tạo tương
quan giả. Sửa bằng cách tính theo từng cặp bản ghi đều có giá trị (pairwise, không impute); kết quả đúng là
nhiệt độ–độ ẩm −0,59, nhiệt độ–áp suất −0,61. Phụ lục trang 44 và 50.

**F9. Partition pruning là gì, vì sao Parquet hiện tại vẫn nhanh dù không partition theo tháng?**

Mỗi row-group trong Parquet lưu sẵn thống kê min/max từng cột; khi truy vấn có điều kiện lọc, Spark đọc thống kê
này trước và bỏ qua row-group không khớp mà không cần đọc dữ liệu thật. Ở quy mô 9 triệu dòng, cơ chế này đã đủ
hiệu quả nên partition thêm theo tháng (tăng 12 lần số partition) không giúp thêm, còn chậm hơn vì small-file.
Phụ lục trang 45.

**F10. Cụm Spark và Kafka có thật sự phân tán không hay chỉ giả lập trên một máy?**

Giả lập trên một máy vật lý, chạy 3 container Docker: 1 master, 2 worker, 1 broker Kafka. Mục đích là kiểm chứng
đúng luồng pipeline chạy đúng logic phân tán, không phải đo hiệu năng phân tán thật — hạn chế này nhóm ghi rõ ở
slide "Giới hạn hạ tầng". Phụ lục trang 46 và 55.

**F11. Vì sao dùng chỉ số ETCCDI (p95/p99, Rx1day, R95p) thay vì một ngưỡng mưa cố định?**

Mưa không phân bố chuẩn nên một ngưỡng mm cố định sẽ không công bằng giữa các trạm có khí hậu nền khác nhau.
Chuẩn ETCCDI tính phân vị trên chính chuỗi dữ liệu của từng trạm (chỉ tính ngày ướt ≥ 1 mm), nên "cực đoan" được
định nghĩa tương đối với khí hậu nền của đúng trạm đó. Phụ lục trang 47.

**F12. Trạm GHCN Phù Liễn mất số liệu đúng lúc bão rồi báo 214 mm ngày 11/9, số này có đáng tin không?**

Đây là hạn chế nhóm ghi nhận, chưa khẳng định chắc chắn: nhiều khả năng là mưa dồn, trạm đo thủ công cộng dồn
các ngày mất số liệu vào lần đo tiếp theo, không phải mưa thật của riêng ngày 11/9. Nhóm không điền số liệu bù
cho 2 ngày mất, chỉ ghi nhận hiện tượng. Phụ lục trang 47.

**F13. Vì sao dùng Mann-Kendall và độ dốc Sen cho xu hướng nhiệt độ thay vì hồi quy tuyến tính?**

Hồi quy tuyến tính giả định phần dư phân bố chuẩn và nhạy với outlier. Mann-Kendall là kiểm định phi tham số cho
ý nghĩa thống kê của xu hướng, không cần giả định phân bố; độ dốc Sen ước lượng tốc độ bằng trung vị độ dốc giữa
các cặp điểm nên bền với outlier hơn. Phụ lục trang 48 và 49.

**F14. Xu hướng ấm lên dài hạn có mâu thuẫn với phần dị thường khí hậu (đo so với nền 1991–2020) không?**

Không mâu thuẫn. Dị thường (z-score) đo độ lệch so với khí hậu nền cố định 1991–2020 theo từng ngày trong năm,
dùng để phát hiện sự kiện bất thường tại một thời điểm. Xu hướng dài hạn đo chính khí hậu nền đó có đang dịch
chuyển theo thời gian không. Slide 48 nói rõ: trừ xu hướng nền đi thì năm 2024 vẫn nổi bật.

**F15. Sao biết trôi cảm biến không phải là biến đổi khí hậu thật?**

Lấy chênh lệch trạm trừ ERA5 cùng vị trí theo tháng: biến động khí hậu thật xảy ra ở cả hai chuỗi như nhau nên
bị triệt tiêu trong phép trừ; phần còn lại chỉ có thể là lỗi riêng của cảm biến hoặc điểm đo. Phụ lục trang 49.

**F16. PCA chỉ giải thích 48–56% phương sai, kết quả có dùng được không?**

Đây là phân tích khám phá để kiểm tra PCA có tự gom đúng các biến liên quan về mặt vật lý không, không dùng để
giảm chiều phục vụ mô hình chính. PC2 của Open-Meteo tự gom độ ẩm, mưa và áp thấp, đúng kiểu hình bão, mà không
cần gán nhãn trước — đủ để minh hoạ cấu trúc dữ liệu. Phụ lục trang 50.

**F17. Vì sao chọn Streamlit cho dashboard mà không phải công cụ BI khác như Superset?**

Mục 3.5 báo cáo ghi rõ nhóm cân nhắc Apache Superset nhưng không dùng: Streamlit viết bằng Python thuần, tích
hợp trực tiếp với pandas/Parquet đã có sẵn trong pipeline, không cần dựng thêm server/database riêng, phù hợp
quy mô đồ án một học kỳ.

**F18. Ảnh dashboard ở slide 52 chụp trên bản rút gọn 1,08 triệu dòng, kết luận trình bày trong bài có đáng tin không?**

Có. Ảnh chụp chỉ để minh hoạ giao diện chạy được, dùng bản rút gọn cho nhẹ khi chụp. Mọi con số và kết luận phân
tích trong bài đều tính trên kho đầy đủ 8,96 triệu dòng, nêu ở Mục 6.1 báo cáo. Phụ lục trang 51–52.

**F19. Khối lượng công việc chia không đều, Nghĩa có vẻ phụ trách nhiều phần nhất, có hợp lý không?**

Theo bảng "Sản phẩm của từng người theo mốc" (slide 54): Quang phụ trách ingestion và QC 4 tầng, Lương phụ
trách Schema, Entity Resolution và Survivorship, Nghĩa phụ trách hạ tầng Spark/Docker/Kafka, streaming, PINN,
tối ưu và dashboard — phần có nhiều cấu phần kỹ thuật nhất nên khối lượng việc lớn hơn, không phải chia ngẫu
nhiên.

**F20. Giới hạn hạ tầng nào ở slide 55 nghiêm trọng nhất, nếu có thêm thời gian sẽ ưu tiên sửa gì?**

Nghiêm trọng nhất là Kafka chỉ 1 broker/1 partition, vì nó giới hạn luôn khả năng Spark đọc song song (chỉ 1
task dù có nhiều worker) — nút thắt này lan sang cả phần streaming. Nếu có thêm thời gian, nhóm ưu tiên tăng
partition Kafka và đo lại ảnh hưởng của AQE tới số đo cache() 69,4%, vì đây là hai điểm đo chưa tách bạch được.

**F21. Mở rộng ra toàn cầu, chi phí lớn nhất nằm ở thành phần nào?**

Lưu trữ và Entity Resolution tốn kém nhất: ERA5 toàn cầu lên tới hàng trăm TB cần HDFS/S3/MinIO thay vì một ổ
cục bộ, và GHCN có hơn 14.000 trạm nên số cặp so khớp không còn 1.066 mà lên hàng trăm triệu, bắt buộc dùng
Blocking/LSH thay vì so toàn bộ cặp như hiện tại. Phụ lục trang 56.

**F22. Tất cả số liệu trên các slide phụ lục có kiểm chứng lại được, hay chỉ tính một lần rồi ghi cố định?**

Toàn bộ số liệu tính trực tiếp từ kho Parquet bằng script trong repo (ví dụ `survivorship_conflict_by_source.py`,
`data_quality_report.py`), không gõ tay. Nhóm đối chiếu chéo nhiều lần trong kỳ, ví dụ bảng hợp giải Survivorship
856.452 dòng khớp đúng giữa slide, báo cáo và lần chạy lại gần nhất.

**F23. 23/26 trạm có mã WMO nhưng chỉ 15 cặp ghép đúng, 11 trạm còn lại vì sao chưa có nhãn?**

Trong 23 trạm có định dạng mã WMO, 15 cặp ghép đúng 1-1 với GHCN để làm nhãn kiểm chứng độc lập. 11 trạm còn
lại: 3 trạm không đúng định dạng mã và 8 trạm không tìm được cặp khớp tương ứng phía GHCN, nên chưa dùng làm
nhãn được — nhóm ghi đây là hướng mở rộng, không che giấu. Phụ lục trang 55.

**F24. Nếu chỉ được hỏi đúng một slide phụ lục để đánh giá cả nhóm, nên hỏi slide nào?**

Slide 44 "Lỗi số liệu trong pipeline" phù hợp nhất, vì buộc trả lời được cả bốn khía cạnh: phát hiện lỗi thế
nào, nguyên nhân kỹ thuật, hệ quả nếu không sửa, và cách sửa kèm bằng chứng — đúng tinh thần "chỉ rõ tiến trình
thực hiện và kết quả đánh giá thực nghiệm" mà cô yêu cầu trong thông báo 15/11.

**F25. Khái niệm "6 mức dị biệt dữ liệu" ở slide 36 học từ buổi nào, áp dụng nguyên văn hay có điều chỉnh?**

Từ bài giảng Buổi 2 (Mediation & Query reformulation / Schema Alignment). Nhóm áp dụng đúng 6 mức nhưng thay ví
dụ lý thuyết bằng ví dụ thật đo được trên chính 5 nguồn của đồ án, không chỉ liệt kê định nghĩa suông.

## G. Kiểm chứng tích hợp — đúng kiểu câu cô hay hỏi

Soạn từ ghi chép thật buổi bảo vệ Nhóm 15 (tích hợp thời tiết + chất lượng không khí): cô hỏi rất sâu và liên
tục về một chủ đề duy nhất — ghép dữ liệu giữa các nguồn có dựa vào giả định không, hay có bằng chứng (khoá, log
đối chiếu) chứng minh khớp. Nhóm 15 bị hỏi dồn vì ghép theo thứ tự mảng toạ độ, chưa kiểm chứng thứ tự trả về.
28 câu dưới đây áp đúng kiểu hỏi đó vào dữ liệu thật của nhóm mình — hầu hết đều có bằng chứng sẵn vì nhóm ghép
theo khoá (`location_id`, `timestamp_utc`) ngay từ đầu, không theo vị trí mảng.

**G1. Dữ liệu 5 nguồn có đều đặn theo khung thời gian cố định không, hay lúc có lúc không?**

Không đều, và nhóm không giả định chúng đều nhau: GHCN theo ngày (1943–2026), ISD theo giờ/METAR-SYNOP
(2015–2024), ERA5 theo giờ (2020–2024), NASA POWER và Open-Meteo theo giờ hoặc ngày (2020–2024). Mỗi nguồn ghi
rõ độ phân giải và độ dài riêng trong bảng nguồn dữ liệu, không trộn lẫn.

**G2. Sau khi gộp theo luật ưu tiên, có còn đúng 1 nguồn thời tiết thống nhất không?**

Không phải "1 nguồn duy nhất cho tất cả", mà là 1 giá trị được chọn minh bạch cho từng biến, từng vị trí, từng
ngày, ghi rõ trong bảng hợp giải (856.452 dòng) nguồn nào được chọn. Vì các nguồn phủ không gian/thời gian khác
nhau, ép về một nguồn duy nhất sẽ mất dữ liệu ở nơi nguồn đó không phủ tới.

**G3. Quy tắc ưu tiên khi trùng thời điểm là gì, nhóm có xác nhận lại rõ ràng không?**

Rõ ràng và cố định trong code (`SOURCE_PRIORITY`): ISD/GHCN (đo thật) > ERA5 > Open-Meteo > NASA POWER. Không
phải quy tắc ngầm hiểu, mà là một dict khai báo đầu file `warehouse/survivorship.py`.

**G4. Nguồn khác bản chất (ví dụ một chỉ số phi khí tượng) có nên đi chung luồng ưu tiên với các nguồn khí tượng không?**

Không nên, và nhóm không gặp tình huống này vì cả 5 nguồn đều là khí tượng cùng bản chất vật lý. Nếu có nguồn
khác bản chất, sẽ phải tách luồng ưu tiên riêng chứ không gộp chung bảng hạng.

**G5. Mỗi vị trí lấy dữ liệu ở điểm nào? Các nguồn có cùng vị trí không, hay lưới khác nhau gây sai lệch?**

Quy về chung một tập toạ độ thật: trạm GHCN/ISD dùng toạ độ vật lý của trạm; ERA5 (lưới 0,25°) được nội suy
Bilinear về đúng toạ độ đó trước khi so sánh, không so trực tiếp hai lưới khác nhau; NASA POWER/Open-Meteo gọi
API đúng toạ độ trạm. Tất cả quy về 119 vị trí trong bảng Location.

**G6. Nhóm ghép dữ liệu giữa các nguồn theo thứ tự trả về của API hay theo khoá?**

Theo khoá `location_id` + `timestamp_utc`, không theo vị trí trong mảng trả về. Mọi phép merge trong
`build_warehouse.py` và `survivorship.py` dùng khoá này, nên API trả thiếu hay đổi thứ tự cũng không gây ghép
nhầm vị trí.

**G7. Nếu một nguồn trả lệch thứ tự so với yêu cầu thì có ghép nhầm vị trí không?**

Không, vì khoá ghép không dựa vào vị trí mảng. Nhóm đã gặp thật tình huống thiếu biến theo nguồn (ISD không có
mưa, GHCN không có gió) — dòng vẫn giữ đúng khoá, chỉ biến thiếu là NULL, không lệch dòng.

**G8. Cùng một mốc thời gian, giá trị ở các nguồn có khớp đúng vị trí/đúng trạm không? Có bằng chứng không?**

Có log thật: `warehouse/survivorship_conflict_by_source.py` in ra tỷ lệ xung đột giữa các nguồn theo từng biến
khi cùng vị trí, cùng ngày (ví dụ nhiệt độ lệch 3,2%, mưa lệch 91,6%). Đây là bảng đối chiếu chứng minh khớp
theo khoá, không phải giả định.

**G9. Vì sao không ghép đơn giản theo đúng thứ tự toạ độ đã gửi đi cho gọn?**

Vì bất kỳ API nào trả thiếu, đổi thứ tự hay timeout một phần cũng sẽ làm ghép theo thứ tự mảng gán sai giá trị
cho sai vị trí. Ghép theo khoá qua pandas/Spark merge an toàn với mọi kiểu thiếu dữ liệu đó.

**G10. Luật hợp nhất khi dữ liệu thiếu là gì, có rõ ràng không hay tuỳ biến từng trường hợp?**

Ba quy tắc cố định: ưu tiên nguồn hạng cao nhất có số liệu; nếu thiếu thì lấy hạng kế (ví dụ GHCN thiếu mưa ngày
Yagi thì lấy ERA5); nếu các nguồn có số liệu nhưng lệch quá ngưỡng thì gắn cờ xung đột chứ không tự chọn. Không
bao giờ nội suy để lấp khoảng thiếu.

**G11. Vị trí của các nguồn có được kiểm chứng bằng bản đồ thật không, hay chỉ giả định cùng toạ độ?**

Có bản đồ vùng nghiên cứu (phụ lục trang 38) vẽ đúng 119 vị trí theo toạ độ thật trong bảng Location, không vẽ
minh hoạ giả định.

**G12. Đồng bộ thời gian giữa các nguồn xử lý ra sao, có nguồn nào lệch múi giờ không?**

Có và đã xử lý một phần: GHCN ghi ngày theo giờ địa phương, còn lại dùng UTC; mọi nguồn chuẩn hoá về UTC khi
nạp. Riêng ranh giới NGÀY của GHCN (lệch 7–8 giờ so với UTC) nhóm ghi rõ là hạn chế chưa xử lý triệt để, không
giấu.

**G13. Nhóm có log nào để truy vết lại quá trình hợp nhất khi có nghi ngờ không?**

Có: cột `qc_flag` ghi lý do mỗi giá trị bị đặt NULL (ví dụ `ISD_QC:SLP=2`); bảng Survivorship ghi cột nguồn được
chọn và cờ xung đột cho từng biến. Truy vết được, không phải hộp đen.

**G14. Nếu thêm một nguồn thứ sáu, có phải sửa lại toàn bộ luồng ưu tiên không?**

Không, chỉ thêm một dòng trong `SOURCE_PRIORITY` và một hàm parse mới; Entity Resolution và Survivorship không
hard-code số nguồn nên không phải sửa logic đã có.

**G15. Nhóm giả định hay đã kiểm chứng thật rằng API trả đúng dữ liệu cho đúng trạm yêu cầu?**

Đã kiểm chứng: `scripts/check_data_sources.py` gọi thật từng nguồn, so khớp toạ độ trả về với toạ độ đã gửi
trước khi tải hàng loạt, kết quả lưu ở `data_samples/`.

**G16. Hai nguồn lệch đơn vị thì nhóm phát hiện bằng cách nào, không phải chỉ đoán?**

Đọc đơn vị trực tiếp từ metadata của từng nguồn (`hourly_units` Open-Meteo, thuộc tính NetCDF ERA5), không viết
cứng; mỗi phép đổi đơn vị có test riêng — lỗi gió km/h bị phóng đại 3,6 lần trước đây chính là do viết cứng đơn
vị, đã sửa và thêm test.

**G17. Nếu được yêu cầu mở code ngay để xem đoạn xử lý ưu tiên nguồn, nhóm mở file nào?**

`warehouse/survivorship.py`, có `SOURCE_PRIORITY` và `CONFLICT_THRESHOLD_PCT` khai báo ngay đầu file. Xem mục
"Mở nhanh khi trình bày" trong `kich-ban-bao-ve.md` để mở đúng file trong một lệnh.

**G18. Ghép trạm (Entity Resolution) có thật sự theo khoá như cô yêu cầu không, hay vẫn có yếu tố giả định vị trí?**

Khoá ghép là toạ độ thật (khoảng cách Haversine), kiểm chứng độc lập bằng mã WMO — một khoá khác, không liên
quan toạ độ. Hai khoá độc lập cho cùng kết quả 100% precision/recall trên 15 cặp có nhãn.

**G19. Một trạm không tìm được trạm tương ứng trong bán kính ghép thì xử lý thế nào, có ép ghép không?**

Không ép ghép: 4/26 trạm ISD không có trạm GHCN nào trong 5\,km thì giữ riêng, không gán nhầm sang trạm gần nhất
ngoài ngưỡng.

**G20. Bản ghi trùng lặp của một nguồn loại theo khoá gì, có phải theo thứ tự dòng trong file không?**

Theo khoá (trạm, thời điểm, loại bản tin METAR/SYNOP), ưu tiên giữ METAR rồi SYNOP, lấy giá trị không rỗng —
không loại theo thứ tự xuất hiện trong file. Giảm đúng 393.155 bản ghi trùng trong số 22,7% bản ghi ISD trùng.

**G21. Nguồn nào khớp với trạm đo thật nhất? Đo bằng số hay chỉ đánh giá định tính?**

Đo bằng số: ERA5 sau nội suy có RMSE nhiệt độ 1,14\,°C, gió 1,05\,m/s so với trạm trên 108.542 cặp. Chính con số
này quyết định ERA5 xếp hạng 2 (sau trạm đo thật) trong luật ưu tiên, không phải nhận định chủ quan.

**G22. Hai nguồn trong ngưỡng cho phép có tự động coi là khớp không, hay vẫn gắn cờ để theo dõi?**

Bảng vẫn lưu trạng thái cờ xung đột (true/false) dù trong hay ngoài ngưỡng — không ẩn đi chỉ vì nằm trong
ngưỡng, người dùng luôn thấy được trạng thái thật.

**G23. Độ phân giải không gian khác nhau giữa các nguồn (lưới 0,25° vs 0,5° vs điểm trạm) ảnh hưởng gì tới luật ưu tiên?**

Có ảnh hưởng trực tiếp và nhất quán: NASA POWER lưới thô nhất (0,5°) xếp hạng thấp nhất; ERA5 mịn hơn (0,25°)
xếp hạng 2. Độ phân giải càng thô thì hạng ưu tiên càng thấp, phản ánh đúng mức tin cậy không gian.

**G24. Timestamp giữa các nguồn có cùng định dạng khi so sánh trực tiếp không, hay phải quy đổi?**

Phải quy đổi: mọi nguồn chuẩn hoá về `timestamp_utc` trước khi so sánh hay ghép, không so trực tiếp timestamp
thô (vốn khác định dạng/múi giờ giữa các nguồn).

**G25. Khi API trả mảng nhiều điểm trong một lần gọi, nhóm xác nhận đúng thứ tự thế nào, hay giả định API trả đúng thứ tự gửi đi?**

`scripts/check_data_sources.py` so khớp toạ độ trả về với toạ độ gửi đi theo từng điểm trước khi gắn
`location_id`, không giả định thứ tự — dù API trả đúng hay sai thứ tự, dữ liệu vẫn gắn đúng khoá trước khi vào
kho.

**G26. Toạ độ lat/lon trong bảng Location có ý nghĩa gì trong tích hợp, hay chỉ là cột mô tả?**

Là khoá không gian chính, dùng ở ba bước: Entity Resolution (khoảng cách Haversine để ghép GHCN–ISD), nội suy
ERA5 (Bilinear đúng lat/lon trạm), và đối chứng dị thường (tìm trạm lân cận trong bán kính 200\,km).

**G27. Mục tiêu và công việc của từng người có đo được rõ ràng không, hay mô tả chung chung?**

Đo được: Quang (M1 — kho đủ 5 nguồn đúng phạm vi), Lương (M2 — GAV/Entity Resolution/Survivorship có số đo),
Nghĩa (M3 tối ưu Spark, M4 dị thường, M5 dashboard) — mỗi mục tiêu có ngưỡng đặt trước khi làm.

**G28. Nếu cô yêu cầu xem ngay bảng đối chiếu chứng minh hai nguồn khớp nhau, nhóm đưa ra bằng chứng gì?**

Bảng Survivorship (856.452 dòng, cột nguồn được chọn + cờ xung đột) và log `survivorship_conflict_by_source.py`
(tỷ lệ xung đột theo biến) — cả hai đều tính trực tiếp từ kho, không phải bảng dựng tay để minh hoạ.

## H. Cửa sổ 2020–2024, Fellegi–Sunter và liên kết trạm–lưới

Cùng kiểu câu ở mục G: cô hỏi "dựa vào giả định hay có bằng chứng", "ngưỡng lấy từ đâu", "ghép hay không ghép".
Mọi số dưới đây lấy từ báo cáo cuối (Mục 6.2, 6.5, 6.8, 6.12).

**H1. Kho có GHCN từ 1943, sao kết quả dị thường chỉ báo 2020–2024?**

Vì 2020–2024 là giai đoạn cả 5 nguồn cùng có dữ liệu và luôn có ERA5 để đối chứng. Trước 2020 phần lớn dị thường
tại trạm không có đối chứng nào, nên không tách được khí hậu thật với lỗi cảm biến. Chuỗi GHCN dài chỉ dùng làm
khí hậu nền 1991–2020 và để tính xu hướng 30 năm (Phụ lục trang 48).

**H2. Trong 2020–2024 không còn ca nào thiếu đối chứng, có phải do nhóm lọc bớt không?**

Không lọc: 5.910 ca bất thường/cực đoan tại trạm GHCN/ISD đều được giữ và phân loại. 5.515 ca (93,3%) được ERA5
hoặc trạm lân cận xác nhận, 375 (6,3%) là dị thường cục bộ, 20 (0,3%) nghi lỗi. Số 0 ca thiếu đối chứng là vì
ERA5 phủ đủ mọi ngày và mọi vị trí trong cửa sổ, không phải do loại bỏ.

**H3. Ngưỡng Fellegi–Sunter θh = 6,64 và θl = −1,31 lấy từ đâu, có chọn tay không?**

Không chọn tay: lấy theo định nghĩa gốc của Fellegi–Sunter. θh ứng với tỷ lệ ghép nhầm μ ≤ 0,05%, θl ứng với tỷ
lệ bỏ sót λ ≤ 1%, tính từ xác suất m, u ước lượng bằng EM không giám sát trên 2.262 cặp. Mã WMO không làm đặc
trưng vì đó là nhãn đánh giá (Phụ lục trang 65).

**H4. Fellegi–Sunter có tốt hơn luật Haversine 5 km không? Nếu không thì làm để làm gì?**

Không tốt hơn, nói thẳng: trên nhãn WMO, bản nhiều–một bằng Haversine (17/17), bản 1–1 kém một cặp ở Don Mueang
(16/17). Giá trị của nó là ngưỡng gắn với tỷ lệ lỗi tường minh thay cho con số 5 km kinh nghiệm, chỉ còn 3 cặp
cần xem tay, và lộ ra Đà Nẵng, Tân Sơn Nhất, Don Mueang mỗi nơi có 2 chuỗi GHCN của cùng sân bay.

**H5. Luật phủ quyết (cannot-link) đặt ngưỡng 10 km và 100 m dựa trên gì? Có loại nhầm cặp đúng không?**

Dựa trên dữ liệu: cặp khớp thật xa nhất 2,76 km và lệch độ cao tối đa 9,3 m, nên 10 km và 100 m còn dư biên rộng.
Ba luật (xa hơn 10 km, lệch hơn 100 m, khác nước) loại 1.625 + 608 + 1 = 2.234 cặp, không cặp đúng nào bị loại, và
chặn 2 cặp sai mà mô hình xếp khớp chỉ vì tên giống: Surabaya/Perak–Juanda (19,7 km), Mandalay–Mandalay Intl
(33,7 km).

**H6. Trạm và ô ERA5 cùng vị trí, sao không gộp làm một mà lại chỉ "liên kết"?**

Vì đó là hai thực thể khác nhau: trạm là một điểm đo, ô ERA5 là trung bình 0,25° trên địa hình mô hình. 19/119
vị trí lệch độ cao quá 100 m; Luang Prabang trạm ở 291 m, ô ERA5 ở 749 m, trạm ấm hơn 3,53 °C. Bias theo độ lệch
độ cao có độ dốc −5,66 °C/km, gần gradient chuẩn −6,5, nên phần lớn là khác biệt đại diện. Gộp sẽ biến chênh lệch
đó thành "xung đột" cần chọn bên thắng. Bảng `station_grid_link.parquet` ghi quan hệ, trung vị 9,42 km (Phụ lục
trang 66).

**H7. Lỗi dữ liệu tập trung ở đâu? Có phải lỗi rải đều do pipeline không?**

Không rải đều, nên không phải lỗi pipeline: trong 2020–2024, 1.590 dòng gắn cờ QC nằm ở 32/61 trạm, năm trạm ISD
ở Campuchia, Lào, Myanmar, Thái Lan chiếm 56,4%. 20 ca nghi lỗi từ xác nhận chéo ở 8 trạm, riêng Phnom Penh 13 ca.
Phnom Penh có mặt ở cả ba lớp (219 dòng cờ QC, 13 ca nghi lỗi, trôi áp suất −0,65 hPa/năm); Viêng Chăn có 210
dòng cờ QC và nhảy bậc nhiệt độ (Phụ lục trang 64).

**H8. PINN giải quyết được bao nhiêu phần trăm dị thường? Mục tiêu tiếp theo có đo được không?**

PINN giải quyết được 2/12 trường của lược đồ chung, độ ẩm và gió, đúng hai trường mà bộ dò dị thường (chạy trên
nhiệt độ 12.209 ca và áp suất 10.237 ca, 2020–2024) chưa phủ, nên nó mở rộng phạm vi phát hiện. Mô hình độ ẩm cho
`rh_pct` ở 3.063.576 bản ghi ISD chỉ có điểm sương (sai số 1,07 điểm %). Mô hình gió điền được gió tại điểm thiếu
số liệu giữa các ô lưới ERA5 hoặc tại trạm (22 vị trí giữ lại: RMSE 1,06 m/s so với gió trung bình 2,26 m/s, sai số
còn cao, cần thêm chiều thời gian). Phần dư của mô hình gió đánh dấu 4/113
vị trí lệch trường vật lý quá 2,62 m/s (Mandalay cả mã ISD lẫn GHCN, Đồng Hới, Phú Quốc), là ứng viên dị thường
gió cục bộ. Mục tiêu tiếp theo đo được: dùng trường PINN phân xử 375 ca dị thường cục bộ (6,3%) mà lưới ERA5
khoảng 28 km không xác nhận được; chỉ tiêu là số ca cục bộ giảm mà tỉ lệ nghi lỗi không tăng giả (Phụ lục trang 57).
