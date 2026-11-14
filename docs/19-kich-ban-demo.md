# Kịch bản demo (chuẩn bị sẵn — không trình bày trong bài, chỉ chạy nếu được yêu cầu)

**Căn cứ đúng yêu cầu gốc** (thông báo Teams của giảng viên, 22:51 tối trước): *"Trình bày báo cáo
không cần demo nhưng cần chỉ rõ tiến trình thực hiện cũng như kết quả đánh giá thực nghiệm. Tuy
nhiên cần chuẩn bị source code và môi trường demo nếu được yêu cầu."*

→ Không đưa demo vào 15 phút trình bày chính (phần "tiến trình + kết quả thực nghiệm" đã có đủ
trong slide và script thuyết trình). Tài liệu này là **runbook dự phòng**: nếu hội đồng yêu cầu xem
code chạy thật, mở file này, copy đúng lệnh, không cần nhớ.

Tất cả lệnh dưới đây chạy từ thư mục gốc dự án:
`cd "/Users/tuannghiat/Downloads/HUST - Tích hợp và xử lý dữ liệu lớn - Vũ Tuyết Trinh/IT5427-Nhom16-TichHopKhiTuong"`

---

## Trước buổi bảo vệ — chuẩn bị 1 lần (không làm lúc đang hỏi-đáp)

1. Mở Docker Desktop, đợi daemon chạy xong (biểu tượng chuyển xanh) — **chỉ cần nếu hội đồng có thể
   hỏi về Kafka/Spark cluster/streaming**. Việc này mất 30 giây đến 1 phút, không làm được trong lúc
   đang trả lời câu hỏi.
2. Chạy thử cả 4 kịch bản dưới đây **ít nhất 1 lần** trước 15/11 (đúng việc "dry-run" đã lên kế hoạch
   nhưng chưa làm) — đo lại thời gian thật trên máy sẽ mang đi bảo vệ, vì máy khác có thể chậm/nhanh
   hơn máy đã đo ở đây.
3. Mở sẵn 2-3 tab terminal, mỗi tab `cd` sẵn vào đúng thư mục trên, để không mất thời gian gõ lại khi
   đang bị hỏi.

---

## Kịch bản 1 — Entity Resolution + Survivorship (khuyến nghị dùng đầu tiên: nhanh nhất, ít rủi ro nhất)

**Khi nào dùng**: hội đồng hỏi "Survivorship có thật sự sinh ra bản ghi nào không?", "truy vấn 1 vị
trí/1 ngày trả về mấy dòng?", hoặc bất kỳ câu nào về Entity Resolution/Survivorship.

**Đã kiểm chứng thật**: chạy xong trong **dưới 2 giây**, không cần Docker, không cần mạng.

```bash
/opt/homebrew/bin/python3 -c "
import duckdb
q = '''
SELECT location_id, day, temp_c, temp_c_source_used, temp_c_conflict,
       precip_mm, precip_mm_source_used,
       pressure_surface_hpa, pressure_surface_hpa_source_used
FROM read_parquet('warehouse/output/weatherobs_fused.parquet')
WHERE location_id = 'VMM00048820' AND day = '2024-09-07'
'''
print(duckdb.sql(q).df().to_string(index=False))
"
```

**Kết quả đúng sẽ thấy** (đây là trạm Hà Nội, ngày bão Yagi đổ bộ):

```text
location_id        day  temp_c temp_c_source_used  temp_c_conflict  precip_mm precip_mm_source_used  pressure_surface_hpa pressure_surface_hpa_source_used
VMM00048820 2024-09-07    25.9               GHCN            False   8.479337                  ERA5            989.208264                             ERA5
```

**Nói gì khi chạy xong**: "Đúng 1 dòng cho 1 vị trí/1 ngày. Nhiệt độ lấy từ GHCN vì GHCN hạng ưu
tiên cao nhất và có giá trị hôm đó; mưa và áp suất GHCN không đo nên tự động rơi xuống ERA5 — đúng
cơ chế Survivorship đã trình bày. Cột `_conflict` cho biết ngày đó các nguồn có đồng thuận không."

Muốn đổi sang trạm/ngày khác: sửa `location_id` và `day` trong câu lệnh — bất kỳ 119 vị trí nào
trong bảng `warehouse/output/location.parquet` đều dùng được.

---

## Kịch bản 2 — PINN trường gió (inference, không train lại từ đầu nếu sợ mất thời gian)

**Khi nào dùng**: hội đồng hỏi về PINN, về kết quả "PINN chưa vượt baseline".

**Đã kiểm chứng thật**: toàn bộ script (gồm cả việc quét 4 giá trị λ) chạy xong trong **4,8 giây**
trên máy chính — dưới xa ngưỡng 3 phút đã đặt trong kế hoạch.

```bash
python3 model/pinn_wind_field_v2.py
```

**Kết quả đúng sẽ thấy** (khớp đúng số đã có trong báo cáo/slide):

```text
lambda=0.0   test_RMSE=1.0473  ...
lambda=0.1   test_RMSE=1.0577  ...
=> PINN KHONG tot hon baseline tren RMSE thuan tuy (1.0% kem hon) ...
PASS n_lambda_tested=4 best_lambda=0.0
```

**Nói gì khi chạy xong**: "Đây là script thật, không phải số đã lưu sẵn — chạy lại từ đầu, quét 4
giá trị λ cân bằng giữa khớp dữ liệu và ràng buộc vật lý Navier–Stokes rút gọn, baseline λ=0 vẫn
thắng nhẹ về RMSE thuần — đúng kết luận trung thực đã trình bày, không chọn cấu hình đẹp số liệu."

---

## Kịch bản 3 — Streaming Kafka + Spark Structured Streaming (nặng nhất, cần Docker đã bật sẵn)

**Khi nào dùng**: hội đồng hỏi cụ thể về Kafka, Spark Streaming, tính velocity.

**Bắt buộc làm trước** (xem mục "Trước buổi bảo vệ" ở trên) — Docker Desktop phải đã chạy từ trước,
không bật kịp trong lúc đang hỏi-đáp.

```bash
# Bước 1 — bật Kafka broker (nếu Docker đã bật sẵn, bước này ~10-15 giây)
docker compose -f docker-compose.kafka.yml up -d

# Bước 2 — phát lại đúng đợt nắng nóng 4-5/2024 vào Kafka
python3 ingestion/kafka_producer.py --source GHCN --start 2024-04-01 --end 2024-05-15 --limit 0 \
    --topic weatherobs.ghcn.replay

# Bước 3 — Spark Structured Streaming đọc Kafka, phát hiện dị thường theo luồng, 60 giây
python3 warehouse/spark_streaming_anomaly.py --topic weatherobs.ghcn.replay --duration 60
```

**Kết quả đúng sẽ thấy**: cảnh báo `|z| >= 2` xuất hiện dần qua các micro-batch trên console, tổng
cộng 179 cảnh báo khi phát lại hết — khớp đúng số đã nêu trong báo cáo/slide (đã kiểm thử trực tiếp
thành công trước đó, xem Mục 6.6 báo cáo).

**Nếu hội đồng chỉ hỏi nhanh, không cần đợi đủ 60 giây**: có thể dừng bằng Ctrl+C sau khi thấy vài
cảnh báo đầu xuất hiện — đủ để chứng minh pipeline chạy thật, không cần chạy hết.

**Rủi ro thật cần biết trước**: nếu mạng Wi-Fi phòng báo cáo chặn cổng Docker hoặc máy không cài kịp
Docker Desktop, kịch bản này **không chạy được tại chỗ** — đây là lý do kịch bản 1 và 2 (không cần
Docker) nên ưu tiên dùng trước nếu có thể chọn.

---

## Kịch bản 4 — Dashboard Streamlit (trực quan nhất, dễ gây ấn tượng nhất nếu còn giờ)

**Khi nào dùng**: hội đồng muốn "xem thử hệ thống" một cách tổng quát, không hỏi sâu kỹ thuật.

```bash
streamlit run dashboard/app.py
```

Đợi terminal in ra địa chỉ `http://localhost:8501`, mở trình duyệt. Dẫn hội đồng qua đúng panel đã
chụp ảnh trong slide: **Panel 1** (tổng quan 5 nguồn) và **Panel 7** (dị thường khí hậu — gõ vào ô
chọn trạm bất kỳ trong 119 trạm, chọn khoảng ngày 4-5/2024, chỉ vào biểu đồ tỷ lệ ngày bất thường
tăng vọt năm 2024).

**Lưu ý nói rõ nếu được hỏi**: dashboard đang đọc kho Parquet đầy đủ (8,96 triệu dòng, không phải
bản rút gọn dùng để chụp ảnh slide trước đây) — nếu load lần đầu chậm vài giây do đọc file lớn, nói
luôn lý do thay vì để im lặng khó xử.

---

## Nếu không kịch bản nào chạy được tại chỗ (lỗi mạng, lỗi máy, hết thời gian)

Không cố sửa lỗi trước mặt hội đồng quá 30 giây. Nói thẳng: *"Môi trường demo gặp sự cố kỹ thuật
ngay lúc này — toàn bộ kết quả này đã được chạy thật và ghi lại trong báo cáo ở Mục [X] kèm lệnh tái
lập, và ảnh chụp dashboard thật ở slide [Y]"* — rồi quay lại đúng trang báo cáo/slide tương ứng. Hội
đồng quan tâm bằng chứng đã có sẵn hơn là cố demo bằng được khi môi trường không hợp tác.

| Kịch bản | Bằng chứng tĩnh thay thế nếu demo lỗi |
| --- | --- |
| 1. ER/Survivorship | Báo cáo Mục 6.2, Bảng 6.2 + đoạn ví dụ Hà Nội/Yagi |
| 2. PINN | Báo cáo Mục 6.5, slide "PINN trường gió chưa vượt baseline" |
| 3. Streaming | Báo cáo Mục 6.6, slide "179/179 khớp batch" |
| 4. Dashboard | Slide ảnh chụp Panel 1 và Panel 7 (đã có sẵn, không cần máy chạy) |
