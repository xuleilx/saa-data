#!/usr/bin/env python3
"""抓取工银前沿医疗(001717) 2016-2021 年历史持仓（天天基金 F10 / 东财接口）。
接口: https://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc
注意: 必须携带 User-Agent，否则返回 404。"""
import json
import re
import sys
from io import StringIO

import pandas as pd
import requests
from bs4 import BeautifulSoup

CODE = "001717"
URL = "https://fundf10.eastmoney.com/FundArchivesDatas.aspx"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Referer": f"https://fundf10.eastmoney.com/ccmx_{CODE}.html",
}


def parse_year(year: str) -> list[dict]:
    params = {"type": "jjcc", "code": CODE, "topline": "10000",
              "year": year, "month": "", "rt": "0.9"}
    r = requests.get(URL, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    text = r.text
    # 返回形如 var apidata={ content:"...",arryear:[...]}; 提取 content
    start = text.find("content:")
    if start == -1:
        return []
    content_start = text.find('"', start) + 1
    # content 是以转义双引号包装的 HTML，结束位置为 \",arryear
    end = text.find('",arryear', content_start)
    content_html = text[content_start:end].replace('\\"', '"')
    soup = BeautifulSoup(content_html, "lxml")
    records = []
    for box in soup.find_all("div", class_="boxitem"):
        h4 = box.find("h4")
        table = box.find("table")
        if h4 is None or table is None:
            continue
        title = h4.get_text(" ", strip=True)
        m = re.search(r"(\d{4})年(\d)季度", title)
        if not m:
            continue
        q_year, q_no = m.group(1), m.group(2)
        dm = re.search(r"(\d{4}-\d{2}-\d{2})", title)
        report_date = dm.group(1) if dm else None
        df = pd.read_html(StringIO(str(table)), converters={"股票代码": str})[0]
        df.columns = [str(c).replace(" ", "").replace("\xa0", "") for c in df.columns]
        for _, row in df.iterrows():
            records.append({
                "year": q_year,
                "quarter": f"{q_year}Q{q_no}",
                "report_date": report_date,
                "rank": int(row.get("序号", 0)),
                "code": str(row.get("股票代码", "")).zfill(6),
                "name": str(row.get("股票名称", "")),
                "ratio": str(row.get("占净值比例", "")).replace("%", ""),
                "shares_wan": str(row.get("持股数（万股）", row.get("持股数(万股)", ""))),
                "value_wan": str(row.get("持仓市值（万元）", row.get("持仓市值(万元)", ""))),
            })
    return records


def main() -> None:
    years = sys.argv[1:] or [str(y) for y in range(2016, 2022)]
    all_records = []
    for y in years:
        try:
            recs = parse_year(y)
            print(f"{y}: {len(recs)} 条")
            all_records.extend(recs)
        except Exception as e:  # noqa: BLE001
            print(f"{y}: 失败 {e}")
    out = f".cache/ttfund/em_holding_{years[0]}_{years[-1]}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=1)
    print("saved:", out, "| 总记录:", len(all_records))
    # 快速预览
    qs = sorted({r["report_date"] for r in all_records if r["report_date"]})
    print("覆盖报告期:", qs)


if __name__ == "__main__":
    main()
