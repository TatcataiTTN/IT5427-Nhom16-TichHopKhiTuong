"""
Veracity: phat hien outlier bang Z-score va IQR (docs/03 Tuan 3, TV1 #2).

2 phuong phap doc lap, dung song song (khop ca 2 = tin cay cao hon):
  - Z-score: |x - mean| / std > threshold (mac dinh 3 - chuan thong ke pho bien)
  - IQR (Tukey's fences): x < Q1 - k*IQR hoac x > Q3 + k*IQR (mac dinh k=1.5)

Ca 2 deu nhay voi outlier CUC DOAN (du lieu loi cam bien, sai don vi...), khong dung de loai bo
bien doi khi hau that su (vd 1 ngay mua cuc lon) - chi GAN CO (flag), khong tu dong xoa.
"""
import numpy as np
import pandas as pd


def detect_outliers_zscore(series: pd.Series, threshold: float = 3.0) -> pd.Series:
    s = series.dropna()
    if len(s) < 2 or s.std() == 0:
        return pd.Series(False, index=series.index)
    z = (series - s.mean()) / s.std()
    return z.abs() > threshold


def detect_outliers_iqr(series: pd.Series, k: float = 1.5) -> pd.Series:
    s = series.dropna()
    if len(s) < 4:
        return pd.Series(False, index=series.index)
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return pd.Series(False, index=series.index)
    lower, upper = q1 - k * iqr, q3 + k * iqr
    return (series < lower) | (series > upper)


def detect_outliers(df: pd.DataFrame, column: str, zscore_threshold: float = 3.0, iqr_k: float = 1.5) -> pd.DataFrame:
    """Tra ve df goc + 3 cot moi: {column}_outlier_zscore, {column}_outlier_iqr,
    {column}_outlier_both (gan co khi CA HAI phuong phap deu dong y - tin cay cao nhat)."""
    out = df.copy()
    z_flag = detect_outliers_zscore(df[column], zscore_threshold)
    iqr_flag = detect_outliers_iqr(df[column], iqr_k)
    out[f"{column}_outlier_zscore"] = z_flag.fillna(False)
    out[f"{column}_outlier_iqr"] = iqr_flag.fillna(False)
    out[f"{column}_outlier_both"] = out[f"{column}_outlier_zscore"] & out[f"{column}_outlier_iqr"]
    return out


if __name__ == "__main__":
    rng = np.random.RandomState(0)
    normal = rng.normal(loc=25.0, scale=2.0, size=200)  # nhiet do gia lap ~N(25,2)
    injected_outliers = np.array([80.0, -60.0, 95.0, -999.0, 70.0])  # loi cam bien ro rang
    data = pd.Series(np.concatenate([normal, injected_outliers]))
    df = pd.DataFrame({"temp_c": data})

    result = detect_outliers(df, "temp_c")
    n_injected = len(injected_outliers)
    tail = result.tail(n_injected)
    z_detected = tail["temp_c_outlier_zscore"].sum()
    iqr_detected = tail["temp_c_outlier_iqr"].sum()
    both_detected = tail["temp_c_outlier_both"].sum()

    fp_z = result.head(len(normal))["temp_c_outlier_zscore"].sum()
    fp_iqr = result.head(len(normal))["temp_c_outlier_iqr"].sum()

    print(f"So outlier da tiem: {n_injected} (gia tri: {injected_outliers.tolist()})")
    print(f"Du lieu sau khi tiem outlier: mean={data.mean():.2f}, std={data.std():.2f} "
          f"(std truoc khi tiem ~2.0 -> bi outlier keo gian manh)")
    print(f"\nZ-score (threshold=3): phat hien {z_detected}/{n_injected} "
          f"({z_detected/n_injected:.0%}), false positive {fp_z}/{len(normal)}")
    print(f"IQR (k=1.5):            phat hien {iqr_detected}/{n_injected} "
          f"({iqr_detected/n_injected:.0%}), false positive {fp_iqr}/{len(normal)}")
    print(f"Ca 2 phuong phap dong y: {both_detected}/{n_injected} ({both_detected/n_injected:.0%})")

    iqr_rate = iqr_detected / n_injected
    if z_detected < n_injected:
        print(f"\nPhat hien that (khong phai loi code): Z-score bi 'masking effect' - cac outlier cuc "
              f"doan (-999, 95, 80...) tu lam std phinh to (2.0 -> {data.std():.1f}), khien nguong "
              f"3*std qua rong de bat chinh cac outlier do gay ra. Day la nhuoc diem thong ke da biet "
              f"cua Z-score (khong 'robust'). IQR dung tu phan vi (khong bi keo gian boi outlier cuc "
              f"doan) nen phat hien dung {iqr_detected}/{n_injected}. Khuyen nghi: dung IQR lam phuong "
              f"phap chinh, Z-score lam tham khao bo sung - khong dung dieu kien 'ca 2 dong y' lam "
              f"tieu chi duy nhat vi se bo sot outlier cuc doan nhu vi du nay.")

    assert iqr_rate >= 0.9, f"IQR (phuong phap robust) phat hien {iqr_rate:.0%} duoi nguong 90% yeu cau"
    print("\nPASS (tieu chi: IQR phat hien >=90% outlier da tiem)")
