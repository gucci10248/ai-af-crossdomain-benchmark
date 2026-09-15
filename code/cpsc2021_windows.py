#!/usr/bin/env python3
"""把 CPSC2021（中国，动态 ECG）切成不重叠 30 秒窗并按诊断/心律注释打房颤标签，
输出与 PTB-XL / CinC2017 同口径的特征表（"中国外部域"）。

标注策略（**关键**：诊断写在 .hea 注释里，不是只有 .atr 有）：
    # non atrial fibrillation        → 全部窗判阴性
    # persistent atrial fibrillation → 全部窗判阳性
    # paroxysmal atrial fibrillation → 用 .atr 心律变迁注释逐窗判定
                                       （只认 '(AFIB'/'(AFL'/'(N' 这类真注释；
                                        被写成字符串 'None'/'' 的节拍注释一律忽略）
其他规则：窗内发生节律转变 → 剔除；未知诊断 → 整条跳过。

用法:
    python3 cpsc2021_windows.py [--sets I,II] [--max-per-patient 20] [--window 30]
"""
import argparse, glob, json, pathlib, re, sys, collections
import numpy as np
import pandas as pd
import wfdb

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from features import extract  # noqa

BASE = pathlib.Path("/Users/mac/Desktop/库/公共数据AF")
DATA = BASE / "data" / "cpsc2021"
OUT = BASE / "out"
OUT.mkdir(exist_ok=True)


def read_dx(hea_path):
    txt = pathlib.Path(hea_path).read_text(errors="ignore")
    c = ""
    for line in txt.splitlines():
        if line.startswith("#"):
            c = line.lstrip("#").strip().lower()
    if "paroxysmal atrial fibrillation" in c:
        return "paroxysmalAF"
    if "persistent atrial fibrillation" in c:
        return "persistentAF"
    if "non atrial fibrillation" in c:
        return "nonAF"
    return "unknown"


def parse_note(note):
    """把注释文本映射成 'af' / 'non_af' / None(忽略)。"""
    if note is None:
        return None
    u = str(note).strip()
    if u == "" or u.lower() in ("none", "nan"):
        return None                       # 节拍注释被写成 'None' 的情况
    u = u.lstrip("(").strip().upper()
    if "AFIB" in u or "AFL" in u:
        return "af"
    if u in ("N", "NSR", "SR", "NONE", "SINUS", "SINUS RHYTHM"):
        return "non_af"
    return None                            # 其他节律（房速/室性等）不参与主分析


def read_events(rec_path):
    try:
        ann = wfdb.rdann(str(rec_path), "atr")
    except Exception:
        return []
    ev = []
    for s, note in zip(ann.sample, ann.aux_note):
        lab = parse_note(note)
        if lab:
            ev.append((int(s), lab))
    # 去重相邻重复
    ded = []
    for s, l in sorted(ev):
        if not ded or ded[-1][1] != l:
            ded.append((s, l))
    return ded


def window_labels(dx, ev, fs, n_samples, win_s=30):
    """返回 (labels, n_dropped_transition)。labels: 1/0/None(剔除)。"""
    win = int(win_s * fs)
    n_win = n_samples // win
    if dx == "nonAF":
        return [0] * n_win, 0
    if dx == "persistentAF":
        return [1] * n_win, 0
    # paroxysmal：按变迁注释逐窗判定
    labels, dropped = [], 0
    for i in range(n_win):
        a, b = i * win, (i + 1) * win
        inside = [l for s, l in ev if a <= s < b]
        if inside:                      # 窗内发生节律转变 → 剔除
            labels.append(None); dropped += 1; continue
        state = None
        for s, l in ev:
            if s < a:
                state = l
        if state is None:
            labels.append(None); dropped += 1
        else:
            labels.append(1 if state == "af" else 0)
    return labels, dropped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", default="I")
    ap.add_argument("--max-per-patient", type=int, default=24)
    ap.add_argument("--window", type=int, default=30)
    args = ap.parse_args()

    rows, skip_stat, pat_count, dx_count = [], collections.Counter(), collections.Counter(), collections.Counter()
    recs = []
    for s in args.sets.split(","):
        recs += sorted(glob.glob(str(DATA / f"Training_set_{s.strip()}" / "data_*.hea")))
    print(f"records with .hea: {len(recs)}")

    for k, hea in enumerate(recs):
        rec_path = pathlib.Path(hea[:-4])
        if not pathlib.Path(str(rec_path) + ".dat").is_file():
            skip_stat["no_dat"] += 1
            continue
        m = re.match(r"data_(\d+)_(\d+)$", rec_path.name)
        patient = m.group(1) if m else rec_path.name
        dx = read_dx(hea)
        if dx == "unknown":
            skip_stat["unknown_dx"] += 1
            continue
        try:
            r = wfdb.rdrecord(str(rec_path))
        except Exception:
            skip_stat["signal_fail"] += 1
            continue
        sig, fs = r.p_signal, float(r.fs)
        ev = read_events(rec_path) if dx == "paroxysmalAF" else []
        if dx == "paroxysmalAF" and not ev:
            skip_stat["paf_without_ann"] += 1
            continue
        labels, dropped = window_labels(dx, ev, fs, sig.shape[0], win_s=args.window)
        skip_stat["transition_removed"] += dropped
        win = int(args.window * fs)
        for i, lab in enumerate(labels):
            if lab is None:
                continue
            if pat_count[patient] >= args.max_per_patient:
                skip_stat["over_patient_cap"] += 1
                break
            seg = sig[i * win:(i + 1) * win, 0]
            f = extract(seg, fs, lead=None)
            if f is None:
                skip_stat["feat_fail"] += 1
                continue
            rows.append({"rec_id": rec_path.name, "patient": patient, "dx": dx,
                         "window_idx": i, "start_s": i * args.window, "label": lab,
                         **{("f_" + kk): vv for kk, vv in f.items()}})
            pat_count[patient] += 1
            dx_count[dx] += 1
        if (k + 1) % 25 == 0:
            print(f"  {k+1}/{len(recs)} | windows={len(rows)} | {dict(skip_stat)}", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "feat_cpsc2021.csv", index=False)
    summary = {"records_scanned": len(recs), "windows": int(len(df)),
               "af_windows": int((df["label"] == 1).sum()) if len(df) else 0,
               "non_af_windows": int((df["label"] == 0).sum()) if len(df) else 0,
               "patients": int(df["patient"].nunique()) if len(df) else 0,
               "by_dx": dict(dx_count), "skipped": dict(skip_stat)}
    json.dump(summary, open(OUT / "cpsc2021_window_summary.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
