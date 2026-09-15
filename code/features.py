#!/usr/bin/env python3
"""特征提取：单导联 ECG / PPG 通用的心率变异性(HRV)+节律不规则度+频谱特征。
用于房颤检测基线（不依赖深度学习，几秒即可跑完数千条记录）。"""
import numpy as np
from scipy import signal as sg


def bandpass(x, fs, lo, hi, order=3):
    nyq = fs / 2.0
    b, a = sg.butter(order, [lo / nyq, hi / nyq], btype="band")
    return sg.filtfilt(b, a, x)


def detect_rpeaks(x, fs):
    """简化 Pan-Tompkins：带通 5-15Hz -> 平方 -> 滑动平均 -> 峰值检测。"""
    x = np.asarray(x, dtype=float)
    x = x - np.nanmean(x)
    y = bandpass(x, fs, 5.0, min(15.0, fs / 2 - 1))
    y = y ** 2
    win = max(1, int(0.15 * fs))
    y = np.convolve(y, np.ones(win) / win, mode="same")
    thr = np.nanmean(y) + 0.5 * np.nanstd(y)
    min_dist = int(0.25 * fs)
    peaks, _ = sg.find_peaks(y, height=thr, distance=max(1, min_dist))
    return peaks


def rr_from_peaks(peaks, fs):
    if len(peaks) < 3:
        return np.array([])
    rr = np.diff(peaks) / float(fs)
    rr = rr[(rr > 0.25) & (rr < 2.5)]
    return rr


def sample_entropy(x, m=2, r_factor=0.2):
    """样本熵（点数少时很快）。"""
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < m + 2:
        return np.nan
    r = r_factor * np.std(x)
    if r == 0:
        return np.nan

    def phi(mm):
        k = n - mm
        if k <= 1:
            return np.nan
        templates = np.lib.stride_tricks.sliding_window_view(x, mm)
        cnt = 0
        for i in range(k):
            d = np.max(np.abs(templates[i + 1:] - templates[i]), axis=1)
            cnt += 2 * np.sum(d <= r)
        return cnt / (k * (k - 1)) if k > 1 else np.nan

    a, b = phi(m + 1), phi(m)
    if not a or not b or b <= 0:
        return np.nan
    return float(-np.log(a / b))


def spectral_features(rr):
    """基于 RR 间期序列（重采样到 4Hz）的频域特征。"""
    out = dict(dom_freq=np.nan, spec_ent=np.nan, lf_hf=np.nan, hf_pow=np.nan, lf_pow=np.nan)
    if len(rr) < 8:
        return out
    t = np.cumsum(rr)
    t = t - t[0]
    fs_i = 4.0
    if t[-1] <= 1.0:
        return out
    tt = np.arange(0, t[-1], 1.0 / fs_i)
    try:
        rr_i = np.interp(tt, t[:-1], rr[1:])
    except Exception:
        return out
    rr_i = rr_i - rr_i.mean()
    f, pxx = sg.welch(rr_i, fs=fs_i, nperseg=min(len(rr_i), 256))
    if pxx.sum() <= 0:
        return out
    out["dom_freq"] = float(f[(pxx > 0).argmax()]) if (pxx > 0).any() else np.nan
    p = pxx / pxx.sum()
    p = p[p > 0]
    out["spec_ent"] = float(-np.sum(p * np.log(p)))
    lf = pxx[(f >= 0.04) & (f < 0.15)].sum()
    hf = pxx[(f >= 0.15) & (f < 0.4)].sum()
    out["lf_pow"], out["hf_pow"] = float(lf), float(hf)
    out["lf_hf"] = float(lf / hf) if hf > 0 else np.nan
    return out


def signal_features(x, fs):
    """波形层面的粗糙度/熵特征（房颤时 f 波使波形更不规则）。"""
    x = np.asarray(x, dtype=float)
    x = x - np.nanmean(x)
    sd = np.nanstd(x) or 1.0
    z = x / sd
    hist, _ = np.histogram(z, bins=50, density=False)
    p = hist / max(1, hist.sum())
    p = p[p > 0]
    shannon = float(-np.sum(p * np.log(p)))
    feats = dict(
        sig_kurt=float(np.nanmean(z ** 4)),
        sig_skew=float(np.nanmean(z ** 3)),
        sig_shannon=shannon,
    )
    for lo, hi, name in [(0.5, 5, "bp_0p5_5"), (5, 15, "bp_5_15"), (15, 40, "bp_15_40")]:
        if hi >= fs / 2:
            continue
        b, a = sg.butter(3, [lo / (fs / 2), hi / (fs / 2)], btype="band")
        y = sg.filtfilt(b, a, x)
        feats[f"pow_{name}"] = float(np.nanmean(y ** 2))
    return feats


def extract(sig, fs, lead=None):
    """sig: 1-D 单导联信号（已选定导联）或 2-D (n, nlead)。"""
    sig = np.asarray(sig, dtype=float)
    if sig.ndim == 2:
        sig = sig[:, 0] if lead is None else sig[:, lead]
    sig = sig.flatten()
    if fs <= 0 or sig.size < fs:      # 少于 1 秒直接判定不可分析
        return None
    feats = {}
    peaks = detect_rpeaks(sig, fs)
    rr = rr_from_peaks(peaks, fs)
    feats["n_beats"] = len(peaks)
    feats["quality_rr_frac"] = len(rr) / max(1, len(peaks) - 1)
    if len(rr) >= 4:
        drr = np.diff(rr)
        feats.update(
            rr_mean=float(np.mean(rr)),
            rr_median=float(np.median(rr)),
            rr_sd=float(np.std(rr, ddof=1)),
            rr_cv=float(np.std(rr, ddof=1) / np.mean(rr)),
            rr_iqr=float(np.percentile(rr, 75) - np.percentile(rr, 25)),
            rr_range=float(np.max(rr) - np.min(rr)),
            rmssd=float(np.sqrt(np.mean(drr ** 2))),
            rmssd_norm=float(np.sqrt(np.mean(drr ** 2)) / np.mean(rr)),
            pnn50=float(np.mean(np.abs(drr) > 0.05)),
            pnn20=float(np.mean(np.abs(drr) > 0.02)),
            drr_sd=float(np.std(drr, ddof=1)) if len(drr) > 1 else np.nan,
            hrv_ratio=float(np.std(rr, ddof=1) / (np.mean(np.abs(drr)) + 1e-9)),
            sd1=float(np.sqrt(0.5) * np.std(drr, ddof=1)) if len(drr) > 1 else np.nan,
            sd2=float(np.sqrt(2.0 * np.var(rr, ddof=1) - 0.5 * np.var(drr, ddof=1))),
            rr_skew=float(np.mean(((rr - rr.mean()) / (rr.std() + 1e-9)) ** 3)),
            rr_kurt=float(np.mean(((rr - rr.mean()) / (rr.std() + 1e-9)) ** 4)),
            sampen=float(sample_entropy(rr, m=2)),
        )
        feats["sd1_sd2"] = feats["sd1"] / feats["sd2"] if feats["sd2"] else np.nan
        feats.update(spectral_features(rr))
    else:
        for k in ["rr_mean", "rr_median", "rr_sd", "rr_cv", "rr_iqr", "rr_range", "rmssd",
                  "rmssd_norm", "pnn50", "pnn20", "drr_sd", "hrv_ratio", "sd1", "sd2",
                  "rr_skew", "rr_kurt", "sampen", "sd1_sd2", "dom_freq", "spec_ent",
                  "lf_hf", "hf_pow", "lf_pow"]:
            feats[k] = np.nan
    feats.update(signal_features(sig, fs))
    return feats
