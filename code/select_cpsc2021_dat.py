#!/usr/bin/env python3
"""按"患者级 + 平衡"原则挑选 CPSC2021 需要下载 .dat 的记录（每条 833KB，必须省着下）。
输出: data/cpsc2021_urls_dat.txt
"""
import pathlib
import pandas as pd

BASE = pathlib.Path("/Users/mac/Desktop/库/公共数据AF")
DATA = BASE / "data"
OUT = BASE / "out"
URL = "https://physionet.org/files/cpsc2021/1.0.0/Training_set_I/"
N_AF_PAT, N_NONAF_PAT, PER_PAT = 8, 8, 4

lab = pd.read_csv(OUT / "cpsc2021_labels.csv")
pat = pd.read_csv(OUT / "cpsc2021_patient_summary.csv")
lab = lab[lab["set"] == "Training_set_I"].dropna(subset=["rec"])
pat = pat.sort_values("patient")

af_pats = [p for p in pat[pat.patient_type == "AF/PAF"]["patient"]][:N_AF_PAT]
non_pats = [p for p in pat[pat.patient_type == "non-AF"]["patient"]][:N_NONAF_PAT]

picked = []
for p in af_pats:
    rows = lab[(lab["patient"] == p) & (lab["has_af"] == 1)].head(PER_PAT)
    picked += list(rows["rec"])
for p in non_pats:
    rows = lab[(lab["patient"] == p)].head(PER_PAT)
    picked += list(rows["rec"])
# 另补两位 PAF（有房颤也有非房颤记录）的患者，用于检验"同患者窗级标注"的稳定性
for p in pat[pat.patient_type == "AF/PAF"]["patient"][N_AF_PAT:N_AF_PAT + 2]:
    rows = lab[(lab["patient"] == p)].head(PER_PAT)
    picked += list(rows["rec"])

picked = sorted(set(picked))
with open(DATA / "cpsc2021_urls_dat.txt", "w") as f:
    for rec in picked:
        f.write(f"cpsc2021/Training_set_I/{rec}.dat\t{URL}{rec}.dat\n")

est_mb = len(picked) * 833 / 1024
print(f"AF-type patients: {af_pats}")
print(f"non-AF patients:  {non_pats}")
print(f"records selected: {len(picked)}  (~{est_mb:.0f} MB)")
print("preview:", picked[:8])
