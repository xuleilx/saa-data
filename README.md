# saa-data

SAA 行情 CSV 缓存（ submodule 挂载到主仓库 `.cache/`）。

| 路径 | 说明 |
|------|------|
| `market/` | 指数/行业温度缓存（`.cache/market`） |
| `pe-percentile/` | 个股 PE 序列缓存（可选） |

主仓库 `data/market.db` 不纳入本仓；换机后 `saa storage init && saa storage backfill` 本地重建。

同步：在主仓库运行 `bash scripts/data-repo-push.sh`。
