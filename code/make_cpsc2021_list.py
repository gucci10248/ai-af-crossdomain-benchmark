#!/usr/bin/env python3
"""CPSC2021（第 4 届中国生理信号挑战赛，阵发性房颤动态 ECG，中国人群，CC-BY）下载清单。
第一阶段只抓 .hea + .atr（每个约 0.2KB / 2.5KB），先从心律注释里判定每条记录是否含房颤，
再决定第二阶段抓哪些 .dat（每条约 833KB，必须按需抓）。
用法: python3 make_cpsc2021_list.py <files_list.txt> [--with-dat "data_0_1,data_0_5,..."]
"""
import pathlib, sys

BASE = pathlib.Path("/Users/mac/Desktop/库/公共数据AF/data")
URL = "https://physionet.org/files/cpsc2021/1.0.0/Training_set_I/"
files = [l.strip() for l in open(sys.argv[1]) if l.strip()]

meta = [f for f in files if f.endswith(".hea") or f.endswith(".atr")]
with open(BASE / "cpsc2021_urls_meta.txt", "w") as f:
    for name in meta:
        f.write(f"cpsc2021/Training_set_I/{name}\t{URL}{name}\n")
print("meta files (.hea/.atr):", len(meta))

if len(sys.argv) > 3 and sys.argv[2] == "--with-dat":
    want = set(sys.argv[3].split(","))
    n = 0
    with open(BASE / "cpsc2021_urls_dat.txt", "w") as f:
        for name in files:
            if name.endswith(".dat") and name[:-4] in want:
                f.write(f"cpsc2021/Training_set_I/{name}\t{URL}{name}\n")
                n += 1
    print("dat files:", n)
