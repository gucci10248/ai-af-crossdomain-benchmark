#!/usr/bin/env python3
"""修复 08 结构（把摘要文本放回，供 Word 生成器读取）并同步修正生成器的切片标记。"""
import pathlib, re

ART = pathlib.Path("/Users/mac/Desktop/文稿库/人工智能临床应用")
KB = pathlib.Path("/Users/mac/Desktop/库/公共数据AF/code")

ABSTRACT = """**Aims.** Wearable and ambulatory algorithms detect atrial fibrillation with high accuracy when validated within the population and device they were developed for. Whether discrimination, calibration and thresholds survive a change of device, recording paradigm or population is unknown.

**Methods and results.** We harmonised three open cohorts onto one 30-second, single-lead task: atrial fibrillation versus non-atrial fibrillation. PTB-XL (Germany, 2,400 records), the PhysioNet/CinC Challenge 2017 cohort (consumer wearable, 2,537 records) and CPSC2021 (China, ambulatory, 583 windows from 25 patients). Models were developed on PTB-XL only. Internal discrimination was high (area under the receiver operating characteristic curve 0.974) with acceptable calibration (Brier score 0.069; expected calibration error 0.064). On external transfer to the wearable cohort, discrimination fell modestly (0.886) whereas calibration degraded three-fold (Brier 0.221; error 0.226) and sensitivity at 90% specificity fell from 0.940 to 0.596. Transfer to the Chinese cohort was better (0.947; 0.861). Most loss came from noisy segments (0.646; 0.199) rather than other rhythms or population. Recalibration repaired probabilities but not discrimination. At 1% prevalence, the external operating point yielded a positive predictive value of 2.7%, versus 66.1% for a validated algorithm with 99.5% specificity.

**Conclusion.** A model that appears deployable by discrimination alone can be clinically unusable after a change of device. External validation should report calibration, negative-class composition and operating-point transferability; deployment needs local recalibration, a target-specificity threshold and a signal-quality gate."""

KEYWORDS = "Keywords: atrial fibrillation; wearable devices; machine learning; external validation; calibration; screening"

p8 = ART / "08_投稿格式与投稿信.md"
s = p8.read_text()

# 取出现有 What's New 段落正文
m = re.search(r"## 三、What's New\?[^\n]*\n(.*?)\n## 四、", s, re.S)
whats_new_body = m.group(1).strip() if m else ""
if not whats_new_body:
    raise SystemExit("未找到 What's New 段")

# 用新结构替换：三 = 文字摘要（最终稿）；四 = What's New?
old_block_start = s.index("## 三、What's New?")
old_block_end = s.index("## 五、备用刊格式差异")
new_block = (
    "## 三、文字摘要（最终稿，带小标题；Europace 要求 text abstract with headings）\n\n"
    + ABSTRACT + "\n\n" + KEYWORDS + "\n\n"
    "（词数：含三个小标题 243 词、不含 239 词；Europace 对摘要无 250 词硬上限，此长度安全）\n\n"
    "## 四、What's New?（≤150 词，2–6 条，Europace 专用）\n\n" + whats_new_body + "\n\n"
    "（**已核对：5 条，116 词 ≤150 词**）\n\n"
)
s = s[:old_block_start] + new_block + s[old_block_end:]
p8.write_text(s)
print("08 结构已修复：三=摘要, 四=What's New")

# 修正生成器切片标记
pb = KB / "make_submission_docx.py"
b = pb.read_text()
b = b.replace('abst = section_slice(md8, "## 三、文字摘要（≤250 词，无缩写、无参考文献）", "## 四、关键词（6 个）")',
              'abst = section_slice(md8, "## 三、文字摘要（最终稿，带小标题；Europace 要求 text abstract with headings）", "## 四、What\'s New?")')
b = b.replace('kw_line = section_slice(md8, "## 四、关键词（6 个）", "## 五、封面信")\nkeywords = kw_line.strip().splitlines()[0].strip()',
              'kw_m = re.search(r"^Keywords:\\s*(.+)$", md8, re.M)\nkeywords = kw_m.group(1).strip()')
pb.write_text(b)
print("生成器标记已同步:", "三、文字摘要（最终稿" in b, "kw_m = re.search" in b)
