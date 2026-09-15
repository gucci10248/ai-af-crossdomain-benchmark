# 权威数字表（写作时只从此处取数）

生成时间：见文件 mtime ｜ 共 120 条 ｜ 来源：out/*.csv|json（均为脚本真实运行输出）

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
| 内部：PTB-XL（德国 12 导联） · auroc | 0.9745 | out/table_domains.csv | make_figures_multidomain.py |
| 内部：PTB-XL（德国 12 导联） · auprc | 0.9714 | out/table_domains.csv | make_figures_multidomain.py |
| 内部：PTB-XL（德国 12 导联） · brier | 0.0688 | out/table_domains.csv | make_figures_multidomain.py |
| 内部：PTB-XL（德国 12 导联） · ece | 0.0632 | out/table_domains.csv | make_figures_multidomain.py |
| 内部：PTB-XL（德国 12 导联） · se_at_sp90 | 0.9397 | out/table_domains.csv | make_figures_multidomain.py |
| 内部：PTB-XL（德国 12 导联） · mean_pred | 0.5512 | out/table_domains.csv | make_figures_multidomain.py |
| 内部：PTB-XL（德国 12 导联） · observed | 0.5112 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 1：CinC2017（消费级单导联） · n | 2537 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 1：CinC2017（消费级单导联） · auroc | 0.888 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 1：CinC2017（消费级单导联） · auprc | 0.7153 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 1：CinC2017（消费级单导联） · brier | 0.2241 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 1：CinC2017（消费级单导联） · ece | 0.2288 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 1：CinC2017（消费级单导联） · se_at_sp90 | 0.5963 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 1：CinC2017（消费级单导联） · mean_pred | 0.5181 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 1：CinC2017（消费级单导联） · observed | 0.2988 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 2：CPSC2021（中国动态 ECG） · n | 583 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 2：CPSC2021（中国动态 ECG） · auroc | 0.9465 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 2：CPSC2021（中国动态 ECG） · auprc | 0.8922 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 2：CPSC2021（中国动态 ECG） · brier | 0.1321 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 2：CPSC2021（中国动态 ECG） · ece | 0.1501 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 2：CPSC2021（中国动态 ECG） · se_at_sp90 | 0.8607 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 2：CPSC2021（中国动态 ECG） · mean_pred | 0.6304 | out/table_domains.csv | make_figures_multidomain.py |
| 外部 2：CPSC2021（中国动态 ECG） · observed | 0.4803 | out/table_domains.csv | make_figures_multidomain.py |

## CI

| 项目 | 数值 | 来源文件 | 复现脚本 |
|---|---|---|---|
| 内部：PTB-XL（德国12导） · AUROC | 0.975 [0.964, 0.984] | out/table_ci.csv | subgroups_ci.py |
| 内部：PTB-XL（德国12导） · Brier | 0.069 [0.053, 0.086] | out/table_ci.csv | subgroups_ci.py |
| 内部：PTB-XL（德国12导） · Se@Sp90 | 0.940 [0.889, 0.975] | out/table_ci.csv | subgroups_ci.py |
| 内部：PTB-XL（德国12导） · Sp@0.5 | 0.877 [0.841, 0.907] | out/table_ci.csv | subgroups_ci.py |
| 外部1：CinC2017 全部（A vs 非A） · AUROC | 0.888 [0.875, 0.900] | out/table_ci.csv | subgroups_ci.py |
| 外部1：CinC2017 全部（A vs 非A） · Brier | 0.224 [0.209, 0.240] | out/table_ci.csv | subgroups_ci.py |
| 外部1：CinC2017 全部（A vs 非A） · Se@Sp90 | 0.596 [0.530, 0.655] | out/table_ci.csv | subgroups_ci.py |
| 外部1：CinC2017 全部（A vs 非A） · Sp@0.5 | 0.663 [0.641, 0.686] | out/table_ci.csv | subgroups_ci.py |
| 外部2：CPSC2021（中国，30秒窗） · AUROC | 0.947 [0.887, 0.992] | out/table_ci.csv | subgroups_ci.py |
| 外部2：CPSC2021（中国，30秒窗） · Brier | 0.132 [0.040, 0.248] | out/table_ci.csv | subgroups_ci.py |
| 外部2：CPSC2021（中国，30秒窗） · Se@Sp90 | 0.861 [0.573, 1.000] | out/table_ci.csv | subgroups_ci.py |
| 外部2：CPSC2021（中国，30秒窗） · Sp@0.5 | 0.719 [0.514, 0.890] | out/table_ci.csv | subgroups_ci.py |
| 外部1a：仅 A vs N · AUROC | 0.948 [0.937, 0.957] | out/table_ci.csv | subgroups_ci.py |
| 外部1a：仅 A vs N · Brier | 0.109 [0.096, 0.124] | out/table_ci.csv | subgroups_ci.py |
| 外部1a：仅 A vs N · Se@Sp90 | 0.877 [0.832, 0.912] | out/table_ci.csv | subgroups_ci.py |
| 外部1a：仅 A vs N · Sp@0.5 | 0.817 [0.793, 0.840] | out/table_ci.csv | subgroups_ci.py |
| 外部1b：A vs O（其他节律） · AUROC | 0.904 [0.885, 0.921] | out/table_ci.csv | subgroups_ci.py |
| 外部1b：A vs O（其他节律） · Brier | 0.152 [0.135, 0.170] | out/table_ci.csv | subgroups_ci.py |
| 外部1b：A vs O（其他节律） · Se@Sp90 | 0.731 [0.651, 0.796] | out/table_ci.csv | subgroups_ci.py |
| 外部1b：A vs O（其他节律） · Sp@0.5 | 0.640 [0.598, 0.683] | out/table_ci.csv | subgroups_ci.py |
| 外部1c：A vs 噪声(~) · AUROC | 0.646 [0.610, 0.686] | out/table_ci.csv | subgroups_ci.py |
| 外部1c：A vs 噪声(~) · Brier | 0.248 [0.221, 0.274] | out/table_ci.csv | subgroups_ci.py |
| 外部1c：A vs 噪声(~) · Se@Sp90 | 0.199 [0.149, 0.294] | out/table_ci.csv | subgroups_ci.py |
| 外部1c：A vs 噪声(~) · Sp@0.5 | 0.154 [0.112, 0.201] | out/table_ci.csv | subgroups_ci.py |

## 亚组

| 项目 | 数值 | 来源文件 | 复现脚本 |
|---|---|---|---|
| PTB-XL 内部 · 性别=0 · AUROC | 0.979 [0.967, 0.990] | out/table_subgroups.csv | subgroups_ci.py |
| PTB-XL 内部 · 性别=0 · Se@Sp90 | 0.944 [0.869, 0.991] | out/table_subgroups.csv | subgroups_ci.py |
| PTB-XL 内部 · 性别=1 · AUROC | 0.969 [0.949, 0.985] | out/table_subgroups.csv | subgroups_ci.py |
| PTB-XL 内部 · 性别=1 · Se@Sp90 | 0.935 [0.859, 0.987] | out/table_subgroups.csv | subgroups_ci.py |
| PTB-XL 内部 · 年龄段=50-64 · AUROC | 0.995 [0.986, 1.000] | out/table_subgroups.csv | subgroups_ci.py |
| PTB-XL 内部 · 年龄段=50-64 · Se@Sp90 | 1.000 [0.958, 1.000] | out/table_subgroups.csv | subgroups_ci.py |
| PTB-XL 内部 · 年龄段=65-74 · AUROC | 0.976 [0.958, 0.990] | out/table_subgroups.csv | subgroups_ci.py |
| PTB-XL 内部 · 年龄段=65-74 · Se@Sp90 | 0.927 [0.830, 0.983] | out/table_subgroups.csv | subgroups_ci.py |
| PTB-XL 内部 · 年龄段=75+ · AUROC | 0.963 [0.938, 0.983] | out/table_subgroups.csv | subgroups_ci.py |
| PTB-XL 内部 · 年龄段=75+ · Se@Sp90 | 0.928 [0.815, 0.992] | out/table_subgroups.csv | subgroups_ci.py |
| 中国域 · paroxysmalAF · AUROC | 0.995 [0.988, 1.000] | out/table_subgroups.csv | subgroups_ci.py |
| 中国域 · paroxysmalAF · Se@Sp90 | 1.000 [0.974, 1.000] | out/table_subgroups.csv | subgroups_ci.py |

## 重校准

| 项目 | 数值 | 来源文件 | 复现脚本 |
|---|---|---|---|
| 源域 PTB-XL · 未校准 | AUROC 0.966 / Brier 0.075 / ECE 0.071 / Se@Sp90 0.921 | out/table_recal_multidomain.csv | recalibrate_multi.py |
| CinC2017（消费级可穿戴单导联） · 未校准 | AUROC 0.859 / Brier 0.256 / ECE 0.263 / Se@Sp90 0.429 | out/table_recal_multidomain.csv | recalibrate_multi.py |
| CinC2017（消费级可穿戴单导联） · 温度缩放(源域拟合) | AUROC 0.859 / Brier 0.223 / ECE 0.263 / Se@Sp90 0.429 | out/table_recal_multidomain.csv | recalibrate_multi.py |
| CinC2017（消费级可穿戴单导联） · 温度缩放(目标域拟合) | AUROC 0.859 / Brier 0.201 / ECE 0.242 / Se@Sp90 0.429 | out/table_recal_multidomain.csv | recalibrate_multi.py |
| CinC2017（消费级可穿戴单导联） · 等渗回归(源域拟合) | AUROC 0.855 / Brier 0.271 / ECE 0.325 / Se@Sp90 0.665 | out/table_recal_multidomain.csv | recalibrate_multi.py |
| CinC2017（消费级可穿戴单导联） · 等渗回归(目标域拟合) | AUROC 0.863 / Brier 0.133 / ECE 0.000 / Se@Sp90 0.611 | out/table_recal_multidomain.csv | recalibrate_multi.py |
| CPSC2021（中国动态 ECG 30 秒窗） · 未校准 | AUROC 0.921 / Brier 0.148 / ECE 0.159 / Se@Sp90 0.754 | out/table_recal_multidomain.csv | recalibrate_multi.py |
| CPSC2021（中国动态 ECG 30 秒窗） · 温度缩放(源域拟合) | AUROC 0.921 / Brier 0.128 / ECE 0.143 / Se@Sp90 0.754 | out/table_recal_multidomain.csv | recalibrate_multi.py |
| CPSC2021（中国动态 ECG 30 秒窗） · 温度缩放(目标域拟合) | AUROC 0.921 / Brier 0.125 / ECE 0.127 / Se@Sp90 0.754 | out/table_recal_multidomain.csv | recalibrate_multi.py |
| CPSC2021（中国动态 ECG 30 秒窗） · 等渗回归(源域拟合) | AUROC 0.917 / Brier 0.156 / ECE 0.180 / Se@Sp90 0.761 | out/table_recal_multidomain.csv | recalibrate_multi.py |
| CPSC2021（中国动态 ECG 30 秒窗） · 等渗回归(目标域拟合) | AUROC 0.927 / Brier 0.093 / ECE 0.000 / Se@Sp90 0.868 | out/table_recal_multidomain.csv | recalibrate_multi.py |

## 域内参照/其他

| 项目 | 数值 | 来源文件 | 复现脚本 |
|---|---|---|---|
| PTB-XL internal (logreg) | n=714 AUROC 0.950 Brier 0.075 ECE 0.037 Se@Sp90 0.844 | out/results_exp1.json | run_experiment.py |
| CinC2017 external (trained on PTB-XL/logreg) | n=2537 AUROC 0.789 Brier 0.588 ECE 0.613 Se@Sp90 0.398 | out/results_exp1.json | run_experiment.py |
| CinC2017 external AF-vs-N only (trained on PTB-XL/logreg) | n=1758 AUROC 0.839 Brier 0.471 ECE 0.491 Se@Sp90 0.574 | out/results_exp1.json | run_experiment.py |
| CinC2017 internal 5-fold (in-domain reference) | n=2537 AUROC 0.952 Brier 0.085 ECE 0.069 Se@Sp90 0.852 | out/results_exp1.json | run_experiment.py |
| PTB-XL internal (hgb) | n=714 AUROC 0.974 Brier 0.069 ECE 0.065 Se@Sp90 0.945 | out/results_exp1.json | run_experiment.py |
| CinC2017 external (trained on PTB-XL/hgb) | n=2537 AUROC 0.886 Brier 0.221 ECE 0.226 Se@Sp90 0.586 | out/results_exp1.json | run_experiment.py |
| CinC2017 external AF-vs-N only (trained on PTB-XL/hgb) | n=1758 AUROC 0.947 Brier 0.104 ECE 0.099 Se@Sp90 0.888 | out/results_exp1.json | run_experiment.py |
| CPSC2021 external (China, trained on PTB-XL/logreg) | n=583 AUROC 0.904 Brier 0.449 ECE 0.476 Se@Sp90 0.604 | out/results_exp1.json | run_experiment.py |
| CPSC2021 external (China, trained on PTB-XL/hgb) | n=583 AUROC 0.946 Brier 0.128 ECE 0.143 Se@Sp90 0.868 | out/results_exp1.json | run_experiment.py |
| CPSC2021 in-domain 5-fold (grouped by patient) | n=583 AUROC 0.923 Brier 0.136 ECE 0.126 Se@Sp90 0.786 | out/results_exp1.json | run_experiment.py |

## PPV/NPV

| 项目 | 数值 | 来源文件 | 复现脚本 |
|---|---|---|---|
| 本研究 · 内部验证（PTB-XL，Se@Sp90） · 患病率1% | PPV 8.7% / NPV 99.93% / 每检出1例需复核 11.5 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 内部验证（PTB-XL，Se@Sp90） · 患病率5% | PPV 33.1% / NPV 99.65% / 每检出1例需复核 3.0 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 内部验证（PTB-XL，Se@Sp90） · 患病率20% | PPV 70.2% / NPV 98.36% / 每检出1例需复核 1.4 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 外部1 可穿戴（0.5 阈值） · 患病率1% | PPV 2.7% / NPV 99.91% / 每检出1例需复核 36.5 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 外部1 可穿戴（0.5 阈值） · 患病率5% | PPV 12.8% / NPV 99.53% / 每检出1例需复核 7.8 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 外部1 可穿戴（0.5 阈值） · 患病率20% | PPV 41.1% / NPV 97.82% / 每检出1例需复核 2.4 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 外部1 可穿戴（Se@Sp90） · 患病率1% | PPV 5.7% / NPV 99.55% / 每检出1例需复核 17.6 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 外部1 可穿戴（Se@Sp90） · 患病率5% | PPV 23.9% / NPV 97.69% / 每检出1例需复核 4.2 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 外部1 可穿戴（Se@Sp90） · 患病率20% | PPV 59.8% / NPV 89.91% / 每检出1例需复核 1.7 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 外部1 严格 A vs N（Se@Sp90） · 患病率1% | PPV 8.1% / NPV 99.86% / 每检出1例需复核 12.3 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 外部1 严格 A vs N（Se@Sp90） · 患病率5% | PPV 31.6% / NPV 99.29% / 每检出1例需复核 3.2 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 外部1 严格 A vs N（Se@Sp90） · 患病率20% | PPV 68.7% / NPV 96.70% / 每检出1例需复核 1.5 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 外部1 A vs 噪声（Se@Sp90） · 患病率1% | PPV 2.0% / NPV 99.11% / 每检出1例需复核 50.7 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 外部1 A vs 噪声（Se@Sp90） · 患病率5% | PPV 9.5% / NPV 95.53% / 每检出1例需复核 10.5 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 外部1 A vs 噪声（Se@Sp90） · 患病率20% | PPV 33.2% / NPV 81.80% / 每检出1例需复核 3.0 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 中国域 CPSC2021（Se@Sp90） · 患病率1% | PPV 8.0% / NPV 99.84% / 每检出1例需复核 12.5 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 中国域 CPSC2021（Se@Sp90） · 患病率5% | PPV 31.2% / NPV 99.19% / 每检出1例需复核 3.2 例 | out/table_ppv_npv.csv | ppv_npv.py |
| 本研究 · 中国域 CPSC2021（Se@Sp90） · 患病率20% | PPV 68.3% / NPV 96.28% / 每检出1例需复核 1.5 例 | out/table_ppv_npv.csv | ppv_npv.py |
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

