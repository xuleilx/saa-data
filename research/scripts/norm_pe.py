#!/usr/bin/env python3
"""正常化 PE：当前总市值 / 近 8 年（2018-2025）归母净利润均值。

口径优势：只用净利润绝对值与当前市值，不依赖价格复权序列。
period_pos = TTM 归母 / 窗口均值    (>1 表示盈利处于周期均值之上)
"""
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path("/home/work/workspace01/bmc/xuleihs/study/saa")
CLI = ROOT / ".qoder/skills/hithink-finance-query/scripts/cli.py"

NAMES = ["宁德时代", "中国中车", "杭叉集团", "华泰证券", "中国平安",
         "吉比特", "巨人网络", "华东医药", "羚锐制药", "东鹏饮料"]
FIELDS = "近8年归母净利润 总市值 市盈率ttm 市净率"

out_path = ROOT / ".cache" / "screen" / "norm_pe_raw.json"
rows = []
for i in range(0, len(NAMES), 5):
    batch = NAMES[i:i + 5]
    q = " ".join(batch) + " " + FIELDS
    cp = subprocess.run(
        [sys.executable, str(CLI), "--query", q, "--limit", "20", "--timeout", "120"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    try:
        payload = json.loads(cp.stdout[cp.stdout.index("{"):])
    except Exception:
        print(f"❌ 解析失败 batch={batch}\n{cp.stdout[:400]}\n{cp.stderr[:400]}", file=sys.stderr)
        continue
    print(f"batch {i//5+1}: {payload.get('code_count')} 条", file=sys.stderr)
    rows.extend(payload.get("datas") or [])

out_path.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")

recs = []
for it in rows:
    name = str(it.get("股票简称") or "").strip()
    if name not in NAMES:
        continue
    ys = {}
    for k, v in it.items():
        if k.startswith("归母净利润[") and k[6:14].isdigit():
            try:
                ys[int(k[6:10])] = float(v) / 1e8
            except (TypeError, ValueError):
                pass
    if not ys:
        continue
    mcap = None
    for k, v in it.items():
        if k.startswith("总市值[") or k == "总市值":
            try:
                mcap = float(v) / 1e8
            except (TypeError, ValueError):
                pass
    pe_ttm = None
    for k, v in it.items():
        if k.startswith("市盈率ttm") or k.startswith("市盈率TTM") or "市盈率" in k:
            try:
                pe_ttm = float(v)
            except (TypeError, ValueError):
                pass
    pb = None
    for k, v in it.items():
        if k.startswith("市净率"):
            try:
                pb = float(v)
            except (TypeError, ValueError):
                pass
    wins = sorted(ys)[-8:]
    full_avg = sum(ys[y] for y in wins) / len(wins)
    last5 = sorted(ys)[-5:]
    avg5 = sum(ys[y] for y in last5) / len(last5)
    ttm = mcap / pe_ttm if (mcap and pe_ttm) else None
    recs.append({
        "name": name,
        "mcap_yi": round(mcap, 0) if mcap else None,
        "pe_ttm": pe_ttm,
        "pb": pb,
        "years": f"{wins[0]}-{wins[-1]}({len(wins)})",
        "avg8_yi": round(full_avg, 1),
        "norm_pe8": round(mcap / full_avg, 1) if mcap else None,
        "avg5_yi": round(avg5, 1),
        "norm_pe5": round(mcap / avg5, 1) if mcap else None,
        "ttm_yi": round(ttm, 1) if ttm else None,
        "pos": round(ttm / full_avg, 2) if (ttm and full_avg > 0) else None,
        "pe_pct_pos": round((ttm / full_avg - 1) * 100, 0) if (ttm and full_avg > 0) else None,
        "np_series": " ".join(f"{y}:{ys[y]:.0f}" for y in wins),
    })

df = pd.DataFrame(recs)
df.to_csv(ROOT / ".cache" / "screen" / "norm_pe.csv", index=False)
pd.set_option("display.width", 260, "display.max_columns", 30, "display.max_colwidth", 90)
print("\n=== 正常化 PE：市值 / 近8年归母均值 ===")
print(df[["name", "mcap_yi", "pe_ttm", "avg8_yi", "norm_pe8", "norm_pe5",
          "ttm_yi", "pos", "pe_pct_pos"]].to_string(index=False))
print("\n=== 年度归母净利润（亿元）===")
for r in recs:
    print(f"{r['name']:<6} {r['np_series']}")
