# Lịch sử, hệ sinh thái & nghiên cứu đã dùng — từng nguồn dữ liệu (bổ sung cho 02-nguon-du-lieu.md)

Tài liệu này bổ sung 3 phần còn thiếu cho mỗi nguồn đã liệt kê ở `02-nguon-du-lieu.md` nhóm A-E
(định dạng/độ phân giải/cách truy cập đã verify ở file đó, KHÔNG lặp lại ở đây): **Lịch sử** (ra
đời khi nào, ai làm, vì sao), **Hệ sinh thái** (thư viện/công cụ/cộng đồng), **Nghiên cứu đã dùng**
(bài báo thật, ưu tiên liên quan Đông Nam Á/bài toán của nhóm). Toàn bộ thông tin lấy từ WebSearch
thật (nguồn trích kèm mỗi mục), không suy đoán — mục nào search không ra thì ghi rõ "⚠️ CHƯA XÁC
MINH" thay vì bịa.

---

## A. Dữ liệu tái phân tích lưới toàn cầu (Gridded Reanalysis)

### ERA5 (Copernicus CDS / ARCO-ERA5)

**Lịch sử.** ERA5 là thế hệ thứ 5 trong dòng tái phân tích của ECMWF — phả hệ bắt đầu từ dự án FGGE
(1979), qua ERA-15 (giữa 1990s), ERA-40 (2001-2003, phủ 1957-2002), ERA-Interim (2006-2019), rồi
đến ERA5. ERA5 được phát triển trong khuôn khổ Copernicus Climate Change Service (C3S) từ 2015, dựa
trên nghiên cứu của 2 dự án EU ERA-CLIM/ERA-CLIM2, dùng engine IFS Cy41r2 (vận hành thật năm 2016).
Đây là tái phân tích ĐẦU TIÊN của ECMWF sản xuất như 1 dịch vụ vận hành thường trực thay vì 1 dự án
nghiên cứu đơn lẻ. Production bắt đầu 1/2016; tháng 1/2019 ECMWF công bố mở rộng thêm 21 năm về
trước, đưa chuỗi dữ liệu về tới 1940. Thế hệ kế tiếp ERA6 (độ phân giải ~14km) đang phát triển, dự
kiến phát hành theo giai đoạn từ cuối 2026 — nhóm nên theo dõi khi ERA5 được thay thế.

**Hệ sinh thái.** Thư viện chuẩn: `cdsapi` (gọi REST API CDS), `xarray` + `cfgrib`/`netCDF4` (đọc
GRIB2/NetCDF4), `xarray.open_zarr` + `gcsfs`/`s3fs` (đọc bản Zarr trên GCS/AWS/Planetary Computer —
đúng cách nhóm đang dùng cho ARCO-ERA5). Cộng đồng: Copernicus Climate Data Store forum, ECMWF
Confluence wiki. Được dùng làm backbone cho rất nhiều nền tảng khác (Google Earth Engine, Microsoft
Planetary Computer, Pangeo).

**Nghiên cứu đã dùng.** Wong et al. (2024), *Environmental Research Communications* 6(10), DOI
10.1088/2515-7620/ad810b — dùng ERA5-derived UTCI/Mean Radiant Temperature phân tích số ngày khó
chịu nhiệt khắp Đông Nam Á 1940-2020, các nước ven biển có mức tăng tuyệt đối nhỏ hơn nhưng tần suất
ngày khó chịu tăng mạnh hơn (hiệu ứng điều hoà của biển). Nghiên cứu Đại học Southampton (ERA5 +
rain-gauge) cho thấy ERA5 phản ánh đúng xu hướng tăng mưa mùa đông ở lục địa Đông Nam Á, liên quan
vận chuyển ẩm từ Tây Thái Bình Dương/Biển Đông. Xie et al. (2025), *PLOS ONE*, DOI
10.1371/journal.pone.0319477 — so sánh ERA5 cùng CPC/CHIRPS/IMERG/PERSIANN với bộ chuẩn SAOBS trên
toàn Đông Nam Á (2001-2017), phát hiện hiệu năng lệch mạnh theo vùng — kết luận quan trọng cho nhóm
khi chọn nguồn mưa chính.
Nguồn: [ECMWF re-analysis (Wikipedia)](https://en.wikipedia.org/wiki/ECMWF_re-analysis), [ECMWF ERA5 overview](https://www.ecmwf.int/node/18797), [Copernicus going forward looking back](https://climate.copernicus.eu/going-forward-looking-back).

### NCEP/NCAR Reanalysis 1

**Lịch sử.** Dự án hợp tác NCEP-NCAR nhằm tái dựng chuỗi phân tích khí quyển toàn cầu dài hạn, ban
đầu dự định phủ 40 năm (1957-1996) nhưng khi sản xuất thực tế đã lùi về tới 1948 và tiếp tục cập
nhật tới nay. Bài báo nền tảng: Kalnay et al. (1996), *Bulletin of the American Meteorological
Society* 77, 437-472, "The NCEP/NCAR 40-year reanalysis project". Hệ thống đồng hoá dữ liệu được
GIỮ CỐ ĐỊNH suốt giai đoạn tái phân tích để tránh bước nhảy khí hậu giả do thay đổi hệ thống vận
hành — nhưng thập kỷ đầu (1948-1957) vẫn thưa quan trắc tầng cao. Các trung tâm dữ liệu hiện khuyến
cáo R1 đã bị thay thế (superseded), chỉ nên dùng bổ trợ, không nên dùng làm nguồn nghiên cứu chính.

**Hệ sinh thái.** Phân phối dạng NetCDF qua `psl.noaa.gov` (đọc bằng `xarray`/`netCDF4` chuẩn), lưới
Gaussian ~1.875°. Dùng rộng rãi trong giới nghiên cứu khí hậu nhờ chuỗi thời gian dài và miễn phí
không cần đăng ký.

**Nghiên cứu đã dùng.** ⚠️ CHƯA XÁC MINH — tìm kiếm chưa ra bài nghiên cứu cụ thể dùng R1 riêng cho
khu vực Đông Nam Á trong phạm vi tìm kiếm của fork này; R1 phù hợp hơn vai trò đối chiếu xu hướng
dài hạn (nhóm đã ghi đúng mục đích này trong bảng gợi ý phối hợp của `02-nguon-du-lieu.md`).
Nguồn: [NCEP/NCAR Reanalysis 1, GDEX/UCAR](https://gdex.ucar.edu/datasets/d090000), [Kalnay et al. 1996 PDF](https://radiometrics.com/wp-content/uploads/2021/10/kistler_bams01.pdf).

### MERRA-2 (NASA GMAO)

**Lịch sử.** Do NASA Global Modeling and Assimilation Office (GMAO) phát triển, kế thừa MERRA gốc
(phát hành 2009, phủ 1979-2/2016). MERRA-2 bắt đầu sản xuất 6/2014 như dự án TRUNG GIAN giữa MERRA
cũ và thế hệ coupled reanalysis tương lai — động lực chính: MERRA cũ không đồng hoá được quan trắc
vệ tinh hyperspectral/radiance, GPS-Radio Occultation hiện đại, và có nguy cơ suy giảm chất lượng
nếu một số nền tảng quan trắc cũ ngừng hoạt động. Điểm mới quan trọng: MERRA-2 có đồng hoá aerosol
tương tác ngược vào hoàn lưu khí quyển (aerosol-climate feedback).

**Hệ sinh thái.** NetCDF4/HDF5 qua NASA Earthdata (`disc.gsfc.nasa.gov`), OPeNDAP cho subset theo
vùng (tránh tải nguyên global) — đọc bằng `xarray`/`h5py`, cần tài khoản Earthdata (dùng chung cho
GPM IMERG, MODIS/VIIRS).

**Nghiên cứu đã dùng.** Ohno, Irie, Momoi & da Silva (2022), *Progress in Earth and Planetary
Science* 9, DOI 10.1186/s40645-022-00520-4 — đánh giá sản phẩm aerosol MERRA-2 so với quan trắc
sky-radiometer/MAX-DOAS trên bán đảo Đông Dương, phát hiện MERRA-2 đánh giá thấp AOD ở độ cao <1km
mùa khô (do thiếu ước lượng phát thải đốt sinh khối gần mặt đất) — bài học quan trọng nếu nhóm dùng
MERRA-2 đối chiếu aerosol/bức xạ cho khu vực Đông Nam Á lục địa. Zheng et al. — đánh giá động lực
aerosol và phơi nhiễm dân cư Đông Nam Á kết hợp MERRA-2 + AERONET (nền tảng cloud-based).
Nguồn: [GMAO MERRA-2 project page](https://gmao.gsfc.nasa.gov/reanalysis/merra-2/), [Ohno et al. 2022](https://progearthplanetsci.springeropen.com/articles/10.1186/s40645-022-00520-4).

### JRA-55 (Cơ quan Khí tượng Nhật Bản — JMA)

**Lịch sử.** Tái phân tích toàn cầu thứ 2 của JMA, kế thừa JRA-25 nhằm sửa các lỗi hệ thống đã biết
(lệch lạnh tầng bình lưu thấp, lệch khô vùng Amazon). Sản xuất bắt đầu 2010, hoàn thành toàn bộ năm
2013, sau đó chuyển sang cập nhật gần thời gian thực (hệ thống JCDAS). Là tái phân tích đầu tiên áp
dụng 4D-Var cho chuỗi 55 năm kể từ ERA-40. Phủ từ 1958 (khi quan trắc radiosonde toàn cầu bắt đầu
đều đặn). Tài liệu tham chiếu chính: Kobayashi et al. (2015), *Journal of the Meteorological Society
of Japan* 93(1), 5-48.

**Hệ sinh thái.** Định dạng GRIB, phân phối qua NCAR Research Data Archive (`rda.ucar.edu`, cần tài
khoản học thuật miễn phí) — đọc bằng `cfgrib`/`eccodes`. Có biến thể JRA-55C (chỉ đồng hoá quan trắc
thông thường, không vệ tinh) dùng để đối chiếu ảnh hưởng của dữ liệu vệ tinh lên tái phân tích.

**Nghiên cứu đã dùng.** ⚠️ CHƯA XÁC MINH cho bài nghiên cứu cụ thể Đông Nam Á trong phạm vi tìm kiếm
— JRA-55 phù hợp nhất với vai trò "tái phân tích độc lập đối chiếu chéo ERA5" (đúng như đề xuất sẵn
có trong `02-nguon-du-lieu.md`), nhưng bản thân bài báo Kobayashi et al. 2015 đã ghi nhận lỗi hệ
thống riêng (lệch nóng tầng đối lưu trên, mất cân bằng năng lượng toàn cầu, mưa nhiệt đới quá mức)
— cần lưu ý nếu nhóm dùng JRA-55 làm "ground truth" đối chiếu.
Nguồn: [Kobayashi et al. 2015, J-STAGE](https://www.jstage.jst.go.jp/article/jmsj/93/1/93_2015-001/_article).

---

## B. Dữ liệu quan trắc trạm mặt đất (Point / Station Time-series)

### NOAA GHCN-Daily

**Lịch sử.** Phát triển tại NOAA National Climatic Data Center (nay là NCEI), mô phỏng theo người
tiền nhiệm GHCN-Monthly (Peterson & Vose 1997/1998), ra đời để lấp khoảng trống dữ liệu NGÀY (nhiều
quốc gia chỉ công khai số liệu tháng). Bài tổng quan chính: Menne, Durre, Vose, Gleason & Houston
(2012), *Journal of Atmospheric and Oceanic Technology*, bản thảo đầu từ 11/2010. Tích hợp từ ~30
nguồn dữ liệu khác nhau, >80.000 trạm, 180 quốc gia — khoảng 2/3 số trạm chỉ đo mưa. GHCN-Daily
KHÔNG được đồng nhất hoá (not homogenized) — NOAA cảnh báo không dùng trực tiếp để định lượng biến
đổi khí hậu mà không xử lý thêm. Phát triển mới nhất: GHCNh (hourly) — thế hệ kế tiếp dự kiến thay
thế cả GHCN-Daily lẫn ISD.

**Hệ sinh thái.** CSV/Fixed-width qua `s3://noaa-ghcn-pds/` (AWS, không cần key) hoặc FTP NCEI — đọc
bằng `pandas` trực tiếp hoặc thư viện `wetterdienst` (Python, hỗ trợ nhiều nguồn NOAA/DWD cùng lúc).
Có DOI chính thức cho từng phiên bản dataset.

**Nghiên cứu đã dùng.** Menne et al. (2012) là tài liệu trích dẫn bắt buộc cho mọi nghiên cứu dùng
GHCN-Daily. ⚠️ CHƯA XÁC MINH bài nghiên cứu cụ thể Đông Nam Á dùng trực tiếp GHCN-Daily trong phạm
vi tìm kiếm — nhưng NOAA khuyến cáo rõ: cần homogenize trước khi dùng cho phân tích xu hướng, điểm
nhóm cần lưu ý khi dùng làm ground truth đối chiếu ERA5/CHIRPS.
Nguồn: [Menne et al. 2012 PDF](https://ncei.noaa.gov/pub/data/ghcn/daily/papers/menne-durre-etalsubmitted.pdf), [GHCN-Daily readme](https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt).

### NOAA ISD / Global Hourly

**Lịch sử.** Bắt đầu phát triển 1998 như hoạt động chung của NCDC và Không quân/Hải quân Mỹ (Federal
Climate Complex, Asheville) — mục tiêu chấm dứt tình trạng mỗi mạng lưới trạm có hệ QC riêng không
thống nhất. Tên gốc "Integrated Surface Hourly" (ISH), đổi thành "Integrated Surface Data" (ISD)
khoảng 2004 khi thêm dữ liệu tổng hợp ngày/tháng. Version 1 (2001) ghép dữ liệu NCDC+Navy+Air Force;
Version 2 (2003) thêm lớp QC đầu tiên. Tích hợp >100 nguồn gốc khác nhau, một số bản ghi từ cuối
1800s nhưng phần lớn trạm bắt đầu 1948-1973. NCEI hiện định hướng người dùng mới sang GHCNh (kế
nhiệm trực tiếp ISD).

**Hệ sinh thái.** CSV/Fixed-width qua `s3://noaa-global-hourly-pds/` (AWS). Hệ thống xử lý nội bộ gọi
là Integrated Surface Data Processing System (ISDPS).

**Nghiên cứu đã dùng.** ⚠️ CHƯA XÁC MINH bài nghiên cứu cụ thể — phần "Nghiên cứu" của ISD nên gắn
chung với GHCN-Daily (nhiều nghiên cứu khí hậu trạm dùng cả 2 làm nguồn bổ sung nhau, nhưng web
search không trả về bài tách riêng ISD).
Nguồn: [ISD history, AMS Confex PDF](https://ams.confex.com/ams/pdfpapers/131387.pdf).

### NOAA GSOD

**Lịch sử.** Sản phẩm PHÁI SINH (derived) từ ISD, do NCDC (nay NCEI) tổng hợp hàng ngày từ dữ liệu
giờ/synop gốc, nguồn gốc gắn với kho Air Weather Service/US Air Force Climatology Center. Phủ
1929-nay, nhưng giai đoạn từ 1973 trở đi mới đầy đủ nhất; cần tối thiểu 4 lần quan trắc/ngày để tính
tổng hợp.

**Hệ sinh thái.** CSV qua `s3://noaa-gsod-pds/` (AWS). Lưu ý license: đơn vị đã quy đổi (knot...) nên
có thể lệch nhẹ so với báo cáo gốc; giờ tính theo GMT.

**Nghiên cứu đã dùng.** ⚠️ CHƯA XÁC MINH — không tìm được bài nghiên cứu cụ thể; có 1 bài phản biện
kỹ thuật (Speedwell Weather) cảnh báo KHÔNG nên dùng GSOD để định giá hợp đồng rủi ro thời tiết do
hạn chế chất lượng — đáng lưu ý nếu nhóm định dùng GSOD cho ứng dụng tài chính/bảo hiểm.
Nguồn: [GSOD limitations, Speedwell Weather](https://www.speedwellweather.com/PDF/PressDocuments/The%20Limitations%20of%20the%20GSOD%20Weather%20Data%20Set.pdf).

### Meteostat

**Lịch sử.** Sáng lập bởi Christian Lamprecht (lập trình viên người Đức, sống tại Canada) năm 2015,
mục tiêu công khai hoá dữ liệu thời tiết/khí hậu miễn phí cho tất cả mọi người. Thư viện Python
version 1.0 phát hành 12/2020. Lamprecht từng tự mô tả là người duy nhất phát triển dự án ở giai
đoạn đầu, sau đó kêu gọi cộng đồng đóng góp.

**Hệ sinh thái.** Thư viện Python `meteostat` (MIT license cho code; dữ liệu khí tượng theo giấy phép
CC BY-NC 4.0 — LƯU Ý: phi thương mại, cần ghi rõ trong báo cáo license của nhóm). REST API + JSON/CSV
+ bulk download. Tổng hợp dữ liệu từ NOAA, DWD, ECCC... thành 1 giao diện thống nhất.

**Nghiên cứu đã dùng.** ⚠️ CHƯA XÁC MINH — không tìm được bài nghiên cứu học thuật cụ thể dùng
Meteostat trong phạm vi tìm kiếm của fork này (Meteostat phổ biến hơn trong ứng dụng thực tế/dashboard
hơn là trích dẫn học thuật).
Nguồn: [Meteostat patrons/founder](https://meteostat.net/en/patrons), [Meteostat about](https://meteostat.net/nl/about).

### ECA&D (European Climate Assessment & Dataset)

**Lịch sử.** Khởi động bởi KNMI (Hà Lan) và European Climate Support Network năm 1998 (một số tài
liệu khác ghi nhận 2000/2003 là mốc chuyển đổi coordinating role hoặc kế nhiệm dự án ECA — các nguồn
không thống nhất hoàn toàn về mốc chính xác, nhưng 1998 là năm được nhắc nhiều nhất). Giai đoạn
2003-2008 được EUMETNET đồng tài trợ; từ 2009 KNMI tự tài trợ toàn bộ và chuyển từ hoạt động nghiên
cứu sang vận hành thường trực (operational). Sau đó được công nhận là Regional Climate Centre của
WMO khu vực VI (châu Âu/Trung Đông) cho dữ liệu quan trắc độ phân giải cao.

**Hệ sinh thái.** TXT/CSV tải bulk từ `ecad.eu`, không cần đăng ký.

**Nghiên cứu đã dùng.** ⚠️ CHƯA XÁC MINH liên quan Đông Nam Á (ECA&D chỉ phủ châu Âu — nguồn này
đóng vai trò tham khảo phương pháp QC, không phải nguồn dữ liệu trực tiếp cho vùng nghiên cứu của
nhóm, đúng như `02-nguon-du-lieu.md` đã ghi).
Nguồn: [KNMI ECA&D project page](https://www.knmi.nl/research/observations-data-technology/projects/the-european-climate-assessment-dataset).

### Iowa Environmental Mesonet (IEM) — ASOS/METAR

**Lịch sử.** Dự án của Iowa State University (Ames, Iowa), xây dựng trên hợp tác giữa các nhóm công/
tư/học thuật — mục tiêu ban đầu là tích hợp nhiều nguồn dữ liệu môi trường rời rạc thành 1 điểm thu
thập/lưu trữ duy nhất, vì mạng ASOS/NWS/FAA chuẩn không đủ dày đặc không-thời gian để phân giải hiện
tượng mesoscale. ⚠️ CHƯA XÁC MINH năm thành lập chính xác và người sáng lập — tài liệu tìm được chỉ
xác nhận các tác giả liên quan sớm gồm Daryl Herzmann, Ray Arritt, Dennis Todey (Iowa State/South
Dakota State), qua 1 slide deck hội nghị AMS 2003.

**Hệ sinh thái.** CSV qua form request hoặc API (`mesonet.agron.iastate.edu/request/download.phtml`).
Lưu ý: IEM tự ghi rõ ít QC trên kho lưu trữ lịch sử ("IEM performs little quality control on this
historical archive") — khác với GHCN-Daily/ISD đã qua QC chính thức của NOAA.

**Nghiên cứu đã dùng.** ⚠️ CHƯA XÁC MINH bài nghiên cứu cụ thể trong phạm vi tìm kiếm.
Nguồn: [IEM ASOS background, AMS Confex](https://ams.confex.com/ams/pdfpapers/41314.pdf).

---

## C. Dữ liệu mưa vệ tinh độ phân giải cao (Satellite Precipitation)

### CHIRPS (Climate Hazards Group)

**Lịch sử.** Phát triển bởi UC Santa Barbara Climate Hazards Group + USGS Center for Earth Resources
Observation and Science, công bố chính thức trong Funk et al. (2015), *Scientific Data*, DOI
10.1038/sdata.2015.66 (tiền thân là báo cáo USGS Data Series 832, Funk et al. 2014). Động lực ra đời:
hỗ trợ hệ thống cảnh báo sớm nạn đói của USAID (FEWS NET — Famine Early Warning Systems Network).
Kết hợp Cold Cloud Duration hồng ngoại vệ tinh + trạm mặt đất, dùng kỹ thuật nội suy "smart
interpolation" — độ trễ sản phẩm sơ bộ ~2 ngày, sản phẩm cuối ~3 tuần.

**Hệ sinh thái.** GeoTIFF/NetCDF, tải bulk từ `chc.ucsb.edu/data/chirps` hoặc qua Google Earth Engine
catalog (`UCSB-CHG/CHIRPS/DAILY`) — đọc bằng `rasterio`/`xarray`+`rioxarray`. Pete Peterson (đồng tác
giả) đã từ bỏ toàn bộ bản quyền dữ liệu CHIRPS theo pháp luật cho phép (public domain-like).

**Nghiên cứu đã dùng (liên quan trực tiếp Việt Nam/ĐNA):**
- Nghiên cứu ngô nhờ nước trời tại Việt Nam (PMC8752618): so 5 sản phẩm mưa vệ tinh, kết luận
  CHIRP/S tốt hơn đáng kể CMORPH/CPC/GSMaP (hệ số tương quan cao, sai số thấp); mô phỏng năng suất
  cho RMSE 715 kg/ha.
- Nghiên cứu Tây Bắc Việt Nam (11 trạm, 2000-2024): CHIRPS có RMSE thấp hơn nhưng đánh giá thấp mưa
  ở trạm độ cao lớn; GSMaP tương quan nhỉnh hơn một chút; hiệu chỉnh theo độ cao giúp giảm RMSE.
- Nghiên cứu Thừa Thiên Huế (2020-2023): MSWEP vượt trội hơn CHIRPS/GSMaP/GPM (R=0.58, RMSE=23mm/
  ngày) — CHIRPS KHÔNG phải luôn tốt nhất, phụ thuộc vùng.
- Xie et al. (2025), *PLOS ONE* — CHIRPS là 1 trong 5 sản phẩm so sánh toàn ĐNA với benchmark SAOBS.

Kết luận quan trọng cho nhóm: CHIRPS hoạt động TỐT ở vùng thấp/nông nghiệp nhưng ĐÁNH GIÁ THẤP mưa
vùng núi cao và có thể lệch cao ở vùng địa hình phức tạp phía Nam Việt Nam (theo 1 nghiên cứu REMO) —
cần kiểm chứng theo vùng cụ thể, không giả định CHIRPS luôn đáng tin cậy nhất cho toàn lãnh thổ.
Nguồn: [Funk et al. 2015, USGS](https://pubs.usgs.gov/publication/70188064), [Vietnam maize CHIRPS study, PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8752618/).

### GPM IMERG (NASA/JAXA)

**Lịch sử.** Kế nhiệm trực tiếp của TRMM (vệ tinh chung NASA-JAXA phóng 1997, chính thức ngừng
8/2015). GPM Core Observatory phóng 27/2/2014 từ Tanegashima (Nhật), bằng tên lửa H-IIA — phóng bị
trì hoãn bởi động đất Fukushima 2011 và đóng cửa chính phủ Mỹ 10/2013. Radar mưa kép tần số (DPR) do
JAXA chế tạo, microwave imager do Ball Aerospace (Mỹ) chế tạo. IMERG thay thế sản phẩm TRMM 3B42
(TMPA), bắt đầu phát hành từ 12/3/2014 — kết hợp dữ liệu từ 12 vệ tinh thành 1 bản đồ liền mạch, dùng
GPM Core Observatory làm chuẩn hiệu chỉnh ("reference standard").

**Hệ sinh thái.** HDF5/NetCDF4 qua NASA Earthdata (`disc.gsfc.nasa.gov`, dataset GPM_3IMERGHH) — đọc
bằng `h5py`/`xarray`. Cần tài khoản Earthdata (dùng chung MERRA-2/MODIS).

**Nghiên cứu đã dùng (liên quan trực tiếp Việt Nam/ĐNA):**
- Nghiên cứu các sự kiện cực đoan 2020 tại Việt Nam, *Remote Sensing* 2024, DOI (MDPI
  remotesensing-16-00805): so 7 sản phẩm mưa với >1200 trạm đo mưa Việt Nam ở lưới 0.02° — radar
  thời tiết tốt nhất, nhưng cả ERA5-Land lẫn IMERG đều KHÔNG bắt được cường độ mưa cực đoan cao
  nhất; GPM-DPR cho kết quả khả quan hơn ở mưa cường độ cao.
  CHIRPS có RMSE thấp hơn nhưng đánh giá thấp mưa ở trạm độ cao lớn.
- Do Van Quang và cộng sự, Thuyloi University (2021), *Polish Journal of Environmental Studies* —
  đánh giá IMERG cho Bắc Việt Nam, dùng TRMM làm benchmark; kết luận IMERG KHÔNG cải thiện đáng kể
  so với TRMM khi so với trạm đo mưa, nhưng vẫn là lựa chọn thay thế hợp lý.
- Xie et al. (2025), *PLOS ONE* — IMERG là 1 trong 5 sản phẩm so sánh toàn ĐNA.

Nguồn: [GPM launch history, Universe Today](https://www.universetoday.com/106727/powerful-new-next-gen-usjapan-gpm-satellite-to-revolutionize-global-precipitation-observations-and-climate-science-research), [Vietnam 2020 extreme events validation, MDPI Remote Sensing 2024](https://mdpi-res.com/d_attachment/remotesensing/remotesensing-16-00805/article_deploy/remotesensing-16-00805.pdf).

---

## D. Bức xạ mặt trời & năng lượng (Radiative)

### NASA POWER

**Lịch sử.** Dự án "Prediction of Worldwide Energy Resources" của NASA Langley Research Center, ra
đời để cải tiến bộ dữ liệu năng lượng tái tạo hiện có và khai thác dữ liệu từ các hệ thống vệ tinh
mới. Phục vụ 3 cộng đồng người dùng: Năng lượng tái tạo, Công trình bền vững (Sustainable Buildings),
và Nông-khí hậu học (Agroclimatology) — phần agroclimatology là trọng tâm gần nhất với bài toán nông
nghiệp của nhóm. Dữ liệu bức xạ lấy chủ yếu từ CERES/GEWEX, khí tượng từ GEOS/MERRA-2 (tức POWER
thực chất là lớp "đóng gói thân thiện người dùng" trên nền MERRA-2 cho phần khí tượng). Có hội nghị
cộng đồng người dùng thường niên (Global Community Summit) bắt đầu từ 2022.

**Hệ sinh thái.** JSON/CSV qua REST API `power.larc.nasa.gov/api`, không cần đăng ký; hỗ trợ định
dạng DSSAT ASCII sẵn cho mô hình cây trồng (rất tiện nếu nhóm làm ứng dụng nông nghiệp). Lưới 1°×1°
cho phần agroclimatology.

**Nghiên cứu đã dùng (liên quan trực tiếp Đông Nam Á):**
- Yuan et al. (2022), *Nature Food*, DOI 10.1038/s43016-022-00477-z, "Southeast Asia must narrow
  down the yield gap to continue to be a major rice bowl" — dùng NASA POWER Agro-climatic database
  thay thế dữ liệu trạm bị thiếu ở 8 điểm Indonesia + 3 điểm Thái Lan. Đây là bài liên quan GẦN NHẤT
  tới bài toán của nhóm (nông nghiệp lúa gạo Đông Nam Á).
- Nghiên cứu Cotabato, Philippines (*Data in Brief*, 12/2023) — dùng NASA POWER 2007-2021 kết hợp
  hồi quy tuyến tính đa biến xác định yếu tố khí hậu ảnh hưởng năng suất lúa tưới/nhờ nước trời.
- Lưu ý quan trọng: 1 nghiên cứu đối chiếu dữ liệu thời tiết toàn cầu phát hiện NASA POWER ĐƠN LẺ mô
  phỏng năng suất kém khớp với mô phỏng dựa trạm thật — kết hợp bức xạ NASA POWER với dữ liệu trạm
  NOAA cho kết quả khớp tốt hơn nhiều. → gợi ý: nhóm nên dùng POWER làm nguồn BỨC XẠ bổ sung, không
  thay thế hoàn toàn dữ liệu trạm cho các biến khác.
Nguồn: [NASA POWER overview, Earthdata](https://www.earthdata.nasa.gov/learn/articles/power-overview), [Yuan et al. 2022, Nature Food supplement](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs43016-022-00477-z/MediaObjects/43016_2022_477_MOESM1_ESM.pdf).

---

## E. Nguồn tổng hợp qua API tiện lợi (Aggregator APIs)

### Open-Meteo Historical API

**Lịch sử.** Sáng lập bởi Patrick Zippenfenig (kỹ sư/nhà khí tượng Thuỵ Sĩ) qua công ty OpenMeteo
GmbH, năm 2022 (⚠️ mốc năm lấy từ 1 trang review bên thứ 3, chưa đối chiếu được trang chính thức của
công ty). Open-Meteo KHÔNG tự chạy mô hình dự báo riêng mà tổng hợp/chuẩn hoá dữ liệu mở từ >15 cơ
quan khí tượng quốc gia (bao gồm ERA5/DWD/NOAA) thành 1 API thống nhất — đúng mô tả trong
`02-nguon-du-lieu.md`. Mã nguồn mở theo AGPLv3, có thể tự host bằng Docker.

**Hệ sinh thái.** REST API không cần key, gói Python `openmeteo-requests`, gói R `openmeteo`/
`ropenmeteo` (CRAN). DOI Zenodo chính thức cho trích dẫn: 10.5281/ZENODO.7970649.

**Nghiên cứu đã dùng.** 1 bài arXiv preprint (2512.09076) "Beyond the Hype: Comparing Lightweight and
Deep Learning Models for Air Quality Forecasting" dùng Open-Meteo làm nguồn biến khí tượng đầu vào
(nhiệt độ, điểm sương) cho mô hình dự báo chất lượng không khí. ⚠️ CHƯA XÁC MINH bài học thuật khác
ngoài preprint này trong phạm vi tìm kiếm — Open-Meteo phổ biến hơn trong ứng dụng thực tế/demo hơn
là trích dẫn học thuật chính thống, phù hợp vai trò "demo nhanh" mà `02-nguon-du-lieu.md` đã ghi.
Nguồn: [Open-Meteo about Zippenfenig](https://gappsy.com/tools/open-meteo/), [Open-Meteo license/citation](https://open-meteo.com/en/license).

### Visual Crossing Weather API

**Lịch sử.** Công ty thành lập năm 2003, trụ sở tại Reston, Virginia (Mỹ), theo CB Insights và
Neudata. ⚠️ CHƯA XÁC MINH tên người sáng lập/lịch sử phát triển chi tiết — không tìm được trong phạm
vi tìm kiếm của fork này.

**Hệ sinh thái.** REST API, JSON/CSV, có UI truy vấn nhanh trên web.

**Nghiên cứu đã dùng.** ⚠️ CHƯA XÁC MINH.
Nguồn: [Visual Crossing, CB Insights](https://www.cbinsights.com/company/visual-crossing).

### Weatherbit Historical API

**Lịch sử.** Công ty thành lập năm 2017, trụ sở Raleigh, North Carolina (Mỹ), theo CB Insights. ⚠️
CHƯA XÁC MINH tên người sáng lập. Dữ liệu tổng hợp từ >20 bộ dữ liệu khác nhau (quan trắc trạm, mô
hình số GFS/ECMWF, mô hình phân giải cao HRRR/NAM/DWD ICON, và cả sản phẩm tái phân tích).

**Hệ sinh thái.** REST API, JSON, cần đăng ký key miễn phí (giới hạn request/ngày).

**Nghiên cứu đã dùng.** ⚠️ CHƯA XÁC MINH.
Nguồn: [Weatherbit, CB Insights](https://www.cbinsights.com/company/weatherbit/alternatives-competitors), [Weatherbit về chúng tôi](https://cdn.weatherbit.io/about).

---

## Tổng kết nhanh — nguồn nào có bằng chứng nghiên cứu Đông Nam Á mạnh nhất

Xếp theo mức độ liên quan trực tiếp tới bài toán của nhóm (tích hợp đa nguồn khí tượng, phát hiện dị
thường, nông nghiệp/năng lượng/UAV, khu vực Đông Nam Á — ưu tiên Việt Nam khi có):

1. **CHIRPS** — nhiều nhất bằng chứng Việt Nam cụ thể (4 nghiên cứu khác nhau, kết luận trái chiều
   theo vùng — dữ liệu quý để nhóm tự làm case study "không nguồn nào tốt nhất tuyệt đối").
2. **GPM IMERG** — 2 nghiên cứu Việt Nam trực tiếp + 1 nghiên cứu toàn vùng.
3. **ERA5** — 1 nghiên cứu toàn vùng + 1 nghiên cứu Đông Nam Á lục địa, nhưng không có nghiên cứu
   riêng cho Việt Nam trong phạm vi tìm kiếm.
4. **NASA POWER** — có bài *Nature Food* 2022 liên quan trực tiếp nông nghiệp lúa gạo ĐNA.
5. **MERRA-2** — nhiều nghiên cứu aerosol Đông Nam Á (Đông Dương, Indonesia, Philippines).
6. **NCEP/NCAR R1, JRA-55, GHCN-Daily, ISD, GSOD, Meteostat, ECA&D, IEM-ASOS, Visual Crossing,
   Weatherbit** — chưa xác minh được nghiên cứu học thuật gắn trực tiếp Đông Nam Á trong phạm vi tìm
   kiếm của fork này; các nguồn này vẫn hợp lệ cho vai trò ground-truth/đối chiếu/demo mà
   `02-nguon-du-lieu.md` đã gán, chỉ là chưa có trích dẫn khoa học cụ thể để đưa vào case-study.

**Khuyến nghị cho module "Bài tập lớn":** ưu tiên case-study CHIRPS và GPM IMERG (nhiều bằng chứng
Việt Nam nhất, kể cả mâu thuẫn giữa các nghiên cứu — chính là ví dụ sống động nhất cho khái niệm
Veracity/đối chiếu đa nguồn của môn học), sau đó ERA5/NASA POWER/MERRA-2. Các nguồn còn thiếu nghiên
cứu nên trình bày trung thực là "nguồn hạ tầng/ground-truth đã verify kỹ thuật, nhưng nhóm chưa tìm
thấy nghiên cứu học thuật trích dẫn trực tiếp cho khu vực" — không bịa thêm cho đủ.
