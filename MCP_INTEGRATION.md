# MCP_INTEGRATION · 麦当劳 MCP 集成说明

## 使用的 MCP Server

- **McDonald's China MCP Server**（`https://mcp.mcd.cn`，Streamable HTTP，Bearer Token 鉴权）
- 官方仓库：[M-China/mcd-mcp-server](https://github.com/M-China/mcd-mcp-server)
- Token 申请：[open.mcd.cn/mcp](https://open.mcd.cn/mcp)

## 工具清单与调用流程

### 场景 A：账户体检

```
now-time-info → query-my-account → points_health.py(health_report)
```

1. `now-time-info`：获取当前日期，作为过期判断的时间基准
2. `query-my-account`：拉取可用 / 累计 / 冻结 / 即将过期积分
3. 本地脚本计算"即将过期占比"，输出红/黄/绿风险等级与建议（确定性，可复现）

### 场景 B：过期抢救

```
available-coupons → auto-bind-coupons（需确认） → query-my-coupons
```

先列出可领优惠券，经用户确认后一键领券，作为"兑换/抽奖"之外的第三条抢救路径。

### 场景 C：抽奖性价比评估

```
query-lottery-info → points_health.py(lottery_value) → draw-lottery（需确认） → query-my-prizes
```

1. `query-lottery-info`：取活动状态、奖品列表、抽奖消耗
2. 本地脚本按官方概率/数量分布计算**期望价值**，对比消耗积分给出"划算/持平/不划算"结论
3. `draw-lottery` 属消耗型操作，仅在用户明确确认后执行
4. `query-my-prizes`：中奖记录回查

### 场景 D：商城最优兑换

```
mall-points-products → mall-product-detail → 按积分/价值比本地排序 → mall-create-order（需确认） → mall-order-list / mall-order-detail
```

1. 拉取商城商品列表，逐个取详情（注意 600 次/分钟限流，分批调用）
2. 本地按"商品价值 ÷ 所需积分"排序输出 Top N 推荐
3. 下单前向用户展示商品、积分、订单摘要，确认后 `mall-create-order`，返回订单号与券码

## 业务价值

| 痛点 | 对应能力 | 价值 |
|---|---|---|
| 积分默默过期 | 账户体检 + 过期预警 | 把"沉睡资产"变成明确行动清单 |
| 抽奖值不值靠猜 | 期望价值确定性计算 | 用数字代替直觉，防冲动消费 |
| 商城商品太多不会选 | 积分/价值比排序 | 一眼看到最划算的兑换 |
| 操作繁琐 | 对话式托管 + 确认制 | 查询免确认，花钱必确认 |

## 限流与安全

- 官方限流 600 次/分钟（429），Skill 内置分批与退避策略
- Token 通过环境变量注入，仓库内配置仅含占位符，绝不提交真实凭证
