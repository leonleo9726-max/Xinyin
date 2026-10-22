# 核心业务规则

## 1. 口径与周期

| Rule Name | Trigger Condition | Formula | Threshold Values | Applicable Policy |
|---|---|---|---|---|
| 半月周期 | Payroll 薪资与 BD 当前周期流水 | 上半月 `[1日 00:00, 16日 00:00)`；下半月 `[16日 00:00, 下月1日 00:00)` | 每月 1 日、16 日 | 双周结算及 BD 实时统计；master 实现 |
| 自然月周期 | BD/BDM 底薪、Bonus、月结 | 仅累计目标自然月内且位于各自有效区间的流水；历史月读取月结快照，当前月读取实时数据 | 自然月 | BD/BDM；master 实现 |
| 金额精度 | 计算薪资、比例及汇总 | `BigDecimal` 保留两位小数，主要计算采用 `RoundingMode.DOWN`；不要将分和美元直接相加 | 两位小数 | Payroll、BDM；master 实现 |
| 政策与区域 | 查档前 | 按成员 `settlement_policy_type` 和区域查 `app_payer_salary_v2_config`；同一公会成员政策可不同 | 政策 `1` 双周、`2` 自由；区域 `0` 英语、`2` 中东 | Payroll；master 实现 |

## 2. Payroll：成员薪资与公会分成

### 2.1 输入和查档

| Rule Name | Trigger Condition | Formula | Threshold Values | Applicable Policy |
|---|---|---|---|---|
| 主播档位与超档 | 当前周期实时计算或发起结算 | `host_diamonds = gain_diamond + send_gain_diamond`；取 `diamonds <= host_diamonds` 的最高档；低于首档按 0 档、全量超档 | 档位以配置表为准 | 双周、自由；master 实现 |
| 公会长档位与超档 | 计算成员对应的公会长分成 | **按钻石流水 `flow_diamonds` 独立查档**，不是按 `gain_coin`；低于首档按 0 档 | 档位以配置表为准 | 双周、自由；master 实现；与原 Payroll §3.1-3.2 冲突 |
| 实时累计钻石流水 | 实时薪资展示 | `flow_diamonds = host_diamonds + 本周期已结算钻石 + 本周期兑换花掉的钻石` | 周期边界按结算周期 | 双周、自由；master 实现 |
| 双周实际结算流水 | 双周系统结算 | `flow_diamonds = 结算快照中的 host_diamonds + 本周期兑换钻石`；主播基础/超档仍按快照钻石余额 | 当前周期 | 双周；master 实现 |
| 自由实际结算流水 | 自由政策系统或手动结算 | `flow_diamonds = host_diamonds + 本周期已结算钻石 + 本周期兑换钻石`；上次已付累计佣金以最近已打款记录的 `flow_diamonds` 为基点 | 当前周期 | 自由；master 实现 |
| `gain_coin` 历史口径 | 单独追溯原 Payroll §3.2 时 | 原规则曾要求汇总 `app_user_coin_detail` 的本期净增，并排除周期开始 10 分钟内指定的上期清算扣减；**master 公会长查档不使用该值，薪资验算不得套用此公式** | 原文排除窗口 `[start, start+10min)` | 历史差异记录；非 master 薪资规则 |

配置字段为 `level`、`diamonds`、`host_salary`、`agency_owner_salary`、`host_tg_reward`、`agency_owner_tg_reward`、`excess_diamonds_rate`。配置必须按地区、政策实时读取；下述默认分母和比例均允许配置覆盖。

### 2.2 公式、达标和精度

| Rule Name | Trigger Condition | Formula | Threshold Values | Applicable Policy |
|---|---|---|---|---|
| 双周主播应得 | 主播钻石查档后 | `deserved_salary = tier_host_salary + tier_host_tg_reward + max(0, host_diamonds-tier_diamonds) / excess_diamonds_rate` | 超档分母缺省 `25000`；配置表可覆盖 | 双周；master 实现 |
| 双周公会长分成 | 公会长钻石流水查档后 | `agency_owner_salary = owner_tier_salary × salary_ratio`；`agency_owner_tg_reward = owner_tier_tg_reward × salary_ratio`；公会长不分主播超档工资 | 配置列可为 0；不能一概认定无 TG 奖励 | 双周；master 实现 |
| 双周首周期保护 | `join_time > 当前周期起点` | `salary_ratio = 1.00`，优先于直播任务 | 严格大于周期起点 | 双周；master 实现 |
| 双周直播任务 | 不在首周期 | 有效天数 `>=6` 且总直播时长 `>=12` 小时，比例 `1.00`；否则 `0.70`；有效日需当天时长 `>=7200` 秒 | 6 天、12 小时、每天 2 小时 | 双周；master 实现 |
| 双周实际主播工资 | 比例已确定 | `actual_salary = truncate2(deserved_salary × salary_ratio)`；原始 `host_salary`、`host_tg_reward`、`excess_salary` 仍分别存储 | 比例 `1.00` 或 `0.70` | 双周；master 实现；原文“各字段先打折再求和”不等价 |
| 自由主播工资 | 主播钻石查档后 | 结算明细 `host_salary = tier_host_salary`；`excess_diamonds_salary = truncate2(truncate4((host_diamonds-tier_diamonds)/diamonds_to_usd_rate) × salary_percentage/100)`；`deserved_salary = actual_salary = host_salary + excess_diamonds_salary + tier_host_tg_reward`。公会薪资聚合展示时才将基础和超档合并为主播工资 | 分母默认 `16026`，主播比例配置默认 `75` | 自由；master 实现；区分结算字段与展示字段 |
| 自由公会长累计佣金 | `flow_diamonds` 独立查档后 | `cumulative_owner_salary = tier_owner_salary + truncate2(truncate4((flow_diamonds-owner_tier_diamonds)/diamonds_to_usd_rate) × owner_percentage/100)`；TG 取公会长所属档 | 公会长比例配置默认 `25` | 自由；master 实现 |
| 自由公会长本次结算 | 一个周期可多次手动结算 | `本次公会长工资/TG = max(0, 当前累计值-上次已付累计值)`，避免重复支付；实时展示可能显示累计值 | 上次 `flow_diamonds` 无记录视为 0 | 自由；master 实现 |
| 自由政策达标 | 自由政策结算 | `salary_ratio = 1.00`，代码无“人工指定未达标后乘 0.70”的结算分支 | 不套用双周直播任务 | 自由；master 实现；与原文例外条款冲突 |
| 自由手动结算门槛 | 主播主动发起自由结算 | 仅当 `host_salary + excess_diamonds_salary >= min_withdraw_amount` 才允许结算；TG 奖励不参与门槛。系统自动结算关闭此检查 | 配置默认 `1.00 USD` | 自由；master 实现；原 Payroll §1 的“无准入门槛”仅适用于查档，不适用于主动结算 |

> 自由政策的百分比、分母取 `content.salary.free` 运行时配置，双周超档优先取档位配置。`truncate4` 和 `truncate2` 分别指保留四位、两位并向零截断；对非负薪资等同向下取整。配置缺失、负流水等异常应先复核，不用默认示例值推算实发。

### 2.3 公会汇总、预支与盈余

| Rule Name | Trigger Condition | Formula | Threshold Values | Applicable Policy |
|---|---|---|---|---|
| 成员总工资 | 成员薪资计算完成 | `host_actual_salary = actual_salary`；逻辑上的主播总工资含档位工资、超档工资和 TG | 未达标时使用比例后的工资 | 双周、自由；master 实现 |
| 公会长佣金 | 公会所有成员计算完成 | `agent_commission = Σ(agency_owner_salary + agency_owner_tg_reward)`，含会长本人作为成员产生的分成 | 按成员政策分别计算 | 双周、自由；master 实现 |
| 公会总薪资 | 公会成员汇总 | `agency_total_salary = Σ(host_actual_salary) + agent_commission` | 含会长作为主播的实际工资 | 双周、自由；master 实现 |
| 公会薪资余额 | 公会展示 | `max(0, agency_total_salary - Σ(member_advance_salary))`；可借支额直接读公会的 `borrowable_amount`，不再次减借支 | 余额下限 0 | 双周、自由；master 实现 |
| 公会长薪资余额 | 会长展示 | `agent_total_salary = agent_commission + owner_host_salary + owner_host_tg_reward`；此处 `owner_host_salary` 是公会薪资聚合后的展示字段，已含超档及对应比例，不等于结算明细的原始 `host_salary`；`owner_salary_balance = agent_total_salary - owner_advance_salary`；借支另列。聚合的主播工资与 TG 分别截断，可能与一次性截断的 `actual_salary` 有分位差 | 预支与借支不可重复扣减 | 双周、自由；master 实现 |
| 已结算盈余本期薪资 | 公会长盈余归档 | `period_salary = Σ(会长本人已打款 actual_salary - advanced_amount/100) + Σ(全体成员已打款公会长工资及 TG)` | `status=PAID`；`advanced_amount` 单位分 | 双周系统 / 自由手动；master 实现 |
| 盈余本期借支与欠款 | 盈余归档或实时展示 | 本期借支取借支减期内还款的非负净额；历史欠款取此前最近归档中负 `period_actual_salary` 的绝对值；`period_actual_salary = period_salary-period_borrow-historical_debt` | 实时展示借支取最后一次结算之后净额 | 双周系统 / 自由手动；master 实现 |

金额与时长单位：`app_payer_host_salary_detail_v2.advanced_amount`、`.borrowed_amount` 存**分**，展示美元时除以 100；`app_user_agency.borrowed_amount`、`.borrowable_amount` 和 `app_user_account.advance_salary_total_amount` 为**美元**；`app_live_user_site_daily_summary.duration` 为**秒**，展示小时除以 3600。当前预支取账户字段，历史预支取结算明细并换算单位。

## 3. BDM：BD 个人薪资与团队管理薪资

### 3.1 人员、有效流水及底薪/Bonus

| Rule Name | Trigger Condition | Formula | Threshold Values | Applicable Policy |
|---|---|---|---|---|
| BD/BDM 身份 | 员工建档及薪资查询 | `role_bd=1` 可有 BD 个人薪资；`role_bdm=1` 可有 BDM 团队薪资；同一人可有 `salary_role=1` 和 `2` 两条记录 | 试用、转正为在职；离职不计 | BD/BDM；master 实现 |
| BD 公会流水来源 | 当前自然月实时汇总 | 当前半月公会薪资快照或现场聚合，加本月 payer 结算明细；含**所有政策的主播实际工资、公会长工资及 TG**。当前周期明细只补主播 `actual_salary`，避免公会长增量重复计入；先前半月明细加主播实际工资和公会长两列。**实时明细查询没有 `status` 条件**，因此与月结状态 `1/2/3` 口径不同 | 源选择由 `content.bd.salary.agency-cycle-salary-source` 配置 | BD/BDM；master 实现 |
| BD 月结流水来源 | 关账月 | **只遍历关账时仍绑定中的公会**，且该绑定的 `bind_time <= 关账月末`；按关账月 payer 明细求 `actual_salary+agency_owner_salary+agency_owner_tg_reward`。SQL 下界为**月初**，未按绑定发生时刻截断；解绑公会的历史绑定不进入本次月结 | 状态 `1/2/3`；排除 `0/4` | BD/BDM；master 实现；换绑当月需特别复核 |
| 单公会底薪有效流水 | 公会当前绑定中，且底薪通道可计该自然月 | 以自然月/半月周期起点为查询下界，按失效时间裁剪上界，**不按 `bind_time` 裁剪下界**；底薪通道流水达到全局门槛时全额计入，否则 0 | 全局默认约 `300 USD`，运行时配置为准 | BD/BDM；master 实现；与原 BDM §2.2 的“绑定有效期交集”不等价 |
| 单公会 Bonus 有效流水 | 公会当前绑定中，且 Bonus 通道可计该自然月 | 独立于底薪通道查询及判断；同样不按 `bind_time` 裁剪下界；达门槛全额计入 | 全局门槛同上 | BD/BDM；master 实现 |
| BD 底薪和提成 | 按公会汇总两路有效流水后 | 底薪流水命中 `bd_level_config_detail.threshold_tg` 最高档，取该档 `base_salary`；Bonus 流水**独立比档**，以对应 `commission_rate × bonus_effective_flow` 算提成 | 档位与有效月数取绑定的 BD 政策配置 | BD；master 实现 |
| BD 本月总薪资/存储余额 | 底薪、提成和新增公会数已知 | `total_salary = base_salary_amount + bonus_share_reward`；薪资计算记录的 `total_salary_balance = total_salary - 当前选定新增公会扣款`；预支和借支另存债务账 | 金额两位小数 | BD；master 实现；后台展示余额见 §3.3 |
| BDM 团队薪资记录 | 当前月实时或月结 | 汇总**BDM 本人及直属在职 BD** 的两路有效流水；兼任 BD 的 BDM 通过 `supervisor_staff_id = bd_staff.id` 自挂，本人也命中团队成员查询。团队流水按 BDM 政策重新比档，`team_salary = team_base_salary + team_bonus_flow × team_commission_rate`；本人 BD 薪资另按 BD 政策计算和结算。月结取各成员已落库的 BD 月结有效流水；缺少 BD 月结行时该成员按 0 计并登记问题单 | BDM 无新增公会考核扣款；团队不递归汇总间接下属；官方挂靠 BDM 不参与月结发薪 | BDM；master 实现；与原 BDM §4 的本人参与口径一致 |

> 当前周期实时快照的 `guild_salary_total` 是**整月公会总薪资展示值**，不等于受底薪/Bonus 到期日分别裁剪的 `base_effective_flow`、`bonus_effective_flow`。验算 BD 薪资应使用两路有效流水。见 [实时快照生成](code/admin-content/content-service/src/main/kotlin/com/dy/admin/content/service/service/bd/impl/BdRealtimeSalarySnapshotJobServiceImpl.kt)。

### 3.2 等级、有效期和新增公会

| Rule Name | Trigger Condition | Formula | Threshold Values | Applicable Policy |
|---|---|---|---|---|
| BD 展示等级 | 展示当前等级 | `max(1, 本月Bonus流水命中等级, 上月已结算Bonus流水命中等级)`；上月之前的最高等级未被永久保存为下限 | 最低 Level 1 | BD；master 实现；不保证终身只升不降 |
| BDM 展示等级 | 展示团队等级 | 比较本月团队 Bonus 流水与上月团队成员（含自挂的 BDM 本人）BD 月结 Bonus 流水之和，取更高命中等级，最低 1 | 用 BDM 政策比档 | BDM；master 实现 |
| 绑定有效期 | 新绑定或重算失效日 | 绑定日 **1-14 日**：绑定月算第 1 月，落在配置有效月数对应月末 `23:59:59`；绑定日 **15 日起**：落在绑定月加配置月数后的 **15 日 `23:59:59`** | 底薪、Bonus 各取政策配置月数；非固定 3/6 月 | BD；master 实现；不是简单“16 日起 +15 天” |
| 到期区间 | 汇总有效流水 | 已过期时查询上界裁剪至失效时刻；明细 SQL 使用 `settlement_time <= endTime`，因此失效日 `23:59:59` 仍可计入；失效月后的整月不计 | 失效月及其之前 | BD；master 实现；与原文“到期日当天不计”冲突 |
| 本月绑定数 | 新增公会统计 | 当前有效绑定中 `bind_time` 落在本自然月的记录数；未检查公会首次创建时间和首次绑定 BD | 自然月 | BD；master 实现 |
| 本月有效绑定数 | 新增有效公会统计 | 本月绑定，且底薪或 Bonus 任一通道达到单公会有效流水门槛的公会数 | 门槛取全局配置 | BD；master 实现 |
| 新增公会扣款 | 本月选定口径新增数小于政策目标 | `(base_salary_amount+bonus_share_reward) × deduction_rate`；两套口径均计算并保存，实际余额默认按 `EFFECTIVE_COUNT`，可配置为 `BIND_COUNT`；仅使用中的 BD 政策扣款 | `target_new_guild_count`、`deduction_rate` 取 BD 政策 | BD；master 实现；BDM 不扣 |

### 3.3 查询、余额与原文保留条款

| Rule Name | Trigger Condition | Formula | Threshold Values | Applicable Policy |
|---|---|---|---|---|
| 当前月薪资查询 | 查询 BD 当前自然月 | 读 `bd_realtime_staff_salary` 的 BD 个人薪资行；团队薪资另用 BDM 角色行 | `salary_role=1` 为 BD、`2` 为 BDM | BD/BDM；master 实现 |
| 历史月薪资查询 | 查询已关账月份 | 读 `bd_staff_monthly_salary`，不能与实时快照拼接为一笔薪资 | 以 `salary_month` 和 `salary_role` 定位 | BD/BDM；master 实现 |
| BD 后台实时列表余额 | 展示 BD 当前月薪资明细 | 选有效新增口径时：`total_salary - effective_deduct - debt.advance_total_amount - debt.borrowed_amount`；选绑定新增口径时：`r.total_salary_balance - debt.advance_total_amount - debt.borrowed_amount`；债务缺失按 0。后一分支直接沿用存储余额，若生成快照后切换扣款口径，不能假定它等于当前所选扣款的重算值 | 与薪资记录存储的 `total_salary_balance` 不同 | BD；master 实现；与原 BDM §11“直接展示”冲突 |
| BD 后台历史列表余额 | 展示 BD 历史月薪资明细 | `monthly.total_salary - selected_deduct - before_advance_total_amount - before_borrowed_amount`；使用月结前债务快照，不拼入当前债务 | 按当月选定扣款口径 | BD；master 实现 |
| BDM 后台列表总薪资 | 展示 BDM 当前或历史月 | 在 BDM 团队薪资记录 `total_salary` 上**另加本人 BD 记录的 `bonus_share_reward`**；该展示式未加本人 BD 底薪；再扣预支和借支展示余额并钳至 0 | 当前月用实时债务，历史月优先用本人 BD 月结前债务快照 | BDM 后台列表；master 实现；与底层双轨记录须区分 |
| 债务与额度 | 展示预支、借支和可借支额 | `bd_staff_salary_debt` 按 `staff_id` 存债务；可借支额=`borrow_limit_amount-borrowed_amount`；“无债务记录”文案及字段完整性按原 BDM §11 核查 | 当前余额与历史快照不可混用 | BD/BDM；部分 master 实现，页面文案待专项核验 |
| 提现余额 | BD 薪资提现 | BD/BDM 使用独立的 `bd_staff_balance` 余额，申请前校验可用额；金币申请即时扣款并发币，现金申请创建待审订单后**立即扣减余额**，拒绝时按订单幂等退款 | 金币最低 `1 USD`；现金最低 `50 USD`、每月 3-7 日（中东时区）；金额必须为整数 USD | master 实现；与原 BDM §9“现金提交不冻结”冲突 |
| 换绑 BD | 公会更换绑定 BD | 已核实的 master 管理入口提供解绑和重新绑定：解绑删除绑定主表行，重绑按新 BD 政策生成失效日，新记录 `bind_time` 参与新增数；不按原规则的“换绑不计新增、不重置有效期”验算。专用换绑入口是否存在仍待核验 | 当月流水按 §3.1 的当前绑定与查询区间口径 | 已核实入口以 master 实现为准；其他入口待核验 |
| 查询质量门禁 | 薪资验算或导出 | 有未解决 `bd_staff_monthly_salary_issue` 时标注异常；先核对列名和前 3 行，完整列出有薪资人员与金额字段 | `issue_status=1` | 沿用原 BDM §11.2 的验算要求 |

### 3.4 已核验的规则

以下仅列已通过 master 源码核实的执行口径。

| Rule Name | Trigger Condition | Formula | Threshold Values | Applicable Policy |
|---|---|---|---|---|
| 政策状态 | 新建公会绑定或停用薪资政策 | 新建绑定要求 BD 政策 `IN_USE`；仍被正常员工档案绑定的 BD/BDM 政策不能停用 | `IN_USE` / `DISABLED`；员工 `record_status=1` | BD/BDM；master 实现 |
| 公会审核 | BD 提交创建公会申请，BDM 或管理员审核 | 提交后为审核中；仅审核中申请可审核，通过后创建公会并绑定发起 BD，拒绝后记录驳回原因；公会名称不得与现存公会或审核中申请重名，已拒绝申请不占用名称 | `apply_status=0/1/2` 分别为审核中/已通过/已拒绝；master 未定义“已取消”状态 | BDM 原 §1；master 实现 |
| 提现审核 | BD/BDM 申请薪资提现 | 金币申请创建已批准订单、扣余额后发币；现金申请创建待审订单并扣余额，审核通过只更新订单状态，拒绝时按原扣款日志退款 | 金币最低 `1 USD`；现金最低 `50 USD` | BD/BDM；master 实现 |
| 提现时间、渠道和汇率 | BD/BDM 申请薪资提现 | 金币申请没有日期窗口；现金申请限每月 3-7 日，允许 `USDT`、`Bank`、`Vodafone`、`Shamcash`、`JazzCash`、`Easypaisa`、`Western Union`；BD 金币换算使用服务端常量 `11800` 金币/USD | 现金日期按中东时区；提现金额须为整数 USD | BD/BDM；master 实现 |
| 管理端公会绑定 | 管理员绑定、解绑或重新绑定公会 | 公会已有绑定时拒绝重复绑定；解绑删除 `bd_agency_bind` 主表行并写操作日志；重新绑定按目标 BD 政策和新 `bind_time` 生成底薪、Bonus 失效日 | 目标 BD 档案正常、在职且承担 BD 职责；政策须 `IN_USE` | BD；master 实现 |
| 公会换绑 BD | 管理端将公会由原 BD 改绑至目标 BD | 先解绑再绑定；旧绑定主表行被删除，新绑定按目标 BD 政策重新计算底薪、Bonus 失效日；新 `bind_time` 落在本月时参与新增公会数，月结仅遍历届时仍绑定的公会 | 公会未解散、目标 BD 档案正常且在职；流水查询与月结范围见 §3.1、§3.2 | BDM 原 §10；按 master 已核实的管理端执行口径 |
| 主播换公会 | 主播在结算周期内变更公会并进入周期结算 | 周期末从当前有效公会成员关系生成钻石快照，快照记录 `agency_id`；主播薪资明细及公会长分成使用该快照公会。对应 BD 的流水归集继续按 §3.1 的当前公会绑定和月结查询口径，不能仅凭主播快照推定历史 BD 归属 | 半月结算周期；快照生成时的有效公会成员关系 | BDM 原 §8；Payroll 周期结算；master 实现 |
| 公会长负值结转 | 归档 `period_actual_salary < 0` | 负值实际工资原样归档；后续周期取此前最近归档负值的绝对值作为历史欠款。实时展示从本期薪资扣本期借支与历史欠款，`period_actual_salary` 可以仍为负值 | 历史欠款在最近归档实际工资非负时为 0 | Payroll 公会长盈余；master 实现 |

## 4. master 业务规则速查

下表汇总已核实的执行口径；计算细节和数据来源见 §2、§3。

| Rule Name | Trigger Condition | Formula | Threshold Values | Applicable Policy |
|---|---|---|---|---|
| 公会长独立查档 | 计算成员对应的公会长分成 | 用本周期累计钻石流水 `flow_diamonds` 独立匹配公会长档位；双周取档位分成，自由政策另按超档钻石计算增量佣金 | 档位按地区、政策配置 | Payroll 双周、自由；master 实现 |
| 双周未达标工资 | 首周期保护不适用且直播任务未达标 | 主播 `actual_salary = truncate2(deserved_salary × 0.70)`；公会长工资和 TG 各自乘 `0.70` 后截断 | 有效直播天数 `<6` 或总时长 `<12` 小时 | Payroll 双周；master 实现 |
| 自由政策工资比例 | 计算自由政策薪资 | 超档分母及主播/公会长比例读取 `content.salary.free`；`salary_ratio = 1.00` | 缺省分母 `16026`，主播 `75%`，公会长 `25%` | Payroll 自由；master 实现 |
| 自由手动结算门槛 | 主播发起自由结算 | `host_salary + excess_diamonds_salary >= min_withdraw_amount`；系统自动结算跳过此检查 | 门槛默认 `1.00 USD`；TG 不计入 | Payroll 自由；master 实现 |
| BD 公会薪资流水 | 汇总当前月或关账月单公会流水 | 计入各政策主播 `actual_salary` 与公会长工资、TG；实时当前周期明细仅补 `actual_salary`，先前周期明细计入三列 | 底薪与 Bonus 分别应用单公会有效门槛 | BD/BDM；master 实现 |
| 实时与月结明细状态 | 查询当前月实时流水或生成月结 | 实时月内 payer 明细不筛 `status`；月结只纳入 `status IN (1,2,3)`，排除 `0/4` | 按明细 `settlement_time` 落入查询区间 | BD/BDM；master 实现 |
| 当前绑定与流水区间 | 实时汇总或月结 BD 公会流水 | 仅遍历当前绑定公会；查询下界取自然月或当前半月周期起点，不以 `bind_time` 截断；月结不读取已解绑绑定主表记录 | 月结要求 `bind_time <= 关账月末`；各通道按失效时刻裁剪上界 | BD/BDM；master 实现 |
| BD/BDM 展示等级 | 展示本月等级 | 比较本月与上月 Bonus 有效流水的命中档位，取较高等级，最低 Level 1 | 上月之前的等级不作为永久下限 | BD/BDM；master 实现 |
| 绑定失效日及边界 | 创建绑定或累计到期月流水 | 1-14 日绑定按配置有效月数落在对应月末；15 日起绑定落在绑定月加有效月数后的 15 日 `23:59:59`；失效时刻可计入明细 | 底薪、Bonus 各取政策配置月数 | BD；master 实现 |
| 新增公会数和扣款 | 统计当前月绑定并计算 BD 薪资 | 当前绑定中 `bind_time` 落在本月即计绑定新增；有效新增另要求底薪或 Bonus 任一通道达门槛；低于政策目标时按选定口径计算扣款 | 默认 `EFFECTIVE_COUNT`，可配置 `BIND_COUNT`；目标和比例取 BD 政策 | BD；master 实现 |
| 后台 BD 薪资余额 | 查询当前或历史月 BD 列表 | 当前月按 §3.3 的所选扣款分支再减实时预支、借支；历史月按所选扣款减月结前债务快照 | 当前债务与历史快照分开取值 | BD 后台；master 实现 |
| 后台 BDM 合并展示 | 查询当前或历史月 BDM 列表 | `展示总薪资 = BDM 团队 total_salary + 本人 BD bonus_share_reward`；展示余额再减相应债务并钳至 0 | 本人 BD 底薪不加入该展示式 | BDM 后台；master 实现 |
| 后台 BD 列表范围 | 查询当前月 BD 薪资明细 | 筛 `salary_role=1`、`role_bd=1` 等条件；不附加 `total_salary>0` 条件 | 0 薪资行可能出现 | BD 后台；master 实现 |
| 政策停用限制 | 停用 BD/BDM 薪资政策 | 正常员工档案仍绑定该政策时拒绝停用；新建公会绑定要求 BD 政策为 `IN_USE` | `record_status=1` 的绑定员工参与停用校验 | BD/BDM；master 实现 |
| BD 提现扣款及金币汇率 | BD/BDM 申请薪资提现 | 金币申请扣 `bd_staff_balance` 后发币，按 `11800` 金币/USD 换算；现金申请创建待审订单时扣余额，拒绝时退款 | 金币最低 `1 USD`；现金最低 `50 USD` 且仅每月 3-7 日（中东时区） | BD/BDM；master 实现 |

## 5. 源码定位

| 主题 | master 源码 |
|---|---|
| Payroll 成员档位、比例、自由佣金与主动结算门槛 | [SalaryV2Extension.kt](code/app-payer/payer-client/src/main/kotlin/com/dy/app/payer/extension/SalaryV2Extension.kt)、[ContentSalarySettlementServiceImpl.kt](code/admin-content/content-service/src/main/kotlin/com/dy/admin/content/service/service/salary/v2/impl/ContentSalarySettlementServiceImpl.kt)、[ContentSalaryCalculationV2ServiceImpl.kt](code/admin-content/content-service/src/main/kotlin/com/dy/admin/content/service/service/salary/v2/impl/ContentSalaryCalculationV2ServiceImpl.kt)、[ContentFreeSalaryServiceImpl.kt](code/admin-content/content-service/src/main/kotlin/com/dy/admin/content/service/service/salary/v2/impl/ContentFreeSalaryServiceImpl.kt) |
| 公会薪资聚合、盈余 | [ContentAgencyMemberSalaryV2ServiceImpl.kt](code/admin-content/content-service/src/main/kotlin/com/dy/admin/content/service/service/salary/v2/impl/ContentAgencyMemberSalaryV2ServiceImpl.kt)、[SalaryAggregationCalculator.kt](code/admin-content/content-service/src/main/kotlin/com/dy/admin/content/service/service/salary/v2/util/SalaryAggregationCalculator.kt)、[ContentAgencyOwnerSurplusServiceImpl.kt](code/admin-content/content-service/src/main/kotlin/com/dy/admin/content/service/service/salary/v2/impl/ContentAgencyOwnerSurplusServiceImpl.kt) |
| BD 两路有效流水、等级和扣款 | [BdSalaryRealtimeSummaryServiceImpl.kt](code/admin-content/content-service/src/main/kotlin/com/dy/admin/content/service/service/bd/impl/BdSalaryRealtimeSummaryServiceImpl.kt)、[ContentBdSalaryProperties.kt](code/admin-content/content-service/src/main/kotlin/com/dy/admin/content/service/properties/ContentBdSalaryProperties.kt) |
| BDM 团队实时及月结 | [BdStaffServiceImpl.kt](code/admin-content/content-service/src/main/kotlin/com/dy/admin/content/service/service/bd/impl/BdStaffServiceImpl.kt)、[BdBdmTeamRealtimeSalaryServiceImpl.kt](code/admin-content/content-service/src/main/kotlin/com/dy/admin/content/service/service/bd/impl/BdBdmTeamRealtimeSalaryServiceImpl.kt)、[BdStaffMonthlySalarySettlementServiceImpl.kt](code/admin-content/content-service/src/main/kotlin/com/dy/admin/content/service/service/bd/impl/BdStaffMonthlySalarySettlementServiceImpl.kt) |
| BD/BDM 后台列表展示 | [BdRealtimeStaffSalaryDao.xml](code/admin-content/content-service/src/main/resources/mapper/BdRealtimeStaffSalaryDao.xml)、[BdStaffMonthlySalaryDao.xml](code/admin-content/content-service/src/main/resources/mapper/BdStaffMonthlySalaryDao.xml) |
| 公会快照与绑定失效边界 | [ContentHostSalaryRealtimeSnapshotDao.xml](code/admin-content/content-service/src/main/resources/mapper/ContentHostSalaryRealtimeSnapshotDao.xml)、[BdAgencyBindExpireRules.kt](code/admin-content/content-service/src/main/kotlin/com/dy/admin/content/service/service/bd/BdAgencyBindExpireRules.kt)、[BdAgencyBindSalaryQueryBounds.kt](code/admin-content/content-service/src/main/kotlin/com/dy/admin/content/service/service/bd/BdAgencyBindSalaryQueryBounds.kt) |
| 绑定、政策停用及提现 | [BdAgencyBindServiceImpl.kt](code/admin-content/content-service/src/main/kotlin/com/dy/admin/content/service/service/bd/impl/BdAgencyBindServiceImpl.kt)、[BdLevelConfigServiceImpl.kt](code/admin-content/content-service/src/main/kotlin/com/dy/admin/content/service/service/bd/impl/BdLevelConfigServiceImpl.kt)、[SalaryWithdrawServiceImpl.kt](code/app-payer/payer-service/src/main/kotlin/com/dy/app/payer/service/service/withdraw/impl/SalaryWithdrawServiceImpl.kt)、[BdSalaryWithdrawBalanceServiceImpl.kt](code/admin-content/content-service/src/main/kotlin/com/dy/admin/content/service/service/bd/impl/BdSalaryWithdrawBalanceServiceImpl.kt) |
