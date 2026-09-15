#!/usr/bin/env python3
"""把作者信息（来自 /Users/mac/Desktop/文稿库/CV预防LMIC_作者信息.md）填入投稿稿件生成器。

作者：Jinkai Guo（第一作者，MD Candidate，ORCID 0009-0000-2455-0486）
      Hua Chen（通讯作者，MD PhD，ORCID 0000-0001-9140-5019，Zxcv8521@163.com）
单位：Department of Cardiology, Inner Mongolia Autonomous Region People's Hospital, Hohhot 010017, China
补充：作者贡献、基金（None）、利益冲突（无）、伦理（不适用：公开数据）、致谢
"""
import pathlib

KB = pathlib.Path("/Users/mac/Desktop/库/公共数据AF/code")
p = KB / "make_submission_docx.py"
s = p.read_text()

OLD_BLOCK = '''p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("Running title: Cross-device AF detection: calibration collapse")
p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("[Author 1, Author 2, Author 3 …]  ← 作者顺序与单位待定稿")
p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("[Affiliations: Inner Mongolia Autonomous Region People's Hospital; …]")
p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("Correspondence: [name], [address], [email]")
p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("Word count (main text, excl. abstract/references): ≈3,100  |  Figures: 5  |  Tables: 5  |  References: 24")'''

NEW_BLOCK = '''p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("Jinkai Guo, MD Candidate\\(^{1}\\); Hua Chen, MD, PhD\\(^{1,2}\\)")
p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("\\u00b9 Department of Cardiology, Inner Mongolia Autonomous Region People's Hospital, Hohhot 010017, China\\n"
              "\\u00b2 National Clinical Research Center for Cardiovascular Diseases (affiliated unit), Beijing, China")
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
p.add_run("Word count (main text, excl. abstract/references/table text): \\u22483,100  |  Figures: 5  |  Tables: 5  |  "
          "References: 24  |  Supplementary: Tables S1\\u2013S3")

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
body(d, "None.")'''

if OLD_BLOCK in s:
    s = s.replace(OLD_BLOCK, NEW_BLOCK, 1)
    p.write_text(s)
    print("作者信息与声明段落已写入生成器")
else:
    print("ERROR: 未找到占位块，需人工核对")
