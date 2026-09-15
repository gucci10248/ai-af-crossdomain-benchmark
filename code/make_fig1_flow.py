#!/usr/bin/env python3
"""Fig 1：研究流程图（三个公开队列 → 标签统一 → 30 秒片段 → 患者级划分 → 三域评估）。
几何约束：所有箭头尾/头都落在框边界上；框之间不重叠（坐标显式计算）。
输出：out/fig1_flow.png
"""
import pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

_CJK = "/Library/Fonts/Arial Unicode.ttf"
try:
    font_manager.fontManager.addfont(_CJK)
    plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]
    plt.rcParams["axes.unicode_minus"] = False
except Exception:
    pass

OUT = pathlib.Path("/Users/mac/Desktop/库/公共数据AF/out")
C1, C2, C3, C4 = "#1f77b4", "#d62728", "#2ca02c", "#6a5acd"
BOX = dict(boxstyle="round,pad=0.35", linewidth=1.4)


def box(ax, x, y, w, h, text, color, fontsize=8.6, fc="white"):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                       linewidth=1.6, edgecolor=color, facecolor=fc, zorder=3)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize, zorder=4)
    return (x, y, w, h)


def arrow(ax, src, dst, color="black", label=None, lw=1.4, side="top"):
    """从 src 框指向 dst 框，箭头两端均落在框边界上。"""
    sx, sy, sw, sh = src
    dx, dy, dw, dh = dst
    if side == "top" and dy >= sy + sh:                 # dst 在上方
        p1 = (sx + sw / 2, sy + sh); p2 = (dx + dw / 2, dy)
    elif side == "bottom":
        p1 = (sx + sw / 2, sy); p2 = (dx + dw / 2, dy + dh)
    elif side == "right":
        p1 = (sx + sw, sy + sh / 2); p2 = (dx, dy + dh / 2)
    else:                                                # left
        p1 = (sx, sy + sh / 2); p2 = (dx + dw, dy + dh / 2)
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=13,
                                 color=color, lw=lw, zorder=2,
                                 connectionstyle="arc3,rad=0"))
    if label:
        ax.text((p1[0] + p2[0]) / 2 + 0.15, (p1[1] + p2[1]) / 2, label,
                fontsize=7.4, color=color, ha="left", va="center", zorder=5)


fig, ax = plt.subplots(figsize=(13.2, 7.4))
ax.set_xlim(0, 13.2); ax.set_ylim(0, 7.4); ax.axis("off")

# --- 顶层：三个公开队列 ---
b_ptb = box(ax, 0.35, 5.9, 3.9, 1.15,
            "PTB-XL 1.0.3（德国）\n12 导联 · 10 s · 取 I 导 100 Hz\nAF/AFL 1,200 + 匹配对照 1,200", C1)
b_c17 = box(ax, 4.65, 5.9, 3.9, 1.15,
            "CinC 2017（AliveCor 可穿戴）\n单导联 · ≤60 s\nAF 758 / 正常 1,000 / 其他 500 / 噪声 279", C2)
b_cps = box(ax, 8.95, 5.9, 3.9, 1.15,
            "CPSC2021（中国）\n动态 ECG 200 Hz · 4–106 min\n719 条记录 / 54 患者", C3)

# --- 第二层：标签统一 ---
b_harm = box(ax, 2.6, 4.05, 8.0, 1.0,
             "标签统一为「房颤（含房扑）vs 非房颤」\n"
             "PTB-XL: SCP AFIB/AFLT ｜ CinC2017: 官方 A/N/O/~（阴性类分三种口径）\n"
             "CPSC2021: .hea 诊断注释（non/persistent/paroxysmal AF）+ .atr 心律变迁注释", "#333333", fontsize=8.2)

# --- 第三层：片段化 + 划分 ---
b_seg = box(ax, 0.35, 2.35, 5.6, 1.15,
            "片段级任务\nPTB-XL / CinC2017：记录级（10–60 s）\n"
            "CPSC2021：切成不重叠 30 s 窗 → 583 窗 / 25 患者\n（剔除跨节律窗 130 个）", C4, fontsize=8.2)
b_split = box(ax, 6.45, 2.35, 6.4, 1.15,
              "患者级划分（防泄漏）\nPTB-XL 7:3 → 训练 1,685 / 内部测试 714\n"
              "CPSC2021：按患者分组 5 折（域内参照）\nCinC2017：无患者编号 → 记录级自助（已声明局限）", C4, fontsize=8.2)

# --- 第四层：模型 ---
b_model = box(ax, 2.6, 1.15, 8.0, 0.85,
              "模型仅用 PTB-XL 训练（外部域不参与调参）：31 维 HRV/频谱/波形特征 → LogReg 与 HistGradientBoosting",
              "#333333", fontsize=8.2)

# --- 第五层：评估输出 ---
b_eval = box(ax, 0.35, 0.15, 12.5, 0.72,
             "评估：AUROC / AUPRC ｜ Brier / ECE（校准）｜ 0.5 阈值与固定 90% 特异度操作点 ｜ "
             "决策曲线净获益 ｜ 重校准（温度缩放・等渗，源域 vs 目标域 oracle）｜ 聚类自助法 95% CI + 亚组",
             "#333333", fontsize=8.0)

# --- 箭头（两端均贴框边） ---
for b in (b_ptb, b_c17, b_cps):
    arrow(ax, b, b_harm, color="#555555", side="bottom")
arrow(ax, b_harm, b_seg, side="bottom")
arrow(ax, b_seg, b_split, side="right")
arrow(ax, b_seg, b_model, side="bottom")
arrow(ax, b_split, b_model, side="bottom")
arrow(ax, b_model, b_eval, side="bottom")

ax.text(0.35, 7.15, "Fig 1｜研究流程：三个公开队列 → 统一标签 → 片段级任务 → 患者级划分 → 跨域评估",
        fontsize=10.5, fontweight="bold")
ax.text(0.35, 0.02, "注：全部数据为公开库（PhysioNet 开放 / CC-BY），无院内或去标识患者数据。",
        fontsize=7.2, color="#666666")

fig.savefig(OUT / "fig1_flow.png", dpi=200, bbox_inches="tight")
print("saved:", OUT / "fig1_flow.png")
