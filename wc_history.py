# -*- coding: utf-8 -*-
"""拉取白酒龙头历史年度财报（1998-2020），复盘 1998-2003 与 2012-2015 两轮调整"""
import akshare as ak

codes = {
    "600519": "贵州茅台",
    "000858": "五粮液",
    "000568": "泸州老窖",
    "600809": "山西汾酒",
    "002304": "洋河股份",
    "000596": "古井贡酒",
}

for code, name in codes.items():
    print("=" * 24, name, code)
    try:
        df = ak.stock_financial_abstract_ths(symbol=code, indicator="按年度")
        cols = list(df.columns)
        keep = [
            c
            for c in ["报告期", "营业总收入", "营业总收入同比增长率", "净利润", "净利润同比增长率"]
            if c in cols
        ]
        if not keep:
            print("cols:", cols)
            continue
        d = df[keep].copy()
        d["_rp"] = d["报告期"].astype(str)
        d = d[d["_rp"].str.contains("199|200|2010|2011|2012|2013|2014|2015|2016|2017|2018|2019|2020", regex=True)]
        print(d.to_string(index=False))
    except Exception as e:
        print("ERROR:", repr(e))

print("#" * 30, "分季度 2012-2016（找单季拐点）")
for code in ["600519", "000858", "000568", "600809"]:
    print("=" * 24, code)
    try:
        df = ak.stock_financial_abstract_ths(symbol=code, indicator="按报告期")
        keep = [
            c
            for c in ["报告期", "营业总收入", "营业总收入同比增长率", "净利润", "净利润同比增长率"]
            if c in df.columns
        ]
        d = df[keep].copy()
        d["_rp"] = d["报告期"].astype(str)
        d = d[d["_rp"].str.contains("2012|2013|2014|2015|2016", regex=True)]
        print(d.to_string(index=False))
    except Exception as e:
        print("ERROR:", repr(e))
