#!/usr/bin/env python3
"""方法学模块 2：重校准（温度缩放 / 等渗回归）与决策曲线分析（DCA）。

回答三个问题（都是"评价学"论文要的）：
  Q1 源域校准 → 目标域：用源域留出的校准集拟合温度，能否救回目标域校准？（可迁移的重校准）
  Q2 目标域校准（oracle 上界）：如果直接在目标域拟合，校准能恢复多少？（给出可达上限）
  Q3 决策层面：重校准前后，净获益（net benefit）差多少？

注意：温度缩放/等渗回归都是单调变换，**AUROC 不变**——这本身就是要写的结论：
      "校准改善不改变排序能力，但改变可用性"。
输出：out/recalibration_results.json, out/table_recal.csv, out/fig3_recalibration_netbenefit.png
"""
import json, pathlib, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from scipy.optimize import minimize_scalar
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

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


def logit(p, eps=1e-6):
    p = np.clip(p, eps, 1 - eps)
    return np.log(p / (1 - p))


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def fit_temperature(p, y):
    """在给定概率与标签上拟合温度 T（最小化 log loss）。"""
    z = logit(p)

    def nll(logT):
        return -np.mean(y * np.log(sigmoid(z / np.exp(logT)) + 1e-12) +
                         (1 - y) * np.log(1 - sigmoid(z / np.exp(logT)) + 1e-12))

    res = minimize_scalar(nll, bounds=(-3, 3), method="bounded")
    return float(np.exp(res.x))


def ece(y, p, bins=10):
    edges = np.linspace(0, 1, bins + 1)
    e = 0.0
    for i in range(bins):
        m = (p >= edges[i]) & (p < edges[i + 1] if i < bins - 1 else p <= 1.0)
        if m.sum():
            e += m.sum() / len(y) * abs(p[m].mean() - y[m].mean())
    return float(e)


def sens_at_spec(y, p, target_spec=0.90):
    """在目标特异度下的灵敏度：阈值取阴性分布的 (1-spec) 分位点。"""
    y = np.asarray(y); p = np.asarray(p)
    neg = p[y == 0]
    if len(neg) == 0:
        return float("nan"), float("nan")
    # 特异度 = 阴性中低于阈值的比例 → 阈值取阴性分布的 spec 分位点（spec=0.90 → 90% 分位）
    thr = np.quantile(neg, target_spec)
    pred = p >= thr
    se = (pred & (y == 1)).sum() / max(1, (y == 1).sum())
    sp = (~pred & (y == 0)).sum() / max(1, (y == 0).sum())
    return float(se), float(sp)


def ece_equal_count(y, p, bins=10):
    """等频分箱 ECE（对分布漂移更稳健，避免固定分箱全挤在低概率端）。"""
    y = np.asarray(y); p = np.asarray(p)
    order = np.argsort(p)
    chunks = np.array_split(order, bins)
    e = 0.0
    for idx in chunks:
        if len(idx) == 0:
            continue
        e += len(idx) / len(y) * abs(p[idx].mean() - y[idx].mean())
    return float(e)


def calib_slope(y, p):
    """校准斜率：y ~ logit(p) 的斜率，1.0 为理想。"""
    z = logit(p).reshape(-1, 1)
    try:
        lr = LogisticRegression(penalty=None, max_iter=1000).fit(z, y)
        return float(lr.coef_[0][0]), float(lr.intercept_[0])
    except Exception:
        return float("nan"), float("nan")


def dca(y, p, thresholds=np.arange(0.01, 0.51, 0.01)):
    """决策曲线：net benefit = TP/n - FP/n * (pt/(1-pt))。"""
    y = np.asarray(y); p = np.asarray(p); n = len(y)
    nb, nb_all, nb_none = [], [], []
    prev = y.mean()
    for pt in thresholds:
        pred = p >= pt
        tp = (pred & (y == 1)).sum(); fp = (pred & (y == 0)).sum()
        nb.append(tp / n - fp / n * (pt / (1 - pt)))
        nb_all.append(prev - (1 - prev) * (pt / (1 - pt)))     # 全部判阳性
        nb_none.append(0.0)                                    # 全部判阴性
    return thresholds, np.array(nb), np.array(nb_all), np.array(nb_none)


def metrics(y, p, tag):
    se90, sp90 = sens_at_spec(y, p, 0.90)
    sl, ic = calib_slope(y, np.clip(p, 1e-6, 1 - 1e-6))
    return {"setting": tag, "n": int(len(y)), "auroc": float(roc_auc_score(y, p)),
            "brier": float(brier_score_loss(y, np.clip(p, 0, 1))),
            "ece": ece(y, np.clip(p, 0, 1)), "ece_eq": ece_equal_count(y, np.clip(p, 0, 1)),
            "cal_slope": sl, "cal_intercept": ic,
            "sens_at_spec90": se90, "spec_at_spec90": sp90,
            "mean_pred": float(np.mean(np.clip(p, 0, 1))), "observed": float(np.mean(y))}


def main():
    df_p = pd.read_csv(OUT / "feat_ptbxl.csv")
    df_c = pd.read_csv(OUT / "feat_cinc2017.csv")
    feats = [c for c in df_p.columns if c.startswith("f_")]
    print(f"PTB-XL n={len(df_p)}  CinC2017 n={len(df_c)}  features={len(feats)}")

    # 患者级：训练 / 测试 / 校准（校准集从训练患者里再切 20%）
    pats = df_p["patient_id"].unique()
    rng = np.random.RandomState(SEED)
    rng.shuffle(pats)
    n_tr = int(0.7 * len(pats))
    tr_pats = pats[:n_tr]
    rng2 = np.random.RandomState(SEED + 1)
    rng2.shuffle(tr_pats)
    n_cal = int(0.2 * len(tr_pats))
    cal_pats, fit_pats = set(tr_pats[:n_cal]), set(tr_pats[n_cal:])
    fit = df_p[df_p["patient_id"].isin(fit_pats)]
    cal = df_p[df_p["patient_id"].isin(cal_pats)]
    te = df_p[~df_p["patient_id"].isin(set(tr_pats))]
    print(f"fit={len(fit)} cal={len(cal)} internal-test={len(te)} external={len(df_c)}")

    results = {}
    fig_data = {}
    for name, mdl in {
        "hgb": make_pipeline(HistGradientBoostingClassifier(max_iter=300, learning_rate=0.06, random_state=0)),
        "logreg": make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                                LogisticRegression(max_iter=2000, class_weight="balanced")),
    }.items():
        mdl.fit(fit[feats], fit["label"])
        p_cal = mdl.predict_proba(cal[feats])[:, 1]
        p_in = mdl.predict_proba(te[feats])[:, 1]
        p_ex = mdl.predict_proba(df_c[feats])[:, 1]
        y_in, y_ex = te["label"].values, df_c["label"].values

        T_src = fit_temperature(p_cal, cal["label"].values)          # 源域校准（可迁移）
        T_tgt = fit_temperature(p_ex, y_ex)                          # 目标域校准（oracle 上界）
        iso_src = IsotonicRegression(out_of_bounds="clip").fit(p_cal, cal["label"].values)
        iso_tgt = IsotonicRegression(out_of_bounds="clip").fit(p_ex, y_ex)

        rows = [
            metrics(y_in, p_in, f"{name} | 内部验证（未校准）"),
            metrics(y_ex, p_ex, f"{name} | 外部验证（未校准）"),
            metrics(y_ex, sigmoid(logit(p_ex) / T_src), f"{name} | 外部 + 源域温度(T={T_src:.2f})"),
            metrics(y_ex, sigmoid(logit(p_ex) / T_tgt), f"{name} | 外部 + 目标域温度(T={T_tgt:.2f}, oracle)"),
            metrics(y_ex, iso_src.predict(p_ex), f"{name} | 外部 + 源域等渗"),
            metrics(y_ex, iso_tgt.predict(p_ex), f"{name} | 外部 + 目标域等渗(oracle)"),
        ]
        for r in rows:
            results[r["setting"]] = r
            print(f"  {r['setting']:52s} AUROC={r['auroc']:.3f} Brier={r['brier']:.3f} "
                  f"ECE={r['ece']:.3f} ECE_eq={r['ece_eq']:.3f} 斜率={r['cal_slope']:.2f} Se@Sp90={r['sens_at_spec90']:.3f} 平均预测={r['mean_pred']:.3f} 实际={r['observed']:.3f}")

        # DCA 关键阈值净获益
        for tag, pp in [("外部(未校准)", p_ex),
                        ("外部+源域温度", sigmoid(logit(p_ex) / T_src)),
                        ("外部+目标域温度", sigmoid(logit(p_ex) / T_tgt)),
                        ("内部(未校准)", p_in)]:
            th, nb, nb_all, nb_none = dca(y_ex if "外部" in tag else y_in, pp)
            for pt in (0.05, 0.10, 0.20, 0.30):
                i = int(np.argmin(np.abs(th - pt)))
                results.setdefault("dca", {}).setdefault(tag, {})[f"nb@{pt:.2f}"] = float(nb[i])
        results.setdefault("temperatures", {})[name] = {"T_source": T_src, "T_target": T_tgt}

        if name == "hgb":
            fig_data = {"y_in": y_in, "p_in": p_in, "y_ex": y_ex, "p_ex": p_ex,
                        "p_ex_Tsrc": sigmoid(logit(p_ex) / T_src),
                        "p_ex_Ttgt": sigmoid(logit(p_ex) / T_tgt), "T_src": T_src, "T_tgt": T_tgt}

    pd.DataFrame([v for k, v in results.items() if isinstance(v, dict) and "auroc" in v]) \
        .to_csv(OUT / "table_recal.csv", index=False)
    json.dump(results, open(OUT / "recalibration_results.json", "w"), indent=1, ensure_ascii=False)

    # ---- 图 3：左=重校准前后可靠性曲线；右=决策曲线 ----
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    ax = axes[0]

    def rel(y, p, bins=10):
        edges = np.linspace(0, 1, bins + 1)
        xs, ys = [], []
        for i in range(bins):
            m = (p >= edges[i]) & (p < edges[i + 1] if i < bins - 1 else p <= 1.0)
            if m.sum() >= 5:
                xs.append(p[m].mean()); ys.append(y[m].mean())
        return np.array(xs), np.array(ys)

    for arr, lab, col, ls in [(fig_data["p_ex"], "外部（未校准）", "#d62728", "-"),
                              (fig_data["p_ex_Tsrc"], f"外部 + 源域温度(T={fig_data['T_src']:.2f})", "#ff7f0e", "--"),
                              (fig_data["p_ex_Ttgt"], f"外部 + 目标域温度(T={fig_data['T_tgt']:.2f})", "#2ca02c", "-"),
                              (fig_data["p_in"], "内部（未校准）", "#1f77b4", "-")]:
        xs, ys = rel(fig_data["y_ex"] if "外部" in lab else fig_data["y_in"], arr)
        ax.plot(xs, ys, marker="o", ls=ls, color=col, label=lab)
    ax.plot([0, 1], [0, 1], "k--", lw=1, label="完美校准")
    ax.set_xlabel("模型预测概率"); ax.set_ylabel("实际房颤比例")
    ax.set_title("重校准前后：温度缩放能否救回校准"); ax.legend(fontsize=8); ax.grid(alpha=.3)

    ax = axes[1]
    for arr, lab, col in [(fig_data["p_ex"], "外部（未校准）", "#d62728"),
                          (fig_data["p_ex_Tsrc"], "外部 + 源域温度", "#ff7f0e"),
                          (fig_data["p_ex_Ttgt"], "外部 + 目标域温度", "#2ca02c")]:
        th, nb, _, _ = dca(fig_data["y_ex"], arr)
        ax.plot(th, nb, color=col, label=lab)
    th, nb, nb_all, _ = dca(fig_data["y_ex"], fig_data["p_ex"])
    ax.plot(th, nb_all, "k:", lw=1, label="全部判阳性")
    ax.axhline(0, color="gray", lw=1, ls="-")
    ax.set_ylim(-0.2, max(0.35, np.nanmax(nb) * 1.2))
    ax.set_xlabel("阈值概率 pt"); ax.set_ylabel("净获益 net benefit")
    ax.set_title("决策曲线：校准对临床净获益的影响"); ax.legend(fontsize=8); ax.grid(alpha=.3)

    plt.tight_layout()
    fig.savefig(OUT / "fig3_recalibration_netbenefit.png", dpi=200)
    print("saved:", OUT / "fig3_recalibration_netbenefit.png")


if __name__ == "__main__":
    main()
