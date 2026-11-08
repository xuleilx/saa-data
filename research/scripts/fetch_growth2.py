"""获取最新中报增速，验证增长与扣非质量。"""
import json
import os
import subprocess
import sys
import time

ROOT = "/home/work/workspace01/bmc/xuleihs/study/saa"
CLI = os.path.join(ROOT, ".qoder/skills/hithink-finance-query/scripts/cli.py")
OUT = os.path.join(ROOT, ".cache/screen")

BATCHES = {
    "growth1": ["吉比特", "三七互娱", "华润三九", "华东医药", "伊利股份", "中国平安"],
    "growth2": ["中创智领", "徐工机械", "柳工", "阳光电源", "宁德时代", "正泰电器"],
}

FIELDS = "2026年中报归母净利润同比增长率 2026年中报扣非净利润同比增长率 2026年中报营业收入同比增长率"


def run(key, names):
    q = " ".join(names) + " " + FIELDS
    cmd = [sys.executable, CLI, "--query", q, "--limit", "20", "--timeout", "90"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        print(f"[FAIL] {key} rc={p.returncode} {p.stderr[:200]}")
        return
    try:
        data = json.loads(p.stdout)
    except json.JSONDecodeError:
        print(f"[FAIL] {key} decode {p.stdout[:200]}")
        return
    json.dump(data, open(os.path.join(OUT, f"g_{key}.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"[OK] {key} n={data.get('code_count')} chunks={data.get('chunks_info')}")


if __name__ == "__main__":
    for k, v in BATCHES.items():
        run(k, v)
        time.sleep(1.5)
