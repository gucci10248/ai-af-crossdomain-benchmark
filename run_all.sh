#!/usr/bin/env zsh
# 一键重跑 P2 论文完整分析链（含图表、审计、投稿 docx 重生成）。
# 用法：cd /Users/mac/Desktop/库/公共数据AF && ./run_all.sh
# 默认复用特征缓存（REUSE_FEATURES=1）；如需强制重新提取特征，传 --rebuild-features。
set -euo pipefail

BASE="/Users/mac/Desktop/库/公共数据AF"
ART="/Users/mac/Desktop/文稿库/人工智能临床应用"
PY="/Users/mac/.venvs/afpub/bin/python"
cd "$BASE"

REUSE=1
if [[ "${1:-}" == "--rebuild-features" ]]; then
    REUSE=0
    rm -f out/feat_ptbxl.csv out/feat_cinc2017.csv out/feat_cpsc2021.csv
    echo "[run_all] 强制重新提取特征"
fi

export REUSE_FEATURES=$REUSE
export SEED=0
export SPLIT_SEED=20260915
export OUT_DIR="$BASE/out"

echo "============================================"
echo "P2 完整分析链重跑"
echo "REUSE_FEATURES=$REUSE | SEED=$SEED | OUT_DIR=$OUT_DIR"
echo "============================================"

# 1. 主实验（产生 results_exp1.json / table_exp1.csv / fig_reliability / feature_importance）
echo "[1/9] run_experiment.py"
$PY code/run_experiment.py

# 2. 多域图与 table_domains / table_ci
echo "[2/9] make_figures_multidomain.py"
$PY code/make_figures_multidomain.py

# 3. 旧版图 1 校准漂移（可选，保留兼容）
echo "[3/9] make_figures.py"
$PY code/make_figures.py || true

# 4. 亚组/森林图
echo "[4/9] subgroups_ci.py"
$PY code/subgroups_ci.py

# 5. 重校准多域
echo "[5/9] recalibrate_multi.py"
$PY code/recalibrate_multi.py

# 6. DCA 重校准
echo "[6/9] recalibrate_dca.py"
$PY code/recalibrate_dca.py

# 7. PPV/NPV
echo "[7/9] ppv_npv.py"
$PY code/ppv_npv.py

# 8. 汇总权威数字表
echo "[8/9] make_numbersheet.py"
$PY code/make_numbersheet.py

# 9. 数字审计
echo "[9/9] audit_numbers.py"
$PY code/audit_numbers.py

# 10. 重新生成投稿 docx
echo "[10/10] make_submission_docx.py"
$PY code/make_submission_docx.py

# 11. 重新生成 JACC 变体、补充材料、图形摘要
echo "[bonus] JACC variant / supplementary / graphical abstract"
$PY code/make_jacccp_variant.py || true
$PY code/make_supplementary_docx.py || true
$PY code/make_graphical_abstract.py || true

echo "============================================"
echo "全链完成。输出目录: $BASE/out"
echo "投稿主稿: $ART/P2_manuscript_v0.1.docx"
echo "============================================"
