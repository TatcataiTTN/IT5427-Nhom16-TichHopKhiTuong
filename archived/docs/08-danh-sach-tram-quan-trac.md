# Danh sách trạm quan trắc — đã lọc thật từ GHCN & ISD (Đông Nam Á)

Không suy đoán — toàn bộ danh sách dưới đây lấy trực tiếp từ 2 file metadata gốc:
- `ghcnd-stations.txt` (11.4MB, danh mục chính thức toàn bộ trạm GHCN toàn cầu)
- `isd-history.csv` (2.9MB, danh mục chính thức toàn bộ trạm ISD toàn cầu, tải từ `ncei.noaa.gov`)

4 file CSV kết quả đã lưu sẵn ở `reference/` — dùng thẳng trong code, không cần tự lọc lại.

---

## 1. Phát hiện quan trọng khi lọc dữ liệu (cần biết trước khi code)

- **Mã quốc gia Việt Nam trong ISD không nhất quán**: vừa xuất hiện `VM` vừa xuất hiện `VN` cho cùng khu vực (VD trạm Tân Sơn Nhất `489000` mang mã `VN`, còn phần lớn trạm khác mang mã `VM`). **Khi lọc ISD theo quốc gia Việt Nam phải kiểm tra cả 2 mã**, nếu không sẽ bị sót trạm quan trọng.
- **Mã quốc gia Brunei trong ISD là `BX`, không phải `BS`** (`BS` là mã của Bahamas — nếu gõ nhầm sẽ lấy nhầm trạm Nassau/Bahamas). GHCN dùng đúng `BX` ngay từ đầu, chỉ ISD có rủi ro nhầm.
- **GHCN-Daily không có trạm tên "Hà Nội"/"Ho Chi Minh"** — GHCN đặt tên theo sân bay/địa danh: Hà Nội = **NOIBAI INTL** (`VMM00048820`), TP.HCM = **TAN SON HOA** (`VM000048900`, mã cũ của Tân Sơn Nhất). Tra theo tên thành phố sẽ không ra kết quả — phải biết trước tên trạm tương ứng.
- **Lào không có trạm ISD tên "Vientiane"** — thủ đô Lào trong ISD mang tên sân bay **WATTAY INTL** (`489400`).

---

## 2. Trạm Việt Nam — GHCN-Daily (56 trạm, đầy đủ toàn quốc)

File đầy đủ: `reference/ghcn_stations_vietnam_full.csv`. 16 trạm có mã WMO chính thức (độ tin cậy cao nhất, nên ưu tiên):

| Mã trạm (ID) | Tên | Vĩ độ | Kinh độ | Cao độ (m) | Vùng |
|---|---|---|---|---|---|
| `VMM00048820` | NOIBAI INTL (Hà Nội) | 21.221 | 105.807 | 11.9 | Bắc Bộ |
| `VMM00048825` | HA DONG | 20.967 | 105.767 | 7.9 | Bắc Bộ |
| `VMM00048826` | PHU LIEN (Hải Phòng) | 20.800 | 106.633 | 116.0 | Bắc Bộ |
| `VMM00048806` | SON LA | 21.333 | 103.900 | 676.0 | Tây Bắc |
| `VMM00048808` | CAO BANG | 22.667 | 106.250 | 243.0 | Đông Bắc |
| `VMM00048830` | LANG SON | 21.833 | 106.767 | 263.0 | Đông Bắc |
| `VMM00048840` | THANH HOA | 19.750 | 105.783 | 5.0 | Bắc Trung Bộ |
| `VMM00048845` | VINH | 18.737 | 105.671 | 5.2 | Bắc Trung Bộ |
| `VMM00048848` | DONG HOI | 17.483 | 106.600 | 8.0 | Bắc Trung Bộ |
| `VMM00048855` | DANANG INTL | 16.044 | 108.199 | 10.1 | Nam Trung Bộ (có cờ **GSN** — mạng lưới toàn cầu) |
| `VMW00041010` | NHA TRANG | 12.233 | 109.200 | 9.1 | Nam Trung Bộ |
| `VMW00041011` | QUI NHON | 13.767 | 109.217 | 9.1 | Nam Trung Bộ |
| `VMM00048887` | PHAN THIET | 10.933 | 108.100 | 5.0 | Nam Trung Bộ |
| `VM000048900` | TAN SON HOA (TP.HCM) | 10.820 | 106.670 | 5.0 | Nam Bộ (cờ **GSN**) |
| `VMM00048914` | CA MAU | 9.183 | 105.150 | 2.0 | Nam Bộ |
| `VMM00048917` | PHU QUOC | 10.217 | 103.967 | 4.0 | Đảo |

*(40 trạm còn lại không có mã WMO nhưng vẫn dùng được — đủ trong `reference/ghcn_stations_vietnam_full.csv`, gồm cả Đà Lạt, Pleiku, Buôn Ma Thuột, Vũng Tàu, Tây Ninh, Cần Thơ khu vực (Bình Thuỷ/Phong Điền), Sóc Trăng, Vĩnh Long...)*

## 3. Trạm Việt Nam — NOAA ISD (10 trạm đang hoạt động, dữ liệu theo giờ, cập nhật đến 24/8/2025)

File: `reference/isd_stations_vietnam_active.csv`. Đây là tập trạm **ưu tiên cho phần dữ liệu theo giờ** (Batch vs. Streaming replay) — phủ đều 3 miền:

| USAF-WBAN | Tên | ICAO | Vĩ độ | Kinh độ | Cao độ (m) | Bắt đầu |
|---|---|---|---|---|---|---|
| 488200-99999 | NOIBAI INTL | VVNB | 21.221 | 105.807 | 11.9 | 1958 |
| 488251-99999 | CAT BI (Hải Phòng) | VVCI | 20.819 | 106.725 | 1.8 | 2017 |
| 488450-99999 | VINH | VVVH | 18.737 | 105.671 | 5.2 | 1974 |
| 488520-99999 | PHU BAI (Huế) | VVPB | 16.402 | 107.703 | 14.6 | 1957 |
| 488550-99999 | DANANG INTL | VVDN | 16.044 | 108.199 | 10.1 | 1956 |
| 488660-99999 | PLEIKU | VVPK | 14.005 | 108.017 | 741.9 | 1958 |
| 488700-99999 | QUY NHON | VVQN | 13.767 | 109.217 | 6.0 | 1957 |
| 488770-99999 | NHA TRANG | VVNT | 12.250 | 109.200 | 10.0 | 1956 |
| **489000-99999** | **TAN SON NHAT INTL (TP.HCM)** | VVTS | 10.819 | 106.652 | 10.1 | 1949 |
| 489125-99999 | CAN THO | VVCT | 10.083 | 105.717 | 3.1 | 1965 |

> Trạm `489000-99999` là trạm nhóm đã dùng làm mẫu test trong `scripts/check_data_sources.py` (44.560 bản ghi GHCN, 16.741 bản ghi ISD/giờ — đều đã xác nhận tải được thật).

## 4. Trạm ưu tiên — các nước Đông Nam Á khác

File: `reference/ghcn_stations_sea_priority.csv` (daily) và `reference/isd_stations_sea_priority.csv` (hourly). Mỗi nước lấy sân bay/trạm thủ đô hoặc thành phố lớn nhất có chuỗi dữ liệu dài nhất:

| Nước | Trạm ưu tiên | ICAO (ISD) | Vĩ độ | Kinh độ | Nguồn có |
|---|---|---|---|---|---|
| Thái Lan | Don Mueang Intl (Bangkok) | VTBD | 13.913 | 100.607 | GHCN + ISD |
| Thái Lan | Suvarnabhumi Intl (Bangkok) | VTBS | 13.681 | 100.748 | ISD |
| Thái Lan | Chiang Mai Intl | VTCC | 18.767 | 98.963 | GHCN + ISD |
| Indonesia | Soekarno-Hatta Intl (Jakarta) | WIII | -6.126 | 106.656 | GHCN + ISD |
| Indonesia | Surabaya Juanda | WRSJ | -7.380 | 112.787 | GHCN + ISD |
| Indonesia | Denpasar Ngurah Rai (Bali) | WRRR | -8.749 | 115.167 | GHCN + ISD |
| Malaysia | Kuala Lumpur Intl | WMKK | 2.746 | 101.710 | GHCN + ISD |
| Malaysia | Penang Intl | WMKP | 5.297 | 100.277 | GHCN + ISD |
| Philippines | Ninoy Aquino Intl (Manila) | RPLL | 14.509 | 121.020 | GHCN + ISD |
| Philippines | Mactan Cebu Intl | RPVM | 10.308 | 123.979 | GHCN + ISD |
| Campuchia | Phnom Penh Intl | VDPP | 11.547 | 104.844 | GHCN + ISD |
| Lào | Wattay Intl (Vientiane) | VLVT | 17.988 | 102.563 | ISD |
| Lào | Luang Prabang Intl | VLLB | 19.897 | 102.161 | GHCN + ISD |
| Myanmar | Yangon Intl | VYYY | 16.907 | 96.133 | GHCN + ISD |
| Myanmar | Mandalay Intl | VYMD | 21.702 | 95.978 | ISD |
| Brunei | Brunei Intl | WBSB | 4.944 | 114.928 | GHCN + ISD |

**Ghi nhớ kèm bảng độ phủ đã có sẵn trong `05-bao-cao-kiem-tra-nguon-du-lieu.md` mục 4:** Campuchia và Brunei có tổng cộng chỉ 1 trạm GHCN/nước trên toàn quốc — bảng trên gần như là **toàn bộ** những gì có, không phải bản rút gọn từ danh sách dài hơn.

---

## 5. Cách dùng trong code (Python)

```python
import pandas as pd

vn_ghcn = pd.read_csv("reference/ghcn_stations_vietnam_full.csv")
vn_isd = pd.read_csv("reference/isd_stations_vietnam_active.csv")
sea_ghcn = pd.read_csv("reference/ghcn_stations_sea_priority.csv")
sea_isd = pd.read_csv("reference/isd_stations_sea_priority.csv")

# Vi du: tai GHCN cho toan bo 16 tram VN co WMO ID
priority_ids = vn_ghcn[vn_ghcn["has_wmo"]]["ID"].tolist()
for station_id in priority_ids:
    url = f"https://noaa-ghcn-pds.s3.amazonaws.com/csv/by_station/{station_id}.csv"
    # requests.get(url) ...
```

## 6. Khuyến nghị phạm vi cho đề tài (để không quá tải với nhóm 3 người)

- **Bounding box đề xuất**: Đông Nam Á lục địa + hải đảo chính, khoảng **lat -11 đến 23, lon 92 đến 141** (đã dùng để test FIRMS ở phiên trước) — đủ phủ cả 9 nước.
- **Giai đoạn dữ liệu đề xuất**: 5 năm gần nhất (2020–2024 hoặc 2020–2025) để cân bằng giữa Volume (đủ lớn cho tiêu chí 5V) và thời gian xử lý thực tế của nhóm 3 người.
- **Số trạm khởi điểm khuyến nghị cho Tuần 1–2** (đủ để build/test pipeline mà không quá tải): **10 trạm ISD Việt Nam** (mục 3, đã phủ đều 3 miền) + **8 trạm ưu tiên các nước còn lại** (mục 4) = **18 trạm** làm tập lõi. Mở rộng thêm sang toàn bộ 56 trạm GHCN Việt Nam + 246 trạm ISD toàn ĐNA (mục 1 script, đã có sẵn trong `data_samples`/`reference`) **chỉ khi Tuần 3 còn dư thời gian**.
