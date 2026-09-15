#!/usr/bin/env python3
"""补齐 5 条"列表有、正文未引"的参考文献（[4] [7] [8] [12] [18]），使引用与列表完全对齐。"""
import pathlib

p6 = pathlib.Path("/Users/mac/Desktop/文稿库/人工智能临床应用/06_P2_Methods与Results初稿.md")
s = p6.read_text()
n = 0

# 1) Methods 队列清单第 2 条：补会议论文 [12]
a = "2. **PhysioNet/Computing in Cardiology Challenge 2017 (consumer wearable)** — 12,186 single-lead AliveCor recordings of up to 60 seconds."
b = ("2. **PhysioNet/Computing in Cardiology Challenge 2017 (consumer wearable)** [12,20] — 12,186 single-lead "
     "AliveCor recordings of up to 60 seconds.")
if a in s: s = s.replace(a, b, 1); n += 1

# 2) Introduction：补 Attia 2019 [4]
a2 = "Atrial fibrillation (AF) affects an estimated 1-2% of the general population" if "1-2%" in s else "Atrial fibrillation (AF) affects an estimated 1–2% of the general population"
anchor = "and machine-learning algorithms now underpin rhythm classification in that setting [1–3]."
add = (" Artificial intelligence applied to the conventional 12-lead electrocardiogram can even identify patients with a "
       "history of atrial fibrillation while they are in sinus rhythm [4], which raises the possibility of opportunistic "
       "screening without documented rhythm.")
if anchor in s: s = s.replace(anchor, anchor + add, 1); n += 1

# 3) Discussion：补 mAFA-II [7,8] 与消融终点/监测模态 [18,22]
anchor2 = "For randomized evaluations of AI-supported AF care"
if anchor2 in s:
    add2 = ("Experience from mobile-health integrated-care trials in China indicates that digital tools improve outcomes "
            "when the intervention bundles a care pathway rather than a device alone [7,8], and randomised ablation "
            "trials define success through rhythm documentation, so the monitoring modality becomes part of the endpoint "
            "itself [18,22]. ")
    s = s.replace(anchor2, add2 + anchor2, 1); n += 1

p6.write_text(s)
print("已补引文处数:", n)
