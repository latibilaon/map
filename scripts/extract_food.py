#!/usr/bin/env python3
"""Extract 美西餐厅筛选 docx into structured JSON for the /food page."""
import json, re, sys
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

SRC = "/Users/ponjuy/Desktop/美国核心攻略/美西沿途餐厅筛选_V2_2026核实版_20260707.docx"
OUT = "food-data.json"

doc = Document(SRC)

def iter_block_items(doc):
    from docx.oxml.ns import qn
    body = doc.element.body
    for child in body.iterchildren():
        if child.tag == qn('w:p'):
            yield Paragraph(child, doc)
        elif child.tag == qn('w:tbl'):
            yield Table(child, doc)

DAY_RE = re.compile(r'^(8/\d{1,2})\s+(\w{3})｜(.+)$')

days = []          # [{date, weekday, route, notes:[], top5:[], types:[], pool:[]}]
preamble = {"intro": [], "michelin": [], "parks": [], "landmines": [], "logic": []}
booking_tiers = [] # global 预订清单 table
anchors = []       # appendix A
checklist_done, checklist_todo = [], []

cur_day = None
section = "pre"    # pre -> days -> appendix
last_heading = ""

def clean(s):
    return re.sub(r'\s+', ' ', s.replace(' ', ' ')).strip()

def table_rows(tbl):
    rows = []
    for r in tbl.rows:
        cells = [clean('\n'.join(p.text for p in c.paragraphs)) for c in r.cells]
        rows.append(cells)
    return rows

for block in iter_block_items(doc):
    if isinstance(block, Paragraph):
        t = clean(block.text)
        if not t:
            continue
        m = DAY_RE.match(t)
        if m:
            cur_day = {"date": m.group(1), "weekday": m.group(2), "route": m.group(3).strip(),
                       "notes": [], "top5": [], "types": [], "pool": [], "pool_count": None}
            days.append(cur_day)
            section = "days"
            last_heading = ""
            continue
        if t.startswith("主要来源"):
            section = "sources"; cur_day = None; continue
        if t.startswith("附录 A"):
            section = "appendixA"; cur_day = None; continue
        if t.startswith("附录 B"):
            section = "appendixB"; cur_day = None; continue
        if section == "appendixB":
            if t.startswith("已完成"):
                last_heading = "done"; continue
            if t.startswith("仍需"):
                last_heading = "todo"; continue
            body = t.lstrip("☑☐ ").strip()
            if last_heading == "done": checklist_done.append(body)
            elif last_heading == "todo": checklist_todo.append(body)
            continue
        if cur_day is not None:
            if t in ("总推荐", "不同类型推荐", "完整候选表") or t.startswith("【V2"):
                last_heading = t
                continue
            m2 = re.match(r'候选池数量：(\d+)', t)
            if m2:
                cur_day["pool_count"] = int(m2.group(1)); continue
            # everything else in a day before tables = V2 notes / execution advice
            cur_day["notes"].append(t)
        elif section == "pre":
            preamble["intro"].append(t)
    else:  # Table
        rows = table_rows(block)
        if not rows: continue
        header = rows[0]
        if cur_day is not None:
            if header[0].startswith("排序") or (len(header) == 2 and "首选" in header[1]):
                for r in rows[1:]:
                    if len(r) >= 2 and r[1]:
                        cur_day["top5"].append(clean(r[1]))
            elif header[0].startswith("类型") and len(header) == 3:
                for r in rows[1:]:
                    if len(r) >= 3:
                        cur_day["types"].append({"type": r[0], "pick": r[1], "tip": r[2]})
            elif "English" in ' '.join(header) or header[0].startswith("级别"):
                # candidate pool: 级别, English name, 位置, 类型/特色, 餐次, 人均/评分, [预订], 执行建议
                ncols = len(header)
                for r in rows[1:]:
                    if len(r) < 6: continue
                    if ncols >= 8:
                        rec = {"tier": r[0], "name": r[1], "loc": r[2], "kind": r[3],
                               "meal": r[4], "price": r[5], "book": r[6], "tip": r[7] if len(r) > 7 else ""}
                    else:  # 7 cols, no separate 预订
                        rec = {"tier": r[0], "name": r[1], "loc": r[2], "kind": r[3],
                               "meal": r[4], "price": r[5], "book": "", "tip": r[6] if len(r) > 6 else ""}
                    if rec["name"]:
                        cur_day["pool"].append(rec)
        elif section == "appendixA" or (header and header[0].startswith("日期")):
            for r in rows[1:]:
                if len(r) >= 5:
                    anchors.append({"date": r[0], "anchor": r[1], "platform": r[2],
                                    "window": r[3], "note": r[4]})
            section = "appendixA_done"
        elif section == "pre" and header[0].startswith("层级"):
            for r in rows[1:]:
                if len(r) >= 2:
                    booking_tiers.append({"tier": r[0], "list": r[1]})

data = {"preamble": preamble["intro"], "booking_tiers": booking_tiers,
        "days": days, "anchors": anchors,
        "checklist_done": checklist_done, "checklist_todo": checklist_todo}

with open(OUT, "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

print(f"days={len(days)}")
for d in days:
    print(f"  {d['date']} {d['weekday']} pool={len(d['pool'])}/{d['pool_count']} top5={len(d['top5'])} types={len(d['types'])} notes={len(d['notes'])}")
print(f"booking_tiers={len(booking_tiers)} anchors={len(anchors)} checklist={len(checklist_done)}+{len(checklist_todo)}")

# ---------- post-process: repair shifted rows + classify ----------
import re as _re

TIER_OK = _re.compile(r'(必|建议|否|强烈|不可控|排队|电话|候选|补给|快速|早餐|咖啡|打包|酒吧|正餐|海|机场|稳妥|轻|经典|特色|家庭|平价|高端|BBQ|Bib|Selected|One Star|pizza|pub|Diner|diner|Mexican|Spanish|Traditional|ranch|Deli|24h|food truck|Gardiner|Bozeman|Belgrade|Pebble|17-Mile|Steak|Global|Italian|Casual|Rooftop|Patio|Bistro|Tapas|Seafood|地标)')

def fix_pool(days):
    fixed = 0
    for d in days:
        for p in d["pool"]:
            t = p["tier"]
            if not (t.startswith(("A", "B", "C")) and len(t) < 20) and not TIER_OK.search(t):
                # shifted row: name landed in tier
                p2 = {"tier": "B 候选", "name": t, "loc": p["name"],
                      "kind": (p["loc"] + " / " + p["kind"]).strip(" /"),
                      "meal": "", "price": p["price"], "book": p["book"] or p["meal"],
                      "tip": p["tip"]}
                p.update(p2); fixed += 1
    return fixed

def classify(p):
    text = p["kind"] + " " + p["tier"]
    # michelin badge
    star = ""
    k = p["kind"]
    if _re.search(r'3 Stars|三星|Michelin 3', k): star = "三星"
    elif _re.search(r'2 Stars?|二星|Two Stars', k): star = "二星"
    elif _re.search(r'One Star|1 Star|一星', k): star = "一星"
    elif _re.search(r'Bib', k): star = "Bib"
    elif _re.search(r'Michelin Selected|Selected', k): star = "Selected"
    elif _re.search(r'Michelin Guide|Michelin 高端|Green Star', k): star = "Guide"
    elif _re.search(r'James Beard|JBF', k + " " + p["price"]): star = "JBF"
    p["star"] = star
    # category
    if star and star not in ("JBF",) or _re.search(r'高端|fine dining|tasting|omakase|steakhouse|Steakhouse|名人餐厅', text):
        cat = "fine" if (star in ("三星","二星","一星") or _re.search(r'高端|tasting|omakase|fine dining', text)) else "feature"
    else:
        cat = "feature"
    if _re.search(r'早餐咖啡|咖啡|bakery|Bakery|coffee|Coffee|brunch|早餐经典|donuts|甜品|甜点|Ice Cream|ice cream', text): cat = "cafe"
    if _re.search(r'补给|grocery|超市|deli(?!ca)|Deli|General Store|Market(?! &)|打包|机场快餐|机场补给|机场正餐|机场经典', text): cat = "supply"
    if _re.search(r'平价|快速|快餐|保底|cafeteria|food hall|counter|taco|Taco|burger|Burger|pizza(?!ria M)|Pizza(?! Deck)', text) and cat not in ("cafe","supply"): cat = "fast"
    if _re.search(r'园内正餐|园内高端|园内轻食|园内 casual|景区补给', text): cat = "park"
    if star in ("三星","二星","一星") or _re.search(r'Michelin 高端', text): cat = "fine"
    p["cat"] = cat
    # booking level
    b = p["book"] + " " + p["tier"]
    if _re.search(r'必须|必订|必须预订', b): lvl = "must"
    elif _re.search(r'强烈', b): lvl = "strong"
    elif _re.search(r'建议|复核|电话|查|早到|排队', b): lvl = "should"
    else: lvl = "walkin"
    p["bk"] = lvl

fixed = fix_pool(days)
for d in days:
    for p in d["pool"]:
        classify(p)

with open(OUT, "w") as f:
    json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

import collections
cats = collections.Counter(p["cat"] for dd in days for p in dd["pool"])
bks = collections.Counter(p["bk"] for dd in days for p in dd["pool"])
stars = collections.Counter(p["star"] for dd in days for p in dd["pool"] if p["star"])
print(f"repaired={fixed} cats={dict(cats)} bk={dict(bks)} stars={dict(stars)}")
