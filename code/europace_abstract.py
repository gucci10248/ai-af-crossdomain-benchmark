#!/usr/bin/env python3
"""按 Europace 要求把摘要改为 4 段式标题：Background and Aims / Methods / Results / Conclusion。"""
import pathlib, re

ART = pathlib.Path("/Users/mac/Desktop/文稿库/人工智能临床应用")
p8 = ART / "08_投稿格式与投稿信.md"
s = p8.read_text()

NEW_ABS = """**Background and Aims.** Wearable and ambulatory algorithms detect atrial fibrillation with high accuracy when validated within the population and device they were developed for. Whether discrimination, calibration and thresholds survive a change of device, recording paradigm or population is unknown.

**Methods.** We harmonised three open cohorts onto one 30-second, single-lead task (atrial fibrillation versus non-atrial fibrillation): PTB-XL (Germany, 2,400 records), the PhysioNet/CinC Challenge 2017 cohort (consumer wearable, 2,537 records) and CPSC2021 (China, ambulatory, 583 windows from 25 patients). Models were developed on PTB-XL only and evaluated for discrimination, calibration, operating-point transferability, post-hoc recalibration and decision-curve net benefit with cluster bootstrap confidence intervals.

**Results.** Internal discrimination was high (area under the receiver operating characteristic curve 0.974) with acceptable calibration (Brier score 0.069; expected calibration error 0.064). On external transfer to the wearable cohort, discrimination fell modestly (0.886) whereas calibration degraded three-fold (Brier 0.221; error 0.226) and sensitivity at 90% specificity fell from 0.940 to 0.596. Transfer to the Chinese cohort was better (0.947; 0.861). Most loss came from noisy segments (0.646; 0.199) rather than other rhythms or population. Recalibration repaired probabilities but not discrimination. At 1% prevalence, the external operating point yielded a positive predictive value of 2.7%, versus 66.1% for a validated algorithm with 99.5% specificity.

**Conclusion.** A model that appears deployable by discrimination alone can be clinically unusable after a change of device. External validation should report calibration, negative-class composition and operating-point transferability; deployment needs local recalibration, a target-specificity threshold and a signal-quality gate."""

start = s.index("**Background and Aims.**") if "**Background and Aims.**" in s else s.index("**Aims.**")
end = s.index("Keywords:", start)
s = s[:start] + NEW_ABS + "\n\n" + s[end:]
s = s.replace("（词数：含三个小标题 243 词、不含 239 词；Europace 对摘要无 250 词硬上限，此长度安全）",
              "（**Europace 要求摘要按下述 4 个标题分段：(1) Background and Aims, (2) Methods, (3) Results, (4) Conclusion；后接 3–6 个关键词——已按其官网原文调整。词数见下方核对。**）")
p8.write_text(s)

# 精确计数
sec = s.split("## 三、文字摘要（最终稿")[1].split("## 四、What's New?")[0]
lines = [l for l in sec.splitlines() if l.strip() and not l.strip().startswith("Keywords:") and not l.strip().startswith("（")]
txt = " ".join(lines)
words = len(txt.split())
print("摘要词数（含 4 个小标题）:", words, "| 不含标题:", words - 6, "| ≤250?", words <= 250)
