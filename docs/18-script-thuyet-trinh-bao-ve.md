# Script thuyết trình bảo vệ — Nhóm 16, IT5427 (15/11/2026)

Script này viết cho **một người nói liên tục từ đầu tới cuối** — chưa chia vai theo từng phần, để cả
nhóm đọc hiểu trọn vẹn mạch câu chuyện trước, rồi tự quyết định ai nói đoạn nào. Mỗi mục dưới đây
ứng với đúng một slide trong `final-defense.tex` (41 slide, kể cả slide tiêu đề/ngăn mục), theo đúng
thứ tự thật. Chữ nghiêng là ghi chú cho người nói (không đọc ra), chữ thường là lời nói ra.

Tổng thời lượng mục tiêu: **15 phút**. Thời gian ghi ở đầu mỗi slide là ước lượng — slide có bảng số
liệu cần nói chậm hơn slide chuyển mục. Nếu thiếu giờ, cắt ở các đoạn đánh dấu **(*cắt được nếu
thiếu giờ*)** trước, không cắt phần in đậm.

---

## Mở đầu (0:00 – 0:40)

### Slide 1 — Trang bìa
*(10 giây, trong lúc màn hình hiện trang bìa)*

> Kính chào thầy/cô và các bạn. Nhóm 16 xin trình bày đồ án: **Hệ thống tích hợp và xử lý dữ liệu khí
> tượng đa nguồn phục vụ phát hiện dị thường khí hậu khu vực Đông Nam Á**. Nhóm gồm ba thành viên:
> Ngô Văn Quang, Nguyễn Cao Lương và Trương Tuấn Nghĩa.

### Slide 2 — "Nội dung"
*(15 giây)*

> Bài trình bày có sáu phần: bài toán và kiến trúc, tổng kết kết quả chung, rồi đi theo bốn mảng kỹ
> thuật — Ingestion, Schema và Warehousing, Spark/Streaming/PINN, Dashboard — và kết thúc bằng rủi
> ro, giới hạn và kết luận. Phần phân công cụ thể theo người sẽ nói ở gần cuối.

---

## Bài toán & kiến trúc (0:40 – 2:10)

### Slide 3 — "Tích hợp năm nguồn khí tượng dị biệt... với 5 mục tiêu có ngưỡng đo được trước"
*(45 giây — đây là slide quan trọng nhất để người nghe hiểu bài toán, không cắt*

> Bài toán của nhóm: khí tượng Đông Nam Á có năm nguồn dữ liệu công khai, nhưng chúng đo theo ba
> cách khác nhau — ERA5 là dữ liệu dạng **lưới** (một mô hình tái phân tích tính ra giá trị tại mọi
> điểm trên bản đồ), còn GHCN-Daily, NOAA ISD, NASA POWER, Open-Meteo là dữ liệu **điểm** đo tại
> từng trạm. Nhóm hợp nhất cả năm nguồn này thành một kho dữ liệu duy nhất, truy vấn được, để từ đó
> phát hiện dị thường khí hậu.
>
> Điều nhóm làm khác với một báo cáo thông thường: **mọi mục tiêu đều có một con số ngưỡng đặt
> trước khi đo**, không chỉ nói chung chung "làm hệ thống tốt". Ví dụ M3 — tối ưu Spark bằng cache
> phải tăng tốc ít nhất 30%, không phải "nhanh hơn" mơ hồ. Cách làm này giúp cuối buổi có thể trả lời
> dứt khoát: đạt hay không đạt, bằng đúng con số đã hứa từ đầu.

### Slide 4 — "Kiến trúc thật: 8,96 triệu dòng đã vào kho, ERA5 đã tải đủ 540/540 file qua CDS"
*(40 giây)*

> Đây là kiến trúc thật của hệ thống — mọi con số trên sơ đồ là số đo thật, không phải số minh hoạ.
> Năm nguồn bên trái đi qua một tầng Ingestion có kiểm soát chất lượng bốn tầng, hội tụ vào một lược
> đồ trung gian gọi là Mediated Schema — tên bảng là `WeatherObs` — rồi ghi thành kho Parquet
> **8.955.313 dòng**. Từ kho đó, bốn nhánh xử lý tiếp: Entity Resolution khớp trạm, Survivorship hợp
> giải xung đột giá trị, phát hiện dị thường khí hậu, và PINN. Một nhánh riêng mô phỏng tính chất
> luồng thời gian thực qua Kafka và Spark Streaming. Tất cả đổ về một dashboard Streamlit.
> *(*cắt được nếu thiếu giờ*: không cần đọc hết từng nhãn trên sơ đồ, chỉ cần nói luồng chính)*

---

## 1. Tổng kết kết quả chung (2:10 – 3:40)

### Slide 5 — Ngăn mục "1. Tổng kết kết quả chung"
*(3 giây, đọc tên mục rồi chuyển luôn)*

### Slide 6 — "Pipeline tích hợp 5 nguồn... thành 1 kho dữ liệu thống nhất, có thể truy vấn được"
*(25 giây)*

> Tổng quan nhanh: **8,96 triệu bản ghi thật**, **119 vị trí** — gồm 113 trạm quan trắc và 6 điểm đại
> diện — trải trên **9 nước Đông Nam Á**. Dữ liệu thô khoảng 23 GB, sau khi tích hợp và nén còn 303
> MB — vừa bộ nhớ một máy tính thường, điều này sẽ quay lại ở phần giới hạn hạ tầng.

### Slide 7 — "Không phải 5 nguồn ngang hàng: 2 nguồn là mô hình, 1 nguồn chỉ là lớp trung gian của chính ERA5"
*(35 giây — slide thể hiện tư duy phản biện của nhóm, nên nói kỹ)*

> Một điểm nhóm muốn nhấn mạnh trước khi đi vào kết quả: **năm nguồn không "ngang hàng"** về độ tin
> cậy. GHCN và ISD là quan trắc trực tiếp tại trạm. ERA5 và NASA POWER là **sản phẩm mô hình** —
> ước lượng tính toán, không phải đo trực tiếp. Và Open-Meteo thực chất là một **lớp trung gian**:
> khi nhóm kiểm tra kỹ, phát hiện Open-Meteo lấy một phần dữ liệu lịch sử trực tiếp từ chính ERA5.
> Hệ quả: nếu sau này thấy ERA5 và Open-Meteo "khớp nhau", đó **không phải** hai nguồn độc lập xác
> nhận lẫn nhau — vì bản chất chúng có thể là cùng một con số đi qua hai đường khác nhau. Đây là lý
> do nhóm chỉ dùng GHCN và ISD làm "sự thật mặt đất" để đối chứng dị thường.

### Slide 8 — Bản đồ khu vực nghiên cứu (ASEAN 11 nước)
*(20 giây)*

> Đây là bản đồ khu vực nghiên cứu thật — không phải minh hoạ. Vùng khung nét đứt là vùng tải ERA5,
> phủ hình học đủ cả **11 nước ASEAN** — tính cả Timor-Leste, nước gia nhập khối ngày 26/10/2025.
> Nhưng trạm quan trắc thật nhóm chọn được chỉ phủ **9 trên 11 nước** — Singapore và Timor-Leste nằm
> trong vùng tải nhưng không có trạm nào. Nhóm nói rõ giới hạn này thay vì che đi.

---

## 2. Ingestion (3:40 – 6:10)

### Slide 9 — Ngăn mục "2. Ingestion"
*(3 giây)*

### Slide 10 — "Dữ liệu thô 3 nguồn trước chuẩn hoá: thiếu, đơn vị khác, định nghĩa khác — 3 bản ghi thật"
*(45 giây — đây là bằng chứng cụ thể nhất cho phần "đặc trưng dữ liệu", nói chậm)*

> Đây chính là phần trả lời trực tiếp câu hỏi giảng viên đã hỏi thẳng nhóm: dữ liệu thu thập có
> những loại vấn đề gì cần xử lý. Nhóm minh hoạ bằng ba **bản ghi thật**, trích thẳng từ dữ liệu đã
> tải, không dựng tay.
>
> Thứ nhất, **thiếu dữ liệu**: trạm ISD ghi áp suất là `99999,9` — đây không phải một giá trị áp suất
> thật, mà là mã quy ước của NOAA nghĩa là "không đo được". Nếu không biết quy ước này, hệ thống sẽ
> coi 99999 hPa là một con số hợp lệ — sai nghiêm trọng.
>
> Thứ hai, **đơn vị khác nhau**: Open-Meteo trả tốc độ gió là 4,9 — nhưng đơn vị là km/h, trong khi
> cột của nhóm quy ước là m/s. Một phiên bản parser cũ từng ghi thẳng 4,9 vào cột m/s mà không đổi
> đơn vị — phóng đại tốc độ gió thật lên **3,6 lần**.
>
> Thứ ba, **định nghĩa khác nhau tuy cùng tên biến**: GHCN có một cột "nhiệt độ trung bình ngày",
> nhưng giá trị TAVG thật đo được không bằng công thức (nhiệt độ cao nhất + thấp nhất) chia 2 — lệch
> 0,4 độ C. Hai cách tính này là hai định nghĩa vật lý khác nhau, trộn lẫn sẽ làm sai các phân tích
> xu hướng dài hạn về sau.

### Slide 11 — "IQR phát hiện đủ 5/5 outlier cực đoan trong khi Z-score chỉ bắt được 1/5"
*(30 giây)*

> Nhóm cũng làm một thí nghiệm nhỏ để chọn đúng công cụ phát hiện giá trị bất thường. Tiêm 5 giá trị
> cực đoan giả vào một tập dữ liệu mô phỏng, rồi thử hai cách đo: Z-score — dựa trên độ lệch chuẩn —
> chỉ bắt được 1 trên 5. Lý do: chính 5 giá trị cực đoan đó làm độ lệch chuẩn phình to từ 2,0 lên
> 72,2, khiến ngưỡng "3 lần độ lệch chuẩn" trở nên quá rộng — gọi là hiệu ứng **masking**. Trong khi
> đó IQR — dựa trên tứ phân vị, không bị kéo méo bởi chính các outlier — bắt đủ cả 5. Nhóm chọn IQR
> làm chỉ số chính.

### Slide 12 — "Đã tải đủ dữ liệu theo phạm vi đề cương: kho dữ liệu tăng 8,3 lần lên 9,0 triệu bản ghi"
*(30 giây)*

> Về khối lượng: so với lần báo cáo giữa kỳ, kho dữ liệu đã tăng **8,3 lần**, lên 8,96 triệu dòng.
> ERA5 — nguồn trung tâm về mặt lý thuyết của đề tài — đã tải đủ **540 trên 540 file**, đúng 9 biến
> nhân 60 tháng, không thiếu một tháng nào, qua kênh CDS chính thức của Copernicus.

### Slide 13 — "Kiểm tra lại trên dữ liệu đầy đủ phát hiện và sửa 4 lỗi số liệu thật trong pipeline"
*(40 giây — quan trọng vì thể hiện nhóm tự kiểm tra, không chỉ chạy một lần rồi thôi)*

> Khi chạy lại toàn bộ phân tích trên dữ liệu đầy đủ, nhóm **tự phát hiện và sửa bốn lỗi thật** trong
> chính pipeline của mình — đây là bằng chứng nhóm có kiểm tra chéo, không chỉ tin vào lần chạy đầu.
> Lỗi gió Open-Meteo phóng đại 3,6 lần như vừa nói ở trên. Một lỗi tính tương quan giả: ban đầu nhóm
> thay giá trị thiếu bằng 0 trước khi tính tương quan — nhưng mỗi nguồn thiếu biến khác nhau, nên
> phép thay 0 này tạo ra tương quan gió và độ ẩm dương giả +0,57. Tính lại đúng cách, bỏ qua các ô
> thiếu thay vì gán 0, lộ ra tương quan thật là nhiệt độ với độ ẩm **−0,59**, nhiệt độ với áp suất
> **−0,61** — đúng chiều vật lý, nóng thì ẩm giảm và áp suất giảm.

### Slide 14 — "Kiểm soát chất lượng 4 tầng khi nạp: loại 3.661 giá trị mà NOAA đã gắn cờ lỗi"
*(25 giây) **(*cắt được nếu thiếu giờ*, nói nhanh)***

> Nhóm xây bốn tầng kiểm soát chất lượng khi nạp dữ liệu: đọc cờ lỗi gốc của chính NOAA, kiểm giới
> hạn vật lý, và phát hiện bước nhảy phi vật lý theo thời gian. Tổng cộng loại 3.661 giá trị lỗi,
> trong đó có hai bản tin từng ghi tốc độ gió 83 mét/giây — rõ ràng là lỗi cảm biến, không phải gió
> thật.

### Slide 15 — "Chỉ 0,09% dữ liệu bị can thiệp QC"
*(15 giây)*

> Biểu đồ này cho thấy toàn cảnh: tổng số lần can thiệp QC chỉ chiếm 0,09% dữ liệu — phần lớn đến từ
> cờ gốc của ISD, không phải lỗi vật lý nghiêm trọng.

---

## 3. Schema & Warehousing (6:10 – 8:10)

### Slide 16 — Ngăn mục "3. Schema & Warehousing"
*(3 giây)*

### Slide 17 — "Entity Resolution theo khoảng cách toạ độ khớp được 22/26 trạm ISD với GHCN"
*(35 giây)*

> Đây là phần áp dụng trực tiếp lý thuyết Entity Resolution đã học. Vấn đề: GHCN và NOAA ISD là hai
> cơ quan khác nhau, gán hai mã trạm độc lập cho cùng một vị trí vật lý — không thể nối bằng khoá vì
> không có khoá chung. Nhóm dùng khoảng cách Haversine, tìm trạm gần nhất trong ngưỡng 5 km, khớp
> được **22 trên 26 cặp**, khoảng cách trung bình chỉ 0,53 km. Nhiều cặp khớp đúng tại 0,000 km —
> xác nhận đây thật sự là cùng một trạm vật lý, không phải trùng hợp ngẫu nhiên.

### Slide 18 — "Đối chiếu 108 nghìn cặp trạm–ERA5..."
*(30 giây)*

> Nhóm cũng kiểm chuẩn xem ERA5 — dữ liệu lưới — nội suy vào vị trí trạm có đáng tin không, bằng
> cách so với giá trị trạm thật đo được, trên 108 nghìn cặp quan sát. Kết quả: nhiệt độ và gió nội
> suy chấp nhận được, sai số khoảng 1 độ C và 1 m/s. Nhưng **mưa thì không** — sai số lên tới gần 20
> mm, vì mưa biến thiên rất cục bộ mà lưới ERA5 có độ phân giải 0,25 độ không bắt được. Đây là lý do
> nhóm luôn ưu tiên dùng trạm thật cho mưa, chỉ dùng ERA5 cho mưa khi không còn lựa chọn khác.

### Slide 19 — "Cache giúp truy vấn Spark SQL nhanh hơn 69% thật"
*(20 giây)*

> Về tối ưu Spark: mục tiêu đặt trước là cache phải tăng tốc ít nhất 30%. Đo thật cho kết quả 69,4%
> — vượt ngưỡng, từ 0,36 giây xuống 0,11 giây.

### Slide 20 — "Giảm data skew từ 11,1% xuống 0,9% khả thi nhưng đánh đổi 12 lần số partition"
*(30 giây — thể hiện nhóm biết đánh giá đánh đổi, không chỉ chọn phương án "đẹp số liệu nhất")*

> Một quyết định kỹ thuật thú vị: nhóm thử chia nhỏ partition hơn, từ 109 xuống còn phân theo cả
> năm-tháng-nguồn, được 1.306 partition — giảm được độ lệch tải từ 11,1% xuống 0,9%, con số đẹp hơn
> nhiều. Nhưng đo thật tốc độ truy vấn thì **chậm hơn**, vì 1.306 partition làm nặng thêm vấn đề
> "nhiều file nhỏ". Nhóm quyết định **giữ nguyên** cách chia cũ — chọn đúng, không chọn con số đẹp.

---

## 4. Spark, Streaming & PINN (8:10 – 10:10)

### Slide 21 — Ngăn mục "4. Spark, Streaming & PINN"
*(3 giây)*

### Slide 22 — "PINN trường gió chưa vượt baseline hồi quy thuần về RMSE"
*(30 giây — nói thẳng kết quả không đạt, đây là điểm mạnh về sự trung thực)*

> Phần tuỳ chọn: nhóm thử Physics-Informed Neural Network cho trường gió, ràng buộc bằng phương
> trình liên tục rút gọn từ Navier-Stokes. Kết quả thật: ở quy mô dữ liệu hiện tại — chỉ một lát cắt
> không gian tại một thời điểm — PINN **chưa vượt được** mô hình hồi quy thuần không ràng buộc vật
> lý, chênh lệch khoảng 1% trên tập kiểm tra, chưa đủ để kết luận mô hình nào tốt hơn. Nhóm báo cáo
> đúng kết quả này thay vì chỉ chọn cấu hình làm đẹp số liệu.

### Slide 23 — "Spark Structured Streaming tính đúng cửa sổ trượt 1 phút"
*(20 giây)*

> Nhóm cũng dựng một cụm Spark và Kafka giả lập — ba container trên một máy vật lý, không phải ba
> máy thật, nhóm nói rõ điều này. Streaming tính đúng nhiệt độ trung bình theo cửa sổ trượt một
> phút, bước nhảy 30 giây, đã kiểm thử trực tiếp thành công.

### Slide 24 — "Phát hiện dị thường theo luồng: cảnh báo hiện ra dần... khớp 100% với batch"
*(25 giây)*

> Trên hạ tầng đó, nhóm phát lại đúng đợt nắng nóng tháng 4-5/2024 vào Kafka, Spark Streaming tính
> dị thường ngay trong từng micro-batch. Kết quả: **179 trên 179 cảnh báo khớp tuyệt đối** với kết
> quả tính bằng batch — vì hai đường xử lý dùng chung một công thức. Cảnh báo cực đoan nhất: một trạm
> Thái Lan ghi 38,6 độ C ngày 30/4, lệch 3,53 lần độ lệch chuẩn so với nền khí hậu.

---

## Phát hiện dị thường khí hậu (10:10 – 12:40)

### Slide 25 — Ngăn mục "Phát hiện dị thường khí hậu"
*(3 giây)*

### Slide 26 — "Nắng nóng và Yagi rõ rệt, hạn Mekong chỉ có tín hiệu yếu"
*(40 giây — slide trung tâm của phần "Value", nói kỹ)*

> Đây là phần trả lời câu hỏi "vì sao cần hệ thống này" — ba sự kiện khí hậu thật đã biết trước,
> dùng để kiểm chứng hệ thống có phát hiện đúng không.
>
> **Nắng nóng tháng 4-5/2024**: biểu đồ bên trái cho thấy năm 2024 vọt lên 11,2% số ngày bất thường
> tính trên cả năm — vượt trội hẳn mọi năm khác từ 2016. Còn riêng hai tháng 4-5, tỷ lệ là 12,3%,
> gấp 10 lần so với cùng kỳ giai đoạn nền 1991-2020. 29 trên 34 trạm có đợt nóng kéo dài, có nơi tới
> 30 ngày liên tục.
>
> **Bão Yagi, 7/9/2024**: áp suất ERA5 tụt xuống 978,8 hPa tại Hải Phòng — đúng nơi bão đổ bộ.
>
> **Hạn Mekong 2019-2020**: tín hiệu **yếu hơn** — chỉ số SPI âm đúng chiều hạn hán, nhưng vì chỉ có
> 2 trong 12 trạm đủ dữ liệu mưa rơi đúng vùng đang xét, nhóm không phóng đại kết luận thành "phát
> hiện rõ rệt" như hai sự kiện kia.

### Slide 27 — "Đối chứng bằng ERA5 và trạm lân cận tách được khí hậu thật khỏi cảm biến hỏng"
*(35 giây)*

> Một đóng góp nhóm tự hào: hệ thống không chỉ báo "có dị thường" mà còn **phân loại được** dị
> thường đó có đáng tin hay không, bằng cách đối chứng chéo với ERA5 và các trạm lân cận trong bán
> kính 200 km. Khi chỉ đối chiếu ERA5, số ca "dị thường khí hậu thật" là 5.380 — nhưng thêm trạm lân
> cận vào, con số tăng lên **20.357**, vì trạm lân cận phủ được cả giai đoạn trước 2020 khi chưa có
> ERA5.
>
> Ví dụ cụ thể: trạm ISD tại Phnom Penh ngày 3/7/2023 ghi áp suất dao động từ 995 đến 1054 hPa trong
> một ngày — dù đã qua kiểm soát chất lượng của chính NOAA — trong khi ERA5 cho thấy ngày đó hoàn
> toàn bình thường. Hệ thống kết luận đúng: đây là **cảm biến lỗi**, không phải một cơn bão.

### Slide 28 — "Bão Yagi: 7/9/2024 là ngày mưa lớn nhất 5 năm tại 4 trạm miền Bắc"
*(25 giây)*

> Về mưa do bão Yagi: tại cả bốn trạm miền Bắc kiểm tra — Hà Đông, Nội Bài, Phù Liễn, Cát Bi — ngày
> 7/9/2024 đều là ngày mưa lớn nhất trong toàn bộ chuỗi 5 năm 2020-2024, gấp 2,6 đến 3,1 lần ngưỡng
> bách phân vị 99. Một chi tiết thú vị: trạm GHCN Phù Liễn bị **mất số liệu đúng hai ngày bão đổ
> bộ** — rồi ghi nhận 214 mm ngay sau đó — cho thấy cả giới hạn thật của quan trắc mặt đất khi gặp
> thời tiết cực đoan.

### Slide 29 — "25/27 trạm ấm lên có ý nghĩa thống kê giai đoạn 1975–2024"
*(30 giây)*

> Tách riêng xu hướng khí hậu dài hạn khỏi dị thường ngắn hạn: dùng kiểm định Mann-Kendall và độ
> dốc Sen — phương pháp chuẩn trong khí hậu học, không giả định phân bố chuẩn. Kết quả: **25 trên 27
> trạm GHCN** có xu hướng ấm lên với ý nghĩa thống kê trong giai đoạn 1975-2024, trung vị **+0,21 độ
> C mỗi thập kỷ**. Quan trọng: sau khi đã tính tới xu hướng nền này, năm 2024 **vẫn nổi bật** — tức
> là đợt nóng 2024 không chỉ là hệ quả của xu hướng ấm lên dài hạn, mà là một dị thường thật sự.

### Slide 30 — "Chênh lệch trạm − ERA5 lộ ra cảm biến áp suất Phnom Penh nhảy bậc"
*(25 giây) **(*cắt được nếu thiếu giờ*)***

> Cuối cùng, kỹ thuật đồng nhất hoá chuỗi: vì biến động khí hậu thật có ở cả trạm lẫn ERA5 nên sẽ
> triệt tiêu khi lấy chênh lệch, phần còn lại là lỗi cảm biến. Biểu đồ cho thấy rõ cảm biến áp suất
> tại Phnom Penh **trôi dần** rồi có một bước nhảy khoảng −2,6 hPa từ cuối năm 2022. Mô phỏng tiêm
> lỗi vào 76 chuỗi dữ liệu thật đang ổn định cho thấy phương pháp phát hiện được 100% lỗi trôi dần và
> 95-98% lỗi nhảy bậc.

### Slide 31 — "EDA+PCA thật: PC2 của Open-Meteo tự lộ ra đúng 'chữ ký bão'"
*(25 giây)*

> Phân tích khám phá dữ liệu bằng PCA cho một phát hiện đẹp: thành phần chính thứ hai của Open-Meteo
> — kết hợp độ ẩm, lượng mưa và áp suất thấp cùng tăng giảm — hiện ra **tự nhiên từ dữ liệu**, không
> hề gán nhãn trước, và đúng là chữ ký thống kê của một cơn bão hoặc áp thấp nhiệt đới. Hai thành
> phần chính đầu chỉ giải thích 48 đến 56% phương sai — không phải trên 90% — cho thấy khí tượng
> Đông Nam Á có nhiều hơn hai trục biến động độc lập thật sự, đúng kỳ vọng vật lý chứ không phải mô
> hình chạy sai.

---

## 5. Dashboard (12:40 – 13:30)

### Slide 32 — Ngăn mục "5. Dashboard"
*(3 giây)*

### Slide 33 — "Dashboard Streamlit có 10 panel đọc kho Parquet"
*(15 giây)*

> Toàn bộ kết quả trên được trình bày qua một dashboard Streamlit mười panel, đọc trực tiếp từ kho
> dữ liệu thật, đã kiểm chứng chạy đúng trên trình duyệt, không lỗi.

### Slide 34, 35 — Ảnh chụp giao diện dashboard (panel 1, panel 7)
*(15 giây cho cả hai, nói nhanh — đây là ảnh chụp thật, không phải mockup)*

> Đây là ảnh chụp thật từ trình duyệt đang chạy, không phải ảnh dựng — panel tổng quan và panel dị
> thường khí hậu, số liệu đọc trực tiếp từ warehouse.

### Slide 36 — "Ba mốc chính thức đều có sản phẩm cụ thể theo từng người"
*(10 giây — đây sẽ là lúc nhóm chia vai nói phần của mình, không đọc hết bảng)*

> Đây là bảng phân công và tiến độ theo ba mốc chính thức của học phần — chi tiết từng người sẽ
> trình bày ở phần của mình.

---

## 6. Rủi ro, giới hạn & kết luận (13:30 – 15:00)

### Slide 37 — Ngăn mục "6. Rủi ro, giới hạn & kết luận"
*(3 giây)*

### Slide 38 — "Giới hạn hạ tầng nói thẳng trước khi bị hỏi"
*(30 giây — chủ động nói trước, không đợi hội đồng hỏi)*

> Nhóm chủ động nói rõ năm giới hạn hạ tầng thật, trước khi hội đồng hỏi. Kafka chỉ một broker, hệ số
> nhân bản bằng một — nên không chịu lỗi thật. Không có HDFS hay object storage — kho chỉ là một bản
> sao trên ổ cục bộ. AQE của Spark dùng cấu hình mặc định, chưa tự đo tách riêng hiệu quả. Entity
> Resolution có nhãn độc lập để kiểm chứng trên 15 trong 26 trạm ISD. Và mạng trạm còn thưa nên một
> phần dị thường chưa có đối chứng. Nhóm khẳng định rõ: **không điểm nào trong năm điểm này làm sai
> kết quả đã báo cáo** — chỉ giới hạn những gì có thể kết luận về hiệu năng và độ tin cậy hạ tầng.

### Slide 39 — "Đúng cho quy mô hiện tại, chưa sẵn sàng toàn cầu"
*(25 giây)*

> Nhìn xa hơn: thiết kế hiện tại — GAV đơn giản, Entity Resolution không cần Blocking, Spark một máy
> — là **lựa chọn đúng có điều kiện quy mô**, không phải thiết kế sẵn sàng cho toàn cầu. Nếu mở rộng
> thật, ví dụ GHCN có hơn 14 nghìn trạm toàn cầu, Entity Resolution sẽ bắt buộc cần kỹ thuật Blocking
> bằng LSH đã học ở Buổi 4, nếu không số cặp cần so khớp sẽ lên tới hàng trăm triệu.

### Slide 40 — "4/5 mục tiêu đạt đầy đủ, 1/5 đạt một phần"
*(35 giây — slide kết luận, nói chắc chắn và rõ ràng)*

> Tổng kết lại năm mục tiêu đã đặt ngưỡng từ đầu: **bốn trên năm mục tiêu đạt đầy đủ**. M1, kho đủ
> năm nguồn. M2, GAV và Entity Resolution/Survivorship có kiểm chứng định lượng — Entity Resolution
> đạt precision và recall 100% trên tập có nhãn, Survivorship đã thực sự sinh ra bảng giá trị đã hợp
> giải, 856 nghìn dòng. M3, cache vượt ngưỡng 30%. M5, dashboard chạy đúng. Riêng **M4 đạt một
> phần**: nắng nóng và bão Yagi tín hiệu rõ, nhưng hạn Mekong tín hiệu yếu vì thiếu trạm — nhóm không
> phóng đại kết quả này lên thành "đạt đầy đủ". Hướng phát triển tiếp theo: hạ tầng nhiều máy thật,
> mở rộng nhãn cho Entity Resolution, và hai ứng dụng nông nghiệp/năng lượng còn ở dạng đề xuất chưa
> cài đặt.
>
> Nhóm 16 xin cảm ơn thầy/cô và các bạn đã lắng nghe. Nhóm sẵn sàng trả lời câu hỏi.

### Slide 41 — "Thank you"
*(kết thúc)*

---

## Ghi chú cho người trình bày

- **Những con số hay bị hỏi lại, nên thuộc lòng**: 8.955.313 dòng; 119 vị trí, 9/11 nước ASEAN;
  540/540 file ERA5 qua CDS; 22/26 Entity Resolution; 69,4% tăng tốc cache; 179/179 streaming khớp
  batch; 25/27 trạm ấm lên +0,21°C/thập kỷ; 4/5 mục tiêu đạt đầy đủ.
- **Nếu hội đồng hỏi "Survivorship có thật sự sinh bảng kết quả không?"**: trả lời có — tên bảng
  `weatherobs_fused.parquet`, 856.452 dòng, 1 dòng/vị trí/ngày, có cột nguồn được chọn và cờ xung
  đột cho từng biến; ví dụ cụ thể nếu cần: truy vấn trạm Hà Nội ngày bão Yagi 7/9/2024 trả về đúng 1
  dòng.
- **Nếu bị hỏi "AQE có đo tách riêng chưa?"**: trả lời thẳng — chưa, nhóm dùng cấu hình mặc định, đây
  là một giới hạn đã nêu rõ ở Slide 38, không phải điều nhóm giấu.
- **Nếu bị hỏi về kho mã**: kho đã có lịch sử commit đầy đủ trên GitHub
  (`TatcataiTTN/IT5427-Nhom16-TichHopKhiTuong`) — nếu hội đồng không truy cập được, có thể do quyền
  riêng tư, cần kiểm tra lại trước buổi bảo vệ và chuyển sang public nếu cần.
