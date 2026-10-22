# 麦麦积分管家 MCD Points Butler

> 麦当劳积分一站式管家——**让每一分麦麦积分都不白白过期。**
> 基于麦当劳官方 MCP 能力开发 · 麦当劳程序员创意开发大赛参赛作品

## 这是什么

麦当劳 App 的积分体系很散：余额分"可用/冻结/即将过期"几个口径，抽奖性价比要自己心算，麦麦商城几百个兑换商品不知道哪个最值。大多数人攒了几千分，最后默默过期。

**麦麦积分管家**把它变成一句对话：

| 你说 | 它做 |
|---|---|
| 「我的积分怎么样？」 | 账户体检报告：余额 / 冻结 / 即将过期明细 + 红黄绿风险等级 |
| 「积分要过期了怎么办？」 | 过期预警 + 抢救方案（抽奖消耗 / 商城兑换 / 领券抵扣） |
| 「抽奖划算吗？」 | 抽奖性价比评估：期望价值 vs 消耗积分，附奖品清单 |
| 「积分换点什么好？」 | 商城最优兑换推荐：按积分/价值比排序，确认后可代下单 |

## 在线演示

👉 **https://loya-art.github.io/mcd-points-butler/**

不用安装、不用 Token，打开就能改数字看实时体检结果。纯前端本地计算，数据不上传。

## 快速体验（无需 Token）

```bash
# 账户体检（示例数据）
python skill/scripts/points_health.py examples/account-danger.json

# 抽奖蒙特卡洛模拟（10 万次抽样，输出期望值/ROI/中奖分布）
python skill/scripts/lottery_sim.py examples/lottery-active.json

# 单元测试（14 项，覆盖空仓/过期超额/异常字段等边界）
python tests/test_points_health.py
```

## 设计原则

1. **取数交给 MCP，算术交给代码，表达交给 Agent**——账户数据全部来自麦当劳官方 MCP 工具；风险等级、期望价值等由本地确定性脚本计算，结果可复现、可核验，不靠大模型"感觉"。
2. **只读优先，写操作必须确认**——所有查询直接执行；抽奖（消耗积分）、商城兑换（扣积分下单）必须先展示方案并获用户明确确认。
3. **诚实报价**——展示价与所需积分不一致时如实标注，宁少报不多报。

## 目标用户

- 有麦当劳会员账户、攒了积分但从不打理的"积分沉睡用户"
- 想在过期前把积分花在刀刃上的精打细算党
- 需要帮家人朋友管理多个积分账户的"家庭积分管理员"

## 安装

1. **申请 MCP Token**：打开 [open.mcd.cn/mcp](https://open.mcd.cn/mcp)，手机号登录后在控制台激活领取（免费）。
2. **配置 MCP Server**：将本仓库根目录的 `mcp-config.example.json` 内容加入你的 MCP Client，把 `${MCD_MCP_TOKEN}` 替换为你的 Token（或设置同名环境变量）：

```json
{
  "mcpServers": {
    "mcd-mcp": {
      "type": "streamablehttp",
      "url": "https://mcp.mcd.cn",
      "headers": { "Authorization": "Bearer ${MCD_MCP_TOKEN}" }
    }
  }
}
```

3. **安装 Skill**：将 `skill/` 目录作为技能包装入你的 Agent 平台（WorkBuddy / Cherry Studio / Cursor 等）。

## 使用示例

```text
用户：我的麦麦积分怎么样？
管家：📊 账户体检报告
      余额 2,340 分（可用 2,140 / 冻结 200）
      ⚠️ 620 分将于 10-31 过期，占比 29%，风险等级：红
      建议动作：本周内抽奖消耗约 200 分 + 商城兑换一个 400 分档商品
      进阶玩法：麦麦省今日有 3 张可领优惠券，叠加下单更省
```

## 技术结构

```
├── README.md                  # 本文件
├── CONTEST_DECLARATION.md     # 参赛声明（官方原文）
├── MCP_INTEGRATION.md         # MCP 集成说明
├── mcp-config.example.json    # 脱敏 MCP 配置示例
├── workbuddy.md               # WorkBuddy 开发对话存档
└── skill/
    ├── SKILL.md               # 技能定义（Agent 读取）
    └── scripts/
        └── points_health.py   # 本地确定性计算（账户体检 / 抽奖期望价值）
```

## License

MIT
