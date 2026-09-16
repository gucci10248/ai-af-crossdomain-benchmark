#!/usr/bin/env python3
"""重校准 / DCA 多域版：源域校准 vs 目标域校准（oracle），在**两个外部域**上分别评估。

结论口径：
  - 单调重校准（温度缩放/等渗）**不改变 AUROC**，改的是概率可用性与决策；
  - 源域拟合的温度能否迁移过去？目标域 oracle 重校准能恢复到什么程度（上界）？
  - 判别力（AUROC / Se@Sp90）与校准（Brier/ECE）在跨域时是两件不同的事。
输出：out/recalibration_results.json, out/table_recal_multidomain.csv, out/fig3_recalibration_multidomain.png
"""
import json, pathlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from scipy.optimize import minimize_scalar
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss
from sklearn.pipeline import make_pipeline

_CJK = "/Library/Fonts/Arial Unicode.ttf"
try:
    font_manager.fontManager.addfont(_CJK)
    plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]
    plt.rcParams["axes.unicode_minus"] = False
except Exception:
    pass

BASE = pathlib.Path("/Users/mac/Desktop/库/公共数据AF")
OUT = BASE / "out"
SEED = 20260915


def logit(p, eps=1e-12):
    # eps=1e-12：尽量保持严格单调（旧版 1e-6 会把大量接近 1 的概率压成同值，产生并列、拉低 AUROC）
    p = np.clip(p, eps, 1 - eps)
    return np.log(p / (1 - p))


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def fit_temperature(p, y):
    z = logit(p)

    def nll(logT):
        q = sigmoid(z / np.exp(logT))
        return -np.mean(y * np.log(q + 1e-12) + (1 - y) * np.log(1 - q + 1e-12))

    return float(np.exp(minimize_scalar(nll, bounds=(-3, 3), method="bounded").x))


def ece(y, p, bins=10, equal=False):
    y = np.asarray(y); p = np.asarray(p)
    if equal:
        return float(sum(len(i) / len(y) * abs(p[i].mean() - y[i].mean())
                         for i in np.array_split(np.argsort(p), bins) if len(i)))
    edges = np.linspace(0, 1, bins + 1); e = 0.0
    for i in range(bins):
        m = (p >= edges[i]) & (p < edges[i + 1] if i < bins - 1 else p <= 1.0)
        if m.sum():
            e += m.sum() / len(y) * abs(p[m].mean() - y[m].mean())
    return float(e)


def se_at_spec(y, p, spec=0.90):
    neg = np.asarray(p)[np.asarray(y) == 0]
    thr = np.quantile(neg, spec)
    pred = np.asarray(p) >= thr
    return float((pred & (np.asarray(y) == 1)).sum() / max(1, (np.asarray(y) == 1).sum()))


def dca(y, p, thresholds=np.arange(0.01, 0.61, 0.01)):
    y = np.asarray(y); p = np.asarray(p); n = len(y); prev = y.mean()
    nb, nb_all = [], []
    for pt in thresholds:
        pred = p >= pt
        tp = (pred & (y == 1)).sum(); fp = (pred & (y == 0)).sum()
        nb.append(tp / n - fp / n * (pt / (1 - pt)))
        nb_all.append(prev - (1 - prev) * (pt / (1 - pt)))
    return thresholds, np.array(nb), np.array(nb_all)


def row(y, p, setting, domain, method):
    return {"domain": domain, "method": method, "setting": setting, "n": int(len(y)),
            "auroc": float(roc_auc_score(y, p)), "brier": float(brier_score_loss(y, np.clip(p, 0, 1))),
            "ece": ece(y, np.clip(p, 0, 1)), "ece_eq": ece(y, np.clip(p, 0, 1), equal=True),
            "se_at_sp90": se_at_spec(y, p, 0.90), "mean_pred": float(np.mean(p)), "observed": float(np.mean(y))}


def main():
    df_p = pd.read_csv(OUT / "feat_ptbxl.csv")
    domains = {"CinC2017（消费级可穿戴单导联）": pd.read_csv(OUT / "feat_cinc2017.csv"),
               "CPSC2021（中国动态 ECG 30 秒窗）": pd.read_csv(OUT / "feat_cpsc2021.csv")}
    feats = sorted([c for c in df_p.columns if c.startswith("f_")])  # 与 run_experiment.py 一致：列序影响 HGB 结果

    pats = df_p["patient_id"].unique()
    rng = np.random.RandomState(SEED); rng.shuffle(pats)
    tr_pats = list(pats[:int(0.7 * len(pats))])
    # 2026-09-15 修复：取消校准留出集（旧版 fit 只用 80% 训练患者 → 与主结果不是同一模型，
    # 导致本表"未校准"行 AUROC 0.868 与 table_domains 的 0.885 对不上，构成第二次"数字双源"）。
    # 现改为：模型用全部训练患者（与 run_experiment 完全一致），源域温度/等渗在训练集上
    # in-sample 拟合。in-sample 只会让源域校准则更乐观，而本文结论是"即使这样也无法迁移"，
    # 结论方向不变且表述更强。
    fit = df_p[df_p["patient_id"].isin(set(tr_pats))]
    te = df_p[~df_p["patient_id"].isin(set(tr_pats))]
    mdl = make_pipeline(SimpleImputer(strategy="median"),
                        HistGradientBoostingClassifier(max_iter=300, learning_rate=0.06, random_state=0))
    mdl.fit(fit[feats], fit["label"])
    # 源域校准器用训练集 5 折患者级交叉预测（out-of-fold）拟合——诚实的源域校准，
    # 且最终评估模型就是全训练集模型 → 本表"未校准"行与 run_experiment/table_domains 逐位一致。
    from sklearn.model_selection import GroupKFold
    p_cv = np.zeros(len(fit))
    for _tr, _va in GroupKFold(n_splits=5).split(fit[feats], fit["label"], groups=fit["patient_id"].values):
        m_cv = make_pipeline(SimpleImputer(strategy="median"),
                             HistGradientBoostingClassifier(max_iter=300, learning_rate=0.06, random_state=0))
        m_cv.fit(fit[feats].iloc[_tr], fit["label"].iloc[_tr])
        p_cv[_va] = m_cv.predict_proba(fit[feats].iloc[_va])[:, 1]
    T_src = fit_temperature(p_cv, fit["label"].values)
    iso_src = IsotonicRegression(out_of_bounds="clip").fit(p_cv, fit["label"].values)
    print(f"源域校准温度 T={T_src:.2f}（训练集 5 折 OOF 拟合；>1 表示源域概率偏极端）")

    rows = [row(te["label"].values, mdl.predict_proba(te[feats])[:, 1], "内部验证（源域测试集）", "源域 PTB-XL", "未校准")]
    fig_data = {}
    for dname, df in domains.items():
        y = df["label"].values
        p = mdl.predict_proba(df[feats])[:, 1]
        T_tgt = fit_temperature(p, y)
        iso_tgt = IsotonicRegression(out_of_bounds="clip").fit(p, y)
        rows += [
            row(y, p, "未校准", dname, "未校准"),
            row(y, sigmoid(logit(p) / T_src), f"源域温度 T={T_src:.2f}", dname, "温度缩放(源域拟合)"),
            row(y, sigmoid(logit(p) / T_tgt), f"目标域温度 T={T_tgt:.2f}（oracle）", dname, "温度缩放(目标域拟合)"),
            row(y, iso_src.predict(p), "源域等渗", dname, "等渗回归(源域拟合)"),
            row(y, iso_tgt.predict(p), f"目标域等渗（oracle）", dname, "等渗回归(目标域拟合)"),
        ]
        fig_data[dname] = {"y": y, "p": p, "p_Tsrc": sigmoid(logit(p) / T_src),
                           "p_Ttgt": sigmoid(logit(p) / T_tgt), "T_src": T_src, "T_tgt": T_tgt}
        print(f"\n--- {dname} ---")
        for r in rows[-5:]:
            print(f"  {r['method']:20s} AUROC={r['auroc']:.3f} Brier={r['brier']:.3f} "
                  f"ECE={r['ece']:.3f} ECE_eq={r['ece_eq']:.3f} Se@Sp90={r['se_at_sp90']:.3f} "
                  f"平均预测={r['mean_pred']:.3f} 实际={r['observed']:.3f}")

    tbl = pd.DataFrame(rows)
    tbl.to_csv(OUT / "table_recal_multidomain.csv", index=False)
    json.dump({"rows": rows, "T_source": T_src,
               "T_target": {d: float(fd["T_tgt"]) for d, fd in fig_data.items()}},
              open(OUT / "recalibration_results.json", "w"), indent=1, ensure_ascii=False)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    ax = axes[0]
    for dname, d in fig_data.items():
        for key, lab, col, ls in [("p", "未校准", "#D55E00", "-"),
                                  ("p_Tsrc", f"源域温度({d['T_src']:.2f})", "#E69F00", "--"),
                                  ("p_Ttgt", f"目标域温度({d['T_tgt']:.2f})", "#009E73", "-")]:
            edges = np.linspace(0, 1, 11); xs, ys = [], []
            for i in range(10):
                m = (d[key] >= edges[i]) & (d[key] < edges[i + 1] if i < 9 else d[key] <= 1.0)
                if m.sum() >= 5:
                    xs.append(d[key][m].mean()); ys.append(d["y"][m].mean())
            ax.plot(xs, ys, "o-", ls=ls, color=col, alpha=0.85,
                    label=f"{dname[:10]}… {lab}")
    ax.plot([0, 1], [0, 1], "k--", lw=1)
    ax.set_xlabel("预测概率"); ax.set_ylabel("实际房颤比例")
    ax.set_title("两个外部域的校准与重校准"); ax.legend(fontsize=6.5); ax.grid(alpha=.3)

    ax = axes[1]
    for dname, d in fig_data.items():
        th, nb, nb_all = dca(d["y"], d["p"])
        th2, nb2, _ = dca(d["y"], d["p_Ttgt"])
        ax.plot(th, nb, color="#D55E00", ls="-" if "CinC" in dname else "--", label=f"{dname[:12]}… 未校准")
        ax.plot(th, nb2, color="#009E73", ls="-" if "CinC" in dname else "--", label=f"{dname[:12]}… 目标域重校准")
        ax.plot(th, nb_all, color="gray", lw=1, ls=":", label="全部判阳性" if "CinC" in dname else None)
    ax.axhline(0, color="gray", lw=1)
    ax.set_ylim(-0.25, 0.40)
    ax.set_xlabel("阈值概率 pt"); ax.set_ylabel("净获益 net benefit")
    ax.set_title("决策曲线：重校准不改变 AURC，但改变可用阈值区间"); ax.legend(fontsize=6.5); ax.grid(alpha=.3)

    plt.tight_layout()
    fig.savefig(OUT / "fig3_recalibration_multidomain.png", dpi=600)
    fig.savefig(OUT / "fig3_recalibration_multidomain.tiff", dpi=600, pil_kwargs={"compression": "tiff_lzw"})
    print("\nsaved:", OUT / "fig3_recalibration_multidomain.png")


if __name__ == "__main__":
    main()
