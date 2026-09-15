#!/usr/bin/env python3
"""把"平衡抽样得到的灵敏度/特异度"换算成真实患病率下的 PPV / NPV（补上审稿人必问的一环）。

为什么必须做：本文三个域都是近 1:1 平衡抽样，阳性率 30–50% 是人为的。
临床场景里房颤患病率可能只有 1%（社区老年人筛查），此时特异度稍微不够，PPV 就会崩。

输入的操作点（Se, Sp）来自 out/table_domains.csv 与 out/table_ci.csv 的真实运行结果，
以及导师团队已发表算法（作为对照锚点，说明"为什么他们要把特异度做到 99%+"）。

输出：out/table_ppv_npv.md, out/fig5_ppv_npv.png
"""
import pathlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

_CJK = "/Library/Fonts/Arial Unicode.ttf"
try:
    font_manager.fontManager.addfont(_CJK)
    plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]
    plt.rcParams["axes.unicode_minus"] = False
except Exception:
    pass

BASE = pathlib.Path("/Users/mac/Desktop/库/公共数据AF")
OUT = BASE / "out"

# --- 操作点（Se, Sp, 来源） ---
OPS = [
    ("本研究 · 内部验证（PTB-XL，Se@Sp90）", 0.940, 0.900, "out/table_domains.csv"),
    ("本研究 · 外部1 可穿戴（0.5 阈值）", 0.941, 0.663, "out/table_domains.csv"),
    ("本研究 · 外部1 可穿戴（Se@Sp90）", 0.596, 0.900, "out/table_domains.csv"),
    ("本研究 · 外部1 严格 A vs N（Se@Sp90）", 0.877, 0.900, "out/table_ci.csv"),
    ("本研究 · 外部1 A vs 噪声（Se@Sp90）", 0.199, 0.900, "out/table_ci.csv"),
    ("本研究 · 中国域 CPSC2021（Se@Sp90）", 0.861, 0.900, "out/table_ci.csv"),
    ("对照锚点 · 导师团队 PACE 2024（间期级，消融人群）", 0.963, 0.995, "PACE 2024;47(4):511-517"),
    ("对照锚点 · 导师团队 Adv Sci 2026（双模态校正后）", 0.986, 0.9927, "Advanced Science 2026"),
    ("对照锚点 · 导师团队 JACC Clin EP 2026（间期级，728 例前瞻）", 0.9870, 0.9956, "JACC Clin Electrophysiol 2026; PMID 42283663"),
    ("对照锚点 · 导师团队 Heart Rhythm O2 2025（眼底 DL 外验 AUROC 0.773）", 0.773, 0.900, "Heart Rhythm O2 2025; PMID 40496585（按特异度 90% 假设）"),
]

PREV = [0.005, 0.01, 0.02, 0.05, 0.10, 0.20, 0.30, 0.50]


def ppv(se, sp, p):
    return se * p / (se * p + (1 - sp) * (1 - p))


def npv(se, sp, p):
    return sp * (1 - p) / (sp * (1 - p) + (1 - se) * p)


rows = []
for name, se, sp, src in OPS:
    for p in PREV:
        P = ppv(se, sp, p); N = npv(se, sp, p)
        rows.append({"operating_point": name, "prevalence": p, "se": se, "sp": sp,
                     "PPV": round(P, 4), "NPV": round(N, 4),
                     "LR+": round(se / (1 - sp), 2), "LR-": round((1 - se) / sp, 3),
                     "每检出1例需复核阳性例数": round(1 / P, 1) if P > 0 else np.nan,
                     "source": src})
tbl = pd.DataFrame(rows)
tbl.to_csv(OUT / "table_ppv_npv.csv", index=False)

# markdown 摘要（只保留 1% / 5% / 20% 三档，正文好引）
md = ["# 真实患病率下的 PPV / NPV 换算（来自平衡抽样的操作点）", "",
      "> 说明：以下 PPV/NPV 由真实运行得到的 Se/Sp 操作点按贝叶斯公式换算，**不是模型直接输出**。",
      "> 临床解读：**筛查场景（患病率低）里，PPV 几乎完全由特异度决定**；这也是导师团队把特异度做到 99%+ 的原因。", ""]
for p in (0.01, 0.05, 0.20):
    md.append(f"## 患病率 = {p:.0%}")
    md.append("| 操作点 | Se | Sp | PPV | NPV | LR+ | 每检出 1 例需复核阳性例数 |")
    md.append("|---|---|---|---|---|---|---|")
    sub = tbl[np.isclose(tbl["prevalence"], p)]
    for _, r in sub.iterrows():
        md.append(f"| {r['operating_point']} | {r['se']:.3f} | {r['sp']:.4f} | **{r['PPV']:.1%}** | "
                  f"{r['NPV']:.2%} | {r['LR+']} | {r['每检出1例需复核阳性例数']:.1f} |")
    md.append("")
md.append("## 结论要点")
md.append("1. 患病率 1% 时：特异度 90%（哪怕灵敏度 94%）只有 **约 9% 的 PPV**——每 11 个阳性里 10 个是假阳性；")
md.append("   而特异度 99.5% 可以把 PPV 抬到 **约 66%**。**筛查场景的真正瓶颈是特异度，不是灵敏度。**")
md.append("2. 本研究外部域在 0.5 固定阈值下特异度仅 0.663 → 低患病率下 PPV 不足 3%，说明跨设备沿用默认阈值会制造海量假阳性。")
md.append("3. 反过来，在中国动态 ECG 域（Se@Sp90 = 0.861）与内部验证水平接近，说明**校准/阈值本地化之后筛查是可行的**。")
(OUT / "table_ppv_npv.md").write_text("\n".join(md) + "\n")

# --- 图：PPV 随患病率变化 ---
fig, ax = plt.subplots(figsize=(10.5, 6))
prev_grid = np.logspace(np.log10(0.002), np.log10(0.6), 200)
styles = [("#1f77b4", "-"), ("#d62728", "--"), ("#d62728", "-"), ("#9467bd", "-."),
          ("#8c564b", ":"), ("#2ca02c", "-"), ("#ff7f0e", "-"), ("#e377c2", "--")]
for (name, se, sp, _), (col, ls) in zip(OPS, styles):
    ax.plot(prev_grid, [ppv(se, sp, p) * 100 for p in prev_grid], color=col, ls=ls, lw=2,
            label=f"{name}  (Se={se:.2f}, Sp={sp*100:.2f}%)")
ax.set_xscale("log")
ax.set_xlabel("房颤患病率（对数轴）"); ax.set_ylabel("阳性预测值 PPV (%)")
ax.set_title("筛查场景的真相：低患病率下 PPV 几乎只由特异度决定")
ax.axvline(0.01, color="gray", ls=":", lw=1); ax.text(0.0105, 92, "社区筛查 ~1%", fontsize=8, color="gray")
ax.axvline(0.20, color="gray", ls=":", lw=1); ax.text(0.21, 92, "高危门诊 ~20%", fontsize=8, color="gray")
ax.grid(alpha=.3); ax.legend(fontsize=7.6, loc="upper left"); ax.set_ylim(0, 100)
plt.tight_layout()
fig.savefig(OUT / "fig5_ppv_npv.png", dpi=200)
print("saved:", OUT / "fig5_ppv_npv.png")
print(tbl[tbl["prevalence"].isin([0.01, 0.05, 0.20])][
    ["operating_point", "prevalence", "se", "sp", "PPV", "NPV", "每检出1例需复核阳性例数"]].to_string(index=False))
