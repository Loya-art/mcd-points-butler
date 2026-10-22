#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""麦麦积分管家 · 本地确定性计算
账户体检评分与建议分级。输入来自麦当劳 MCP 的 query-my-account 返回数据，
计算过程纯本地、可复现，不联网、无第三方依赖。

用法（Agent 会把 MCP 返回的 JSON 存为临时文件后调用）:
    python points_health.py account.json
"""
import json
import sys


def health_report(account: dict) -> dict:
    """account: query-my-account 工具的返回 JSON（字段名做防御性解析）。"""
    def pick(d, *keys):
        for k in keys:
            if isinstance(d, dict) and k in d and d[k] is not None:
                return d[k]
        return 0

    available = int(pick(account, "availablePoints", "available_points", "balance"))
    frozen = int(pick(account, "frozenPoints", "frozen_points"))
    expiring = int(pick(account, "expiringPoints", "expiring_points", "soonExpirePoints"))
    total = available + frozen

    # 风险等级：即将过期积分占可用积分比例
    ratio = expiring / available if available > 0 else 0
    if expiring <= 0:
        level, color = "安全", "绿"
    elif ratio >= 0.3:
        level, color = "高危", "红"
    elif ratio >= 0.1:
        level, color = "注意", "黄"
    else:
        level, color = "安全", "绿"

    if color == "红":
        advice = "即将过期积分占比过高，建议本周内通过抽奖消耗或商城兑换处理。"
    elif color == "黄":
        advice = "有一批积分临近过期，建议浏览麦麦商城挑选兑换商品。"
    else:
        advice = "积分状态健康，可按需兑换或继续攒分。"

    return {
        "total": total,
        "available": available,
        "frozen": frozen,
        "expiring": expiring,
        "expiring_ratio": round(ratio, 4),
        "risk_level": level,
        "risk_color": color,
        "advice": advice,
    }


def lottery_value(lottery: dict) -> dict:
    """抽奖性价比评估。lottery: query-lottery-info 返回 JSON。
    若官方返回了奖品及概率/数量分布，按期望价值计算；否则输出缺口提示。"""
    cost = lottery.get("pointsCost") or lottery.get("drawCost") or 0
    prizes = lottery.get("prizes") or []
    ev = None
    if prizes:
        weights_total = 0
        weighted_value = 0.0
        has_prob = all(("probability" in p or "weight" in p) for p in prizes)
        for p in prizes:
            prob = float(p.get("probability") or p.get("weight") or 0)
            value = float(p.get("value") or p.get("worth") or 0)
            weights_total += prob
            weighted_value += prob * value
        if weights_total > 0 and has_prob:
            ev = weighted_value / weights_total
    return {
        "draw_cost_points": cost,
        "expected_value": round(ev, 2) if ev is not None else None,
        "verdict": None if ev is None else (
            "划算：期望价值高于消耗积分" if ev > cost else
            "持平：期望价值约等于消耗" if ev > cost * 0.8 else
            "不划算：期望价值明显低于消耗，建议直接商城兑换"
        ),
        "note": None if ev is not None else "官方未开放概率数据，无法计算期望价值，建议按奖品清单人工判断。",
    }


if __name__ == "__main__":
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    if "expiring" in data or "expiringPoints" in data or "balance" in data:
        print(json.dumps(health_report(data), ensure_ascii=False, indent=2))
    else:
        print(json.dumps(lottery_value(data), ensure_ascii=False, indent=2))
