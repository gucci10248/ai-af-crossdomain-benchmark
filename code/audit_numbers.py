#!/usr/bin/env python3
"""数字审计 v2（2026-09-15 重写，修复 v1 的存在性匹配弱点）。

v1 弱点：把所有 out/*.csv|json 的数值汇成 2 万级大池子，文档数字只做"存在性匹配"——
两个不同运行（如 exp1 vs table_domains）的第三小数位差异会同时入池，导致"混源引用"穿过审计。

v2 两层校验：
  A. 同源一致性（回归测试）：同一指标在多个结果文件中的取值必须逐位一致
     - results_exp1.json (hgb)  vs  table_domains.csv
     - table_ci.csv 点估计      vs  table_domains.csv
     任一指标 |diff| >= 5e-4 → FAIL（禁止两个运行家族并存）。
  B. 文档取数校验：文档里的小数必须命中【numbersheet.json 权威值池】
     （不再是整个 out/ 池），派生差值只允许由权威值池内数值相减得到。
输出：out/number_audit.md；进程退出码 0=PASS，1=FAIL。
"""
import json, pathlib, re, sys
import pandas as pd

BASE = pathlib.Path("/Users/mac/Desktop/库/公共数据AF")
OUT = BASE / "out"
ART = pathlib.Path("/Users/mac/Desktop/文稿库/人工智能临床应用")
DOCS = [ART / "05_P2论文骨架.md",
        ART / "06_P2_Methods与Results初稿.md",
        ART / "08_投稿格式与投稿信.md",
        ART / "10_一页中文研究简介.md",
        BASE / "README_正式结果.md"]

TOL = 5e-4  # 打印三位小数（四舍五入）允许的最大差

# ============ A. 同源一致性 ============
dom = pd.read_csv(OUT / "table_domains.csv").set_index("domain")
res = json.load(open(OUT / "results_exp1.json"))

def _find_key(pat):
    hits = [k for k in res if re.search(pat, k) and "hgb" in k]
    return hits[0] if hits else None

pairs = [  # (exp1 key 正则, table_domains 行名)
    (r"ptbxl_internal", "内部：PTB-XL（德国 12 导联）"),
    (r"cinc2017_external", "外部 1：CinC2017（消费级单导联）"),
    (r"cpsc2021_external", "外部 2：CPSC2021（中国动态 ECG）"),
]
METRIC_MAP = [("auroc", "auroc"), ("auprc", "auprc"), ("brier", "brier"), ("ece", "ece")]

consistency = []  # (指标, exp1值, domains值, |diff|, ok)
for pat, dom_name in pairs:
    k = _find_key(pat)
    if k is None or dom_name not in dom.index:
        consistency.append((pat, "KEY MISSING", "", "", False))
        continue
    r1, r2 = res[k], dom.loc[dom_name]
    for m1, m2 in METRIC_MAP:
        a, b = float(r1[m1]), float(r2[m2])
        consistency.append((f"{dom_name} · {m1}", f"{a:.6f}", f"{b:.6f}", f"{abs(a-b):.2e}", abs(a-b) < TOL))
    a, b = float(r1["at_spec90"]["sens"]), float(r2["se_at_sp90"])
    consistency.append((f"{dom_name} · se_at_sp90", f"{a:.6f}", f"{b:.6f}", f"{abs(a-b):.2e}", abs(a-b) < TOL))

# table_ci.csv 点估计 vs table_domains.csv
ci = pd.read_csv(OUT / "table_ci.csv")
CI_MAP = [("内部：PTB-XL（德国12导）", "内部：PTB-XL（德国 12 导联）"),
          ("外部1：CinC2017 全部（A vs 非A）", "外部 1：CinC2017（消费级单导联）"),
          ("外部2：CPSC2021（中国，30秒窗）", "外部 2：CPSC2021（中国动态 ECG）")]
for ci_name, dom_name in CI_MAP:
    row = ci[ci["group"] == ci_name]
    if row.empty or dom_name not in dom.index:
        continue
    row = row.iloc[0]
    for m_ci, m_dom in [("AUROC", "auroc"), ("Se@Sp90", "se_at_sp90"), ("Brier", "brier")]:
        a, b = float(row[m_ci]), float(dom.loc[dom_name][m_dom])
        consistency.append((f"CI表 {ci_name} · {m_ci}", f"{a:.6f}", f"{b:.6f}", f"{abs(a-b):.2e}", abs(a-b) < TOL))

# table_recal_multidomain.csv 未校准行 vs table_domains.csv
# （回归测试：2026-09-15 修复前，recal 用 80% 训练集的另一个模型，未校准行对不上主结果）
_recal_path = OUT / "table_recal_multidomain.csv"
if _recal_path.exists():
    re_ = pd.read_csv(_recal_path)
    RECAL_MAP = [("源域 PTB-XL", "内部：PTB-XL（德国 12 导联）"),
                 ("CinC2017（消费级可穿戴单导联）", "外部 1：CinC2017（消费级单导联）"),
                 ("CPSC2021（中国动态 ECG 30 秒窗）", "外部 2：CPSC2021（中国动态 ECG）")]
    for re_name, dom_name in RECAL_MAP:
        row = re_[(re_["domain"] == re_name) & (re_["method"] == "未校准")]
        if row.empty or dom_name not in dom.index:
            continue
        row = row.iloc[0]
        for m in ["auroc", "brier", "ece", "se_at_sp90"]:
            a, b = float(row[m]), float(dom.loc[dom_name][m])
            consistency.append((f"重校准表未校准行 {re_name} · {m}", f"{a:.6f}", f"{b:.6f}",
                                f"{abs(a-b):.2e}", abs(a - b) < TOL))

n_bad = sum(1 for c in consistency if c[-1] is not True)
consistency_pass = (n_bad == 0)

# ============ B. 文档取数校验（权威值池 = numbersheet.json） ============
ns = json.load(open(OUT / "numbersheet.json"))
ns_rows = ns if isinstance(ns, list) else ns.get("rows", [])
vals = set()
for row in ns_rows:
    for tok in re.findall(r"\d+\.\d+", str(row.get("value", ""))):
        vals.add(round(float(tok), 3)); vals.add(round(float(tok), 2))

# 派生值：权威值池内两两之差（ΔAUROC 等写作常见派生量）
diff_vals = set()
base = sorted(v for v in vals if 0.15 <= v <= 1.0)
for i, a in enumerate(base):
    for b in base[i + 1:]:
        diff_vals.add(round(abs(a - b), 3)); diff_vals.add(round(abs(a - b), 2))

WHITELIST = {2026, 2025, 2024, 2023, 2022, 2021, 2020, 2019, 2017,
             0.5, 0.9, 0.1, 0.2, 0.8, 1.0, 0.0, 0.05, 0.3, 0.4, 0.6, 0.7, 0.95, 1.2, 100.0}
EXTERNAL = {
    "98.60": "导师团队 Adv Sci 2026 报告灵敏度",
    "99.27": "导师团队 Adv Sci 2026 报告特异度",
    "96.3": "导师团队 PACE 2024 间期级灵敏度",
    "99.5": "导师团队 PACE 2024 间期级特异度",
    "98.70": "导师团队 JACC Clin EP 2026 间期级灵敏度（PMID 42283663）",
    "99.56": "导师团队 JACC Clin EP 2026 间期级特异度（同上）",
    "62.5": "导师团队 JACC Clin EP 2026：智能手表 PPG 片段有效率（同上）",
    "96.2": "导师团队 JACC Clin EP 2026：贴片 ECG 有效率（同上）",
    "1.34": "导师团队 JACC Clin EP 2026：负荷差值均数 −1.34%（同上）",
    "0.999": "导师团队 JACC Clin EP 2026：负荷相关 r=0.999（同上）",
    "0.855": "导师团队 Heart Rhythm O2 2025：内部验证 AUROC（PMID 40496585）",
    "0.773": "导师团队 Heart Rhythm O2 2025：外部验证 AUROC（同上）",
    "10.2": "Europace 2025 影响因子（期刊官网）",
    "14.8": "Europace 2025 CiteScore（期刊官网）",
    "3.12": "Python 3.12（软件版本，非指标）",
}

DOI_PREFIX = re.compile(r"^10\.\d{4}$")  # DOI 前缀（如 10.5281/zenodo.xxx），非指标数字

report = []
for doc in DOCS:
    if not doc.exists():
        continue
    text = doc.read_text()
    nums = re.findall(r"(?<![\d.])(\d+\.\d{2,4})(?![\d])", text)
    missing = []
    for s in sorted(set(nums)):
        f = float(s)
        if DOI_PREFIX.match(s):
            continue
        r3, r2 = round(f, 3), round(f, 2)
        if f in WHITELIST or r3 in vals or r2 in vals or s in EXTERNAL:
            continue
        if r3 in diff_vals or r2 in diff_vals:
            continue
        missing.append(s)
    report.append((doc, len(set(nums)), missing))

# ============ 输出 ============
lines = ["# 数字出处审计 v2（权威值池 + 同源一致性回归）", ""]
lines.append(f"权威值池（numbersheet.json）数值个数：{len(vals)}")
lines.append("")
lines.append("## A. 同源一致性（exp1 vs table_domains vs table_ci，容差 5e-4）")
for name, a, b, d, ok in consistency:
    mark = "✅" if ok is True else ("❌" if ok is False else "—")
    lines.append(f"- {mark} {name}: exp1={a} vs domains/ci={b} (|Δ|={d})")
lines.append(f"\n**一致性结论：{'PASS' if consistency_pass else f'FAIL（{n_bad} 项不一致）'}**")

for doc, n, missing in report:
    lines.append(f"\n## {doc.name}（抽取到 {n} 个小数）")
    if not missing:
        lines.append("- ✅ 全部命中权威值池（numbersheet.json）")
    else:
        lines.append(f"- ⚠️ {len(missing)} 个数字不在权威值池，请人工核对：")
        for m in missing[:40]:
            lines.append(f"    - {m}")

all_ok = consistency_pass and all(not m for _, _, m in report)
lines.append(f"\n---\n总体：{'✅ PASS' if all_ok else '❌ FAIL'}")
txt = "\n".join(lines) + "\n"
(OUT / "number_audit.md").write_text(txt)
print(txt)
sys.exit(0 if all_ok else 1)
