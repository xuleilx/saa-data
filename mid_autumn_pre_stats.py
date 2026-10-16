# -*- coding: utf-8 -*-
"""中秋节前后交易日涨跌幅统计（基准：上证指数 sh000001，1991-2025）"""
import pandas as pd
import akshare as ak
from lunardate import LunarDate

mid_autumn = {y: pd.Timestamp(LunarDate(y, 8, 15).to_solar_date()) for y in range(1991, 2026)}

df = ak.stock_zh_index_daily(symbol="sh000001")
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)
df["pct"] = df["close"].pct_change() * 100

rows = []
for year, d in sorted(mid_autumn.items()):
    pre = df[df["date"] < d]
    post = df[df["date"] > d]
    if pre.empty or post.empty:
        continue
    pre_idx = pre.index[-1]
    post_idx = post.index[0]
    pre_row = df.loc[pre_idx]
    post_row = df.loc[post_idx]
    cum5pre = (pre_row["close"] / df.loc[pre_idx - 5, "close"] - 1) * 100 if pre_idx >= 5 else None
    seg5 = df.loc[post_idx: post_idx + 4]
    cum5post = (seg5["close"].iloc[-1] / pre_row["close"] - 1) * 100 if len(seg5) == 5 else None
    rows.append({
        "年份": year,
        "中秋": d.strftime("%m-%d"),
        "中秋当天": "开市" if (df["date"] == d).any() else "休市",
        "节前末日": pre_row["date"].strftime("%m-%d"),
        "节前末日涨跌%": round(pre_row["pct"], 4),
        "节前5日累计%": round(cum5pre, 4) if cum5pre is not None else None,
        "节后首日": post_row["date"].strftime("%m-%d"),
        "节后首日涨跌%": round(post_row["pct"], 4),
        "节后5日累计%": round(cum5post, 4) if cum5post is not None else None,
    })

res = pd.DataFrame(rows)
print(res.to_string(index=False))

def summary(sub, col, label):
    n = len(sub)
    up = int((sub[col] > 0).sum())
    down = int((sub[col] < 0).sum())
    vals = sub[col].dropna()
    print(f"\n=== {label}（{n} 个样本）===")
    print(f"上涨 {up} 次（{up/n*100:.1f}%） | 下跌 {down} 次（{down/n*100:.1f}%） | 平盘 {n-up-down} 次")
    print(f"平均 {vals.mean():+.2f}% | 中位数 {vals.median():+.2f}% | 标准差 {vals.std():.2f}%")
    print(f"最大 {vals.max():+.2f}%（{int(sub.loc[vals.idxmax(), '年份'])} 年）"
          f" | 最小 {vals.min():+.2f}%（{int(sub.loc[vals.idxmin(), '年份'])} 年）")

for col in ["节前末日涨跌%", "节前5日累计%", "节后首日涨跌%", "节后5日累计%"]:
    print(f"\n########## {col} ##########")
    summary(res, col, "全部 1991-2025")
    summary(res[res["年份"] <= 2007], col, "1991-2007（中秋非法定假日）")
    summary(res[res["年份"] >= 2008], col, "2008-2025（中秋为法定假日）")
    summary(res[res["年份"] >= 2016], col, "近十年 2016-2025")

same = (res["节前末日涨跌%"] > 0) == (res["节后首日涨跌%"] > 0)
print(f"\n中秋：节前末日与节后首日同向 {int(same.sum())} 次 / 反向 {int((~same).sum())} 次（共 {len(res)} 次）")
print("反向年份:", res.loc[~same, "年份"].astype(int).tolist())

# 对照：国情节前 5 日累计
nd = []
for year in range(1991, 2026):
    oct1 = pd.Timestamp(f"{year}-10-01")
    pre = df[df["date"] < oct1]
    if pre.empty:
        continue
    pre_idx = pre.index[-1]
    cum5 = (df.loc[pre_idx, "close"] / df.loc[pre_idx - 5, "close"] - 1) * 100 if pre_idx >= 5 else None
    nd.append({"年份": year, "节前5日累计%": round(cum5, 4)})
nd = pd.DataFrame(nd)
print("\n########## 国情节前5日累计%（对照） ##########")
summary(nd, "节前5日累计%", "全部 1991-2025")
summary(nd[nd["年份"] <= 1998], "节前5日累计%", "1991-1998（无黄金周）")
summary(nd[nd["年份"] >= 1999], "节前5日累计%", "1999-2025（黄金周时代）")
summary(nd[nd["年份"] >= 2016], "节前5日累计%", "近十年 2016-2025")
