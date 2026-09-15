# 权威数字表（写作时只从此处取数）

生成时间：见文件 mtime ｜ 共 123 条 ｜ 来源：out/*.csv|json（均为脚本真实运行输出）

## 数据

| 项目 | 数值 | 来源文件 | 复现脚本 |
|---|---|---|---|
| PTB-XL 纳入记录数 | 2399 | data/ptbxl_subset_ids.txt（2400 抽样，1 条读取失败） | make_ptbxl_subset.py |
| PTB-XL 训练/内部测试（患者级 7:3） | 1685 / 714 | out/exp_final.log | run_experiment.py |
| CinC2017 纳入记录数 | 2537 | out/table_domains.csv | make_cinc2017_subset.py |
| CinC2017 类别分布 | A758/N1000/O500/~279 | data/cinc2017_subset.txt + REFERENCE-v3.csv | make_cinc2017_subset.py |
| CPSC2021 记录数（Set I，已解析诊断） | 719 | out/cpsc2021_records_dx.csv | scan_cpsc2021_dx.py |
| CPSC2021 诊断=nonAF | 470 | out/cpsc2021_records_dx.csv | scan_cpsc2021_dx.py |
| CPSC2021 诊断=persistentAF | 153 | out/cpsc2021_records_dx.csv | scan_cpsc2021_dx.py |
| CPSC2021 诊断=paroxysmalAF | 96 | out/cpsc2021_records_dx.csv | scan_cpsc2021_dx.py |
| CPSC2021 窗级数据集 | 583 窗 / 25 患者（AF 280 / 非AF 303；剔除跨节律窗 130） | out/cpsc2021_window_summary.json | cpsc2021_windows.py |

## 主结果

| 项目 | 数值 | 来源文件 | 复现脚本 |
|---|---|---|---|
| 内部：PTB-XL（德国 12 导联） · n | 714 | out/table_domains.csv | make_figures_multidomain.py |
| 内部：PTB-XL（德国 12 导联） · auroc | 0.9744 | out/table_domains.csv | make_figures_multidomain.py |
| 内部：PTB-XL（德国 12 导联） · auprc | 0.972 | out/table_domains.csv | make_figures_multidomain.py |
| 内部：PTB-XL（德国 12 导联） · brier | 0.0693 | out/table_domains.csv | make_figures_multidomain.py |
| 内部：PTB-XL（德国 12 导联） · ece | 0.0649 | out/table_domains.csv | make_figures_multidomain.py |
| 内部：PTB-XL（德国 12 导联） · se_at_sp90 | 0.9452 | out/table_domains.csv | make_figures_multidomain.py |
| 内部：PTB-XL（德国 12 导联） · mean_pred | 0.5491 | out/table_domains.csv | make_figures_multidomain.py |
| 内部：PTB-XL（德国 12 导联） · observed | 0.5112 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 1：CinC2017（消费级单导联） · n | 2537 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 1：CinC2017（消费级单导联） · auroc | 0.8855 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 1：CinC2017（消费级单导联） · auprc | 0.7015 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 1：CinC2017（消费级单导联） · brier | 0.2207 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 1：CinC2017（消费级单导联） · ece | 0.2254 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 1：CinC2017（消费级单导联） · se_at_sp90 | 0.5858 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 1：CinC2017（消费级单导联） · mean_pred | 0.5145 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 1：CinC2017（消费级单导联） · observed | 0.2988 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 2：CPSC2021（中国动态 ECG） · n | 583 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 2：CPSC2021（中国动态 ECG） · auroc | 0.9461 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 2：CPSC2021（中国动态 ECG） · auprc | 0.8918 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 2：CPSC2021（中国动态 ECG） · brier | 0.1281 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 2：CPSC2021（中国动态 ECG） · ece | 0.1433 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 2：CPSC2021（中国动态 ECG） · se_at_sp90 | 0.8714 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 2：CPSC2021（中国动态 ECG） · mean_pred | 0.6235 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 2：CPSC2021（中国动态 ECG） · observed | 0.4803 | out/table_domains.csv | make_figures_multidomain.py |

## CI

| 项目 | 数值 | 来源文件 | 复现脚本 |
|---|---|---|---|
| 内部：PTB-XL（德国12导） · AUROC | 0.974 [0.964, 0.983] | out/table_ci.csv | subgroups_ci.py |
| 内部：PTB-XL（德国12导） · Brier | 0.069 [0.054, 0.087] | out/table_ci.csv | subgroups_ci.py |
| 内部：PTB-XL（德国12导） · Se@Sp90 | 0.945 [0.899, 0.974] | out/table_ci.csv | subgroups_ci.py |
| 内部：PTB-XL（德国12导） · Sp@0.5 | 0.880 [0.845, 0.910] | out/table_ci.csv | subgroups_ci.py |
| 外部1：CinC2017 全部（A vs 非A） · AUROC | 0.885 [0.872, 0.897] | out/table_ci.csv | subgroups_ci.py |
| 外部1：CinC2017 全部（A vs 非A） · Brier | 0.221 [0.205, 0.237] | out/table_ci.csv | subgroups_ci.py |
| 外部1：CinC2017 全部（A vs 非A） · Se@Sp90 | 0.586 [0.522, 0.643] | out/table_ci.csv | subgroups_ci.py |
| 外部1：CinC2017 全部（A vs 非A） · Sp@0.5 | 0.672 [0.649, 0.694] | out/table_ci.csv | subgroups_ci.py |
| 外部2：CPSC2021（中国，30秒窗） · AUROC | 0.946 [0.886, 0.991] | out/table_ci.csv | subgroups_ci.py |
| 外部2：CPSC2021（中国，30秒窗） · Brier | 0.128 [0.037, 0.247] | out/table_ci.csv | subgroups_ci.py |
| 外部2：CPSC2021（中国，30秒窗） · Se@Sp90 | 0.871 [0.551, 1.000] | out/table_ci.csv | subgroups_ci.py |
| 外部2：CPSC2021（中国，30秒窗） · Sp@0.5 | 0.729 [0.518, 0.908] | out/table_ci.csv | subgroups_ci.py |
| 外部1a：仅 A vs N · AUROC | 0.948 [0.937, 0.958] | out/table_ci.csv | subgroups_ci.py |
| 外部1a：仅 A vs N · Brier | 0.104 [0.091, 0.117] | out/table_ci.csv | subgroups_ci.py |
| 外部1a：仅 A vs N · Se@Sp90 | 0.891 [0.845, 0.920] | out/table_ci.csv | subgroups_ci.py |
| 外部1a：仅 A vs N · Sp@0.5 | 0.833 [0.809, 0.855] | out/table_ci.csv | subgroups_ci.py |
| 外部1b：A vs O（其他节律） · AUROC | 0.904 [0.885, 0.922] | out/table_ci.csv | subgroups_ci.py |
| 外部1b：A vs O（其他节律） · Brier | 0.153 [0.135, 0.171] | out/table_ci.csv | subgroups_ci.py |
| 外部1b：A vs O（其他节律） · Se@Sp90 | 0.735 [0.652, 0.808] | out/table_ci.csv | subgroups_ci.py |
| 外部1b：A vs O（其他节律） · Sp@0.5 | 0.638 [0.596, 0.680] | out/table_ci.csv | subgroups_ci.py |
| 外部1c：A vs 噪声(~) · AUROC | 0.630 [0.594, 0.673] | out/table_ci.csv | subgroups_ci.py |
| 外部1c：A vs 噪声(~) · Brier | 0.249 [0.223, 0.275] | out/table_ci.csv | subgroups_ci.py |
| 外部1c：A vs 噪声(~) · Se@Sp90 | 0.166 [0.121, 0.242] | out/table_ci.csv | subgroups_ci.py |
| 外部1c：A vs 噪声(~) · Sp@0.5 | 0.154 [0.113, 0.199] | out/table_ci.csv | subgroups_ci.py |

## 亚组

| 项目 | 数值 | 来源文件 | 复现脚本 |
|---|---|---|---|
| PTB-XL 内部 · 性别=0 · AUROC | 0.978 [0.965, 0.989] | out/table_subgroups.csv | subgroups_ci.py |
| PTB-XL 内部 · 性别=0 · Se@Sp90 | 0.949 [0.874, 0.989] | out/table_subgroups.csv | subgroups_ci.py |
| PTB-XL 内部 · 性别=1 · AUROC | 0.971 [0.951, 0.986] | out/table_subgroups.csv | subgroups_ci.py |
| PTB-XL 内部 · 性别=1 · Se@Sp90 | 0.935 [0.874, 0.984] | out/table_subgroups.csv | subgroups_ci.py |
| PTB-XL 内部 · 年龄段=50-64 · AUROC | 0.994 [0.984, 1.000] | out/table_subgroups.csv | subgroups_ci.py |
| PTB-XL 内部 · 年龄段=50-64 · Se@Sp90 | 1.000 [0.951, 1.000] | out/table_subgroups.csv | subgroups_ci.py |
| PTB-XL 内部 · 年龄段=65-74 · AUROC | 0.976 [0.958, 0.990] | out/table_subgroups.csv | subgroups_ci.py |
| PTB-XL 内部 · 年龄段=65-74 · Se@Sp90 | 0.927 [0.841, 0.981] | out/table_subgroups.csv | subgroups_ci.py |
| PTB-XL 内部 · 年龄段=75+ · AUROC | 0.962 [0.938, 0.982] | out/table_subgroups.csv | subgroups_ci.py |
| PTB-XL 内部 · 年龄段=75+ · Se@Sp90 | 0.928 [0.781, 0.993] | out/table_subgroups.csv | subgroups_ci.py |
| 中国域 · paroxysmalAF · AUROC | 0.995 [0.988, 1.000] | out/table_subgroups.csv | subgroups_ci.py |
| 中国域 · paroxysmalAF · Se@Sp90 | 1.000 [0.974, 1.000] | out/table_subgroups.csv | subgroups_ci.py |

## 重校准

| 项目 | 数值 | 来源文件 | 复现脚本 |
|---|---|---|---|
| 源域 PTB-XL · 未校准 | AUROC 0.974 / Brier 0.069 / ECE 0.065 / Se@Sp90 0.945 | out/table_recal_multidomain.csv | recalibrate_multi.py |
| CinC2017（消费级可穿戴单导联） · 未校准 | AUROC 0.885 / Brier 0.221 / ECE 0.225 / Se@Sp90 0.586 | out/table_recal_multidomain.csv | recalibrate_multi.py |
| CinC2017（消费级可穿戴单导联） · 温度缩放(源域拟合) | AUROC 0.885 / Brier 0.187 / ECE 0.226 / Se@Sp90 0.586 | out/table_recal_multidomain.csv | recalibrate_multi.py |
| CinC2017（消费级可穿戴单导联） · 温度缩放(目标域拟合) | AUROC 0.885 / Brier 0.180 / ECE 0.225 / Se@Sp90 0.586 | out/table_recal_multidomain.csv | recalibrate_multi.py |
| CinC2017（消费级可穿戴单导联） · 等渗回归(源域拟合) | AUROC 0.883 / Brier 0.192 / ECE 0.227 / Se@Sp90 0.722 | out/table_recal_multidomain.csv | recalibrate_multi.py |
| CinC2017（消费级可穿戴单导联） · 等渗回归(目标域拟合) | AUROC 0.888 / Brier 0.121 / ECE 0.000 / Se@Sp90 0.623 | out/table_recal_multidomain.csv | recalibrate_multi.py |
| CPSC2021（中国动态 ECG 30 秒窗） · 未校准 | AUROC 0.946 / Brier 0.128 / ECE 0.143 / Se@Sp90 0.871 | out/table_recal_multidomain.csv | recalibrate_multi.py |
| CPSC2021（中国动态 ECG 30 秒窗） · 温度缩放(源域拟合) | AUROC 0.946 / Brier 0.109 / ECE 0.135 / Se@Sp90 0.871 | out/table_recal_multidomain.csv | recalibrate_multi.py |
| CPSC2021（中国动态 ECG 30 秒窗） · 温度缩放(目标域拟合) | AUROC 0.946 / Brier 0.109 / ECE 0.130 / Se@Sp90 0.871 | out/table_recal_multidomain.csv | recalibrate_multi.py |
| CPSC2021（中国动态 ECG 30 秒窗） · 等渗回归(源域拟合) | AUROC 0.944 / Brier 0.113 / ECE 0.132 / Se@Sp90 0.889 | out/table_recal_multidomain.csv | recalibrate_multi.py |
| CPSC2021（中国动态 ECG 30 秒窗） · 等渗回归(目标域拟合) | AUROC 0.952 / Brier 0.070 / ECE 0.000 / Se@Sp90 0.918 | out/table_recal_multidomain.csv | recalibrate_multi.py |
| 源域温度 T_source（in-sample 拟合） | 3.2455 | out/recalibration_results.json | recalibrate_multi.py |
| CinC2017（消费级可穿戴单导联） · 目标域温度 T_target（oracle） | 5.8858 | out/recalibration_results.json | recalibrate_multi.py |
| CPSC2021（中国动态 ECG 30 秒窗） · 目标域温度 T_target（oracle） | 3.8158 | out/recalibration_results.json | recalibrate_multi.py |

## 域内参照/其他

| 项目 | 数值 | 来源文件 | 复现脚本 |
|---|---|---|---|
| PTB-XL internal (logreg) | n=714 AUROC 0.950 Brier 0.075 ECE 0.037 Se@Sp90 0.847 | out/results_exp1.json | run_experiment.py |
| CinC2017 external (trained on PTB-XL/logreg) | n=2537 AUROC 0.789 Brier 0.588 ECE 0.613 Se@Sp90 0.398 | out/results_exp1.json | run_experiment.py |
| CinC2017 external AF-vs-N only (trained on PTB-XL/logreg) | n=1758 AUROC 0.839 Brier 0.471 ECE 0.491 Se@Sp90 0.577 | out/results_exp1.json | run_experiment.py |
| CinC2017 internal 5-fold (in-domain reference) | n=2537 AUROC 0.952 Brier 0.086 ECE 0.072 Se@Sp90 0.865 | out/results_exp1.json | run_experiment.py |
| PTB-XL internal (hgb) | n=714 AUROC 0.974 Brier 0.069 ECE 0.065 Se@Sp90 0.945 | out/results_exp1.json | run_experiment.py |
| CinC2017 external (trained on PTB-XL/hgb) | n=2537 AUROC 0.885 Brier 0.221 ECE 0.225 Se@Sp90 0.586 | out/results_exp1.json | run_experiment.py |
| CinC2017 external AF-vs-N only (trained on PTB-XL/hgb) | n=1758 AUROC 0.948 Brier 0.104 ECE 0.098 Se@Sp90 0.891 | out/results_exp1.json | run_experiment.py |
| CPSC2021 external (China, trained on PTB-XL/logreg) | n=583 AUROC 0.904 Brier 0.449 ECE 0.476 Se@Sp90 0.607 | out/results_exp1.json | run_experiment.py |
| CPSC2021 external (China, trained on PTB-XL/hgb) | n=583 AUROC 0.946 Brier 0.128 ECE 0.143 Se@Sp90 0.871 | out/results_exp1.json | run_experiment.py |
| CPSC2021 in-domain 5-fold (grouped by patient) | n=583 AUROC 0.923 Brier 0.136 ECE 0.126 Se@Sp90 0.786 | out/results_exp1.json | run_experiment.py |

## PPV/NPV

| 项目 | 数值 | 来源文件 | 复现脚本 |
|---|---|---|---|
| 本研究 · 内部验证（PTB-XL，Se@Sp90） · 患病率1% | PPV 8.7% / NPV 99.94% / 每检出1例需复核 11.5 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 内部验证（PTB-XL，Se@Sp90） · 患病率5% | PPV 33.2% / NPV 99.68% / 每检出1例需复核 3.0 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 内部验证（PTB-XL，Se@Sp90） · 患病率20% | PPV 70.3% / NPV 98.50% / 每检出1例需复核 1.4 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 外部1 可穿戴（0.5 阈值） · 患病率1% | PPV 2.8% / NPV 99.91% / 每检出1例需复核 35.6 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 外部1 可穿戴（0.5 阈值） · 患病率5% | PPV 13.1% / NPV 99.54% / 每检出1例需复核 7.6 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 外部1 可穿戴（0.5 阈值） · 患病率20% | PPV 41.7% / NPV 97.84% / 每检出1例需复核 2.4 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 外部1 可穿戴（Se@Sp90） · 患病率1% | PPV 5.6% / NPV 99.54% / 每检出1例需复核 17.9 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 外部1 可穿戴（Se@Sp90） · 患病率5% | PPV 23.6% / NPV 97.63% / 每检出1例需复核 4.2 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 外部1 可穿戴（Se@Sp90） · 患病率20% | PPV 59.4% / NPV 89.68% / 每检出1例需复核 1.7 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 外部1 严格 A vs N（Se@Sp90） · 患病率1% | PPV 8.2% / NPV 99.88% / 每检出1例需复核 12.1 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 外部1 严格 A vs N（Se@Sp90） · 患病率5% | PPV 31.9% / NPV 99.36% / 每检出1例需复核 3.1 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 外部1 严格 A vs N（Se@Sp90） · 患病率20% | PPV 69.0% / NPV 97.05% / 每检出1例需复核 1.4 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 外部1 A vs 噪声（Se@Sp90） · 患病率1% | PPV 1.7% / NPV 99.07% / 每检出1例需复核 60.6 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 外部1 A vs 噪声（Se@Sp90） · 患病率5% | PPV 8.0% / NPV 95.35% / 每检出1例需复核 12.4 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 外部1 A vs 噪声（Se@Sp90） · 患病率20% | PPV 29.4% / NPV 81.19% / 每检出1例需复核 3.4 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 中国域 CPSC2021（Se@Sp90） · 患病率1% | PPV 8.1% / NPV 99.86% / 每检出1例需复核 12.4 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 中国域 CPSC2021（Se@Sp90） · 患病率5% | PPV 31.4% / NPV 99.25% / 每检出1例需复核 3.2 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 中国域 CPSC2021（Se@Sp90） · 患病率20% | PPV 68.5% / NPV 96.55% / 每检出1例需复核 1.5 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 对照锚点 · 导师团队 PACE 2024（间期级，消融人群） · 患病率1% | PPV 66.0% / NPV 99.96% / 每检出1例需复核 1.5 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 对照锚点 · 导师团队 PACE 2024（间期级，消融人群） · 患病率5% | PPV 91.0% / NPV 99.80% / 每检出1例需复核 1.1 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 对照锚点 · 导师团队 PACE 2024（间期级，消融人群） · 患病率20% | PPV 98.0% / NPV 99.08% / 每检出1例需复核 1.0 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 对照锚点 · 导师团队 Adv Sci 2026（双模态校正后） · 患病率1% | PPV 57.7% / NPV 99.99% / 每检出1例需复核 1.7 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 对照锚点 · 导师团队 Adv Sci 2026（双模态校正后） · 患病率5% | PPV 87.7% / NPV 99.93% / 每检出1例需复核 1.1 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 对照锚点 · 导师团队 Adv Sci 2026（双模态校正后） · 患病率20% | PPV 97.1% / NPV 99.65% / 每检出1例需复核 1.0 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 对照锚点 · 导师团队 JACC Clin EP 2026（间期级，728 例前瞻） · 患病率1% | PPV 69.4% / NPV 99.99% / 每检出1例需复核 1.4 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 对照锚点 · 导师团队 JACC Clin EP 2026（间期级，728 例前瞻） · 患病率5% | PPV 92.2% / NPV 99.93% / 每检出1例需复核 1.1 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 对照锚点 · 导师团队 JACC Clin EP 2026（间期级，728 例前瞻） · 患病率20% | PPV 98.2% / NPV 99.67% / 每检出1例需复核 1.0 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 对照锚点 · 导师团队 Heart Rhythm O2 2025（眼底 DL 外验 AUROC 0.773） · 患病率1% | PPV 7.2% / NPV 99.75% / 每检出1例需复核 13.8 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 对照锚点 · 导师团队 Heart Rhythm O2 2025（眼底 DL 外验 AUROC 0.773） · 患病率5% | PPV 28.9% / NPV 98.69% / 每检出1例需复核 3.5 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 对照锚点 · 导师团队 Heart Rhythm O2 2025（眼底 DL 外验 AUROC 0.773） · 患病率20% | PPV 65.9% / NPV 94.07% / 每检出1例需复核 1.5 例 | out/table_ppv_npv.csv | ppv_npv.py |

