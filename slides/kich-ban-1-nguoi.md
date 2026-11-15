# Kịch bản thuyết trình, 1 người đọc để chạy thử

Đề tài: Tích hợp dữ liệu khí tượng đa nguồn Đông Nam Á. Nhóm 16, IT5427 Tích hợp và xử lý dữ liệu lớn, bảo vệ
15/11/2026.

Thời lượng đầy đủ: khoảng 21–22 phút (31 slide chính, dựa trên `final-defense.pdf`). Số trong ngoặc vuông là số
trang trong `final-defense.pdf`. Buổi bảo vệ thật chia ba người nói (xem `kich-ban-bao-ve.md`); file này gộp lại
thành một mạch cho một người đọc thử từ đầu tới cuối, để tự kiểm tra lại toàn bộ luồng trước khi lên chia vai.

Phụ lục trang 32–53 không có trong file này, chỉ mở khi hội đồng hỏi (xem `hoi-dap-bao-ve.md`).

---

## Phần mở đầu (0:30)

**[1–2] Bìa và nội dung trình bày (0:30)**

Em chào cô. Nhóm 16 gồm Quang, Lương và Nghĩa, đề tài là tích hợp dữ liệu khí tượng đa nguồn cho Đông Nam Á.

Bài gồm sáu phần. Em trình bày ba phần đầu: vấn đề, mục tiêu và đặc trưng dữ liệu. Lương trình bày phần tích hợp. Nghĩa trình bày phần xử lý, phân tích và kết luận.

Trước hết là vì sao bài toán này cần tích hợp nhiều nguồn.

---

## Phần 1. Đặt vấn đề (2:00)

**[3–4] Bối cảnh (1:00)**

Đông Nam Á mấy năm gần đây có nhiều hiện tượng cực đoan: nắng nóng tháng 4, tháng 5 năm 2024, bão Yagi tháng 9 năm 2024, hạn ở hạ lưu Mekong 2019–2020.

Muốn biết một ngày có bất thường không thì phải có số liệu. Nhưng trạm quan trắc phân bố rất không đều. Singapore và Timor-Leste, nhóm không tìm được trạm nào dùng được.

Có hai loại dữ liệu. Trạm là số đo thật nhưng thưa và hay mất số liệu. ERA5 là dữ liệu tái phân tích, có giá trị ở mọi ô lưới, nhưng đó là ước lượng của mô hình.

Nên một trạm báo nhiệt độ rất cao thì chưa biết là nóng thật hay cảm biến hỏng. Phải so với ERA5 và với trạm bên cạnh. Đó là lý do cần tích hợp.

Nhưng tích hợp không đơn giản là gộp các file lại với nhau.

**[5] Lỗi khi nạp thẳng dữ liệu thô (1:00)**

Đây là bốn lỗi nhóm gặp thật khi đọc thẳng dữ liệu thô.

ISD ghi 99999 để báo không đo. Đọc thẳng thì thành áp suất gần mười nghìn hPa.

Open-Meteo trả gió theo km/h. Lúc đầu nhóm ghi vào cột m/s, gió bị phóng đại 3,6 lần.

ISD gửi cùng một quan trắc hai lần, qua METAR và SYNOP, nên có hơn 393 nghìn bản ghi trùng.

Và trạm Phnom Penh: số liệu đã qua QC của NOAA mà áp suất trong một ngày vẫn dao động gần 60 hPa.

Điểm chung là không có lỗi nào làm chương trình dừng. Số liệu sai cứ thế đi vào kho.

Từ đó nhóm đặt ra mục tiêu cụ thể, có ngưỡng đo được.

---

## Phần 2. Mục tiêu, dữ liệu và kiến trúc (3:00)

**[6–7] Mục tiêu (1:00)**

Nhóm đặt năm mục tiêu, mỗi mục tiêu có chỉ số và ngưỡng đặt trước khi làm.

M1 là kho đủ năm nguồn, đúng phạm vi đề cương: ERA5 năm năm, ISD mười năm. M2 là ba kỹ thuật tích hợp của môn học, GAV, Entity Resolution và Survivorship, phải có số đo. M3 là tối ưu Spark, cache() phải giảm thời gian truy vấn ít nhất 30%. M4 là phát hiện dị thường, phải đúng chiều với ba sự kiện đã chọn trước. M5 là dashboard chạy không lỗi.

Cuối bài nhóm sẽ đối chiếu lại từng mục này.

Năm nguồn dữ liệu cụ thể như sau.

**[8] Nguồn dữ liệu và đặc trưng dữ liệu lớn (1:00)**

Năm nguồn khác nhau ngay từ cấu trúc. ERA5 là lưới. GHCN và ISD là chuỗi tại trạm. NASA POWER và Open-Meteo là điểm, truy vấn qua API. Độ phân giải cũng khác: từ 30 phút tới một ngày.

Về đặc trưng dữ liệu lớn: dữ liệu thô 23,4 GB, phần lớn là ERA5. Sau tích hợp còn 303 MB Parquet, gần 9 triệu bản ghi. Variety là ba dạng cấu trúc và ba định dạng.

Velocity thì em nói rõ: đây là dữ liệu lịch sử. Nhóm mô phỏng luồng bằng cách phát lại qua Kafka vào Spark Structured Streaming.

Veracity là phần thiếu, sai, lệch giữa các nguồn, em trình bày kỹ ở phần 3.

*Số dòng ERA5 trên bảng là sau khi nội suy vào 113 trạm, không phải số ô lưới gốc.*

Các nguồn này đi qua hệ thống theo kiến trúc sau.

**[9] Kiến trúc tổng thể (1:00)**

Dữ liệu đi từ trái sang phải.

Năm nguồn vào tầng Ingestion. Ở đây dữ liệu được parse, chuẩn hoá và chạy QC. ERA5 được nội suy vào toạ độ trạm.

Sau đó dữ liệu ánh xạ vào lược đồ chung WeatherObs theo GAV, rồi ghi vào kho Parquet, chia partition theo năm và nguồn.

Từ kho, các bước phía sau cùng đọc chung: Entity Resolution, Survivorship, phát hiện dị thường, PINN. Kafka phát lại dữ liệu cho Spark Streaming. Cuối cùng là dashboard.

Phần quan trọng nhất là tầng đầu tiên: dữ liệu thô có vấn đề gì và phải xử lý ra sao.

---

## Phần 3. Đặc trưng dữ liệu và yêu cầu xử lý (6:30)

**[10–11] Tổng quan đặc trưng và yêu cầu xử lý (1:00)**

Nhóm đo các vấn đề trực tiếp trên dữ liệu thật và chia làm sáu nhóm.

Thiếu dữ liệu. Giá trị ngoài khoảng và giá trị sai. Đơn vị đo khác nhau. Khác nhau về ngữ nghĩa, tức là trùng tên nhưng khác đại lượng. Khác nhau về thời gian. Và khác nhau về không gian, định danh.

Cột giữa là số đo được, cột phải là yêu cầu xử lý. Em đi lần lượt từng nhóm.

*Cô quan tâm phần này nhất. Nói chậm, rõ, đừng cắt dù thiếu giờ.*

Đầu tiên là dữ liệu thiếu.

**[12] Dữ liệu thiếu (1:15)**

Nhóm tách thiếu làm hai loại.

Loại thứ nhất là nguồn không đo biến đó. Các ô 100% màu đỏ là như vậy. GHCN không đo độ ẩm, gió, áp suất. ISD trong dữ liệu đã tải không có mưa. Cái này không phải lỗi, không được bịa số.

Loại thứ hai là có đo nhưng mất số liệu. GHCN trung vị đủ 91,3% số ngày, trạm tệ nhất chỉ còn 46,5%.

Có một điểm dễ sai là mưa. GHCN chỉ có số liệu mưa ở 58,7% số ngày. Ngày không báo cáo khác hẳn ngày không mưa.

Yêu cầu xử lý: mọi mã thiếu, 99999, −999, null, đều đổi thành NULL. Không điền 0, không điền trung bình. Khi tổng hợp phải đủ dữ liệu mới tính, ví dụ tháng mưa phải có ít nhất 90% số ngày.

Nhóm đã từng vi phạm: thay NULL bằng 0 trước khi tính tương quan, ra tương quan giả 0,57 giữa gió và độ ẩm.

Có số liệu rồi thì câu hỏi tiếp theo là số liệu đó có đúng không.

**[13] Giá trị ngoài khoảng và giá trị sai (1:15)**

Nhóm kiểm tra theo bảy tầng, từ đơn giản đến phức tạp.

Tầng 1 đọc cờ QC của chính NOAA. 406 giá trị GHCN và 3.255 giá trị ISD bị NOAA gắn cờ lỗi, nhóm đặt chúng thành NULL.

Tầng 2 là giới hạn vật lý, ví dụ gió không quá 75 m/s. Có hai bản tin gió 83 m/s, nhưng NOAA đã gắn cờ từ trước.

Tầng 4 bắt bước nhảy, ví dụ nhiệt độ đổi hơn 10 độ trong một giờ. Có 36 điểm như vậy.

Bốn tầng đầu chạy ngay khi nạp. Ba tầng sau cần dữ liệu đã tích hợp: IQR, đối chứng với ERA5 và trạm lân cận, và phát hiện trôi cảm biến.

Nguyên tắc chung là gắn cờ, không xoá bản ghi, để bước sau còn truy lại được.

Ví dụ Phnom Penh: giá trị đã qua QC của NOAA vẫn nhảy 25 hPa trong 3 giờ. Chỉ tầng 4, 6 và 7 mới bắt được.

Giá trị đúng rồi, nhưng mỗi nguồn lại ghi bằng một đơn vị khác nhau.

**[14] Đơn vị đo không đồng nhất (1:00)**

Bảng này là đơn vị thật của từng nguồn.

Nhiệt độ: GHCN và ISD ghi phần mười độ C, ERA5 ghi Kelvin. Áp suất: ERA5 dùng Pa, NASA POWER dùng kPa. Gió: Open-Meteo dùng km/h, ERA5 lại tách thành hai thành phần u, v.

Độ ẩm thì ISD không có sẵn, nhóm tính từ điểm sương theo phương trình Clausius–Clapeyron.

Yêu cầu là đọc đơn vị từ metadata của nguồn, không tự giả định, và mỗi phép đổi có test. Lỗi km/h ở phần đặt vấn đề chính là do lúc đầu nhóm tự giả định đơn vị.

Khó hơn đơn vị là trường hợp cùng tên biến nhưng thực ra là hai đại lượng khác nhau.

**[15] Không đồng nhất về ngữ nghĩa và thời gian (1:00)**

Ví dụ gió: NASA POWER mặc định đo ở độ cao 2 mét, các nguồn khác đo ở 10 mét. Gió 2 mét chỉ bằng 0,65 lần. Nhóm tải biến gió 10 mét của NASA.

Nhiệt độ ngày có ba cách tính. TAVG của GHCN thấp hơn trung bình max–min khoảng 0,25 độ. Nhóm ghi cách tính vào cột temp_def.

Áp suất bề mặt và áp suất mực biển là hai đại lượng khác nhau, lệch khoảng 12 hPa mỗi 100 mét độ cao. Hai cột này giữ riêng.

Về thời gian, mọi nguồn chuẩn hoá về UTC.

Còn một việc nhóm chưa xử lý: ngày của GHCN là ngày giờ địa phương, lệch 7–8 tiếng so với UTC. Khi so với ERA5 theo ngày thì có độ lệch này.

Nhóm cuối là khác nhau về không gian: lưới ERA5 và điểm trạm.

**[16] Không đồng nhất về không gian (1:00)**

ERA5 là lưới 0,25 độ, khoảng 28 km. Nhóm nội suy Bilinear vào toạ độ từng trạm, rồi so với số đo thật cùng ngày: hơn 108 nghìn cặp.

Nhiệt độ sai khoảng 1,1 độ, gió khoảng 1 m/s, chấp nhận được. Mưa thì sai gần 20 mm, kém.

Trạm càng cao thì nhiệt độ càng lệch, vì lưới 0,25 độ không thể hiện được địa hình.

Hạn chế nhóm ghi nhận: khi trạm thiếu số liệu mưa, giá trị lấy từ ERA5 có sai số lớn.

Còn vấn đề cùng một trạm có hai mã GHCN và ISD, Lương sẽ trình bày ở phần tích hợp.

Dữ liệu đã sạch và cùng đơn vị. Lương trình bày cách đưa năm nguồn về một kho.

---

## Phần 4. Tích hợp dữ liệu (3:00)

**[17–18] Mediated Schema và ánh xạ GAV (1:00)**

*Chuyển người nói: Lương.*

Em là Lương, em trình bày phần tích hợp.

Nhóm định nghĩa một lược đồ trung gian là WeatherObs: vị trí, thời gian UTC, nguồn, các biến khí tượng, cùng hai cột temp_def và qc_flag từ bước xử lý.

Mỗi nguồn được viết thành một view vào lược đồ này, tức là Global-as-View. Ví dụ NASA POWER: T2M ánh xạ vào temp_c.

Hai nguồn cần biến đổi trước. GHCN ở dạng long, mỗi dòng một biến, nên phải PIVOT. ISD gói giá trị và mã QC trong một trường, nên phải PARSE.

Nhóm chọn GAV vì có đúng năm nguồn cố định. Trả lời truy vấn chỉ cần khai triển view, không phải viết lại truy vấn như LAV.

Lược đồ chung rồi, nhưng GHCN và ISD vẫn gọi cùng một trạm bằng hai mã khác nhau.

**[19] Entity Resolution GHCN và ISD (1:00)**

GHCN và ISD không có mã chung. Nhóm ghép theo khoảng cách: với mỗi trạm ISD, tìm trạm GHCN gần nhất theo khoảng cách Haversine, ngưỡng 5 km.

Kết quả ghép được 22 trên 26 trạm. Nhiều cặp cách nhau đúng 0 km, vì hai cơ quan dùng chung toạ độ WMO gốc.

Để kiểm chứng, nhóm dùng mã WMO làm nhãn độc lập. Có 15 cặp có nhãn, precision và recall đều 100%.

Số trạm nhỏ nên nhóm so toàn bộ cặp, chưa cần bước blocking.

Khi đã biết hai bản ghi là cùng một trạm, câu hỏi tiếp theo là hai nguồn lệch nhau thì lấy giá trị nào.

**[20] Hợp giải giá trị giữa các nguồn, Survivorship (1:00)**

Với mỗi vị trí, mỗi ngày, nếu nhiều nguồn cùng có giá trị thì lấy nguồn hạng cao nhất. Trạm đo trực tiếp đứng đầu, rồi đến ERA5, Open-Meteo, NASA POWER.

Nếu các nguồn lệch quá ngưỡng thì gắn cờ xung đột. Ngưỡng đặt riêng cho từng biến, ví dụ nhiệt độ 10%, mưa 50%, vì mưa tự nhiên đã biến động mạnh.

Bảng bên phải là tỷ lệ xung đột đo được. Áp suất mực biển gần như không lệch, 0%. Mưa lệch tới 91,6%, vì mỗi nguồn tích luỹ mưa theo chu kỳ khác nhau.

Kết quả là bảng hợp giải 856 nghìn dòng, mỗi vị trí mỗi ngày một dòng, ghi rõ giá trị lấy từ nguồn nào.

Phần tiếp theo, Nghĩa trình bày xử lý và phân tích trên kho này.

---

## Phần 5. Xử lý và phân tích (5:15)

**[21–22] Tối ưu Spark (1:00)**

*Chuyển người nói: Nghĩa.*

Em là Nghĩa. Mục tiêu M3 là tối ưu Spark.

Với truy vấn tổng hợp nhiệt độ theo trạm và tháng, cache() giảm thời gian từ 0,36 giây xuống 0,11 giây, tức giảm 69,4%, vượt ngưỡng 30%.

Nhóm cũng thử partition thêm theo tháng. Data skew giảm rõ, nhưng số partition tăng từ 109 lên hơn 1.300.

Đo lại thì ở quy mô 9 triệu bản ghi, partition còn chậm hơn không partition, vì Parquet đã tự bỏ qua dữ liệu không liên quan. Nhóm vẫn giữ partition theo năm và nguồn, vì lợi ích sẽ rõ khi dữ liệu lớn hơn hoặc nằm trên S3.

Kho đã truy vấn được, giờ là ứng dụng chính: phát hiện dị thường khí hậu.

**[23] Đối chứng với ba sự kiện đã biết (1:00)**

Dị thường được đo bằng z: lấy giá trị trừ khí hậu nền rồi chia cho độ lệch chuẩn. Khí hậu nền tính từ GHCN giai đoạn 1991–2020, theo từng ngày trong năm.

Ba sự kiện được chọn từ trước. Nắng nóng tháng 4–5/2024: 12,3% số ngày có z từ 2 trở lên, gấp 10 lần bình thường. Bão Yagi: áp suất ERA5 ở Hải Phòng xuống 978,8 hPa, đúng nơi bão đổ bộ.

Hạn Mekong thì tín hiệu yếu: đúng chiều, nhưng chỉ 2 trạm có số liệu SPI đúng vùng và giai đoạn. Nhóm báo cáo đúng như vậy.

Một giá trị z cao có thể là nóng thật, cũng có thể là cảm biến hỏng. Nhóm tách hai trường hợp này như sau.

**[24] Đối chứng bằng ERA5 và trạm lân cận (1:00)**

Với mỗi giá trị cực đoan ở trạm, nhóm xem ERA5 cùng vị trí và các trạm trong bán kính 200 km có cùng chiều không.

Cùng chiều thì là dị thường khí hậu thật. Trạm cực đoan mà đối chứng ngược chiều thì nghi lỗi dữ liệu.

Chỉ dùng ERA5 thì xác nhận được 5.380 ca. Thêm trạm lân cận thì lên 20.357, vì trạm lân cận phủ được cả giai đoạn trước 2020 khi chưa có ERA5. 343 ca bị đánh dấu nghi lỗi dữ liệu.

Trạm cách nhau dưới 5 km thì không dùng làm đối chứng, vì theo Entity Resolution đó là cùng một trạm.

Các phép tính này chạy bằng batch. Nhóm kiểm tra xem làm theo luồng có ra cùng kết quả không.

**[25] Phát hiện dị thường theo luồng (1:00)**

Cụm gồm một master, hai worker và Kafka một broker, chạy trên một máy.

Producer phát lại đợt nắng nóng 2024 vào Kafka. Spark Structured Streaming đọc từng micro-batch, join với bảng khí hậu nền đã tính bằng batch, rồi cảnh báo khi trị tuyệt đối của z từ 2 trở lên.

Kết quả 179 cảnh báo, khớp đủ 179 với kết quả batch, giá trị z giống hệt.

Cảnh báo cao nhất là ngày 30/4/2024, một trạm Thái Lan 38,6 độ, cao hơn nền hơn 8 độ.

Ngoài thống kê, nhóm thử một mô hình học máy có ràng buộc vật lý cho trường gió.

**[26] PINN cho trường gió (0:45)**

Mục đích là làm mịn trường gió giữa lưới ERA5 và trạm, có thêm ràng buộc vật lý là phương trình liên tục.

λ là trọng số của ràng buộc vật lý; λ bằng 0 là hồi quy thuần. Baseline có RMSE tốt nhất. PINN với λ 0,1 tốt hơn một chút về MAE. Chênh lệch khoảng 1%, trên 22 trạm kiểm tra, nên nhóm chưa kết luận mô hình nào tốt hơn.

Lý do có thể là nhóm mới có một thời điểm, trong khi ràng buộc vật lý cần chuỗi thời gian.

Kết quả của các phần trên được gom lại trên dashboard.

**[27] Dashboard (0:30)**

Dashboard viết bằng Streamlit, 10 panel, đọc trực tiếp từ kho Parquet. Đây là panel dị thường khí hậu: tỷ lệ ngày nóng bất thường, đợt nóng dài nhất 30 ngày, năm 2024 cao hẳn các năm khác.

Nhóm kiểm tra cả 10 panel trên trình duyệt, không có lỗi runtime.

Em tổng kết lại theo năm mục tiêu ban đầu.

---

## Kết luận (1:30)

**[28–29] Kết quả theo mục tiêu (0:45)**

Đối chiếu với năm mục tiêu: M1 đủ năm nguồn, đúng phạm vi. M2 có toàn vẹn tham chiếu 100%, Entity Resolution đúng trên 15 cặp có nhãn, bảng hợp giải 856 nghìn dòng. M3 giảm 69,4%, vượt ngưỡng. M5 dashboard không lỗi.

M4 nhóm đánh giá là đạt một phần, vì hạn Mekong chỉ có tín hiệu yếu.

Hệ thống có 83 test tự động, gồm cả test chạy với Spark và Kafka.

Cuối cùng là những gì nhóm chưa làm được.

**[30–31] Kết luận và hướng phát triển (0:45)**

Nhóm đã có kho gần 9 triệu bản ghi từ năm nguồn. Dữ liệu được xử lý thiếu, sai, đơn vị, ngữ nghĩa ngay từ đầu pipeline, rồi tích hợp bằng GAV, Entity Resolution và Survivorship.

Hạn chế: ngày GHCN chưa căn theo giờ địa phương; trôi cảm biến mới phát hiện, chưa hiệu chỉnh; hạ tầng chạy trên một máy; mưa lấy từ ERA5 còn sai số lớn.

Hướng tiếp theo đi đúng vào các hạn chế đó. Em xin cảm ơn cô, nhóm sẵn sàng trả lời câu hỏi.

---

## Hỏi đáp: câu hỏi dễ gặp và gợi ý trả lời

1. **Dữ liệu thiếu xử lý thế nào? Sao không nội suy hay điền trung bình?**
   Nhóm giữ NULL, không điền. Lý do: phần lớn chỗ thiếu là do nguồn không đo biến đó (GHCN không đo gió, độ ẩm), điền vào là bịa số. Chỗ thiếu thật thì chọn nguồn khác qua Survivorship. Khi tổng hợp phải đủ ngưỡng: tháng mưa ≥ 90% số ngày, năm nhiệt độ ≥ 80%. Nhóm từng thay NULL bằng 0 và ra tương quan giả 0,57. Slide 12.

2. **Thiếu mưa và mưa bằng 0 khác nhau thế nào, xử lý ra sao?**
   GHCN chỉ có số liệu mưa ở 58,7% số ngày; trong số đó 57,1% là 0 mm. Ngày không báo cáo giữ NULL, ngày 0 mm giữ 0. Mưa không nội suy. SPI và tổng mưa tháng chỉ tính khi tháng đủ 90% số ngày.

3. **Ngưỡng giới hạn vật lý (−10…50 °C, gió 0…75 m/s…) lấy ở đâu? Có loại nhầm dữ liệu cực đoan thật không?**
   Ngưỡng đặt rộng, chỉ để bắt giá trị không thể xảy ra, không phải để bắt cực đoan. Kiểm chứng: sau tầng 1 (cờ QC của NOAA) thì 0 giá trị vi phạm, kể cả trong đợt nắng nóng và bão Yagi. Cực đoan thật được xử lý ở tầng sau bằng đối chứng, không phải bằng ngưỡng. Slide 13.

4. **Vì sao gắn cờ chứ không xoá bản ghi lỗi?**
   Để truy vết được (provenance) và để bước sau tự quyết. Giá trị lỗi được đặt NULL, lý do ghi vào qc_flag (ví dụ ISD_QC:SLP=2, JUMP:temp_c), còn bản ghi vẫn giữ các biến khác đúng.

5. **Vì sao IQR mà không dùng Z-score để phát hiện outlier?**
   Z-score bị "masking": chính outlier làm độ lệch chuẩn phình ra. Thử trên dữ liệu mô phỏng N(25,2) với 5 outlier, std từ 2,0 lên 72,2, Z-score chỉ bắt 1/5, IQR bắt 5/5.

6. **Phát hiện dị thường lại dùng z-score, có mâu thuẫn với câu trên không?**
   Hai việc khác nhau. IQR dùng cho chất lượng dữ liệu trên chuỗi thô có thể lẫn lỗi. z ở phần dị thường tính so với khí hậu nền 1991–2020 theo ngày trong năm, trên dữ liệu đã qua QC; mục đích là đo một ngày lệch bao nhiêu so với bình thường, không phải tìm lỗi.

7. **Đơn vị: làm sao đảm bảo đổi đúng? Nếu nguồn đổi đơn vị thì sao?**
   Đọc đơn vị từ metadata của nguồn (hourly_units của Open-Meteo, fill_value của NASA POWER, thuộc tính NetCDF của ERA5) chứ không viết cứng; mỗi phép đổi có test. Nếu metadata không đổi theo thì test sẽ không bắt được; đây là phần schema drift nhóm chưa xử lý đầy đủ.

8. **Ranh giới ngày GHCN chưa xử lý thì ảnh hưởng thế nào?**
   Ngày GHCN là ngày địa phương, lệch 7–8 giờ so với ngày UTC của ERA5. Ảnh hưởng nhiều nhất là mưa, vì mưa tích luỹ theo cửa sổ 24 giờ; đây là một phần lý do xung đột mưa cao. Nhóm ghi rõ là hạn chế.

9. **Trôi cảm biến phát hiện thế nào? Sao chưa hiệu chỉnh?**
   Lấy chuỗi chênh lệch trạm − ERA5 theo tháng. Trôi dần dùng Mann-Kendall và độ dốc Sen, nhảy bậc dùng Pettitt. Gắn cờ 4/80 chuỗi, rõ nhất là áp suất Phnom Penh nhảy −2,6 hPa từ 11/2022. Tiêm lỗi nhân tạo vào 76 chuỗi ổn định: bắt 100% ca trôi, 95–98% ca nhảy bậc. Hiệu chỉnh cần hồ sơ lịch sử trạm để biết nguyên nhân, nhóm chưa có.

10. **Vì sao chọn GAV mà không phải LAV?**
    Có đúng 5 nguồn cố định, mỗi nguồn ánh xạ vào WeatherObs bằng một view. GAV trả lời truy vấn chỉ cần khai triển view. Đổi lại, thêm nguồn mới phải sửa định nghĩa view; với 5 nguồn cố định thì chấp nhận được.

11. **Vì sao chọn data warehouse mà không tích hợp ảo (virtual)?**
    Nguồn chậm và không ổn định: hàng đợi CDS có lúc chờ hơn 1 giờ, ERA5 thô 22 GB. Phân tích dị thường quét 977 nghìn ngày-trạm và lặp nhiều lần. Dữ liệu lịch sử, không cần cập nhật tức thời. Nên vật chất hoá vào kho rồi tính là hợp lý.

12. **Entity Resolution chỉ dựa trên khoảng cách có đủ không? Precision/recall 100% trên 15 cặp có đáng tin?**
    Với trạm khí tượng, toạ độ là thuộc tính mạnh nhất: nhiều cặp trùng đúng 0 km. Nhưng 15 cặp có nhãn là mẫu nhỏ; 7/22 cặp tìm được không có mã WMO để kiểm chứng độc lập. Nhóm nói rõ đây là giới hạn.

13. **Sao không dùng blocking?**
    Chỉ 26 × 41 = 1.066 cặp, so hết còn nhanh. Blocking (ví dụ LSH) cần khi lên toàn cầu: GHCN hơn 14.000 trạm thì số cặp lên hàng trăm triệu.

14. **Hạng nguồn trong Survivorship dựa vào đâu? Ngưỡng xung đột chọn thế nào?**
    Trạm đo trực tiếp và có cờ QC nên hạng 1; ERA5 có đồng hoá số liệu quan trắc; Open-Meteo nội suy lại từ ERA5; NASA POWER lưới thô nhất 0,5°. Ngưỡng đặt trước theo biên độ tự nhiên của từng biến: áp suất 2%, nhiệt độ 10%, mưa 50%.

15. **Mưa xung đột 91,6% thì giá trị mưa trong kho có dùng được không?**
    Xung đột cao chủ yếu vì mỗi nguồn tích luỹ mưa theo cửa sổ khác nhau, cộng với lệch ranh giới ngày GHCN. Giá trị lấy theo hạng nguồn và có cờ xung đột để người dùng biết. Các phân tích mưa trên slide tính theo từng nguồn, không gộp mù quáng.

16. **Kho chỉ 303 MB, vừa RAM một máy, sao gọi là dữ liệu lớn và cần Spark?**
    Đúng, kho sau tích hợp nhỏ. Volume nằm ở bước nạp: ERA5 thô 22 GB, nếu lấy qua kênh ARCO phải tải khoảng 1 TB. Nhóm đo thẳng: ở quy mô này DuckDB nhanh hơn Spark 7,3–8,4 lần. Spark dùng để có pipeline mở rộng được cho toàn bộ lưới ERA5, không phải vì kho hiện tại vượt RAM.

17. **Velocity: dữ liệu lịch sử thì streaming có ý nghĩa gì?**
    Nhóm nói rõ là mô phỏng: phát lại dữ liệu theo thứ tự thời gian qua Kafka. Giá trị là chứng minh pipeline streaming cho kết quả đúng bằng batch, 179/179 cảnh báo khớp.

18. **69,4% đo thế nào? Có công bằng không?**
    Cùng một truy vấn, trung bình 3 lần chạy, so với và không có cache(). Hạn chế: AQE của Spark 4 để mặc định, có tự gộp shuffle partition, nhóm chưa tách riêng ảnh hưởng này.

19. **Partition chậm hơn không partition sao vẫn giữ?**
    Ở 9 triệu bản ghi trên ổ cục bộ, Parquet đã bỏ qua dữ liệu nhờ thống kê min/max của row-group, nên partition không giúp được thêm. Partition pruning có lợi khi dữ liệu lớn hơn nhiều hoặc nằm trên S3/GCS.

20. **Khí hậu nền chỉ từ GHCN 1991–2020, các nguồn ngắn hơn thì sao?**
    Tỷ lệ ngày z ≥ 2 trên slide tính trên 34 trạm GHCN với nền 1991–2020. ERA5 và ISD chỉ có 5–10 năm, ngắn hơn chuẩn 30 năm của WMO; nhóm ghi đây là giới hạn, cùng với 15.938 ca chưa có đối chứng.

21. **Ngưỡng |z| ≥ 2 có phải tuỳ tiện không?**
    z ≥ 2 nghĩa là lệch hơn 2 độ lệch chuẩn so với bình thường, cỡ 2–3% số ngày nếu phân bố gần chuẩn. Nền 1991–2020 đo được 1,2% số ngày, năm 2024 lên 11,2%. Đợt nóng dùng chỉ số TG90p theo chuẩn ETCCDI.

22. **PINN không tốt hơn baseline thì đưa vào làm gì?**
    Báo cáo đúng kết quả. Chênh lệch khoảng 1% trên 22 trạm, một seed, chưa đủ kết luận. Physics loss giảm mạnh khi tăng λ (0,53 xuống 0,011), tức trường gió dự đoán thoả ràng buộc vật lý hơn.

23. **Bilinear sao không dùng Kriging?**
    Kriging cần ước lượng variogram, đòi hỏi trạm đủ dày; 113 trạm trên 9 nước là thưa. Bilinear đã kiểm chứng RMSE nhiệt độ 1,14 °C trên 108.542 cặp.

24. **Mỗi người làm phần nào?**
    Quang: thu thập 5 nguồn, QC, sửa lỗi pipeline. Lương: Mediated Schema, Entity Resolution, Survivorship. Nghĩa: môi trường Spark/Docker, Kafka, streaming, PINN, tối ưu, dashboard.

25. **Có demo được không?**
    Theo thông báo 15/11 thì không demo trực tiếp trong bài. Cụm Docker và pytest chạy được ngay nếu cô yêu cầu xem.

*Còn 7 câu nữa (áp suất mực biển ISD, trùng lặp ISD, gió 2m→10m, Open-Meteo không độc lập, provenance, Kafka 1 broker, số liệu trùng tên): xem đầy đủ trong `hoi-dap-bao-ve.md`.*

## Số cần nhớ

- Kho: 5 nguồn, 8.955.313 dòng (gần 9 triệu); dữ liệu thô 23,4 GB → 303 MB Parquet sau tích hợp.
- ERA5: đủ 540/540 file CDS; nội suy Bilinear vào 113 trạm, RMSE nhiệt độ 1,14 °C, gió 1,05 m/s, mưa 19,83 mm trên hơn 108.542 cặp.
- Entity Resolution: 22/26 trạm GHCN–ISD khớp, ngưỡng Haversine 5 km; precision/recall 100%/100% trên 15 cặp có nhãn WMO độc lập.
- Survivorship: bảng hợp giải 856.452 dòng; xung đột theo biến từ 0% (áp suất mực biển) tới 91,6% (mưa).
- Tối ưu Spark: cache() giảm 69,4% thời gian truy vấn (0,36s → 0,11s), vượt ngưỡng mục tiêu 30%.
- Dị thường khí hậu: năm 2024 có 11,2% số ngày z ≥ 2 (nền 1991–2020 chỉ 1,2%); đối chứng ERA5 + trạm lân cận xác nhận 20.357 ca (chỉ ERA5 là 5.380), 343 ca nghi lỗi dữ liệu.
- Ba sự kiện đối chứng: nắng nóng 4–5/2024 (12,3% ngày z ≥ 2), bão Yagi (ERA5 Hải Phòng 978,8 hPa), hạn Mekong (tín hiệu yếu, chỉ 2 trạm SPI).
- Kafka + Spark Streaming: 179/179 cảnh báo khớp đúng kết quả tính bằng batch.
- PINN: chênh lệch RMSE khoảng 1% so với baseline trên 22 trạm, một seed, chưa đủ kết luận mô hình nào tốt hơn.
- Hệ thống: 83 test tự động (gồm test chạy với Spark và Kafka); dashboard Streamlit 10 panel, không lỗi runtime.

## Mẹo khi nói

- Phần 3 (đặc trưng dữ liệu, slide 10–16) là phần cô hỏi nhiều nhất: nói chậm, rõ, đừng cắt dù thiếu giờ.
- Nếu bị nhắc giờ, nói lướt theo thứ tự: slide 8 (chỉ nói Volume và Velocity), slide 16 (chỉ nói RMSE mưa kém), slide 26 PINN ("chưa vượt baseline, chênh 1%, chưa kết luận"), slide 27 Dashboard.
- Mỗi slide chỉ nói đúng 1–2 ý chính trong bảng hay biểu đồ, chỉ tay vào đúng ô số liệu đang nói, đừng đọc nguyên văn chữ trên slide.
- Gặp câu hỏi chưa chắc, trả lời "nhóm chưa làm/chưa kiểm chứng điểm này" thay vì đoán, rồi tra `hoi-dap-bao-ve.md`.
- Câu cuối luôn giữ nguyên: cảm ơn cô và nói rõ nhóm sẵn sàng trả lời câu hỏi.
