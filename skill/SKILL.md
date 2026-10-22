---
name: mcd-points-butler
title: 麦麦积分管家
description: 麦当劳积分一站式管家——积分账户体检、到期预警、抽奖性价比评估、麦麦商城最优兑换建议。基于麦当劳官方 MCP 能力开发，麦当劳程序员创意开发大赛参赛作品。
---

# 麦麦积分管家（MCD Points Butler）

一句话：**让每一分麦麦积分都不白白过期。**

## 解决什么问题

麦当劳 App 里的积分体系很散：积分余额分散在"可用/冻结/即将过期"几个口径里，抽奖活动性价比要自己心算，麦麦商城里几百个兑换商品不知道哪个最值。大多数人攒了几千分，最后默默过期。

本 Skill 把这件事变成一句对话：

- **「我的积分怎么样？」** → 账户体检报告（余额 / 冻结 / 即将过期明细 + 风险等级）
- **「积分要过期了怎么办？」** → 过期预警 + 抢救方案（抽奖用掉 / 商城兑换 / 领券抵扣）
- **「抽奖划算吗？」** → 抽奖性价比评估（期望价值 vs 抽奖消耗，附奖品清单）
- **「积分换点什么好？」** → 商城最优兑换推荐（按积分/价值比排序，可代下单）

## 设计原则

1. **取数交给 MCP，算术交给代码，表达交给 Agent**——所有账户数据来自麦当劳官方 MCP 工具，积分价值比、期望价值等计算由本地确定性脚本完成，不靠大模型"感觉"。
2. **只读优先，写操作必须确认**——查询类工具直接调用；`draw-lottery`（消耗积分）、`mall-create-order`（扣积分下单）必须先向用户展示方案并获明确确认。
3. **诚实报价**——商城展示价与所需积分不一致时如实标注，宁少报不多报。

## 依赖的 MCP Tools

| 场景 | Tools |
|---|---|
| 时间基准 | `now-time-info` |
| 账户体检 | `query-my-account` |
| 抽奖评估 | `query-lottery-info` → 本地计算 → `draw-lottery`（需确认） → `query-my-prizes` |
| 商城兑换 | `mall-points-products` → `mall-product-detail` → `mall-create-order`（需确认） → `mall-order-list` / `mall-order-detail` |
| 过期抢救 | `available-coupons` / `auto-bind-coupons` / `query-my-coupons` |

## 使用前提

1. 按 [README.md](../README.md) 配置麦当劳 MCP Server（需要 MCP Token）
2. 将本目录（`skill/`）作为技能包安装到你的 MCP Client / Agent 平台

## 输出格式约定

账户体检报告固定输出四段：**余额概览 → 过期风险（红/黄/绿） → 本周建议动作 → 可选进阶玩法**。风险等级由本地脚本 `scripts/points_health.py` 依据"即将过期积分占比"计算，不凭语感。
