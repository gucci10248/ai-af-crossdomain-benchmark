#!/usr/bin/env python3
"""从 PTB-XL 元数据中挑出 AF 与非 AF 记录，生成按标签平衡的下载清单（子集下载用）。
注意：PTB-XL 的 patient_id/age 在 CSV 里是浮点写法（如 15709.0），必须 int(float())。"""
import csv, ast, json, random, collections, pathlib

BASE = pathlib.Path("/Users/mac/Desktop/库/公共数据AF/data")
random.seed(20260915)
MAX_PER_CLASS = 1200

def to_int(x):
    try:
        return int(float(x))
    except Exception:
        return None

rows = []
with open(BASE / "ptbxl_database.csv", newline="") as f:
    for r in csv.DictReader(f):
        try:
            codes = ast.literal_eval(r["scp_codes"])
        except Exception:
            codes = {}
        age = r["age"].strip()
        rows.append({
            "ecg_id": to_int(r["ecg_id"]),
            "patient_id": to_int(r["patient_id"]),
            "age": float(age) if age not in ("", "nan") else None,
            "sex": r["sex"].strip(),
            "codes": codes,
        })

print("total records in PTB-XL metadata:", len(rows))

af_codes = ("AFIB", "AFLT")
af = [r for r in rows if any(c in r["codes"] for c in af_codes)]
print("AF/AFL records:", len(af))

af_pat = {r["patient_id"] for r in af}
non_af = [r for r in rows if not any(c in r["codes"] for c in af_codes)
          and r["patient_id"] not in af_pat]
print("non-AF (patient-level clean) records:", len(non_af))

# 年龄十岁段 + 性别 1:1 粗匹配，控制混杂
pools = collections.defaultdict(list)
for r in non_af:
    if r["age"] is not None:
        pools[(int(r["age"] // 10), r["sex"])].append(r)

af_ok = [r for r in af if r["age"] is not None][:MAX_PER_CLASS]
selected = []
for r in sorted(af_ok, key=lambda x: x["ecg_id"]):
    key = (int(r["age"] // 10), r["sex"])
    alt = (key[0], "1" if key[1] == "0" else "0")
    cands = pools.get(key) or pools.get(alt) or []
    if cands:
        pick = random.choice(cands)
        cands.remove(pick)
        selected.append(pick)

print("AF used:", len(af_ok), " matched controls:", len(selected))

subset = [dict(r, label=1) for r in af_ok] + [dict(r, label=0) for r in selected]
subset.sort(key=lambda x: x["ecg_id"])

def rec_paths(ecg_id, root):
    folder = f"{(ecg_id - 1) // 1000 * 1000:05d}"
    name = f"{ecg_id:05d}_lr"
    return f"{root}/{folder}/{name}.dat", f"{root}/{folder}/{name}.hea"

with open(BASE / "ptbxl_subset_ids.txt", "w") as f:
    for r in subset:
        f.write(f"{r['ecg_id']},{r['patient_id']},{r['age']},{r['sex']},{r['label']}\n")

with open(BASE / "ptbxl_download_list.txt", "w") as f:
    for r in subset:
        for p in rec_paths(r["ecg_id"], "records100"):
            f.write(p + "\n")

meta = [{"ecg_id": r["ecg_id"], "patient_id": r["patient_id"], "age": r["age"],
         "sex": r["sex"], "label": r["label"], "codes": r["codes"]} for r in subset]
json.dump(meta, open(BASE / "ptbxl_subset_meta.json", "w"), ensure_ascii=False, indent=1)

print("subset total:", len(subset), " AF:", sum(r['label'] for r in subset),
      " controls:", sum(1 for r in subset if r['label'] == 0))
print("files to download:", 2 * len(subset))
