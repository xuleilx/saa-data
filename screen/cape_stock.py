#!/usr/bin/env python3
"""个股 CAPE（席勒 PE）测算：复用 saa.market.cape 的 CPI 定基与滚动均值口径。

EPS_t     = 收盘价_t / PE-TTM_t      （序列同源）
real_eps_t = EPS_t × CPI_最新 / CPI_t
CAPE       = 最新价 / 近 N 个月真实 EPS 均值
period_pos = 真实 EPS 当前值 / 窗口均值      （>1 说明盈利在周期均值之上）
"""
import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path("/home/work/workspace01/bmc/xuleihs/study/saa")
sys.path.insert(0, str(ROOT))
from saa.market.cape import _load_cpi, compute_cape_monthly  # noqa: E402

STOCKS = {
    "300750": ("宁德时代", "电力设备"),
    "601766": ("中国中车", "机械设备"),
    "603298": ("杭叉集团", "机械设备"),
    "601688": ("华泰证券", "非银金融"),
    "601318": ("中国平安", "非银金融"),
    "603444": ("吉比特", "传媒"),
    "002558": ("巨人网络", "传媒"),
    "000963": ("华东医药", "医药生物"),
    "600285": ("羚锐制药", "医药生物"),
    "605499": ("东鹏饮料", "食品饮料"),
}

cpi_levels, cpi_diff = _load_cpi(no_cache=False)
print(f"CPI 定基校验最大偏差 {cpi_diff:.3f}pct，最新月 {cpi_levels.index[-1]}", file=sys.stderr)

con = sqlite3.connect(ROOT / "data" / "market.db")
rows = []
detail = {}
for code, (name, ind) in STOCKS.items():
    df = pd.read_sql(
        "select trade_date, metric, value from market_bars "
        "where symbol=? and metric in ('close','pe_ttm')",
        con, params=(code,),
    )
    piv = df.pivot_table(index="trade_date", columns="metric", values="value", aggfunc="last")
    piv.index = pd.to_datetime(piv.index)
    piv = piv.sort_index()
    close = piv["close"].dropna()
    pe = piv["pe_ttm"].where(piv["pe_ttm"] > 0).dropna()

    m = compute_cape_monthly(close, pe, cpi_levels, 120, allow_short=True)
    if len(m) < 24:
        print(f"⚠ {name} 月样本不足 {len(m)}", file=sys.stderr)
        continue

    out = {"code": code, "name": name, "industry": ind,
           "close_now": float(close.iloc[-1]), "pe_now": float(pe.iloc[-1]),
           "months": len(m), "start": str(m.index[0])}

    # PE 分位（序列自身可比口径）
    out["pe_pct"] = round(float((m["pe"] < out["pe_now"]).mean() * 100), 1)

    for win in (120, 60):
        # 序列分位用 min_periods=36 才能形成历史分布；当前值用完整窗口均值
        minp = min(win, 36, len(m))
        mean_real = m["real_eps"].rolling(win, min_periods=minp).mean()
        cape = (m["close"] / mean_real).dropna()
        win_n = min(win, len(m))
        eps_avg = float(m["real_eps"].iloc[-win_n:].mean())
        cape_now = out["close_now"] / eps_avg
        tag = f"cape{win}"
        out[f"{tag}"] = round(cape_now, 2)
        out[f"{tag}_pct"] = round(float((cape < cape_now).mean() * 100), 1)
        out[f"{tag}_n"] = len(cape)
        out[f"{tag}_min"] = round(float(cape.min()), 2)
        out[f"{tag}_med"] = round(float(cape.median()), 2)
        out[f"{tag}_max"] = round(float(cape.max()), 2)
        out[f"{tag}_fair"] = round(out[f"{tag}_med"] * eps_avg, 2)
        out[f"{tag}_cheap"] = round(out[f"{tag}_min"] * eps_avg, 2)
        out[f"{tag}_pos"] = round(float(m["real_eps"].iloc[-1]) / eps_avg, 2)

    # 周期位置再给一个 TTM EPS 相对 12 个月前的变化
    out["eps_ttm"] = round(out["close_now"] / out["pe_now"], 3)
    if len(m) >= 13:
        out["eps_yoy"] = round(
            float(m["eps"].iloc[-1]) / float(m["eps"].iloc[-13]) - 1, 4)
    detail[name] = m
    rows.append(out)

res = pd.DataFrame(rows)
cols = ["code", "name", "industry", "close_now", "pe_now", "pe_pct",
        "cape120", "cape120_pct", "cape120_pos", "cape120_med", "cape120_fair",
        "cape60", "cape60_pct", "cape60_pos", "cape60_med", "cape60_fair",
        "eps_ttm", "eps_yoy", "months", "start"]
res = res[[c for c in cols if c in res.columns]]
res.to_csv(ROOT / ".cache" / "screen" / "stock_cape.csv", index=False)
pd.set_option("display.width", 240, "display.max_columns", 40)

print("\n=== 个股 CAPE（窗口 120 月，不足则以全部可得月份替代）===")
print(res[["name", "close_now", "pe_now", "pe_pct", "cape120", "cape120_pct",
           "cape120_pos", "cape120_med", "cape120_fair", "eps_yoy"]].to_string(index=False))
print("\n=== 对照：窗口 60 月 ===")
print(res[["name", "cape60", "cape60_pct", "cape60_pos", "cape60_med", "cape60_fair"]].to_string(index=False))

print("\n=== 年度真实 EPS 序列（CPI 定基到最新月）===")
for name, m in detail.items():
    yr = m["real_eps"].resample("Y").mean().round(3)
    print(f"{name:<6}", " ".join(f"{i.year}:{v}" for i, v in yr.items() if v == v))
