# 代码与数据可复现包（P2：房颤检测的跨域外部验证基准）

公开数据二次分析，**不含任何院内或去标识患者数据**。全部输入来自 PhysioNet / CC-BY 公开库。

## 目录
```
code/                      全部分析脚本（按执行顺序）
  make_ptbxl_subset.py     PTB-XL 按标签平衡抽样 + 患者级划分清单
  make_cinc2017_subset.py  CinC2017 分层子集（含全部 AF）
  rebuild_urls.py          下载清单（修正 CinC2017 子目录路径）
  fetch.py                 并行下载器（断点续传、4xx 快速失败）
  scan_cpsc2021_dx.py      CPSC2021 记录级诊断解析（.hea 注释）
  select_cpsc2021_dat*.py  CPSC2021 .dat 按患者分层抽样（短记录优先）
  cpsc2021_windows.py      CPSC2021 → 30 秒窗 + 标签（.hea 诊断 + .atr 注释）
  features.py              31 维特征提取（HRV/频谱/波形）
  run_experiment.py        主实验：内部 + 两个外部 + 域内参照
  recalibrate_multi.py     温度缩放/等渗重校准 + 决策曲线（源域 vs oracle）
  subgroups_ci.py          聚类自助法 95% CI + 亚组/阴性类构成分析
  make_figures*.py         论文图（Fig 2 / Fig 3）
  make_numbersheet.py      汇总权威数字表（写作取数唯一来源）
out/                       结果：表（csv）、图（png）、数字表（numbersheet.md/json）、原始日志
submission/                TRIPOD+AI 自检清单、本文件
```

## 复现（约需 2–3 小时，主要耗时是下载；本机国际出口 20–50 KB/s）
```bash
PY=~/.venvs/afpub/bin/python          # wfdb 4.3.1 / scikit-learn 1.9.1 / pandas 3.0.5
python3 code/make_ptbxl_subset.py && python3 code/make_cinc2017_subset.py
python3 code/rebuild_urls.py
$PY code/fetch.py data/download_urls_priority.txt 24        # PTB-XL + CinC2017
$PY code/scan_cpsc2021_dx.py && $PY code/select_cpsc2021_dat2.py
$PY code/fetch.py data/cpsc2021_urls_dat2.txt 10            # CPSC2021 子集
$PY code/cpsc2021_windows.py --sets I --max-per-patient 24
REUSE_FEATURES=1 $PY code/run_experiment.py                 # 主结果（表 2）
$PY code/recalibrate_multi.py                               # 表 4 / Fig 3
$PY code/subgroups_ci.py                                    # 表 3/5 / Fig 4
$PY code/make_figures_multidomain.py                        # Fig 2
$PY code/make_numbersheet.py                                # out/numbersheet.md
```

## 数据来源与许可
| 库 | 来源 | 许可 |
|---|---|---|
| PTB-XL 1.0.3 | PhysioNet `ptb-xl/1.0.3` | Open (ODC-BY / CC-BY 视版本) |
| CinC Challenge 2017 | PhysioNet `challenge-2017/1.0.0` | Open |
| CPSC2021 | PhysioNet `cpsc2021/1.0.0` | CC-BY 4.0 |

## 引用要求
使用本文代码时请引用三个原始数据集文献（PTB-XL: Wagner et al. 2020；CinC2017: Clifford et al. 2017；CPSC2021: Wang et al. 2021）以及本文。

## 已知限制（与稿件一致）
1. 训练域仅 PTB-XL **I 导 / 100 Hz**，与目标域存在设备与时长双重差异（量化的是联合迁移代价）。
2. 三域均按近 1:1 平衡抽样，**患病率非真实**；未报 PPV/NPV。
3. CinC2017 无患者编号 → 该域自助法为记录级（患者级 CI 待原始数据支持）。
4. CPSC2021 的 persistent-AF 记录按整条判阳性（可能高估）；paroxysmal 记录剔除跨节律窗 130 个。
5. 特征为手工 HRV/频谱，非深度模型。
