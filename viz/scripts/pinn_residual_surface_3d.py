"""
Trực quan hoá 3D (visualization-3d skill): bề mặt sai số PINN residual_ms = |pred - obs|
theo (lat, lon), cộng điểm trạm thật và vector gió dự đoán vs quan trắc.

Nguồn dữ liệu: warehouse/output/pinn_wind_field_output.parquet (113 trạm thật, không mock).
Nhãn theo quy tắc skill visualization-3d / visualization-earth:
  - Real: toạ độ trạm (lat, lon), u_obs/v_obs (quan trắc thật), residual_ms tại từng trạm.
  - Derived: mặt residual nội suy (scipy griddata, cubic) giữa các trạm -- KHÔNG đo trực tiếp,
    chỉ để nhìn xu hướng không gian. Vùng ngoài lưới lồi (convex hull) của trạm bị NaN, không vẽ.

Câu hỏi hình phải trả lời: "PINN dự đoán sai gió nhiều nhất ở vùng nào, và lệch bao nhiêu so
với các trạm lân cận có sai số thấp?"

Chạy: python3 viz/scripts/pinn_residual_surface_3d.py --out viz/output/pinn_residual_surface.html
"""
import argparse
import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.interpolate import griddata

PARQUET = os.path.join(os.path.dirname(__file__), "..", "..", "warehouse", "output", "pinn_wind_field_output.parquet")


def build(out_path: str) -> None:
    df = pd.read_parquet(PARQUET)

    grid_n = 120
    loni = np.linspace(df.lon.min(), df.lon.max(), grid_n)
    lati = np.linspace(df.lat.min(), df.lat.max(), grid_n)
    LONI, LATI = np.meshgrid(loni, lati)
    # method="linear" (khong "cubic"): cubic spline overshoot am voi tram thua/khong deu,
    # tao residual < 0 vo nghia vat ly (residual = |pred - obs| >= 0 theo dinh nghia).
    RESI = griddata(
        (df.lon.values, df.lat.values), df.residual_ms.values,
        (LONI, LATI), method="linear",
    )
    RESI = np.clip(RESI, 0, None)

    fig = go.Figure()

    fig.add_trace(go.Surface(
        x=loni, y=lati, z=RESI,
        colorscale="Inferno", opacity=0.82, showscale=True,
        colorbar=dict(title="Residual (m/s)", x=1.08, len=0.75, y=0.4),
        name="Mặt residual nội suy (Derived)",
        hoverinfo="skip",
    ))

    fig.add_trace(go.Scatter3d(
        x=df.lon, y=df.lat, z=df.residual_ms,
        mode="markers",
        marker=dict(
            size=5, color=df.residual_ms, colorscale="Inferno",
            line=dict(color="white", width=1),
        ),
        text=[
            f"{r.location_id}<br>residual = {r.residual_ms:.3f} m/s"
            f"<br>pred (u,v) = ({r.u_pred_ms:.2f}, {r.v_pred_ms:.2f}) m/s"
            f"<br>obs  (u,v) = ({r.u_obs_ms:.2f}, {r.v_obs_ms:.2f}) m/s"
            for r in df.itertuples()
        ],
        hovertemplate="%{text}<extra></extra>",
        name="113 trạm thật (Real)",
    ))

    worst = df.nlargest(5, "residual_ms")

    fig.update_layout(
        title=(
            "Sai số trường gió PINN (|dự đoán - quan trắc|) theo không gian -- "
            f"113 trạm thật, residual trung bình {df.residual_ms.mean():.3f} m/s, "
            f"tệ nhất {df.residual_ms.max():.3f} m/s tại {worst.iloc[0]['location_id']}"
        ),
        scene=dict(
            xaxis_title="Kinh độ (°E)",
            yaxis_title="Vĩ độ (°N)",
            zaxis_title="Residual |pred - obs| (m/s)",
            aspectmode="manual", aspectratio=dict(x=1.3, y=1.3, z=0.7),
        ),
        template="plotly_dark",
        height=800,
        margin=dict(l=0, r=0, t=60, b=60),
        annotations=[],
    )
    fig.add_annotation(
        text="Real: toạ độ trạm + residual tại trạm (113 trạm)  |  Derived: mặt nội suy tuyến tính giữa các trạm (scipy griddata, clip ≥ 0)",
        xref="paper", yref="paper", x=0.5, y=-0.08, showarrow=False,
        font=dict(size=12, color="#aaaaaa"),
    )

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.write_html(out_path, include_plotlyjs=True, full_html=True)
    print(f"Wrote {out_path} ({os.path.getsize(out_path) / 1024:.0f} KB)")
    print(f"residual: mean={df.residual_ms.mean():.3f} max={df.residual_ms.max():.3f} "
          f"at {worst.iloc[0]['location_id']} ({worst.iloc[0]['lat']:.3f},{worst.iloc[0]['lon']:.3f})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="viz/output/pinn_residual_surface.html")
    args = ap.parse_args()
    build(args.out)
