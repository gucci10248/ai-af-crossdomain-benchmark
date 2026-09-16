#!/usr/bin/env python3
"""多种子稳健性汇总：读取 out_robustness/seed_*/results_exp1.json，
对关键域×关键指标给出 seed0 值、6 种子均值±SD、min–max 区间。
输出：out_robustness/robustness_summary.csv / .md
用法：python code/aggregate_robustness.py
"""
import json
import pathlib

import pandas as pd

BASE = pathlib.Path("/Users/mac/Desktop/库/公共数据AF")
ROB = BASE / "out_robustness"

KEYS = {
    "ptbxl_internal_hgb": "内部 PTB-XL（患者级划分）",
    "cinc2017_external_from_hgb": "外部1 CinC2017（可穿戴单导联）",
    "cinc2017_external_strict_hgb": "外部1a CinC2017 严格 A vs N",
    "cpsc2021_external_hgb": "外部2 CPSC2021（中国动态 ECG）",
    "cinc2017_internal_5fold": "CinC2017 域内 5 折参照",
    "cpsc2021_internal_5fold": "CPSC2021 域内分组 5 折参照",
}
METRICS = [("auroc", "AUROC"), ("auprc", "AUPRC"), ("brier", "Brier"), ("ece", "ECE")]


def get_metric(res, m):
    return res[m]


def main():
    seeds = sorted(p.name for p in ROB.glob("seed_*") if (p / "results_exp1.json").exists())
    assert seeds, "未找到 out_robustness/seed_*/results_exp1.json"
    runs = {s: json.load(open(ROB / s / "results_exp1.json")) for s in seeds}

    rows = []
    for key, label in KEYS.items():
        if key not in runs[seeds[0]]:
            continue
        for m, mlabel in METRICS:
            vals = [get_metric(runs[s][key], m) for s in seeds if key in runs[s]]
            se90 = [runs[s][key]["at_spec90"]["sens"] for s in seeds if key in runs[s]]
            if m == "auroc":  # 每个域顺带记一行 Se@Sp90
                rows.append({"domain": label, "metric": "Se@Sp90", "seed0": se90[0],
                             "mean": sum(se90) / len(se90),
                             "sd": pd.Series(se90).std(ddof=1),
                             "min": min(se90), "max": max(se90), "n_seeds": len(se90)})
            rows.append({"domain": label, "metric": mlabel, "seed0": vals[0],
                         "mean": sum(vals) / len(vals),
                         "sd": pd.Series(vals).std(ddof=1),
                         "min": min(vals), "max": max(vals), "n_seeds": len(vals)})

    df = pd.DataFrame(rows)
    df.to_csv(ROB / "robustness_summary.csv", index=False)

    lines = ["# 多种子稳健性汇总（6 个种子：seed0 为论文权威值，seed1–5 变动模型种子与患者级划分种子）",
             "",
             "| 域 | 指标 | seed0（论文值） | 均值±SD | min–max |",
             "|---|---|---|---|---|"]
    for _, r in df.iterrows():
        lines.append(f"| {r['domain']} | {r['metric']} | {r['seed0']:.4f} | "
                     f"{r['mean']:.4f}±{r['sd']:.4f} | {r['min']:.4f}–{r['max']:.4f} |")
    (ROB / "robustness_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(df.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print("\n已写入:", ROB / "robustness_summary.csv / .md")


if __name__ == "__main__":
    main()
