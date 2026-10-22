# 示例数据目录

让任何人不申请 MCP Token、不连麦当劳账户，也能一键体验麦麦积分管家的完整计算链路。

## 文件说明

| 文件 | 场景 | 对应入口 |
|---|---|---|
| `account-empty.json` | 空仓（0 积分新户） | 从零开始 |
| `account-safe.json` | 健康账户（无过期压力） | 健康账户 |
| `account-danger.json` | 高危（本月 1100 分即将过期） | 过期预警 |
| `lottery-active.json` | 进行中的抽奖活动（含官方概率示例） | 抽奖评估 |

## 一键运行

```bash
# 账户体检（对齐 query-my-account 真实字段）
python skill/scripts/points_health.py examples/account-danger.json

# 抽奖期望价值（对齐 query-lottery-info 真实字段）
python skill/scripts/points_health.py examples/lottery-active.json
```

预期输出（account-danger）：

```json
{
  "risk_level": "高危",
  "risk_color": "红",
  "expiring_this_month": 1100,
  ...
}
```

> 字段说明：以上 JSON 结构与麦当劳 MCP Server `query-my-account` /
> `query-lottery-info` 工具的真实返回字段一致（availablePoint /
> currentMouthExpirePoint / drawPoint 等），由真机联调校验。所有数据均为
> 脱敏示例，不含任何真实账户信息。
