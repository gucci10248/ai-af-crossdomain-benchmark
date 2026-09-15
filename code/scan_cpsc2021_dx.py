#!/usr/bin/env python3
"""CPSC2021 记录级诊断标签解析（关键发现：诊断写在 .hea 注释里，而不是只在 .atr 里）。

.hea 末行形如：
    # non atrial fibrillation / # persistent atrial fibrillation / # paroxysmal atrial fibrillation
窗口标注策略：
    non-AF       → 整条记录所有 30 秒窗判阴性
    persistentAF → 整条记录所有窗判阳性
    paroxysmalAF → 用 .atr 的心律变迁注释逐窗判定（只认 '(AFIB' / '(AFL' / '(N' 这类真注释，
                  忽略被写成字符串 'None'/'' 的节拍注释）
输出: out/cpsc2021_records_dx.csv, out/cpsc2021_patient_dx.csv
"""
import glob, pathlib, re, collections
import pandas as pd

BASE = pathlib.Path("/Users/mac/Desktop/库/公共数据AF")
DATA = BASE / "data" / "cpsc2021"
OUT = BASE / "out"

DX_MAP = [
    ("paroxysmal atrial fibrillation", "paroxysmalAF"),
    ("persistent atrial fibrillation", "persistentAF"),
    ("non atrial fibrillation", "nonAF"),
]

rows = []
for hea in sorted(glob.glob(str(DATA / "Training_set_*" / "data_*.hea"))):
    p = pathlib.Path(hea)
    txt = p.read_text(errors="ignore")
    comment = ""
    for line in txt.splitlines():
        if line.startswith("#"):
            comment = line.lstrip("#").strip()
    dx = "unknown"
    for key, val in DX_MAP:
        if key in comment.lower():
            dx = val
            break
    m = re.match(r"data_(\d+)_(\d+)$", p.stem)
    head = txt.splitlines()[0].split()
    try:
        fs = float(head[2]); n = int(head[3])
        dur_min = n / fs / 60
    except Exception:
        dur_min = float("nan")
    rows.append({"set": p.parent.name, "rec": p.stem, "patient": m.group(1) if m else "?",
                 "dx": dx, "comment": comment, "dur_min": round(dur_min, 1)})

df = pd.DataFrame(rows)
df.to_csv(OUT / "cpsc2021_records_dx.csv", index=False)
print("records:", len(df))
print(df.groupby(["set", "dx"]).size().to_string())

pat = df.groupby("patient").agg(recs=("rec", "count"),
                                dx_set=("dx", lambda s: "|".join(sorted(set(s)))))
pat["patient_type"] = pat["dx_set"].map(lambda s: "mixed" if "|" in s else s)
pat.to_csv(OUT / "cpsc2021_patient_dx.csv")
print("\n患者类型分布:")
print(pat["patient_type"].value_counts().to_string())
print("\n各类型可用的短记录（时长 ≤ 25 分钟）数量:")
short = df[df.dur_min <= 25]
print(short.groupby("dx").size().to_string())
