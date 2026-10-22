---
name: guild-salary-query
description: 查询 Top 测试环境或显式授权的生产只读库中指定公会或用户的本月薪资，按月结/周结展示成员或用户工资明细，并隔离合并两类数据；适用于公会薪资、用户薪资、成员分类和本月公会总薪资查询，不用于资金变更。
---

# 公会薪资查询

该技能用于把公会或用户薪资查询收敛为一次只读数据库连接和一次汇总输出，避免反复手工查表、重算工资或漏掉周结成员。

## 执行前

- 工作目录保持在 `E:\Codex\Top\Guild` 或其子目录；不得读取 `Wechill`。
- 完整读取 `Guild\AGENTS.md` 和 `Guild\核心业务规则.md`。若规则与本技能冲突，以项目规则为准。
- 默认使用 `.env` 中 `APP_ENV=test` 的测试库；用户未指定月份时使用当前自然月（当前日期按运行环境）。
- 生产查询必须显式传入 `--environment production --confirm-production`，使用独立的 `PROD_MYSQL_*` 凭据，并要求 `PROD_MYSQL_READ_ONLY=true`；脚本会设置只读事务。缺少任一条件时拒绝连接。
- 用户输入纯数字公会编号按 `guild.guild_info.guild_no` 查询，不按主键 `id` 查询。

## 查询流程

优先执行 `scripts/query_guild_salary.py`，传入公会编号或用户号和可选月份；`--guild-no` 与 `--user-no` 必须二选一：

```powershell
& 'E:\python\work\.venv\Scripts\python.exe' '<skill-dir>\scripts\query_guild_salary.py' --guild-no 1027 --month 2026-09

& 'E:\python\work\.venv\Scripts\python.exe' '<skill-dir>\scripts\query_guild_salary.py' --user-no 4279602 --month 2026-09

& 'E:\python\work\.venv\Scripts\python.exe' '<skill-dir>\scripts\query_guild_salary.py' --guild-no 1027 --month 2026-09 --environment production --confirm-production
```

脚本在同一 MySQL 连接内完成：

1. 对公会、成员、用户、月结明细/账单、周结明细/账单执行 `SHOW COLUMNS`，再查询数据。
2. 公会范围通过 `guild_no` 解析 `guild_id`，读取全部成员，不只读取有工资行的成员；用户范围先通过 `ln_user.user_no` 解析 `user_id`，再定位唯一有效成员关系及所属公会。
3. 月结只读 `guild_salary_detail` / `guild_settlement_bill` 的 `policy_type IN (1,2)` 和目标月份。
4. 周结只读 `guild_salary_detail_weekly` / `guild_settlement_bill_weekly` 的 `policy_type=3`，按 `period_start` 的 UTC+3 自然周起点筛选落在目标自然月的周；周结自由政策使用独立参数 `0.8 / 130000 / 0.73 / 0.27 / 0.2`（总分成比 / 钻石换算美元比例 / 主播分成比 / 公会长分成比 / 强制充值比例），月结自由政策继续使用 `1.1 / 150000 / 0.8 / 0.2 / 0.2`。
5. 已有关联账单时标记 `settled_snapshot` 或 `unconfirmed_settlement_bill`；`settlement_bill_id=0` 标记 `realtime`。不得把实时行称为已结算。来源状态必须保留在每条工资明细上；同一成员存在多个周期或来源时分别输出，不能合并成一个成员级来源状态。
6. 主播总薪资使用主播侧 `non_coin_reward_amount + coin_reward_amount`；公会长管理收益只汇总 `bill_owner_type=2 AND member_id<>0`，并使用 `total_salary_amount + guild_coin_reward_amount`，不得把 `member_id=0` 汇总行重复计入。
7. 公会范围按全部有效成员当前 `policy_type` 分类：`1/2` 写入 `monthly_members`，`3` 写入 `weekly_members`；用户范围只输出目标用户的有效成员关系和对应工资明细。分类不依赖工资明细是否存在。
8. 公会汇总按周期生成 `period_totals.monthly` 和 `period_totals.weekly`，每组分别输出主播薪资、公会长管理收益和公会薪资。月结沿用原口径；周结明细完整输出，但 `settled_snapshot` 仅作明细与审计展示，不得计入 `period_totals.weekly` 或 `totals`。未结算周结行才参与周结和本月公会薪资汇总。

自由政策计算口径：月结主播工资基数为 `D_balance * 1.1 / 150000 * 0.8`，月结公会长管理收益基数为 `D_flow * 1.1 / 150000 * 0.2`；周结主播工资基数为 `D_balance * 0.8 / 130000 * 0.73`，周结公会长管理收益基数为 `D_flow * 0.8 / 130000 * 0.27`。月结沿用其既有金币/非金币拆分；自由政策周结工资项拆分为金币工资 `0%`、非金币工资 `100%`，周结不得沿用月结参数。

## 输出要求

对外使用简体中文，先给结论，再给成员表和异常声明。成员表必须覆盖所有有效成员；没有工资行的周结成员也要列出并标记“暂无周结明细”，不能省略或擅自解释为已确认收入为 0。

至少输出：

- 数据环境、统计月份、公会名称和查询口径（客户端/后台）；用户范围额外展示目标用户号。
- 公会范围先展示“月结成员”组，再展示“周结成员”组，两组覆盖全部有效成员；用户范围仅展示目标用户。每名成员展示用户号、角色、政策类型、月结工资、可计入汇总的未结算周结工资和总薪资；已结算周结金额仅在工资明细逐行展示。来源状态必须回到工资明细逐行展示；同一成员的历史结算快照、当前实时行或未确认账单分别列出周期、来源和结算状态，不得在成员表拼接成“历史快照+当前实时”等合并状态。
- 每名成员同时展示当前可提现余额（含金币）及余额池明细。余额读取 `guild.guild_balance_pool.available_amount`，仅纳入启用余额池，冻结金额不计入；可提现余额与周期工资独立。没有余额池记录时标记“暂无余额池记录”，不得直接解释为已确认收入为 0。
- 公会长兼主播按其主播政策进入对应分组；若没有工资行，保留成员并标记“暂无工资明细”。
- 对每条主播工资明细展示周期、有效钻石流水/余额、非金币工资、金币工资、总薪资、预支抵扣、薪资余额和实时/结算来源；月结与周结明细分开呈现。
- 每条月结/周结主播明细还要展示对应公会长管理收益、主播底薪和主播 TG 薪资；`policy_type=1` 展示实际底薪/TG，`policy_type=2/3` 展示 `--`。
- 主播总薪资、公会长管理收益、公会总薪资。公会长本人兼主播时，主播工资和管理收益分开计算。
- 先展示月结汇总和周结汇总，再展示本月合计；周结汇总和本月合计排除 `settled_snapshot`，但周结明细仍逐条展示该来源；不能只输出混合后的公会总薪资。
- 「异常声明」：无明细周结成员、重复快照、空值/非法金额、未结算实时行、月结与周结混读风险等。

不得对自由政策补造普通政策底薪/TG 分项；客户端口径下自由政策分项显示 `--`。不得展示 `member_id`，该字段仅用于内部关联和去重。

## 生产查询边界

- 生产模式仅允许读取结构、成员和薪资数据；脚本内置 SQL 全部为 `SHOW COLUMNS` 或 `SELECT`，并在生产连接上设置只读事务。
- 生产结果必须保留 `environment=production` 和 `read_only=true` 标记；不得将生产结果表述为测试数据。
- 生产库的提现、预支、结算、余额或其他写操作仍不适用此技能。

## 何时不用此技能

提现/预支/结算变更、日志排障等任务不适用本技能；应先确认对应专用流程和授权。
