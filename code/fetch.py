#!/usr/bin/env python3
"""稳健的并行下载器（替代 bash/xargs 版本：macOS 的 xargs -I 会按空白切分参数，导致建出
形如 "A00001.hea https:" 的目录）。用法：
    python3 fetch.py <url_list.tsv> [并发数]
TSV 每行: <本地相对路径>\t<URL>
特性：已存在且非空的文件跳过（可断点续跑）；失败重试 5 次；下载到 .part 再原子改名。
"""
import os, sys, time, pathlib, urllib.request, urllib.error, threading
from concurrent.futures import ThreadPoolExecutor

BASE = pathlib.Path("/Users/mac/Desktop/库/公共数据AF/data")
LIST = pathlib.Path(sys.argv[1])
JOBS = int(sys.argv[2]) if len(sys.argv) > 2 else 12

entries = []
for line in LIST.read_text().splitlines():
    line = line.strip()
    if not line:
        continue
    parts = line.split("\t")
    if len(parts) != 2:
        parts = line.split(None, 1)
    if len(parts) != 2 or not parts[1].startswith("http"):
        print("[warn] bad line skipped:", line[:80])
        continue
    entries.append((parts[0].strip(), parts[1].strip()))

lock = threading.Lock()
stat = {"done": 0, "skip": 0, "fail": 0}

def fetch(item):
    local, url = item
    target = BASE / local
    if target.is_file() and target.stat().st_size > 0:
        with lock:
            stat["skip"] += 1
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".part")
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "research-data-fetch/1.0"})
            with urllib.request.urlopen(req, timeout=90) as r, open(tmp, "wb") as f:
                while True:
                    chunk = r.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
            if tmp.stat().st_size == 0:
                raise IOError("empty file")
            os.replace(tmp, target)
            with lock:
                stat["done"] += 1
                n = stat["done"] + stat["skip"] + stat["fail"]
                if n % 50 == 0:
                    print(f"  progress: done={stat['done']} skip={stat['skip']} fail={stat['fail']} / {len(entries)}", flush=True)
            return
        except urllib.error.HTTPError as e:
            if 400 <= e.code < 500:      # 4xx 直接放弃，重试没意义
                with lock:
                    stat["fail"] += 1
                    print("  [fail-4xx]", e.code, local, flush=True)
                return
            time.sleep(2 * (attempt + 1))
        except Exception:
            time.sleep(2 * (attempt + 1))
    with lock:
        stat["fail"] += 1
        print("  [fail]", local, flush=True)

t0 = time.time()
with ThreadPoolExecutor(max_workers=JOBS) as ex:
    list(ex.map(fetch, entries))
dt = time.time() - t0
print(f"finished: done={stat['done']} skip={stat['skip']} fail={stat['fail']} "
      f"entries={len(entries)} elapsed={dt/60:.1f}min")
print("bytes on disk (data dir):", sum(f.stat().st_size for f in BASE.rglob("*") if f.is_file()))
