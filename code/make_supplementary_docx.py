#!/usr/bin/env python3
"""生成补充材料（Supplementary Materials）Word 文件。

内容：
  Table S1  亚组结果（性别 / 年龄段 / 中国域 paroxismal 窗），含聚类自助法 95% CI
  Table S2  完整重校准结果（两个外部域 × 未校准/源域温度/目标域温度/源域等渗/目标域等渗）
  Table S3  实现细节（特征清单、模型超参、随机种子、各域样本量与标签构成、剔除与缺失）
  Legends   主文 Fig 1–5、Table 1–5 图注/表注 + 图形摘要说明
数据来源：out/*.csv|json（脚本真实运行输出）
输出：/Users/mac/Desktop/文稿库/人工智能临床应用/P2_supplementary_v0.1.docx
"""
import json, pathlib, csv
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

BASE = pathlib.Path("/Users/mac/Desktop/库/公共数据AF")
OUT = BASE / "out"
ART = pathlib.Path("/Users/mac/Desktop/文稿库/人工智能临床应用")


def base_doc():
    d = Document()
    st = d.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11)
    st.paragraph_format.line_spacing = 1.5; st.paragraph_format.space_after = Pt(0)
    for s in d.sections:
        s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Cm(2.2)
    return d


def H(d, text, size=13, space=10):
    p = d.add_paragraph(); r = p.add_run(text); r.bold = True; r.font.size = Pt(size)
    p.paragraph_format.space_before = Pt(space); p.paragraph_format.space_after = Pt(4)
    return p


def P(d, text, italic=False, size=10.5):
    p = d.add_paragraph(); r = p.add_run(text); r.italic = italic; r.font.size = Pt(size)
    return p


def table(d, header, rows, widths=None):
    t = d.add_table(rows=1, cols=len(header)); t.style = "Table Grid"
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; c.text = ""
        r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(9.5)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            cells[i].paragraphs[0].add_run(str(v)).font.size = Pt(9.5)
    return t


d = base_doc()
p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Supplementary Materials"); r.bold = True; r.font.size = Pt(15)
p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("Calibration Collapse in Cross-Population Atrial Fibrillation Detection: "
          "A Multi-Dataset Benchmark of Diagnostic Performance, Calibration and Operating-Point Transferability")
p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("[Authors — to be completed]").italic = True

# ---------------- Table S1 亚组 ----------------
H(d, "Supplementary Table S1. Subgroup analyses (cluster bootstrap, B = 1,000)")
P(d, "Subgroups were resampled by patient where patient identifiers exist (PTB-XL, CPSC2021); "
     "CinC2017 provides no patient identifiers and is therefore not included here. "
     "Se@Sp90 = sensitivity at a fixed 90% specificity.")
rows = []
with open(OUT / "table_subgroups.csv", newline="") as f:
    for r_ in csv.DictReader(f):
        rows.append([r_["group"], r_["n"],
                     f'{float(r_["AUROC"]):.3f} ({float(r_["AUROC_lo"]):.3f}–{float(r_["AUROC_hi"]):.3f})',
                     f'{float(r_["Se@Sp90"]):.3f} ({float(r_["Se@Sp90_lo"]):.3f}–{float(r_["Se@Sp90_hi"]):.3f})',
                     f'{float(r_["Brier"]):.3f}', f'{float(r_["Sp@0.5"]):.3f}'])
table(d, ["Subgroup", "n", "AUROC (95% CI)", "Se@Sp90 (95% CI)", "Brier", "Sp@0.5"], rows)

# ---------------- Table S2 重校准 ----------------
H(d, "Supplementary Table S2. Post-hoc recalibration in full (temperature scaling is strictly monotone and leaves "
     "AUROC unchanged; isotonic regression may create ties, shifting AUROC by at most 0.008)")
P(d, "Source-fitted = parameters estimated on out-of-fold predictions from five-fold patient-grouped "
     "cross-validation within the PTB-XL training data (deployable without target-domain data; the evaluated "
     "model is always the full-training-set model, so uncalibrated rows match main-text Table 2 exactly); "
     "oracle = parameters fitted directly on the target domain (upper bound, not deployable). "
     "ECE_eq = expected calibration error with equal-count bins.")
rows = []
with open(OUT / "table_recal_multidomain.csv", newline="") as f:
    for r_ in csv.DictReader(f):
        rows.append([r_["domain"][:28], r_["method"], r_["n"],
                     f'{float(r_["auroc"]):.3f}', f'{float(r_["brier"]):.3f}',
                     f'{float(r_["ece"]):.3f}', f'{float(r_["ece_eq"]):.3f}',
                     f'{float(r_["se_at_sp90"]):.3f}',
                     f'{float(r_["mean_pred"]):.3f} / {float(r_["observed"]):.3f}'])
table(d, ["Domain", "Recalibration", "n", "AUROC", "Brier", "ECE", "ECE (eq-count)", "Se@Sp90", "Mean pred / observed"], rows)

# ---------------- Table S3 实现细节 ----------------
H(d, "Supplementary Table S3. Implementation details and cohort accounting")
feat_cols = [c for c in open(OUT / "feat_ptbxl.csv").readline().strip().split(",") if c.startswith("f_")]
cpsc = json.load(open(OUT / "cpsc2021_window_summary.json"))
# CinC2017 子集类别分布
from collections import Counter
lab = {}
with open(BASE / "data" / "REFERENCE-v3.csv") as f:
    for line in f:
        parts = line.strip().split(",")
        if len(parts) == 2:
            lab[parts[0]] = parts[1]
sub = [x.strip() for x in open(BASE / "data" / "cinc2017_subset.txt") if x.strip()]
cnt = Counter(lab.get(s, "?") for s in sub)

P(d, f"Features ({len(feat_cols)} dimensions, no deep learning): RR-interval statistics, RMSSD/pNN20/pNN50, "
     f"Poincaré SD1/SD2, sample entropy of the RR series, RR-tachogram spectral features (dominant frequency, "
     f"spectral entropy, LF/HF power and ratio), and amplitude/band-power descriptors (0.5–5, 5–15, 15–40 Hz). "
     f"R-peak detection: band-pass 5–15 Hz, squaring, 150 ms moving average, adaptive threshold.")
P(d, "Models (fitted on PTB-XL only): (i) L2-regularised logistic regression with median imputation, "
     "standardisation and balanced class weights (max_iter = 2,000); (ii) histogram-based gradient boosting "
     "(HistGradientBoostingClassifier, max_iter = 300, learning_rate = 0.06, random_state = 0). "
     "Splitting random seed = 20260915 (patient-level 70/30 for PTB-XL; grouped 5-fold for CPSC2021).")
P(d, f"PTB-XL: 2,400 records sampled (all AFIB/AFLT records plus age-decade- and sex-matched controls); "
     f"1 record could not be read, leaving 2,399 (1,685 training / 714 internal test, patient-level).")
P(d, f"CinC2017: {len(sub)} records sampled from the official training set with per-class caps "
     f"(A {cnt.get('A', 0)}, N {cnt.get('N', 0)}, O {cnt.get('O', 0)}, ~ {cnt.get('~', 0)}); no patient identifiers available.")
P(d, f"CPSC2021 set I: the official release lists 730 records; {730 - cpsc['records_scanned']} records were "
     f"excluded because the WFDB header could not be parsed into a record-level diagnosis, leaving "
     f"{cpsc['records_scanned']} records with verified diagnoses (54 patients); signal was downloaded for "
     f"107 records (bandwidth-bounded, shortest-record-first sampling); "
     f"{cpsc['windows']} non-overlapping 30-second windows from {cpsc['patients']} patients "
     f"(AF {cpsc['af_windows']} / non-AF {cpsc['non_af_windows']}); by record diagnosis: "
     + ", ".join(f"{k} {v}" for k, v in cpsc["by_dx"].items()) +
     f". Excluded: {cpsc['skipped']['transition_removed']} windows containing a rhythm transition, "
     f"{cpsc['skipped']['over_patient_cap']} above the 24-window-per-patient cap, and "
     f"{cpsc['skipped']['no_dat']} records without downloaded signal.")
P(d, "Prevalence-based PPV/NPV in the main text were derived by Bayesian conversion of the measured "
     "sensitivity/specificity operating points, not measured directly (all cohorts were sampled at approximately 1:1).")

# ---------------- Legends ----------------
H(d, "Legends")
P(d, "Figure 1. Study flow. Three openly available cohorts were harmonised onto one 30-second, single-lead, "
     "segment-level AF-versus-non-AF task; all splits were performed at the patient level; models were developed "
     "on PTB-XL only.", italic=True)
P(d, "Figure 2. Multi-domain performance. Left: reliability (calibration) curves for internal and both external "
     "domains. Middle: distribution of predicted probabilities (score shift). Right: discrimination, calibration "
     "error and operating-point sensitivity side by side.", italic=True)
P(d, "Figure 3. Recalibration and clinical usefulness. Left: reliability before and after source-fitted and "
     "target-domain (oracle) recalibration. Right: decision-curve net benefit across threshold probabilities.", italic=True)
P(d, "Figure 4. Forest plot of AUROC and sensitivity at 90% specificity across domains, negative-class "
     "definitions and subgroups, with 95% confidence intervals (cluster bootstrap, B = 1,000).", italic=True)
P(d, "Figure 5. Positive predictive value versus prevalence for each measured operating point, with a "
     "previously validated high-specificity algorithm shown for reference.", italic=True)
P(d, "Graphical abstract. Discrimination, calibration and operating-point transferability across the three "
     "cohorts, and the resulting positive predictive value at screening prevalence.", italic=True)
P(d, "Table 1. Cohort characteristics. Table 2. Three-domain discrimination, calibration and operating-point "
     "performance. Table 3. Decomposition by negative-class composition. Table 4. Recalibration "
     "(source-fitted versus target-domain oracle). Table 5. Positive predictive value and negative predictive "
     "value at real-world prevalence.", italic=True)

out = ART / "P2_supplementary_v0.1.docx"
d.save(out)
print("saved:", out)
print("S1 rows:", len(open(OUT / 'table_subgroups.csv').readlines()) - 1,
      "| S2 rows:", len(open(OUT / 'table_recal_multidomain.csv').readlines()) - 1,
      "| features:", len(feat_cols), "| CinC2017 subset:", len(sub), dict(cnt))
