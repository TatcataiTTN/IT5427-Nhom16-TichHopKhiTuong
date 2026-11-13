"""
Trình kiểm tra + giám sát tài nguyên hệ thống trước và trong khi chạy lệnh nặng (download ERA5
song song, benchmark Spark local[*], v.v.) — ra đời sau sự cố thật ngày 12/11: chạy ERA5 với
concurrency=6 cộng các app đang mở (LM Studio, VS Code, Chrome...) đã làm cạn RAM, gây 2 sự kiện
Jetsam (kernel diệt tiến trình vì cạn RAM), Word/LM Studio/Preview bị "hang", máy phải khởi động
lại (xem /Library/Logs/DiagnosticReports/JetsamEvent-*.ips lúc 15:13-15:14 hôm đó).

Dùng công cụ sẵn có của macOS, không cần cài thêm gì:
- memory_pressure: chỉ số "System-wide memory free percentage" (macOS tự tính, kể cả trang nhớ
  nén/có thể giải phóng, đáng tin hơn "Pages free" thô vì macOS vốn dùng RAM rảnh để cache).
- sysctl vm.swapusage: % swap đang dùng.
- uptime: load average 1 phút, so với số core (sysctl hw.ncpu).
- df: dung lượng đĩa trống.
GPU: lệnh ERA5/Spark trong đồ án này không dùng GPU (thuần CPU + mạng), nên KHÔNG có cổng kiểm
tra GPU ở đây. Nếu sau này chạy job dùng GPU (vd PINN training), macOS chỉ cho đọc bộ nhớ GPU qua
`sudo powermetrics`, cần mật khẩu nên không phù hợp để tự động hoá — phải kiểm tay riêng.

Chạy:
  python3 scripts/resource_guard.py check
  python3 scripts/resource_guard.py run -- python3 scripts/download_era5_full.py --concurrency 3
"""
import argparse
import os
import re
import signal
import subprocess
import sys
import time

LOG = os.path.join(os.path.dirname(__file__), "..", "data_samples", "resource_guard.log")

# Ngưỡng AN TOÀN để KHỞI ĐỘNG lệnh mới (nghiêm hơn ngưỡng huỷ giữa chừng, vì lúc khởi động
# ta còn lựa chọn không chạy; lúc đang chạy thì chỉ còn lựa chọn huỷ để cứu máy).
START_MEM_FREE_FLOOR_PCT = 25
START_SWAP_CEILING_PCT = 80
START_DISK_FREE_FLOOR_GB = 30

# Ngưỡng HUỶ GIỮA CHỪNG khi đang watch (lỏng hơn chút, chỉ huỷ khi THỰC SỰ nguy hiểm)
ABORT_MEM_FREE_FLOOR_PCT = 15
ABORT_SWAP_CEILING_PCT = 95


def _run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=False).stdout


def mem_free_pct():
    out = _run(["memory_pressure"])
    m = re.search(r"System-wide memory free percentage:\s*(\d+)%", out)
    return int(m.group(1)) if m else None


def swap_used_pct():
    out = _run(["sysctl", "vm.swapusage"])
    m = re.search(r"total\s*=\s*([\d.]+)M\s*used\s*=\s*([\d.]+)M", out)
    if not m:
        return 0.0
    total, used = float(m.group(1)), float(m.group(2))
    return round(100.0 * used / total, 1) if total > 0 else 0.0


def load_avg_1m():
    out = _run(["uptime"])
    m = re.search(r"load averages?:\s*([\d.]+)", out)
    return float(m.group(1)) if m else None


def ncpu():
    return int(_run(["sysctl", "-n", "hw.ncpu"]).strip() or "1")


def disk_free_gb(path="."):
    out = _run(["df", "-g", path])
    lines = [l for l in out.splitlines() if l.strip()]
    if len(lines) < 2:
        return None
    parts = lines[-1].split()
    return float(parts[3]) if len(parts) >= 4 else None


def snapshot():
    return {
        "mem_free_pct": mem_free_pct(),
        "swap_used_pct": swap_used_pct(),
        "load_avg_1m": load_avg_1m(),
        "ncpu": ncpu(),
        "disk_free_gb": disk_free_gb(),
    }


def verdict(snap, mem_floor, swap_ceiling):
    """mem_free_pct (macOS tự tính, gồm cả trang có thể giải phóng) là điều kiện CHẶN CỨNG, vì đó
    là tín hiệu "có thể cấp RAM NGAY BÂY GIỜ không". swap_used_pct KHÔNG dùng để chặn cứng: macOS
    không chủ động đẩy dữ liệu từ swap về RAM chỉ vì RAM đã rảnh trở lại (chỉ trang nào bị truy cập
    lại mới được nạp về), nên swap cao có thể chỉ là "dư nợ" còn sót từ sự cố trước, không phải dấu
    hiệu đang nguy hiểm NGAY — chặn cứng theo swap% dễ khiến trình này từ chối chạy mãi dù máy đã
    thực sự ổn. Swap cao chỉ làm HẠ mức song song gợi ý (xem recommend()), không chặn hẳn.
    """
    reasons = []
    if snap["mem_free_pct"] is not None and snap["mem_free_pct"] < mem_floor:
        reasons.append(f"RAM rảnh {snap['mem_free_pct']}% < ngưỡng {mem_floor}%")
    if snap["swap_used_pct"] >= swap_ceiling:
        reasons.append(f"Swap đang dùng {snap['swap_used_pct']}% >= ngưỡng {swap_ceiling}% "
                        f"(cảnh báo tham khảo, không chặn)")
    hard_fail = snap["mem_free_pct"] is not None and snap["mem_free_pct"] < mem_floor
    return (not hard_fail), reasons


def recommend(snap):
    """Gợi ý concurrency/workers AN TOÀN cho job kiểu download_era5_full.py, dựa trên RAM rảnh
    hiện tại (điều kiện chính) và swap (chỉ hạ mức song song, không chặn). Đây là heuristic đơn
    giản (không mô hình hoá chính xác), chọn an toàn hơn là nhanh."""
    mf = snap["mem_free_pct"] or 0
    swap_high = snap["swap_used_pct"] >= 85
    if mf >= 60 and not swap_high:
        return {"concurrency": 4, "workers": 2, "note": "RAM rảnh nhiều, có thể chạy song song vừa phải"}
    if mf >= 40:
        note = "RAM rảnh trung bình, song song nhẹ"
        if swap_high:
            note += " (swap đang cao, giảm 1 bậc so với RAM thật cho an toàn)"
            return {"concurrency": 1, "workers": 2, "note": note}
        return {"concurrency": 2, "workers": 2, "note": note}
    if mf >= START_MEM_FREE_FLOOR_PCT:
        return {"concurrency": 1, "workers": 2, "note": "RAM còn ít, chạy tuần tự cho an toàn"}
    return {"concurrency": 0, "workers": 0, "note": "Không an toàn để chạy lúc này"}


def log(msg):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def cmd_check(args):
    snap = snapshot()
    ok, reasons = verdict(snap, START_MEM_FREE_FLOOR_PCT, START_SWAP_CEILING_PCT)
    rec = recommend(snap)
    print(f"RAM rảnh: {snap['mem_free_pct']}% | Swap dùng: {snap['swap_used_pct']}% | "
          f"Load 1p: {snap['load_avg_1m']}/{snap['ncpu']} core | Đĩa trống: {snap['disk_free_gb']}GB")
    if snap["disk_free_gb"] is not None and snap["disk_free_gb"] < START_DISK_FREE_FLOOR_GB:
        ok = False
        reasons.append(f"Đĩa trống {snap['disk_free_gb']}GB < ngưỡng {START_DISK_FREE_FLOOR_GB}GB")
    if ok:
        print(f"AN TOÀN để chạy. Gợi ý: --concurrency {rec['concurrency']} --workers {rec['workers']} "
              f"({rec['note']})")
        sys.exit(0)
    else:
        print("CHƯA AN TOÀN để chạy lệnh nặng:")
        for r in reasons:
            print(f"  - {r}")
        print("Gợi ý: đóng app nặng RAM (LM Studio, nhiều tab Chrome...), chờ vài phút rồi check lại.")
        sys.exit(1)


def cmd_run(args):
    snap = snapshot()
    ok, reasons = verdict(snap, START_MEM_FREE_FLOOR_PCT, START_SWAP_CEILING_PCT)
    if not ok:
        log("TU CHOI chay: " + "; ".join(reasons))
        sys.exit(1)

    log(f"Bat dau giam sat lenh: {' '.join(args.command)}")
    log(f"Snapshot luc bat dau: {snap}")
    proc = subprocess.Popen(args.command, start_new_session=True)  # process group riêng -> kill gọn
    try:
        while True:
            ret = proc.poll()
            if ret is not None:
                log(f"Lenh ket thuc, exit code {ret}")
                sys.exit(ret)
            snap = snapshot()
            ok, reasons = verdict(snap, ABORT_MEM_FREE_FLOOR_PCT, ABORT_SWAP_CEILING_PCT)
            if not ok:
                log("NGUY HIEM, HUY lenh de bao ve may: " + "; ".join(reasons))
                log(f"Snapshot luc huy: {snap}")
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                time.sleep(5)
                if proc.poll() is None:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                sys.exit(137)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        raise


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)

    p_check = sub.add_parser("check", help="Chi kiem tra, khong chay gi")
    p_check.set_defaults(func=cmd_check)

    p_run = sub.add_parser("run", help="Kiem tra, roi chay lenh duoi giam sat, huy neu nguy hiem")
    p_run.add_argument("--interval", type=float, default=30.0, help="Giay giua 2 lan kiem tra")
    p_run.add_argument("command", nargs=argparse.REMAINDER)
    p_run.set_defaults(func=cmd_run)

    args = parser.parse_args()
    if args.action == "run":
        if args.command and args.command[0] == "--":
            args.command = args.command[1:]
        if not args.command:
            parser.error("Thieu lenh can chay sau '--'")
    args.func(args)


if __name__ == "__main__":
    main()
