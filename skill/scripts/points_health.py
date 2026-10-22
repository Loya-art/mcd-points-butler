#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""麦麦积分管家 · 本地确定性计算
账户体检评分与建议分级。输入来自麦当劳 MCP 的 query-my-account /
query-lottery-info 返回数据，计算过程纯本地、可复现，不联网、无第三方依赖。

已对齐官方真实字段（2026-10-22 实测）：
- query-my-account: availablePoint / frozenPoint / accumulativePoint /
  currentMouthExpirePoint(本月将过期) / nextMouthExpirePoint(下月将过期) / expiredPoint
- query-lottery-info: drawPoint(单次消耗积分) / activityStatusText / prizes 等

用法（Agent 会把 MCP 返回的 JSON 存为临时文件后调用）:
    python points_health.py account.json
"""
import json
import sys


def _pick(d, *keys):
    for k in keys:
        if isinstance(d, dict) and d.get(k) is not None:
            return d[k]
    return 0


def _to_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def health_report(account: dict) -> dict:
    """账户体检。account: query-my-account 返回的 data 部分（或整个返回，防御性解析）。"""
    available = _to_int(_pick(account, "availablePoint", "available_points", "balance"))
    frozen = _to_int(_pick(account, "frozenPoint", "frozen_points"))
    # 本月将过期是最紧迫口径；下月将过期单独提示
    expiring = _to_int(_pick(account, "currentMouthExpirePoint", "expiringPoints"))
    expiring_next = _to_int(_pick(account, "nextMouthExpirePoint", 0))
    total = available + frozen

    ratio = expiring / available if available > 0 else 0
    if available == 0:
        level, color = "空仓", "灰"
    elif expiring <= 0:
        level, color = "安全", "绿"
    elif ratio >= 0.3:
        level, color = "高危", "红"
    elif ratio >= 0.1:
        level, color = "注意", "黄"
    else:
        level, color = "安全", "绿"

    advice = {
        "灰": "当前没有可用积分，消费或活动攒分后再来体检。",
        "绿": "积分状态健康，可按需兑换或继续攒分。",
        "黄": "有一批积分临近过期，建议浏览麦麦商城挑选兑换商品。",
        "红": "即将过期积分占比过高，建议本周内通过抽奖消耗或商城兑换处理。",
    }[color]

    return {
        "total": total,
        "available": available,
        "frozen": frozen,
        "expiring_this_month": expiring,
        "expiring_next_month": expiring_next,
        "expiring_ratio": round(ratio, 4),
        "risk_level": level,
        "risk_color": color,
        "advice": advice,
    }


def lottery_value(lottery: dict) -> dict:
    """抽奖性价比评估。lottery: query-lottery-info 返回的 data 部分。"""
    cost = _to_int(_pick(lottery, "drawPoint", "pointsCost", "drawCost"))
    prizes = lottery.get("prizes") or []
    ev = None
    if prizes:
        weights_total = 0.0
        weighted_value = 0.0
        has_prob = all(("probability" in p or "weight" in p) for p in prizes)
        for p in prizes:
            prob = float(p.get("probability") or p.get("weight") or 0)
            value = float(p.get("value") or p.get("worth") or 0)
            weights_total += prob
            weighted_value += prob * value
        if weights_total > 0 and has_prob:
            ev = weighted_value / weights_total
    verdict = None
    if ev is not None:
        verdict = (
            "划算：期望价值高于消耗积分" if ev > cost else
            "持平：期望价值约等于消耗" if ev > cost * 0.8 else
            "不划算：期望价值明显低于消耗，建议直接商城兑换"
        )
    return {
        "activity": lottery.get("activityName"),
        "activity_status": lottery.get("activityStatusText"),
        "draw_cost_points": cost,
        "expected_value": round(ev, 2) if ev is not None else None,
        "verdict": verdict,
        "note": None if ev is not None else "官方未开放概率数据，无法计算期望价值，建议按奖品清单人工判断。",
    }


def mall_rank(products: list, top_n: int = 5) -> list:
    """商城积分/价值比排序。products: mall-points-products 返回的 data 数组。
    排序键：所需积分升序 + 上架状态过滤（status==2 上架）。价值字段官方未开放时按积分排序。"""
    rows = []
    for p in products:
        if _to_int(p.get("status")) != 2:
            continue
        rows.append({
            "name": p.get("spuName"),
            "point": _to_int(p.get("point")),
            "selling": p.get("selling"),
            "spuId": p.get("spuId"),
        })
    rows.sort(key=lambda r: r["point"])
    return rows[:top_n]


if __name__ == "__main__":
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    # 兼容整包返回（取 data）或裸数据
    payload = data.get("data", data) if isinstance(data, dict) else data
    if isinstance(payload, dict):
        if "drawPoint" in payload or "prizes" in payload:
            out = lottery_value(payload)
        else:
            out = health_report(payload)
    elif isinstance(payload, list):
        out = {"top": mall_rank(payload)}
    else:
        out = {"error": "无法识别的输入"}
    print(json.dumps(out, ensure_ascii=False, indent=2))
