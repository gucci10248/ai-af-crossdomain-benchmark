#!/usr/bin/env python3
"""方法学模块 3：**聚类自助法 95% 置信区间 + 亚组/阴性类构成分析**（审稿人必问的那部分）。

覆盖：
  1) 各域主指标（AUROC / Brier / ECE / Se@Sp90）的 95% CI
     - PTB-XL、CPSC2021 有患者编号 → **按患者聚类**自助（同一患者的记录/窗一起抽）
     - CinC2017 无患者编号 → 记录级自助（在正文中作为局限说明）
  2) 阴性类构成分析：CinC2017 把"其他节律(O)"与"噪声(~)"分别作为阴性时，性能如何变化
  3) 亚组：PTB-XL 按性别/年龄段；CPSC2021 按诊断类型（nonAF / persistentAF / paroxysmalAF）
输出：out/table_ci.csv, out/table_subgroups.csv, out/fig4_forest.png
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
B = 1000


def ece(y, p, bins=10):
    edges = np.linspace(0, 1, bins + 1); e = 0.0
    for i in range(bins):
        m = (p >= edges[i]) & (p < edges[i + 1] if i < bins - 1 else p <= 1.0)
        if m.sum():
            e += m.sum() / len(y) * abs(p[m].mean() - y[m].mean())
    return float(e)


def se_at_spec(y, p, spec=0.90):
    neg = p[y == 0]
    if len(neg) < 5:
        return np.nan
    thr = np.quantile(neg, spec)
    return float(((p >= thr) & (y == 1)).sum() / max(1, (y == 1).sum()))


def spec_at_thr(y, p, thr=0.5):
    neg = y == 0
    return float(((p < thr) & neg).sum() / max(1, neg.sum()))


METRICS = {
    "AUROC": lambda y, p: roc_auc_score(y, p) if len(set(y)) > 1 else np.nan,
    "Brier": lambda y, p: brier_score_loss(y, np.clip(p, 0, 1)),
    "ECE": lambda y, p: ece(y, np.clip(p, 0, 1)),
    "Se@Sp90": lambda y, p: se_at_spec(y, p, 0.90),
    "Sp@0.5": lambda y, p: spec_at_thr(y, p, 0.5),
}


def cluster_bootstrap(y, p, clusters, metrics, B=B, seed=SEED):
    rng = np.random.RandomState(seed)
    uniq = np.unique(clusters)
    idx_by_cluster = {c: np.where(clusters == c)[0] for c in uniq}
    point = {k: f(y, p) for k, f in metrics.items()}
    draws = {k: [] for k in metrics}
    for _ in range(B):
        pick = rng.choice(uniq, size=len(uniq), replace=True)
        idx = np.concatenate([idx_by_cluster[c] for c in pick])
        yy, pp = y[idx], p[idx]
        if len(set(yy)) < 2:
            continue
        for k, f in metrics.items():
            try:
                draws[k].append(f(yy, pp))
            except Exception:
                pass
    ci = {}
    for k in metrics:
        arr = np.array([v for v in draws[k] if np.isfinite(v)])
        ci[k] = (float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))) if len(arr) > 20 else (np.nan, np.nan)
        ci[k + "_point"] = float(point[k])
    return ci


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

    p_in = mdl.predict_proba(te[feats])[:, 1]
    p_c = mdl.predict_proba(df_c[feats])[:, 1]
    p_x = mdl.predict_proba(df_x[feats])[:, 1]
    y_in, y_c, y_x = te["label"].values, df_c["label"].values, df_x["label"].values

    rows = []
    jobs = [
        ("内部：PTB-XL（德国12导）", y_in, p_in, te["patient_id"].values),
        ("外部1：CinC2017 全部（A vs 非A）", y_c, p_c, df_c["rec_id"].values),
        ("外部2：CPSC2021（中国，30秒窗）", y_x, p_x, df_x["patient"].values),
    ]
    # 阴性类构成：把 O / ~ 分别作为阴性（正类恒为 A）
    for tag, keep in [("外部1a：仅 A vs N", ["A", "N"]),
                      ("外部1b：A vs O（其他节律）", ["A", "O"]),
                      ("外部1c：A vs 噪声(~)", ["A", "~"])]:
        m = df_c["label_raw"].isin(keep).values
        y2 = (df_c["label_raw"].values == "A").astype(int)[m]
        jobs.append((tag, y2, p_c[m], df_c["rec_id"].values[m]))

    for tag, y, p, cl in jobs:
        ci = cluster_bootstrap(y, p, cl, METRICS)
        row = {"group": tag, "n": len(y), "pos": int(y.sum()), "pos_rate": float(y.mean())}
        for k in METRICS:
            row[f"{k}"] = ci[f"{k}_point"]; row[f"{k}_lo"] = ci[k][0]; row[f"{k}_hi"] = ci[k][1]
        rows.append(row)
        print(f"{tag:34s} n={row['n']:5d} AUROC={row['AUROC']:.3f}[{row['AUROC_lo']:.3f},{row['AUROC_hi']:.3f}] "
              f"Se@Sp90={row['Se@Sp90']:.3f}[{row['Se@Sp90_lo']:.3f},{row['Se@Sp90_hi']:.3f}] "
              f"Brier={row['Brier']:.3f} Sp@0.5={row['Sp@0.5']:.3f}")

    # 亚组
    sub_rows = []
    # PTB-XL 性别 / 年龄
    te2 = te.copy(); te2["p_in"] = p_in
    for key, label in [("sex", "性别"), ("age_band", "年龄段")]:
        for val in sorted(te2[key].dropna().unique()):
            m = (te2[key] == val).values
            if m.sum() < 40 or te2.loc[m, "label"].nunique() < 2:
                continue
            ci = cluster_bootstrap(te2.loc[m, "label"].values, te2.loc[m, "p_in"].values,
                                   te2.loc[m, "patient_id"].values, METRICS)
            sub_rows.append({"group": f"PTB-XL 内部 · {label}={val}", "n": int(m.sum()),
                             "AUROC": ci["AUROC_point"], "AUROC_lo": ci["AUROC"][0], "AUROC_hi": ci["AUROC"][1],
                             "Se@Sp90": ci["Se@Sp90_point"], "Se@Sp90_lo": ci["Se@Sp90"][0], "Se@Sp90_hi": ci["Se@Sp90"][1],
                             "Brier": ci["Brier_point"], "Sp@0.5": ci["Sp@0.5_point"]})
    # CPSC2021 诊断类型
    df_x2 = df_x.copy(); df_x2["p_x"] = p_x
    for dx in sorted(df_x2["dx"].unique()):
        m = (df_x2["dx"] == dx).values
        if m.sum() < 40 or df_x2.loc[m, "label"].nunique() < 2:
            continue
        ci = cluster_bootstrap(df_x2.loc[m, "label"].values, df_x2.loc[m, "p_x"].values,
                               df_x2.loc[m, "patient"].values, METRICS)
        sub_rows.append({"group": f"中国域 · {dx}", "n": int(m.sum()),
                         "AUROC": ci["AUROC_point"], "AUROC_lo": ci["AUROC"][0], "AUROC_hi": ci["AUROC"][1],
                         "Se@Sp90": ci["Se@Sp90_point"], "Se@Sp90_lo": ci["Se@Sp90"][0], "Se@Sp90_hi": ci["Se@Sp90"][1],
                         "Brier": ci["Brier_point"], "Sp@0.5": ci["Sp@0.5_point"]})

    pd.DataFrame(rows).to_csv(OUT / "table_ci.csv", index=False)
    subs = pd.DataFrame(sub_rows)
    subs.to_csv(OUT / "table_subgroups.csv", index=False)
    print("\n亚组：")
    print(subs.to_string(index=False))

    # ---- Fig 4：森林图（AUROC 与 Se@Sp90，含 95% CI）----
    allrows = pd.concat([pd.DataFrame(rows), subs], ignore_index=True)
    fig, axes = plt.subplots(1, 2, figsize=(14, 0.42 * len(allrows) + 2), sharey=True)
    ypos = np.arange(len(allrows))[::-1]
    for ax, metric, title in [(axes[0], "AUROC", "AUROC（95% CI，聚类自助法）"),
                              (axes[1], "Se@Sp90", "特异度 90% 下的灵敏度（95% CI）")]:
        for yy, (_, r) in zip(ypos, allrows.iterrows()):
            col = "#1f77b4" if r["group"].startswith("内部") or "内部" in r["group"] else \
                  ("#2ca02c" if (r["group"].startswith("中国") or "中国域" in r["group"]) else "#d62728")
            ax.errorbar(r[metric], yy, xerr=[[r[metric] - r[f"{metric}_lo"]], [r[f"{metric}_hi"] - r[metric]]],
                        fmt="o", color=col, capsize=3, lw=1.5, ms=5)
            ax.text(1.01, yy, f"{r[metric]:.3f} [{r[f'{metric}_lo']:.2f},{r[f'{metric}_hi']:.2f}]",
                    transform=ax.get_yaxis_transform(), va="center", fontsize=7.5)
        ax.set_title(title); ax.grid(alpha=.3, axis="x"); ax.set_xlim(0.2, 1.05)
    axes[0].set_yticks(ypos)
    axes[0].set_yticklabels([f"{r['group']}  (n={r['n']})" for _, r in allrows.iterrows()], fontsize=8)
    plt.tight_layout()
    fig.savefig(OUT / "fig4_forest.png", dpi=200)
    print("\nsaved:", OUT / "fig4_forest.png")


if __name__ == "__main__":
    main()
