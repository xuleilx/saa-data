"""批量取候选股基本面：3年利润/营收CAGR、负债率、股息率、经营现金流。"""
import json
import os
import subprocess
import sys
import time

ROOT = "/home/work/workspace01/bmc/xuleihs/study/saa"
CLI = os.path.join(ROOT, ".qoder/skills/hithink-finance-query/scripts/cli.py")
OUT = os.path.join(ROOT, ".cache/screen")

BATCHES = {
    "media": ["吉比特", "三七互娱", "恺英网络", "中南传媒", "凤凰传媒"],
    "pharma": ["华润三九", "华东医药", "丽珠集团", "恩华药业", "鱼跃医疗", "华润双鹤"],
    "food": ["伊利股份", "青岛啤酒", "双汇发展", "安琪酵母", "山西汾酒"],
    "fin": ["中国平安", "中国太保", "华泰证券", "国泰海通", "江苏金租"],
    "mach": ["徐工机械", "三一重工", "柳工", "杭叉集团", "豪迈科技", "中创智领"],
    "power": ["阳光电源", "宁德时代", "正泰电器", "宏发股份"],
}

FIELDS = "近三年净利润复合增长率 近三年营业收入复合增长率 资产负债率 股息率 经营活动产生的现金流量净额"


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
    path = os.path.join(OUT, f"fund_{key}.json")
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[OK] {key} n={data.get('code_count')} -> {path}")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for k, v in BATCHES.items():
        run(k, v)
        time.sleep(1.5)
