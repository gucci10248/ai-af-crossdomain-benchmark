# 数字出处审计 v2（权威值池 + 同源一致性回归）

权威值池（numbersheet.json）数值个数：342

## A. 同源一致性（exp1 vs table_domains vs table_ci，容差 5e-4）
- ✅ 内部：PTB-XL（德国 12 导联） · auroc: exp1=0.974400 vs domains/ci=0.974400 (|Δ|=0.00e+00)
- ✅ 内部：PTB-XL（德国 12 导联） · auprc: exp1=0.971970 vs domains/ci=0.971970 (|Δ|=1.11e-16)
- ✅ 内部：PTB-XL（德国 12 导联） · brier: exp1=0.069266 vs domains/ci=0.069266 (|Δ|=5.55e-17)
- ✅ 内部：PTB-XL（德国 12 导联） · ece: exp1=0.064924 vs domains/ci=0.064924 (|Δ|=4.16e-17)
- ✅ 内部：PTB-XL（德国 12 导联） · se_at_sp90: exp1=0.945205 vs domains/ci=0.945205 (|Δ|=0.00e+00)
- ✅ 外部 1：CinC2017（消费级单导联） · auroc: exp1=0.885496 vs domains/ci=0.885496 (|Δ|=0.00e+00)
- ✅ 外部 1：CinC2017（消费级单导联） · auprc: exp1=0.701484 vs domains/ci=0.701484 (|Δ|=0.00e+00)
- ✅ 外部 1：CinC2017（消费级单导联） · brier: exp1=0.220735 vs domains/ci=0.220735 (|Δ|=8.33e-17)
- ✅ 外部 1：CinC2017（消费级单导联） · ece: exp1=0.225398 vs domains/ci=0.225398 (|Δ|=5.55e-17)
- ✅ 外部 1：CinC2017（消费级单导联） · se_at_sp90: exp1=0.585752 vs domains/ci=0.585752 (|Δ|=0.00e+00)
- ✅ 外部 2：CPSC2021（中国动态 ECG） · auroc: exp1=0.946146 vs domains/ci=0.946146 (|Δ|=0.00e+00)
- ✅ 外部 2：CPSC2021（中国动态 ECG） · auprc: exp1=0.891792 vs domains/ci=0.891792 (|Δ|=0.00e+00)
- ✅ 外部 2：CPSC2021（中国动态 ECG） · brier: exp1=0.128084 vs domains/ci=0.128084 (|Δ|=5.55e-17)
- ✅ 外部 2：CPSC2021（中国动态 ECG） · ece: exp1=0.143260 vs domains/ci=0.143260 (|Δ|=0.00e+00)
- ✅ 外部 2：CPSC2021（中国动态 ECG） · se_at_sp90: exp1=0.871429 vs domains/ci=0.871429 (|Δ|=0.00e+00)
- ✅ CI表 内部：PTB-XL（德国12导） · AUROC: exp1=0.974400 vs domains/ci=0.974400 (|Δ|=0.00e+00)
- ✅ CI表 内部：PTB-XL（德国12导） · Se@Sp90: exp1=0.945205 vs domains/ci=0.945205 (|Δ|=0.00e+00)
- ✅ CI表 内部：PTB-XL（德国12导） · Brier: exp1=0.069266 vs domains/ci=0.069266 (|Δ|=0.00e+00)
- ✅ CI表 外部1：CinC2017 全部（A vs 非A） · AUROC: exp1=0.885496 vs domains/ci=0.885496 (|Δ|=0.00e+00)
- ✅ CI表 外部1：CinC2017 全部（A vs 非A） · Se@Sp90: exp1=0.585752 vs domains/ci=0.585752 (|Δ|=0.00e+00)
- ✅ CI表 外部1：CinC2017 全部（A vs 非A） · Brier: exp1=0.220735 vs domains/ci=0.220735 (|Δ|=0.00e+00)
- ✅ CI表 外部2：CPSC2021（中国，30秒窗） · AUROC: exp1=0.946146 vs domains/ci=0.946146 (|Δ|=0.00e+00)
- ✅ CI表 外部2：CPSC2021（中国，30秒窗） · Se@Sp90: exp1=0.871429 vs domains/ci=0.871429 (|Δ|=0.00e+00)
- ✅ CI表 外部2：CPSC2021（中国，30秒窗） · Brier: exp1=0.128084 vs domains/ci=0.128084 (|Δ|=0.00e+00)
- ✅ 重校准表未校准行 源域 PTB-XL · auroc: exp1=0.974400 vs domains/ci=0.974400 (|Δ|=0.00e+00)
- ✅ 重校准表未校准行 源域 PTB-XL · brier: exp1=0.069266 vs domains/ci=0.069266 (|Δ|=0.00e+00)
- ✅ 重校准表未校准行 源域 PTB-XL · ece: exp1=0.064924 vs domains/ci=0.064924 (|Δ|=0.00e+00)
- ✅ 重校准表未校准行 源域 PTB-XL · se_at_sp90: exp1=0.945205 vs domains/ci=0.945205 (|Δ|=0.00e+00)
- ✅ 重校准表未校准行 CinC2017（消费级可穿戴单导联） · auroc: exp1=0.885496 vs domains/ci=0.885496 (|Δ|=0.00e+00)
- ✅ 重校准表未校准行 CinC2017（消费级可穿戴单导联） · brier: exp1=0.220735 vs domains/ci=0.220735 (|Δ|=0.00e+00)
- ✅ 重校准表未校准行 CinC2017（消费级可穿戴单导联） · ece: exp1=0.225398 vs domains/ci=0.225398 (|Δ|=0.00e+00)
- ✅ 重校准表未校准行 CinC2017（消费级可穿戴单导联） · se_at_sp90: exp1=0.585752 vs domains/ci=0.585752 (|Δ|=0.00e+00)
- ✅ 重校准表未校准行 CPSC2021（中国动态 ECG 30 秒窗） · auroc: exp1=0.946146 vs domains/ci=0.946146 (|Δ|=0.00e+00)
- ✅ 重校准表未校准行 CPSC2021（中国动态 ECG 30 秒窗） · brier: exp1=0.128084 vs domains/ci=0.128084 (|Δ|=0.00e+00)
- ✅ 重校准表未校准行 CPSC2021（中国动态 ECG 30 秒窗） · ece: exp1=0.143260 vs domains/ci=0.143260 (|Δ|=0.00e+00)
- ✅ 重校准表未校准行 CPSC2021（中国动态 ECG 30 秒窗） · se_at_sp90: exp1=0.871429 vs domains/ci=0.871429 (|Δ|=0.00e+00)

**一致性结论：PASS**

## 05_P2论文骨架.md（抽取到 110 个小数）
- ✅ 全部命中权威值池（numbersheet.json）

## 06_P2_Methods与Results初稿.md（抽取到 84 个小数）
- ✅ 全部命中权威值池（numbersheet.json）

## 08_投稿格式与投稿信.md（抽取到 18 个小数）
- ✅ 全部命中权威值池（numbersheet.json）

## 10_一页中文研究简介.md（抽取到 25 个小数）
- ✅ 全部命中权威值池（numbersheet.json）

## README_正式结果.md（抽取到 133 个小数）
- ✅ 全部命中权威值池（numbersheet.json）

---
总体：✅ PASS
