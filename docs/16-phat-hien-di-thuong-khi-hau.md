# Phát hiện dị thường khí hậu — phương pháp và kết quả kiểm chứng

Mục tiêu chính trong tên đề tài ("phát hiện dị thường khí hậu", `docs/01` mục 2). Code:
`warehouse/anomaly_detection.py` (Spark + pandas), unit test `tests/test_anomaly.py` (9 test),
hiển thị ở dashboard mục 4. Số liệu dưới đây lấy từ lần chạy thật ngày 13/10/2026 trên warehouse
đầy đủ (8.955.315 bản ghi, đã qua kiểm soát chất lượng ở Ingestion — `docs/17`) — chạy hết ~45 giây.

```bash
python3 warehouse/anomaly_detection.py   # cần warehouse/output/weatherobs.parquet (build_warehouse.py)
python3 warehouse/climate_trends.py      # xu hướng dài hạn (mục 6)
python3 warehouse/sensor_drift.py        # trôi cảm biến (mục 7)
```

---

## 1. Phương pháp

Nguyên tắc: một giá trị chỉ "dị thường" khi so với **khí hậu bình thường của chính nơi đó, vào đúng
thời điểm đó trong năm** — 35°C ở Hà Nội tháng 6 là bình thường, tháng 1 thì không. Mọi ngưỡng đều
lấy từ chuẩn khí tượng quốc tế, không tự đặt.

| Bước | Cách làm | Ghi chú |
|---|---|---|
| 1. Tổng hợp theo ngày (Spark) | 9,0 triệu bản ghi → 977.239 ngày × vị trí × nguồn: nhiệt độ TB ngày, tổng mưa, gió max, áp suất MSL thấp nhất | Ngày của nguồn đo theo giờ (ISD, ERA5, Open-Meteo) chỉ hợp lệ khi có quan trắc ở **đủ 4 khối 6 giờ** — tránh trung bình bị lệch nóng khi thiếu số liệu ban đêm |
| 2. Khí hậu nền (Spark) | Theo (vị trí, nguồn, ngày-trong-năm), cửa sổ trượt **±15 ngày**: trung bình, độ lệch chuẩn, bách phân vị 90 | Mỗi ngày nền được nhân thành 31 bản ghi lệch ngày rồi `groupBy` — chạy phân tán. 29/2 gộp vào 28/2 |
| 3. Dị thường chuẩn hoá | z = (x − TB nền) / ĐLC nền; \|z\| ≥ 2 bất thường, ≥ 3 cực đoan | Áp dụng cho nhiệt độ TB ngày và áp suất MSL thấp nhất ngày |
| 4. Đợt nóng | ≥ 3 ngày liên tiếp nhiệt độ TB ngày > bách phân vị 90 của nền | Chỉ số **TG90p** của ETCCDI (WMO), gom thành đợt. Ngày *thiếu dữ liệu* ≤ 1 ngày giữa 2 ngày nóng được nối qua (thiếu số liệu ≠ trời mát); ngày *có dữ liệu mà không nóng* làm đứt đợt |
| 5. Hạn/ẩm — SPI | SPI-1, SPI-3 (McKee 1993): khớp **phân bố gamma** theo từng tháng trên nền 1991–2020, xử lý riêng xác suất tháng không mưa | Mưa không có phân bố chuẩn nên **không** dùng z-score. Tháng thiếu > 10% số ngày bị loại |
| 6. Xác nhận chéo đa nguồn | Dị thường tại trạm (GHCN/ISD) đối chiếu với ERA5 nội suy tại **cùng vị trí, cùng ngày** | Xem mục 3 — đây là phần gắn trực tiếp với nội dung tích hợp dữ liệu của học phần |

**Giai đoạn nền theo nguồn:**

| Nguồn | Nền | Ghi chú |
|---|---|---|
| GHCN | **1991–2020** | Chuẩn khí hậu WMO 30 năm. 32 trạm có ≥ 15 năm nhiệt độ trong nền và đủ số liệu 2024 |
| ISD | 2015–2024 | Nền ngắn (cờ `nen_ngan`) |
| ERA5, Open-Meteo, NASA POWER | 2020–2024 | Nền ngắn — năm cần đánh giá nằm *trong* nền nên z bị kéo về 0; chỉ dùng để so sánh tương đối và xác nhận chéo, không dùng làm kết luận khí hậu |

## 2. Kiểm chứng với sự kiện có thật

### 2.1. Nắng nóng tháng 4–5/2024 trên toàn ĐNA

34 trạm GHCN, so với nền WMO 1991–2020:

| Chỉ số | 4/2024 – 15/5/2024 | Cùng kỳ 1991–2020 |
|---|---|---|
| Tỷ lệ ngày nóng bất thường (z ≥ 2) | **12,3%** | 1,2% (gấp **10 lần**) |
| z trung bình | +0,99 | ~0 |
| Số trạm có đợt nóng | **29/34** | |

**2024 nổi bật hẳn so với mọi năm khác** (tỷ lệ ngày z ≥ 2 trong tháng 4–5) — chứng tỏ hệ thống bắt
được sự kiện thật chứ không chỉ phản ánh xu hướng ấm lên dài hạn:

| 2016 | 2019 | 2020 | 2021 | 2022 | **2023** | **2024** | 2025 |
|---|---|---|---|---|---|---|---|
| 3,5% | 3,9% | 2,4% | 0,8% | 0,4% | 4,1% | **11,2%** | 0,8% |

(Các năm 2010–2025 khác đều ≤ 2,7%. 2016 và 2023–2024 là các năm El Niño.)

**Đợt nóng dài nhất 2024:** Thái Lan (TH000048564) 30 ngày nóng liên tục 3/4–3/5; TP.HCM (Tân Sơn Hoà,
VM000048900) 27 ngày 7/4–4/5; Phan Thiết 26 ngày; một trạm Thái Lan khác 25 ngày; Penang (Malaysia)
22 ngày. Ngày bất thường nhất: trạm Thái Lan 38,6°C ngày 30/4 (nền 30,2°C, z = +3,5); Vinh 35,8°C
(nền 26,9°C, z = +3,2).

### 2.2. Bão Yagi, 6–8/9/2024

ERA5 nội suy tại 8 trạm miền Bắc Việt Nam: áp suất MSL thấp nhất **978,8 hPa** tại Cát Bi (Hải Phòng),
**z = −7,2**; Phù Liễn (Hải Phòng) 979,8 hPa, z = −7,0; **88% số trạm có z ≤ −3**. Hai trạm lệch nhất
đều ở Hải Phòng — đúng khu vực bão đổ bộ.

### 2.3. Hạn hán Mekong 2019–2020

Chỉ 2 trạm GHCN trong vùng Mekong có đủ số liệu mưa cho SPI. SPI-3 trung bình 6/2019–5/2020 là
**−0,59**; tỷ lệ tháng hạn (SPI-3 ≤ −1) **22%**, so với 13% của toàn chuỗi. Đúng chiều nhưng tín hiệu
yếu vì quá ít trạm — **hạn chế cần nêu trong báo cáo**: GHCN thiếu nhiều số liệu mưa ở ĐNA (chỉ 12
trạm đủ điều kiện tính SPI).

## 3. Xác nhận chéo đa nguồn — tích hợp dữ liệu để phân biệt khí hậu thật và lỗi dữ liệu

| Trạm | ERA5 cùng vị trí, cùng ngày | Phân loại | Số trường hợp |
|---|---|---|---|
| Bất thường | Cùng chiều, \|z\| ≥ 1 | `xac_nhan_khi_hau` — tín hiệu khí hậu thật trên diện rộng | **5.380** |
| Cực đoan (\|z\| ≥ 3) | Gần bình thường (\|z\| < 0,5) hoặc ngược chiều | `nghi_loi_du_lieu` — nghi lỗi cảm biến/ghi chép | **23** |
| Bất thường | Lệch nhẹ | `chua_xac_dinh` — dị thường cục bộ, ERA5 (~28 km) có thể không bắt được | 507 |
| Bất thường | Không có (trước 2020) | `khong_co_era5` | 34.453 |

**Ví dụ lỗi dữ liệu thật phát hiện được:** trạm ISD Phnom Penh (48991099999) ngày 3/7/2023. Giá trị
thấp nhất 981,6 hPa đã bị chính NOAA gắn mã QC "nghi ngờ" nên bị loại ngay ở Ingestion (`docs/17` mục 3).
Nhưng các giá trị *đạt* QC của NOAA cùng ngày vẫn dao động 995,0–1053,6 hPa (nhảy 25 hPa trong 3 giờ):
áp suất thấp nhất ngày **995,0 hPa (z = −5,5)** trong khi ERA5 cùng vị trí *bình thường* (z = +1,6) —
không có bão nào qua Phnom Penh hôm đó. Trạm này có 13 ngày bị đánh giá nghi lỗi, dày đặc trong
6–9/2023 (z ≈ −3,2 đến −5,5) khi ERA5 vẫn bình thường → dấu hiệu **cảm biến áp suất hỏng/trôi**, khớp với
kết quả phát hiện trôi cảm biến ở mục 7.

Ý nghĩa với học phần: một nguồn đơn lẻ không thể tự phân biệt "khí hậu cực đoan thật" với "cảm biến
hỏng". Khi **tích hợp** trạm điểm với lưới tái phân tích qua Record Linkage không-thời gian
(nội suy ERA5 vào đúng `location_id` của trạm), hai trường hợp này tách được ra.

## 4. Mưa cực đoan (chỉ số ETCCDI)

Mưa không có phân bố chuẩn nên không dùng z-score. Theo ETCCDI: **ngày ướt** là ngày ≥ 1 mm; ngưỡng
**p95 / p99** tính trên các ngày ướt của giai đoạn nền, theo từng vị trí–nguồn (160 vị trí–nguồn đủ
≥ 100 ngày ướt). Ngày vượt p95 là mưa lớn, vượt p99 là mưa cực đoan. Chỉ số năm: PRCPTOT (tổng mưa
ngày ướt), Rx1day (mưa ngày lớn nhất), R95p / R99p (tổng mưa của các ngày vượt ngưỡng), R95pTOT (% đóng
góp của mưa lớn); năm thiếu > 10% số ngày bị loại. Output: `precip_extremes_daily.parquet`,
`precip_indices_annual.parquet`.

**Kiểm chứng — mưa do bão Yagi:** ngày **7/9/2024 là ngày mưa lớn nhất của cả chuỗi ERA5 2020–2024**
(hạng 1) tại 5 trạm miền Bắc Việt Nam, tới **222,6 mm** — gấp khoảng **3 lần ngưỡng p99**; 11/13 cặp
trạm–nguồn vượt p99 trong 6–11/9/2024. Trạm GHCN Phù Liễn (Hải Phòng) **mất số liệu đúng 7–8/9** (lúc bão
đổ bộ) rồi ghi 214 mm ngày 11/9.

## 5. Xác nhận chéo bằng trạm lân cận

Đối chứng thứ hai, độc lập với ERA5: các trạm GHCN/ISD khác trong bán kính **200 km** (mạng trạm ĐNA
thưa — 43/61 trạm có ≥ 1 láng giềng ở bán kính này). Cặp cách nhau < 5 km bị loại: đó là cùng một trạm
vật lý được GHCN và ISD gán hai mã (Entity Resolution) — cùng cảm biến, không phải bằng chứng độc lập.
92 cặp trạm lân cận.

Phân loại tổng hợp (`xac_nhan_tong_hop`): xác nhận khi ERA5 cùng chiều **hoặc** ≥ 50% trạm lân cận cùng
chiều (|z| ≥ 1); nghi lỗi dữ liệu khi trạm cực đoan và **mọi** đối chứng hiện có đều không ủng hộ.

| Phân loại | Chỉ ERA5 | ERA5 + trạm lân cận |
|---|---|---|
| Xác nhận khí hậu thật | 5.380 | **20.357** |
| Dị thường cục bộ / chưa xác định | 507 | 3.725 |
| Nghi lỗi dữ liệu | 23 | 343 |
| Không có đối chứng | 34.453 | **15.938** |

Trạm lân cận phủ được giai đoạn trước 2020 (chưa có ERA5): 14.842 dị thường từng không có đối chứng nay
được xác nhận. 3 ca từng bị nghi lỗi (chỉ dựa ERA5) được trạm lân cận lật lại thành khí hậu thật.

## 6. Xu hướng khí hậu dài hạn (`warehouse/climate_trends.py`)

Tách biến đổi khí hậu dài hạn khỏi dị thường ngắn hạn. **Kiểm định Mann-Kendall** (hiệu chỉnh giá trị
trùng) cho ý nghĩa thống kê, **độ dốc Sen** cho tốc độ (°C/thập kỷ) — cả hai phi tham số, bền với
outlier. Nhiệt độ trung bình năm (năm hợp lệ khi ≥ 80% ngày có số liệu), tối thiểu 30 năm.

| Giai đoạn | Số trạm | Ấm lên có ý nghĩa (p < 0,05) | Độ dốc Sen trung vị |
|---|---|---|---|
| 1975–2024 (chung, so sánh công bằng) | 27 | **25** | **+0,21 °C/thập kỷ** |
| Toàn bộ chuỗi | 28 | 24 | +0,17 °C/thập kỷ |

Ấm lên nhanh nhất 1975–2024: Jakarta +0,41; Penang +0,35; Bangkok +0,35; Cao Bằng +0,34; Chiang Mai
+0,33 °C/thập kỷ. Xu hướng mưa (PRCPTOT, Rx1day) chỉ có 1–6 trạm đủ 30 năm số liệu mưa — không đủ để
kết luận. *Hạn chế:* Mann-Kendall giả định chuỗi không tự tương quan (chưa dùng hiệu chỉnh
Hamed–Rao); nhiệt độ GHCN là TAVG hoặc (TMAX+TMIN)/2, nếu một trạm đổi cách tính giữa chừng có thể tạo
xu hướng giả — mục 7 phát hiện được dạng lỗi này khi có ERA5 đối chiếu.

## 7. Phát hiện trôi cảm biến (`warehouse/sensor_drift.py`, TV1 Tuần 3 #3)

Kỹ thuật đồng nhất hoá chuỗi khí hậu: chuỗi **bias tháng = trạm − ERA5** tại cùng vị trí, cùng ngày.
Biến động khí hậu thật có ở cả hai nên bị triệt tiêu; phần còn lại là lỗi cảm biến/điểm đo.
Trôi dần: Mann-Kendall + độ dốc Sen; nhảy bậc: **kiểm định Pettitt**. Gắn cờ khi p < 0,05 **và** vượt
ngưỡng vật lý (nhiệt độ 0,3 °C/năm hoặc bước 0,5 °C; áp suất 0,5 hPa/năm hoặc bước 1 hPa).

| Trạm | Biến | Kết luận | Chi tiết |
|---|---|---|---|
| ISD Phnom Penh (Campuchia) | Áp suất MSL | **Trôi** | −0,65 hPa/năm, điểm gãy 11/2022, bước −2,6 hPa |
| ISD Wattay, Viêng Chăn (Lào) | Nhiệt độ | Nhảy bậc | −0,52 °C từ 2/2022 |
| ISD Cần Thơ (Việt Nam) | Nhiệt độ | Nhảy bậc | −0,52 °C từ 11/2021 |
| GHCN THW00041018 (Thái Lan) | Nhiệt độ | Nhảy bậc | −0,69 °C từ 5/2022 |

Trạm Phnom Penh khớp với ca nghi lỗi phát hiện độc lập ở mục 3. **Kiểm chứng bằng mô phỏng** (đúng tiêu
chí kế hoạch): tiêm trôi / bước nhảy gấp 2 lần ngưỡng vào 76 chuỗi thật đang ổn định → phát hiện
**100% trôi** và **95–98% nhảy bậc**.

## 8. Phát hiện dị thường theo luồng (`warehouse/spark_streaming_anomaly.py`)

Kafka → Spark Structured Streaming → cảnh báo: producer phát lại bản ghi GHCN; mỗi micro-batch (giới
hạn `maxOffsetsPerTrigger` để cảnh báo xuất hiện dần) được join tĩnh với khí hậu nền
(`climatology.parquet`, lưu từ pipeline batch), tính z và phát cảnh báo |z| ≥ 2 ra console và
`stream_alerts.parquet`.

```bash
python3 ingestion/kafka_producer.py --source GHCN --start 2024-04-01 --end 2024-05-15 --limit 0 --topic weatherobs.ghcn.replay
python3 warehouse/spark_streaming_anomaly.py --topic weatherobs.ghcn.replay --duration 60
```

Phát lại đợt nắng nóng 1/4–15/5/2024: 10 micro-batch, 1.407 bản ghi, **179 cảnh báo — khớp 179/179
với kết quả batch, z giống hệt** (batch và stream dùng chung logic). Cảnh báo cực đoan nhất: 30/4/2024
trạm Thái Lan 38,6 °C (nền 30,2 °C, z = +3,53). Có test tích hợp với Kafka thật.

## 9. Hạn chế và việc tiếp theo

- **Nền ngắn** cho ISD/ERA5/Open-Meteo/NASA POWER (5–10 năm, gồm cả năm đánh giá) — kết luận khí hậu
  chỉ dựa trên GHCN nền 1991–2020.
- Nhiệt độ GHCN là TAVG hoặc (TMAX+TMIN)/2 — schema `WeatherObs` hiện chưa tách TMAX, nên chưa tính
  được TX90p (ngày nóng theo nhiệt độ cao nhất) chuẩn ETCCDI.
- SPI chỉ có 12 trạm do GHCN thiếu số liệu mưa; có thể bổ sung bằng mưa ERA5 khi có nền dài hơn.
- Trạm lân cận thưa (18/61 trạm không có láng giềng trong 200 km) — 15.938 dị thường vẫn không có
  đối chứng.
- Luồng streaming hiện dùng bản ghi GHCN theo ngày; nguồn theo giờ (ISD, ERA5) cần thêm bước gom ngày
  theo event-time + watermark.
- Tiếp theo: panel hỗ trợ quyết định (UAV: gió/mưa; nông nghiệp: SPI; năng lượng: bức xạ).
