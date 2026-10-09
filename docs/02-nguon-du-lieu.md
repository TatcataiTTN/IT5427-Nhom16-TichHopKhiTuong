# Danh sách mở rộng: Nguồn dữ liệu khí tượng/khí hậu quá khứ — 100% miễn phí

Tài liệu này bổ sung cho `03-ke-hoach-160-tasks.md`, liệt kê **càng nhiều nguồn dữ liệu thời tiết/khí hậu lịch sử miễn phí càng tốt**, gom theo nhóm chức năng để nhóm dễ chọn phối hợp — vẫn giữ 4 nguồn lõi đã chốt trong đề cương (ERA5, NOAA ISD/GHCN, NASA POWER, Open-Meteo) làm xương sống, các nguồn còn lại dùng để **làm giàu Variety**, **đối chiếu Veracity (cross-validation)**, **mở rộng Volume**, hoặc bổ sung ảnh vệ tinh (mục H) làm nguồn dữ liệu tùy chọn cho các ứng dụng hỗ trợ UAV/quan sát khu vực.

> Tiêu chí chọn: (1) miễn phí vĩnh viễn cho mục đích học thuật/nghiên cứu, (2) không cần thẻ tín dụng, (3) có API hoặc bulk download rõ ràng. Nguồn nào cần đăng ký tài khoản (miễn phí) sẽ ghi rõ.

---

## A. Dữ liệu tái phân tích lưới toàn cầu (Gridded Reanalysis)

Dùng làm **backbone không gian** — mô phỏng khí quyển liên tục theo lưới, chuẩn cho việc nội suy về trạm điểm.

| # | Nguồn | Mô tả | Độ phân giải | Giai đoạn | Định dạng | Truy cập | Đăng ký |
|---|---|---|---|---|---|---|---|
| 1 | **ERA5** (Copernicus CDS) | Tái phân tích khí quyển hàng đầu của ECMWF, đồng hoá vệ tinh + trạm mặt đất | 0.25° (~28km), giờ | 1940–nay | NetCDF4/GRIB2 | `cdsapi` (Python), REST API | Cần tài khoản CDS (miễn phí) |
| 2 | **ERA5 trên AWS Open Data** | Bản ERA5 dạng Zarr, tối ưu cho truy vấn cloud, khỏi cần tải nguyên file | 0.25°, giờ | 2008–nay (một phần biến) | Zarr (đọc bằng `xarray` + `s3fs`) | `s3://era5-pds/` — **đã kiểm chứng 30/9/2026: đây là bucket "Requester Pays"**, request ẩn danh bị từ chối (HTTP 403). Cần **tài khoản AWS thật** (đăng ký thẻ tín dụng) để truy cập, không miễn phí hoàn toàn như ghi chú ban đầu | Cần tài khoản AWS (khác với CDS) |
| 2b | **ERA5 trên Google Cloud (ARCO-ERA5)** ⭐ *mới, khuyến nghị* | Bản ERA5 đã re-chunk tối ưu cho truy vấn cục bộ (Analysis-Ready Cloud-Optimized), hợp tác Google×ECMWF | 0.25° (1440×721), giờ | **1959–2021-12-31** (tên kho ghi "2022" nhưng mốc thời gian cuối thực tế là 23h ngày 31/12/2021 — đã kiểm chứng 9/10/2026 bằng cách đọc thật `ds.time.values`) | Zarr (đọc bằng `xarray.open_zarr`) | `gcs://gcp-public-data-arco-era5/ar/1959-2022-full_37-1h-0p25deg-chunk-1.zarr-v2` — **đã kiểm chứng 30/9/2026: tải thật `.zmetadata` thành công, HTTP 200, 35 biến, hoàn toàn public; 9/10/2026: tải thật subset 3 ngày vùng ĐNA (31 MB, 4 biến) thành công** | **Không cần** tài khoản/key gì cả (`storage_options={"token":"anon"}`) |
| 2c | **ERA5 trên Microsoft Planetary Computer** *(dự phòng)* | Cùng dữ liệu ERA5, lưu trên Azure Blob, cấp token tự động khi gọi API | Tuỳ dataset | Tuỳ dataset | Zarr qua STAC + `planetary-computer` SDK | `planetarycomputer.microsoft.com` — đã kiểm chứng: endpoint cấp SAS token hoạt động, nhưng cần dùng đúng SDK `pip install planetary-computer` (tự ghép URL thủ công sẽ lỗi auth) | Không cần đăng ký (token tự cấp) |
| 3 | **NCEP/NCAR Reanalysis 1** (NOAA PSL) | Tái phân tích lâu đời nhất, độ phân giải thô hơn nhưng chuỗi thời gian rất dài | ~2.5°, ngày/tháng | 1948–nay | NetCDF | HTTP trực tiếp từ `psl.noaa.gov` | Không cần đăng ký |
| 4 | **MERRA-2** (NASA GMAO) | Tái phân tích của NASA, mạnh về aerosol/bức xạ — hữu ích để đối chiếu chéo với ERA5 | 0.5°×0.625°, giờ | 1980–nay | NetCDF4/HDF5 | NASA Earthdata (`disc.gsfc.nasa.gov`), OPeNDAP subset theo vùng | Cần tài khoản NASA Earthdata (miễn phí) |
| 5 | **JRA-55** (Cơ quan Khí tượng Nhật Bản) | Tái phân tích độc lập của Nhật, tốt để đối chiếu chéo với ERA5 | 1.25°, 6 giờ | 1958–nay | GRIB | NCAR RDA (`rda.ucar.edu`) | Cần tài khoản RDA (miễn phí, học thuật) |

---

## B. Dữ liệu quan trắc trạm mặt đất (Point / Station Time-series)

Dùng làm **ground truth** để hiệu chỉnh và kiểm chuẩn lưới ở mục A.

| # | Nguồn | Mô tả | Số trạm | Giai đoạn | Định dạng | Truy cập | Đăng ký |
|---|---|---|---|---|---|---|---|
| 6 | **NOAA GHCN-Daily** | Nhiệt độ max/min, mưa, tuyết theo ngày | ~100.000 trạm toàn cầu | 1750–nay (tuỳ trạm) | CSV/Fixed-width | `s3://noaa-ghcn-pds/` (AWS, không cần key) hoặc FTP NCEI | Không cần |
| 7 | **NOAA ISD / Global Hourly** | Nhiệt độ, gió, áp suất, tầm nhìn xa theo giờ — chi tiết hơn GHCN | ~14.000 trạm | 1901–nay | CSV/Fixed-width | `s3://noaa-global-hourly-pds/` (AWS) | Không cần |
| 8 | **NOAA GSOD** (Global Summary of the Day) | Tổng hợp ngày từ ISD, dễ dùng hơn ISD thô | ~9.000 trạm | 1929–nay | CSV | `s3://noaa-gsod-pds/` (AWS) | Không cần |
| 9 | **Meteostat** | Nền tảng tổng hợp dữ liệu từ NOAA, DWD, ECCC... thành 1 API/thư viện Python thống nhất | Hàng chục nghìn trạm + dữ liệu mô hình | Tuỳ trạm, nhiều trạm >30 năm | JSON/CSV, thư viện `meteostat` (pandas-ready) | REST API + Python package `pip install meteostat` | Không cần key (free tier rộng) |
| 10 | **ECA&D** (European Climate Assessment & Dataset) | Chuỗi ngày chất lượng cao, hữu ích để đối chiếu phương pháp QC | ~11.000 trạm (chủ yếu châu Âu) | Nhiều trạm >100 năm | TXT/CSV | Tải bulk từ `ecad.eu` | Không cần |
| 11 | **Iowa Environmental Mesonet (IEM) — ASOS/METAR** | Dữ liệu METAR sân bay toàn cầu tần suất cao (5–60 phút), hợp phần "dữ liệu hàng không/nhiễu động" trong outline gốc | Hàng nghìn sân bay | Khác nhau theo sân bay, nhiều nơi >20 năm | CSV qua form request hoặc API | `mesonet.agron.iastate.edu/request/download.phtml` | Không cần |

---

## C. Dữ liệu mưa vệ tinh độ phân giải cao (Satellite Precipitation)

Bổ sung cho biến lượng mưa — vốn ERA5/trạm thường sai số lớn ở vùng nhiệt đới/núi.

| # | Nguồn | Mô tả | Độ phân giải | Giai đoạn | Định dạng | Truy cập | Đăng ký |
|---|---|---|---|---|---|---|---|
| 12 | **CHIRPS** (Climate Hazards Group) | Kết hợp vệ tinh + trạm, rất phổ biến cho vùng nhiệt đới/Đông Nam Á | 0.05° (~5km), ngày/tháng | 1981–nay | GeoTIFF/NetCDF | Bulk download `chc.ucsb.edu/data/chirps`, hoặc qua Google Earth Engine | Không cần |
| 13 | **GPM IMERG** (NASA/JAXA) | Vệ tinh đo mưa toàn cầu độ phân giải cao, cập nhật gần thời gian thực và có bản lịch sử | 0.1° (~10km), 30 phút | 2000–nay | HDF5/NetCDF4 | NASA Earthdata (`disc.gsfc.nasa.gov`, dataset GPM_3IMERGHH) | Cần tài khoản Earthdata (miễn phí) |

---

## D. Bức xạ mặt trời & năng lượng (Radiative)

| # | Nguồn | Mô tả | Độ phân giải | Giai đoạn | Định dạng | Truy cập | Đăng ký |
|---|---|---|---|---|---|---|---|
| 14 | **NASA POWER** | Bức xạ sóng ngắn, nhiệt độ, gió phục vụ nông nghiệp/năng lượng — đã có trong đề cương | 0.5°, giờ/ngày | 1981–nay | JSON/CSV | REST API `power.larc.nasa.gov/api` | Không cần |

---

## E. Nguồn tổng hợp qua API tiện lợi (Aggregator APIs — dễ tích hợp nhất)

Nhóm này phù hợp để **demo nhanh** hoặc làm nguồn đối chiếu thứ 4–5 mà không tốn nhiều công parse.

| # | Nguồn | Mô tả | Giai đoạn | Định dạng | Truy cập | Giới hạn free |
|---|---|---|---|---|---|---|
| 15 | **Open-Meteo Historical API** | Nội suy từ ERA5/DWD/NOAA, rất dễ dùng — đã có trong đề cương | 1940–nay | JSON/Parquet | REST, không cần key | Không giới hạn cho non-commercial |
| 16 | **Meteostat API** | Như mục B.9, có thể dùng như API tổng hợp thay vì chỉ điểm trạm | Tuỳ trạm | JSON/CSV | REST + thư viện Python | Free tier rộng, có thể tự host (open-source) |
| 17 | **Visual Crossing Weather API** | Dữ liệu lịch sử theo toạ độ, dễ dùng, có UI truy vấn nhanh | ~2000s–nay | JSON/CSV | REST API | 1.000 record/ngày miễn phí (cần đăng ký email) |
| 18 | **Weatherbit Historical API** | Dữ liệu lịch sử theo giờ/ngày | Vài chục năm gần đây | JSON | REST API | Free tier giới hạn số request/ngày (cần đăng ký) |

---

## F. Sol khí & chất lượng không khí (Aerosol/AQ)

Nhóm dữ liệu bổ sung cho Veracity/Variety — mây, sương mù, nồng độ sol khí (AOD) là các biến khí quyển có tương tác phi tuyến với nhiệt độ/bức xạ, hữu ích để đối chiếu chéo và làm phong phú bộ đặc trưng cho mô hình phân tích khí hậu.

| # | Nguồn | Mô tả | Độ phân giải | Giai đoạn | Định dạng | Truy cập | Đăng ký |
|---|---|---|---|---|---|---|---|
| 19 | **AERONET** (NASA) | Mạng lưới trạm mặt đất đo Aerosol Optical Depth (AOD) trực tiếp bằng sun-photometer — độ chính xác cao nhất cho AOD | Điểm trạm, phút/giờ | 1993–nay (tuỳ trạm) | CSV/TXT | `aeronet.gsfc.nasa.gov` | Không cần |
| 20 | **MODIS/VIIRS Aerosol & Cloud Products** (NASA) | AOD và độ che phủ mây dạng lưới vệ tinh, bổ sung không gian cho AERONET | 1–10km, ngày | 2000 (MODIS)/2012 (VIIRS)–nay | HDF/NetCDF | NASA Earthdata hoặc Google Earth Engine catalog | Cần Earthdata (miễn phí) |
| 21 | **Copernicus Sentinel-5P (TROPOMI)** | Thành phần khí quyển: aerosol index, mây, NO₂, hơi nước cột — độ phân giải rất cao | ~5.5×3.5km, ngày | 2018–nay | NetCDF | Copernicus Data Space Ecosystem (`dataspace.copernicus.eu`) | Cần tài khoản (miễn phí) |
| 22 | **OpenAQ** | Dữ liệu chất lượng không khí (PM2.5, PM10...) từ mạng lưới trạm quan trắc mở toàn cầu — proxy cho sol khí gần mặt đất | Điểm trạm, giờ | 2015–nay (tuỳ trạm/thành phố) | JSON (REST API) | **⚠️ đã kiểm chứng 30/9/2026: API v1/v2 (`api.openaq.org/v2/...`) đã bị khai tử hoàn toàn — trả về HTTP 410 Gone: "Version 1 and Version 2 API endpoints are retired". Phải dùng **v3** (`api.openaq.org/v3/...`), và khác endpoint cũ, key phải gửi qua HTTP header `X-API-Key` (không phải query param như v2) | Cần API key miễn phí, đăng ký tại `explore.openaq.org/register` (đã đổi domain đăng ký so với ghi chú cũ) |

---

## G. Nền tảng truy xuất hợp nhất (giảm công sức ghép nhiều nguồn)

Nếu hạ tầng nhóm hạn chế băng thông/lưu trữ, các nền tảng này cho phép **truy vấn trực tiếp trên cloud** thay vì tải toàn bộ file thô về máy — vẫn tính là dữ liệu "đã tải/xử lý" hợp lệ cho pipeline vì output cuối cùng do nhóm tự trích xuất.

| # | Nguồn | Mô tả | Bộ dữ liệu có sẵn liên quan | Truy cập | Đăng ký |
|---|---|---|---|---|---|
| 23 | **Google Earth Engine** | Catalog hàng trăm bộ dữ liệu khí hậu/vệ tinh đã tiền xử lý (ERA5, CHIRPS, MODIS, Sentinel-5P...) trong 1 API Python/JavaScript | ERA5, CHIRPS, MODIS AOD, Sentinel-5P, GPM | `earthengine.google.com` + `earthengine-api` (Python) | Cần tài khoản Google + đăng ký non-commercial (miễn phí) |
| 24 | **NOAA CDO / Climate Data Online** | Giao diện tìm kiếm hợp nhất cho GHCN, ISD, và nhiều bộ NOAA khác, có API token | GHCN, ISD, Storm Events... | `www.ncdc.noaa.gov/cdo-web/` | Cần token miễn phí qua email |

---

## G2. Ranh giới hành chính (Dashboard) — mới bổ sung 9/10/2026

4 nguồn lõi (A–D) chỉ trả về dữ liệu theo toạ độ điểm/lưới, **không có ranh giới hành chính** — mà TV4/Dashboard cần ranh giới này để vẽ bản đồ và tổng hợp (aggregate) số liệu theo quốc gia/tỉnh. Mục này bổ sung nguồn ranh giới miễn phí, đã kiểm chứng thực nghiệm.

| # | Nguồn | Mô tả | Độ chi tiết | Định dạng | Truy cập | Đăng ký |
|---|---|---|---|---|---|---|
| 25 | **Natural Earth** ⭐ *khuyến nghị* | Ranh giới quốc gia/tỉnh chuẩn, nhẹ, dùng rộng rãi trong giới GIS mã nguồn mở | 1:10m / 1:50m / 1:110m (càng số nhỏ càng chi tiết) | Shapefile | `naturalearth.s3.amazonaws.com` — **đã kiểm chứng 9/10/2026: tải thật `ne_50m_admin_0_countries.zip` (800KB), đọc bằng `geopandas`, xác nhận đủ 9 nước ĐNA** | Không cần |
| 26 | **GADM** | Ranh giới hành chính chi tiết tới cấp huyện/xã (level 2–3), phù hợp nếu cần phân tích dưới cấp tỉnh | Tới level 3–4 tuỳ nước | Shapefile/GeoPackage | `gadm.org/download_country.html` | Không cần (giới hạn dùng phi thương mại) |

---

## H. Ảnh vệ tinh quan sát Trái Đất & khí tượng (tùy chọn — không bắt buộc trong lõi 160 tác vụ)

Nhóm dữ liệu **mở rộng**, dùng nếu nhóm còn dư thời gian sau khi hoàn thiện 4 nguồn lõi (mục A–D). Đây là dữ liệu ảnh raster (khác hẳn NetCDF/CSV/JSON), cần thêm kỹ năng xử lý ảnh — chỉ nên bổ sung ở Tuần 3–4 sau khi pipeline lõi đã ổn định, không đưa vào mốc nộp đề cương 5/10.

| # | Nguồn | Mô tả | Độ phân giải | Giai đoạn | Định dạng | Truy cập | Đăng ký |
|---|---|---|---|---|---|---|---|
| 25 | **Sentinel-1 SAR** (Copernicus) | Ảnh radar khẩu độ tổng hợp — xuyên được mây/sương mù, chụp được bất kể điều kiện thời tiết, dùng làm nguồn ảnh mặt đất ưu tiên khi trời xấu | ~5–20m, chu kỳ 6–12 ngày | 2014–nay | GeoTIFF/SAFE | Copernicus Data Space Ecosystem (`dataspace.copernicus.eu`) | Cần tài khoản (miễn phí) |
| 26 | **Sentinel-2 / Landsat-8,9** (quang học) | Ảnh quang học đa phổ độ phân giải cao — chỉ dùng được khi trời quang (không mây che phủ khu vực chụp) | 10–30m, chu kỳ 5–16 ngày | 2013/2015–nay | GeoTIFF/JP2 | Copernicus Data Space Ecosystem hoặc USGS EarthExplorer | Cần tài khoản (miễn phí) |
| 27 | **Himawari-8 và Himawari-9** (JMA) hoặc **GOES** (NOAA) | Ảnh vệ tinh khí tượng địa tĩnh — theo dõi mây, bão, đối lưu gần thời gian thực trên toàn khu vực Đông Nam Á | ~500m–2km, 10 phút/lần | 2015–nay | NetCDF/HDF5 | AWS Open Data — **đã kiểm chứng 30/9/2026: tải thật 1MB đầu 1 file sản phẩm mây ngày 12/10/2025 từ `s3://noaa-himawari8/`, xác nhận file HDF5 hợp lệ, vẫn đang được cập nhật đều đặn (không hề ngừng hoạt động như nhận định sai ở lần kiểm tra trước)**. `s3://noaa-himawari9/` cũng tồn tại song song (vệ tinh chính từ cuối 2022, Himawari-8 đóng vai trò dự phòng nhưng vẫn phát dữ liệu). **Lưu ý:** mỗi file full-disk nặng 85MB–800MB, nên crop theo vùng hoặc dùng HTTP Range request, không tải nguyên file | Không cần key (AWS, public bucket) |

**Ứng dụng cụ thể trong đề tài (nếu triển khai):**
- **Logic chọn ảnh theo thời tiết**: dùng độ che phủ mây từ ERA5/Himawari để quyết định — trời quang thì ưu tiên Sentinel-2/Landsat (ảnh quang học, thông tin phổ phong phú hơn); trời nhiều mây thì bắt buộc dùng Sentinel-1 SAR (không bị mây cản).
- **Panel dashboard**: hiển thị gợi ý loại ảnh vệ tinh khả dụng cho một khu vực/thời điểm dựa trên dự báo mây từ kho dữ liệu lõi — đây là ví dụ cụ thể cho giá trị gia tăng (Value) của việc tích hợp đa nguồn, không cần crawl/xử lý khối lượng lớn ảnh thật để chứng minh khái niệm.

---

## Gợi ý phối hợp theo hướng nghiên cứu

| Mục tiêu | Nguồn chính | Nguồn đối chiếu/bổ sung |
|---|---|---|
| Phát hiện dị thường khí hậu theo khu vực (nhiệt, ẩm, gió) | ERA5 + NOAA ISD/GHCN | NCEP/NCAR (kiểm tra xu hướng dài hạn), Meteostat (điền khuyết trạm) |
| Đánh giá lượng mưa cực đoan vùng nhiệt đới | CHIRPS + GPM IMERG | NOAA GHCN-Daily (đối chiếu trạm), Open-Meteo |
| Giám sát chất lượng không khí đô thị | OpenAQ + AERONET (AOD) | MODIS/VIIRS Aerosol, Sentinel-5P |
| Năng lượng tái tạo (điện mặt trời) | NASA POWER | MERRA-2, Sentinel-5P (che phủ mây) |
| Hỗ trợ ra quyết định bay UAV an toàn | ERA5/NOAA (gió, mưa) | Himawari-8/9 (mây/đối lưu gần thời gian thực, tuỳ chọn) |
| Gợi ý chọn ảnh vệ tinh theo thời tiết (tuỳ chọn) | Himawari-8/9 (độ che phủ mây) | Sentinel-1 SAR (khi nhiều mây), Sentinel-2/Landsat (khi trời quang) |

---

## Lưu ý khi triển khai

- **Không cần key**: ERA5-AWS Zarr, NCEP/NCAR, NOAA GHCN/ISD/GSOD (AWS), Open-Meteo, ECA&D, CHIRPS bulk, IEM/ASOS, AERONET — ưu tiên dùng trước nếu muốn giảm thủ tục đăng ký.
- **Cần đăng ký miễn phí (email, vài phút)**: Copernicus CDS, NASA Earthdata (dùng chung 1 tài khoản cho MERRA-2, GPM IMERG, MODIS/VIIRS), Copernicus Data Space Ecosystem, Google Earth Engine, OpenAQ, NOAA CDO, Visual Crossing, Weatherbit.
- **Giấy phép/license**: mọi nguồn trên đều cho phép dùng cho mục đích nghiên cứu/học thuật phi thương mại — TV1 vẫn nên lưu lại điều khoản sử dụng (attribution) của từng nguồn để trích dẫn trong báo cáo (đã có tác vụ "Kiểm tra bảo mật/license dữ liệu" ở Tuần 4, #7 trong kế hoạch 160 tác vụ).
- **Khuyến nghị số lượng thực tế**: không cần dùng hết 27 nguồn — chọn 4 nguồn lõi (đã chốt) + 2–3 nguồn đối chiếu (VD: CHIRPS cho mưa, MERRA-2/Meteostat để điền khuyết và đối chiếu trạm) là đủ để chứng minh **Variety** ở mức "Đạt tuyệt đối" mà không làm vỡ khối lượng công việc của nhóm 4 người trong 6 tuần. Ảnh vệ tinh (mục H) chỉ nên thêm ở Tuần 3–4 nếu còn dư thời gian, tuyệt đối không đưa vào mốc nộp đề cương 5/10.
