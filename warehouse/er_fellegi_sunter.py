"""
Entity Resolution GHCN <-> ISD theo mo hinh xac suat Fellegi-Sunter (1969), co luat phu quyet
(cannot-link) ap dung TRUOC khi cham diem. Chay tren dung khong gian ung vien ma
warehouse/entity_resolution.py dang dung: moi cap (tram GHCN, tram ISD) trong location.parquet.

  1. Dac trung so sanh (roi rac hoa thanh muc): khoang cach Haversine, chenh do cao, do giong ten
     tram (difflib tren ten da chuan hoa tu reference/*.csv). KHONG dung so WMO lam dac trung vi so
     WMO duoc dung lam nhan danh gia (dung lai se la ro ri nhan).
  2. Uoc luong m/u bang EM khong giam sat (gia dinh doc lap co dieu kien giua cac dac trung),
     khong dung nhan.
  3. Trong so w = sum log2(m/u); nguong theta_h / theta_l chon theo dung dinh nghia Fellegi-Sunter:
     ti le ghep nham mu = P(gan "khop" | khong khop) <= MU, ti le bo sot lambda = P(gan "khong khop"
     | khop) <= LAMBDA, tinh tu chinh m/u da uoc luong.
  4. Danh gia tren 2 tap nhan WMO doc lap voi toa do:
       L15  -- dung quy uoc cua er_precision_recall.py (5 so cuoi ma GHCN = 5 so dau USAF ket thuc 0);
       Lmeta -- so WMO trong truong metadata WMO_ID cua danh ba GHCN (reference/*.csv), cho ca cac tram
                ma GHCN khong ma hoa WMO trong ma tram (vd VMW00041010 -> WMO 48877).

Chay: python3 warehouse/er_fellegi_sunter.py
Output: warehouse/output/er_fellegi_sunter_pairs.parquet, er_fellegi_sunter_summary.json
"""
import difflib
import json
import os
import re
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from warehouse.entity_resolution import resolve_entities

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(os.path.dirname(__file__), "output")
LOC = os.path.join(OUT, "location.parquet")

DIST_BANDS = [0, 1, 5, 25, 100, np.inf]          # km
ELEV_BANDS = [0, 5, 30, 100, np.inf]             # m, chenh lech tuyet doi
NAME_BANDS = [0, 0.4, 0.6, 0.85, 1.0001]         # ti so difflib
MU, LAMBDA = 0.0005, 0.01                         # muc loi muc tieu cua Fellegi-Sunter
VETO_DIST_KM = 10.0
VETO_ELEV_M = 100.0

STOP = re.compile(r"\b(INTL|INTERNATIONAL|ARPT|AIRPORT|AP|AERO|AB|AWOS|WMO)\b")


def norm_name(s: str) -> str:
    s = re.sub(r"[^A-Z ]", " ", str(s).upper())
    return re.sub(r"\s+", " ", STOP.sub(" ", s)).strip()


def name_sim(a: str, b: str) -> float:
    a, b = norm_name(a), norm_name(b)
    if not a or not b:
        return 0.0
    # ten ISD hay ghep nhieu ten bang "/" (vd "CAT BI INTL ARPT/HAI PHONG"): lay muc giong cao nhat
    whole = difflib.SequenceMatcher(None, a, b).ratio()
    tok_a, tok_b = set(a.split()), set(b.split())
    jacc = len(tok_a & tok_b) / len(tok_a | tok_b)
    return max(whole, jacc)


def haversine_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371.0088 * np.arcsin(np.sqrt(a))


def load_stations():
    loc = pd.read_parquet(LOC)
    st = loc[loc["type"] == "station"]
    ghcn = st[st["location_id"].str.match(r"^[A-Za-z]")].copy()
    isd = st[~st["location_id"].str.match(r"^[A-Za-z]")].copy()
    rg = pd.concat([pd.read_csv(os.path.join(ROOT, "reference/ghcn_stations_sea_priority.csv")),
                    pd.read_csv(os.path.join(ROOT, "reference/ghcn_stations_vietnam_full.csv"))])
    ri = pd.concat([pd.read_csv(os.path.join(ROOT, "reference/isd_stations_sea_priority.csv")),
                    pd.read_csv(os.path.join(ROOT, "reference/isd_stations_vietnam_active.csv"))])
    ri["location_id"] = ri["USAF"].astype(str).str.zfill(6) + ri["WBAN"].astype(str).str.zfill(5)
    ghcn = ghcn.merge(rg[["ID", "NAME", "has_wmo", "WMO_ID"]].drop_duplicates("ID"),
                      left_on="location_id", right_on="ID", how="left")
    isd = isd.merge(ri[["location_id", "STATION NAME"]].drop_duplicates("location_id"),
                    on="location_id", how="left").rename(columns={"STATION NAME": "NAME"})
    ghcn["wmo_code5"] = ghcn["location_id"].str[-5:]
    ghcn["wmo_meta"] = ghcn["WMO_ID"].where(ghcn["has_wmo"].astype(bool)).astype("Int64").astype(str) \
        .replace("<NA>", np.nan)
    usaf = isd["location_id"].str[:6]
    isd["wmo"] = usaf.str[:5].where(usaf.str[-1] == "0")
    return ghcn, isd


def build_pairs(ghcn, isd):
    p = ghcn.add_suffix("_g").merge(isd.add_suffix("_i"), how="cross")
    p["dist_km"] = haversine_km(p["lat_g"], p["lon_g"], p["lat_i"], p["lon_i"])
    p["elev_diff_m"] = (p["elevation_m_g"] - p["elevation_m_i"]).abs()
    p["name_sim"] = [name_sim(a, b) for a, b in zip(p["NAME_g"], p["NAME_i"])]
    p["same_country"] = p["country_g"] == p["country_i"]
    p["g_dist"] = np.digitize(p["dist_km"], DIST_BANDS[1:-1])
    p["g_elev"] = np.digitize(p["elev_diff_m"].fillna(1e9), ELEV_BANDS[1:-1])
    p["g_name"] = np.digitize(p["name_sim"], NAME_BANDS[1:-1])
    # Nhan: L15 (quy uoc ma tram) va Lmeta (truong WMO_ID cua danh ba GHCN); NaN = khong gan nhan duoc
    p["label_l15"] = np.where(p["wmo_i"].notna(), p["wmo_code5_g"] == p["wmo_i"], np.nan)
    p["label_meta"] = np.where(p["wmo_i"].notna() & p["wmo_meta_g"].notna(),
                               p["wmo_meta_g"] == p["wmo_i"], np.nan)
    return p


FEATS = [("g_dist", len(DIST_BANDS) - 1), ("g_elev", len(ELEV_BANDS) - 1), ("g_name", len(NAME_BANDS) - 1)]


ALPHA = 0.5   # gia dem Jeffreys moi muc, tranh u = 0 tuyet doi (trong so vo han) khi lop M rat nho


def em_fellegi_sunter(p, n_iter=500, tol=1e-10):
    """EM cho mo hinh hon hop 2 lop (khop M / khong khop U), dac trung roi rac doc lap co dieu kien."""
    X = p[[f for f, _ in FEATS]].to_numpy()
    prior = 0.01
    # khoi tao: M nghieng ve muc 'gan/giong' (muc 0 cua khoang cach, chenh do cao; muc cao nhat cua ten)
    m, u = [], []
    for (f, k), col in zip(FEATS, X.T):
        mm = np.full(k, 0.1 / (k - 1))
        mm[k - 1 if f == "g_name" else 0] = 0.9
        m.append(mm)
        u.append(np.bincount(col, minlength=k) / len(col) + 1e-9)
    ll_old = -np.inf
    for it in range(n_iter):
        pm = prior * np.prod([m[j][X[:, j]] for j in range(len(FEATS))], axis=0)
        pu = (1 - prior) * np.prod([u[j][X[:, j]] for j in range(len(FEATS))], axis=0)
        g = pm / (pm + pu)
        ll = np.log(pm + pu).sum()
        prior = g.mean()
        for j, (_, k) in enumerate(FEATS):
            m[j] = (np.bincount(X[:, j], weights=g, minlength=k) + ALPHA) / (g.sum() + ALPHA * k)
            u[j] = (np.bincount(X[:, j], weights=1 - g, minlength=k) + ALPHA) / ((1 - g).sum() + ALPHA * k)
        if abs(ll - ll_old) < tol:
            break
        ll_old = ll
    return prior, m, u, g, it + 1


def fs_thresholds(m, u):
    """theta_h/theta_l theo Fellegi-Sunter tren khong gian mau (pattern) day du."""
    ks = [k for _, k in FEATS]
    grids = np.array(np.meshgrid(*[np.arange(k) for k in ks], indexing="ij")).reshape(len(ks), -1).T
    mp = np.prod([m[j][grids[:, j]] for j in range(len(ks))], axis=0)
    up = np.prod([u[j][grids[:, j]] for j in range(len(ks))], axis=0)
    w = np.log2(mp / up)
    order = np.argsort(-w)
    w_s, m_s, u_s = w[order], mp[order], up[order]
    cum_u = np.cumsum(u_s)                     # ti le ghep nham neu gan "khop" cho moi mau tu tren xuong
    hi = np.searchsorted(cum_u, MU, side="right")   # so mau dau tien co tong u <= MU
    theta_h = w_s[hi - 1] if hi > 0 else np.inf
    cum_m_rev = np.cumsum(m_s[::-1])           # ti le bo sot neu gan "khong khop" tu duoi len
    lo = np.searchsorted(cum_m_rev, LAMBDA, side="right")
    theta_l = w_s[::-1][lo - 1] if lo > 0 else -np.inf
    return float(theta_h), float(theta_l)


def one_to_one(df, score_col):
    """Gan 1-1 tham lam theo diem giam dan, hoa thi uu tien cap gan hon (rang buoc 1-1 nhu
    entity_resolution.py, nhung khong phu thuoc thu tu duyet tram)."""
    used_g, used_i, keep = set(), set(), []
    for idx, r in df.sort_values([score_col, "dist_km"], ascending=[False, True]).iterrows():
        if r["location_id_g"] in used_g or r["location_id_i"] in used_i:
            continue
        used_g.add(r["location_id_g"]); used_i.add(r["location_id_i"]); keep.append(idx)
    return df.loc[keep]


def evaluate(pred_pairs: set, p: pd.DataFrame, label_col: str) -> dict:
    lab = p[p[label_col].notna()]
    pos = set(zip(lab.loc[lab[label_col] == 1, "location_id_g"], lab.loc[lab[label_col] == 1, "location_id_i"]))
    neg = set(zip(lab.loc[lab[label_col] == 0, "location_id_g"], lab.loc[lab[label_col] == 0, "location_id_i"]))
    tp, fp, fn = len(pred_pairs & pos), len(pred_pairs & neg), len(pos - pred_pairs)
    prec = tp / (tp + fp) if tp + fp else float("nan")
    rec = tp / (tp + fn) if tp + fn else float("nan")
    return {"tp": tp, "fp": fp, "fn": fn, "n_pos": len(pos), "n_labelled_pairs": len(pos) + len(neg),
            "precision": round(prec, 4), "recall": round(rec, 4),
            "unlabelled_predictions": len(pred_pairs - pos - neg)}


def main():
    ghcn, isd = load_stations()
    p = build_pairs(ghcn, isd)
    print(f"Ung vien: {len(ghcn)} GHCN x {len(isd)} ISD = {len(p):,} cap")

    # ---- Luat phu quyet (cannot-link), danh gia rieng tung luat va luy ke ----
    pos_meta = p["label_meta"] == 1
    pos_any = pos_meta | (p["label_l15"] == 1)
    rules = {
        "khac_quoc_gia": ~p["same_country"],
        f"khoang_cach_gt_{VETO_DIST_KM:g}km": p["dist_km"] > VETO_DIST_KM,
        f"chenh_do_cao_gt_{VETO_ELEV_M:g}m": p["elev_diff_m"] > VETO_ELEV_M,
    }
    veto = pd.Series(False, index=p.index)
    veto_stats = {}
    for name, r in rules.items():
        new = r & ~veto
        veto_stats[name] = {"loai_rieng": int(r.sum()), "loai_them_khi_ap_tuan_tu": int(new.sum()),
                            "cap_khop_that_bi_loai": int((r & pos_any).sum())}
        veto |= r
    p["vetoed"] = veto
    print("Luat phu quyet:", json.dumps(veto_stats, ensure_ascii=False))
    print(f"  Con lai sau phu quyet: {int((~veto).sum())} cap")

    # Can cu chon nguong: phan bo khoang cach / chenh do cao cua cap khop that va cua lang gieng gan nhat
    dpos = p.loc[pos_any, ["dist_km", "elev_diff_m"]]
    nn_other = (p[~pos_any & p["same_country"]].groupby("location_id_i")["dist_km"].min())
    justification = {
        "cap_khop_that_dist_km_max": round(float(dpos["dist_km"].max()), 3),
        "cap_khop_that_elev_diff_m_max": round(float(dpos["elev_diff_m"].max()), 1),
        "lang_gieng_gan_nhat_khong_phai_cap_that_dist_km": {
            "min": round(float(nn_other.min()), 2), "median": round(float(nn_other.median()), 2)},
        "so_tram_ISD_co_lang_gieng_khac_trong_10km": int((nn_other <= VETO_DIST_KM).sum()),
    }
    print("Can cu nguong:", justification)

    # ---- EM tren toan bo cap ung vien (khong dung nhan) ----
    prior, m, u, gpost, n_it = em_fellegi_sunter(p)
    print(f"EM hoi tu sau {n_it} vong, ti le khop tien nghiem p = {prior:.5f} (~{prior * len(p):.1f} cap)")
    W = np.zeros(len(p))
    for j, (f, _) in enumerate(FEATS):
        W += np.log2(m[j][p[f].to_numpy()] / u[j][p[f].to_numpy()])
    p["weight"] = W
    p["posterior"] = gpost
    th_h, th_l = fs_thresholds(m, u)
    print(f"theta_h = {th_h:.2f}, theta_l = {th_l:.2f} (MU={MU}, LAMBDA={LAMBDA})")
    p["fs_class"] = np.select([p["vetoed"], p["weight"] >= th_h, p["weight"] > th_l],
                              ["khong_khop_phu_quyet", "khop", "can_xem_xet"], "khong_khop")
    cls = p["fs_class"].value_counts().to_dict()
    print("Phan lop:", cls)

    # ---- So sanh 3 cach tren cung tap nhan ----
    rule = resolve_entities(pd.read_parquet(LOC))
    rule_set = set(zip(rule["ghcn_id"], rule["isd_id"]))
    fs_match = one_to_one(p[p["fs_class"] == "khop"], "weight")
    fs_match_set = set(zip(fs_match["location_id_g"], fs_match["location_id_i"]))
    fs_review = p[p["fs_class"] == "can_xem_xet"]
    fs_plus = one_to_one(p[p["fs_class"].isin(["khop", "can_xem_xet"])], "weight")
    fs_plus_set = set(zip(fs_plus["location_id_g"], fs_plus["location_id_i"]))
    nov = one_to_one(p[(p["weight"] >= th_h)], "weight")  # FS khong co luat phu quyet
    nov_set = set(zip(nov["location_id_g"], nov["location_id_i"]))
    m2o = p[p["fs_class"] == "khop"]
    m2o_set = set(zip(m2o["location_id_g"], m2o["location_id_i"]))
    methods = {"haversine_5km_1_1": rule_set, "fs_khop_1_1": fs_match_set,
               "fs_khop_nhieu_mot": m2o_set,
               "fs_khop_va_can_xem_xet_1_1": fs_plus_set, "fs_khong_phu_quyet_1_1": nov_set}
    # Tac dung thuc cua luat phu quyet: so cap ma neu KHONG co phu quyet se duoc FS xep "khop"/"can xem xet"
    cls_noveto = np.select([p["weight"] >= th_h, p["weight"] > th_l], ["khop", "can_xem_xet"], "khong_khop")
    veto_effect = {"khop_bi_chan": int(((cls_noveto == "khop") & p["vetoed"]).sum()),
                   "can_xem_xet_bi_chan": int(((cls_noveto == "can_xem_xet") & p["vetoed"]).sum())}
    print("Tac dung phu quyet:", veto_effect)
    # Nhieu-mot: tram ISD co >= 2 chuoi GHCN cung xep "khop" -> doc do phu thoi gian that tu kho
    multi = m2o.groupby("location_id_i").filter(lambda d: len(d) >= 2)
    daily = pd.read_parquet(os.path.join(OUT, "weather_daily.parquet"), columns=["location_id", "source", "date"],
                            filters=[("location_id", "in", sorted(set(multi["location_id_g"])))])
    daily = daily[daily["source"] == "GHCN"]
    yrs = pd.to_datetime(daily["date"]).dt.year.groupby(daily["location_id"]).agg(["min", "max"])
    multi = multi.merge(yrs, left_on="location_id_g", right_index=True, how="left")
    print("ISD co nhieu chuoi GHCN cung khop:\n", multi[["location_id_i", "NAME_i", "location_id_g", "NAME_g",
                                                          "dist_km", "weight", "label_meta", "min", "max"]]
          .round(3).to_string(index=False))
    comparison = {k: {"so_cap": len(v), "L15": evaluate(v, p, "label_l15"),
                      "Lmeta": evaluate(v, p, "label_meta")} for k, v in methods.items()}
    for k, v in comparison.items():
        print(k, v)
    review = fs_review.sort_values("weight", ascending=False)[
        ["location_id_g", "NAME_g", "location_id_i", "NAME_i", "dist_km", "elev_diff_m", "name_sim", "weight",
         "label_meta"]]
    print("Cap can xem xet thu cong:\n", review.round(3).to_string(index=False))
    diff = {"fs_them_so_voi_haversine": sorted(map(list, fs_match_set - rule_set)),
            "haversine_them_so_voi_fs": sorted(map(list, rule_set - fs_match_set))}
    print("Khac biet:", diff)

    params = {f: {"m": np.round(m[j], 4).tolist(), "u": np.round(u[j], 5).tolist(),
                  "w_log2": np.round(np.log2(m[j] / u[j]), 2).tolist()} for j, (f, _) in enumerate(FEATS)}
    summary = {
        "so_cap_ung_vien": int(len(p)), "so_ghcn": int(len(ghcn)), "so_isd": int(len(isd)),
        "bands": {"dist_km": DIST_BANDS[:-1], "elev_diff_m": ELEV_BANDS[:-1], "name_sim": NAME_BANDS[:-1]},
        "em": {"vong_lap": n_it, "p_khop": round(float(prior), 5), "tham_so": params},
        "theta_h": round(th_h, 2), "theta_l": round(th_l, 2), "MU": MU, "LAMBDA": LAMBDA,
        "phan_lop": {k: int(v) for k, v in cls.items()},
        "phu_quyet": veto_stats, "can_cu_nguong_phu_quyet": justification,
        "so_sanh": comparison, "cap_can_xem_xet": review.round(3).astype(str).to_dict("records"),
        "khac_biet": diff, "tac_dung_phu_quyet": veto_effect,
        "nhieu_mot": multi[["location_id_i", "NAME_i", "location_id_g", "NAME_g", "dist_km", "weight",
                            "label_meta", "min", "max"]].round(3).astype(str).to_dict("records"),
        "nhan": {"L15_so_cap_duong": int((p["label_l15"] == 1).sum()),
                 "Lmeta_so_cap_duong": int((p["label_meta"] == 1).sum()),
                 "Lmeta_so_cap_gan_nhan": int(p["label_meta"].notna().sum())},
    }
    keep_cols = ["location_id_g", "NAME_g", "location_id_i", "NAME_i", "dist_km", "elev_diff_m", "name_sim",
                 "same_country", "g_dist", "g_elev", "g_name", "vetoed", "weight", "posterior", "fs_class",
                 "label_l15", "label_meta"]
    p[keep_cols].to_parquet(os.path.join(OUT, "er_fellegi_sunter_pairs.parquet"), index=False)
    with open(os.path.join(OUT, "er_fellegi_sunter_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print("Da ghi er_fellegi_sunter_pairs.parquet, er_fellegi_sunter_summary.json")


if __name__ == "__main__":
    main()
