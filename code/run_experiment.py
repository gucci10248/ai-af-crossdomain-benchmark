#!/usr/bin/env python3
"""实验 1：PTB-XL（德国，12 导联取 I 导）内部验证 + 外部迁移到 CinC2017（AliveCor 可穿戴单导联）。

目的（对应选题 P2）：不做"刷 AUC"，而是量化
  1) 同数据集内的性能（患者级划分，避免泄漏）
  2) 跨数据集 / 跨设备 / 跨人群的外部验证衰减
  3) 校准度（Brier / ECE）与亚组（性别、年龄）差异 —— 这些才是"评价学"论文的真正内容
输出：out/results_exp1.json、out/table_exp1.csv、out/fig_reliability.png、out/fig_feature_importance.png
"""
import json, pathlib, sys, warnings
import numpy as np
import pandas as pd
import wfdb
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss

warnings.filterwarnings("ignore")
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from features import extract  # noqa

BASE = pathlib.Path("/Users/mac/Desktop/库/公共数据AF")
DATA = BASE / "data"
OUT = BASE / "out"
OUT.mkdir(exist_ok=True)


# ---------------- 数据读取 ----------------
def load_ptbxl_subset():
    meta = json.load(open(DATA / "ptbxl_subset_meta.json"))
    recs = []
    for m in meta:
        eid = m["ecg_id"]
        p = DATA / "records100" / f"{(eid - 1) // 1000 * 1000:05d}" / f"{eid:05d}_lr"
        if not (pathlib.Path(str(p) + ".hea").is_file() and pathlib.Path(str(p) + ".dat").is_file()):
            continue          # 尚未下载完的记录直接跳过（支持“边下边跑”）
        try:
            r = wfdb.rdrecord(str(p))
            recs.append({**m, "signal": r.p_signal, "fs": r.fs})
        except Exception as e:
            print("  [skip]", eid, type(e).__name__)
    return recs


C17_MAP = {"A": 1, "N": 0, "O": 0, "~": 0}   # 先做"房颤 vs 非房颤"；O/~ 视为非房颤（更严格口径会在脚本里另算）


def c17_relpath_map():
    """CinC2017 训练集在 PhysioNet 上按子目录存放（A00/A00001.mat），需从官方 RECORDS 取真实路径。"""
    m = {}
    p = DATA / "cinc2017_RECORDS.txt"
    if p.exists():
        for line in p.read_text().splitlines():
            line = line.strip()
            if line:
                m[line.split("/")[-1]] = line
    return m


C17_REL = c17_relpath_map()


def load_cinc2017():
    ids = [x.strip() for x in open(DATA / "cinc2017_subset.txt") if x.strip()]
    lab = {}
    for line in open(DATA / "REFERENCE-v3.csv"):
        parts = line.strip().split(",")
        if len(parts) >= 2:
            lab[parts[0]] = parts[1]
    recs = []
    for rid in ids:
        rel = C17_REL.get(rid, rid)
        p = DATA / "cinc2017" / "training" / rel
        if not pathlib.Path(str(p) + ".hea").is_file():
            continue
        try:
            r = wfdb.rdrecord(str(p))
            recs.append({"rec_id": rid, "label": C17_MAP.get(lab.get(rid, ""), 0),
                         "label_raw": lab.get(rid, ""), "signal": r.p_signal, "fs": r.fs})
        except Exception as e:
            print("  [skip]", rid, type(e).__name__)
    return recs


# ---------------- 特征 ----------------
def featurize(recs, lead=None, tag=""):
    rows = []
    for i, r in enumerate(recs):
        f = extract(r["signal"], r["fs"], lead=lead)
        if f is None:
            f = {}
        rows.append({**{k: v for k, v in r.items() if k not in ("signal",)},
                     **{("f_" + k): v for k, v in f.items()}})
        if (i + 1) % 500 == 0:
            print(f"  {tag} featurized {i+1}/{len(recs)}")
    return pd.DataFrame(rows)


# ---------------- 评估 ----------------
def ece(y, p, bins=10):
    edges = np.linspace(0, 1, bins + 1)
    e = 0.0
    n = len(y)
    for i in range(bins):
        m = (p >= edges[i]) & (p < edges[i + 1] if i < bins - 1 else p <= 1.0)
        if m.sum() == 0:
            continue
        e += m.sum() / n * abs(p[m].mean() - y[m].mean())
    return float(e)


def evaluate(y, p, name, meta=None):
    y = np.asarray(y).astype(int)
    p = np.asarray(p, dtype=float)
    ok = ~np.isnan(p)
    y, p = y[ok], p[ok]
    res = {"dataset": name, "n": int(len(y)), "n_pos": int(y.sum()),
           "prevalence": float(y.mean()) if len(y) else float("nan"),
           "auroc": float(roc_auc_score(y, p)) if y.min() != y.max() else float("nan"),
           "auprc": float(average_precision_score(y, p)) if y.min() != y.max() else float("nan"),
           "brier": float(brier_score_loss(y, p)), "ece": ece(y, p)}

    def at(thr):
        pred = p >= thr
        tp = int((pred & (y == 1)).sum()); fn = int((~pred & (y == 1)).sum())
        tn = int((~pred & (y == 0)).sum()); fp = int((pred & (y == 0)).sum())
        return {
            "thr": float(thr),
            "sens": tp / (tp + fn) if (tp + fn) else float("nan"),
            "spec": tn / (tn + fp) if (tn + fp) else float("nan"),
            "ppv": tp / (tp + fp) if (tp + fp) else float("nan"),
            "npv": tn / (tn + fn) if (tn + fn) else float("nan"),
        }

    res["at_0.5"] = at(0.5)
    # 阈值取到"特异度≈90%"的操作点（筛查场景常用）
    order = np.argsort(-p)
    y_sorted = y[order]
    tn_total = int((y == 0).sum())
    thr90 = p[order][min(len(p) - 1, max(0, np.searchsorted(np.cumsum(y_sorted == 0), 0.10 * tn_total)))] if tn_total else 0.5
    res["at_spec90"] = at(thr90)
    if meta is not None:
        sub = {}
        for key in ("sex", "age_band"):
            if key in meta.columns:
                for val in sorted(meta[key].dropna().unique()):
                    m = (meta[key] == val).values
                    if m.sum() < 20:
                        continue
                    m = m[ok]
                    if y[m].min() == y[m].max():
                        continue
                    sub[f"{key}={val}"] = {"n": int(m.sum()),
                                           "auroc": float(roc_auc_score(y[m], p[m])),
                                           "sens": float(((p[m] >= 0.5) & (y[m] == 1)).sum() / max(1, (y[m] == 1).sum())),
                                           "spec": float(((p[m] < 0.5) & (y[m] == 0)).sum() / max(1, (y[m] == 0).sum()))}
        res["subgroups"] = sub
    return res


def main():
    print("== 读取 PTB-XL 子集 ==")
    ptb = load_ptbxl_subset()
    print("  loaded:", len(ptb))
    print("== 读取 CinC2017 子集 ==")
    c17 = load_cinc2017()
    print("  loaded:", len(c17))

    print("== 特征提取 ==")
    import os
    reuse = os.environ.get("REUSE_FEATURES", "0") == "1"
    if reuse and (OUT / "feat_ptbxl.csv").exists():
        df_p = pd.read_csv(OUT / "feat_ptbxl.csv")
        print(f"  复用 PTB-XL 缓存特征: {len(df_p)}")
    else:
        df_p = featurize(ptb, lead=0, tag="ptbxl(lead I)")
        df_p.to_csv(OUT / "feat_ptbxl.csv", index=False)
    if reuse and (OUT / "feat_cinc2017.csv").exists():
        df_c = pd.read_csv(OUT / "feat_cinc2017.csv")
        print(f"  复用 CinC2017 缓存特征: {len(df_c)}")
    else:
        df_c = featurize(c17, lead=0, tag="cinc2017(single-lead)")
        df_c.to_csv(OUT / "feat_cinc2017.csv", index=False)
    df_p["age_band"] = pd.cut(df_p["age"], [0, 50, 65, 75, 120], labels=["<50", "50-64", "65-74", "75+"])
    df_p["sex"] = df_p["sex"].astype(str)

    # 第三个域：CPSC2021（中国，动态 ECG 切 30 秒窗）——由 cpsc2021_windows.py 预先产出
    df_x = pd.DataFrame()
    fx = OUT / "feat_cpsc2021.csv"
    if fx.exists() and fx.stat().st_size > 100:
        df_x = pd.read_csv(fx)
        df_x["label"] = df_x["label"].astype(int)
        print(f"  CPSC2021 窗级特征已载入: {len(df_x)} 窗 / {df_x['patient'].nunique()} 位患者 / "
              f"阳性窗 {int(df_x['label'].sum())}")

    feats = sorted([c for c in df_p.columns if c.startswith("f_")])
    print("  n features:", len(feats))

    # 患者级划分（同一患者的所有记录只进一侧，避免泄漏）
    pats = df_p["patient_id"].unique()
    rng = np.random.RandomState(20260915)
    rng.shuffle(pats)
    n_tr = int(0.7 * len(pats))
    tr_pats = set(pats[:n_tr])
    tr = df_p[df_p["patient_id"].isin(tr_pats)]
    te = df_p[~df_p["patient_id"].isin(tr_pats)]
    print(f"  PTB-XL patient-level split: train {len(tr)} recs / test {len(te)} recs")

    models = {
        "logreg": make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                                LogisticRegression(max_iter=2000, class_weight="balanced")),
        "hgb": make_pipeline(SimpleImputer(strategy="median"),
                             HistGradientBoostingClassifier(max_iter=300, learning_rate=0.06,
                                                            max_depth=None, random_state=0)),
    }
    results = {}
    best_name, best_auc, best_model = None, -1, None
    for name, mdl in models.items():
        mdl.fit(tr[feats], tr["label"])
        p = mdl.predict_proba(te[feats])[:, 1]
        meta = te[["sex", "age_band"]].reset_index(drop=True)
        r = evaluate(te["label"].values, p, f"PTB-XL internal ({name})", meta=meta)
        r["split"] = "internal (patient-level)"
        results[f"ptbxl_internal_{name}"] = r
        print(f"  [{name}] AUROC={r['auroc']:.3f} AUPRC={r['auprc']:.3f} Brier={r['brier']:.3f} ECE={r['ece']:.3f}")
        if r["auroc"] > best_auc:
            best_name, best_auc, best_model = name, r["auroc"], mdl

        if len(df_c) < 20:
            print("  CinC2017 数据尚不足，跳过外部验证与域内对照（等下载完成后再跑）")
            continue
        # 外部迁移：在同一模型上直接测 CinC2017（跨设备/跨人群/跨信号长度）
        p_ext = mdl.predict_proba(df_c[feats])[:, 1]
        r_ext = evaluate(df_c["label"].values, p_ext, f"CinC2017 external (trained on PTB-XL/{name})")
        r_ext["split"] = "external (PTB-XL -> CinC2017)"
        results[f"cinc2017_external_from_{name}"] = r_ext
        print(f"  [{name}] EXTERNAL CinC2017 AUROC={r_ext['auroc']:.3f} "
              f"Sens={r_ext['at_0.5']['sens']:.3f} Spec={r_ext['at_0.5']['spec']:.3f} Brier={r_ext['brier']:.3f}")

        # 严格口径：只用 A（房颤）与 N（正常）两类，剔除 O（其他节律）与噪声，避免"非房颤"含义过宽
        strict = df_c[df_c["label_raw"].isin(["A", "N"])]
        if len(strict) >= 40 and strict["label"].nunique() == 2:
            p_str = mdl.predict_proba(strict[feats])[:, 1]
            r_str = evaluate(strict["label"].values, p_str,
                             f"CinC2017 external AF-vs-N only (trained on PTB-XL/{name})")
            r_str["split"] = "external strict (A vs N)"
            results[f"cinc2017_external_strict_{name}"] = r_str
            print(f"  [{name}] EXTERNAL strict(A vs N) n={r_str['n']} AUROC={r_str['auroc']:.3f} "
                  f"Sens={r_str['at_0.5']['sens']:.3f} Spec={r_str['at_0.5']['spec']:.3f}")

        # 逐年 / 逐来源的域内对照：CinC2017 自身 5 折（患者不可辨，按记录随机）
        from sklearn.model_selection import StratifiedKFold
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
        oof = np.zeros(len(df_c))
        for tri, tei in skf.split(df_c[feats], df_c["label"]):
            m2 = type(mdl)(**mdl.named_steps[list(mdl.named_steps)[-1]].get_params()) if False else None
            mdl2 = make_pipeline(SimpleImputer(strategy="median"),
                                 HistGradientBoostingClassifier(max_iter=300, learning_rate=0.06, random_state=0))
            mdl2.fit(df_c.iloc[tri][feats], df_c.iloc[tri]["label"])
            oof[tei] = mdl2.predict_proba(df_c.iloc[tei][feats])[:, 1]
        r_in = evaluate(df_c["label"].values, oof, "CinC2017 internal 5-fold (in-domain reference)")
        r_in["split"] = "internal (CinC2017 5-fold)"
        results["cinc2017_internal_5fold"] = r_in
        print(f"  [{name}] CinC2017 in-domain 5-fold AUROC={r_in['auroc']:.3f}")

    # ---- 第三个域：CPSC2021（中国，动态 ECG 的 30 秒窗）作为第二个外部测试集 ----
    if len(df_x) >= 40 and df_x["label"].nunique() == 2:
        from sklearn.model_selection import GroupKFold
        for name, mdl in models.items():
            p_x = mdl.predict_proba(df_x[feats])[:, 1]
            r_x = evaluate(df_x["label"].values, p_x,
                           f"CPSC2021 external (China, trained on PTB-XL/{name})")
            r_x["split"] = "external (PTB-XL -> CPSC2021 China)"
            results[f"cpsc2021_external_{name}"] = r_x
            print(f"  [{name}] EXTERNAL CPSC2021(中国) n={r_x['n']} AUROC={r_x['auroc']:.3f} "
                  f"Brier={r_x['brier']:.3f} ECE={r_x['ece']:.3f} "
                  f"Se={r_x['at_0.5']['sens']:.3f} Sp={r_x['at_0.5']['spec']:.3f}")

        # 域内参照：按"患者"分组的 5 折（防止同一患者的窗跨训练/测试），只算一次
        g = df_x["patient"].values
        gkf = GroupKFold(n_splits=5)
        oof = np.zeros(len(df_x))
        for tri, tei in gkf.split(df_x[feats], df_x["label"], groups=g):
            m2 = make_pipeline(SimpleImputer(strategy="median"),
                               HistGradientBoostingClassifier(max_iter=300, learning_rate=0.06, random_state=0))
            m2.fit(df_x.iloc[tri][feats], df_x.iloc[tri]["label"])
            oof[tei] = m2.predict_proba(df_x.iloc[tei][feats])[:, 1]
        r_xin = evaluate(df_x["label"].values, oof, "CPSC2021 in-domain 5-fold (grouped by patient)")
        r_xin["split"] = "internal (CPSC2021 grouped 5-fold)"
        results["cpsc2021_internal_5fold"] = r_xin
        print(f"  [hgb] CPSC2021 域内(按患者分组5折) AUROC={r_xin['auroc']:.3f} "
              f"Brier={r_xin['brier']:.3f} ECE={r_xin['ece']:.3f}")

    # 特征重要性（用最佳模型里的 HGB）
    try:
        from sklearn.inspection import permutation_importance
        imp = permutation_importance(best_model, te[feats], te["label"], n_repeats=5,
                                     random_state=0, scoring="roc_auc")
        order = np.argsort(-imp.importances_mean)[:20]
        imp_rows = [{"feature": feats[i], "drop_in_auroc": float(imp.importances_mean[i])} for i in order]
        json.dump(imp_rows, open(OUT / "feature_importance.json", "w"), indent=1)
        print("  top features:", ", ".join(f"{r['feature']}({r['drop_in_auroc']:.3f})" for r in imp_rows[:8]))
    except Exception as e:
        print("  permutation importance failed:", e)

    json.dump(results, open(OUT / "results_exp1.json", "w"), indent=1, ensure_ascii=False)
    rows = []
    for k, v in results.items():
        rows.append({"key": k, "dataset": v["dataset"], "n": v["n"], "auroc": v["auroc"],
                     "auprc": v["auprc"], "brier": v["brier"], "ece": v["ece"],
                     "sens@0.5": v["at_0.5"]["sens"], "spec@0.5": v["at_0.5"]["spec"],
                     "sens@spec90": v["at_spec90"]["sens"]})
    pd.DataFrame(rows).to_csv(OUT / "table_exp1.csv", index=False)
    print("\n== 汇总 ==")
    print(pd.DataFrame(rows).to_string(index=False))
    print("\n结果已写入:", OUT)


if __name__ == "__main__":
    main()
