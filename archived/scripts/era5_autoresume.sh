#!/bin/bash
# Tu dong tiep tuc tai ERA5 (qua resource_guard) moi khi dang nhap/khoi dong lai may —
# de nho sap sap khong lam mat tien do (file da tai se tu bo qua, chi tai phan con thieu).
# Khong lam gi neu da co tien trinh dang chay (tranh chay trung).
cd "/Users/tuannghiat/Downloads/HUST - Tích hợp và xử lý dữ liệu lớn - Vũ Tuyết Trinh/IT5427-Nhom16-TichHopKhiTuong" || exit 1

if pgrep -f "download_era5_full.py" > /dev/null 2>&1; then
    exit 0
fi

# Da tai het chua? (không còn gì để làm thì không tự chạy nữa)
remaining=$(python3 -c "
import sys
sys.path.insert(0, 'scripts')
from download_era5_full import month_range, VARIABLES, OUT
import os
months = month_range('2020-01', '2024-12')
total = len(months) * len(VARIABLES)
done = sum(1 for v in VARIABLES for m in months if os.path.exists(os.path.join(OUT, v, f'{m}.nc')))
print(total - done)
" 2>/dev/null)

if [ "$remaining" = "0" ]; then
    exit 0
fi

nohup python3 scripts/resource_guard.py run --interval 30 -- \
    python3 scripts/download_era5_full.py --concurrency 1 --workers 2 \
    >> data_samples/era5_full/download.log 2>&1 < /dev/null &
disown
