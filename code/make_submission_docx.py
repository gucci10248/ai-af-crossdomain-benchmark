#!/usr/bin/env python3
"""把 06 初稿（英文正文）+ 08（250 词摘要/关键词）+ 07（参考文献）合成 EHJ 投稿用的 Word 文件。

产出：
  P2_manuscript_v0.1.docx   正文（标题页 / 摘要 / Introduction / Methods / Results / Discussion / 图表位置标注 / 参考文献）
  P2_abstract_250w.docx     摘要独立文件（期刊要求单独提交）
排版：Times New Roman 12pt、2.0 行距、页边距 2.5cm（通用投稿格式，最终按刊方要求微调）
"""
import pathlib, re, csv, json
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

ART = pathlib.Path("/Users/mac/Desktop/文稿库/人工智能临床应用")
AFBASE = pathlib.Path("/Users/mac/Desktop/库/公共数据AF")
OUT = AFBASE / "out"
DOC6 = ART / "06_P2_Methods与Results初稿.md"
DOC7 = ART / "07_参考文献清单.md"
DOC8 = ART / "08_投稿格式与投稿信.md"
TITLE = ("Calibration Collapse in Cross-Population Atrial Fibrillation Detection: "
         "A Multi-Dataset Benchmark of Diagnostic Performance, Calibration and Operating-Point Transferability")


def base_doc():
    d = Document()
    st = d.styles["Normal"]
    st.font.name = "Times New Roman"; st.font.size = Pt(12)
    pf = st.paragraph_format
    pf.line_spacing = 2.0; pf.space_after = Pt(0)
    for s in d.sections:
        s.top_margin = s.bottom_margin = Cm(2.5)
        s.left_margin = s.right_margin = Cm(2.5)
    return d


def h(d, text, level=1):
    p = d.add_paragraph()
    r = p.add_run(text); r.bold = True
    r.font.size = Pt(14 if level == 1 else 12)
    p.paragraph_format.space_before = Pt(12); p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.5
    return p


def body(d, text, style=None):
    """保留 **粗体** 标记，去掉 markdown 链接/反引号等；可选列表样式。"""
    text = text.replace("`", "")
    p = d.add_paragraph(style=style) if style else d.add_paragraph()
    for i, chunk in enumerate(re.split(r"\*\*(.+?)\*\*", text)):
        if not chunk:
            continue
        r = p.add_run(chunk)
        if i % 2 == 1:
            r.bold = True
    return p


def callout(d, text):
    p = d.add_paragraph()
    r = p.add_run(text); r.italic = True; r.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    p.paragraph_format.space_before = Pt(6)
    return p


def add_table(d, header, rows, font=9.5):
    """真正的 Word 表格（Table Grid），供投稿包主文 Tables 区使用。"""
    t = d.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    for i, htxt in enumerate(header):
        c = t.rows[0].cells[i]; c.text = ""
        r = c.paragraphs[0].add_run(htxt); r.bold = True; r.font.size = Pt(font)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            cells[i].paragraphs[0].add_run(str(v)).font.size = Pt(font)
    return t


def fmt3(x):
    return f"{float(x):.3f}"


def ci3(v, lo, hi):
    return f"{float(v):.3f} ({float(lo):.3f}\u2013{float(hi):.3f})"


def section_slice(text, start_marker, end_marker):
    i = text.index(start_marker) + len(start_marker)
    j = text.index(end_marker) if end_marker in text[i:] else len(text)
    return text[i:j]


md6 = DOC6.read_text()
md7 = DOC7.read_text()
md8 = DOC8.read_text()

# --- 从 06 抽取英文正文（INTRODUCTION / METHODS / RESULTS / DISCUSSION；跳过中文注与中文小标题行）---
intro = section_slice(md6, "## INTRODUCTION（英文正稿）", "## METHODS（英文正稿）")
methods = section_slice(md6, "## METHODS（英文正稿）", "## RESULTS（英文正稿）")
results = section_slice(md6, "## RESULTS（英文正稿）", "## DISCUSSION（英文正稿）")
disc = section_slice(md6, "## DISCUSSION（英文正稿）", "## 中文工作注")

# --- 摘要：取 08 第三节 ---
abst = section_slice(md8, "## 三、文字摘要（最终稿，带小标题；Europace 要求 text abstract with headings）", "## 四、What's New?")
abst_clean = re.sub(r"\n?（\*\*.*?）\n?", "", abst, flags=re.S).strip()
abst_clean = re.sub(r"^Keywords:.*$", "", abst_clean, flags=re.M).strip()  # 关键词由下方显式写入，避免重复
kw_m = re.search(r"^Keywords:\s*(.+)$", md8, re.M)
keywords = kw_m.group(1).strip()

# --- What's New：解析 08 第四节的项目符号（单一事实源，避免手抄漂移）---
wn_sec = section_slice(md8, "## 四、What's New?", "## 五、")
WHATS_NEW = [re.sub(r"^-\s*", "", ln).strip() for ln in wn_sec.split("\n") if ln.strip().startswith("- ")]
assert 2 <= len(WHATS_NEW) <= 6, f"What's New 条数异常: {len(WHATS_NEW)}"

# --- 主文词数：按实际切片计算（不含摘要/参考文献/表内文字/图注）---
def _wc(*texts):
    return len(re.findall(r"[A-Za-z0-9][\w\-'.%]*", " ".join(texts)))
wc_main = _wc(intro, methods, results, disc)

# --- 参考文献：解析 07 的表格，**保留原编号**（避免与正文 [n] 错位）---
refmap = {}
for m in re.finditer(r"^\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*([^|]*)\|\s*$", md7, re.M):
    num, cite = int(m.group(1)), m.group(2).strip()
    if cite.startswith("完整著录") or cite.startswith("---"):
        continue
    refmap[num] = cite
refs = [refmap[k] for k in sorted(refmap)]
print("refs parsed:", len(refs), "| 编号:", sorted(refmap)[:3], "...", sorted(refmap)[-3:])

# ============ 正文文件 ============
d = base_doc()
p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run(TITLE); r.bold = True; r.font.size = Pt(15)
p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("Jinkai Guo, MD Candidate; Hua Chen, MD, PhD")
p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Department of Cardiology, Inner Mongolia Autonomous Region People's Hospital, Hohhot 010017, China")
r.font.size = Pt(10.5)
p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("ORCID: Jinkai Guo 0009-0000-2455-0486; Hua Chen 0000-0001-9140-5019")
r.font.size = Pt(10.5)
p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("Running title: Cross-device AF detection: calibration collapse")
p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Corresponding author: Hua Chen, MD, PhD, Department of Cardiology, Inner Mongolia Autonomous Region "
              "People's Hospital, Hohhot 010017, China. Email: Zxcv8521@163.com. ORCID: 0000-0001-9140-5019")
r.font.size = Pt(10.5)
p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run(f"Word count (main text, excl. abstract/references/table text): \u2248{wc_main:,}  |  Figures: 5  |  Tables: 5  |  "
          f"References: {len(refmap)}  |  Supplementary: Tables S1\u2013S3")

h(d, "Abstract", 1)
for para in [x.strip() for x in abst_clean.split("\n") if x.strip()]:
    body(d, para)
body(d, f"Keywords: {keywords}")
callout(d, "[Graphical abstract submitted as a separate file: graphical_abstract.png]")
callout(d, "[Target journal: Europace (SCIE; IF 10.2, JCR 17/237). Additional What's New? box required - see below.]")

h(d, "What's New?", 2)
for b in WHATS_NEW:
    p = d.add_paragraph(style="List Bullet")
    p.add_run(b).font.size = Pt(11)

def emit(text):
    """按行输出正文：### → 二级标题；- / 1. → 列表；其余 → 段落。"""
    for para in [x.strip() for x in text.split("\n") if x.strip()]:
        if para.startswith("###"):
            h(d, re.sub(r"^###\s*", "", para), 2)
        elif para.startswith("- "):
            body(d, para[2:].strip(), style="List Bullet")
        elif re.match(r"^\d+\.\s+", para):
            body(d, re.sub(r"^\d+\.\s+", "", para), style="List Number")
        else:
            body(d, para)


h(d, "Introduction", 1)
emit(intro)

h(d, "Methods", 1)
emit(methods)

h(d, "Results", 1)
emit(results)
callout(d, "[Table 1 near here] [Table 2 near here] [Table 3 near here] [Fig 1 near here] [Fig 2 near here] [Fig 3 near here] [Fig 4 near here] [Fig 5 near here]")

h(d, "Discussion", 1)
emit(disc)

h(d, "Authors' contributions", 2)
body(d, "Jinkai Guo: conceptualization; methodology; software and formal analysis (data acquisition, harmonisation, "
        "benchmark implementation); investigation; writing - original draft. "
        "Hua Chen: conceptualization; supervision; validation; writing - review and editing; corresponding author. "
        "Both authors read and approved the final manuscript.")

h(d, "Funding", 2)
body(d, "None.")

h(d, "Competing interests", 2)
body(d, "The authors declare no competing interests.")

h(d, "Ethics", 2)
body(d, "Not applicable. This study used only openly available, de-identified public datasets (PTB-XL, "
        "PhysioNet/CinC Challenge 2017, CPSC2021); no human participants were recruited and no institutional data "
        "were accessed.")

h(d, "Acknowledgements", 2)
body(d, "None.")

h(d, "Data availability", 1)
body(d, "All data are openly available: PTB-XL v1.0.3 (doi:10.13026/kfzx-aw45), PhysioNet/CinC Challenge 2017 "
        "(doi:10.13026/d3hm-sf11) and CPSC2021 v1.0.0 (doi:10.13026/ksya-qw89). Analysis code, derived feature tables, "
        "figure sources and the numeric audit trail are openly available at "
        "https://github.com/gucci10248/ai-af-crossdomain-benchmark; the archival record of this project is "
        "deposited at Zenodo (doi:10.5281/zenodo.22764409; all versions: doi:10.5281/zenodo.22764408), and the "
        "archived code release corresponding to the final version of this manuscript will be updated at revision.")

h(d, "References", 1)
for k in sorted(refmap):
    body(d, f"{k}. {refmap[k]}")

# ============ Tables（全部从 out/*.csv|json 真实运行结果生成，禁止手抄） ============
dom = {r["domain"]: r for r in csv.DictReader(open(OUT / "table_domains.csv"))}
ci_rows = {r["group"]: r for r in csv.DictReader(open(OUT / "table_ci.csv"))}
exp1 = json.load(open(OUT / "results_exp1.json"))
recal = list(csv.DictReader(open(OUT / "table_recal_multidomain.csv")))
ppv_all = list(csv.DictReader(open(OUT / "table_ppv_npv.csv")))
subg = list(csv.DictReader(open(OUT / "table_subgroups.csv")))

DOM_INT = "内部：PTB-XL（德国 12 导联）"
DOM_E1 = "外部 1：CinC2017（消费级单导联）"
DOM_E2 = "外部 2：CPSC2021（中国动态 ECG）"
CI_INT = "内部：PTB-XL（德国12导）"
CI_E1 = "外部1：CinC2017 全部（A vs 非A）"
CI_E2 = "外部2：CPSC2021（中国，30秒窗）"

d.add_page_break()
h(d, "Tables", 1)

# ---- Table 1：队列特征 ----
h(d, "Table 1. Cohort characteristics", 2)
add_table(d,
    ["Cohort", "Country / setting", "Device & recording", "Sampling", "Included in this study", "AF prevalence"],
    [["PTB-XL v1.0.3", "Germany, clinical", "12-lead, 10 s (lead I, 100 Hz release)",
      "All AFIB/AFLT records + age-decade/sex-matched controls",
      "2,399 records (1,685 training / 714 internal test, patient-level)", "50% (by sampling design)"],
     ["PhysioNet/CinC Challenge 2017", "Consumer wearable (AliveCor)", "Single-lead, \u226460 s, 300 Hz",
      "All AF records + capped subsets of N/O/~", "2,537 records (A 758 / N 1,000 / O 500 / ~ 279)", "29.9% (A)"],
     ["CPSC2021 set I", "China, ambulatory", "12-lead Holter / 3-lead wearable, 200 Hz, 4\u2013106 min",
      "Non-overlapping 30-s windows, \u226424 per patient; transition windows excluded",
      "719 records \u2192 583 windows from 25 patients (AF 280 / non-AF 303)", "48.0% (window level)"]])

# ---- Table 2：三域主结果 ----
def _row2(dom_key, ci_key, label, exp1_key=None):
    r, c = dom[dom_key], ci_rows[ci_key]
    e = exp1[exp1_key] if exp1_key else None
    se05 = f'{e["at_0.5"]["sens"]:.3f}/{e["at_0.5"]["spec"]:.3f}' if e else "\u2014"
    return [label, r["n"], ci3(c["AUROC"], c["AUROC_lo"], c["AUROC_hi"]), fmt3(r["auprc"]),
            fmt3(r["brier"]), fmt3(r["ece"]), se05,
            ci3(c["Se@Sp90"], c["Se@Sp90_lo"], c["Se@Sp90_hi"])]

h(d, "Table 2. Three-domain discrimination, calibration and operating-point performance "
     "(gradient boosting trained on PTB-XL only; 95% CI by cluster bootstrap, B = 1,000)", 2)
rows2 = [
    _row2(DOM_INT, CI_INT, "Internal: PTB-XL (Germany, 12-lead)", "ptbxl_internal_hgb"),
    _row2(DOM_E1, CI_E1, "External 1: CinC2017 (consumer single-lead, AF vs non-AF)", "cinc2017_external_from_hgb"),
    _row2(DOM_E2, CI_E2, "External 2: CPSC2021 (China, ambulatory 30-s windows)", "cpsc2021_external_hgb"),
]
# 参照行：严格口径 + 域内参照（来自 results_exp1.json，无 bootstrap CI）
for key, lab in [("cinc2017_external_strict_hgb", "External 1, AF vs normal only (n = 1,758)"),
                 ("cinc2017_internal_5fold", "CinC2017 in-domain 5-fold CV (reference)"),
                 ("cpsc2021_internal_5fold", "CPSC2021 in-domain grouped 5-fold CV (reference)")]:
    v = exp1[key]
    rows2.append([lab, v["n"], fmt3(v["auroc"]), fmt3(v["auprc"]), fmt3(v["brier"]), fmt3(v["ece"]),
                  f'{v["at_0.5"]["sens"]:.3f}/{v["at_0.5"]["spec"]:.3f}', fmt3(v["at_spec90"]["sens"])])
add_table(d, ["Domain", "n", "AUROC (95% CI)", "AUPRC", "Brier", "ECE", "Se/Sp @ 0.5", "Se@Sp90 (95% CI)"], rows2)
body(d, "Reference rows without CIs were computed by in-domain cross-validation or on a restricted negative class; "
        "bootstrap CIs for those analyses are given in Table 3 and Supplementary Table S1.")

# ---- Table 3：阴性类分解 ----
h(d, "Table 3. Decomposition of the external-1 evaluation by negative-class composition "
     "(positive class = AF throughout)", 2)
rows3 = []
for gkey, lab in [("外部1a：仅 A vs N", "AF vs normal (N)"),
                  ("外部1b：A vs O（其他节律）", "AF vs other rhythms (O)"),
                  ("外部1c：A vs 噪声(~)", "AF vs noisy segments (~)")]:
    c = ci_rows[gkey]
    rows3.append([lab, c["n"], ci3(c["AUROC"], c["AUROC_lo"], c["AUROC_hi"]),
                  ci3(c["Se@Sp90"], c["Se@Sp90_lo"], c["Se@Sp90_hi"]),
                  fmt3(c["Brier"]), ci3(c["Sp@0.5"], c["Sp@0.5_lo"], c["Sp@0.5_hi"])])
add_table(d, ["Negative class", "n", "AUROC (95% CI)", "Se@Sp90 (95% CI)", "Brier", "Sp@0.5 (95% CI)"], rows3)

# ---- Table 4：重校准 ----
h(d, "Table 4. Post-hoc recalibration: source-fitted versus target-domain (oracle)", 2)
mname = {"未校准": "Uncalibrated", "温度缩放(源域拟合)": "Temperature scaling (source-fitted, T = 3.25)",
         "等渗回归(源域拟合)": "Isotonic regression (source-fitted)",
         "温度缩放(目标域拟合)": "Temperature scaling (target-domain oracle)",
         "等渗回归(目标域拟合)": "Isotonic regression (target-domain oracle)"}
rows4 = [[r["domain"].split("（")[0], mname.get(r["method"], r["method"]),
          fmt3(r["auroc"]), fmt3(r["brier"]), fmt3(r["ece"]), fmt3(r["se_at_sp90"])]
         for r in recal]
add_table(d, ["Domain", "Recalibration", "AUROC", "Brier", "ECE", "Se@Sp90"], rows4)
body(d, "Source-fitted calibrators were estimated on out-of-fold predictions from five-fold patient-grouped "
        "cross-validation within the PTB-XL training data; the evaluated model was always the full-training-set "
        "model, so uncalibrated rows are identical to Table 2 by construction. Temperature scaling is strictly "
        "monotone (AUROC unchanged); isotonic regression may create ties (AUROC shifted by at most 0.008).")

# ---- Table 5：PPV/NPV ----
h(d, "Table 5. Positive and negative predictive value at real-world prevalence "
     "(Bayesian conversion of the measured operating points)", 2)
show_ops = ["本研究 · 内部验证（PTB-XL，Se@Sp90）", "本研究 · 外部1 可穿戴（0.5 阈值）",
            "本研究 · 外部1 可穿戴（Se@Sp90）", "本研究 · 外部1 严格 A vs N（Se@Sp90）",
            "本研究 · 外部1 A vs 噪声（Se@Sp90）", "本研究 · 中国域 CPSC2021（Se@Sp90）",
            "对照锚点 · 导师团队 PACE 2024（间期级，消融人群）"]
op_label = {op: op.split(" · ")[-1] for op in show_ops}
rows5 = []
for op in show_ops:
    cells = [op_label[op]]
    sub0 = next(r for r in ppv_all if r["operating_point"] == op)
    cells.append(f'{float(sub0["se"]):.3f}/{float(sub0["sp"]):.4f}'.rstrip("0").rstrip("."))
    for prev in ("0.01", "0.05", "0.2"):
        r = next(x for x in ppv_all if x["operating_point"] == op and abs(float(x["prevalence"]) - float(prev)) < 1e-9)
        cells.append(f'{float(r["PPV"])*100:.1f}% / {float(r["NPV"])*100:.2f}%')
    r1 = next(x for x in ppv_all if x["operating_point"] == op and abs(float(x["prevalence"]) - 0.01) < 1e-9)
    cells.append(r1["每检出1例需复核阳性例数"])
    rows5.append(cells)
add_table(d, ["Operating point", "Se / Sp", "PPV / NPV at 1%", "PPV / NPV at 5%", "PPV / NPV at 20%",
              "Positives reviewed per case found (1%)"], rows5)
body(d, "PPV/NPV at prevalence p are computed from the measured sensitivity/specificity by Bayes' theorem; "
        "all three cohorts were sampled at near 1:1, so these are conversions, not direct measurements.")

# ============ Figure legends（按 Europace 要求置于文末） ============
d.add_page_break()
h(d, "Figure legends", 1)
for leg in [
    "Figure 1. Study flow and cohort provenance. Three openly available cohorts were harmonised onto one "
    "30-second, single-lead, segment-level AF-versus-non-AF task; all splits were performed at the patient "
    "level; models were developed on PTB-XL only and the two external cohorts never informed model selection.",
    "Figure 2. Multi-domain performance. Left: reliability (calibration) curves for the internal and both "
    "external domains. Middle: distribution of predicted probabilities (score shift across domains). "
    "Right: discrimination, calibration error and operating-point sensitivity shown side by side.",
    "Figure 3. Recalibration and clinical usefulness. Left: reliability before and after source-fitted and "
    "target-domain (oracle) recalibration in the two external domains. Right: decision-curve net benefit "
    "across threshold probabilities.",
    "Figure 4. Forest plot of AUROC and sensitivity at 90% specificity across domains, negative-class "
    "definitions and pre-specified subgroups, with 95% confidence intervals (cluster bootstrap, B = 1,000).",
    "Figure 5. Positive predictive value versus prevalence for each measured operating point; a previously "
    "validated high-specificity smartwatch algorithm (99.5% specificity) is shown for reference.",
]:
    body(d, leg)
callout(d, "[Figures 1\u20135 are submitted as separate files (600 dpi, PNG and LZW-compressed TIFF, "
           "colour-blind-safe Okabe\u2013Ito palette): fig1_flow / fig2_multidomain_calibration / "
           "fig3_recalibration_multidomain / fig4_forest / fig5_ppv_npv; graphical abstract submitted separately.]")

out1 = ART / "P2_manuscript_v0.1.docx"
d.save(out1)

# ============ 摘要独立文件 ============
d2 = base_doc()
p = d2.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Abstract"); r.bold = True; r.font.size = Pt(14)
for para in [x.strip() for x in abst_clean.split("\n") if x.strip()]:
    body(d2, para)
body(d2, f"Keywords: {keywords}")
out2 = ART / "P2_abstract_250w.docx"
d2.save(out2)

print("saved:", out1, "\nsaved:", out2)
print("refs parsed:", len(refs))
print("abstract words (approx):", len(re.sub(r"[^\w\s-]", " ", abst_clean).split()))
