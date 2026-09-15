#!/usr/bin/env python3
"""检测文档里出现的指标数字，是否都能在结果文件里找到出处（写作防错）。

做法：
  1. 从 out/*.csv|json 收集所有指标数值（三位小数集合）
  2. 从三份文档里正则抽取形如 0.xxx 的数字（以及 x.xx）
  3. 输出"文档里有、结果文件里找不到"的数字清单 → 人工核对（可能是笔误或来自其他来源）
不做自动改写，只出清单（避免误改）。
输出：out/number_audit.md
"""
import json, pathlib, re
import pandas as pd

BASE = pathlib.Path("/Users/mac/Desktop/库/公共数据AF")
OUT = BASE / "out"
DOCS = [pathlib.Path("/Users/mac/Desktop/文稿库/人工智能临床应用/05_P2论文骨架.md"),
        pathlib.Path("/Users/mac/Desktop/文稿库/人工智能临床应用/06_P2_Methods与Results初稿.md"),
        BASE / "README_正式结果.md"]

vals = set()

# 允许"派生值"：两个已知数值的差（ΔAUROC 等），写作时常见
diff_vals = set()


def _note(v):
    vals.add(round(float(v), 3))
    vals.add(round(float(v), 2))

def harvest_csv(p):
    try:
        df = pd.read_csv(p)
    except Exception:
        return
    for c in df.columns:
        if pd.api.types.is_numeric_dtype(df[c]):
            for v in df[c].dropna():
                vals.add(round(float(v), 3))
                vals.add(round(float(v), 2))

for p in OUT.glob("*.csv"):
    harvest_csv(p)
try:
    res = json.load(open(OUT / "results_exp1.json"))
    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, (int, float)):
            vals.add(round(float(o), 3)); vals.add(round(float(o), 2))
    walk(res)
except Exception:
    pass

# 派生值：指标之间的差（ΔAUROC / ΔBrier 等）
base = sorted(v for v in vals if 0.15 <= v <= 1.0)
for i, a in enumerate(base):
    for b in base[i + 1:]:
        diff_vals.add(round(abs(a - b), 3))
        diff_vals.add(round(abs(a - b), 2))

# 允许的"非指标"数字（年份/样本量/比例常数等）
WHITELIST = {2026, 2025, 2024, 0.5, 0.9, 0.1, 0.2, 0.8, 1.0, 0.0, 0.05, 0.3, 0.4, 0.6, 0.7, 0.95, 1.2, 100.0}
# 明确标注的外部来源数字（来自导师团队已发表论文，非本研究运行结果）
EXTERNAL = {
    "98.60": "导师团队 Adv Sci 2026 报告灵敏度（《马长生团队AI相关研究汇编》）",
    "99.27": "导师团队 Adv Sci 2026 报告特异度（同上）",
    "96.3": "导师团队 PACE 2024 间期级灵敏度（同上）",
    "99.5": "导师团队 PACE 2024 间期级特异度（同上）",
}

report = []
for doc in DOCS:
    if not doc.exists():
        continue
    text = doc.read_text()
    nums = re.findall(r"(?<![\d.])(\d+\.\d{2,4})(?![\d])", text)
    missing = []
    for s in sorted(set(nums)):
        f = float(s)
        r3, r2 = round(f, 3), round(f, 2)
        if f in WHITELIST or r3 in vals or r2 in vals or s in EXTERNAL:
            continue
        if r3 in diff_vals or r2 in diff_vals:
            continue          # 两个已知指标的差
        missing.append(s)
    report.append((doc, len(set(nums)), missing))

lines = ["# 数字出处审计（文档中的指标数字 vs 结果文件）", ""]
lines.append(f"结果文件可查数值集合大小：{len(vals)}")
for doc, n, missing in report:
    lines.append(f"\n## {doc.name}（抽取到 {n} 个小数）")
    if not missing:
        lines.append("- ✅ 全部可溯源（未发现可疑数字）")
    else:
        lines.append(f"- ⚠️ {len(missing)} 个数字在结果文件中找不到，请人工核对：")
        for m in missing[:40]:
            lines.append(f"    - {m}")
txt = "\n".join(lines) + "\n"
(OUT / "number_audit.md").write_text(txt)
print(txt)
