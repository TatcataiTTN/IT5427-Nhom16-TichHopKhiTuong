# Kịch bản thuyết trình: Tích hợp dữ liệu khí tượng đa nguồn Đông Nam Á

**Người nghe:** hội đồng IT5427 (cô Vũ Tuyết Trinh). **Mục đích:** bảo vệ project cuối kỳ (60% điểm).
**Thời lượng:** 30 phút gồm cả hỏi đáp. Bài chính khoảng 20 phút, để lại khoảng 10 phút hỏi đáp.
**Slide:** `final-defense.pdf`, bài chính trang 1–31, Phụ lục trang 32–53 (chỉ mở khi bị hỏi).

**Cô quan tâm nhất:** dữ liệu thu thập có đặc trưng gì, yêu cầu xử lý gì (thiếu, ngoài khoảng, đơn vị không đồng
nhất…). Phần 3 trả lời thẳng câu này; đừng nói vội phần 3.

**Chia người nói** (theo phân công trong deck cũ, chỉnh lại nếu nhóm chia khác):

| Phần | Nội dung | Người nói | Slide (trang) | Thời lượng |
|---|---|---|---|---|
| 0 | Mở đầu | Quang | 1–2 | 0:30 |
| 1 | Đặt vấn đề | Quang | 3–5 | 2:00 |
| 2 | Mục tiêu, dữ liệu và kiến trúc | Quang | 6–9 | 3:00 |
| 3 | Đặc trưng dữ liệu và yêu cầu xử lý | Quang | 10–16 | 6:00 |
| 4 | Tích hợp dữ liệu | Lương | 17–20 | 3:00 |
| 5 | Xử lý và phân tích | Nghĩa | 21–27 | 5:00 |
| 6 | Kết luận | Nghĩa | 28–31 | 1:30 |
| | **Tổng bài chính** | | **31 trang** | **khoảng 21 phút** |

Nếu bị nhắc giờ: xem mục "Slide có thể nói lướt" ở cuối file.

---

# Phần 0. Mở đầu

## 0.1. Bìa và nội dung trình bày (30 giây)

**Trên slide**

Tích hợp dữ liệu khí tượng đa nguồn Đông Nam Á; mục lục 6 phần.

**Lời nói**
> Em chào cô. Nhóm 16 gồm Quang, Lương và Nghĩa, đề tài là tích hợp dữ liệu khí tượng đa nguồn cho Đông Nam Á.
>
> Bài gồm sáu phần. Em trình bày ba phần đầu: vấn đề, mục tiêu và đặc trưng dữ liệu. Lương trình bày phần tích hợp.
> Nghĩa trình bày phần xử lý, phân tích và kết luận.

**Chuyển ý**
> Trước hết là vì sao bài toán này cần tích hợp nhiều nguồn.

---

# Phần 1. Đặt vấn đề

## 1.1. Bối cảnh (1 phút)

**Trên slide**

Đông Nam Á chịu nhiều hiện tượng khí hậu cực đoan, nhưng trạm quan trắc phân bố không đều
- Nắng nóng 4–5/2024, bão Yagi 9/2024, hạn Mekong 2019–2020
- Singapore, Timor-Leste không có trạm nào nhóm chọn được
- Trạm đo trực tiếp nhưng thưa; ERA5 phủ kín nhưng là ước lượng của mô hình

Kết luận: tích hợp để so trạm với ERA5 và trạm lân cận, lấy ERA5 khi trạm mất số liệu.

**Lời nói**
> Đông Nam Á mấy năm gần đây có nhiều hiện tượng cực đoan: nắng nóng tháng 4, tháng 5 năm 2024, bão Yagi tháng 9
> năm 2024, hạn ở hạ lưu Mekong 2019–2020.
>
> Muốn biết một ngày có bất thường không thì phải có số liệu. Nhưng trạm quan trắc phân bố rất không đều. Singapore
> và Timor-Leste, nhóm không tìm được trạm nào dùng được.
>
> Có hai loại dữ liệu. Trạm là số đo thật nhưng thưa và hay mất số liệu. ERA5 là dữ liệu tái phân tích, có giá trị ở
> mọi ô lưới, nhưng đó là ước lượng của mô hình.
>
> Nên một trạm báo nhiệt độ rất cao thì chưa biết là nóng thật hay cảm biến hỏng. Phải so với ERA5 và với trạm bên
> cạnh. Đó là lý do cần tích hợp.

**Chuyển ý**
> Nhưng tích hợp không đơn giản là gộp các file lại với nhau.

## 1.2. Lỗi khi nạp thẳng dữ liệu thô (1 phút)

**Trên slide**

Nạp dữ liệu thô mà không chuẩn hoá thì số liệu sai, nhưng chương trình không báo lỗi
- ISD `SLP="99999,9"` là mã "không đo", đọc thẳng thành 9.999,9 hPa
- Open-Meteo trả gió km/h, ghi vào cột m/s thì phóng đại 3,6 lần
- ISD gửi cùng quan trắc qua METAR và SYNOP: 393.155 bản ghi trùng lặp
- ISD Phnom Penh 3/7/2023: áp suất 995–1054 hPa dù đã qua QC của NOAA

**Lời nói**
> Đây là bốn lỗi nhóm gặp thật khi đọc thẳng dữ liệu thô.
>
> ISD ghi 99999 để báo không đo. Đọc thẳng thì thành áp suất gần mười nghìn hPa.
>
> Open-Meteo trả gió theo km/h. Lúc đầu nhóm ghi vào cột m/s, gió bị phóng đại 3,6 lần.
>
> ISD gửi cùng một quan trắc hai lần, qua METAR và SYNOP, nên có hơn 393 nghìn bản ghi trùng.
>
> Và trạm Phnom Penh: số liệu đã qua QC của NOAA mà áp suất trong một ngày vẫn dao động gần 60 hPa.
>
> Điểm chung là không có lỗi nào làm chương trình dừng. Số liệu sai cứ thế đi vào kho.

**Chuyển ý**
> Từ đó nhóm đặt ra mục tiêu cụ thể, có ngưỡng đo được.

---

# Phần 2. Mục tiêu, dữ liệu và kiến trúc

## 2.1. Mục tiêu (1 phút)

**Trên slide**

Bảng M1–M5: kho đủ 5 nguồn; GAV, ER, Survivorship có kiểm chứng; `cache()` giảm thời gian ≥ 30%; dị thường đối
chứng 3 sự kiện; dashboard không lỗi runtime.

**Lời nói**
> Nhóm đặt năm mục tiêu, mỗi mục tiêu có chỉ số và ngưỡng đặt trước khi làm.
>
> M1 là kho đủ năm nguồn, đúng phạm vi đề cương: ERA5 năm năm, ISD mười năm. M2 là ba kỹ thuật tích hợp của môn
> học, GAV, Entity Resolution và Survivorship, phải có số đo. M3 là tối ưu Spark, `cache()` phải giảm thời gian truy
> vấn ít nhất 30%. M4 là phát hiện dị thường, phải đúng chiều với ba sự kiện đã chọn trước. M5 là dashboard chạy
> không lỗi.
>
> Cuối bài nhóm sẽ đối chiếu lại từng mục này.

**Chuyển ý**
> Năm nguồn dữ liệu cụ thể như sau.

## 2.2. Nguồn dữ liệu và đặc trưng dữ liệu lớn (1 phút)

**Trên slide**

Bảng 5 nguồn (cấu trúc, định dạng, độ phân giải, phạm vi, số bản ghi); Volume, Variety, Velocity, Veracity.

**Lời nói**
> Năm nguồn khác nhau ngay từ cấu trúc. ERA5 là lưới. GHCN và ISD là chuỗi tại trạm. NASA POWER và Open-Meteo là
> điểm, truy vấn qua API. Độ phân giải cũng khác: từ 30 phút tới một ngày.
>
> Về đặc trưng dữ liệu lớn: dữ liệu thô 23,4 GB, phần lớn là ERA5. Sau tích hợp còn 303 MB Parquet, gần 9 triệu bản
> ghi. Variety là ba dạng cấu trúc và ba định dạng.
>
> Velocity thì em nói rõ: đây là dữ liệu lịch sử. Nhóm mô phỏng luồng bằng cách phát lại qua Kafka vào Spark
> Structured Streaming.
>
> Veracity là phần thiếu, sai, lệch giữa các nguồn, em trình bày kỹ ở phần 3.

**Chuyển ý**
> Các nguồn này đi qua hệ thống theo kiến trúc sau.

**Ghi chú:** số dòng ERA5 là sau khi nội suy vào 113 trạm.

## 2.3. Kiến trúc tổng thể (1 phút)

**Trên slide**

Sơ đồ: 5 nguồn → Ingestion + QC 4 tầng → Mediated Schema `WeatherObs` (GAV) → kho Parquet → ER, Survivorship, dị
thường, PINN, Kafka/Streaming → Dashboard.

**Lời nói**
> Dữ liệu đi từ trái sang phải.
>
> Năm nguồn vào tầng Ingestion. Ở đây dữ liệu được parse, chuẩn hoá và chạy QC. ERA5 được nội suy vào toạ độ trạm.
>
> Sau đó dữ liệu ánh xạ vào lược đồ chung `WeatherObs` theo GAV, rồi ghi vào kho Parquet, chia partition theo năm và
> nguồn.
>
> Từ kho, các bước phía sau cùng đọc chung: Entity Resolution, Survivorship, phát hiện dị thường, PINN. Kafka phát
> lại dữ liệu cho Spark Streaming. Cuối cùng là dashboard.

**Chuyển ý**
> Phần quan trọng nhất là tầng đầu tiên: dữ liệu thô có vấn đề gì và phải xử lý ra sao.

---

# Phần 3. Đặc trưng dữ liệu và yêu cầu xử lý

## 3.1. Tổng quan đặc trưng và yêu cầu xử lý (1 phút)

**Trên slide**

Bảng 6 nhóm: dữ liệu thiếu; ngoài khoảng, giá trị sai; đơn vị đo; ngữ nghĩa; thời gian; không gian, định danh. Mỗi
nhóm có đặc trưng đo được và yêu cầu xử lý.

**Lời nói**
> Nhóm đo các vấn đề trực tiếp trên dữ liệu thật và chia làm sáu nhóm.
>
> Thiếu dữ liệu. Giá trị ngoài khoảng và giá trị sai. Đơn vị đo khác nhau. Khác nhau về ngữ nghĩa, tức là trùng tên
> nhưng khác đại lượng. Khác nhau về thời gian. Và khác nhau về không gian, định danh.
>
> Cột giữa là số đo được, cột phải là yêu cầu xử lý. Em đi lần lượt từng nhóm.

**Chuyển ý**
> Đầu tiên là dữ liệu thiếu.

## 3.2. Dữ liệu thiếu (1 phút 15 giây)

**Trên slide**

Bảng tỷ lệ thiếu theo biến và nguồn; thiếu theo thời gian; thiếu khác giá trị 0; mã thiếu khác nhau. Yêu cầu: đổi mã
thiếu thành NULL, không điền 0 hay trung bình, tổng hợp phải đủ dữ liệu.

**Lời nói**
> Nhóm tách thiếu làm hai loại.
>
> Loại thứ nhất là nguồn không đo biến đó. Các ô 100% màu đỏ là như vậy. GHCN không đo độ ẩm, gió, áp suất. ISD
> trong dữ liệu đã tải không có mưa. Cái này không phải lỗi, không được bịa số.
>
> Loại thứ hai là có đo nhưng mất số liệu. GHCN trung vị đủ 91,3% số ngày, trạm tệ nhất chỉ còn 46,5%.
>
> Có một điểm dễ sai là mưa. GHCN chỉ có số liệu mưa ở 58,7% số ngày. Ngày không báo cáo khác hẳn ngày không mưa.
>
> Yêu cầu xử lý: mọi mã thiếu, 99999, −999, null, đều đổi thành NULL. Không điền 0, không điền trung bình. Khi tổng
> hợp phải đủ dữ liệu mới tính, ví dụ tháng mưa phải có ít nhất 90% số ngày.
>
> Nhóm đã từng vi phạm: thay NULL bằng 0 trước khi tính tương quan, ra tương quan giả 0,57 giữa gió và độ ẩm.

**Chuyển ý**
> Có số liệu rồi thì câu hỏi tiếp theo là số liệu đó có đúng không.

## 3.3. Giá trị ngoài khoảng và giá trị sai (1 phút 15 giây)

**Trên slide**

Bảng QC 7 tầng: cờ QC nguồn, giới hạn vật lý, nhất quán nội bộ, bước nhảy, IQR, đối chứng không gian, trôi cảm biến.
Tầng 1–4 ở Ingestion, 5–7 ở bước phân tích.

**Lời nói**
> Nhóm kiểm tra theo bảy tầng, từ đơn giản đến phức tạp.
>
> Tầng 1 đọc cờ QC của chính NOAA. 406 giá trị GHCN và 3.255 giá trị ISD bị NOAA gắn cờ lỗi, nhóm đặt chúng thành
> NULL.
>
> Tầng 2 là giới hạn vật lý, ví dụ gió không quá 75 m/s. Có hai bản tin gió 83 m/s, nhưng NOAA đã gắn cờ từ trước.
>
> Tầng 4 bắt bước nhảy, ví dụ nhiệt độ đổi hơn 10 độ trong một giờ. Có 36 điểm như vậy.
>
> Bốn tầng đầu chạy ngay khi nạp. Ba tầng sau cần dữ liệu đã tích hợp: IQR, đối chứng với ERA5 và trạm lân cận, và
> phát hiện trôi cảm biến.
>
> Nguyên tắc chung là gắn cờ, không xoá bản ghi, để bước sau còn truy lại được.
>
> Ví dụ Phnom Penh: giá trị đã qua QC của NOAA vẫn nhảy 25 hPa trong 3 giờ. Chỉ tầng 4, 6 và 7 mới bắt được.

**Chuyển ý**
> Giá trị đúng rồi, nhưng mỗi nguồn lại ghi bằng một đơn vị khác nhau.

## 3.4. Đơn vị đo không đồng nhất (1 phút)

**Trên slide**

Bảng đơn vị theo biến × nguồn và đơn vị chuẩn. Yêu cầu: đọc đơn vị và mã thiếu từ metadata, mỗi phép đổi có test.

**Lời nói**
> Bảng này là đơn vị thật của từng nguồn.
>
> Nhiệt độ: GHCN và ISD ghi phần mười độ C, ERA5 ghi Kelvin. Áp suất: ERA5 dùng Pa, NASA POWER dùng kPa. Gió:
> Open-Meteo dùng km/h, ERA5 lại tách thành hai thành phần u, v.
>
> Độ ẩm thì ISD không có sẵn, nhóm tính từ điểm sương theo phương trình Clausius–Clapeyron.
>
> Yêu cầu là đọc đơn vị từ metadata của nguồn, không tự giả định, và mỗi phép đổi có test. Lỗi km/h ở phần đặt vấn
> đề chính là do lúc đầu nhóm tự giả định đơn vị.

**Chuyển ý**
> Khó hơn đơn vị là trường hợp cùng tên biến nhưng thực ra là hai đại lượng khác nhau.

## 3.5. Không đồng nhất về ngữ nghĩa và thời gian (1 phút)

**Trên slide**

Bảng: gió 2 m và 10 m; 3 định nghĩa nhiệt độ ngày; áp suất bề mặt và mực biển; bức xạ đỉnh khí quyển và bề mặt; bản
tin trùng ISD; độ phân giải thời gian; ranh giới ngày GHCN (chưa xử lý).

**Lời nói**
> Ví dụ gió: NASA POWER mặc định đo ở độ cao 2 mét, các nguồn khác đo ở 10 mét. Gió 2 mét chỉ bằng 0,65 lần. Nhóm
> tải biến gió 10 mét của NASA.
>
> Nhiệt độ ngày có ba cách tính. TAVG của GHCN thấp hơn trung bình max–min khoảng 0,25 độ. Nhóm ghi cách tính vào
> cột `temp_def`.
>
> Áp suất bề mặt và áp suất mực biển là hai đại lượng khác nhau, lệch khoảng 12 hPa mỗi 100 mét độ cao. Hai cột này
> giữ riêng.
>
> Về thời gian, mọi nguồn chuẩn hoá về UTC.
>
> Còn một việc nhóm chưa xử lý: ngày của GHCN là ngày giờ địa phương, lệch 7–8 tiếng so với UTC. Khi so với ERA5
> theo ngày thì có độ lệch này.

**Chuyển ý**
> Nhóm cuối là khác nhau về không gian: lưới ERA5 và điểm trạm.

## 3.6. Không đồng nhất về không gian (1 phút)

**Trên slide**

ERA5 nội suy vào toạ độ trạm: RMSE nhiệt độ 1,14°C, gió 1,05 m/s, mưa 19,83 mm. Hạn chế: mưa lấy từ ERA5 sai số
lớn.

**Lời nói**
> ERA5 là lưới 0,25 độ, khoảng 28 km. Nhóm nội suy Bilinear vào toạ độ từng trạm, rồi so với số đo thật cùng ngày:
> hơn 108 nghìn cặp.
>
> Nhiệt độ sai khoảng 1,1 độ, gió khoảng 1 m/s, chấp nhận được. Mưa thì sai gần 20 mm, kém.
>
> Trạm càng cao thì nhiệt độ càng lệch, vì lưới 0,25 độ không thể hiện được địa hình.
>
> Hạn chế nhóm ghi nhận: khi trạm thiếu số liệu mưa, giá trị lấy từ ERA5 có sai số lớn.
>
> Còn vấn đề cùng một trạm có hai mã GHCN và ISD, Lương sẽ trình bày ở phần tích hợp.

**Chuyển ý**
> Dữ liệu đã sạch và cùng đơn vị. Lương trình bày cách đưa năm nguồn về một kho.

---

# Phần 4. Tích hợp dữ liệu

## 4.1. Mediated Schema và ánh xạ GAV (1 phút)

**Trên slide**

Lược đồ `WeatherObs(...)`; ví dụ view NASA POWER; PIVOT GHCN, PARSE ISD; chọn GAV vì số nguồn cố định. Toàn vẹn tham
chiếu 100%.

**Lời nói**
> Em là Lương, em trình bày phần tích hợp.
>
> Nhóm định nghĩa một lược đồ trung gian là `WeatherObs`: vị trí, thời gian UTC, nguồn, các biến khí tượng, cùng hai
> cột `temp_def` và `qc_flag` từ bước xử lý.
>
> Mỗi nguồn được viết thành một view vào lược đồ này, tức là Global-as-View. Ví dụ NASA POWER: T2M ánh xạ vào
> `temp_c`.
>
> Hai nguồn cần biến đổi trước. GHCN ở dạng long, mỗi dòng một biến, nên phải PIVOT. ISD gói giá trị và mã QC trong
> một trường, nên phải PARSE.
>
> Nhóm chọn GAV vì có đúng năm nguồn cố định. Trả lời truy vấn chỉ cần khai triển view, không phải viết lại truy vấn
> như LAV.

**Chuyển ý**
> Lược đồ chung rồi, nhưng GHCN và ISD vẫn gọi cùng một trạm bằng hai mã khác nhau.

## 4.2. Entity Resolution GHCN và ISD (1 phút)

**Trên slide**

22/26 cặp khớp, khoảng cách trung bình 0,53 km; láng giềng gần nhất Haversine ngưỡng 5 km; precision/recall
100%/100% trên 15 cặp có nhãn.

**Lời nói**
> GHCN và ISD không có mã chung. Nhóm ghép theo khoảng cách: với mỗi trạm ISD, tìm trạm GHCN gần nhất theo khoảng cách
> Haversine, ngưỡng 5 km.
>
> Kết quả ghép được 22 trên 26 trạm. Nhiều cặp cách nhau đúng 0 km, vì hai cơ quan dùng chung toạ độ WMO gốc.
>
> Để kiểm chứng, nhóm dùng mã WMO làm nhãn độc lập. Có 15 cặp có nhãn, precision và recall đều 100%.
>
> Số trạm nhỏ nên nhóm so toàn bộ cặp, chưa cần bước blocking.

**Chuyển ý**
> Khi đã biết hai bản ghi là cùng một trạm, câu hỏi tiếp theo là hai nguồn lệch nhau thì lấy giá trị nào.

## 4.3. Hợp giải giá trị giữa các nguồn (Survivorship) (1 phút)

**Trên slide**

Hạng nguồn: ISD/GHCN > ERA5 > Open-Meteo > NASA POWER; ngưỡng xung đột theo biến; tỷ lệ xung đột 6 biến; bảng hợp
giải 856.452 dòng.

**Lời nói**
> Với mỗi vị trí, mỗi ngày, nếu nhiều nguồn cùng có giá trị thì lấy nguồn hạng cao nhất. Trạm đo trực tiếp đứng đầu,
> rồi đến ERA5, Open-Meteo, NASA POWER.
>
> Nếu các nguồn lệch quá ngưỡng thì gắn cờ xung đột. Ngưỡng đặt riêng cho từng biến, ví dụ nhiệt độ 10%, mưa 50%,
> vì mưa tự nhiên đã biến động mạnh.
>
> Bảng bên phải là tỷ lệ xung đột đo được. Áp suất mực biển gần như không lệch, 0%. Mưa lệch tới 91,6%, vì mỗi
> nguồn tích luỹ mưa theo chu kỳ khác nhau.
>
> Kết quả là bảng hợp giải 856 nghìn dòng, mỗi vị trí mỗi ngày một dòng, ghi rõ giá trị lấy từ nguồn nào.

**Chuyển ý**
> Phần tiếp theo, Nghĩa trình bày xử lý và phân tích trên kho này.

---

# Phần 5. Xử lý và phân tích

## 5.1. Tối ưu Spark (1 phút)

**Trên slide**

`cache()` giảm 69,4% thời gian truy vấn (0,36s → 0,11s); thử partition theo tháng; giữ `year/source`.

**Lời nói**
> Em là Nghĩa. Mục tiêu M3 là tối ưu Spark.
>
> Với truy vấn tổng hợp nhiệt độ theo trạm và tháng, `cache()` giảm thời gian từ 0,36 giây xuống 0,11 giây, tức
> giảm 69,4%, vượt ngưỡng 30%.
>
> Nhóm cũng thử partition thêm theo tháng. Data skew giảm rõ, nhưng số partition tăng từ 109 lên hơn 1.300.
>
> Đo lại thì ở quy mô 9 triệu bản ghi, partition còn chậm hơn không partition, vì Parquet đã tự bỏ qua dữ liệu
> không liên quan. Nhóm vẫn giữ partition theo năm và nguồn, vì lợi ích sẽ rõ khi dữ liệu lớn hơn hoặc nằm trên S3.

**Chuyển ý**
> Kho đã truy vấn được, giờ là ứng dụng chính: phát hiện dị thường khí hậu.

## 5.2. Đối chứng với ba sự kiện đã biết (1 phút)

**Trên slide**

Biểu đồ tỷ lệ ngày z ≥ 2 theo năm (2024: 11,2%); nắng nóng, Yagi, hạn Mekong. Định nghĩa z.

**Lời nói**
> Dị thường được đo bằng z: lấy giá trị trừ khí hậu nền rồi chia cho độ lệch chuẩn. Khí hậu nền tính từ GHCN giai
> đoạn 1991–2020, theo từng ngày trong năm.
>
> Ba sự kiện được chọn từ trước. Nắng nóng tháng 4–5/2024: 12,3% số ngày có z từ 2 trở lên, gấp 10 lần bình thường.
> Bão Yagi: áp suất ERA5 ở Hải Phòng xuống 978,8 hPa, đúng nơi bão đổ bộ.
>
> Hạn Mekong thì tín hiệu yếu: đúng chiều, nhưng chỉ 2 trạm có số liệu SPI đúng vùng và giai đoạn. Nhóm báo cáo đúng
> như vậy.

**Chuyển ý**
> Một giá trị z cao có thể là nóng thật, cũng có thể là cảm biến hỏng. Nhóm tách hai trường hợp này như sau.

## 5.3. Đối chứng bằng ERA5 và trạm lân cận (1 phút)

**Trên slide**

Bảng phân loại: dị thường thật, cục bộ, nghi lỗi dữ liệu, không có đối chứng; chỉ ERA5 so với ERA5 + trạm lân cận.

**Lời nói**
> Với mỗi giá trị cực đoan ở trạm, nhóm xem ERA5 cùng vị trí và các trạm trong bán kính 200 km có cùng chiều không.
>
> Cùng chiều thì là dị thường khí hậu thật. Trạm cực đoan mà đối chứng ngược chiều thì nghi lỗi dữ liệu.
>
> Chỉ dùng ERA5 thì xác nhận được 5.380 ca. Thêm trạm lân cận thì lên 20.357, vì trạm lân cận phủ được cả giai đoạn
> trước 2020 khi chưa có ERA5. 343 ca bị đánh dấu nghi lỗi dữ liệu.
>
> Trạm cách nhau dưới 5 km thì không dùng làm đối chứng, vì theo Entity Resolution đó là cùng một trạm.

**Chuyển ý**
> Các phép tính này chạy bằng batch. Nhóm kiểm tra xem làm theo luồng có ra cùng kết quả không.

## 5.4. Phát hiện dị thường theo luồng (1 phút)

**Trên slide**

179 cảnh báo trong 10 micro-batch; khớp 179/179 với batch; 1.407 bản ghi phát lại.

**Lời nói**
> Cụm gồm một master, hai worker và Kafka một broker, chạy trên một máy.
>
> Producer phát lại đợt nắng nóng 2024 vào Kafka. Spark Structured Streaming đọc từng micro-batch, join với bảng khí
> hậu nền đã tính bằng batch, rồi cảnh báo khi trị tuyệt đối của z từ 2 trở lên.
>
> Kết quả 179 cảnh báo, khớp đủ 179 với kết quả batch, giá trị z giống hệt.
>
> Cảnh báo cao nhất là ngày 30/4/2024, một trạm Thái Lan 38,6 độ, cao hơn nền hơn 8 độ.

**Chuyển ý**
> Ngoài thống kê, nhóm thử một mô hình học máy có ràng buộc vật lý cho trường gió.

## 5.5. PINN cho trường gió (45 giây)

**Trên slide**

Bảng λ = 0; 0,01; 0,1; 1,0 với RMSE, MAE, physics loss. PINN chưa vượt baseline về RMSE.

**Lời nói**
> Mục đích là làm mịn trường gió giữa lưới ERA5 và trạm, có thêm ràng buộc vật lý là phương trình liên tục.
>
> λ là trọng số của ràng buộc vật lý; λ bằng 0 là hồi quy thuần. Baseline có RMSE tốt nhất. PINN với λ 0,1 tốt hơn
> một chút về MAE. Chênh lệch khoảng 1%, trên 22 trạm kiểm tra, nên nhóm chưa kết luận mô hình nào tốt hơn.
>
> Lý do có thể là nhóm mới có một thời điểm, trong khi ràng buộc vật lý cần chuỗi thời gian.

**Chuyển ý**
> Kết quả của các phần trên được gom lại trên dashboard.

## 5.6. Dashboard (30 giây)

**Trên slide**

Ảnh panel 7 (dị thường khí hậu); danh sách 10 panel.

**Lời nói**
> Dashboard viết bằng Streamlit, 10 panel, đọc trực tiếp từ kho Parquet. Đây là panel dị thường khí hậu: tỷ lệ ngày
> nóng bất thường, đợt nóng dài nhất 30 ngày, năm 2024 cao hẳn các năm khác.
>
> Nhóm kiểm tra cả 10 panel trên trình duyệt, không có lỗi runtime.

**Chuyển ý**
> Em tổng kết lại theo năm mục tiêu ban đầu.

---

# Phần 6. Kết luận

## 6.1. Kết quả theo mục tiêu (45 giây)

**Trên slide**

Bảng M1–M5 với kết quả đo được; 4/5 đạt đầy đủ, M4 đạt một phần; 83 test tự động.

**Lời nói**
> Đối chiếu với năm mục tiêu: M1 đủ năm nguồn, đúng phạm vi. M2 có toàn vẹn tham chiếu 100%, Entity Resolution đúng
> trên 15 cặp có nhãn, bảng hợp giải 856 nghìn dòng. M3 giảm 69,4%, vượt ngưỡng. M5 dashboard không lỗi.
>
> M4 nhóm đánh giá là đạt một phần, vì hạn Mekong chỉ có tín hiệu yếu.
>
> Hệ thống có 83 test tự động, gồm cả test chạy với Spark và Kafka.

**Chuyển ý**
> Cuối cùng là những gì nhóm chưa làm được.

## 6.2. Kết luận và hướng phát triển (45 giây)

**Trên slide**

Đã làm / Hạn chế / Hướng tiếp.

**Lời nói**
> Nhóm đã có kho gần 9 triệu bản ghi từ năm nguồn. Dữ liệu được xử lý thiếu, sai, đơn vị, ngữ nghĩa ngay từ đầu
> pipeline, rồi tích hợp bằng GAV, Entity Resolution và Survivorship.
>
> Hạn chế: ngày GHCN chưa căn theo giờ địa phương; trôi cảm biến mới phát hiện, chưa hiệu chỉnh; hạ tầng chạy trên một
> máy; mưa lấy từ ERA5 còn sai số lớn.
>
> Hướng tiếp theo đi đúng vào các hạn chế đó. Em xin cảm ơn cô, nhóm sẵn sàng trả lời câu hỏi.

---

# Hỏi đáp dự kiến

Đã tách sang file riêng: [`hoi-dap-bao-ve.md`](hoi-dap-bao-ve.md).

---

# Slide có thể nói lướt nếu thiếu giờ

- 2.2 Nguồn dữ liệu (10 giây): chỉ nói Volume và Velocity.
- 3.6 Không gian (30 giây): chỉ nói RMSE mưa kém.
- 5.5 PINN (20 giây): "chưa vượt baseline, chênh 1%, chưa kết luận".
- 5.6 Dashboard (15 giây).

Không cắt phần 3: đây là phần cô hỏi trực tiếp.
