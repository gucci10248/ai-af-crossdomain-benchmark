#!/usr/bin/env python3
"""sci-humanizer 去 AI 味（保科学限定、不动数字与引文）：
  ① 破折号 19 → ≤4（改逗号/分号/括号/拆句）
  ② 去掉正文内联加粗（数字与短语），只留章节标题
  ③ 去掉 2 处 AI 味词（state-of-the-art / moreover）
  ④ 为"流行病学与惯例"类断言补官方源头引用（[1] ESC 2024 指南；[9] TRIPOD+AI）
不修改任何数字、单位、引文编号与参考文献列表。
"""
import pathlib, re

ART = pathlib.Path("/Users/mac/Desktop/文稿库/人工智能临床应用")
p6 = ART / "06_P2_Methods与Results初稿.md"
s = p6.read_text()
eng_start, eng_end = s.index("## INTRODUCTION（英文正稿）"), s.index("## 中文工作注")
eng = s[eng_start:eng_end]
orig_em = eng.count("—")

REPL = [
 # 1) 流行病学断言 → 补 ESC 2024 指南引用，并去掉"三分之一"这一无法溯源的表述
 ("Atrial fibrillation (AF) affects an estimated 1–2% of the general population and a substantially higher proportion "
  "of older adults, and it is a leading preventable cause of cardioembolic stroke and heart failure. Because a third "
  "of AF is asymptomatic and paroxysmal, detection has moved out of the clinic into consumer wearables and long-term "
  "ambulatory monitoring, and machine-learning algorithms now underpin rhythm classification in that setting [1–3].",
  "Atrial fibrillation (AF) affects an estimated 1–2% of the general population and a substantially higher proportion "
  "of older adults, and it is a leading preventable cause of cardioembolic stroke and heart failure [1]. Because AF is "
  "frequently asymptomatic and paroxysmal [1], detection has moved out of the clinic into consumer wearables and "
  "long-term ambulatory monitoring, where machine-learning algorithms now underpin rhythm classification [1–3]."),
 # 2) "dominant practice" 断言 → 改为可溯源的表述 + TRIPOD+AI 引用
 ("The dominant practice in the literature is to report a single discrimination metric (usually AUROC) from external "
  "validation. Discrimination, however, is invariant to monotone transformations of the score and therefore says "
  "nothing about whether predicted probabilities remain usable [9,11], nor whether a threshold chosen in the "
  "development cohort retains its sensitivity/specificity elsewhere.",
  "External validation in this field is frequently summarised by a single discrimination metric, usually AUROC, "
  "although reporting guidance requires calibration as well [9]. Discrimination is invariant to monotone "
  "transformations of the score and therefore says nothing about whether predicted probabilities remain usable [9,11], "
  "nor whether a threshold chosen in the development cohort retains its sensitivity/specificity elsewhere."),
 # 3) 破折号 → 拆句（承接段）
 ("Each of these studies validated performance within the population, device and clinical context in which the "
  "algorithm was developed — a limitation the authors themselves state (single-centre, ablation population with high "
  "burden and good adherence).",
  "Each of these studies validated performance within the population, device and clinical context in which the "
  "algorithm was developed. The authors themselves state this limitation (single-centre, ablation population with "
  "high burden and good adherence)."),
 # 4) 三队列列举：破折号 → 冒号 + 拆句
 ("We therefore assembled three openly available cohorts that differ simultaneously in country, device and recording "
  "paradigm — PTB-XL (Germany, clinical 12-lead), the PhysioNet/CinC Challenge 2017 cohort (consumer single-lead, "
  "AliveCor) and CPSC2021 (China, long-duration ambulatory/wearable ECG) — and harmonized them onto a single "
  "30-second, single-lead, segment-level AF-versus-non-AF task.",
  "We therefore assembled three openly available cohorts differing simultaneously in country, device and recording "
  "paradigm: PTB-XL (Germany, clinical 12-lead), the PhysioNet/CinC Challenge 2017 cohort (consumer single-lead, "
  "AliveCor) and CPSC2021 (China, long-duration ambulatory or wearable ECG). These were harmonized onto a single "
  "30-second, single-lead, segment-level AF-versus-non-AF task."),
 # 5) 队列条目里的破折号 → 冒号（同时去加粗）
 ("1. **PTB-XL v1.0.3 (Germany)** —", "1. PTB-XL v1.0.3 (Germany):"),
 ("2. **PhysioNet/Computing in Cardiology Challenge 2017 (consumer wearable)** [12,20] —",
  "2. PhysioNet/Computing in Cardiology Challenge 2017 (consumer wearable) [12,20]:"),
 ("3. **CPSC2021 (China, ambulatory)** —", "3. CPSC2021 (China, ambulatory):"),
 # 6) 患病率换算处的破折号 → 逗号
 ("at a 1% prevalence — typical of community screening — the internal",
  "at a 1% prevalence, typical of community screening, the internal"),
 # 7) "specificity — not sensitivity —" → 逗号
 ("which is why specificity — not sensitivity — is the binding constraint",
  "which is why specificity, not sensitivity, is the binding constraint"),
 # 8) 中国队列处的破折号 → 定语从句
 ("The observation that a Chinese ambulatory cohort — differing in country, ethnicity and recording system — "
  "transferred better",
  "The observation that a Chinese ambulatory cohort, which differed in country, ethnicity and recording system, "
  "transferred better"),
 # 9) 信号质量门控处的破折号 → 括号
 ("a **signal-quality gate** — or, equivalently, an anchor-based correction scheme in which high-confidence segments "
  "are used to adjudicate low-confidence ones — is a prerequisite",
  "a signal-quality gate (equivalently, an anchor-based correction scheme in which high-confidence segments "
  "adjudicate low-confidence ones) is a prerequisite"),
 # 10) 操作点处的破折号 → 逗号
 ("showing that the operating point — not detection accuracy alone — determines clinical value",
  "showing that the operating point, not detection accuracy alone, determines clinical value"),
 # 11) 临床不可行处的破折号 → 拆句
 ("translates directly into clinical infeasibility — which is the quantitative argument for",
  "translates directly into clinical infeasibility. That is the quantitative argument for"),
 # 12) AI 试验处的破折号 → 逗号
 ("For randomized evaluations of AI-supported AF care — an area with an expanding trial pipeline [16] and evolving "
  "statements on integration into electrophysiology workflows — the same logic implies",
  "For randomized evaluations of AI-supported AF care, an area with an expanding trial pipeline [16] and evolving "
  "statements on integration into electrophysiology workflows, the same logic implies"),
 # 13) moreover → 拆句
 ("; moreover, because the detector itself defines episode duration and burden, the endpoint definition must be fixed "
  "independently of the algorithm under test [17].",
  ". The detector also defines episode duration and burden, so the endpoint definition must be fixed independently of "
  "the algorithm under test [17]."),
 # 14) state-of-the-art → 精确表述
 ("absolute performance is below state-of-the-art within-cohort results",
  "absolute performance is below the best reported within-cohort results"),
]

missing = []
for a, b in REPL:
    if a in s:
        s = s.replace(a, b, 1)
    else:
        missing.append(a[:70])

# 统一去掉正文（英文部分）内联加粗：**xxx** → xxx
s2_head = s[:eng_start]
eng2 = s[eng_start:eng_end]
eng2_noB = re.sub(r"\*\*(.+?)\*\*", r"\1", eng2)
s = s2_head + eng2_noB + s[eng_end:]
p6.write_text(s)

new_eng = s[eng_start:s.index("## 中文工作注")]
print("替换失败条目:", missing if missing else "无")
print("破折号:", orig_em, "→", new_eng.count("—"))
print("内联加粗剩余:", len(re.findall(r"\*\*", new_eng)), "（应为 0）")
print("数字总数（核对未丢失）:", len(re.findall(r"\d+\.\d+", new_eng)))
