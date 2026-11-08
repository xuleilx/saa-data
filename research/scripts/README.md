# research/scripts — 一次性分析脚本登记表

这里只收**一次性、可读可弃**的脚本。还要反复用的逻辑必须进主仓 `saa/` 代码，否则这一层会变成下一个「什么都往里丢」的目录。

- 路径约定：脚本内的输出目录一律用 `Path(__file__).resolve().parents[2] / "<区名>"` 推导，**禁止硬编码本机绝对路径**。
- 最近运行日期为迁移前补录，未记录的写「迁移前未记录」；用到时顺手更新。

| 脚本 | 用途 | 读取/写入数据区 | 最近运行 | 可否重跑 |
|------|------|-----------------|----------|----------|
| `fetch_industry.py` | 按行业批量拉低估候选股（问财 hithink-astock-selector） | 写 `research/screen/ind_*.json` | 迁移前未记录 | 可（需 `IWENCAI_API_KEY`） |
| `fetch_fundamentals.py` | 批量取候选股基本面：3 年利润/营收 CAGR、负债率、股息率、经营现金流 | 读 `research/screen/ind_*.json` | 迁移前未记录 | 可（联网） |
| `fetch_growth.py` / `fetch_growth2.py` | 取最新中报增速，验证「增长为正」与扣非质量（两版迭代） | 写 `research/screen/` | 迁移前未记录 | 可（联网） |
| `summarize.py` | 汇总各行业候选股，输出紧凑表格 | 读 `research/screen/ind_*.json`，写 `research/screen/candidates.txt` | 迁移前未记录 | 可（纯本地） |
| `norm_pe.py` | 正常化 PE：当前市值 ÷ 近 8 年归母净利均值 | 联网取财报 | 迁移前未记录 | 可 |
| `norm_pe_v2.py` | 周期股正常化估值修订版 | 联网取财报 | 迁移前未记录 | 可 |
| `cape_stock.py` | 个股 CAPE（席勒 PE）测算，复用 `saa.market.cape` 的 CPI 口径 | 读主仓 `saa` 包 + 行情 | 迁移前未记录 | 可（需主仓环境） |
| `fetch_em_holdings.py` | 抓取工银前沿医疗(001717) 2016-2021 历史持仓（天天基金） | 写 `research/ttfund/` | 迁移前未记录 | 可（ttskill 登录） |
| `wc_history.py` | 拉白酒龙头历史年度财报（1998-2020） | 写 `research/inquiries/` | 迁移前未记录 | 可（问财） |
| `wc_quarterly.py` | 用 akshare 拉七家白酒龙头季度财报 | 写 `research/inquiries/` | 迁移前未记录 | 可（联网） |
| `parse_wc.py` | 解析问财年度同比增速缓存 | 读 `research/inquiries/wc_*.json` | 迁移前未记录 | 可（纯本地） |
| `mid_autumn_pre_stats.py` | 中秋节前后交易日涨跌幅统计（基准：上证指数） | 联网取指数 | 迁移前未记录 | 可 |
| `mid_autumn_stats.py` | 中秋节后首个交易日涨跌幅统计 | 联网取指数 | 迁移前未记录 | 可 |
| `national_day_stats.py` | 国庆节前后交易日涨跌幅统计 | 联网取指数 | 迁移前未记录 | 可 |
| `build_baijiu_deck.py` | 白酒竞争格局分析 PPTX 生成 | 读 `research/screen/` 等 | 迁移前未记录 | 可（需 python-pptx） |
