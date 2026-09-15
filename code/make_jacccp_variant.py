#!/usr/bin/env python3
"""生成 JACC: Clinical Electrophysiology 变体（备用刊）：
  - 结构化五段摘要（Background / Objectives / Methods / Results / Conclusions，≤250 词）
  - Condensed Abstract（≤100 词，强调临床意义）
  - Clinical Perspectives（必需）
  - Central Illustration（必需；以图形摘要承担）
  - **美式拼写**（JACC 要求 American spelling，与 Europace 版相反）
输出：P2_manuscript_JACCCEP_v0.1.docx
"""
import pathlib, re
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

ART = pathlib.Path("/Users/mac/Desktop/文稿库/人工智能临床应用")
DOC6, DOC7, DOC8 = ART / "06_P2_Methods与Results初稿.md", ART / "07_参考文献清单.md", ART / "08_投稿格式与投稿信.md"
TITLE = ("Calibration Collapse in Cross-Population Atrial Fibrillation Detection: "
         "A Multi-Dataset Benchmark of Diagnostic Performance, Calibration and Operating-Point Transferability")

US = [("randomised","randomized"),("analysed","analyzed"),("analyse","analyze"),("harmonised","harmonized"),
      ("summarised","summarized"),("localised","localized"),("normalised","normalized"),("characterised","characterized"),
      ("labelled","labeled"),("labelling","labeling"),("modelling","modeling"),("centre","center"),("centres","centers"),
      ("artefact","artifact"),("behaviour","behavior"),("favour","favor"),("utilised","utilized"),("minimised","minimized")]

def us(t):
    for a, b in US:
        t = re.sub(r"\b" + a + r"\b", b, t)
        t = re.sub(r"\b" + a.capitalize() + r"\b", b.capitalize(), t)
    return t

def base_doc():
    d = Document()
    st = d.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(12)
    st.paragraph_format.line_spacing = 2.0; st.paragraph_format.space_after = Pt(0)
    for s in d.sections:
        s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Cm(2.5)
    return d

def H(d, text, size=13, level=1):
    p = d.add_paragraph(); r = p.add_run(text); r.bold = True; r.font.size = Pt(size)
    p.paragraph_format.space_before = Pt(10); p.paragraph_format.space_after = Pt(4); return p

def B(d, text):
    p = d.add_paragraph()
    for i, chunk in enumerate(re.split(r"\*\*(.+?)\*\*", text)):
        if chunk:
            r = p.add_run(chunk)
            if i % 2 == 1: r.bold = True
    return p

md6, md7 = DOC6.read_text(), DOC7.read_text()
intro = md6.split("## INTRODUCTION（英文正稿）")[1].split("## METHODS（英文正稿）")[0]
methods = md6.split("## METHODS（英文正稿）")[1].split("## RESULTS（英文正稿）")[0]
results = md6.split("## RESULTS（英文正稿）")[1].split("## DISCUSSION（英文正稿）")[0]
disc = md6.split("## DISCUSSION（英文正稿）")[1].split("## 中文工作注")[0]
refmap = {}
for m in re.finditer(r"^\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*([^|]*)\|\s*$", md7, re.M):
    if not m.group(2).strip().startswith("完整著录"):
        refmap[int(m.group(1))] = m.group(2).strip()

ABSTRACT5 = """Background. Wearable and ambulatory algorithms detect atrial fibrillation with high accuracy when validated within the population and device used for development, but external validation is usually summarized by discrimination alone.

Objectives. We tested whether discrimination, calibration and decision thresholds survive a change of device, recording paradigm and population.

Methods. Three open cohorts were harmonized onto one 30-second, single-lead task (atrial fibrillation versus non-atrial fibrillation): PTB-XL (Germany, 2,400 records), the PhysioNet/CinC Challenge 2017 cohort (consumer wearable, 2,537 records) and CPSC2021 (China, ambulatory, 583 windows from 25 patients). Models were developed on PTB-XL only and evaluated for discrimination, calibration, operating-point transferability, recalibration and decision-curve net benefit, with cluster bootstrap confidence intervals.

Results. Internal discrimination was high (area under the receiver operating characteristic curve 0.974) with acceptable calibration (Brier score 0.069; expected calibration error 0.064). On transfer to the wearable cohort, discrimination fell modestly (0.886) whereas calibration degraded threefold (Brier 0.221; error 0.226) and sensitivity at 90% specificity fell from 0.940 to 0.596. Transfer to the Chinese cohort was better (0.947; 0.861). Most loss came from noisy segments (0.646; 0.199) rather than other rhythms or population. Recalibration repaired probabilities but not discrimination. At 1% prevalence the external operating point yielded a positive predictive value of 2.7%, versus 66.1% for an algorithm validated at 99.5% specificity.

Conclusions. A model that appears deployable by discrimination alone can be clinically unusable after a change of device; external validation should report calibration, negative-class composition and operating-point transferability."""

CONDENSED = """In three openly available cohorts harmonized onto one 30-second single-lead task, transferring an atrial fibrillation detection model from a clinical 12-lead dataset to a consumer wearable cohort left discrimination almost intact (area under the curve 0.974 to 0.886) while calibration error tripled and sensitivity at 90% specificity fell from 0.940 to 0.596. Most false positives came from noisy segments. At 1% prevalence, the resulting positive predictive value was 2.7%, against 66.1% for an algorithm validated at 99.5% specificity, so device change, not population change, is what breaks screening performance."""

d = base_doc()
p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run(TITLE); r.bold = True; r.font.size = Pt(15)
for line in ["Jinkai Guo, MD Candidate; Hua Chen, MD, PhD",
             "Department of Cardiology, Inner Mongolia Autonomous Region People's Hospital, Hohhot 010017, China",
             "ORCID: Jinkai Guo 0009-0000-2455-0486; Hua Chen 0000-0001-9140-5019",
             "Running title: Cross-device AF detection: calibration collapse",
             "Corresponding author: Hua Chen, MD, PhD. Email: Zxcv8521@163.com",
             "Word count (introduction to conclusion, incl. references and figure legends): ~3,300 | Figures: 5 | Tables: 5 | References: 24 | Central Illustration: 1 (required)"]:
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rr = p.add_run(us(line)); rr.font.size = Pt(10.5)

H(d, "Abstract", 13)
for para in [x.strip() for x in ABSTRACT5.split("\n\n")]:
    B(d, us(para))
B(d, us("Keywords: atrial fibrillation; wearable devices; machine learning; external validation; calibration; screening"))
H(d, "Condensed Abstract", 12)
B(d, us(CONDENSED))
H(d, "Clinical Perspectives", 12)
B(d, us("Competency in medical knowledge: discrimination metrics from a single development cohort do not bound the clinical behaviour of an atrial fibrillation detection algorithm after a device or platform change; calibration and the specificity at the deployed operating point must be re-established locally."))
B(d, us("Translational outlook: before wearable atrial fibrillation screening is scaled, models should be paired with a signal-quality gate and a target-specificity threshold fitted on the deployment platform, and screening programmes should report positive predictive value at the intended prevalence rather than area under the curve alone."))
H(d, "Central Illustration", 12)
B(d, us("Central Illustration: cross-device calibration collapse and its clinical consequence. Left, discrimination (AUROC) and calibration error (ECE) in the development cohort and in the consumer wearable cohort; middle, sensitivity at a fixed 90% specificity; right, positive predictive value at 1% prevalence for the measured operating point and for a high-specificity validated algorithm. (File: graphical_abstract.png; replace with a purpose-drawn Central Illustration at revision.)"))

for sec_title, body_text in [("Introduction", intro), ("Methods", methods), ("Results", results), ("Discussion", disc)]:
    H(d, sec_title, 13)
    for para in [x.strip() for x in body_text.split("\n") if x.strip()]:
        if para.startswith("###"):
            H(d, us(re.sub(r"^###\s*", "", para)), 12)
        else:
            B(d, us(para.replace("`", "")))

H(d, "References", 13)
for k in sorted(refmap):
    B(d, f"{k}. {refmap[k]}")

out = ART / "P2_manuscript_JACCCEP_v0.1.docx"
d.save(out)
aw = len(us(ABSTRACT5).split()); cw = len(us(CONDENSED).split())
print("saved:", out)
print("结构化摘要词数:", aw, "| ≤250?", aw <= 250, "| Condensed:", cw, "| ≤100?", cw <= 100)
