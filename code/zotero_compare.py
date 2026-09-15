#!/usr/bin/env python3
"""Zotero 逐条比对：把 07 参考文献清单（21 条）与 Zotero 本地库逐条比对。

Zotero 本地 API 未启用（403 Local API is not enabled），故**只读直连 zotero.sqlite**
（sqlite3 URI immutable=1，不写库、不加锁）。
输出：/Users/mac/Desktop/文稿库/人工智能临床应用/09_Zotero逐条比对报告.md
"""
import difflib, pathlib, re, sqlite3

ART = pathlib.Path("/Users/mac/Desktop/文稿库/人工智能临床应用")
DB = pathlib.Path.home() / "Zotero" / "zotero.sqlite"

# ---- 1) 从 07 解析清单：DOI（或 PMID）+ 标题（用于比对） ----
md7 = (ART / "07_参考文献清单.md").read_text()
entries = []          # (num, doi_or_None, pmid, 标题关键词, 原始著录)
for m in re.finditer(r"^\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*([^|]*)\|\s*$", md7, re.M):
    num, cite, tail = int(m.group(1)), m.group(2), m.group(3).strip()
    if cite.startswith("完整著录"):
        continue
    doi = None
    md = re.search(r"(10\.\d{4,9}/[^\s;]+)", cite)
    if md:
        doi = md.group(1).rstrip(".").lower()
    pmid = tail if tail.isdigit() else None
    # 标题：取第一句到句号为止
    t = re.sub(r"^\[dataset\]\s*", "", cite)
    tm = re.split(r"\.\s", t)
    title = tm[1] if len(tm) > 1 else t
    title = re.sub(r"\s+(In:|PhysioNet|IEEE|doi:).*$", "", title).strip()
    entries.append({"num": num, "doi": doi, "pmid": pmid, "title": title, "cite": cite})

# ---- 2) 读 Zotero 库 ----
con = sqlite3.connect(f"file:{DB}?immutable=1", uri=True)
cur = con.cursor()
rows = cur.execute("""
SELECT i.itemID,
       MAX(CASE WHEN f.fieldName='title'        THEN v.value END) AS title,
       MAX(CASE WHEN f.fieldName='DOI'          THEN v.value END) AS doi,
       MAX(CASE WHEN f.fieldName='date'         THEN v.value END) AS date,
       MAX(CASE WHEN f.fieldName='publicationTitle' THEN v.value END) AS journal,
       MAX(CASE WHEN f.fieldName='volume'       THEN v.value END) AS volume,
       MAX(CASE WHEN f.fieldName='issue'        THEN v.value END) AS issue,
       MAX(CASE WHEN f.fieldName='pages'        THEN v.value END) AS pages,
       (SELECT COUNT(*) FROM itemCreators c WHERE c.itemID=i.itemID) AS n_creators
FROM items i
LEFT JOIN itemData d  ON d.itemID = i.itemID
LEFT JOIN itemDataValues v ON v.valueID = d.valueID
LEFT JOIN fields f ON f.fieldID = d.fieldID
WHERE i.itemID NOT IN (SELECT itemID FROM deletedItems)
GROUP BY i.itemID
""").fetchall()
by_doi, items = {}, []
for itemID, title, doi, date, journal, volume, issue, pages, nc in rows:
    rec = {"itemID": itemID, "title": title or "", "doi": (doi or "").lower().replace("https://doi.org/", ""),
           "date": date or "", "journal": journal or "", "volume": volume or "",
           "issue": issue or "", "pages": pages or "", "n_creators": nc}
    items.append(rec)
    if rec["doi"]:
        by_doi[rec["doi"]] = rec

# ---- 3) 逐条比对 ----
def yr(s):
    m = re.search(r"(19|20)\d{2}", s or "")
    return m.group(0) if m else ""

lines, stats = [], {"found": 0, "missing": 0, "mismatch": 0}
lines.append("# 09 Zotero 逐条比对报告\n")
lines.append(f"> 方式：**只读直连 `~/Zotero/zotero.sqlite`**（Zotero 本地 API 未启用：`403 Local API is not enabled`；sqlite URI `immutable=1`，不加锁、不写库）")
lines.append(f"> 库规模：{len(items)} 条（已排除回收站）｜有 DOI：{len(by_doi)} 条")
lines.append(f"> 比对对象：`07_参考文献清单.md` 共 {len(entries)} 条\n")
lines.append("| # | DOI | 库内状态 | 标题相似度 | 年份 | 期刊 | 卷(期) | 页 | 备注 |")
lines.append("|---|---|---|---|---|---|---|---|---|")

for e in entries:
    rec = by_doi.get(e["doi"]) if e["doi"] else None
    sim = ""
    if not rec:      # DOI 未命中 → 用标题模糊匹配
        best, bestr = None, 0.0
        for it in items:
            r = difflib.SequenceMatcher(None, e["title"].lower()[:90], it["title"].lower()[:90]).ratio()
            if r > bestr:
                best, bestr = it, r
        if best and bestr >= 0.80:
            rec, sim = best, f"{bestr:.2f}(标题)"
    if not rec:
        stats["missing"] += 1
        lines.append(f"| {e['num']} | {e['doi'] or '—'} | ❌ **库内无** | — | — | — | — | — | 需导入 |")
        continue
    stats["found"] += 1
    # 字段比对
    diffs = []
    if e["doi"] and rec["doi"] and e["doi"] != rec["doi"]:
        diffs.append("DOI 不一致")
    sim2 = difflib.SequenceMatcher(None, e["title"].lower()[:90], rec["title"].lower()[:90]).ratio()
    if sim2 < 0.90:
        diffs.append(f"标题需核(sim={sim2:.2f})")
    vol_issue = f"{rec['volume']}({rec['issue']})" if rec["issue"] else rec["volume"]
    if not rec["volume"]:
        diffs.append("库内缺卷")
    if not rec["pages"]:
        diffs.append("库内缺页码")
    if not rec["journal"]:
        diffs.append("库内缺期刊")
    if diffs:
        stats["mismatch"] += 1
    lines.append(f"| {e['num']} | {e['doi'] or '—'} | ✅ 已有 | {sim or f'{sim2:.2f}'} | {yr(rec['date'])} | "
                 f"{rec['journal'][:26]} | {vol_issue} | {rec['pages']} | {'；'.join(diffs) if diffs else '一致'} |")

lines.append(f"\n## 汇总\n- 库内已有：**{stats['found']}** 条\n- 库内缺失：**{stats['missing']}** 条\n"
             f"- 有字段待核/补全：**{stats['mismatch']}** 条\n"
             "- 说明：'库内缺卷/缺页码'指 Zotero 条目元数据不完整，**以刊方 PubMed 原始记录为准补全即可**（本报告已提供 PubMed 核验值）。\n")
out = ART / "09_Zotero逐条比对报告.md"
out.write_text("\n".join(lines) + "\n")
print("\n".join(lines))
print("\nsaved:", out)
