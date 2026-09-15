#!/usr/bin/env python3
"""重建下载清单（修正 CinC2017 路径：训练集实际位于 training/A00/A00001.mat 子目录，
之前按 training/A00001.mat 全部 404）。

产出：
  data/download_urls.txt          全量
  data/download_urls_priority.txt 先试点切片（各 150 阳性/150 阴性），后全量
"""
import pathlib, urllib.request

BASE = pathlib.Path("/Users/mac/Desktop/库/公共数据AF/data")
PTB_BASE = "https://physionet.org/files/ptb-xl/1.0.3/"
C17_BASE = "https://physionet.org/files/challenge-2017/1.0.0/training/"
N_PER_CLASS = 150

# --- CinC2017 记录名 -> 子目录（从官方 RECORDS 获取） ---
rec_path = BASE / "cinc2017_RECORDS.txt"
if not rec_path.exists():
    urllib.request.urlretrieve(C17_BASE + "RECORDS", rec_path)
c17_map = {}
for line in rec_path.read_text().splitlines():
    line = line.strip()
    if not line:
        continue
    rid = line.split("/")[-1]          # A00/A00001 -> A00001
    c17_map[rid] = line                # A00/A00001

c17_ids = [x.strip() for x in open(BASE / "cinc2017_subset.txt") if x.strip()]
lab = {}
for l in open(BASE / "REFERENCE-v3.csv"):
    p = l.strip().split(",")
    if len(p) >= 2:
        lab[p[0]] = p[1]

def c17_pairs(rid):
    rel = c17_map.get(rid)
    if rel is None:
        return []
    return [(f"cinc2017/training/{rel}.mat", C17_BASE + f"{rel}.mat"),
            (f"cinc2017/training/{rel}.hea", C17_BASE + f"{rel}.hea")]

# --- PTB-XL ---
ptb_ids = [l.strip().split(",") for l in open(BASE / "ptbxl_subset_ids.txt") if l.strip()]

def ptb_pairs(eid):
    eid = int(eid)
    folder = f"{(eid - 1) // 1000 * 1000:05d}"
    return [(f"records100/{folder}/{eid:05d}_lr.dat", PTB_BASE + f"records100/{folder}/{eid:05d}_lr.dat"),
            (f"records100/{folder}/{eid:05d}_lr.hea", PTB_BASE + f"records100/{folder}/{eid:05d}_lr.hea")]

ptb_af = [x[0] for x in ptb_ids if x[4] == "1"]
ptb_ct = [x[0] for x in ptb_ids if x[4] == "0"]
c17_a = [r for r in c17_ids if lab.get(r) == "A"]
c17_n = [r for r in c17_ids if lab.get(r) == "N"]

full = []
for eid in ptb_af + ptb_ct:
    full += ptb_pairs(eid)
full += [("ptbxl_database.csv", PTB_BASE + "ptbxl_database.csv"),
         ("scp_statements.csv", PTB_BASE + "scp_statements.csv")]
for rid in c17_ids:
    full += c17_pairs(rid)

pilot = []
for i in range(N_PER_CLASS):
    pilot += ptb_pairs(ptb_af[i])
    pilot += ptb_pairs(ptb_ct[i])
for i in range(N_PER_CLASS):
    pilot += c17_pairs(c17_a[i])
    pilot += c17_pairs(c17_n[i])
pilot += [("ptbxl_database.csv", PTB_BASE + "ptbxl_database.csv"),
          ("scp_statements.csv", PTB_BASE + "scp_statements.csv")]

seen = set()
ordered = []
for item in pilot + full:
    if item[0] in seen:
        continue
    seen.add(item[0])
    ordered.append(item)

for name, items in (("download_urls.txt", full), ("download_urls_priority.txt", ordered)):
    with open(BASE / name, "w") as f:
        for local, url in items:
            f.write(f"{local}\t{url}\n")

print("full:", len(full), " priority-ordered:", len(ordered), " pilot-first:", len(pilot))
print("cinc2017 mapped ids:", len(c17_map), " subset:", len(c17_ids))
