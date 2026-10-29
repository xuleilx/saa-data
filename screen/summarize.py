"""汇总各行业候选股，输出紧凑表格。"""
import glob
import json
import os

OUT = "/home/work/workspace01/bmc/xuleihs/study/saa/.cache/screen"


def pick(item, key_prefix, default=None):
    for k, v in item.items():
        if k == key_prefix or k.startswith(key_prefix):
            return v
    return default


rows = []
for path in sorted(glob.glob(os.path.join(OUT, "ind_*.json"))):
    ind = os.path.basename(path)[4:-5]
    d = json.load(open(path, encoding="utf-8"))
    for it in d.get("datas", []):
        rows.append(
            dict(
                ind=ind,
                code=it.get("股票代码"),
                name=it.get("股票简称"),
                pe_ttm=it.get("最新市盈率ttm"),
                pe_dyn=it.get("最新动态市盈率"),
                pb=it.get("最新市净率"),
                roe_h1=pick(it, "净资产收益率[") or pick(it, "净资产收益率"),
                mcap=(pick(it, "总市值[") or 0) / 1e8,
                sub=">".join(it.get("所属同花顺行业") or []),
            )
        )

lines = []
cur = None
for r in sorted(rows, key=lambda x: (x["ind"], x["pe_ttm"] or 999)):
    if r["ind"] != cur:
        cur = r["ind"]
        lines.append(f"\n=== {cur} ===")
        lines.append(f"{'代码':<11}{'名称':<8}{'PE-TTM':>7}{'PE动':>7}{'PB':>6}{'ROE-H1':>7}{'市值亿':>8}  二级行业")
    lines.append(
        f"{r['code']:<11}{r['name']:<8}{(r['pe_ttm'] or 0):>7.1f}{(r['pe_dyn'] or 0):>7.1f}"
        f"{(r['pb'] or 0):>6.2f}{(r['roe_h1'] or 0):>7.1f}{r['mcap']:>8.0f}  {r['sub']}"
    )

txt = "\n".join(lines)
with open(os.path.join(OUT, "candidates.txt"), "w", encoding="utf-8") as f:
    f.write(txt)
print(f"rows={len(rows)} -> candidates.txt")
