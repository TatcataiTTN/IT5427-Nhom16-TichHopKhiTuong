# Báo cáo kiểm tra thực tế các nguồn dữ liệu

**Ngày kiểm tra:** 30/9/2026 · **Người thực hiện:** kiểm tra tự động bằng `scripts/check_data_sources.py`
**Phương pháp:** gọi trực tiếp API/endpoint thật, tải mẫu dữ liệu thật (không mock), lưu vào `data_samples/`, validate nội dung. Không phải tra cứu tài liệu — đây là kết quả chạy thực tế.

> Chạy lại: `python3 scripts/check_data_sources.py` (chỉ dùng thư viện chuẩn Python, không cần cài gì thêm). Kết quả JSON đầy đủ nằm ở `data_samples/check_results.json`.

---

## 1. Tổng hợp kết quả

| # | Nguồn | Trạng thái | Cần đăng ký? | Phủ Đông Nam Á? |
|---|---|---|---|---|
| 1 | **NASA POWER** | ✅ Hoạt động tốt | Không | ✅ Toạ độ bất kỳ (đã test Hà Nội) |
| 2 | **Open-Meteo Historical** | ✅ Hoạt động tốt | Không | ✅ Toạ độ bất kỳ (đã test Jakarta) |
| 3 | **NOAA GHCN-Daily** (AWS S3) | ✅ Hoạt động tốt | Không | ✅ 286 trạm trên 9 nước ĐNA (chi tiết mục 3) |
| 4 | **NOAA ISD/Global Hourly** (AWS S3) | ✅ Hoạt động tốt | Không | ✅ (đã test trạm 48900099999 — khu vực Hà Nội) |
| 5 | **Copernicus CDS** (ERA5 gốc, chính thức) | ⚠️ Server sống, nhưng **cần đăng ký** | **Có** — tài khoản CDS + API key | ✅ (toàn cầu, cắt theo bounding box) |
| 6 | **ERA5 trên AWS** (`era5-pds`) | ⚠️ Bị từ chối khi không có tài khoản AWS | **Có** — tài khoản AWS thật (Requester Pays) | ✅ nhưng **không miễn phí hoàn toàn như tài liệu cũ ghi** |
| 6b | **ERA5 trên Google Cloud** (ARCO-ERA5, **mới phát hiện**) | ✅ Hoạt động tốt, đã tải mẫu thật | **Không** — hoàn toàn public, không tài khoản | ✅ toàn cầu, 1959–2022, 0.25°, hourly, 35 biến |
| 6c | **ERA5 trên Microsoft Planetary Computer** (**mới phát hiện**) | ✅ Cấp token tự động thành công | **Không** — token tự cấp, không cần đăng ký | ✅ (cần dùng đúng SDK `planetary-computer`) |
| 7 | **OpenStreetMap** (Nominatim + Tile) | ⚠️ Không kiểm tra được **từ môi trường sandbox này** (bị chặn DNS ra ngoài) | Không | Có (theo tài liệu chính thức OSM — xem mục 7) |
| 8 | **CHIRPS** (mưa vệ tinh, tuỳ chọn) | ✅ Hoạt động tốt | Không | ✅ (độ phân giải 5km, phủ toàn ĐNA) |
| 9 | **Himawari-8/9** (ảnh vệ tinh khí tượng, tuỳ chọn) | ✅ Đã tải mẫu thật, **vẫn đang hoạt động** (đính chính, xem mục 8) | Không | ✅ (vệ tinh địa tĩnh phủ trọn ĐNA) |

**Kết luận nhanh:** **4 nguồn lõi đã chốt trong đề xuất đề tài (NASA POWER, Open-Meteo, NOAA GHCN, NOAA ISD) đều chạy được ngay hôm nay, không cần đăng ký, có dữ liệu thật cho Đông Nam Á.** Với riêng ERA5, ngoài CDS chính thức (cần đăng ký) và AWS (cần tài khoản AWS trả phí), **kiểm tra lần này phát hiện thêm 2 đường lấy ERA5 hoàn toàn miễn phí và không cần đăng ký gì cả: Google Cloud ARCO-ERA5 và Microsoft Planetary Computer** — xem mục 6b/6c, đây là phát hiện quan trọng nhất của đợt kiểm tra này.

---

## 2. NASA POWER

- **Gọi thử:** `GET https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,PRECTOTCORR,ALLSKY_SFC_SW_DWN&community=AG&longitude=105.85&latitude=21.03&start=20240101&end=20240105&format=JSON`
- **Kết quả:** HTTP 200, trả về đúng 5 ngày dữ liệu trong 0.85 giây, không cần header xác thực.
- **Dữ liệu mẫu thật (nhiệt độ 2m tại Hà Nội, °C):** `20240101: 20.95, 20240102: 21.47, 20240103: 16.11, 20240104: 16.34, 20240105: 19.52` — số liệu hợp lý cho tháng 1 miền Bắc VN (đợt lạnh).
- **Cách hoạt động trong pipeline:** gọi REST API trực tiếp theo từng điểm toạ độ + khoảng ngày → JSON → parse thẳng vào Spark DataFrame. Không cần crawl/parse file nhị phân, phù hợp làm nguồn "dễ nhất" để build pipeline mẫu trước.
- **Giới hạn cần biết:** API tính theo **point query** (1 toạ độ/lần) — muốn phủ cả lưới vùng ĐNA phải lặp qua nhiều toạ độ (mỗi request ~1s), không tải "bulk theo vùng" như ERA5.

---

## 3. Open-Meteo Historical

- **Gọi thử:** `GET https://archive-api.open-meteo.com/v1/archive?latitude=-6.21&longitude=106.85&start_date=2024-01-01&end_date=2024-01-05&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=Asia/Jakarta`
- **Kết quả:** HTTP 200, 5 ngày dữ liệu tại Jakarta, không cần key.
- **Dữ liệu mẫu thật (nhiệt độ max, °C):** `31.7, 32.0, 28.2, 28.2, 31.9` — hợp lý cho khí hậu nhiệt đới Jakarta.
- **Cách hoạt động:** giống NASA POWER (REST theo điểm), nhưng Open-Meteo **nội suy sẵn từ ERA5** — nghĩa là dùng nguồn này gián tiếp lấy được dữ liệu tương đương ERA5 mà **không cần đăng ký CDS**. Đây là phương án dự phòng thực tế rất tốt nếu nhóm không kịp xử lý thủ tục CDS.

---

## 4. NOAA GHCN-Daily & ISD (AWS S3 — public bucket)

- **Cách truy cập:** đây là bucket S3 **public**, chỉ cần HTTPS GET thông thường (`https://noaa-ghcn-pds.s3.amazonaws.com/...`), **không cần AWS CLI, không cần credential, không cần `--no-sign-request`** — khác với ghi chú "AWS CLI" trong tài liệu gốc (CLI chỉ là 1 cách, curl/Python `requests` cũng dùng được thẳng).
- **GHCN-Daily:** tải thử trạm `VMM00048820` (khu vực Hà Nội) → **44.560 bản ghi**, trải dài từ **18/12/1958 đến 05/02/2025** — dữ liệu thật, liên tục, cập nhật gần đây.
- **Số trạm theo từng nước Đông Nam Á** (đếm trực tiếp từ `ghcnd-stations.txt`, danh sách trạm chính thức):

  | Mã | Quốc gia | Số trạm |
  |---|---|---|
  | ID | Indonesia | **104** |
  | VM | Việt Nam | **56** |
  | TH | Thái Lan | **54** |
  | RP | Philippines | **34** |
  | LA | Lào | 15 |
  | MY | Malaysia | 16 |
  | BM | Myanmar | 5 |
  | CB | Campuchia | 1 |
  | BX | Brunei | 1 |

  → **Nhận xét quan trọng:** độ phủ rất lệch giữa các nước — Indonesia/Việt Nam/Thái Lan/Philippines đủ dày để phân tích, nhưng **Campuchia và Brunei gần như không có trạm GHCN** (chỉ 1 trạm/nước). Nếu đề tài mở rộng phạm vi ra toàn ĐNA, cần nêu rõ giới hạn này trong phần Veracity/hạn chế, và có thể bổ sung Meteostat hoặc trạm ISD cho các nước thiếu.

- **NOAA ISD/Global Hourly:** tải thử trạm `48900099999` năm 2024 → **16.741 bản ghi theo giờ**, file ~6MB, tải trong 3.4 giây. Dữ liệu chi tiết hơn GHCN (theo giờ thay vì theo ngày), phù hợp cho phần Batch vs. Streaming replay.

---

## 5. Copernicus CDS (ERA5 gốc)

- **Server:** phản hồi HTTP 202 tại `https://cds.climate.copernicus.eu/api` — dịch vụ đang hoạt động bình thường.
- **Thư viện `cdsapi`:** **chưa cài** trên máy kiểm tra (`pip install cdsapi` — nhẹ, cài trong vài giây).
- **File cấu hình `~/.cdsapirc`:** **chưa có** — đây là file chứa API key cá nhân, chỉ tạo được **sau khi đăng ký tài khoản** tại CDS và đăng nhập lấy key.
- **Việc nhóm cần làm (TV1, ngay tuần 1):**
  1. Đăng ký tài khoản tại `cds.climate.copernicus.eu` (miễn phí, email + vài phút xác thực)
  2. Vào trang cá nhân lấy API key, tạo file `~/.cdsapirc` theo hướng dẫn chính thức (`https://cds.climate.copernicus.eu/how-to-api`)
  3. `pip install cdsapi` rồi chạy thử 1 request nhỏ (1 ngày, 1 biến, bounding box nhỏ) để xác nhận key hoạt động — đúng như task #2 trong `03-ke-hoach-160-tasks.md`
- **Không kiểm tra được việc tải dữ liệu thật** trong lần kiểm tra này vì chưa có tài khoản — đây là việc nhóm cần tự làm vì cần thông tin cá nhân để đăng ký.

---

## 6. ERA5 trên AWS Open Data (`era5-pds`) — phát hiện quan trọng, đã sửa tài liệu

- **Test:** `GET https://era5-pds.s3.amazonaws.com/2024/01/main.nc4` (không mang credential) → **HTTP 403 AccessDenied**.
- **Nguyên nhân:** đây là bucket **"Requester Pays"** — S3 yêu cầu request phải được **ký bằng AWS credential thật** (Access Key + Secret Key của một tài khoản AWS có gắn phương thức thanh toán), ngay cả khi chỉ đọc dữ liệu công khai.
- **Sai lệch so với tài liệu gốc:** file `02-nguon-du-lieu.md` bản cũ ghi *"Requester Pays = 0đ vì cùng region AWS us-east-1"* — **điều này không chính xác**. "Cùng region" chỉ có thể giúp giảm/miễn phí phần **data transfer** nếu compute cũng chạy trên AWS cùng region, nhưng **vẫn bắt buộc phải có tài khoản AWS đã đăng ký thẻ để ký request** — không phải "không cần key" như 3 nguồn AWS S3 khác (GHCN/ISD/Himawari đều là bucket public thật sự, không Requester Pays). **Đã sửa lại dòng này trong `02-nguon-du-lieu.md`.**
- **Khuyến nghị ban đầu (đã cập nhật ở mục 6b):** bỏ `era5-pds` (AWS) khỏi kế hoạch chính vì thủ tục AWS phức tạp không tương xứng lợi ích, ưu tiên CDS chính thức để trích dẫn học thuật + Open-Meteo làm dự phòng. Nay có thêm 2 lựa chọn miễn phí tốt hơn hẳn `era5-pds`, xem ngay dưới đây.

---

## 6b. ERA5 trên Google Cloud — ARCO-ERA5 (phát hiện mới, khuyến nghị dùng chính)

Google + ECMWF hợp tác public hoá **ARCO-ERA5** (Analysis-Ready, Cloud-Optimized ERA5) tại bucket GCS `gcp-public-data-arco-era5` — đây **không phải** bản GRIB2 thô dạng file-theo-ngày như `era5-pds`, mà là **kho Zarr đã re-chunk tối ưu cho truy vấn cục bộ (partial read)**.

- **Đã tải thật:** `.zmetadata` của kho `ar/1959-2022-full_37-1h-0p25deg-chunk-1.zarr-v2` — HTTP 200, 30.7KB, **không cần bất kỳ credential/API key/tài khoản nào**.
- **Xác nhận nội dung:** kho có **35 biến khí tượng** đầy đủ, gồm đúng các biến cần cho đề tài: `2m_temperature`, `10m_u_component_of_wind`, `10m_v_component_of_wind`, `geopotential`, `land_sea_mask`... — độ phân giải **0.25° (1440×721 điểm lưới)**, tần suất **hàng giờ**, giai đoạn **1959–2022**.
- **⚠️ Lưu ý quan trọng đã kiểm chứng bằng thực nghiệm:** kho `raw/ERA5GRIB/...` (GRIB2 thô, chưa re-chunk) có kích thước **~5.4 GB cho 1 ngày/1 biến** — thử tải trực tiếp 1 file bị treo hơn 2 phút và phải huỷ giữa chừng. **Tuyệt đối không dùng nhánh `raw/`** — phải dùng nhánh `ar/...zarr-v2` (đã re-chunk) và đọc bằng `xarray.open_zarr()`, lúc đó có thể lấy đúng lát cắt bounding box + khoảng thời gian cần mà không phải tải nguyên khối dữ liệu toàn cầu nhiều năm.
- **Cách dùng trong code (đã kiểm chứng metadata, chưa test full — cần `pip install zarr gcsfs`):**
  ```python
  import xarray as xr
  ds = xr.open_zarr(
      "gcs://gcp-public-data-arco-era5/ar/1959-2022-full_37-1h-0p25deg-chunk-1.zarr-v2",
      storage_options={"token": "anon"},
      chunks=None,
  )
  vn_slice = ds["2m_temperature"].sel(
      latitude=slice(23, 8), longitude=slice(102, 110),   # bounding box Việt Nam
      time=slice("2020-01-01", "2020-01-31"),
  )
  ```
- **Khuyến nghị:** đây là lựa chọn **tốt nhất cho việc build/test pipeline nhanh** — không mất thời gian chờ duyệt tài khoản CDS. Nhóm vẫn nên **song song đăng ký CDS** (mục 5) vì đây là nguồn gốc chính thức, cần trích dẫn đúng chuẩn học thuật trong báo cáo (`cds.climate.copernicus.eu` là nguồn ECMWF công bố chính thức) — nhưng có thể **bắt đầu code ngay bằng ARCO-ERA5 trong lúc chờ duyệt CDS**, không cần block tiến độ tuần 1.

## 6c. ERA5 trên Microsoft Planetary Computer (phát hiện mới, phương án dự phòng thứ 2)

- **Đã test thật:** STAC catalog trả về item mẫu `era5-pds-2020-12-fc` với 4 asset (nhiệt độ, mưa, bức xạ...); gọi endpoint `/api/sas/v1/token/era5-pds` **nhận được SAS token thật ngay lập tức, không cần đăng ký tài khoản Microsoft**.
- **Hạn chế phát hiện được:** dữ liệu lưu dưới dạng Azure Blob (`abfs://era5/...`), việc tự ghép URL + token thủ công bị lỗi `AuthenticationFailed` (đã thử) vì cần đúng tên storage account nội bộ — **bắt buộc dùng SDK chính thức `pip install planetary-computer pystac-client`**, dùng hàm `planetary_computer.sign()` để tự động ký URL đúng cách, không tự chế URL.
- **Vai trò:** phương án dự phòng thứ 2 nếu ARCO-ERA5 (6b) gặp vấn đề, không cần ưu tiên số 1 vì thêm 1 lớp SDK phụ thuộc.

---

## 7. OpenStreetMap — Nominatim (geocoding) & Tile server (bản đồ nền)

**Không kiểm tra trực tiếp được từ môi trường chạy script này** — cả `nominatim.openstreetmap.org` và `tile.openstreetmap.org` bị **chặn ở tầng DNS** trong sandbox hiện tại (domain bị resolve về `127.0.0.1`, tức bị chặn chủ động bởi chính sách mạng của môi trường này, **không phải OSM bị sập**). Đây là hạn chế của môi trường chạy Claude Code, không phải của dịch vụ. Script `check_data_sources.py` đã tự ghi nhận rõ điều này thay vì báo sai là "dịch vụ lỗi".

**Cách 2 dịch vụ này hoạt động trong thực tế** (theo tài liệu chính thức OSM, để nhóm tự chạy lại và xác nhận trên máy/server thật):

- **Nominatim (geocoding)** — `https://nominatim.openstreetmap.org/search?q=...&format=json`
  - Dùng để chuyển địa chỉ text (VD "Hồ Hoàn Kiếm, Hà Nội") → toạ độ (lat/lon), hoặc ngược lại (reverse geocoding).
  - **Miễn phí, không cần key**, nhưng có **Usage Policy bắt buộc tuân thủ**: tối đa **1 request/giây**, bắt buộc gửi header `User-Agent` định danh ứng dụng (script trong repo đã làm đúng việc này), **không được dùng cho auto-complete tần suất cao**, và nên **tự cache kết quả** (không gọi lại cho cùng 1 địa chỉ đã geocode).
  - Với quy mô project học phần (vài trăm–vài nghìn điểm geocode 1 lần), hoàn toàn dùng được server công cộng — không cần tự host.

- **Tile server (bản đồ nền)** — `https://tile.openstreetmap.org/{z}/{x}/{y}.png`
  - Dùng để vẽ bản đồ nền cho bản đồ nhiệt/heatmap trên Dashboard (Streamlit/Superset dùng qua thư viện `folium`, `leaflet.js`, hoặc `st.map`/`pydeck`).
  - **Miễn phí, không cần key**, nhưng **Tile Usage Policy của OSM Foundation giới hạn nghiêm ngặt** cho việc dùng trực tiếp tile chính thức trong sản phẩm có nhiều người dùng — với 1 dashboard demo nội bộ (giảng viên + nhóm xem) thì **dùng thẳng được**, không vi phạm.
  - **Khuyến nghị thực tế cho project:** hầu hết thư viện Python vẽ bản đồ (`folium`, `plotly.express` với `mapbox_style="open-street-map"`, `streamlit-folium`) đã **tự động trỏ tới tile OSM mặc định miễn phí**, nhóm **không cần tự cấu hình URL tile hay tự host tile server** — chỉ cần gọi đúng API của thư viện, ví dụ `folium.Map(tiles="OpenStreetMap")`.

**Việc cần làm:** chạy lại đúng script `check_data_sources.py` trên máy cá nhân/laptop của nhóm (mạng bình thường, không qua sandbox) để lấy bằng chứng test thật — dự kiến sẽ **pass** vì đây là 2 dịch vụ rất ổn định, được hàng triệu ứng dụng dùng hằng ngày.

---

## 8. Nguồn mở rộng tuỳ chọn (CHIRPS, Himawari) — đã đính chính Himawari

- **CHIRPS:** tải thử header của 1 file `.tif.gz` ngày 1/1/2024 → HTTP 200, file ~3.2MB, không cần đăng ký. Sẵn sàng dùng nếu nhóm mở rộng sang phân tích mưa cực đoan.

- **Himawari-8 — ĐÍNH CHÍNH:** lần kiểm tra trước (chỉ liệt kê thư mục) kết luận sai rằng *"Himawari-8 đã ngừng vận hành cuối 2022"*. Lần này **tải thật 1MB đầu của 1 file sản phẩm mây** (`AHI-CHGT`, ngày **12/10/2025**, dung lượng gốc 793MB) từ bucket `s3://noaa-himawari8/` → **file HDF5/NetCDF hợp lệ, có header đúng chuẩn (magic number `\x89HDF`)**, `LastModified` xác nhận tháng 10/2025.
  → **Kết luận đúng: Himawari-8 vẫn đang hoạt động và cập nhật dữ liệu đều đặn**, bucket `noaa-himawari8` là nguồn thật, đang được nhiều nhóm nghiên cứu khí tượng dùng (đúng như bạn nhận định). Vệ tinh Himawari-9 (phóng 2016) hiện đóng vai trò vệ tinh vận hành chính (primary) từ cuối 2022, còn Himawari-8 chuyển sang vai trò dự phòng (backup) — **nhưng "backup" không có nghĩa là ngừng phát dữ liệu**, bucket vẫn được NOAA duy trì cập nhật. Bucket `s3://noaa-himawari9/` cũng đã kiểm chứng tồn tại song song (index cập nhật 11/2025).
  → **Khuyến nghị:** nhóm có thể dùng **cả 2 bucket** (`noaa-himawari8` và `noaa-himawari9`) tuỳ ngày cần dữ liệu, không cần chỉ dùng himawari9 như đề xuất sai trước đó. Điểm cần lưu ý thật sự: **mỗi file sản phẩm full-disk nặng 85MB–800MB** (khác hẳn NASA POWER/GHCN nhẹ vài KB-MB), nên nếu dùng, chỉ nên tải sản phẩm đã crop theo vùng Đông Nam Á hoặc dùng Range request lấy phần cần thiết, không tải nguyên file full-disk toàn cầu.

---

## 9. Các nguồn "nên hoạt động thế nào" trong pipeline của project (tóm tắt khuyến nghị, đã cập nhật)

```
Batch (chạy 1 lần/định kỳ, TV1 phụ trách):
  NASA POWER API ──┐
  Open-Meteo API ──┼─→ raw JSON/CSV (Raw Zone) → chuẩn hoá đơn vị/thời gian → Curated Zone (Parquet)
  NOAA GHCN/ISD S3 ─┘        (không cần key, dùng requests/urllib đơn giản)

  ERA5 — 2 duong song song, khong can cho nhau:
    ARCO-ERA5 (Google Cloud, xr.open_zarr, KHONG can dang ky) ─→ dung NGAY tuan 1 de code/test pipeline
    Copernicus CDS (can .cdsapirc, dang ky truoc) ─────────────→ chay song song, dung lam nguon
                                                                   trich dan chinh thuc trong bao cao

Tuỳ chọn/mở rộng (chỉ nếu còn thời gian, TV1/TV2 sau khi xong phần lõi):
  CHIRPS ─→ tải file tĩnh .tif.gz qua HTTPS thường, không cần key
  Himawari-8 hoặc Himawari-9 (AWS S3, không cần key) ─→ CHỈ tải phần cần thiết
    (Range request/crop theo vùng ĐNA), KHÔNG tải nguyên file full-disk 85MB–800MB/file

Dashboard (TV4):
  folium/leaflet + tile OSM mặc định ─→ vẽ bản đồ nền cho heatmap
  Nominatim ─→ chỉ dùng 1 lần lúc chuẩn hoá địa chỉ trạm (không gọi lặp lại, có cache)
```

**Không có nguồn nào trong 4 nguồn lõi bị chặn hoàn toàn**, và sau đợt kiểm tra bổ sung này, **ERA5 cũng không còn là điểm nghẽn** — nhóm có ARCO-ERA5 (Google Cloud) làm đường vào miễn phí, không cần đăng ký, dùng được ngay hôm nay, song song với việc xin tài khoản CDS chính thức để trích dẫn học thuật.
