#!/usr/bin/env python3
"""把 06 初稿（英文正文）+ 08（250 词摘要/关键词）+ 07（参考文献）合成 EHJ 投稿用的 Word 文件。

产出：
  P2_manuscript_v0.1.docx   正文（标题页 / 摘要 / Introduction / Methods / Results / Discussion / 图表位置标注 / 参考文献）
  P2_abstract_250w.docx     摘要独立文件（期刊要求单独提交）
排版：Times New Roman 12pt、2.0 行距、页边距 2.5cm（通用投稿格式，最终按刊方要求微调）
"""
import pathlib, re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

ART = pathlib.Path("/Users/mac/Desktop/文稿库/人工智能临床应用")
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


def body(d, text):
    """保留 **粗体** 标记，去掉 markdown 链接等。"""
    p = d.add_paragraph()
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
kw_m = re.search(r"^Keywords:\s*(.+)$", md8, re.M)
keywords = kw_m.group(1).strip()

# --- 参考文献：解析 07 的两张表 ---
refs = []
for m in re.finditer(r"^\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*([^|]*)\|\s*$", md7, re.M):
    num, cite, tail = m.group(1), m.group(2), m.group(3).strip()
    if cite.startswith("完整著录") or cite.startswith("---"):
        continue
    refs.append(cite)
refs = refs[:24]

# ============ 正文文件 ============
d = base_doc()
p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run(TITLE); r.bold = True; r.font.size = Pt(15)
p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("Running title: Cross-device AF detection: calibration collapse")
p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("[Author 1, Author 2, Author 3 …]  ← 作者顺序与单位待定稿")
p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("[Affiliations: Inner Mongolia Autonomous Region People's Hospital; …]")
p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("Correspondence: [name], [address], [email]")
p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("Word count (main text, excl. abstract/references): ≈3,100  |  Figures: 5  |  Tables: 5  |  References: 24")

h(d, "Abstract", 1)
for para in [x.strip() for x in abst_clean.split("\n") if x.strip()]:
    body(d, para)
body(d, f"Keywords: {keywords}")
callout(d, "[Graphical abstract submitted as a separate file: graphical_abstract.png]")
callout(d, "[Target journal: Europace (SCIE; IF 10.2, JCR 17/237). Additional What's New? box required - see below.]")

WHATS_NEW = [
 "Discrimination barely changed across devices (AUROC 0.974 internally versus 0.886 in a consumer wearable cohort), while calibration error tripled and sensitivity at 90% specificity fell from 0.940 to 0.596.",
 "Transfer to a Chinese ambulatory cohort was substantially better (AUROC 0.947), indicating that acquisition and device shift, rather than population shift, dominates the loss.",
 "Most false positives originated from noisy segments (AF versus noise: AUROC 0.646; sensitivity at 90% specificity 0.199), not from other rhythms or population differences.",
 "Source-fitted recalibration transferred poorly, and no post-hoc monotone method improved discrimination.",
 "At 1% prevalence the cross-device operating point implies a positive predictive value of 2.7%, versus 66-69% for algorithms validated at 99.5% specificity or above.",
]
h(d, "What's New?", 2)
for b in WHATS_NEW:
    p = d.add_paragraph(style="List Bullet")
    p.add_run(b).font.size = Pt(11)

h(d, "Introduction", 1)
for para in [x.strip() for x in intro.split("\n") if x.strip()]:
    body(d, para)

h(d, "Methods", 1)
for para in [x.strip() for x in methods.split("\n") if x.strip()]:
    if para.startswith("###"):
        h(d, re.sub(r"^###\s*", "", para), 2)
    else:
        body(d, para)

h(d, "Results", 1)
for para in [x.strip() for x in results.split("\n") if x.strip()]:
    if para.startswith("###"):
        h(d, re.sub(r"^###\s*", "", para), 2)
    else:
        body(d, para)
callout(d, "[Table 1 near here] [Table 2 near here] [Table 3 near here] [Fig 1 near here] [Fig 2 near here] [Fig 3 near here] [Fig 4 near here] [Fig 5 near here]")
callout(d, "[Figure legends: Fig 1 study flow; Fig 2 multi-domain calibration; Fig 3 recalibration and decision curves; "
           "Fig 4 forest plot of AUROC and Se@Sp90 with 95% CI; Fig 5 PPV versus prevalence.]")
callout(d, "[Tables: Table 1 cohort characteristics; Table 2 three-domain discrimination/calibration/operating points; "
           "Table 3 decomposition by negative-class composition; Table 4 recalibration (source-fitted vs target-domain oracle); "
           "Table 5 PPV/NPV at real-world prevalence. Supplementary Tables S1 (subgroups), S2 (full recalibration), "
           "S3 (implementation details and cohort accounting).]")

h(d, "Discussion", 1)
for para in [x.strip() for x in disc.split("\n") if x.strip()]:
    if para.startswith("###"):
        h(d, re.sub(r"^###\s*", "", para), 2)
    else:
        body(d, para)

h(d, "Data availability", 1)
body(d, "All data are openly available: PTB-XL v1.0.3 (doi:10.13026/kfzx-aw45), PhysioNet/CinC Challenge 2017 "
        "(doi:10.13026/d3hm-sf11) and CPSC2021 v1.0.0 (doi:10.13026/ksya-qw89). Analysis code, derived feature tables, "
        "figure sources and the numeric audit trail are archived at Zenodo: "
        "https://doi.org/10.5281/zenodo.22764409 (all versions: 10.5281/zenodo.22764408), "
        "repository: https://github.com/gucci10248/ai-af-crossdomain-benchmark.")

h(d, "References", 1)
for i, cite in enumerate(refs, 1):
    body(d, f"{i}. {cite}")

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
