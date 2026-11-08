# -*- coding: utf-8 -*-
"""解析问财年度同比增速缓存（wc_2021..wc_2026h1），输出七家白酒龙头增速总表"""
import json
import re
import os

files = ["wc_2021", "wc_2022", "wc_2023", "wc_2024", "wc_2025", "wc_2026h1"]
companies = {}
for lab in files:
    path = f".cache/{lab}.json"
    if not os.path.exists(path):
        print("missing", path)
        continue
    d = json.load(open(path))
    for it in d.get("datas", []):
        name = it.get("股票简称")
        norm = {}
        for k, v in it.items():
            nk = re.sub(r"\[.*?\]", "", k.replace(" ", ""))
            norm[nk] = v
        rec = companies.setdefault(name, {})
        tag = lab.replace("wc_", "")
        rec["rev_" + tag] = norm.get("营业总收入同比增长率")
        rec["np_" + tag] = norm.get("归母净利润同比增长率")
        rec["npabs_" + tag] = norm.get("归母净利润")

order = ["贵州茅台", "五粮液", "泸州老窖", "山西汾酒", "洋河股份", "古井贡酒", "今世缘"]
labels = ["2021", "2022", "2023", "2024", "2025", "2026h1"]
disp = ["2021", "2022", "2023", "2024", "2025", "2026H1"]


def fmt(v):
    if v is None:
        return "NA"
    try:
        return f"{v:+.1f}%"
    except Exception:
        return str(v)


print("== 营收同比 ==")
header = "公司".ljust(8) + "".join(d.rjust(9) for d in disp)
print(header)
for name in order:
    r = companies.get(name, {})
    row = name.ljust(8)
    for lab in labels:
        row += fmt(r.get("rev_" + lab)).rjust(9)
    print(row)

print()
print("== 归母净利同比 ==")
print(header)
for name in order:
    r = companies.get(name, {})
    row = name.ljust(8)
    for lab in labels:
        row += fmt(r.get("np_" + lab)).rjust(9)
    print(row)

print()
print("== 归母净利绝对值（亿） ==")
print(header)
for name in order:
    r = companies.get(name, {})
    row = name.ljust(8)
    for lab in labels:
        v = r.get("npabs_" + lab)
        if v is None:
            row += "NA".rjust(9)
        else:
            try:
                row += f"{v / 1e8:.1f}".rjust(9)
            except Exception:
                row += str(v).rjust(9)
    print(row)
