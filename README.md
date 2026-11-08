# saa-data

SAA 项目的**版本化数据仓**，作为 git submodule 挂载到主仓 `saa-data/`。跨机能读、删了就没、或重抓代价高的东西放这里。

## 1. 本仓是什么 / 不是什么

- **是**：原始行情与估值序列、CAPE 原始序列、研究留痕（筛选快照、机构快照、问财原始返回）。
- **不是**：不是代码仓（代码在主仓 `saa/`）；**不放可丢弃缓存**（那类东西在主仓 `data/cache/`）；不是派生库（`data/market.db` 在主仓，可用 `saa storage backfill` 从本仓 CSV 重建）。

## 2. 顶层四分区契约

| 目录 | 内容 | 写入方 | 可否删除 |
|------|------|--------|----------|
| `market/` | 指数/行业/温度行情与估值 CSV（`cs_*`、`sw_pb_*`、`legu_*`、`daily_*`） | 主仓 fetchers（`saa market temperature` 等） | 禁止 |
| `pe-percentile/` | 个股 PE 序列 CSV | `saa market pe` / `saa storage sync-pe` | 禁止 |
| `cape/raw/` | CAPE 原始序列（cpi、指数点位等） | `saa market cape` | 禁止 |
| `research/` | 研究留痕（见第 3 节） | 人工 + `research/scripts/` 一次性脚本 | 禁止 |

**新增顶层目录前必须先改这张表并通知主仓同步契约测试** —— 顶层锁死这四个，避免退回「什么都往里堆」的状态。

## 3. `research/` 四个子区

| 子区 | 内容 |
|------|------|
| `research/screen/` | 选股筛选快照（`ind_*.json`、`v2_*.json`、`*.csv`、`candidates.txt`） |
| `research/ttfund/` | 天天基金快照（持仓、规模、统计 md/json 与 `outputs/` 导出） |
| `research/inquiries/` | 问财原始返回（`wc_*.json`、`wc_hist_out.txt`） |
| `research/scripts/` | 一次性分析脚本 + 登记表（见 `research/scripts/README.md`） |

## 4. 新文件该放哪（三问决策树）

1. **换台机器还想读到？** → 放本仓对应分区（`market/`、`pe-percentile/`、`cape/raw/`、`research/`）。
2. **丢了能重新抓/重算？** → 放主仓 `data/cache/<signal>/`，不要进本仓。
3. **只是一次性脚本或过程产物？** → 主仓 `data/scratch/`；若结论值得留痕，产出的快照放 `research/`，脚本放 `research/scripts/` 并在登记表加一行。

## 5. 同步与查看

```bash
# 主仓内：把本仓变更提交并推送，同时 bump 主仓 submodule 指针
bash scripts/data-repo-push.sh

# 查看本仓最近提交 / 工作区状态
git -C saa-data log --oneline -5
git -C saa-data status --porcelain

# 换机或新克隆
git submodule sync --recursive && git submodule update --init --recursive
```

`git submodule` 首次校验：`git -C saa-data ls-files | wc -l` 应为 247（迁移基线）。

## 6. 变更记录

| 日期 | 变更 |
|------|------|
| 2026-11-08 | 布局重构：submodule 挂载点由 `.cache` 改为 `saa-data`；`screen/`、`ttfund/`、`wc_*` 与 16 个一次性脚本归入 `research/{screen,ttfund,inquiries,scripts}`；`.gitignore` 从 11 条本地缓存黑名单缩为 3 条；新增 `.gitattributes` 强制 CSV/JSON 使用 LF；修正 `summarize.py` 的硬编码绝对路径。设计见主仓 `docs/superpowers/specs/2026-11-08-data-layout-migration-design.md` |
