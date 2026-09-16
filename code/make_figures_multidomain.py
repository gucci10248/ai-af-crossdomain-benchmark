#!/usr/bin/env python3
"""图 2（多域版）：内部（德国）/ 外部 1（消费级可穿戴）/ 外部 2（中国动态 ECG）的校準与操作点对比。
输出: out/fig2_multidomain_calibration.png 与 out/table_domains.csv
"""
import pathlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score, brier_score_loss, average_precision_score
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


def ece(y, p, bins=10, equal=False):
    y = np.asarray(y); p = np.asarray(p)
    if equal:
        idx = np.array_split(np.argsort(p), bins)
        return float(sum(len(i) / len(y) * abs(p[i].mean() - y[i].mean()) for i in idx if len(i)))
    edges = np.linspace(0, 1, bins + 1)
    e = 0.0
    for i in range(bins):
        m = (p >= edges[i]) & (p < edges[i + 1] if i < bins - 1 else p <= 1.0)
        if m.sum():
            e += m.sum() / len(y) * abs(p[m].mean() - y[m].mean())
    return float(e)


def se_at_spec(y, p, spec=0.90):
    neg = np.asarray(p)[np.asarray(y) == 0]
    if len(neg) == 0:
        return float("nan")
    thr = np.quantile(neg, spec)
    pred = np.asarray(p) >= thr
    return float((pred & (np.asarray(y) == 1)).sum() / max(1, (np.asarray(y) == 1).sum()))


def main():
    df_p = pd.read_csv(OUT / "feat_ptbxl.csv")
    df_c = pd.read_csv(OUT / "feat_cinc2017.csv")
    df_x = pd.read_csv(OUT / "feat_cpsc2021.csv")
    feats = sorted([c for c in df_p.columns if c.startswith("f_")])  # 与 run_experiment.py 一致：列序影响 HGB 结果

    pats = df_p["patient_id"].unique()
    rng = np.random.RandomState(SEED); rng.shuffle(pats)
    tr = df_p[df_p["patient_id"].isin(set(pats[:int(0.7 * len(pats))]))]
    te = df_p[~df_p["patient_id"].isin(set(pats[:int(0.7 * len(pats))]))]
    mdl = make_pipeline(SimpleImputer(strategy="median"),
                        HistGradientBoostingClassifier(max_iter=300, learning_rate=0.06, random_state=0))
    mdl.fit(tr[feats], tr["label"])

    sets = [("内部：PTB-XL（德国 12 导联）", te["label"].values, mdl.predict_proba(te[feats])[:, 1], "#0072B2"),
            ("外部 1：CinC2017（消费级单导联）", df_c["label"].values, mdl.predict_proba(df_c[feats])[:, 1], "#D55E00"),
            ("外部 2：CPSC2021（中国动态 ECG）", df_x["label"].values, mdl.predict_proba(df_x[feats])[:, 1], "#009E73")]

    rows = []
    for name, y, p, _ in sets:
        rows.append({"domain": name, "n": len(y), "pos": int(np.sum(y)),
                     "auroc": roc_auc_score(y, p), "auprc": average_precision_score(y, p),
                     "brier": brier_score_loss(y, p), "ece": ece(y, p), "ece_eq": ece(y, p, equal=True),
                     "mean_pred": float(np.mean(p)), "observed": float(np.mean(y)),
                     "se_at_sp90": se_at_spec(y, p, 0.90)})
    tbl = pd.DataFrame(rows)
    tbl.to_csv(OUT / "table_domains.csv", index=False)
    print(tbl.to_string(index=False))

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))
    ax = axes[0]
    for name, y, p, col in sets:
        edges = np.linspace(0, 1, 11); xs, ys = [], []
        for i in range(10):
            m = (p >= edges[i]) & (p < edges[i + 1] if i < 9 else p <= 1.0)
            if m.sum() >= 5:
                xs.append(p[m].mean()); ys.append(y[m].mean())
        ax.plot(xs, ys, "o-", color=col, label=f"{name}\nAUROC={roc_auc_score(y,p):.3f} Brier={brier_score_loss(y,p):.3f}")
    ax.plot([0, 1], [0, 1], "k--", lw=1, label="完美校准")
    ax.set_xlabel("预测概率"); ax.set_ylabel("实际房颤比例")
    ax.set_title("三个域的校准曲线：域越远，校准越差"); ax.legend(fontsize=7.5); ax.grid(alpha=.3)

    ax = axes[1]
    for name, y, p, col in sets:
        ax.hist(p, bins=25, histtype="step", lw=2, color=col, label=name.split("：")[1])
    ax.axvline(0.5, color="k", ls=":", lw=1)
    ax.set_xlabel("预测概率"); ax.set_ylabel("记录/窗数")
    ax.set_title("分数分布漂移（外部队列整体右偏）"); ax.legend(fontsize=8); ax.grid(alpha=.3)

    ax = axes[2]
    x = np.arange(len(tbl)); w = 0.27
    ax.bar(x - w, tbl["auroc"], w, label="AUROC", color="#0072B2")
    ax.bar(x, tbl["brier"], w, label="Brier（越低越好）", color="#D55E00")
    ax.bar(x + w, tbl["se_at_sp90"], w, label="Se@特异度90%", color="#009E73")
    for i, r in tbl.iterrows():
        ax.text(i - w, r.auroc + .01, f"{r.auroc:.2f}", ha="center", fontsize=7.5)
        ax.text(i, r.brier + .01, f"{r.brier:.2f}", ha="center", fontsize=7.5)
        ax.text(i + w, r.se_at_sp90 + .01, f"{r.se_at_sp90:.2f}", ha="center", fontsize=7.5)
    ax.set_xticks(x); ax.set_xticklabels(["内部\n德国12导", "外部1\n可穿戴", "外部2\n中国动态"], fontsize=8)
    ax.set_title("判别力小幅下降，校准与操作点大幅下降"); ax.legend(fontsize=8); ax.grid(alpha=.3, axis="y")

    plt.tight_layout()
    fig.savefig(OUT / "fig2_multidomain_calibration.png", dpi=600)
    fig.savefig(OUT / "fig2_multidomain_calibration.tiff", dpi=600, pil_kwargs={"compression": "tiff_lzw"})
    print("saved:", OUT / "fig2_multidomain_calibration.png")


if __name__ == "__main__":
    main()
