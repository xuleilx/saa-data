# -*- coding: utf-8 -*-
"""用 akshare（同花顺财报摘要）拉取七家白酒龙头 2023-2026 各报告期营收/净利同比增速"""
import akshare as ak

codes = {
    "600519": "贵州茅台",
    "000858": "五粮液",
    "000568": "泸州老窖",
    "600809": "山西汾酒",
    "002304": "洋河股份",
    "000596": "古井贡酒",
    "603369": "今世缘",
}

for code, name in codes.items():
    print("=" * 24, name, code)
    try:
        df = ak.stock_financial_abstract_ths(symbol=code, indicator="按报告期")
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
        d = d[d["_rp"].str.contains("2023|2024|2025|2026", regex=True)]
        print(d.to_string(index=False))
    except Exception as e:
        print("ERROR:", repr(e))
