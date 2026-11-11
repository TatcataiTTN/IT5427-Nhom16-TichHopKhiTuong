"""
Dung HTML tu than (visualization-earth skill, "video/anh tinh tai lap duoc" + hieu ung dong don gian
bang Canvas 2D -- khong can CesiumJS/satvis vi chi can 1 khung canh tinh + lop dong, khong can
xoay/zoom 3D that). Du lieu: bao Yagi, 7/9/2024, 32 tram/diem that (warehouse WeatherObs).

Nhan theo quy tac skill: Real = toa do tram, wind_speed/dir trung binh ngay, tong precip_mm ngay,
%RH trung binh ngay (deu la gia tri thuc do/API that). Derived = truong vector gio noi suy IDW
giua cac tram de ve hat chuyen dong, va lop may la proxy do am (khong phai anh ve tinh may that).

Chay: python3 viz/scripts/build_earth_wind_rain_html.py --out viz/output/earth_wind_rain.html
"""
import argparse
import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "output", "yagi_20240907_stations.json")

TEMPLATE = """<title>Bão Yagi — Gió &amp; Mưa</title>
<style>
  :root {
    --bg: #0b1220; --fg: #e8edf4; --muted: #8696ab; --accent: #ff6a3d;
    --panel: rgba(13, 20, 33, 0.82); --border: rgba(255,255,255,0.12);
  }
  @media (prefers-color-scheme: light) {
    :root:not([data-theme="dark"]) {
      --bg: #eef1f6; --fg: #121823; --muted: #51607a; --accent: #d94e22;
      --panel: rgba(255,255,255,0.88); --border: rgba(0,0,0,0.12);
    }
  }
  :root[data-theme="light"] {
    --bg: #eef1f6; --fg: #121823; --muted: #51607a; --accent: #d94e22;
    --panel: rgba(255,255,255,0.88); --border: rgba(0,0,0,0.12);
  }
  * { box-sizing: border-box; }
  body { background: var(--bg); color: var(--fg); font-family: -apple-system, "Segoe UI", Roboto, sans-serif;
         padding-inline: 16px; padding-block: 18px; }
  h1 { font-size: 1.15rem; margin: 0 0 4px; text-wrap: balance; }
  .sub { color: var(--muted); font-size: 0.82rem; margin: 0 0 14px; }
  .stage { position: relative; width: 100%; max-width: 760px; margin: 0 auto; aspect-ratio: 1400 / 1440;
           border-radius: 10px; overflow: hidden; border: 1px solid var(--border); background: #0b1220; }
  .stage canvas, .stage img { position: absolute; inset: 0; width: 100%; height: 100%; }
  #wind, #fx { pointer-events: none; }
  .tooltip { position: absolute; pointer-events: none; background: var(--panel); border: 1px solid var(--border);
             border-radius: 8px; padding: 8px 10px; font-size: 0.78rem; line-height: 1.45; min-width: 170px;
             backdrop-filter: blur(4px); display: none; z-index: 5; }
  .tooltip b { color: var(--accent); }
  .legend { display: flex; flex-wrap: wrap; gap: 14px; align-items: center; margin-top: 10px; font-size: 0.78rem;
            color: var(--muted); }
  .legend .bar { display: inline-flex; height: 8px; width: 120px; border-radius: 4px; overflow: hidden; vertical-align: middle; }
  .legend .bar span { flex: 1; height: 100%; }
  .legend .row { display: flex; align-items: center; gap: 6px; }
  .note { font-size: 0.74rem; color: var(--muted); margin-top: 10px; max-width: 760px; margin-inline: auto; }
  .note b { color: var(--fg); }
  .controls { max-width: 760px; margin: 8px auto 0; display: flex; gap: 8px; }
  button { background: var(--panel); color: var(--fg); border: 1px solid var(--border); border-radius: 6px;
           padding: 5px 10px; font-size: 0.78rem; cursor: pointer; }
</style>

<h1>Bão Yagi đổ bộ — 7/9/2024</h1>
<p class="sub">Gió, mưa, ẩm thật tại 32 trạm/điểm Đông Nam Á (warehouse WeatherObs, Nhóm 16 IT5427). Hạt gió và lớp mây là hiệu ứng dựng để nhìn xu hướng; số liệu nền là số đo thật.</p>

<div class="stage" id="stage">
  <img src="sea_basemap.png" alt="Bản đồ nền Đông Nam Á (Natural Earth qua cartopy)">
  <canvas id="cloud"></canvas>
  <canvas id="wind"></canvas>
  <canvas id="fx"></canvas>
  <div class="tooltip" id="tooltip"></div>
</div>

<div class="controls">
  <button id="toggle">Tạm dừng</button>
</div>

<div class="legend">
  <div class="row">Tốc độ gió (m/s):
    <span class="bar"><span style="background:#3b82f6"></span><span style="background:#22c55e"></span><span style="background:#eab308"></span><span style="background:#f97316"></span><span style="background:#ef4444"></span></span>
    0 → 25+
  </div>
  <div class="row"><span style="color:#9ec6ff">●</span> hạt mưa (precip &gt; 5mm/ngày tại trạm)</div>
  <div class="row"><span style="color:#cfd8e3">◍</span> lớp mây (proxy độ ẩm RH%)</div>
</div>

<p class="note">
<b>Real</b>: toạ độ 32 trạm/điểm, tốc độ/hướng gió trung bình ngày, tổng lượng mưa ngày, %RH trung bình — đều lấy từ warehouse WeatherObs thật (ISD/GHCN/NASA_POWER/OPEN_METEO), ngày 7/9/2024 (Yagi đổ bộ).
<b>Derived</b>: trường vector gió nội suy IDW giữa các trạm; lớp "mây" là bán kính/độ mờ tỉ lệ với %RH (proxy độ ẩm, KHÔNG phải ảnh mây vệ tinh thật — dữ liệu cloud_cover_pct không có trong warehouse hiện tại).
<b>Schematic</b>: tốc độ hạt gió trên màn hình đã phóng to nhiều lần so với thời gian thực để thấy rõ hướng/độ mạnh tương đối giữa các vùng, không dùng để đọc ra tốc độ di chuyển thật.
</p>

<script>
const STATIONS = __STATIONS_JSON__;
const EXTENT = { lonMin: 92, lonMax: 127, latMin: -11, latMax: 25 };

function project(lon, lat, w, h) {
  const x = (lon - EXTENT.lonMin) / (EXTENT.lonMax - EXTENT.lonMin) * w;
  const y = (EXTENT.latMax - lat) / (EXTENT.latMax - EXTENT.latMin) * h;
  return [x, y];
}

const stage = document.getElementById('stage');
const cloudCv = document.getElementById('cloud');
const windCv = document.getElementById('wind');
const fxCv = document.getElementById('fx');
const tooltip = document.getElementById('tooltip');
let W = 0, H = 0, DPR = Math.min(window.devicePixelRatio || 1, 2);

function sizeCanvases() {
  const rect = stage.getBoundingClientRect();
  W = rect.width; H = rect.height;
  for (const cv of [cloudCv, windCv, fxCv]) {
    cv.width = W * DPR; cv.height = H * DPR;
    cv.getContext('2d').setTransform(DPR, 0, 0, DPR, 0, 0);
  }
}

// --- IDW wind-field grid (Derived), precomputed once from real per-station u,v ---
const GRID_N = 46;
let windGrid = [];
function buildWindGrid() {
  windGrid = [];
  for (let j = 0; j <= GRID_N; j++) {
    const row = [];
    const lat = EXTENT.latMax - (j / GRID_N) * (EXTENT.latMax - EXTENT.latMin);
    for (let i = 0; i <= GRID_N; i++) {
      const lon = EXTENT.lonMin + (i / GRID_N) * (EXTENT.lonMax - EXTENT.lonMin);
      let su = 0, sv = 0, sw = 0;
      for (const s of STATIONS) {
        const dLon = lon - s.lon, dLat = lat - s.lat;
        const d2 = dLon * dLon + dLat * dLat + 0.06; // epsilon tranh chia 0
        const w = 1 / (d2 * d2);
        su += s.u * w; sv += s.v * w; sw += w;
      }
      row.push([su / sw, sv / sw]);
    }
    windGrid.push(row);
  }
}
function sampleWind(lon, lat) {
  const fi = (lon - EXTENT.lonMin) / (EXTENT.lonMax - EXTENT.lonMin) * GRID_N;
  const fj = (EXTENT.latMax - lat) / (EXTENT.latMax - EXTENT.latMin) * GRID_N;
  const i0 = Math.max(0, Math.min(GRID_N - 1, Math.floor(fi)));
  const j0 = Math.max(0, Math.min(GRID_N - 1, Math.floor(fj)));
  const tx = fi - i0, ty = fj - j0;
  const a = windGrid[j0][i0], b = windGrid[j0][i0 + 1], c = windGrid[j0 + 1][i0], d = windGrid[j0 + 1][i0 + 1];
  const u = a[0] * (1 - tx) * (1 - ty) + b[0] * tx * (1 - ty) + c[0] * (1 - tx) * ty + d[0] * tx * ty;
  const v = a[1] * (1 - tx) * (1 - ty) + b[1] * tx * (1 - ty) + c[1] * (1 - tx) * ty + d[1] * tx * ty;
  return [u, v];
}

function speedColor(sp) {
  const stops = [[0, [59,130,246]], [5, [34,197,94]], [12, [234,179,8]], [25, [249,115,22]], [40, [239,68,68]]];
  for (let k = 1; k < stops.length; k++) {
    if (sp <= stops[k][0] || k === stops.length - 1) {
      const [s0, c0] = stops[k - 1], [s1, c1] = stops[k];
      const t = Math.max(0, Math.min(1, (sp - s0) / (s1 - s0)));
      const c = c0.map((v, idx) => Math.round(v + (c1[idx] - v) * t));
      return `rgb(${c[0]},${c[1]},${c[2]})`;
    }
  }
  return 'rgb(239,68,68)';
}

// --- particles: wind streaks (Derived motion from real vector field) ---
let particles = [];
function spawnParticle() {
  return {
    lon: EXTENT.lonMin + Math.random() * (EXTENT.lonMax - EXTENT.lonMin),
    lat: EXTENT.latMin + Math.random() * (EXTENT.latMax - EXTENT.latMin),
    life: 40 + Math.random() * 60, trail: [],
  };
}
function initParticles() { particles = Array.from({ length: 220 }, spawnParticle); }

// --- rain near high-precip stations (Real: precip_mm > 5) ---
const rainStations = STATIONS.filter(s => s.precip > 5);
let raindrops = [];
function spawnDrop(st) {
  const [x, y] = project(st.lon, st.lat, W, H);
  const x0 = x + (Math.random() - 0.5) * 70, y0 = y + (Math.random() - 0.5) * 40 - 30;
  // Rơi cục bộ quanh trạm (~90px), KHÔNG rơi hết chiều cao canvas -- nếu không hạt mưa trôi
  // ngang qua nhiều nước khác trước khi respawn, trông như mưa lan khắp bản đồ thay vì tại trạm.
  return { x: x0, y: y0, baseY: y0, st, speed: 2.2 + Math.random() * 2 };
}
function initRain() {
  raindrops = [];
  for (const st of rainStations) {
    const n = Math.max(6, Math.min(40, Math.round(st.precip / 6)));
    for (let k = 0; k < n; k++) raindrops.push(spawnDrop(st));
  }
}

function drawClouds() {
  const ctx = cloudCv.getContext('2d');
  ctx.clearRect(0, 0, W, H);
  for (const s of STATIONS) {
    if (!s.rh) continue;
    const [x, y] = project(s.lon, s.lat, W, H);
    const r = 24 + (s.rh / 100) * 130;
    const alpha = Math.max(0, (s.rh - 55) / 100) * 0.4;
    if (alpha <= 0) continue;
    const g = ctx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, `rgba(210,220,235,${alpha})`);
    g.addColorStop(1, 'rgba(210,220,235,0)');
    ctx.fillStyle = g;
    ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
  }
}

function drawStations() {
  const ctx = fxCv.getContext('2d');
  for (const s of STATIONS) {
    const [x, y] = project(s.lon, s.lat, W, H);
    ctx.beginPath();
    ctx.fillStyle = speedColor(s.speed);
    ctx.arc(x, y, 3.2, 0, Math.PI * 2); ctx.fill();
    ctx.lineWidth = 1; ctx.strokeStyle = 'rgba(255,255,255,0.55)'; ctx.stroke();
  }
}

let running = true;
function step() {
  if (running) {
    const windCtx = windCv.getContext('2d');
    // Lam mo dan net cu bang cach giam alpha (destination-in), KHONG ve phu mau dac len
    // -- giu canvas trong suot de thay ban do nen phia duoi, chi net gio moi ve la hien ro.
    windCtx.globalCompositeOperation = 'destination-in';
    windCtx.fillStyle = 'rgba(0,0,0,0.90)';
    windCtx.fillRect(0, 0, W, H);
    windCtx.globalCompositeOperation = 'source-over';

    const lonSpan = EXTENT.lonMax - EXTENT.lonMin, latSpan = EXTENT.latMax - EXTENT.latMin;
    for (const p of particles) {
      const [u, v] = sampleWind(p.lon, p.lat);
      const speed = Math.hypot(u, v);
      // He so nhan toc do rat lon (nen thoi gian): day la hieu ung THI GIAC de thay huong/toc
      // do gio tuong doi giua cac vung, KHONG phai chuyen dong theo thoi gian thuc (Schematic).
      const dt = 0.016;
      p.lon += (u / 111.0) * dt * 90;
      p.lat += (v / 111.0) * dt * 90;
      p.life -= 1;
      p.trail.push(project(p.lon, p.lat, W, H));
      if (p.trail.length > 9) p.trail.shift();

      if (p.life <= 0 || p.lon < EXTENT.lonMin || p.lon > EXTENT.lonMax || p.lat < EXTENT.latMin || p.lat > EXTENT.latMax) {
        Object.assign(p, spawnParticle());
        continue;
      }
      if (p.trail.length > 1) {
        windCtx.strokeStyle = speedColor(speed);
        windCtx.globalAlpha = 0.85;
        windCtx.lineWidth = 1.4;
        windCtx.beginPath();
        windCtx.moveTo(p.trail[0][0], p.trail[0][1]);
        for (const pt of p.trail.slice(1)) windCtx.lineTo(pt[0], pt[1]);
        windCtx.stroke();
        windCtx.globalAlpha = 1;
      }
    }

    const fxCtx = fxCv.getContext('2d');
    fxCtx.clearRect(0, 0, W, H);
    fxCtx.strokeStyle = 'rgba(158,198,255,0.75)';
    fxCtx.lineWidth = 1.3;
    for (const d of raindrops) {
      fxCtx.beginPath();
      fxCtx.moveTo(d.x, d.y);
      fxCtx.lineTo(d.x - 2, d.y + 9);
      fxCtx.stroke();
      d.y += d.speed; d.x -= 0.3;
      if (d.y - d.baseY > 90) Object.assign(d, spawnDrop(d.st));
    }
    drawStations();
  }
  requestAnimationFrame(step);
}

function onMove(evt) {
  const rect = stage.getBoundingClientRect();
  const mx = evt.clientX - rect.left, my = evt.clientY - rect.top;
  let best = null, bestD = 16;
  for (const s of STATIONS) {
    const [x, y] = project(s.lon, s.lat, W, H);
    const d = Math.hypot(x - mx, y - my);
    if (d < bestD) { bestD = d; best = s; }
  }
  if (best) {
    tooltip.style.display = 'block';
    tooltip.style.left = Math.min(mx + 14, W - 180) + 'px';
    tooltip.style.top = Math.max(my - 10, 4) + 'px';
    tooltip.innerHTML = `<b>${best.id}</b> (${best.country})<br>`
      + `Gió: ${best.speed.toFixed(1)} m/s<br>`
      + `Mưa (ngày): ${best.precip.toFixed(1)} mm<br>`
      + `Độ ẩm TB: ${best.rh ? best.rh.toFixed(0) + '%' : 'n/a'}`;
  } else {
    tooltip.style.display = 'none';
  }
}

window.addEventListener('resize', () => { sizeCanvases(); });
stage.addEventListener('mousemove', onMove);
stage.addEventListener('mouseleave', () => tooltip.style.display = 'none');
document.getElementById('toggle').addEventListener('click', (e) => {
  running = !running;
  e.target.textContent = running ? 'Tạm dừng' : 'Chạy tiếp';
});

sizeCanvases();
buildWindGrid();
initParticles();
initRain();
drawClouds();
step();
</script>
"""


def build(out_path: str) -> None:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    stations_json = json.dumps(data["stations"], ensure_ascii=False)
    html = TEMPLATE.replace("__STATIONS_JSON__", stations_json)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {out_path} ({len(html)} chars, {len(data['stations'])} stations)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="viz/output/earth_wind_rain.html")
    args = ap.parse_args()
    build(args.out)
