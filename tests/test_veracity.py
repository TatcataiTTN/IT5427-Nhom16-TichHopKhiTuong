import numpy as np
import pandas as pd

from ingestion.veracity import detect_outliers, detect_outliers_iqr, detect_outliers_zscore


def test_zscore_flags_moderate_outlier():
    data = pd.Series([10, 11, 9, 10, 10, 11, 9, 10, 50])  # 50 la outlier ro rang trong day nho
    flags = detect_outliers_zscore(data, threshold=2.0)
    assert flags.iloc[-1] == True  # noqa: E712


def test_iqr_flags_moderate_outlier():
    data = pd.Series([10, 11, 9, 10, 10, 11, 9, 10, 50])
    flags = detect_outliers_iqr(data)
    assert flags.iloc[-1] == True  # noqa: E712


def test_iqr_robust_to_extreme_outliers_zscore_is_not():
    """Tai lap hien tuong masking that: outlier CUC DOAN lam Z-score mat tac dung (std bi keo
    gian), trong khi IQR (dua tren tu phan vi) van phat hien dung. Day la phat hien that, khong
    phai bug - xem ingestion/veracity.py __main__ de biet chi tiet dien giai."""
    rng = np.random.RandomState(0)
    normal = rng.normal(loc=25.0, scale=2.0, size=200)
    extreme = np.array([80.0, -60.0, 95.0, -999.0, 70.0])
    data = pd.Series(np.concatenate([normal, extreme]))

    z_flags = detect_outliers_zscore(data, threshold=3.0)
    iqr_flags = detect_outliers_iqr(data)

    iqr_detected = iqr_flags.tail(len(extreme)).sum()
    z_detected = z_flags.tail(len(extreme)).sum()

    assert iqr_detected == len(extreme), "IQR phai phat hien du 5/5 outlier cuc doan"
    assert z_detected < len(extreme), "Z-score phai bi masking effect (phat hien it hon IQR) trong tinh huong nay"


def test_detect_outliers_no_false_positive_on_clean_normal_data():
    rng = np.random.RandomState(1)
    clean = pd.Series(rng.normal(loc=25.0, scale=2.0, size=500))
    df = pd.DataFrame({"temp_c": clean})
    result = detect_outliers(df, "temp_c")
    # Du lieu sach (khong tiem outlier): ty le flag phai thap (duoi 2%, cho phep vai false positive tu nhien)
    assert result["temp_c_outlier_both"].mean() < 0.02
