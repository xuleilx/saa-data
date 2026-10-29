# -*- coding: utf-8 -*-
"""国庆节前后交易日涨跌幅统计（基准：上证指数 sh000001，1991-2025）"""
import pandas as pd
import akshare as ak

df = ak.stock_zh_index_daily(symbol="sh000001")
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)
df["pct"] = df["close"].pct_change() * 100

# 检查：历史上 10-01 当天是否出现过交易日
oct1_traded = df[df["date"].dt.strftime("%m-%d") == "10-01"]["date"].dt.year.tolist()
print("历史上 10月1日当天开市的年份:", oct1_traded if oct1_traded else "无（从未开市）")

rows = []
for year in range(1991, 2026):
    oct1 = pd.Timestamp(f"{year}-10-01")
    pre = df[df["date"] < oct1]
    post = df[df["date"] >= oct1]
    if pre.empty or post.empty:
        continue
    pre_row = df.loc[pre.index[-1]]
    post_idx = post.index[0]
    post_row = df.loc[post_idx]
    seg5 = df.loc[post_idx: post_idx + 4]          # 节后前5个交易日
    cum5 = (seg5["close"].iloc[-1] / pre_row["close"] - 1) * 100 if len(seg5) == 5 else None
    rows.append({
        "年份": year,
        "节前末日": pre_row["date"].strftime("%m-%d"),
        "节前末日涨跌%": round(pre_row["pct"], 4),
        "节后首日": post_row["date"].strftime("%m-%d"),
        "节后首日涨跌%": round(post_row["pct"], 4),
        "间隔自然日": (post_row["date"] - pre_row["date"]).days,
        "节后5日累计%": round(cum5, 4) if cum5 is not None else None,
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

print("\n" + "=" * 60)
for col in ["节前末日涨跌%", "节后首日涨跌%", "节后5日累计%"]:
    print(f"\n########## {col} ##########")
    summary(res, col, "全部 1991-2025")
    summary(res[res["年份"] <= 1998], col, "1991-1998（无黄金周）")
    summary(res[res["年份"] >= 1999], col, "1999-2025（黄金周时代）")
    summary(res[res["年份"] >= 2016], col, "近十年 2016-2025")

# 节前末日 vs 节后首日的"反转/延续"观察
print("\n=== 节前末日与节后首日方向一致性 ===")
same = (res["节前末日涨跌%"] > 0) == (res["节后首日涨跌%"] > 0)
print(f"同向 {int(same.sum())} 次 / 反向 {int((~same).sum())} 次（共 {len(res)} 次）")
print("反向（节前涨节后跌或反之）年份:", res.loc[~same, "年份"].astype(int).tolist())
