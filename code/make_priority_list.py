#!/usr/bin/env python3
"""重排下载队列：先保证一个"小规模但标签平衡"的试点切片落地（约 1200 个文件），
其余文件排在其后。用于把本机约 20 KB/s 的国际带宽优先花在能立刻跑起来的数据上。"""
import pathlib, collections

BASE = pathlib.Path("/Users/mac/Desktop/库/公共数据AF/data")
lines = [l.rstrip("\n") for l in open(BASE / "download_urls.txt") if l.strip()]
entries = [tuple(l.split("\t")) for l in lines]

N_PER_CLASS = 150  # 每个数据集各取 150 例阳性 + 150 例阴性

ptb_ids = [l.strip().split(",") for l in open(BASE / "ptbxl_subset_ids.txt") if l.strip()]
ptb_af = [x[0] for x in ptb_ids if x[4] == "1"][:N_PER_CLASS]
ptb_ct = [x[0] for x in ptb_ids if x[4] == "0"][:N_PER_CLASS]

c17 = [x.strip() for x in open(BASE / "cinc2017_subset.txt") if x.strip()]
lab = {}
for l in open(BASE / "REFERENCE-v3.csv"):
    p = l.strip().split(",")
    if len(p) >= 2:
        lab[p[0]] = p[1]
c17_a = [r for r in c17 if lab.get(r) == "A"][:N_PER_CLASS]
c17_n = [r for r in c17 if lab.get(r) == "N"][:N_PER_CLASS]

def ptb_files(eid):
    folder = f"{(int(eid) - 1) // 1000 * 1000:05d}"
    return [f"records100/{folder}/{int(eid):05d}_lr.dat", f"records100/{folder}/{int(eid):05d}_lr.hea"]

pilot_names = []
for i in range(N_PER_CLASS):
    pilot_names += ptb_files(ptb_af[i])
    pilot_names += ptb_files(ptb_ct[i])
pilot_names += ["ptbxl_database.csv", "scp_statements.csv"]
for i in range(N_PER_CLASS):
    pilot_names += [f"cinc2017/training/{c17_a[i]}.mat", f"cinc2017/training/{c17_a[i]}.hea"]
    pilot_names += [f"cinc2017/training/{c17_n[i]}.mat", f"cinc2017/training/{c17_n[i]}.hea"]

pilot_set = set(pilot_names)
by_name = {local: url for local, url in entries}
missing = [n for n in pilot_names if n not in by_name]
print("pilot entries:", len(pilot_names), "missing from url list:", len(missing))

ordered = [n for n in pilot_names if n in by_name] + [local for local, _ in entries if local not in pilot_set]
out = open(BASE / "download_urls_priority.txt", "w")
for local in ordered:
    out.write(f"{local}\t{by_name[local]}\n")
out.close()
print("priority list written:", len(ordered), "files (pilot first:", len(pilot_set), ")")
