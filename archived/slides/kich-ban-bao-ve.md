# Kịch bản thuyết trình: Tích hợp dữ liệu khí tượng đa nguồn Đông Nam Á

**Người nghe:** hội đồng IT5427 (cô Vũ Tuyết Trinh). **Mục đích:** bảo vệ project cuối kỳ (60% điểm).
**Thời lượng:** 30 phút gồm cả hỏi đáp. Bài chính khoảng 20 phút, để lại khoảng 10 phút hỏi đáp.
**Slide:** `final-defense.pdf`, bài chính trang 1–34, Phụ lục trang 35–66 (chỉ mở khi bị hỏi).

**Cô quan tâm nhất:** dữ liệu thu thập có đặc trưng gì, yêu cầu xử lý gì (thiếu, ngoài khoảng, đơn vị không đồng
nhất…), và đặc biệt — theo đúng kiểu cô hỏi nhóm 15 — **ghép dữ liệu giữa các nguồn có dựa vào giả định không,
hay có bằng chứng (khoá, log đối chiếu) chứng minh khớp**. Phần 3 trả lời thẳng câu đầu; mục G trong
`hoi-dap-bao-ve.md` trả lời thẳng câu thứ hai. Đừng nói vội phần 3.

**Mở nhanh khi trình bày (1 lệnh):** nếu cô yêu cầu "mở code ra xem" hoặc xem dashboard, chạy ngay
`bash scripts/mo_demo_bao_ve.sh` từ thư mục gốc repo — mở sẵn slide PDF, 7 file source chính theo đúng thứ tự
pipeline (Entity Resolution → Survivorship → Warehouse → Anomaly → PINN → parser → dashboard) trong VS Code, và
chạy luôn Dashboard Streamlit tại `localhost:8501`.

**Chia người nói:**

| Phần | Nội dung | Người nói | Slide (trang) | Thời lượng |
|---|---|---|---|---|
| 0 | Mở đầu | Quang | 1–2 | 0:30 |
| 1 | Đặt vấn đề | Quang | 3–5 | 2:00 |
| 2 | Mục tiêu, dữ liệu và kiến trúc | Quang | 6–9 | 3:00 |
| 3 | Đặc trưng dữ liệu và yêu cầu xử lý | Quang | 10–16 | 6:30 |
| 4 | Tích hợp dữ liệu | Lương | 17–20 | 3:00 |
| 5 | Xử lý và phân tích | Nghĩa | 21–30 | 7:30 |
| 6 | Kết luận | Nghĩa | 31–34 | 1:30 |
| | **Tổng bài chính** | | **34 trang** | **khoảng 24:00** |

Quang: 11:30 (slide 1–16). Lương: 3:00 (slide 17–20). Nghĩa: 9:00 (slide 21–34).

**Phụ lục (trang 35–66), ai hiểu chính/hiểu phụ nếu hội đồng hỏi** — người hiểu chính trả lời trước, người hiểu
phụ chỉ bổ sung nếu được hỏi thêm hoặc người chính trả lời chưa đủ. Lời nói gợi ý cho từng trang nằm trong mục
"Phụ lục: lời nói gợi ý từng trang" ở cuối file (cũng in sẵn trong `final-defense-notes.pdf`, cột bên phải mỗi
trang phụ lục):

| Trang | Nội dung | Hiểu chính | Hiểu phụ |
|---|---|---|---|
| 36 | Dữ liệu nằm ở năm nguồn khác nhau | Quang | Lương |
| 37 | Năm nguồn dữ liệu | Quang | Nghĩa |
| 38 | Vùng nghiên cứu | Quang | Lương |
| 39 | Quy mô kho sau tích hợp | Quang | Nghĩa |
| 40 | Dữ liệu thô trước chuẩn hoá | Lương | Quang |
| 41 | Tải dữ liệu theo phạm vi đề cương | Quang | Nghĩa |
| 42 | Tỷ lệ dữ liệu bị QC can thiệp | Quang | Lương |
| 43 | Chọn IQR thay cho Z-score | Lương | Quang |
| 44 | Lỗi số liệu trong pipeline | Quang | Nghĩa |
| 45 | Chiến lược partition | Nghĩa | Quang |
| 46 | Cụm Spark và Kafka | Nghĩa | Lương |
| 47 | Mưa cực đoan khi bão Yagi | Nghĩa | Lương |
| 48 | Xu hướng nhiệt độ dài hạn | Nghĩa | Lương |
| 49 | Phát hiện trôi cảm biến | Lương | Nghĩa |
| 50 | Tương quan và PCA | Lương | Nghĩa |
| 51 | Các panel của dashboard | Nghĩa | Lương |
| 52 | Panel 1: tổng quan tích hợp | Nghĩa | Quang |
| 53 | Tiến độ theo từng người | Nghĩa | Quang |
| 54 | Sản phẩm của từng người theo mốc | Nghĩa | Lương |
| 55 | Giới hạn hạ tầng | Nghĩa | Lương |
| 56 | Mở rộng ra toàn cầu | Nghĩa | Lương |
| 57 | Kiến trúc PINN và huấn luyện | Nghĩa | Lương |
| 58 | Các loại dị thường khí hậu và bảng xu hướng | Nghĩa | Lương |
| 59 | Ghép theo khoá, không theo thứ tự mảng | Lương | Quang |
| 60 | Trường dữ liệu và độ phân giải theo từng nguồn | Quang | Lương |
| 61 | Chuỗi ngày tại trạm kèm các điểm dị thường | Nghĩa | Lương |
| 62 | Đợt nóng và hạn SPI-3 trong 2020–2024 | Nghĩa | Quang |
| 63 | Mưa cực đoan theo nước (R95pTOT) | Nghĩa | Quang |
| 64 | Mật độ trạm đo lỗi dữ liệu 2020–2024 | Quang | Nghĩa |
| 65 | Fellegi–Sunter và luật phủ quyết | Lương | Nghĩa |
| 66 | Liên kết trạm với lưới ERA5, không gộp | Lương | Nghĩa |

Trang 35 chỉ là trang ngăn mục, không cần ai giải thích riêng. "Hiểu chính" ưu tiên người thật sự làm ra nội
dung đó (Quang: ingestion/QC; Lương: schema/ER/Survivorship; Nghĩa: Spark/Kafka/PINN/dashboard), không nhất
thiết trùng người đang nói phần chính tương ứng.

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

"Bước 1/3" (thanh điều hướng 3 bước ở đầu mỗi slide Phần 4). Lược đồ `WeatherObs(...)`; ví dụ PIVOT GHCN
(48820|7/9|TMAX|317 → 1 dòng), PARSE ISD (TMP="+0250,1" → nhiệt độ 25,0°C); chọn GAV vì số nguồn cố định. Toàn
vẹn tham chiếu 100%.

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

"Bước 2/3". Ví dụ cụ thể: trạm Nội Bài có GHCN VMM00048820 và ISD 48820099999 — máy tính thấy 2 trạm khác nhau.
22/26 cặp khớp, khoảng cách trung bình 0,53 km; láng giềng gần nhất Haversine ngưỡng 5 km; precision/recall
100%/100% trên 15 cặp có nhãn.

**Lời nói**
> GHCN và ISD không có mã chung. Ví dụ trạm Nội Bài: GHCN ghi VMM00048820, ISD ghi 48820099999, máy tính thấy đây là
> hai trạm riêng biệt. Nhóm ghép theo khoảng cách: với mỗi trạm ISD, tìm trạm GHCN gần nhất theo khoảng cách
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

"Bước 3/3", chia 3 cột: (1) hạng nguồn ISD/GHCN > ERA5 > Open-Meteo > NASA POWER; (2) ví dụ thật Hà Nội 7/9/2024
(bão Yagi) — nhiệt độ lấy từ GHCN (hạng 1 có số liệu), mưa và áp suất lấy từ ERA5 (vì GHCN thiếu, tụt xuống hạng
2); (3) bảng ngưỡng gắn cờ theo biến. Bảng hợp giải 856.452 dòng.

**Lời nói**
> Với mỗi vị trí, mỗi ngày, nếu nhiều nguồn cùng có giá trị thì lấy nguồn hạng cao nhất. Trạm đo trực tiếp đứng đầu,
> rồi đến ERA5, Open-Meteo, NASA POWER.
>
> Ví dụ thật ngày bão Yagi, 7/9/2024 tại Hà Nội: nhiệt độ 25,9 độ lấy từ GHCN vì hạng 1 có số liệu; nhưng mưa và áp
> suất GHCN lại thiếu, nên tụt xuống lấy từ ERA5, hạng 2. Ngày này không biến nào bị gắn cờ xung đột.
>
> Nếu các nguồn lệch quá ngưỡng thì gắn cờ xung đột. Ngưỡng đặt riêng cho từng biến, ví dụ nhiệt độ 10%, mưa 50%,
> vì mưa tự nhiên đã biến động mạnh.
>
> Kết quả là bảng hợp giải 856 nghìn dòng, mỗi vị trí mỗi ngày một dòng, ghi rõ giá trị lấy từ nguồn nào. Mưa là
> biến xung đột nhiều nhất, tới 91,6%, vì mỗi nguồn tích luỹ mưa theo chu kỳ khác nhau — chi tiết đủ 6 biến có
> trong báo cáo nếu cô hỏi thêm.

**Chuyển ý**
> Phần tiếp theo, Nghĩa trình bày xử lý và phân tích trên kho này.

---

# Phần 5. Xử lý và phân tích

## 5.1. Tối ưu Spark: bốn việc đã làm (1 phút)

**Trên slide**

Bảng 4 việc: chọn truy vấn đại diện, cache dữ liệu đã lọc, đo lệch dữ liệu, so sánh có/không chia thư mục.

**Lời nói**
> Em là Nghĩa. Mục tiêu M3 là tối ưu Spark, và nhóm làm bốn việc, mỗi việc đo trước và sau trên cùng một truy vấn,
> chạy 3 lần lấy trung bình.
>
> Một, chọn truy vấn đại diện cho dashboard: lọc GHCN, nhóm theo trạm và tháng, tính nhiệt độ trung bình. Spark quét
> Parquet, đẩy điều kiện lọc xuống tầng đọc, gộp sơ bộ trong từng partition, shuffle theo khoá rồi gộp lần cuối.
>
> Hai, cache dữ liệu đã lọc: EXPLAIN cho thấy bước quét Parquet đổi thành đọc từ bộ nhớ.
>
> Ba, đo lệch dữ liệu bằng cách đếm số dòng mỗi partition khi chia theo năm–nguồn và theo năm–tháng–nguồn.
>
> Bốn, so sánh có và không chia thư mục: chia thì Spark bỏ qua cả thư mục không khớp, không chia thì Parquet vẫn bỏ
> qua từng khối nhờ min/max lưu sẵn. Cấu hình AQE và số partition khi shuffle để mặc định của Spark 4.2.

**Chuyển ý**
> Kết quả đo của bốn việc này ở slide tiếp theo.

## 5.2. Tối ưu Spark (1 phút)

**Trên slide**

`cache()` giảm 69,4% thời gian truy vấn (0,36s → 0,11s); thử partition theo tháng; giữ `year/source`.

**Lời nói**
> Kết quả chính: với truy vấn tổng hợp nhiệt độ theo trạm và tháng, `cache()` giảm thời gian từ 0,36 giây xuống 0,11 giây, tức
> giảm 69,4%, vượt ngưỡng 30%.
>
> Nhóm cũng thử partition thêm theo tháng. Data skew giảm rõ, nhưng số partition tăng từ 109 lên hơn 1.300.
>
> Đo lại thì ở quy mô 9 triệu bản ghi, partition còn chậm hơn không partition, vì Parquet đã tự bỏ qua dữ liệu
> không liên quan. Nhóm vẫn giữ partition theo năm và nguồn, vì lợi ích sẽ rõ khi dữ liệu lớn hơn hoặc nằm trên S3.

**Chuyển ý**
> Kho đã truy vấn được, giờ là ứng dụng chính: phát hiện dị thường khí hậu.

## 5.3. Đối chứng với ba sự kiện đã biết (45 giây)

**Trên slide**

Biểu đồ tỷ lệ ngày z ≥ 2 trong tháng 4–5 theo năm, 2020–2024 (2024: 11,2%); nắng nóng, Yagi, hạn Mekong. Định nghĩa z.

**Lời nói**
> Từ đây nhóm chỉ xét kết quả trong cửa sổ 2020–2024, giai đoạn cả năm nguồn cùng có dữ liệu. Dị thường được đo
> bằng z: lấy giá trị trừ khí hậu nền rồi chia cho độ lệch chuẩn. Khí hậu nền tính từ GHCN 1991–2020, theo từng
> ngày trong năm.
>
> Ba sự kiện được chọn từ trước. Nắng nóng 2024: từ 1/4 đến 15/5 có 12,3% số ngày z từ 2 trở lên, gấp 10 lần cùng
> kỳ. Tính cả tháng 4–5 thì năm 2024 là 11,2%, các năm 2020–2023 chỉ 0,4 đến 4,1%. Bão Yagi: áp suất ERA5 ở Hải
> Phòng xuống 978,8 hPa, z bằng âm 7,2.
>
> Hạn Mekong thì tín hiệu yếu: chỉ phần cuối đợt hạn, tháng 1 đến 5/2020, nằm trong cửa sổ, và chỉ 2 trạm đủ số
> liệu mưa. Đúng chiều nhưng yếu, nhóm báo cáo đúng như vậy.

**Chuyển ý**
> Ba sự kiện là kiểm tra có chọn trước. Bức tranh đầy đủ của cả cửa sổ thì như sau.

## 5.4. Dị thường 2020–2024 theo không gian và thời gian (45 giây)

**Trên slide**

Bản đồ tỉ lệ ngày dị thường tại 119 vị trí; biểu đồ số ca theo tháng, tách nhiệt độ và áp suất; đỉnh 4/2024 và 9/2024.

**Lời nói**
> Trong 2020–2024 hệ thống gắn cờ 22.446 giá trị, khoảng một nửa nhiệt độ, một nửa áp suất.
>
> Bản đồ dùng tỉ lệ chứ không dùng số đếm, vì vị trí nào có cả trạm lẫn ERA5 thì số đếm tự nhiên gấp đôi. Tỉ lệ khá
> đều, trung vị 3,78%, thấp hơn mức 4,6% của phân bố chuẩn, nghĩa là ngưỡng z không gắn cờ quá tay.
>
> Theo thời gian thì dồn rõ vào hai sự kiện: tháng 9/2024 cao nhất, 880 ca, phần lớn là áp suất do bão Yagi; tháng
> 4/2024 có 371 ca nhiệt độ, gần như toàn bộ lệch dương. Lưu ý tháng 1/2021 cũng cao nhưng gần hết là ngày lạnh, nên
> phải đọc kèm dấu của z.

**Chuyển ý**
> Phóng to vào đúng một ngày của mỗi sự kiện.

## 5.5. Điểm dị thường trong hai sự kiện 2024 (45 giây)

**Trên slide**

Hai bản đồ điểm z: (a) nhiệt độ 30/4/2024; (b) áp suất 7/9/2024, phóng to lục địa; viền đen là |z| ≥ 3.

**Lời nói**
> Mỗi chấm là một giá trị z trong một ngày; hình tròn là trạm, hình vuông là lưới.
>
> Ngày 30/4, 176 trên 179 giá trị nhiệt độ lệch dương, tức nắng nóng phủ cả lục địa. Cao nhất là một trạm Thái Lan,
> z bằng 3,53. Một trạm có hai mã GHCN và ISD cho cùng kết luận, đúng như Entity Resolution đã ghép.
>
> Ngày 7/9 thì ngược lại: 11 giá trị áp suất z từ âm 3 trở xuống, đều ở Bắc Bộ quanh Hải Phòng, Nam Bộ gần như không
> lệch. Đó đúng là dấu vết của một cơn bão đổ bộ một vùng.

**Chuyển ý**
> Một giá trị z cao có thể là nóng thật, cũng có thể là cảm biến hỏng. Nhóm tách hai trường hợp này như sau.

## 5.6. Đối chứng bằng ERA5 và trạm lân cận (1 phút)

**Trên slide**

Biểu đồ phân loại 5.910 ca tại trạm 2020–2024: 93,3% xác nhận khí hậu thật, 6,3% cục bộ, 0,3% nghi lỗi, 0 ca thiếu đối chứng.

**Lời nói**
> Với mỗi dị thường ở trạm GHCN hoặc ISD, nhóm xem ERA5 cùng vị trí và các trạm trong bán kính 200 km có lệch cùng
> chiều không. Cùng chiều thì là dị thường khí hậu thật. Trạm cực đoan mà mọi đối chứng đều không ủng hộ thì nghi lỗi
> dữ liệu.
>
> Trong 2020–2024 có 5.910 ca: 5.515 ca, tức 93,3%, được xác nhận; 375 ca là dị thường cục bộ; 20 ca nghi lỗi. Không
> ca nào thiếu đối chứng, vì giai đoạn này luôn có ERA5.
>
> 13 trong 20 ca nghi lỗi thuộc trạm ISD Phnom Penh, đúng trạm mà phép phát hiện trôi cảm biến cũng gắn cờ áp suất.
> Trạm cách nhau dưới 5 km thì không dùng làm đối chứng, vì theo Entity Resolution đó là cùng một trạm.

**Chuyển ý**
> Các phép tính này chạy bằng batch. Nhóm kiểm tra xem làm theo luồng có ra cùng kết quả không.

## 5.7. Phát hiện dị thường theo luồng (1 phút)

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

## 5.8. PINN cho trường gió (45 giây)

**Trên slide**

Bảng λ = 0; 0,01; 0,1; 1,0 với RMSE, MAE, physics loss. PINN điền được trường gió nhất quán vật lý, sai số ngang hồi quy thuần (RMSE 1,06 so với 1,05); giải quyết được 2/12 trường (độ ẩm, gió), đánh dấu 4/113 vị trí gió bất thường; tiếp theo là 375 ca cục bộ.

**Lời nói**
> Mục đích là làm mịn trường gió giữa lưới ERA5 và trạm, có thêm ràng buộc vật lý là phương trình liên tục.
>
> λ là trọng số của ràng buộc vật lý; λ bằng 0 là hồi quy thuần. Baseline có RMSE tốt nhất. PINN với λ 0,1 tốt hơn
> một chút về MAE. Chênh lệch khoảng 1%, trên 22 trạm kiểm tra, nên nhóm chưa kết luận mô hình nào tốt hơn.
>
> Lý do có thể là nhóm mới có một thời điểm, trong khi ràng buộc vật lý cần chuỗi thời gian.
>
> Nói thẳng: PINN chưa giải quyết trực tiếp dị thường nào, vì dị thường chỉ tính trên nhiệt độ và áp suất, còn PINN
> làm độ ẩm và gió. Mục tiêu đo được tiếp theo là 375 ca dị thường cục bộ, những chỗ lưới ERA5 khoảng 28 km không
> xác nhận được tín hiệu tại trạm.

**Chuyển ý**
> Kết quả của các phần trên được gom lại trên dashboard.

## 5.9. Dashboard (30 giây)

**Trên slide**

Ảnh panel 7 (dị thường khí hậu); danh sách 10 panel.

**Lời nói**
> Dashboard viết bằng Streamlit, 10 panel, đọc trực tiếp từ kho Parquet. Đây là panel dị thường khí hậu: tỷ lệ ngày
> nóng bất thường theo năm, danh sách đợt nóng, chỉ số hạn SPI và mưa cực đoan.
>
> Nhóm kiểm tra cả 10 panel trên trình duyệt, không có lỗi runtime.

**Chuyển ý**
> Em tổng kết lại theo năm mục tiêu ban đầu.

---

# Phần 6. Kết luận

## 6.1. Kết quả theo mục tiêu (45 giây)

**Trên slide**

Bảng M1–M5 với kết quả đo được (2020–2024); 4/5 đạt đầy đủ, M4 đạt một phần; 83 test tự động.

**Lời nói**
> Đối chiếu với năm mục tiêu: M1 đủ năm nguồn, đúng phạm vi. M2 có toàn vẹn tham chiếu 100%, Entity Resolution đúng
> trên 15 cặp có nhãn, kiểm chéo thêm bằng Fellegi–Sunter trên 17 cặp, bảng hợp giải 856 nghìn dòng. M3 giảm 69,4%,
> vượt ngưỡng. M5 dashboard không lỗi.
>
> M4 nhóm đánh giá là đạt một phần: trong 2020–2024, nắng nóng và Yagi rõ, 93,3% dị thường tại trạm được xác nhận
> chéo, nhưng hạn Mekong chỉ có tín hiệu yếu.
>
> Hệ thống có 83 test tự động, gồm cả test chạy với Spark và Kafka.

**Chuyển ý**
> Cuối cùng là những gì nhóm chưa làm được.

## 6.2. Kết luận và hướng phát triển (45 giây)

**Trên slide**

Đã làm / Hạn chế (Fellegi–Sunter, lệch độ cao trạm–lưới) / Hướng tiếp.

**Lời nói**
> Nhóm đã có kho gần 9 triệu bản ghi từ năm nguồn. Dữ liệu được xử lý thiếu, sai, đơn vị, ngữ nghĩa ngay từ đầu
> pipeline, rồi tích hợp bằng GAV, Entity Resolution và Survivorship.
>
> Hạn chế: nhóm thử thêm mô hình xác suất Fellegi–Sunter để ghép trạm, nhưng nó không chính xác hơn luật 5 km hiện
> tại, 16 trên 17 so với 17 trên 17; luật phủ quyết thì có ích, chặn được 2 cặp sai chỉ vì trùng tên. Ngoài ra 19 vị
> trí lệch độ cao so với địa hình ERA5 hơn 100 m, nhiệt độ lệch khoảng 5,7 độ mỗi km, nên trạm và ô lưới phải được
> liên kết với nhau chứ không gộp làm một. Trôi cảm biến mới phát hiện, chưa hiệu chỉnh; hạ tầng chạy trên một máy.
>
> Hướng tiếp: hiệu chỉnh độ cao cho giá trị ERA5 dùng tại trạm, PINN có chiều thời gian cho 375 ca cục bộ, và hạ tầng
> nhiều máy. Em xin cảm ơn cô, nhóm sẵn sàng trả lời câu hỏi.

---

# Hỏi đáp dự kiến

Đã tách sang file riêng: [`hoi-dap-bao-ve.md`](hoi-dap-bao-ve.md).

---

# Slide có thể nói lướt nếu thiếu giờ

- 2.2 Nguồn dữ liệu (10 giây): chỉ nói Volume và Velocity.
- 3.6 Không gian (30 giây): chỉ nói RMSE mưa kém.
- 5.7 PINN (20 giây): "chưa vượt baseline, chênh 1%, chưa kết luận".
- 5.8 Dashboard (15 giây).
- 5.4 Điểm dị thường hai sự kiện (20 giây): chỉ nói "nắng nóng phủ lục địa, Yagi chỉ ở Bắc Bộ".

---

# Phụ lục: lời nói gợi ý từng trang

Không phải kịch bản phải thuộc — chỉ mở khi hội đồng hỏi. Người "hiểu chính" ở bảng đầu file trả lời trước,
đọc thẳng gợi ý dưới đây rồi diễn giải tự nhiên; không cần đọc nguyên văn.

## 36. Dữ liệu nằm ở năm nguồn khác nhau

**Lời nói**
> **Chính:** Quang · **Phụ:** Lương.
>
> Đây là bảng dị biệt 5 nguồn theo đúng 6 mức trong bài giảng Buổi 2: hệ thống, cú pháp, lược đồ, ngữ nghĩa, định
> danh, chất lượng. Ví dụ hệ thống: NASA POWER và Open-Meteo là REST API JSON, GHCN và ISD là CSV trên AWS S3,
> ERA5 là CDS API và Zarr. Ví dụ ngữ nghĩa: áp suất bề mặt khác áp suất mực nước biển, có 4 cách định nghĩa nhiệt
> độ ngày. Mỗi hàng trong bảng ứng với đúng một vấn đề nhóm đã xử lý ở phần 3.

## 37. Năm nguồn dữ liệu

**Lời nói**
> **Chính:** Quang · **Phụ:** Nghĩa.
>
> Bảng này cho thấy 5 nguồn không hoàn toàn độc lập: Open-Meteo lấy một phần dữ liệu từ ERA5, nên khi đối chứng
> dị thường nhóm không tính Open-Meteo là một xác nhận độc lập. GHCN và ISD cùng của NOAA nhưng QC gốc khác
> nhau, 406 so với 3.255 giá trị lỗi. Chỉ GHCN và ISD được dùng làm ground truth thật.

## 38. Vùng nghiên cứu

**Lời nói**
> **Chính:** Quang · **Phụ:** Lương.
>
> Bbox ERA5 phủ 11 nước ASEAN nhưng trạm quan trắc chỉ có ở 9 nước: 119 vị trí gồm 113 trạm và 6 điểm lưới.
> Singapore và Timor-Leste nằm trong bbox nhưng không có trạm GHCN, ISD hay NASA POWER nào nhóm chọn được. Ranh
> giới dùng Natural Earth 10m, đã cập nhật Timor-Leste gia nhập ASEAN 26/10/2025.

## 39. Quy mô kho sau tích hợp

**Lời nói**
> **Chính:** Quang · **Phụ:** Nghĩa.
>
> Kho có 8.955.313 bản ghi từ 5 nguồn, 119 vị trí, 9 nước, đưa về chung Mediated Schema WeatherObs. ERA5 lấy 5
> năm 2020–2024 theo giờ, ISD 10 năm, GHCN từ 1943. Dữ liệu thô khoảng 23 GB, sau tích hợp còn 303 MB Parquet.

## 40. Dữ liệu thô trước chuẩn hoá

**Lời nói**
> **Chính:** Lương · **Phụ:** Quang.
>
> Ba ví dụ dữ liệu thô thật: ISD ghi SLP=99999,9 là mã không đo của NOAA chứ không phải 9999,9 hPa; Open-Meteo
> trả gió theo km/h nhưng parser cũ ghi thẳng vào cột m/s, phóng đại 3,6 lần; GHCN có TAVG thật khác
> (TMAX+TMIN)/2 tới 0,4 độ nên nhóm giữ cả hai, thêm cột temp_def. Trích trực tiếp từ data_samples/, chi tiết ở
> docs/17.

## 41. Tải dữ liệu theo phạm vi đề cương

**Lời nói**
> **Chính:** Quang · **Phụ:** Nghĩa.
>
> Tải đủ phạm vi đề cương, kho tăng từ 1,08 lên 8,96 triệu bản ghi. ERA5 đủ 540/540 file qua CDS, 43.848/43.848
> giờ mỗi biến, 0% NaN. Nút thắt là hàng đợi CDS, có lúc chờ hơn 1 giờ, nhóm chạy 2 tài khoản song song. Nếu lấy
> qua kênh ARCO thì mỗi chunk là 1 giờ toàn cầu, giữ vùng Đông Nam Á 22 GB phải tải khoảng 1 TB, mất khoảng 27,8
> giờ ở 10 MB/s.

## 42. Tỷ lệ dữ liệu bị QC can thiệp

**Lời nói**
> **Chính:** Quang · **Phụ:** Lương.
>
> QC chỉ đặt NULL hoặc gắn cờ 0,09% số bản ghi, phần lớn do cờ lỗi gốc của ISD, 3.255 giá trị, nhiều hơn GHCN,
> 406 giá trị. Tỷ lệ nhỏ vì đây là can thiệp ở tầng 1 và 2, trước khi tích hợp.

## 43. Chọn IQR thay cho Z-score

**Lời nói**
> **Chính:** Lương · **Phụ:** Quang.
>
> Tiêm 5 outlier cực đoan vào dữ liệu mô phỏng N(25, 2): chính outlier làm độ lệch chuẩn phình từ 2,0 lên 72,2,
> nên ngưỡng 3 sigma rộng tới mức Z-score chỉ bắt được 1/5. IQR tính trên tứ phân vị nên không bị kéo theo, bắt
> được 5/5. Vì vậy nhóm chọn IQR làm chỉ số chính cho Data Quality Report.

## 44. Lỗi số liệu trong pipeline

**Lời nói**
> **Chính:** Quang · **Phụ:** Nghĩa.
>
> Bốn lỗi thật đã gặp và đã sửa: gió Open-Meteo phóng đại 3,6 lần do đọc nhầm đơn vị; tương quan giả gió–độ ẩm
> +0,57 do thay NaN bằng 0 trước khi tính, sửa bằng cách tính theo từng cặp thì còn −0,59; benchmark partition so
> với bản sao cũ sai vì bản không partition chỉ ghi 1 lần nên lúc nào cũng có vẻ chậm hơn, đo lại công bằng thì
> partition chậm hơn 1,5–2,5 lần; bức xạ ERA5 dùng nhầm đại lượng đỉnh khí quyển thay vì bề mặt, đã đổi lại để
> cùng đại lượng với NASA POWER.

## 45. Chiến lược partition

**Lời nói**
> **Chính:** Nghĩa · **Phụ:** Quang.
>
> Thử partition thêm theo tháng: data skew giảm từ 11,08% xuống 0,94%, nhưng số partition tăng 12 lần, từ 109
> lên 1.306, gây vấn đề small-file. Đo lại công bằng trên 9 triệu dòng thì partition hiện tại chậm hơn không
> partition 1,5–2,5 lần, vì Parquet đã tự bỏ qua dữ liệu nhờ thống kê min/max theo row-group. Nhóm giữ
> year/source, vì lợi ích chỉ rõ ở quy mô lớn hơn hoặc trên S3/GCS.

## 46. Cụm Spark và Kafka

**Lời nói**
> **Chính:** Nghĩa · **Phụ:** Lương.
>
> Cụm 3 container Docker trên cùng một máy: 1 master, 2 worker, Kafka 1 broker KRaft, RF 1, topic 1 partition.
> spark_streaming_consumer.py đọc topic Kafka, in nhiệt độ trung bình từng trạm theo cửa sổ trượt 1 phút, trượt
> 30 giây. Mốc 20/10 dựng xong cụm, mốc 9/11 streaming windowing chạy thật.

## 47. Mưa cực đoan khi bão Yagi

**Lời nói**
> **Chính:** Nghĩa · **Phụ:** Lương.
>
> 7/9/2024 là ngày mưa lớn nhất 5 năm tại 4 trạm miền Bắc: Hà Đông 222,6 mm, Nội Bài 203,5 mm, Phù Liễn 187,4 mm,
> Cát Bi 176,5 mm, gấp 2,6–3,1 lần ngưỡng p99. Vì mưa không phân bố chuẩn nên dùng chỉ số ETCCDI p95/p99 trên
> ngày ướt, Rx1day, R95p. 11/13 cặp trạm–nguồn vượt p99 trong 6–11/9/2024. Trạm GHCN Phù Liễn mất số liệu đúng
> lúc bão đổ bộ 7–8/9, rồi ghi 214 mm vào ngày 11/9.

## 48. Xu hướng nhiệt độ dài hạn

**Lời nói**
> **Chính:** Nghĩa · **Phụ:** Lương.
>
> 25/27 trạm GHCN ấm lên có ý nghĩa thống kê giai đoạn 1975–2024, trung vị +0,21 độ C mỗi thập kỷ. Dùng
> Mann-Kendall cho ý nghĩa thống kê, độ dốc Sen cho tốc độ, không giả định phân bố chuẩn. Nhanh nhất là Jakarta
> +0,41, Penang +0,35, Bangkok +0,35, Cao Bằng +0,34 độ mỗi thập kỷ. Trừ xu hướng nền này thì năm 2024 vẫn nổi
> bật. Xu hướng mưa chỉ có 1–6 trạm đủ 30 năm số liệu nên chưa đủ kết luận.

## 49. Phát hiện trôi cảm biến

**Lời nói**
> **Chính:** Lương · **Phụ:** Nghĩa.
>
> Lấy chênh lệch trạm trừ ERA5 theo tháng: biến động khí hậu thật có ở cả hai nên triệt tiêu, phần còn lại là
> lỗi cảm biến hoặc điểm đo. Trôi dần dùng Mann-Kendall và độ dốc Sen, nhảy bậc dùng kiểm định Pettitt. Rõ nhất
> là áp suất Phnom Penh nhảy bậc −2,6 hPa từ 11/2022, tương đương trôi −0,65 hPa mỗi năm. Tiêm lỗi nhân tạo vào
> 76 chuỗi thật đang ổn định: phát hiện 100% ca trôi, 95–98% ca nhảy bậc.

## 50. Tương quan và PCA

**Lời nói**
> **Chính:** Lương · **Phụ:** Nghĩa.
>
> Tương quan tính theo từng cặp, không thay NaN bằng 0: nhiệt độ–độ ẩm −0,59 trên ISD, nhiệt độ–áp suất mực biển
> −0,56 trên Open-Meteo. PCA theo Z-score: PC1 của Open-Meteo là nóng/áp thấp/gió, PC2 gom độ ẩm, mưa và áp thấp
> kiểu bão mà không cần gán nhãn trước. PC1 và PC2 chỉ giải thích 48–56% phương sai, cần thêm thành phần để mô
> tả đủ biến động khí tượng Đông Nam Á.

## 51. Các panel của dashboard

**Lời nói**
> **Chính:** Nghĩa · **Phụ:** Lương.
>
> Dashboard Streamlit có 10 panel, đọc trực tiếp từ kho Parquet, đã kiểm tra trên trình duyệt không lỗi runtime.
> Panel 5 cảnh báo bất thường theo IQR, panel 7 dị thường khí hậu, panel 9 trôi cảm biến, panel 10 cảnh báo theo
> luồng Kafka. Bảng được cache theo ngày, đổi ngày hoặc trạm mất khoảng 0,6 giây.

## 52. Panel 1: tổng quan tích hợp

**Lời nói**
> **Chính:** Nghĩa · **Phụ:** Quang.
>
> Ảnh chụp thật từ trình duyệt, chạy local trên bản warehouse rút gọn 1.076.473 dòng, 119 trạm/điểm, để chụp ảnh
> nhanh. Các slide phân tích chính của bài dùng kho đầy đủ 8,96 triệu dòng, nêu ở Mục 6.1 báo cáo.

## 53. Tiến độ theo từng người

**Lời nói**
> **Chính:** Nghĩa · **Phụ:** Quang.
>
> Mỗi thanh là một sản phẩm cụ thể có bằng chứng, không phải thanh trải đều cả kỳ. Nét liền là ba mốc chính
> thức: đề cương 5/10, tiến độ 20/10, cuối kỳ 15/11. Nét đứt là hai mốc nội bộ nhóm tự đặt: kiểm thử 27/10, hội
> tụ 2/11.

## 54. Sản phẩm của từng người theo mốc

**Lời nói**
> **Chính:** Nghĩa · **Phụ:** Lương.
>
> Mỗi dòng gắn với một file hoặc mục báo cáo cụ thể, không phải lời kể chung chung: Quang có
> check_data_sources.py và thư mục ingestion/, Lương có entity_resolution.py, Nghĩa có docker-compose và Mục
> 6.4–6.7. Theo thông báo 15/11, buổi trình bày không có demo trực tiếp, nhưng cụm Docker và pytest vẫn chạy
> được ngay nếu hội đồng yêu cầu.

## 55. Giới hạn hạ tầng

**Lời nói**
> **Chính:** Nghĩa · **Phụ:** Lương.
>
> Hạ tầng chạy trên một máy nên chưa kết luận được về hiệu năng phân tán. Kafka chỉ 1 broker, RF 1, 1 partition
> nên không chịu lỗi và Spark chỉ đọc bằng 1 task dù cụm có nhiều worker. AQE của Spark 4 để mặc định nên số đo
> cache() chịu ảnh hưởng của việc tự gộp shuffle partition, nhóm chưa tách riêng. Entity Resolution có nhãn độc
> lập ở 15/26 trạm, 11 trạm còn lại chưa có nhãn. Khí hậu nền của ERA5 và ISD chỉ 5–10 năm. Trong cửa sổ kết quả
> 2020–2024 mọi dị thường tại trạm đều có đối chứng; trước 2020, khi chưa có ERA5, phần lớn thì không, nên nhóm
> chỉ báo kết quả cho 2020–2024. SPI mới tính được ở 12 trạm vì GHCN thiếu số liệu mưa.

## 56. Mở rộng ra toàn cầu

**Lời nói**
> **Chính:** Nghĩa · **Phụ:** Lương.
>
> Mở rộng ra toàn cầu thì cả bốn thành phần đều phải đổi: Entity Resolution cần Blocking/LSH vì GHCN có hơn
> 14.000 trạm, số cặp lên hàng trăm triệu; lưu trữ cần HDFS/S3/MinIO vì ERA5 toàn cầu tới hàng trăm TB; Kafka
> cần RF từ 3 trở lên và nhiều partition; Spark cần cụm nhiều máy thật vì DuckDB chỉ nhanh hơn khi dữ liệu còn
> vừa RAM một máy. Cùng lý do này, Mục 2.1 báo cáo không chọn kiến trúc Dataspace hay pay-as-you-go.

## 57. Kiến trúc PINN và huấn luyện

**Lời nói**
> **Chính:** Nghĩa · **Phụ:** Lương.
>
> Nhóm có hai mạng nhỏ. RHNet dự đoán độ ẩm từ nhiệt độ và điểm sương: 2 lớp ẩn 16 nơ-ron, Tanh, đầu ra Sigmoid
> nhân 100, tổng 337 tham số, ràng buộc Clausius–Clapeyron; loss giảm từ 1068 xuống 2,9, sai số tuyệt đối trung
> bình 1,07 điểm phần trăm. WindFieldNet dựng trường gió (u, v) từ toạ độ: 2 lớp ẩn 32 nơ-ron, 1.218 tham số,
> ràng buộc phương trình liên tục tính bằng autograd; 113 trạm ERA5 ngày 15–17/6/2021, 91 luyện, 22 kiểm tra.
>
> PINN điền được trường gió tại mọi điểm, và tăng lambda làm vi phạm vật lý giảm từ 0,53 xuống 0,011. Về sai số thì
> ngang hồi quy thuần: lambda bằng 0 đạt RMSE 1,0473, PINN tốt nhất 1,0577, nên cần thêm chiều thời gian để vượt hẳn. Trên đồ thị,
> Physics Loss ở lambda 0,1 tăng rồi chững chứ không về 0: mạng lúc đầu gần như hằng số nên độ phân kỳ gần 0 một
> cách ngẫu nhiên, khi học được biến thiên thật thì độ phân kỳ xuất hiện.
>
> PINN giải quyết được hai trong mười hai trường, độ ẩm và gió, đúng hai trường mà bộ dò dị thường dựa trên
> nhiệt độ và áp suất chưa phủ. Mô hình độ ẩm cho trường độ ẩm ở hơn ba triệu bản ghi ISD chỉ có điểm sương, sai số
> 1,07 điểm phần trăm. Mô hình gió nhận vào toạ độ nên điền được gió ở bất kỳ điểm nào giữa các ô lưới ERA5 hay tại
> trạm thiếu số liệu; thử trên 22 vị trí giữ lại, sai số 1,06 m/s so với gió trung bình 2,26 m/s, nên còn cao và cần
> thêm chiều thời gian. Mô hình gió có thêm một tác dụng phát hiện: phần dư giữa gió quan trắc và trường PINN đánh dấu
> 4 trên 113 vị trí lệch quá 2,62 m/s, là Mandalay, Đồng Hới và Phú Quốc, đều là thung lũng, ven biển hoặc đảo.
> Bước tiếp theo đo được là dùng trường PINN phân xử 375 ca dị thường cục bộ, 6,3%, mà lưới ERA5 khoảng 28 km
> không xác nhận được.

## 58. Các loại dị thường khí hậu và bảng xu hướng

**Lời nói**
> **Chính:** Nghĩa · **Phụ:** Lương.
>
> Nhóm đo bốn loại dị thường và cực đoan khác nhau, không gộp chung một chỉ số. Dị thường chung dùng z-score so
> với khí hậu nền, cửa sổ trượt 15 ngày quanh mỗi ngày trong năm. Đợt nóng là từ ba ngày liên tiếp trở lên có
> nhiệt độ vượt bách phân vị 90 của nền, theo đúng chỉ số TG90p chuẩn ETCCDI. Hạn hán dùng SPI, khớp phân bố
> Gamma theo từng tháng trên nền 1991 đến 2020. Mưa cực đoan dùng bốn chỉ số ETCCDI: tổng mưa ngày ướt, mưa ngày
> lớn nhất, và tổng mưa vượt bách phân vị 95, 99.
>
> Sau khi phát hiện, mỗi dị thường được gắn một trong bốn nhãn đối chứng: xác nhận khí hậu thật nếu ERA5 hoặc
> phần lớn trạm lân cận đồng thuận; nghi lỗi dữ liệu nếu trạm báo cực đoan mà mọi đối chứng đều phản đối; dị
> thường cục bộ nếu đối chứng chỉ ủng hộ yếu; và không đối chứng nếu không có dữ liệu để so.
>
> Bảng xu hướng khác với z-score ở chỗ nó đo chính khí hậu nền có đang dịch chuyển theo thời gian hay không,
> dùng kiểm định Mann-Kendall cho ý nghĩa thống kê và độ dốc Sen cho tốc độ thay đổi mỗi thập kỷ.

## 59. Ghép theo khoá, không theo thứ tự mảng

**Lời nói**
> **Chính:** Lương · **Phụ:** Quang.
>
> Mọi phép ghép giữa năm nguồn đều dùng khoá location_id cộng timestamp_utc, không bao giờ dựa vào vị trí trong
> mảng mà API trả về. Lý do: một API có thể trả thiếu, đổi thứ tự, hoặc timeout một phần, ghép theo vị trí mảng
> sẽ gán sai giá trị cho sai vị trí ngay khi có bất kỳ sai lệch nào.
>
> Cách làm cụ thể: check_data_sources.py so khớp toạ độ trả về với toạ độ đã gửi theo từng điểm trước, gắn
> location_id rồi mới lưu. Mọi bước sau, từ build_warehouse đến survivorship, đều merge theo đúng khoá này.
>
> Khi một nguồn thiếu hoặc lệch, dữ liệu vẫn an toàn: ISD thiếu mưa hay GHCN thiếu gió thì dòng vẫn giữ đúng
> khoá, chỉ biến đó là NULL. Bốn trạm ISD không tìm được trạm GHCN trong bán kính thì giữ riêng, không ép ghép.
>
> Bằng chứng đo được: Entity Resolution kiểm chứng chéo bằng mã WMO, một khoá hoàn toàn độc lập với toạ độ, vẫn
> cho precision và recall đều 100% trên 15 cặp có nhãn — tức là ghép theo khoá vị trí và ghép theo khoá WMO cho
> ra cùng kết quả, không phải trùng hợp ngẫu nhiên.

## 60. Trường dữ liệu và độ phân giải theo từng nguồn

**Lời nói**
> **Chính:** Quang · **Phụ:** Lương.
>
> Mỗi nguồn chỉ được chọn đúng tập trường cần cho WeatherObs, không phải toàn bộ trường mà API hay tệp gốc có
> thể cung cấp. GHCN chỉ cho nhiệt độ và mưa, theo ngày, từ 1943. ISD cho thêm độ ẩm suy từ điểm sương, áp suất
> và gió, theo giờ, nhưng chỉ từ 2015. NASA POWER và Open-Meteo đều là điểm, gọi API đúng toạ độ trạm, 5 năm gần
> đây. ERA5 là nguồn duy nhất dạng lưới, 0,25 độ, phải nội suy Bilinear về toạ độ trạm trước khi so sánh được.
>
> Điểm quan trọng: mọi trường trong sáu trường chính đều có ít nhất hai nguồn cùng báo cáo, và đều đo được mức
> sai lệch cụ thể giữa các nguồn, từ 0% ở áp suất mực biển tới 91,6% ở mưa. Đây là điều kiện bắt buộc để Entity
> Resolution và Survivorship có ý nghĩa — nếu một trường chỉ một nguồn báo cáo thì không có gì để đối chiếu.

Không cắt phần 3: đây là phần cô hỏi trực tiếp.

## 61. Chuỗi ngày tại trạm kèm các điểm dị thường

**Lời nói**
> **Chính:** Nghĩa · **Phụ:** Lương.
>
> Ở mức một trạm, dị thường là các ngày rơi ra ngoài dải nền cộng trừ hai độ lệch chuẩn của chính trạm đó. Tại
> Bangkok, nắng nóng tháng 4/2024 chỉ có một ngày vượt ngưỡng, 21/4, 33,8 độ, z bằng 2,01; sáu ngày còn lại bị
> gắn cờ đều là ngày mát bất thường. Nắng nóng ở đây là nhiều tuần sát cận trên của dải nền, nên cần thêm chỉ
> số đợt nóng TG90p bên cạnh z. Tại Hải Phòng, áp suất rơi từ 992,6 hPa ngày 6/9 xuống 978,8 hPa ngày 7/9, z
> bằng âm 7,2, rồi về lại dải nền sau hai ngày, đúng dạng bão Yagi đi qua.

## 62. Đợt nóng và hạn SPI-3 trong 2020–2024

**Lời nói**
> **Chính:** Nghĩa · **Phụ:** Quang.
>
> Trong 2020–2024 có 3.832 đợt nóng. Phân bố lệch phải: trung vị 4 ngày, 68,6% số đợt chỉ 3–4 ngày, 116 đợt từ
> 10 ngày trở lên. Dài nhất ở Phuket, 43 ngày từ 26/1/2024 và 30 ngày từ 3/4/2024, khớp đợt nắng nóng 2024.
>
> SPI-3 chỉ có hai trạm vùng Mekong đủ chuỗi mưa tháng, Cà Mau và Phan Thiết. Trong cửa sổ chỉ có đuôi 1–5/2020
> của đợt hạn 2019–2020: 4 trên 7 tháng–trạm có SPI-3 từ âm 1 trở xuống, so với 9,9% của cả giai đoạn. Đúng
> chiều, nhưng hai trạm ven biển chưa đại diện cho cả lưu vực.

## 63. Mưa cực đoan theo nước (R95pTOT)

**Lời nói**
> **Chính:** Nghĩa · **Phụ:** Quang.
>
> R95pTOT là phần trăm lượng mưa năm đến từ những ngày vượt bách phân vị 95 của chính trạm. Trong 2020–2024 tỉ lệ
> này khoảng một phần năm đến một phần tư: cao nhất Philippines 27,6% và Việt Nam 24,6%, thấp nhất Campuchia
> 19,2%. Chênh giữa các nước chỉ khoảng 8 điểm phần trăm và nhiều nước có ít năm–vị trí, nên nhóm không xếp hạng
> chặt giữa các nước.

## 64. Mật độ trạm đo lỗi dữ liệu 2020–2024

**Lời nói**
> **Chính:** Quang · **Phụ:** Nghĩa.
>
> Hình trái là tầng Ingestion: 1.590 dòng có cờ QC nằm ở 32 trên 61 trạm, gần hết là ISD, và năm trạm ISD ở
> Campuchia, Lào, Myanmar, Thái Lan chiếm 56,4%, tức lỗi gắn với trạm và cơ quan vận hành. Hình phải là tầng phân
> tích: xác nhận chéo chỉ còn 20 ca nghi lỗi ở 8 trạm vì giai đoạn này luôn có ERA5; riêng Phnom Penh 13 ca.
>
> Vòng đen là bốn chuỗi trôi cảm biến. Phnom Penh có mặt ở cả ba lớp: 219 dòng gắn cờ QC, 13 ca nghi lỗi và trôi
> áp suất âm 0,65 hPa mỗi năm. Viêng Chăn có 210 dòng gắn cờ và nhảy bậc nhiệt độ. Đây là các trạm cần kiểm tra
> hồ sơ thiết bị trước khi dùng chuỗi.

## 65. Fellegi–Sunter và luật phủ quyết

**Lời nói**
> **Chính:** Lương · **Phụ:** Nghĩa.
>
> Ngưỡng 5 km là quyết định cứng, nên nhóm chạy thêm Fellegi–Sunter trên đúng 2.262 cặp ứng viên, đặc trưng là
> khoảng cách, chênh độ cao và độ giống tên; mã WMO không làm đặc trưng vì đó là nhãn. Xác suất m, u ước lượng
> bằng EM không giám sát. Ngưỡng theo định nghĩa gốc: theta h bằng 6,64 ứng với tỷ lệ ghép nhầm không quá
> 0,05%, theta l bằng âm 1,31 ứng với tỷ lệ bỏ sót không quá 1%.
>
> Trước khi chấm điểm, ba luật phủ quyết lấy ngưỡng từ dữ liệu: cặp thật xa nhất 2,76 km, lệch độ cao 9,3 m, nên
> loại cặp xa hơn 10 km, lệch hơn 100 m hoặc khác nước. Ba luật loại 2.234 cặp, không loại cặp thật nào, và chặn
> hai cặp mô hình xếp khớp chỉ vì tên giống: Surabaya/Perak với Juanda, và Mandalay với Mandalay Intl.
>
> Kết quả trung thực: Fellegi–Sunter không chính xác hơn Haversine. Bản nhiều–một bằng, bản 1–1 kém một cặp ở
> Don Mueang. Giá trị của nó là ngưỡng gắn với tỷ lệ lỗi tường minh, và lộ ra Đà Nẵng, Tân Sơn Nhất, Don Mueang
> mỗi nơi có hai chuỗi GHCN của cùng một sân bay.

## 66. Liên kết trạm với lưới ERA5, không gộp

**Lời nói**
> **Chính:** Lương · **Phụ:** Nghĩa.
>
> Trạm là một điểm đo, còn ô ERA5 là trung bình của ô 0,25 độ trên địa hình mô hình: hai thực thể khác nhau cùng
> quan trắc một hiện tượng. Vì vậy nhóm ghi quan hệ chứ không hợp nhất: bảng station_grid_link nối 119 vị trí
> với tâm ô gần nhất, trung vị 9,42 km, kèm độ lệch độ cao.
>
> 19 trên 119 vị trí lệch độ cao quá 100 m. Luang Prabang ở 291 m trong khi ô ERA5 ở 749 m, và trạm ấm hơn 3,53
> độ. Bias nhiệt theo độ lệch độ cao có độ dốc âm 5,66 độ mỗi km, gần gradient chuẩn âm 6,5, nên phần lớn chênh
> lệch là khác biệt đại diện, không phải lỗi. Gộp hai thực thể sẽ biến 3,5 độ đó thành một xung đột cần chọn bên
> thắng. Bảng hợp giải hiện vẫn lấy nhiệt ERA5 chưa hiệu chỉnh ở 10,3% số ngày tại 19 vị trí này; hiệu chỉnh
> theo gradient là đề xuất, chưa cài đặt.
