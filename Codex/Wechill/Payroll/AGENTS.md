# AGENTS.md — 多地区薪资自动化处理中心

## 1. 环境与执行权限 (Environment & Autonomy)
- **PYTHON_EXE**: `E:\python\work\.venv\Scripts\python.exe`
- **SHELL**: Windows PowerShell / Git Bash
- **免试授权**: 脚本执行、文件读写、数据计算**无需询问**。遇错（如路径、编码、环境问题）必须**自动修复重试**。
- **调用约束**: Python 执行必须显式使用 `${PYTHON_EXE}` 全路径。

## 2. 核心业务规则

> 所有薪资计算规则、档位表、公式定义详见 **`核心业务规则.md`**。执行计算前必须完整读取该文件。公会级字段定义及盈余模块参见 **`公会薪资计算规则.md`**。

### 2.1 用户存在性验证（强制）

计算薪资前，默认按 `user_number` 在 MySQL 中验证并解析 `user_id`；只有用户明确说明输入是 `user_id` 时才直接使用。缺失用户（如 16444）直接返回「无数据」，不进行后续计算。

### 2.2 档位独立判定

- **主播档位**: 由 `gain_diamond + send_gain_diamond` 决定
- **公会长档位**: 由 **调整后的本期 `period_gain_coin`** 独立决定；其来自 `app_user_coin_detail`，不使用历史累计 `gain_coin`。两者互不影响，可处于不同档位

## 3. 技术执行规范 (Technical Standards)
- **依赖库**: 必须使用 `pandas` 或 `openpyxl`。
- **截断算法**: 严禁四舍五入。统一使用 `math.floor(x * 100) / 100`。
- **预检机制**: 处理前强制检查：`空值`、`重复 ID`、`负数流水`。
- **安全性**: 结算完成后，中间过程变量需在内存中清零，不保留敏感计算轨迹。

## 4. 工作流指令 (Workflow)
1. **预览**: 读取数据后，输出 `列名` 及 `前 3 行` 采样。
2. **计算**: 依据 `核心业务规则.md` 中的地区档位表与公式进行逻辑匹配与计算。
3. **交付**: 
    - 导出文件：`New_Settlement_YYYYMMDD.xlsx`。
    - **异常声明**: 在结论前单独列出数据质量问题。
    - **风险提示**: 高亮提示异常高薪或逻辑跳档。

## 5. 数据库表速查 (Database Tables, 库: `stay`)

| 表名 | 用途 | 关键字段 |
|:---|:---|:---|
| `app_user` | 主用户表 | `user_id`, `nickname`, `sex`, `status` |
| `app_user_account` | 用户钻石/余额 | `gain_coin`（历史累计，仅作审计；**当前周期分成基数需取 coin_detail 调整后本期净增**，见核心业务规则 §3.2）, `gain_diamond + send_gain_diamond`（主播薪资基数）, `advance_salary_total_amount`（预支总额，美元）, `withdrawal_balance`（可提现余额，美元） |
| `app_user_agency` | 公会信息 + 借支额度 | `agency_id`, `agency_name`, `owner_user_id`, `region`, `country`, `settlement_policy_type`, `borrowed_amount`（已借金额，**美元**）, `borrowable_amount`（可借支额度，**美元**，直接读字段，不做动态扣减） |
| `app_user_agency_member` | 公会成员关系 | `user_id`, `agency_id`, `role`, `settlement_policy_type`, `status`, `join_time`（用于首周期免罚判定） |
| `app_payer_salary_v2_config` | 档位配置表（计算必须实时查询，严禁硬编码） | `settlement_policy_type`, `region`, `level`, `diamonds`, `host_salary`, `agency_owner_salary`, `host_tg_reward`, `agency_owner_tg_reward`, `excess_diamonds_rate` |
| `app_payer_host_salary_detail_v2` | 历史结算记录（status=2=已打款） | `user_id`, `agency_id`, `host_salary`, `excess_diamonds_salary`, `host_tg_reward`, `actual_salary`, `salary_ratio`, `agency_owner_salary`, `agency_owner_tg_reward`, `advanced_amount`（**分** ÷100=美元）, `borrowed_amount`（**分** ÷100=美元）, `diamonds`, `settlement_time` |
| `app_payer_diamond_purchase_detail` | 钻石→金币兑换记录 | `user_id`, `spent_diamonds`（兑换花掉的钻石）, `create_time` |
| `app_live_user_site_daily_summary` | 每日直播时长汇总 | `user_id`, `dates`, `duration`（**秒** ÷3600=小时） |
| `app_user_coin_detail` | gain_coin 账变流水 | `user_id`, `coin`, `send_coin`, `left_coin`, `coin_type`（1=gain_coin, 5=send_coin）, `source_type`, `option_type`, `remark`, `object_id`（提现场景 `salary withdraw coins` 关联 `app_salary_withdraw_order.id`）, `create_time`；周期开始后 10 分钟内的 `source_type=18` + `option_type=203` + `remark='host salary'` + 负 `coin` 为上期清算，需从本期分成基数排除 |
| `app_payer_agency_owner_surplus` | 公会长盈余归档（每期结算后一条） | `agency_id`, `owner_user_id`, `cycle_start`, `cycle_end`, `period_salary`, `period_borrow`, `period_actual_salary`, `historical_debt`, `settlement_type`, `status` |

### 5.1 单位换算警示

| 字段 | 所在表 | 存储单位 | 页面单位 | 换算 |
|:---|:---|:---|:---|:---|
| `advanced_amount` | `app_payer_host_salary_detail_v2` | **分** | 美元 | ÷ 100 |
| `borrowed_amount` | `app_payer_host_salary_detail_v2` | **分** | 美元 | ÷ 100 |
| `borrowed_amount` | `app_user_agency` | 美元 | 美元 | 无需换算 |
| `borrowable_amount` | `app_user_agency` | 美元 | 美元 | 无需换算 |
| `duration` | `app_live_user_site_daily_summary` | **秒** | 小时 | ÷ 3600 |
| 其余金额字段 | 各表 | 美元 | 美元 | 无需换算 |

**枚举值：**
- `role`: 0=公会长, 2=主播
- `settlement_policy_type`: 1=双周政策, 2=自由政策
- `region`: 0=英语区, 2=中东区

**资产计算查询模板：**
```sql
-- 主播薪资档位查询
SELECT `level`, diamonds, host_salary, agency_owner_salary,
       host_tg_reward, agency_owner_tg_reward, excess_diamonds_rate
FROM stay.app_payer_salary_v2_config
WHERE settlement_policy_type = ?   -- 1=双周, 2=自由
  AND region = ?                   -- 0=英语区, 2=中东区
ORDER BY `level` ASC

-- 用户账户及公会信息（公会长分成基数见核心业务规则.md §3.2，需取本期 gain_coin 净增）
SELECT a.user_id, a.gain_coin, a.gain_diamond, a.send_gain_diamond,
       m.agency_id, m.role, m.settlement_policy_type
FROM app_user_account a
LEFT JOIN app_user_agency_member m
  ON a.user_id = m.user_id AND m.status = 1
WHERE a.user_id IN (<user_ids>)

-- 当前周期 gain_coin 净增（公会长分成基数；排除周期起始上期清算扣减）
SELECT IFNULL(SUM(CASE
  WHEN source_type = 18 AND option_type = 203 AND remark = 'host salary'
   AND coin < 0 AND create_time >= ? AND create_time < DATE_ADD(?, INTERVAL 10 MINUTE)
  THEN 0 ELSE coin
END), 0) AS period_gain_coin
FROM app_user_coin_detail
WHERE user_id = ? AND coin_type = 1
  AND create_time >= ? AND create_time < ?;
```

---

## 5.2 子目录结构

| 目录 | 用途 |
|:---|:---|
| `reports/` | 结算数据报告（如 `April_2026_Settlement_Data.md`） |
| `scripts/` | 薪资验算/校验脚本（`salary_validator.py` / `may_salary_check.py`） |

---

## 6. 输出准则 (Output)
- **语言**: 简体中文。结论先行，无填充词。
- **格式**: 数据对比用 **Markdown 表格**；重要信息 **加粗**；文件/变量用 `反引号`。
