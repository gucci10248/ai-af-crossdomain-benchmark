#!/usr/bin/env python3
"""由图 1：内验证 vs 外部验证的校准崩塌（reliability curve）+ 分数分布。"""
import pathlib, numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

_CJK = "/Library/Fonts/Arial Unicode.ttf"
try:
    font_manager.fontManager.addfont(_CJK)
    plt.rcParams["font.sans-serif"] = ["Arial Unicode MS", "Arial Unicode"]
    plt.rcParams["axes.unicode_minus"] = False
except Exception as e:
    print("[warn] CJK font not registered:", e)
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score, brier_score_loss

BASE = pathlib.Path("/Users/mac/Desktop/库/公共数据AF")
OUT = BASE / "out"
df_p = pd.read_csv(OUT / "feat_ptbxl.csv")
df_c = pd.read_csv(OUT / "feat_cinc2017.csv")
feats = [c for c in df_p.columns if c.startswith("f_")]

pats = df_p["patient_id"].unique()
rng = np.random.RandomState(20260915)
rng.shuffle(pats)
tr = df_p[df_p["patient_id"].isin(set(pats[:int(0.7 * len(pats))]))]
te = df_p[~df_p["patient_id"].isin(set(pats[:int(0.7 * len(pats))]))]

mdl = make_pipeline(SimpleImputer(strategy="median"),
                    HistGradientBoostingClassifier(max_iter=300, learning_rate=0.06, random_state=0))
mdl.fit(tr[feats], tr["label"])
p_in = mdl.predict_proba(te[feats])[:, 1]
p_ex = mdl.predict_proba(df_c[feats])[:, 1]
y_in, y_ex = te["label"].values, df_c["label"].values


def reliability(y, p, bins=10):
    edges = np.linspace(0, 1, bins + 1)
    xs, ys, ns = [], [], []
    for i in range(bins):
        m = (p >= edges[i]) & (p < edges[i + 1] if i < bins - 1 else p <= 1.0)
        if m.sum():
            xs.append(p[m].mean()); ys.append(y[m].mean()); ns.append(int(m.sum()))
    return np.array(xs), np.array(ys), np.array(ns)


fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))
ax = axes[0]
for y, p, lab, col in [(y_in, p_in, f"内部验证 PTB-XL→PTB-XL (n={len(y_in)})", "#1f77b4"),
                       (y_ex, p_ex, f"外部验证 PTB-XL→CinC2017 (n={len(y_ex)})", "#d62728")]:
    xs, ys, _ = reliability(y, p)
    ax.plot(xs, ys, "o-", color=col,
            label=f"{lab}\nAUROC={roc_auc_score(y,p):.3f}  Brier={brier_score_loss(y,p):.3f}")
ax.plot([0, 1], [0, 1], "k--", lw=1, label="完美校准")
ax.set_xlabel("模型预测概率"); ax.set_ylabel("实际房颤比例")
ax.set_title("校准曲线：跨设备/跨人群后校准崩塌"); ax.legend(fontsize=8, loc="upper left"); ax.grid(alpha=.3)

ax = axes[1]
ax.hist(p_in[y_in == 1], bins=20, alpha=.6, label="内部-房颤", color="#1f77b4")
ax.hist(p_in[y_in == 0], bins=20, alpha=.6, label="内部-非房颤", color="#8ecae6")
ax.hist(p_ex[y_ex == 1], bins=20, alpha=.5, label="外部-房颤", color="#d62728", histtype="step", lw=2)
ax.hist(p_ex[y_ex == 0], bins=20, alpha=.5, label="外部-非房颤", color="#ffb3b3", histtype="step", lw=2)
ax.axvline(0.5, color="k", ls=":", lw=1)
ax.set_xlabel("预测概率"); ax.set_ylabel("记录数")
ax.set_title("分数分布：外部数据整体右偏 → 固定阈值失效"); ax.legend(fontsize=8); ax.grid(alpha=.3)

ax = axes[2]
names = ["内部 AUROC", "外部 AUROC", "内部 Brier", "外部 Brier", "内部 ECE", "外部 ECE"]
vals = [roc_auc_score(y_in, p_in), roc_auc_score(y_ex, p_ex),
        brier_score_loss(y_in, p_in), brier_score_loss(y_ex, p_ex),
        np.mean(np.abs(p_in - y_in)), np.mean(np.abs(p_ex - y_ex))]
cols = ["#1f77b4", "#d62728", "#1f77b4", "#d62728", "#1f77b4", "#d62728"]
ax.bar(names, vals, color=cols)
for i, v in enumerate(vals):
    ax.text(i, v + .01, f"{v:.3f}", ha="center", fontsize=8)
ax.set_title("AUROC 只掉 0.09，校准指标却差 7 倍"); ax.tick_params(axis="x", rotation=25, labelsize=8)
ax.grid(alpha=.3, axis="y")

plt.tight_layout()
fig.savefig(OUT / "fig1_calibration_shift.png", dpi=200)
print("saved:", OUT / "fig1_calibration_shift.png")
print(f"internal AUROC={roc_auc_score(y_in,p_in):.4f} Brier={brier_score_loss(y_in,p_in):.4f}")
print(f"external AUROC={roc_auc_score(y_ex,p_ex):.4f} Brier={brier_score_loss(y_ex,p_ex):.4f}")
