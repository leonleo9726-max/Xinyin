---
name: payroll-data-audit
description: Audit MySQL source data and tier configuration required for Payroll calculations without calculating or writing payouts. 检查薪资计算前的用户数据、档位配置、枚举和结算期数据质量。Use when validating Payroll data, investigating an anomalous payout, or preparing a batch for salary calculation.
---

# Payroll Data Audit

在计算前建立可追溯的数据质量证据。此 skill 只读取数据并报告异常；薪资计算仍使用 `$calculate-salary`。

## 范围与输入

- 将任务限定为 `Payroll/`，先读取 `Payroll/核心业务规则.md` 与 `Payroll/AGENTS.md`。
- 从请求解析 `user_number`、region、policy 与结算期。只询问无法可靠推断且会改变查询范围的值。
- 不写入数据库，不修复历史数据，不计算或承诺薪资金额。

## 审计流程

1. 每张首次访问的表先执行 `SHOW COLUMNS FROM <table>`；所有用户表优先按 `user_number` 查询。仅在 schema 确认不存在该列时，先解析为 `user_id` 再查询。
2. 对每项查询展示列名与前 3 行。用户不存在前，按 `Payroll/AGENTS.md` 同时检查基础表和扩展/审核表。
3. 检查主播基数 `gain_diamond`、`send_gain_diamond` 的空值、非数值、负值和异常数量级。`app_user_account.gain_coin` 仅作历史累计审计，不作为会长结算基数；保留原始字段，不用 `COALESCE` 掩盖异常。
4. 审计 `app_user_coin_detail` 的会长结算基数：验证半开周期边界、`coin_type = 1`、原始 `SUM(coin)`、周期起始 10 分钟内上期清算扣减的排除金额、调整后 `period_gain_coin` 与记录数。非精确匹配的负向流水必须保留；调整后仍为负时列出明细并标记待复核。
5. 检查 `stay.app_payer_salary_v2_config`：region、policy 与请求一致；档位唯一且升序；门槛、基础薪资、TG 奖励为可解析的非负数；相邻档位不存在重复或倒退门槛。
6. 双周政策时，检查成员级 `settlement_policy_type`、结算期边界、`join_time` 与每日直播时长数据是否足以判定新成员豁免和达标罚则。自由政策明确标记直播时长检查为不适用。
7. 区分数据缺失、格式错误、枚举不匹配与业务上有效的未达档，禁止将这些情况混为零值。

## 输出

先给出 **可计算**、**需人工确认** 或 **不可安全计算** 的结论，再返回完整审计表：

| 检查项 | 数据源 | 结果 | 证据 | 影响 |
|--------|--------|------|------|------|

出现任一异常时，在结论前增加 **异常声明**，逐项说明影响、缺失证据和下一步查询或修复责任方。
