#!/usr/bin/env python3
"""生成 CinC2017（AliveCor 单导联可穿戴，30 秒）分层子集下载清单。
标签：N 正常、A 房颤、O 其他节律、~ 噪声。"""
import csv, pathlib, collections

BASE = pathlib.Path("/Users/mac/Desktop/库/公共数据AF/data")
C17_BASE = "https://physionet.org/files/challenge-2017/1.0.0/training/"
PTB_BASE = "https://physionet.org/files/ptb-xl/1.0.3/"
CAP = {"A": 100000, "N": 1000, "O": 500, "~": 300}   # A 全取

labels = {}
with open(BASE / "REFERENCE-v3.csv", newline="") as f:
    for row in csv.reader(f):
        if len(row) >= 2:
            labels[row[0].strip()] = row[1].strip()

counts = collections.Counter(labels.values())
print("CinC2017 label distribution:", dict(counts))

picked = []
taken = collections.Counter()
for rid in sorted(labels):
    lab = labels[rid]
    if taken[lab] < CAP.get(lab, 0):
        picked.append(rid)
        taken[lab] += 1
print("picked:", len(picked), dict(taken))

urls = []
for rid in picked:
    urls.append((f"cinc2017/training/{rid}.mat", C17_BASE + f"{rid}.mat"))
    urls.append((f"cinc2017/training/{rid}.hea", C17_BASE + f"{rid}.hea"))

# PTB-XL 子集 + 元数据
for line in open(BASE / "ptbxl_download_list.txt"):
    p = line.strip()
    if p:
        urls.append((p, PTB_BASE + p))
urls.append(("ptbxl_database.csv", PTB_BASE + "ptbxl_database.csv"))
urls.append(("scp_statements.csv", PTB_BASE + "scp_statements.csv"))

with open(BASE / "download_urls.txt", "w") as f:
    for local, url in urls:
        f.write(f"{local}\t{url}\n")
with open(BASE / "cinc2017_subset.txt", "w") as f:
    f.write("\n".join(picked) + "\n")

print("total files queued:", len(urls))
