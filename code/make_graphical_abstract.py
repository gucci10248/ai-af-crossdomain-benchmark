#!/usr/bin/env python3
"""图形摘要（Graphical Abstract）——EHJ-Digital Health 要求提交（修回阶段必需）。

设计：三块信息，一个结论
  A 判别力 vs 校准：三域的 AUROC 与 ECE 对比（判别力小降、校准大降）
  B 操作点：固定 90% 特异度下的灵敏度（0.945 → 0.586 → 0.871）
  C 临床后果：患病率 1% 时的 PPV（本研究外部 2.8% vs 高特异度算法的 66.0%）
  底部 Take-home：外部验证要报校准/阴性类构成/操作点；部署需本地重校准 + 特异度目标 + 信号质量门控
字体：Arial（EHJ 接受 Helvetica/Arial）；数字取自 out/table_domains.csv 与 out/table_ppv_npv.csv（禁止手抄）
输出：out/graphical_abstract.png
"""
import csv
import pathlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Helvetica", "Arial", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = pathlib.Path("/Users/mac/Desktop/库/公共数据AF/out")
C_IN, C_EXT1, C_EXT2 = "#1f77b4", "#d62728", "#2ca02c"

# --- 数字全部从权威结果文件读取 ---
_dom = {r["domain"]: r for r in csv.DictReader(open(OUT / "table_domains.csv"))}
_k_in, _k_e1, _k_e2 = ("内部：PTB-XL（德国 12 导联）", "外部 1：CinC2017（消费级单导联）", "外部 2：CPSC2021（中国动态 ECG）")
auroc = [float(_dom[k]["auroc"]) for k in (_k_in, _k_e1, _k_e2)]
ece = [float(_dom[k]["ece"]) for k in (_k_in, _k_e1, _k_e2)]
se90 = [float(_dom[k]["se_at_sp90"]) for k in (_k_in, _k_e1, _k_e2)]

_ppv = list(csv.DictReader(open(OUT / "table_ppv_npv.csv")))
def _ppv_at(op, prev=0.01):
    r = next(x for x in _ppv if x["operating_point"] == op and abs(float(x["prevalence"]) - prev) < 1e-9)
    return float(r["PPV"]) * 100
ppv = [_ppv_at("本研究 · 外部1 可穿戴（0.5 阈值）"),
       _ppv_at("本研究 · 外部1 可穿戴（Se@Sp90）"),
       _ppv_at("对照锚点 · 导师团队 PACE 2024（间期级，消融人群）")]

domains = ["PTB-XL\n(Germany, 12-lead)", "Wearable cohort\n(single-lead)", "CPSC2021\n(China, ambulatory)"]
colors = [C_IN, C_EXT1, C_EXT2]

fig = plt.figure(figsize=(9.2, 12.4), dpi=200)
gs = fig.add_gridspec(3, 2, height_ratios=[1.0, 0.85, 0.62], hspace=0.55, wspace=0.35,
                      left=0.11, right=0.96, top=0.90, bottom=0.055)

fig.suptitle("Cross-device AF detection: discrimination survives, calibration and thresholds do not",
             fontsize=13.5, fontweight="bold", y=0.962)
fig.text(0.5, 0.933, "Three openly available cohorts, one 30-second single-lead task · models trained on PTB-XL only",
         ha="center", fontsize=9.2, color="#444444")

# --- A: AUROC vs ECE ---
ax = fig.add_subplot(gs[0, :])
x = np.arange(3); w = 0.34
b1 = ax.bar(x - w / 2, auroc, w, color=colors, label="AUROC (discrimination)")
b2 = ax.bar(x + w / 2, ece, w, color=colors, alpha=0.42, hatch="//", label="ECE (calibration error)")
for r, v in zip(b1, auroc):
    ax.text(r.get_x() + r.get_width() / 2, v + 0.02, f"{v:.3f}", ha="center", fontsize=9.5, fontweight="bold")
for r, v in zip(b2, ece):
    ax.text(r.get_x() + r.get_width() / 2, v + 0.02, f"{v:.3f}", ha="center", fontsize=9.5)
ax.annotate("", xy=(0.83, 0.30), xytext=(1.17, 0.30), arrowprops=dict(arrowstyle="<->", color="#555555", lw=1.2))
ax.text(1.0, 0.325, f"AUROC \u2212{auroc[0]-auroc[1]:.3f}\nyet ECE \u00d7{ece[1]/ece[0]:.1f}", ha="center", fontsize=9, color="#333333")
ax.set_xticks(x); ax.set_xticklabels(domains, fontsize=9.4)
ax.set_ylim(0, 1.22); ax.set_ylabel("Metric value", fontsize=9.4)
ax.set_title("A  Transfer penalty is hidden by AUROC", fontsize=10.6, loc="left", fontweight="bold")
ax.legend(fontsize=8.6, loc="upper right", frameon=False); ax.grid(alpha=0.25, axis="y")
ax.tick_params(labelsize=8.6)

# --- B: Se at 90% specificity ---
ax = fig.add_subplot(gs[1, :])
bars = ax.barh(range(3), se90, color=colors, height=0.5)
for i, v in enumerate(se90):
    ax.text(v + 0.012, i, f"{v:.3f}", va="center", fontsize=10, fontweight="bold")
ax.set_yticks(range(3)); ax.set_yticklabels([d.replace("\n", " ") for d in domains], fontsize=9.2)
ax.invert_yaxis(); ax.set_xlim(0, 1.06)
ax.set_xlabel("Sensitivity at a fixed 90% specificity", fontsize=9.4)
ax.set_title("B  At the clinically used operating point, a third of sensitivity is lost", fontsize=10.6, loc="left", fontweight="bold")
ax.grid(alpha=0.25, axis="x"); ax.tick_params(labelsize=8.6)

# --- C: PPV at 1% prevalence ---
ax = fig.add_subplot(gs[2, :])
labels = ["This study\nexternal, default 0.5 threshold", "This study\nexternal, Se@Sp90", "Validated algorithm\n99.5% specificity"]
cols = [C_EXT1, "#9467bd", "#ff7f0e"]
bars = ax.bar(range(3), ppv, color=cols, width=0.5)
for i, v in enumerate(ppv):
    ax.text(i, v + 1.5, f"{v:.1f}%", ha="center", fontsize=10, fontweight="bold")
ax.set_xticks(range(3)); ax.set_xticklabels(labels, fontsize=8.4)
ax.set_ylabel("PPV at 1% prevalence", fontsize=9.4); ax.set_ylim(0, 80)
ax.set_title("C  At screening prevalence, specificity decides everything", fontsize=10.6, loc="left", fontweight="bold")
ax.grid(alpha=0.25, axis="y"); ax.tick_params(labelsize=8.6)

# --- Take-home box ---
fig.text(0.5, 0.022,
         "Take-home:  external validation must report calibration, negative-class composition and operating-point transferability;\n"
         "most cross-device error came from noisy segments, not other rhythms or populations — deployment needs local recalibration,\n"
         "a target-specificity threshold and a signal-quality gate.",
         ha="center", va="bottom", fontsize=9.0, color="#111111",
         bbox=dict(boxstyle="round,pad=0.6", facecolor="#f2f6fb", edgecolor="#4a6fa5", linewidth=1.2))

fig.savefig(OUT / "graphical_abstract.png", dpi=200, bbox_inches="tight")
print("saved:", OUT / "graphical_abstract.png")
