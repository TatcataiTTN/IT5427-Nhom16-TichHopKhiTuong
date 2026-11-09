# Phát hiện dị thường khí hậu — phương pháp và kết quả kiểm chứng

Mục tiêu chính trong tên đề tài ("phát hiện dị thường khí hậu", `docs/01` mục 2). Code:
`warehouse/anomaly_detection.py` (Spark + pandas), unit test `tests/test_anomaly.py` (9 test),
hiển thị ở dashboard mục 4. Số liệu dưới đây lấy từ lần chạy thật ngày 13/10/2026 trên warehouse
đầy đủ (9.348.470 bản ghi) — chạy hết ~52 giây.

```bash
python3 warehouse/anomaly_detection.py   # cần warehouse/output/weatherobs.parquet (build_warehouse.py)
```

---

## 1. Phương pháp

Nguyên tắc: một giá trị chỉ "dị thường" khi so với **khí hậu bình thường của chính nơi đó, vào đúng
thời điểm đó trong năm** — 35°C ở Hà Nội tháng 6 là bình thường, tháng 1 thì không. Mọi ngưỡng đều
lấy từ chuẩn khí tượng quốc tế, không tự đặt.

| Bước | Cách làm | Ghi chú |
|---|---|---|
| 1. Tổng hợp theo ngày (Spark) | 9,3 triệu bản ghi → 977.239 ngày × vị trí × nguồn: nhiệt độ TB ngày, tổng mưa, gió max, áp suất MSL thấp nhất | Ngày của nguồn đo theo giờ (ISD, ERA5, Open-Meteo) chỉ hợp lệ khi có quan trắc ở **đủ 4 khối 6 giờ** — tránh trung bình bị lệch nóng khi thiếu số liệu ban đêm |
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
| Bất thường | Cùng chiều, \|z\| ≥ 1 | `xac_nhan_khi_hau` — tín hiệu khí hậu thật trên diện rộng | **5.375** |
| Cực đoan (\|z\| ≥ 3) | Gần bình thường (\|z\| < 0,5) hoặc ngược chiều | `nghi_loi_du_lieu` — nghi lỗi cảm biến/ghi chép | **25** |
| Bất thường | Lệch nhẹ | `chua_xac_dinh` — dị thường cục bộ, ERA5 (~28 km) có thể không bắt được | 514 |
| Bất thường | Không có (trước 2020) | `khong_co_era5` | 33.052 |

**Ví dụ lỗi dữ liệu thật phát hiện được:** trạm ISD Phnom Penh (48991099999) ghi áp suất MSL
**981,6 hPa ngày 3/7/2023 (z = −9,1)** trong khi ERA5 cùng vị trí *bình thường* (z = +1,6) — không có
bão nào qua Phnom Penh hôm đó. Cùng trạm còn liên tục ghi áp suất thấp bất thường (z ≈ −4,4 đến −4,9)
suốt 7–9/2023 khi ERA5 vẫn bình thường → dấu hiệu **cảm biến áp suất hỏng/trôi**. Đây là đầu vào trực
tiếp cho việc phát hiện outlier và sensor drift ở Tuần 3 (TV1 #2, #3).

Ý nghĩa với học phần: một nguồn đơn lẻ không thể tự phân biệt "khí hậu cực đoan thật" với "cảm biến
hỏng". Khi **tích hợp** trạm điểm với lưới tái phân tích qua Record Linkage không-thời gian
(nội suy ERA5 vào đúng `location_id` của trạm), hai trường hợp này tách được ra.

## 4. Hạn chế và việc tiếp theo

- **Nền ngắn** cho ISD/ERA5/Open-Meteo/NASA POWER (5–10 năm, gồm cả năm đánh giá) — kết luận khí hậu
  chỉ dựa trên GHCN nền 1991–2020.
- Nhiệt độ GHCN là TAVG hoặc (TMAX+TMIN)/2 — schema `WeatherObs` hiện chưa tách TMAX, nên chưa tính
  được TX90p (ngày nóng theo nhiệt độ cao nhất) chuẩn ETCCDI.
- SPI chỉ có 12 trạm do GHCN thiếu số liệu mưa; có thể bổ sung bằng mưa ERA5 khi có nền dài hơn.
- Chưa xác nhận chéo theo **trạm lân cận** (mới đối chiếu với ERA5) — làm ở Tuần 3 cùng Entity
  Resolution GHCN↔ISD theo khoảng cách toạ độ.
- Tiếp theo: xu hướng dài hạn (Mann-Kendall + độ dốc Sen trên chuỗi GHCN 80 năm), panel hỗ trợ quyết
  định (UAV: gió/mưa; nông nghiệp: SPI; năng lượng: bức xạ).
