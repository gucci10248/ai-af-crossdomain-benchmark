#!/usr/bin/env python3
"""CPSC2021 第二阶段 .dat 选取 v2：
  - 用 .hea 诊断（nonAF / persistentAF / paroxysmalAF）做分层
  - 偏好"短记录"（省带宽：.dat 大小随时长线性增长）
  - 患者级分组，禁止同一患者跨域
输出: data/cpsc2021_urls_dat2.txt
"""
import pathlib
import pandas as pd

BASE = pathlib.Path("/Users/mac/Desktop/库/公共数据AF")
DATA = BASE / "data"
OUT = BASE / "out"
URL = "https://physionet.org/files/cpsc2021/1.0.0/Training_set_I/"

N_NON, N_PERS, N_PARA, PER = 8, 5, 8, 3
DUR_MIN, DUR_MAX = 4, 18      # 分钟：太短窗太少，太长费带宽

df = pd.read_csv(OUT / "cpsc2021_records_dx.csv")
df = df[(df["set"] == "Training_set_I") & df["dur_min"].between(DUR_MIN, DUR_MAX)].copy()
df["mb"] = df["dur_min"] * 60 * 200 * 2 * 2 / 1e6      # 200Hz × 2 导 × 2 字节

pat = pd.read_csv(OUT / "cpsc2021_patient_dx.csv")
af_pat = set(pat[pat.patient_type == "persistentAF"]["patient"])
mixed_pat = set(pat[pat.patient_type == "mixed"]["patient"])
non_pat = set(pat[pat.patient_type == "nonAF"]["patient"])

picked, summary = [], {}
for tag, pats, n_pat in [("nonAF", non_pat, N_NON),
                         ("persistentAF", af_pat, N_PERS),
                         ("paroxysmal(mixed)", mixed_pat, N_PARA)]:
    used = 0
    for p in sorted(pats):
        if used >= n_pat:
            break
        sub = df[df["patient"] == p]
        sub = sub[sub["dx"].isin(["nonAF"] if tag == "nonAF" else ["paroxysmalAF", "persistentAF"])]
        sub = sub.sort_values("mb").head(PER)
        if len(sub) < 2:
            continue
        picked += list(sub["rec"])
        used += 1
    summary[tag] = used
print("患者入选数:", summary)

picked = sorted(set(picked))
already = {p.stem for p in (DATA / "cpsc2021" / "Training_set_I").glob("*.dat")}
todo = [r for r in picked if r not in already]
est = df[df["rec"].isin(todo)]["mb"].sum()
with open(DATA / "cpsc2021_urls_dat2.txt", "w") as f:
    for rec in todo:
        f.write(f"cpsc2021/Training_set_I/{rec}.dat\t{URL}{rec}.dat\n")
print(f"选中 {len(picked)} 条；已存在 {len(picked)-len(todo)} 条；待下 {len(todo)} 条 ≈ {est:.0f} MB")
