#!/usr/bin/env python3
"""周期股正常化估值修订版。

主口径（不受复权污染）:
  TTM 归母      = 2025 全年 + 2026H1 - 2025H1
  norm_pe8      = 当前总市值 / 近 8 年归母均值
  pos           = TTM 归母 / 8 年均值        (>1 盈利在周期均值之上)
  trough_pe     = 市值 / 8 年最低年度利润    (周期底部压力测试)
  peak_pe       = 市值 / 8 年最高年度利润
  pb_pct        = PB 历史分位（market.db，金融股主锚）
"""
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path("/home/work/workspace01/bmc/xuleihs/study/saa")

# name: (代码, 总市值亿, 2025全年, 2025H1, 2026H1, 年度净利序列)
DATA = {
    "中国平安": ("601318", 8670, 1348.0, 680.47, 925.85, [1074, 1494, 1431, 1016, 1110, 857, 1266, 1348]),
    "宁德时代": ("300750", 12309, 722.0, 304.85, 432.84, [34, 46, 56, 159, 307, 441, 507, 722]),
    "中国中车": ("601766", 1745, 132.0, 72.46, 79.91, [113, 118, 113, 103, 117, 117, 124, 132]),
    "华泰证券": ("601688", 1528, 164.0, 75.49, 116.92, [50, 90, 108, 133, 111, 128, 154, 164]),
    "杭叉集团": ("603298", 286, 22.0, None, None, [5, 6, 8, 9, 10, 17, 20, 22]),
    "巨人网络": ("002558", 403, 18.0, 7.77, 21.44, [11, 8, 10, 10, 9, 11, 14, 18]),
    "东鹏饮料": ("605499", 798, 44.0, 23.75, 28.67, [2, 6, 8, 12, 14, 20, 33, 44]),
    "吉比特": ("603444", 243, 18.0, None, None, [7, 8, 10, 15, 15, 11, 9, 18]),
    "羚锐制药": ("600285", 121, 8.0, None, None, [2, 3, 3, 4, 5, 6, 7, 8]),
    "华东医药": ("000963", 464, 34.0, None, None, [23, 28, 28, 23, 25, 28, 35, 34]),
}
# 未取到 2026H1 的标的，用 pe_ttm 反推的 TTM 兜底
TTM_FALLBACK = {"杭叉集团": 24.3, "吉比特": 21.9, "羚锐制药": 10.0, "华东医药": 37.2}
YEARS = list(range(2018, 2026))

con = sqlite3.connect(ROOT / "data" / "market.db")
recs = []
for name, (code, mcap, fy25, h125, h126, series) in DATA.items():
    s = pd.Series(series, index=YEARS, dtype=float)
    avg8 = float(s.mean())
    avg5 = float(s.iloc[-5:].mean())
    ttm = (fy25 + h126 - h125) if (h125 and h126) else TTM_FALLBACK.get(name)
    low, high = float(s.min()), float(s.max())

    pb_now = pb_pct = None
    df = pd.read_sql(
        "select trade_date, value from market_bars where symbol=? and metric='pb' order by trade_date",
        con, params=(code,))
    if len(df) > 100:
        v = pd.to_numeric(df["value"], errors="coerce").dropna()
        pb_now = float(v.iloc[-1])
        pb_pct = round(float((v < pb_now).mean() * 100), 1)

    recs.append({
        "name": name, "code": code, "mcap_yi": mcap,
        "pe_ttm": round(mcap / ttm, 1) if ttm else None,
        "ttm_yi": round(ttm, 1) if ttm else None,
        "avg8_yi": round(avg8, 1),
        "norm_pe8": round(mcap / avg8, 1),
        "norm_pe5": round(mcap / avg5, 1),
        "pos": round(ttm / avg8, 2) if ttm else None,
        "prem": round(mcap / avg8 / (mcap / ttm), 2) if ttm else None,
        "trough_pe": round(mcap / low, 1),
        "peak_pe": round(mcap / high, 1),
        "low_yi": round(low, 1), "high_yi": round(high, 1),
        "pb": round(pb_now, 2) if pb_now else None,
        "pb_pct": pb_pct,
    })

df = pd.DataFrame(recs).sort_values("prem", ascending=False)
df.to_csv(ROOT / ".cache" / "screen" / "norm_pe_v2.csv", index=False)
pd.set_option("display.width", 260, "display.max_columns", 30)
print("=== 周期股正常化估值（按正常化溢价降序）===")
print(df[["name", "mcap_yi", "pe_ttm", "norm_pe8", "norm_pe5", "pos", "prem",
          "trough_pe", "peak_pe", "pb", "pb_pct"]].to_string(index=False))
print("\n=== 8 年利润区间（亿元）===")
for r in recs:
    print(f"{r['name']:<6} 低 {r['low_yi']:>6.1f}  高 {r['high_yi']:>6.1f}  均值 {r['avg8_yi']:>7.1f}  "
          f"TTM {r['ttm_yi'] or 0:>7.1f}")
