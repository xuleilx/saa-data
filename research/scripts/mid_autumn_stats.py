# -*- coding: utf-8 -*-
"""中秋节后首个交易日涨跌幅统计（基准：上证指数 sh000001，1991-2025）"""
import pandas as pd
import akshare as ak
from lunardate import LunarDate

# 1) 历年中秋（农历八月十五）折算公历日期
mid_autumn = {y: pd.Timestamp(LunarDate(y, 8, 15).to_solar_date()) for y in range(1991, 2026)}

# 2) 上证指数全历史日线
df = ak.stock_zh_index_daily(symbol="sh000001")
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)
df["pct"] = df["close"].pct_change() * 100

# 3) 每个中秋节 -> 其后首个交易日
rows = []
for year, d in sorted(mid_autumn.items()):
    fut = df[df["date"] > d]
    if fut.empty:
        continue
    r = df.loc[fut.index[0]]
    rows.append({
        "年份": year,
        "中秋日期": d.strftime("%Y-%m-%d"),
        "星期": "一二三四五六日"[d.weekday()],
        "中秋当天": "开市" if (df["date"] == d).any() else "休市",
        "节后首日": r["date"].strftime("%Y-%m-%d"),
        "间隔自然日": (r["date"] - d).days,
        "节后首日收盘": round(r["close"], 2),
        "首日涨跌幅%": round(r["pct"], 4),
    })

res = pd.DataFrame(rows)
print(res.to_string(index=False))

# 4) 分组统计
def summary(sub, label):
    n = len(sub)
    up = int((sub["首日涨跌幅%"] > 0).sum())
    down = int((sub["首日涨跌幅%"] < 0).sum())
    flat = n - up - down
    pcts = sub["首日涨跌幅%"]
    print(f"\n=== {label}（{n} 个样本）===")
    print(f"上涨 {up} 次（{up/n*100:.1f}%） | 下跌 {down} 次（{down/n*100:.1f}%） | 平盘 {flat} 次")
    print(f"平均 {pcts.mean():+.2f}% | 中位数 {pcts.median():+.2f}% | 标准差 {pcts.std():.2f}%")
    print(f"最大 {pcts.max():+.2f}%（{int(sub.loc[pcts.idxmax(), '年份'])} 年）"
          f" | 最小 {pcts.min():+.2f}%（{int(sub.loc[pcts.idxmin(), '年份'])} 年）")
    print(f"涨幅>1%的年份: {sorted(sub.loc[pcts > 1, '年份'].astype(int).tolist())}")
    print(f"跌幅>1%的年份: {sorted(sub.loc[pcts < -1, '年份'].astype(int).tolist())}")

summary(res, "全部 1991-2025")
summary(res[res["年份"] <= 2007], "1991-2007（中秋非法定假日）")
summary(res[res["年份"] >= 2008], "2008-2025（中秋为法定假日）")
summary(res[res["年份"] >= 2016], "近十年 2016-2025")
summary(res[res["中秋当天"] == "开市"], "中秋当天仍开市的年份（节后首日=中秋次日）")

# 5) 涨跌幅分布（按精确值分桶）
p = res["首日涨跌幅%"]
bins = [("> 2%", p > 2), ("1%~2%", (p > 1) & (p <= 2)), ("0~1%", (p > 0) & (p <= 1)),
        ("-1%~0", (p > -1) & (p <= 0)), ("-2%~-1%", (p > -2) & (p <= -1)), ("< -2%", p <= -2)]
print("\n=== 全样本涨跌幅分布（35 年）===")
for label, mask in bins:
    years = res.loc[mask, "年份"].astype(int).tolist()
    print(f"{label:>8}: {len(years):>2} 次  {years}")
