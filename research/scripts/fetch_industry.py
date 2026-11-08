"""按行业批量拉取低估候选股（问财 hithink-astock-selector）。"""
import json
import os
import subprocess
import sys
import time

ROOT = "/home/work/workspace01/bmc/xuleihs/study/saa"
CLI = os.path.join(ROOT, ".qoder/skills/hithink-astock-selector/scripts/cli.py")
OUT = os.path.join(ROOT, ".cache/screen")

INDUSTRIES = ["医药生物", "食品饮料", "传媒", "非银金融", "机械设备", "电力设备"]

QUERY = (
    "所属行业为{ind}，市盈率ttm大于0小于40，市净率大于0小于5，"
    "总市值大于100亿，净资产收益率大于5%，按市盈率从小到大排名"
)


def run(ind):
    q = QUERY.format(ind=ind)
    cmd = [sys.executable, CLI, "--query", q, "--limit", "100", "--timeout", "90"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        print(f"[FAIL] {ind} rc={p.returncode} {p.stderr[:200]}")
        return None
    try:
        data = json.loads(p.stdout)
    except json.JSONDecodeError:
        print(f"[FAIL] {ind} json decode, head={p.stdout[:200]}")
        return None
    path = os.path.join(OUT, f"ind_{ind}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"[OK] {ind} code_count={data.get('code_count')} returned={data.get('returned_count')} -> {path}")
    return data


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    summary = {}
    for ind in INDUSTRIES:
        d = run(ind)
        summary[ind] = (d or {}).get("code_count", -1)
        time.sleep(1.5)
    print(json.dumps(summary, ensure_ascii=False))
