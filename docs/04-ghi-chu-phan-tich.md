# Ghi chú phân tích trước khi chốt đề xuất — đề tài khí tượng đa nguồn

## Bản chất vấn đề

Chuyển trọng tâm sang dữ liệu thời tiết **quá khứ** làm giảm áp lực về Velocity (tốc độ luồng dữ liệu), nhưng đẩy độ phức tạp của Volume và Variety lên mức cao nhất. Bản chất bài toán tích hợp ở đây là xử lý sự không đồng nhất về không gian và thời gian (**Spatio-Temporal Heterogeneity**) giữa dữ liệu viễn thám/tái phân tích dạng lưới và dữ liệu cảm biến điểm, nhằm tạo ra một bộ dữ liệu đồng nhất phục vụ phân tích và phát hiện dị thường khí hậu.

---

## Phân tích hai mặt

### Chiến lược thu thập và tính khả thi (mặt thuận lợi)

Dùng dữ liệu quá khứ cho phép thiết kế một pipeline ETL offline vững chắc, không phụ thuộc vào việc hứng luồng thời gian thực liên tục. Ba nhóm nguồn chính:

1. **Dữ liệu lưới không gian (Spatial Grid Data):** Copernicus Climate Data Store — bộ ERA5 của ECMWF. Tái phân tích khí quyển và bề mặt Trái Đất quy mô toàn cầu qua nhiều thập kỷ. Định dạng NetCDF/GRIB (đa chiều, cần kỹ năng bóc tách ma trận không gian).
2. **Dữ liệu chuỗi thời gian từ trạm mặt đất (Point Time-series Data):** NOAA GHCN/ISD. Nhiệt độ, lượng mưa, độ ẩm hàng ngày/giờ từ hàng chục nghìn trạm quan trắc. Định dạng CSV/TXT.
3. **Dữ liệu bức xạ & năng lượng:** NASA POWER — bức xạ mặt trời, nhiệt độ phục vụ nông nghiệp/năng lượng, dùng làm nguồn thứ ba bổ sung góc nhìn về tương tác bề mặt–khí quyển.

Với cấu trúc này, công việc chia rõ: hai thành viên lo thu thập, giải mã cấu trúc (parsing) và đối sánh lược đồ (schema matching) giữa dữ liệu lưới và dữ liệu điểm; một thành viên tối ưu xử lý trên Spark và (tuỳ chọn) huấn luyện mô hình vật lý-học máy (PINN) từ tập dữ liệu lớn; thành viên còn lại xây dashboard trực quan hoá không gian địa lý.

### Lỗ hổng logic và rủi ro hệ thống (mặt trái)

Giả định "càng nhiều nguồn càng chi tiết càng tốt" chứa rủi ro thực tế trong tích hợp dữ liệu lớn: cố ép ghép dữ liệu dạng lưới (ô ~28km×28km của ERA5) với dữ liệu điểm (toạ độ chính xác một trạm cảm biến) sẽ tạo xung đột cấu trúc (**structural conflict**) không giải quyết được bằng phép JOIN thông thường. Thiếu mô hình nội suy không gian chuẩn xác sẽ sinh ra dữ liệu rác (poor quality data). Thêm vào đó, xử lý hàng chục năm dữ liệu NetCDF đa chiều nếu không có chiến lược quản lý bộ nhớ và phân mảnh dữ liệu (chunking) hợp lý sẽ làm tràn bộ nhớ và đánh sập luồng xử lý trước khi kịp phân tích.

---

## Câu hỏi chất vấn (chuẩn bị trước cho buổi báo cáo/bảo vệ)

1. Thu thập hàng loạt dữ liệu viễn thám và mặt đất chỉ là bước chuẩn bị nguyên liệu — vấn đề cốt lõi mà mô hình phân tích của nhóm giải quyết là gì cụ thể (ví dụ: mô phỏng/dự báo hiện tượng cực đoan theo khu vực, hay xây bộ dữ liệu chuẩn hoá phục vụ nghiên cứu khí hậu)?
2. Nhóm dùng kỹ thuật nào để đồng bộ thang đo (scale normalization) và xử lý giá trị khuyết thiếu (missing-value policy) khi hợp nhất một ô lưới bao phủ hàng chục km² với dữ liệu đo tại một toạ độ vật lý duy nhất?
3. Nếu chọn phạm vi dữ liệu đủ lớn để đạt quy mô Terabyte, hạ tầng máy tính của nhóm sẽ dùng cơ chế lưu trữ phân tán và phân mảnh dữ liệu (chunking/partitioning) như thế nào để tránh tràn bộ nhớ khi thực hiện Record Linkage giữa trạm và ô lưới?

---

## Các yếu tố thời tiết & định hướng xử lý riêng biệt/tích hợp

Thời tiết là một hệ động lực học phức tạp, gồm các nhóm biến: nhiệt động lực học (nhiệt độ, áp suất), độ ẩm/thuỷ văn (độ ẩm tương đối, lượng mưa), động lực học chất lưu (gió), và bức xạ/tương tác bề mặt (bức xạ mặt trời, độ che phủ mây). Tách rời các nhóm biến này giúp tối ưu hoá làm sạch dữ liệu ban đầu (mỗi nhóm có missing-value policy và chuẩn hoá đơn vị riêng), nhưng để mô phỏng chính xác sự biến đổi của hệ thống, việc tích hợp nên được dẫn dắt bởi các nguyên lý vật lý cơ bản thay vì chỉ ghép nối dữ liệu thuần tuý (Data Merging đơn thuần bỏ qua các ràng buộc tương quan phi tuyến giữa các biến).

Đây là lý do đề xuất chính thức đưa Physics-Informed Neural Networks (PINN) vào như một điểm nhấn học thuật tuỳ chọn: các phương trình vi phân riêng phần (Clausius-Clapeyron cho quan hệ nhiệt độ–độ ẩm, Navier-Stokes rút gọn cho chuyển động gió) được nhúng vào hàm mất mát, giúp mô hình học máy không sinh ra kết quả phi logic về mặt vật lý. Khi cân bằng trọng số giữa Data Loss (nhiều sai số đo lường thực tế) và Physics Loss (mang tính lý tưởng hoá), nhóm cần thử nghiệm nhiều giá trị λ và chọn dựa trên metric validation — đây cũng là một câu hỏi phản biện nên chuẩn bị trước.

---

## Vì sao không dùng từ "vi khí hậu" trong tên đề tài

Bản nháp ban đầu dùng "vi khí hậu" (microclimate) — thuật ngữ chỉ khí hậu ở quy mô không gian rất nhỏ (mét đến vài km, ví dụ trong một thung lũng/tán rừng/khu phố). Dữ liệu thực tế của nhóm (lưới ERA5 ~28km/ô, ghép với trạm điểm) ở quy mô **khu vực (regional/meso-scale)**, chênh lệch hàng trăm lần so với quy mô vi mô thật sự — dùng "vi khí hậu" sẽ không khớp với phần định lượng 5V đã khai báo và dễ bị phản biện chất vấn. Tên đề tài chính thức vì vậy chuyển sang mô tả đúng bản chất: tích hợp dữ liệu khí tượng lịch sử để **phát hiện dị thường khí hậu** và **hỗ trợ ra quyết định** cho các bài toán ứng dụng cụ thể.

## Kết luận sơ bộ dẫn tới đề xuất chính thức

Chốt hướng: **Hệ thống tích hợp và xử lý dữ liệu khí tượng đa nguồn phục vụ phát hiện dị thường khí hậu và hỗ trợ ra quyết định đa ngành khu vực Đông Nam Á**, tích hợp ERA5 (lưới tái phân tích) với NOAA ISD/GHCN (trạm mặt đất) và NASA POWER (bức xạ) thành một kho dữ liệu chuẩn hoá, xử lý bằng Apache Spark (batch + Structured Streaming giả lập), có tuỳ chọn mô hình vật lý-học máy (PINN) và dashboard trực quan hoá theo không gian/thời gian. Ảnh vệ tinh (SAR/quang học/khí tượng) được giữ như nguồn mở rộng tùy chọn, không bắt buộc trong lõi tiến độ.

Nội dung đầy đủ (nguồn dữ liệu, kiến trúc, 5V, phân công, timeline) đã được viết thành đề xuất chính thức trong file `01-de-xuat-de-tai.md` cùng thư mục.
