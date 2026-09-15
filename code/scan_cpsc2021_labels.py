#!/usr/bin/env python3
"""扫描已下载的 CPSC2021 .atr 注释，判定每条记录是否含房颤，并按"患者"汇总。
用途：在只有 .hea/.atr（小文件）的阶段就能决定第二阶段该抓哪些 .dat（833KB/条）。
输出: out/cpsc2021_labels.csv, out/cpsc2021_patient_summary.csv
"""
import collections, glob, json, pathlib, re
import pandas as pd
import wfdb

BASE = pathlib.Path("/Users/mac/Desktop/库/公共数据AF")
DATA = BASE / "data" / "cpsc2021"
OUT = BASE / "out"

rows = []
for setname in ("Training_set_I", "Training_set_II"):
    for atr in sorted(glob.glob(str(DATA / setname / "data_*.atr"))):
        rec = pathlib.Path(atr[:-4]).name
        m = re.match(r"data_(\d+)_(\d+)$", rec)
        patient = m.group(1) if m else "?"
        try:
            ann = wfdb.rdann(str(pathlib.Path(atr[:-4])), "atr")
        except Exception as e:
            rows.append({"set": setname, "rec": rec, "patient": patient, "error": type(e).__name__})
            continue
        notes = [(n or "").upper().lstrip("(").strip() for n in ann.aux_note]
        notes = [n for n in notes if n]
        has_af = any(("AFIB" in n) or ("AFL" in n) for n in notes)
        rows.append({
            "set": setname, "rec": rec, "patient": patient,
            "n_rhythm_ann": len(notes),
            "start_rhythm": notes[0] if notes else "",
            "rhythms": "|".join(sorted(set(notes))[:8]),
            "has_af": int(has_af),
            "atr_size": pathlib.Path(atr).stat().st_size,
        })

df = pd.DataFrame(rows)
df.to_csv(OUT / "cpsc2021_labels.csv", index=False)

ok = df[df.get("error").isna()] if "error" in df.columns else df
if len(ok):
    pat = ok.groupby("patient").agg(recs=("rec", "count"),
                                    af_recs=("has_af", "sum"),
                                    af_frac=("has_af", "mean")).reset_index()
    pat["patient_type"] = pat["af_frac"].map(lambda x: "AF/PAF" if x > 0 else "non-AF")
    pat.to_csv(OUT / "cpsc2021_patient_summary.csv", index=False)
    print("records scanned:", len(ok), " with AF:", int(ok['has_af'].sum()))
    print("patients:", len(pat), " AF-type:", int((pat.patient_type == 'AF/PAF').sum()),
          " non-AF:", int((pat.patient_type == 'non-AF').sum()))
    print(pat.to_string(index=False))
    print("\n心律标签词频（前 15）:")
    cnt = collections.Counter()
    for r in ok["rhythms"]:
        for t in str(r).split("|"):
            if t:
                cnt[t] += 1
    for k, v in cnt.most_common(15):
        print(f"  {k:20s} {v}")
else:
    print("no .atr scanned yet")
