#!/usr/bin/env python3
"""生成 PTB-XL(1.0.3) 子集与 CinC2017 训练集的 curl 并行下载清单。"""
import pathlib

BASE = pathlib.Path("/Users/mac/Desktop/库/公共数据AF/data")
PTB_BASE = "https://physionet.org/files/ptb-xl/1.0.3/"
C17_BASE = "https://physionet.org/files/challenge-2017/1.0.0/training/"

# --- PTB-XL 子集 ---
urls = []
for line in open(BASE / "ptbxl_download_list.txt"):
    p = line.strip()
    if p:
        urls.append((p, PTB_BASE + p))
# 必需的小文件
urls.append(("ptbxl_database.csv", PTB_BASE + "ptbxl_database.csv"))
urls.append(("scp_statements.csv", PTB_BASE + "scp_statements.csv"))
with open(BASE / "ptbxl_urls.txt", "w") as f:
    for local, url in urls:
        f.write(f"{local}\t{url}\n")

# --- CinC 2017 训练集（8,528 条，单导联 30 秒，AliveCor 可穿戴域） ---
c17 = []
for i in range(1, 8529):
    rid = f"A{i:05d}"
    c17.append((f"cinc2017/training/{rid}.mat", C17_BASE + f"{rid}.mat"))
    c17.append((f"cinc2017/training/{rid}.hea", C17_BASE + f"{rid}.hea"))
with open(BASE / "cinc2017_urls.txt", "w") as f:
    for local, url in c17:
        f.write(f"{local}\t{url}\n")

print("ptb-xl files:", len(urls), " cinc2017 files:", len(c17))
