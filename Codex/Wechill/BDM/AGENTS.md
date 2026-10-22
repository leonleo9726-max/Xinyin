# AGENTS.md — BDM 1.0

This file provides guidance to Codex when working in this subproject.

## Project Context
- **BDM 1.0** — BD/BDM 薪资计算与公会管理系统。BD 通过绑定公会获取底薪+提成，BDM 管理 BD 团队并叠加团队管理收益。
- 业务规则文档：`rules/BDM业务规则.md`，所有薪资计算、等级匹配、有效期、扣款、审核逻辑以此为准。
- 父目录 `..\AGENTS.md` 的通用规范（Python 执行路径、MCP 配置、输出风格）同样适用于本子目录。

## 核心领域模型

```
公会(Guild) ──绑定──▶ BD ──归属──▶ BDM
                        │              │
                    BD政策          BDM政策
                  (底薪+提成)    (团队管理收益)
```

- **BD**：绑定公会获取底薪（底薪等级表）+ 提成（Bonus流水×比例），考核新增公会数
- **BDM**：双轨制 — 个人BD薪资（本人绑定公会）+ 团队管理薪资（下属BD业绩汇总）
- **薪资流水**来源：公会长公会分成薪资、公会分成TG、自由政策主播手动结算
- **结算口径**：当月数据实时计算；历史月读取结算快照，禁止混用
- **提现**：金币+现金共池，现金仅每月3-7号开放

## 关键业务常量

| 常量 | 默认值 | 来源 |
|------|--------|------|
| 公会有效薪资门槛 | 300$ | 全局配置 |
| BD/BDM 转正门槛 | 1000$ | 全局配置 |
| 兑换汇率 | 11800 | 服务端 |
| 现金提现窗口 | 每月3-7号 | 服务端 |
| 底薪有效时长 | 3自然月 | 政策配置 |
| Bonus有效时长 | 6自然月 | 政策配置 |
| 等级范围 | 1～11级 | 固定 |
| 有效期+15天触发日 | 16日及以后首次绑定 | 固定规则 |

## 结算周期

```
上半月：[1日 00:00:00, 16日 00:00:00)
下半月：[16日 00:00:00, 下月1日 00:00:00)
```

## 薪资验算规范

### 验算流程（三阶段）

**阶段〇：数据质量门禁**（验算前强制）

验算开始前，必须检查 `bd_staff_monthly_salary_issue` 是否存在当前结算月未解决的薪资异常：

```sql
SELECT * FROM bd_staff_monthly_salary_issue
WHERE bd_user_id = ? AND salary_month = ? AND issue_status = 1
```

若存在记录，在结论中以「**异常声明**」单独列出，标记为 **待修正数据**，当前验算结果仅为中间态。

---

**阶段一：公式层验证**（以 BD 自身 guild_salary 为输入）

```
bd_staff 身份 → bd_agency_bind 绑定公会 → bd_realtime_staff_salary + bd_realtime_guild_salary
→ 验证 level/base_salary/commission/deduction 公式一致性
```

- BD: `total_salary = base_salary + bonus_effective_flow × commission_rate`
- BD 扣款: `(base_salary + bonus_share_reward) × deduction_rate`（仅当 new_guild < target 时）
- BDM: 团队 effective_flow = Σ(下属BD effective_flow) + 本人BD effective_flow
- **BDM 无扣款**逻辑（仅 BD 政策适用）
- 等级: `max(上月Bonus有效流水, 本月Bonus有效流水)` → 匹配等级表最高达标 Level，只升不降

**阶段二：Payroll 底层 + BD佣金三层交叉比对**

### 底层公会流水验算（强制）

BD/BDM 薪资验算时，公会底层流水必须走完整 Payroll 计算路径，**不可**用 `app_payer_host_salary_realtime_snapshot.agency_owner_salary` 等单字段简单比对。

### 成员级政策独立（关键规则）

公会成员可拥有与公会默认 `settlement_policy_type` 不同的独立政策。计算公会薪资时**必须**逐成员查询 `app_user_agency_member.settlement_policy_type`，不可直接继承公会级政策。

```sql
SELECT m.user_id, m.role, m.settlement_policy_type AS member_policy,
       a.gain_coin AS historical_gain_coin,
       a.gain_diamond, a.send_gain_diamond
FROM app_user_agency_member m
JOIN app_user_account a ON m.user_id = a.user_id
WHERE m.agency_id = ? AND m.status = 1
```

### Payroll 计算步骤

使用 `skills:calculate-salary` skill（位于 `.agents/skills/calculate-salary/`），按成员各自 policy 选择档位表和 DENOM：
1. 查成员各自 `settlement_policy_type` + 公会 `region` → 确定档位表（双周英语区/双周中东区/自由英语区）
2. 各成员的 `gain_diamond + send_gain_diamond` → 主播薪资（档位 + 超档佣金 + TG）
3. 各成员通过 `app_user_coin_detail` 得到调整后的本期 `period_gain_coin` → 公会长分成（档位 + 超档佣金 + TG）；`historical_gain_coin` 仅作审计，不参与档位判定
4. 公会会长分成总额 = Σ 各成员公会长分成
5. 与 BD 系统 `base_guild_salary_total` / `bonus_guild_salary_total` 比对（**预期有差异**，因手动结算数据未计入）

### BD guild_salary 数据源与口径

BD 系统 `guild_salary_total` = **全口径公会薪资**（agent 侧 + host 侧，档位计算 + 独立结算）。

#### 构成公式

```
guild_salary_total = Snapshot Σ(agency_owner_salary + agency_owner_tg_reward + host_salary + tg_reward)
                   + 独立结算 host 侧（detail_v2 中 settlement_type=1 的 host_salary + host_tg_reward + excess_diamonds_salary）
```

#### 口径说明

| 侧 | Snapshot 覆盖 | 独立结算补充 |
|----|-------------|------------|
| **Agent** | ✅ 档位 + 独立结算 agent 均含 | 无需补充 |
| **Host** | ⚠️ 仅 gain_diamond 档位计算 | detail_v2 type=1 的 host_salary + host_tg_reward + excess_diamonds_salary |

- `app_payer_host_salary_realtime_snapshot` 的 agent 字段已合并档位计算与独立结算 agent 结果。
- snapshot 的 `host_salary` / `tg_reward` 仅反映 gain_diamond 档位计算，**不含**独立结算 host 侧。
- 独立结算 host 侧从 `app_payer_host_salary_detail_v2`（`settlement_type=1`, 当前周期内）取 `host_salary + host_tg_reward + excess_diamonds_salary` 单列汇总补入。

### 双层交叉比对

构建两层验证链路：

```
Snapshot Σ(agency_owner_salary + agency_owner_tg_reward + host_salary + tg_reward)
    + 独立结算 host 侧（detail_v2 type=1: host_salary + host_tg_reward + excess_diamonds_salary）
    ↓ 按公会汇总
BD 公会流水 (bd_realtime_guild_salary.guild_salary_total)
    ↓ 应一致；差异需追查
BD 有效流水 (bd_realtime_staff_salary)
```

1. **Layer 1**: `snapshot` 全字段汇总 + `detail_v2` 独立结算 host 侧 → 预期公会总流水
2. **Layer 2**: `bd_realtime_guild_salary.guild_salary_total` → 与 Layer 1 交叉比对，应一致

---

## 数据库 Schema
详见 `rules/数据库表结构.md`。查询前先 `SHOW COLUMNS FROM <表名>`。
