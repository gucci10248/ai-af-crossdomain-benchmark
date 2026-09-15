#!/usr/bin/env python3
"""汇总所有结果文件，生成**唯一权威数字表**（out/numbersheet.md + numbersheet.json）。
用途：写作时只从这里取数，避免"文档里的数字与运行结果不一致"（这是最容易出错的地方）。
每个数字都标注来源文件与复现脚本。
"""
import json, pathlib
import numpy as np
import pandas as pd

BASE = pathlib.Path("/Users/mac/Desktop/库/公共数据AF")
OUT = BASE / "out"
rows = []
src = {}

def add(section, key, value, source, script):
    rows.append({"section": section, "key": key, "value": value, "source": source, "script": script})

# --- 数据集规模 ---
cpsc_dx = pd.read_csv(OUT / "cpsc2021_records_dx.csv")
cpsc_sum = json.load(open(OUT / "cpsc2021_window_summary.json"))
add("数据", "PTB-XL 纳入记录数", 2400 - 1, "data/ptbxl_subset_ids.txt（2400 抽样，1 条读取失败）", "make_ptbxl_subset.py")
add("数据", "PTB-XL 训练/内部测试（患者级 7:3）", "1685 / 714", "out/exp_final.log", "run_experiment.py")
add("数据", "CinC2017 纳入记录数", 2537, "out/table_domains.csv", "make_cinc2017_subset.py")
add("数据", "CinC2017 类别分布", "A758/N1000/O500/~279", "data/cinc2017_subset.txt + REFERENCE-v3.csv", "make_cinc2017_subset.py")
add("数据", "CPSC2021 记录数（Set I，已解析诊断）", len(cpsc_dx), "out/cpsc2021_records_dx.csv", "scan_cpsc2021_dx.py")
for k, v in cpsc_dx["dx"].value_counts().items():
    add("数据", f"CPSC2021 诊断={k}", int(v), "out/cpsc2021_records_dx.csv", "scan_cpsc2021_dx.py")
add("数据", "CPSC2021 窗级数据集", f"{cpsc_sum['windows']} 窗 / {cpsc_sum['patients']} 患者（AF {cpsc_sum['af_windows']} / 非AF {cpsc_sum['non_af_windows']}；剔除跨节律窗 {cpsc_sum['skipped']['transition_removed']}）",
    "out/cpsc2021_window_summary.json", "cpsc2021_windows.py")

# --- 主结果（table_domains.csv 为三域权威表）---
dom = pd.read_csv(OUT / "table_domains.csv")
for _, r in dom.iterrows():
    tag = r["domain"]
    add("主结果", f"{tag} · n", int(r["n"]), "out/table_domains.csv", "make_figures_multidomain.py")
    for m in ("auroc", "auprc", "brier", "ece", "se_at_sp90", "mean_pred", "observed"):
        add("主结果", f"{tag} · {m}", round(float(r[m]), 4), "out/table_domains.csv", "make_figures_multidomain.py")

# --- 置信区间与亚组 ---
ci = pd.read_csv(OUT / "table_ci.csv")
for _, r in ci.iterrows():
    for m in ("AUROC", "Brier", "Se@Sp90", "Sp@0.5"):
        add("CI", f"{r['group']} · {m}", f"{r[m]:.3f} [{r[m+'_lo']:.3f}, {r[m+'_hi']:.3f}]", "out/table_ci.csv", "subgroups_ci.py")
sub = pd.read_csv(OUT / "table_subgroups.csv")
for _, r in sub.iterrows():
    add("亚组", f"{r['group']} · AUROC", f"{r['AUROC']:.3f} [{r['AUROC_lo']:.3f}, {r['AUROC_hi']:.3f}]", "out/table_subgroups.csv", "subgroups_ci.py")
    add("亚组", f"{r['group']} · Se@Sp90", f"{r['Se@Sp90']:.3f} [{r['Se@Sp90_lo']:.3f}, {r['Se@Sp90_hi']:.3f}]", "out/table_subgroups.csv", "subgroups_ci.py")

# --- 重校准 ---
re_ = pd.read_csv(OUT / "table_recal_multidomain.csv")
for _, r in re_.iterrows():
    add("重校准", f"{r['domain']} · {r['method']}", f"AUROC {r['auroc']:.3f} / Brier {r['brier']:.3f} / ECE {r['ece']:.3f} / Se@Sp90 {r['se_at_sp90']:.3f}",
        "out/table_recal_multidomain.csv", "recalibrate_multi.py")

# --- 域内参照（results_exp1.json）---
res = json.load(open(OUT / "results_exp1.json"))
for k, v in res.items():
    if isinstance(v, dict) and "auroc" in v:
        add("域内参照/其他", v["dataset"], f"n={v['n']} AUROC {v['auroc']:.3f} Brier {v['brier']:.3f} ECE {v['ece']:.3f} "
            f"Se@Sp90 {v['at_spec90']['sens']:.3f}", "out/results_exp1.json", "run_experiment.py")

# --- 真实患病率下的 PPV/NPV（每个操作点只记一行，避免重复）---
ppv = pd.read_csv(OUT / "table_ppv_npv.csv")
for op in ppv["operating_point"].unique():
    for prev in (0.01, 0.05, 0.20):
        sub = ppv[(ppv["operating_point"] == op) & (np.isclose(ppv["prevalence"], prev))]
        if len(sub):
            s = sub.iloc[0]
            add("PPV/NPV", f"{op} · 患病率{prev:.0%}",
                f"PPV {s['PPV']:.1%} / NPV {s['NPV']:.2%} / 每检出1例需复核 {s['每检出1例需复核阳性例数']:.1f} 例",
                "out/table_ppv_npv.csv", "ppv_npv.py")

df = pd.DataFrame(rows)
json.dump(rows, open(OUT / "numbersheet.json", "w"), ensure_ascii=False, indent=1)

groups = {}
for r in rows:
    groups.setdefault(r["section"], []).append(r)
with open(OUT / "numbersheet.md", "w") as f:
    f.write("# 权威数字表（写作时只从此处取数）\n\n")
    f.write(f"生成时间：见文件 mtime ｜ 共 {len(rows)} 条 ｜ 来源：out/*.csv|json（均为脚本真实运行输出）\n\n")
    for sec, items in groups.items():
        f.write(f"## {sec}\n\n| 项目 | 数值 | 来源文件 | 复现脚本 |\n|---|---|---|---|\n")
        for r in items:
            f.write(f"| {r['key']} | {r['value']} | {r['source']} | {r['script']} |\n")
        f.write("\n")
print(f"numbersheet: {len(rows)} 条 → out/numbersheet.md")
print(pd.DataFrame(rows).groupby('section').size().to_string())
