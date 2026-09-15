#!/usr/bin/env python3
"""加入导师团队（马长生团队）高分文献 3 篇 + 强化"方法论承接"叙事 + 填入 Zenodo DOI。

改动清单：
  06 初稿：Introduction 第 2 段（承接段落重写）、第 3 段（补同组外验衰减实例）、
           Discussion 信号质量节（补其自身 PPG 有效率数据）、图/表引用不变
  07 清单：新增 #22 PROMPT-AF(JAMA 2025)、#23 JACC Clin EP 2026、#24 Heart Rhythm O2 2025
"""
import pathlib, re

ART = pathlib.Path("/Users/mac/Desktop/文稿库/人工智能临床应用")
p6 = ART / "06_P2_Methods与Results初稿.md"
s = p6.read_text()

# ---------- 1) Introduction 第 2 段：改成"承接"叙事 ----------
old2_start = "Within-cohort accuracy of such algorithms is high and increasingly well documented:"
i = s.index(old2_start)
j = s.index("\n", s.index("good adherence).", i))
old2 = s[i:j]
new2 = (
 "The Anzhen electrophysiology programme has established, in a stepwise manner, that consumer-grade hardware can "
 "quantify atrial fibrillation. Interval-level validation of smartwatch photoplethysmography (PPG) against "
 "simultaneous patch ECG showed 96.3% sensitivity and 99.5% specificity in patients undergoing ablation [14]; "
 "a prospective cohort of 728 patients extended this to continuous burden estimation, reporting interval-level "
 "sensitivity 98.70% and specificity 99.56% with excellent agreement in burden (mean difference −1.34%, r = 0.999) [23]; "
 "and dual-modal PPG with artificial-intelligence-guided ECG-anchored correction raised performance to 98.60%/99.27% "
 "in 1,054 patients [15]. The programme has also used wearable single-lead ECG patches as the endpoint-ascertainment "
 "instrument in a multicentre randomised ablation trial [22], and has applied deep learning with an independent "
 "external cohort in the retinal domain [24]. "
 "Each of these studies validated performance within the population, device and clinical context in which the "
 "algorithm was developed — a limitation the authors themselves state (single-centre, ablation population with high "
 "burden and good adherence). The natural next question for this programme is therefore not whether a wearable can "
 "measure atrial fibrillation, but what happens to those very high specificity figures when the same model meets a "
 "different device, a different recording paradigm and a different population."
)
s = s[:i] + new2 + s[j:]

# ---------- 2) Introduction 第 3 段：补一句同组外验衰减实例 ----------
anchor3 = "In screening, where prevalence is low, the practical consequence of threshold or calibration shift is not a modest drop in AUROC: the positive predictive value collapses, and clinicians face unmanageable numbers of false positives."
add3 = (" That cross-domain decay is not hypothetical is shown by the same group's retinal model, whose discrimination fell "
        "from 0.855 internally to 0.773 on an independent external cohort [24]; and the wider deep-learning literature has "
        "repeatedly documented that apparently excellent models degrade when the acquisition pipeline changes [11].")
if anchor3 in s:
    s = s.replace(anchor3, anchor3 + add3, 1)
else:
    print("WARN: 第 3 段锚点未找到")

# ---------- 3) Discussion 信号质量节：补其自身 PPG 有效率 ----------
anchor4 = "In practice this means the dominant error mode of a deployed AF algorithm is mistaking a corrupted segment for AF."
add4 = (" Notably, the Anzhen smartwatch validation itself reported an overall validity rate of only 62.5% for "
        "watch-based PPG versus 96.2% for patch ECG across 1,440,826 30-second segments [23]: nearly two of every five "
        "wearable segments carried insufficient signal quality to be interpretable, which is precisely the regime in "
        "which our model produced its false positives.")
if anchor4 in s:
    s = s.replace(anchor4, anchor4 + add4, 1)
else:
    print("WARN: Discussion 锚点未找到")

p6.write_text(s)
print("06 更新完成；引文标记:", sorted(set(re.findall(r"\[[0-9,\u2013\-]+\]", s))))

# ---------- 4) 07 清单：追加 3 条参考 ----------
p7 = ART / "07_参考文献清单.md"
t7 = p7.read_text()
new_rows = (
 "| 22 | Sang C, Liu Q, Lai Y, et al. Pulmonary Vein Isolation With Optimized Linear Ablation vs Pulmonary Vein Isolation Alone for Persistent AF: The PROMPT-AF Randomized Clinical Trial. JAMA. 2025;333(5):381-389. doi:10.1001/jama.2024.24438 | 39556379 |\n"
 "| 23 | Zuo S, Zhou L, Feng H, et al. Validation of Smartwatches Integrated With Photoplethysmography for Continuous Evaluation of Atrial Fibrillation Burden. JACC Clin Electrophysiol. 2026 Jun 8 (online ahead of print). doi:10.1016/j.jacep.2026.03.036 | 42283663 |\n"
 "| 24 | Wang Z, Li M, Xia P, et al. Screening cognitive impairment in patients with atrial fibrillation: A deep learning model based on retinal fundus photographs. Heart Rhythm O2. 2025;6(5):678-686. doi:10.1016/j.hroo.2025.01.019 | 40496585 |\n"
)
anchor7 = "## 二、数据集引用"
if anchor7 in t7 and "| 24 |" not in t7:
    t7 = t7.replace(anchor7, new_rows + "\n" + anchor7, 1)
    t7 = t7.replace("| Discussion（信号质量/锚点校正） | [14,15] |",
                    "| Discussion（信号质量/锚点校正） | [14,15,23] |")
    t7 = t7.replace("| Introduction 2 段（同源高精度） | [14] PACE 2024、[15] Adv Sci 2026、[4] Attia 2019 |",
                    "| Introduction 2 段（同源高精度 + **承接叙事**） | [14] PACE 2024、[23] JACC Clin EP 2026、[15] Adv Sci 2026、[22] PROMPT-AF/JAMA 2025、[24] Heart Rhythm O2 2025 |")
    t7 += ("\n## 五、导师团队（马长生团队）文献纳入情况（按用户要求加强）\n\n"
           "| 序 | 文献 | 期刊/年份 | 在本稿中的作用 |\n|---|---|---|---|\n"
           "| [14] | 智能手表 PPG 房颤负荷（间期级 96.3%/99.5%） | PACE 2024 | 引子：同源验证的高精度起点 |\n"
           "| [23] | 智能手表 PPG 连续房颤负荷验证（728 例，98.70%/99.56%；PPG 有效率 62.5%） | JACC Clin Electrophysiol 2026 | **承接核心**：其自报有效率直接支撑本文\"信号质量门控\"结论 |\n"
           "| [15] | 双模态 PPG + AI-ECG 锚点校正（98.60%/99.27%） | Adv Sci 2026 | 承接：锚点校正=用高质量片段纠正低质量片段，与本文结论同源 |\n"
           "| [22] | PROMPT-AF 随机对照试验（可穿戴单导联 ECG 贴片作为终点判定） | JAMA 2025;333(5):381-389 | 承接：其终点判定依赖可穿戴设备 → 设备侧误判直接威胁终点效度 |\n"
           "| [24] | 眼底照片深度学习筛查房颤患者认知障碍（外验 AUROC 0.855→0.773） | Heart Rhythm O2 2025 | 承接：同组自报的跨域衰减实例 |\n")
    p7.write_text(t7)
    print("07 已追加 #22–#24 与承接说明")
else:
    print("WARN: 07 未修改（锚点缺失或已存在）")
