#!/usr/bin/env python3
"""生成初审快照校验清单：对投稿文件与结果文件做 SHA-256，并回填到 12_初审快照与校验.md。
（只读文件、只写校验清单；不触碰 v1.0.0、不创建 Release、不重排参考文献）"""
import hashlib, pathlib, re, subprocess

ART = pathlib.Path("/Users/mac/Desktop/文稿库/人工智能临床应用")
BASE = pathlib.Path("/Users/mac/Desktop/库/公共数据AF")
OUT = BASE / "out"

SUBMISSION = ["P2_manuscript_v0.1.docx", "P2_abstract_250w.docx", "P2_supplementary_v0.1.docx",
              "P2_manuscript_JACCCEP_v0.1.docx", "参考文献_24条_P2.ris",
              "05_P2论文骨架.md", "06_P2_Methods与Results初稿.md", "07_参考文献清单.md",
              "08_投稿格式与投稿信.md", "09_Zotero逐条比对报告.md", "10_一页中文研究简介.md",
              "11_投稿流程约定.md"]
RESULTS = ["table_domains.csv", "table_ci.csv", "table_subgroups.csv", "table_recal_multidomain.csv",
           "table_ppv_npv.csv", "numbersheet.md", "number_audit.md",
           "fig1_flow.png", "fig2_multidomain_calibration.png", "fig3_recalibration_multidomain.png",
           "fig4_forest.png", "fig5_ppv_npv.png", "graphical_abstract.png"]


def h(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


lines = ["# 初审快照 SHA-256 校验清单", f"生成: {__import__('datetime').datetime.now():%Y-%m-%d %H:%M:%S}",
         "", "## 投稿文件", ""]
rows_md = []
for f in SUBMISSION:
    p = ART / f
    if p.exists():
        dg = h(p)
        lines.append(f"{dg}  {f}")
        rows_md.append((f, dg))
lines += ["", "## 结果与图表文件（项目 out/）", ""]
for f in RESULTS:
    p = OUT / f
    if p.exists():
        lines.append(f"{h(p)}  out/{f}")
# git 状态
try:
    tag = subprocess.run(["git", "-C", str(BASE), "rev-parse", "v1.0.0^{commit}"],
                         capture_output=True, text=True).stdout.strip()
    head = subprocess.run(["git", "-C", str(BASE), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    lines += ["", "## Git 状态", f"v1.0.0 = {tag}", f"HEAD   = {head}"]
except Exception as e:
    lines.append(f"git 查询失败: {e}")
(OUT / "snapshot_manifest.txt").write_text("\n".join(lines) + "\n")

# 回填到 12 号文稿
p12 = ART / "12_初审快照与校验.md"
s = p12.read_text()
tbl = ["| 文件 | SHA-256（前 16 位） |", "|---|---|"]
for f, dg in rows_md:
    tbl.append(f"| {f} | `{dg[:16]}` |")
old_start = s.index("| 文件 | SHA-256（前 16 位） |")
old_end = s.index("> 完整 64 位哈希由")
s = s[:old_start] + "\n".join(tbl) + "\n\n" + s[old_end:]
s = s.replace("（见下方\"重新生成后校验\"）", "")
p12.write_text(s)
print("snapshot_manifest.txt 生成完毕；12 号文稿哈希表已回填")
print(f"投稿文件 {len(rows_md)} 个 | 结果文件 {sum((OUT/f).exists() for f in RESULTS)} 个")
