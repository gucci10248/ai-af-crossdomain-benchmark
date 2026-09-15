#!/bin/bash
# 并行抓取 PhysioNet 数据（本机国际出口约 40-100 KB/s，故用 12 路并发 + 断点续传 + 重试）
# 用法: bash fetch.sh <url_list.tsv> [并发数]
set -u
LIST="$1"
JOBS="${2:-12}"
BASE="/Users/mac/Desktop/库/公共数据AF/data"
cd "$BASE" || exit 1

dl() {
  local line="$1"
  local local_path="${line%%$'\t'*}"
  local url="${line##*$'\t'}"
  mkdir -p "$(dirname "$local_path")"
  if [ -s "$local_path" ]; then
    return 0
  fi
  curl -sS --retry 6 --retry-delay 2 --retry-all-errors \
       --connect-timeout 25 --max-time 600 \
       -C - -o "$local_path" "$url" >/dev/null 2>&1
}
export -f dl

cat "$LIST" | xargs -P "$JOBS" -I LINE bash -c 'dl "$@"' _ LINE
echo "download pass done: $(find cinc2017 records100 -type f 2>/dev/null | wc -l) files present"
du -sh "$BASE" 2>/dev/null
