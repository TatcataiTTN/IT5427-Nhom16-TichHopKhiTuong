"""
Exploratory Data Analysis (EDA) + Principal Component Analysis (PCA) that tren
warehouse/output/weatherobs.parquet — bo sung cho data_quality_report.py (von chi do missing/
outlier), o day do THEM: phan phoi (skew/kurtosis), tuong quan cheo bien (pairwise, KHONG fillna(0)
— bai hoc tu loi da sua o Muc 6.11 bao cao), va PCA that de tim cau truc an trong khong gian nhieu
chieu cua du lieu khi tuong.

Phuong phap:
  - EDA phan phoi: mean/std/skew/kurtosis tung bien x tung nguon, chi tinh tren gia tri khong null.
  - Tuong quan: Pearson pairwise-complete (pandas .corr() mac dinh), KHONG thay NaN=0 (loi da biet).
  - PCA: chuan hoa Z-score (StandardScaler) roi PCA, tren 2 tap bien "sach" nhat (OPEN_METEO 6 bien
    100% day du; ISD 5 bien ~99% day du, N lon). Huong gio (wind_dir_deg, dai luong goc/circular)
    duoc tach thanh sin/cos TRUOC khi dua vao PCA tuyen tinh — khong dua thang goc 0-360 vao (loi
    pho bien: PCA tuyen tinh hieu sai y nghia "360 gan 0" neu dung truc tiep goc do).

Chay:  python3 warehouse/eda_pca.py
Output: warehouse/output/eda_summary.json, warehouse/output/pca_summary.json
"""
import json
import os

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

OUT = os.path.join(os.path.dirname(__file__), "output")
WAREHOUSE = os.path.join(OUT, "weatherobs.parquet")
NUM_COLS = ["temp_c", "rh_pct", "dewpoint_c", "precip_mm", "wind_speed_ms", "wind_dir_deg",
            "pressure_surface_hpa", "pressure_msl_hpa", "solar_rad_wm2", "cloud_cover_pct"]


def eda_distribution(df: pd.DataFrame) -> dict:
    """Thong ke phan phoi (mean/std/skew/kurtosis) tung bien x tung nguon — bo sung cho
    missing/outlier da co o data_quality_report.py. Skew > 0: lech phai (duoi dai ben phai,
    dung voi mua/buc xa); kurtosis > 0: duoi day hon phan phoi chuan (nhieu gia tri cuc doan hon)."""
    out = {}
    for src, g in df.groupby("source", observed=True):
        out[src] = {}
        for col in NUM_COLS:
            s = g[col].dropna()
            if len(s) < 30:
                continue
            out[src][col] = {
                "n": int(len(s)), "mean": round(float(s.mean()), 3), "std": round(float(s.std()), 3),
                "skew": round(float(s.skew()), 3), "kurtosis": round(float(s.kurtosis()), 3),
                "p01": round(float(s.quantile(0.01)), 2), "p50": round(float(s.quantile(0.5)), 2),
                "p99": round(float(s.quantile(0.99)), 2),
            }
    return out


def correlation_matrix(df: pd.DataFrame, source: str, cols: list) -> pd.DataFrame:
    """Tuong quan Pearson pairwise-complete (moi cap bien dung rieng cac dong ca hai cung co gia
    tri) — KHONG dien NaN=0 truoc khi tinh (loi da phat hien va sua o Muc 6.11 bao cao: dien 0 tao
    tuong quan gia vi cac nguon thieu bien khac nhau)."""
    sub = df[df["source"] == source][cols]
    return sub.corr(method="pearson", min_periods=100)


def run_pca(df: pd.DataFrame, source: str, linear_cols: list, circular_col: str = None,
            n_components: int = None, sample_n: int = 200_000, seed: int = 0) -> dict:
    """PCA tren 1 nguon, sau khi chuan hoa Z-score. circular_col (vd wind_dir_deg) duoc tach
    sin/cos truoc khi dua vao thay vi dung goc do truc tiep. Lay mau sample_n dong (neu nguon lon
    hon) de PCA chay nhanh tren may don, co co dinh seed de tai lap duoc."""
    sub = df[df["source"] == source].copy()
    cols = list(linear_cols)
    if circular_col:
        rad = np.deg2rad(sub[circular_col])
        sub[f"{circular_col}_sin"] = np.sin(rad)
        sub[f"{circular_col}_cos"] = np.cos(rad)
        cols = [c for c in cols if c != circular_col] + [f"{circular_col}_sin", f"{circular_col}_cos"]
    sub = sub.dropna(subset=cols)
    n_total = len(sub)
    if n_total > sample_n:
        sub = sub.sample(sample_n, random_state=seed)
    X = sub[cols].values
    Xz = StandardScaler().fit_transform(X)
    k = n_components or len(cols)
    pca = PCA(n_components=k, random_state=seed)
    pca.fit(Xz)
    loadings = pd.DataFrame(pca.components_.T, index=cols,
                            columns=[f"PC{i+1}" for i in range(k)])
    return {
        "nguon": source, "bien_dau_vao": cols, "n_dong_dung_PCA": int(len(sub)),
        "n_dong_tong_cua_nguon": int(n_total),
        "ty_le_phuong_sai_giai_thich": [round(float(v), 4) for v in pca.explained_variance_ratio_],
        "ty_le_luy_ke": [round(float(v), 4) for v in np.cumsum(pca.explained_variance_ratio_)],
        "he_so_tai_PC1_PC2": loadings.iloc[:, :2].round(3).to_dict(),
    }


def main():
    print("== Doc warehouse ==")
    df = pd.read_parquet(WAREHOUSE)
    print(f"  {len(df):,} dong, {df['source'].nunique()} nguon")

    print("\n== 1/3: EDA phan phoi (skew/kurtosis) theo bien x nguon ==")
    eda = eda_distribution(df)
    for src in eda:
        print(f"  {src}: {len(eda[src])} bien co du lieu")

    print("\n== 2/3: Ma tran tuong quan (pairwise-complete, khong fillna0) ==")
    corr_open = correlation_matrix(df, "OPEN_METEO",
                                   ["temp_c", "rh_pct", "precip_mm", "wind_speed_ms", "pressure_msl_hpa"])
    corr_isd = correlation_matrix(df, "ISD", ["temp_c", "rh_pct", "dewpoint_c", "wind_speed_ms"])
    print("  OPEN_METEO:\n" + corr_open.round(2).to_string().replace("\n", "\n  "))
    print("  ISD:\n" + corr_isd.round(2).to_string().replace("\n", "\n  "))

    print("\n== 3/3: PCA (chuan hoa Z-score, huong gio tach sin/cos) ==")
    pca_open = run_pca(df, "OPEN_METEO",
                       linear_cols=["temp_c", "rh_pct", "precip_mm", "wind_speed_ms", "pressure_msl_hpa"],
                       circular_col="wind_dir_deg")
    print(f"  OPEN_METEO ({pca_open['n_dong_dung_PCA']:,}/{pca_open['n_dong_tong_cua_nguon']:,} dong): "
         f"PC1+PC2 giai thich {pca_open['ty_le_luy_ke'][1]:.1%} phuong sai")
    pca_isd = run_pca(df, "ISD", linear_cols=["temp_c", "rh_pct", "dewpoint_c", "wind_speed_ms"],
                      circular_col="wind_dir_deg")
    print(f"  ISD ({pca_isd['n_dong_dung_PCA']:,}/{pca_isd['n_dong_tong_cua_nguon']:,} dong): "
         f"PC1+PC2 giai thich {pca_isd['ty_le_luy_ke'][1]:.1%} phuong sai")

    with open(os.path.join(OUT, "eda_summary.json"), "w", encoding="utf-8") as f:
        json.dump(eda, f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUT, "pca_summary.json"), "w", encoding="utf-8") as f:
        json.dump({
            "correlation_open_meteo": corr_open.round(4).to_dict(),
            "correlation_isd": corr_isd.round(4).to_dict(),
            "pca_open_meteo": pca_open,
            "pca_isd": pca_isd,
        }, f, ensure_ascii=False, indent=2)
    print("\nDa ghi warehouse/output/eda_summary.json va pca_summary.json")


if __name__ == "__main__":
    main()
