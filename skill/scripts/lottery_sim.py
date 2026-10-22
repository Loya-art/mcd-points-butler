#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""麦麦积分管家 · 抽奖蒙特卡洛模拟
用大样本模拟代替单点期望，输出中奖分布与置信区间，供"抽奖评估"入口使用。

输入：query-lottery-info 返回的 JSON（含 prizes[].value / weight 与 drawPoint）
运行：python skill/scripts/lottery_sim.py examples/lottery-active.json [N]
"""
import json
import random
import sys

N_DEFAULT = 100_000


def simulate(lottery: dict, n: int = N_DEFAULT) -> dict:
    cost = float(lottery.get("drawPoint") or 0)
    prizes = lottery.get("prizes") or []
    if not prizes:
        return {"error": "无奖品数据，无法模拟"}

    weights = [float(p.get("weight") or 0) for p in prizes]
    values = [float(p.get("value") or 0) for p in prizes]
    names = [p.get("name") or "?" for p in prizes]
    total_w = sum(weights)
    if total_w <= 0:
        return {"error": "奖品权重全为 0，无法模拟"}

    rng = random.Random(1024)  # 固定种子，结果可复现
    totals, hit_counts = [], {name: 0 for name in names}
    cum = []
    acc = 0.0
    for w in weights:
        acc += w
        cum.append(acc)

    for _ in range(n):
        draw = rng.random() * total_w
        for i, c in enumerate(cum):
            if draw < c:
                totals.append(values[i])
                hit_counts[names[i]] += 1
                break

    totals.sort()
    mean = sum(totals) / n
    p5, p50, p95 = totals[int(n * .05)], totals[int(n * .50)], totals[int(n * .95)]
    win_rate = sum(1 for t in totals if t > 0) / n

    return {
        "draws": n,
        "draw_cost_points": cost,
        "expected_value": round(mean, 2),
        "roi": round(mean / cost, 2) if cost > 0 else None,
        "win_rate": f"{win_rate:.1%}",
        "p5": p5, "p50": p50, "p95": p95,
        "distribution": {k: f"{v / n:.1%}" for k, v in hit_counts.items()},
        "verdict": (
            "划算：期望回报高于消耗积分" if mean > cost else
            "持平：期望回报接近消耗" if mean > cost * 0.8 else
            "不划算：期望回报明显低于消耗，建议直接商城兑换"
        ) if cost > 0 else None,
    }


if __name__ == "__main__":
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    payload = data.get("data", data) if isinstance(data, dict) else data
    n = int(sys.argv[2]) if len(sys.argv) > 2 else N_DEFAULT
    print(json.dumps(simulate(payload, n), ensure_ascii=False, indent=2))
