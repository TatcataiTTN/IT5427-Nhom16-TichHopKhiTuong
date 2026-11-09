# Đặc trưng dữ liệu thu thập và yêu cầu xử lý

Tài liệu này làm rõ dữ liệu của 5 nguồn có những vấn đề gì (thiếu, ngoài khoảng, không đồng nhất
về đơn vị / ngữ nghĩa / thời gian / không gian...), **đo trực tiếp trên dữ liệu thật** (ngày 10/11/2026,
bộ đầy đủ: GHCN 41 trạm toàn lịch sử, ISD 26 trạm × 10 năm, ERA5 9 biến × 5 năm, Open-Meteo / NASA
POWER 6 điểm × 5 năm), và đối chiếu với những gì pipeline **đã** xử lý.

Ký hiệu trạng thái: ✅ đã xử lý · ⚠️ xử lý một phần / chỉ phát hiện, chưa sửa · ❌ chưa xử lý.

---

## 0. Tổng quan

| # | Nhóm vấn đề | Nguồn bị ảnh hưởng | Mức độ đo được | Trạng thái |
|---|---|---|---|---|
| 1 | Định dạng / cú pháp khác nhau | cả 5 | 5 định dạng, 4 kiểu mã thiếu | ✅ |
| 2 | Thiếu do **cấu trúc nguồn** (nguồn không đo biến đó) | GHCN, ISD, ERA5, NASA | GHCN 100% thiếu RH/gió/áp suất; ISD 100% thiếu mưa | ✅ (ghi NULL, không bịa) |
| 3 | Thiếu theo **thời gian** | GHCN, ISD | độ đầy đủ trung vị GHCN 91,3%, ISD 98,5%; thấp nhất 46,5% / 32,0% | ⚠️ |
| 4 | **Thiếu ≠ 0** (mưa) | GHCN | 41,3% số ngày không báo cáo mưa | ⚠️ |
| 5 | Giá trị **bị nguồn gắn cờ lỗi QC** nhưng vẫn được dùng | GHCN, ISD | GHCN 406 giá trị; ISD 2.932 giá trị (mã 2/6) | ❌ |
| 6 | **Ngoài khoảng vật lý** | ISD | gió 83 m/s (2 bản tin) | ❌ |
| 7 | **Nhảy giá trị phi vật lý** | ISD | 38 lần nhiệt độ đổi > 10°C trong ≤ 1 giờ | ❌ |
| 8 | Outlier thống kê | cả 5 | IQR: 0,7–16% tuỳ biến (`docs/13`) | ✅ gắn cờ |
| 9 | Dị thường thật vs lỗi dữ liệu | GHCN, ISD | 335 ca nghi lỗi sau đối chứng ERA5 + trạm lân cận | ✅ |
| 10 | Trôi / nhảy bậc cảm biến | GHCN, ISD | 4/80 chuỗi (vd áp suất Phnom Penh −2,6 hPa) | ⚠️ phát hiện, chưa hiệu chỉnh |
| 11 | **Đơn vị** khác nhau | cả 5 | 12 cặp biến–nguồn cần đổi đơn vị | ✅ |
| 12 | **Độ cao đo gió** khác nhau (2 m vs 10 m) | NASA POWER | gió 2 m chỉ bằng 0,71 lần gió 10 m | ❌ |
| 13 | **Định nghĩa** nhiệt độ ngày khác nhau | GHCN (+ so với nguồn giờ) | TAVG thấp hơn (TMAX+TMIN)/2 trung bình 0,25°C; 29.380 ngày dùng (TMAX+TMIN)/2 | ⚠️ |
| 14 | Áp suất bề mặt vs mực nước biển | NASA, ISD, ERA5, Open-Meteo | 2 đại lượng vật lý khác nhau | ✅ (2 cột riêng) |
| 15 | Bức xạ đỉnh khí quyển vs bề mặt | ERA5 | — | ✅ (đã sửa) |
| 16 | ISD có biến chưa được khai thác | ISD | áp suất trạm MA1 có ở 97,9% bản tin nhưng chưa parse (SLP chỉ 16,7%) | ❌ |
| 17 | **Bản tin trùng** | ISD | 22,7% số dòng trùng (trạm, thời điểm) | ❌ |
| 18 | Độ phân giải thời gian khác nhau | cả 5 | ngày / giờ / ~30 phút không đều | ✅ (gom theo ngày khi so sánh) |
| 19 | **Ranh giới ngày** khác nhau (giờ địa phương vs UTC) | GHCN | ngày GHCN là ngày địa phương (UTC+7…+8) | ❌ |
| 20 | Lưới vs điểm | ERA5 | 113 trạm nội suy Bilinear | ✅ |
| 21 | Chênh lệch độ cao lưới–trạm | ERA5 | RMSE nhiệt độ nhóm trạm cao 1,42°C vs 0,94–0,99°C | ⚠️ |
| 22 | Mã trạm khác nhau cho cùng trạm | GHCN, ISD | 22 cặp cùng trạm vật lý | ✅ (Entity Resolution) |

---

## 1. Dị biệt cú pháp / định dạng

| Nguồn | Định dạng | Cấu trúc | Mã giá trị thiếu | Xử lý |
|---|---|---|---|---|
| GHCN-Daily | CSV dạng **long** (1 dòng / biến / ngày) | `ID, DATE, ELEMENT, DATA_VALUE, M/Q/S_FLAG, OBS_TIME` | dòng không tồn tại | ✅ PIVOT long → wide |
| NOAA ISD | CSV có **trường nén** nhiều thành phần | vd `TMP = "+0250,1"` (giá trị, mã QC); `WND = "090,1,N,0031,1"` | `+9999`, `99999`, `999` | ✅ PARSE tách thành phần, mã thiếu → NULL |
| NASA POWER | JSON wide theo ngày | `properties.parameter.<BIẾN>.<YYYYMMDD>` | `-999` (`fill_value` trong header) | ✅ |
| Open-Meteo | JSON mảng song song theo giờ | `hourly.<biến>[i]`, đơn vị ở `hourly_units` | `null` | ✅ |
| ERA5 (ARCO) | NetCDF/Zarr lưới 0,25° | `(time, latitude, longitude)` | — (0% NaN đã kiểm) | ✅ nội suy vào trạm |

## 2. Dữ liệu thiếu (missing)

### 2.1. Thiếu do cấu trúc nguồn — không phải lỗi, không được "lấp" bằng số bịa

| Biến | GHCN | ISD | ERA5 | Open-Meteo | NASA POWER |
|---|---|---|---|---|---|
| Nhiệt độ | 4,1% | 0,1% | 0% | 0% | 0% |
| Độ ẩm tương đối | **100%** (không đo) | 0,3% (suy từ điểm sương) | **100%** (chưa tải điểm sương) | 0% | 0% |
| Mưa | 41,3% | **100%** (chưa parse AA1) | 0% | 0% | 0% |
| Gió | **100%** (không đo) | 0,8% | 0% | 0% | 0% |
| Áp suất mực nước biển | **100%** | 83,3% | 0% | 0% | **100%** (chỉ có áp suất bề mặt) |

**Yêu cầu:** giữ NULL, chọn nguồn thay thế bằng quy tắc Survivorship (`warehouse/survivorship.py`), **không** điền 0
hay trung bình. ✅ Đã làm. *Lỗi đã từng gặp vì vi phạm yêu cầu này:* tính tương quan sau khi thay NULL bằng 0 tạo
ra tương quan giả (đã sửa, xem `docs/10`).

### 2.2. Thiếu theo thời gian

| Nguồn | Bước thời gian | Độ đầy đủ trung vị | Thấp nhất |
|---|---|---|---|
| ERA5, Open-Meteo, NASA POWER | giờ / giờ / ngày | 100% | 100% |
| ISD | giờ | 98,5% | 32,0% (trạm 48866099999) |
| GHCN | ngày | 91,3% | 46,5% (trạm BMM00048042) |
| ISD — năm thiếu hẳn | — | trạm Cát Bi không có 2015–2016 trên NOAA | |

**Yêu cầu** (theo loại biến — `docs/ingestion.md` mục 4):
- Biến liên tục, trơn (nhiệt độ, áp suất): khoảng trống ngắn có thể nội suy tuyến tính khi *cần chuỗi liên tục*
  (vd vẽ biểu đồ); **không** nội suy khi tính thống kê khí hậu.
- Biến gián đoạn (mưa): **không** nội suy, không điền 0.
- Tổng hợp theo ngày / tháng / năm phải có **ngưỡng đầy đủ**, nếu không kết quả bị lệch. ✅ Đã áp dụng: ngày theo
  giờ cần đủ 4 khối 6 giờ; tháng mưa cần ≥ 90% ngày; năm nhiệt độ ≥ 80% ngày; tháng bias ≥ 15 ngày.
- Khoảng trống giữa một đợt (vd đợt nóng) không được coi là "kết thúc đợt". ✅ Đã áp dụng (nối qua ≤ 1 ngày thiếu).

### 2.3. Thiếu ≠ 0 với lượng mưa — ⚠️
GHCN chỉ có số liệu mưa ở 58,7% số ngày; trong các ngày có số liệu, 57,1% là 0 mm. Ngày **không báo cáo** khác hẳn
ngày **không mưa**. Pipeline hiện giữ đúng NULL, nhưng **yêu cầu còn thiếu**: các chỉ số tích luỹ (tổng mưa tháng,
SPI) phải loại tháng có quá nhiều ngày thiếu — ✅ đã có ngưỡng 90%; phân biệt "khô thật" và "thiếu" trong
dashboard — ❌ chưa có.

## 3. Giá trị ngoài khoảng / sai — kiểm soát chất lượng (QC)

Nên kiểm tra theo **nhiều tầng**, từ rẻ đến đắt:

| Tầng | Kiểm tra | Kết quả đo | Trạng thái |
|---|---|---|---|
| 1. Cờ QC của chính nguồn | GHCN `Q_FLAG` khác rỗng = **không qua QC của NOAA** | 406 giá trị: O (outlier) 306, I (không nhất quán nội bộ) 70, G (khoảng trống) 19, D (trùng) 6, K (lặp giá trị) 5 — chủ yếu TMIN/TMAX | ❌ đang dùng như dữ liệu tốt |
| | ISD mã QC thành phần (`1`, `5` = qua QC; `2`, `6` = nghi ngờ; `3`, `7` = sai) | TMP 1.551, DEW 897, SLP 312, gió 172 giá trị mã 2/6 | ❌ đang dùng như dữ liệu tốt |
| 2. Giới hạn vật lý | nhiệt độ −10…50°C, áp suất MSL 870…1085 hPa, gió 0…75 m/s, RH 0…100%, mưa 0…600 mm/ngày, bức xạ 0…1400 W/m² | ISD gió 83 m/s (2 bản tin); các biến khác không vi phạm | ❌ chưa có bước kiểm tra |
| 3. Nhất quán nội bộ | điểm sương ≤ nhiệt độ | 0 vi phạm | — (nên giữ làm kiểm tra) |
| 4. Nhảy theo thời gian | nhiệt độ đổi > 10°C trong ≤ 1 giờ ở cùng trạm | 38 lần (ISD) | ❌ |
| 5. Outlier thống kê | IQR (`ingestion/veracity.py`), bền hơn Z-score | `docs/13` | ✅ gắn cờ |
| 6. So với khí hậu nền của trạm | z-score theo ngày-trong-năm | 6.319 giá trị cực đoan | ✅ |
| 7. Đối chứng không gian | ERA5 cùng vị trí + trạm lân cận ≤ 200 km | 335 ca nghi lỗi dữ liệu | ✅ |
| 8. Ổn định theo thời gian | chuỗi bias trạm − ERA5: Mann-Kendall/Sen + Pettitt | 4/80 chuỗi gắn cờ | ⚠️ phát hiện, chưa hiệu chỉnh |

**Yêu cầu:** tầng 1–4 phải chạy ở **Ingestion**, gắn cờ (cột `qc_flag`) chứ không xoá dòng, để tầng sau và người
dùng tự quyết. Tầng 5–8 là phân tích đã có.

## 4. Không đồng nhất về đơn vị đo

| Biến | GHCN | ISD | ERA5 | Open-Meteo | NASA POWER | Chuẩn trong `WeatherObs` | Trạng thái |
|---|---|---|---|---|---|---|---|
| Nhiệt độ | 1/10 °C | 1/10 °C | K | °C | °C | °C | ✅ |
| Mưa | 1/10 mm (24 giờ) | — | m (tích luỹ 1 giờ) | mm/giờ | mm/ngày | mm | ✅ |
| Gió | — | 1/10 m/s | m/s, dạng vectơ (u, v) | **km/h**, dạng cực | m/s | m/s, (tốc độ, hướng) | ✅ (km/h từng bị bỏ sót — gió Open-Meteo phóng đại 3,6 lần, đã sửa) |
| Áp suất | — | 1/10 hPa | Pa | hPa | **kPa** | hPa | ✅ |
| Bức xạ | — | — | **J/m² tích luỹ 1 giờ** | W/m² | **MJ/m²/ngày** | W/m² | ✅ |
| Mây | — | — | tỷ lệ 0–1 | — | — | % | ✅ |
| Độ ẩm | — | điểm sương (1/10 °C) | — | % | % | % (ISD suy bằng Clausius-Clapeyron) | ✅ |

**Yêu cầu:** đọc đơn vị từ **metadata của nguồn** (`hourly_units`, `fill_value`, thuộc tính NetCDF) thay vì giả
định, và có test cho từng phép đổi. ✅ Có test cho Open-Meteo, NASA POWER, ISD.

## 5. Không đồng nhất về ngữ nghĩa (cùng tên, khác đại lượng)

| Vấn đề | Bằng chứng | Yêu cầu | Trạng thái |
|---|---|---|---|
| **Gió đo ở độ cao khác nhau** | NASA POWER `WS2M` là gió ở **2 m**; ISD, ERA5, Open-Meteo ở **10 m**. Tỷ số đo được 2 m / 10 m = **0,71** (lý thuyết hồ sơ gió logarit với độ nhám 0,1 m: 0,65) | Quy về 10 m bằng hồ sơ gió logarit, hoặc tải `WS10M` của NASA POWER thay cho `WS2M` | ❌ |
| **Nhiệt độ ngày** có 3 định nghĩa | GHCN TAVG (trung bình giờ, cờ `M_FLAG = H`) thấp hơn (TMAX+TMIN)/2 trung bình **0,25°C**; 29.380 ngày chỉ có TMAX/TMIN nên dùng (TMAX+TMIN)/2; nguồn giờ dùng trung bình 24 giờ | Ghi rõ định nghĩa trong cột riêng (`temp_def`); không trộn trong cùng một chuỗi xu hướng, hoặc hiệu chỉnh độ lệch 0,25°C | ⚠️ đang trộn — có thể tạo xu hướng giả khi trạm đổi cách tính |
| Áp suất bề mặt vs mực nước biển | lệch nhau theo độ cao trạm (~12 hPa / 100 m) | Hai cột riêng, không bao giờ thay thế cho nhau | ✅ |
| Bức xạ đỉnh khí quyển vs bề mặt | ERA5 `toa_incident_solar_radiation` khác `ALLSKY_SFC_SW_DWN` | Dùng `surface_solar_radiation_downwards` | ✅ |
| Mưa: khoảng tích luỹ khác nhau | GHCN: 24 giờ kết thúc lúc quan trắc buổi sáng giờ địa phương; ERA5 / Open-Meteo: tổng các giờ UTC | Khi so sánh theo ngày phải căn cùng cửa sổ 24 giờ | ❌ (đang so ngày UTC với ngày GHCN) |
| ISD có biến chưa khai thác | áp suất trạm `MA1` có ở **97,9%** bản tin (SLP chỉ 16,7%); mưa `AA1` ở 4,4% | Parse `MA1` vào `pressure_surface_hpa`, `AA1` vào `precip_mm` | ❌ |
| Open-Meteo không độc lập | Open-Meteo Historical là sản phẩm phái sinh từ ERA5 | Không dùng Open-Meteo làm bằng chứng "độc lập" khi xác nhận ERA5 | ✅ (chỉ dùng ERA5 + trạm) |

## 6. Không đồng nhất về thời gian

| Vấn đề | Bằng chứng | Yêu cầu | Trạng thái |
|---|---|---|---|
| Độ phân giải khác nhau | GHCN, NASA: ngày; ERA5, Open-Meteo: giờ; ISD: không đều (FM-15 METAR ~30 phút, FM-12 SYNOP 3 giờ) | Gom về ngày khi so sánh đa nguồn | ✅ |
| **Bản tin trùng** | **22,7%** số dòng ISD trùng (trạm, thời điểm) — cùng một quan trắc được gửi ở cả METAR (FM-15) và SYNOP (FM-12); 76,6% số giờ có ≥ 2 bản tin | Khử trùng theo (trạm, thời điểm), ưu tiên bản tin có mã QC tốt hơn | ❌ — số bản ghi ISD (3,46 triệu) đang bị đếm trùng; trung bình ngày ít bị ảnh hưởng |
| Múi giờ | Mọi nguồn chuẩn hoá về `timestamp_utc` | | ✅ |
| **Ranh giới ngày GHCN** | Ngày GHCN là ngày **địa phương** (UTC+7…+8 ở ĐNA), nhưng đang gán 00:00 UTC | Ghi rõ ngày GHCN là ngày địa phương; khi ghép với ERA5 theo ngày, dịch cửa sổ 24 giờ theo múi giờ trạm | ❌ (lệch 7–8 giờ khi so sánh theo ngày) |

## 7. Không đồng nhất về không gian

| Vấn đề | Bằng chứng | Yêu cầu | Trạng thái |
|---|---|---|---|
| Lưới (ERA5 0,25° ≈ 28 km) vs điểm (trạm) | | Nội suy Bilinear vào toạ độ trạm | ✅ |
| Chênh lệch độ cao lưới – trạm | RMSE nhiệt độ ERA5 – trạm: 0,99 / 0,94 / **1,42°C** theo nhóm độ cao thấp → cao | Hiệu chỉnh theo gradient nhiệt độ thẳng đứng (~6,5°C/km) dùng độ cao địa hình ERA5 | ⚠️ |
| Mã trạm khác nhau | GHCN `VMM00048820` và ISD `48820099999` là cùng trạm Nội Bài | Entity Resolution theo khoảng cách (≤ 5 km) | ✅ 22/26 cặp |
| Mạng trạm thưa | 18/61 trạm không có láng giềng trong 200 km | Ghi nhận giới hạn khi xác nhận chéo | ✅ ghi nhận |

## 8. Ưu tiên xử lý tiếp theo (phần Ingestion — TV1)

| Ưu tiên | Việc | Lý do | Công sức |
|---|---|---|---|
| 1 | Đọc cờ QC của nguồn (GHCN `Q_FLAG`, ISD mã 2/3/6/7) và thêm kiểm tra giới hạn vật lý, nhảy giá trị → cột `qc_flag` | Đang dùng ~3.300 giá trị mà chính NOAA đã đánh dấu nghi ngờ / sai | Nhỏ |
| 2 | Khử trùng bản tin ISD | 22,7% dòng trùng làm sai mọi số đếm | Nhỏ |
| 3 | Quy gió NASA POWER về 10 m (hoặc tải `WS10M`) | Gió NASA thấp hơn hệ thống ~30% — sai so sánh đa nguồn | Nhỏ |
| 4 | Parse áp suất trạm `MA1` và mưa `AA1` của ISD | Tăng độ phủ áp suất ISD từ 16,7% lên ~98% | Nhỏ |
| 5 | Lưu định nghĩa nhiệt độ ngày (`temp_def`) cho GHCN | Tránh xu hướng giả do trộn định nghĩa | Nhỏ |
| 6 | Căn ranh giới ngày GHCN theo giờ địa phương khi so với ERA5 | Lệch 7–8 giờ làm tăng sai số so sánh ngày, nhất là với mưa | Trung bình |
| 7 | Hiệu chỉnh độ cao khi so ERA5 với trạm | Giảm sai số ở trạm vùng cao | Trung bình |
| 8 | Hiệu chỉnh (không chỉ phát hiện) chuỗi trôi cảm biến | Phục vụ phân tích xu hướng dài hạn | Lớn |

*Cách tái lập số liệu trong tài liệu này: các phép đo được chạy trực tiếp trên `data_samples/` (dữ liệu thô) và
`warehouse/output/weatherobs.parquet`; xem `docs/13-data-quality-report.md` cho tỷ lệ thiếu và outlier theo nguồn.*
