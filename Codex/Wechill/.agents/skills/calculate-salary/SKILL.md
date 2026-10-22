---
name: calculate-salary
description: Calculate streamer salary from MySQL data and business rules. 从 MySQL 数据和业务规则计算主播/公会长薪资；读取 Payroll/核心业务规则.md 与 Payroll/AGENTS.md。Use when tier-based payroll computation is needed for English or Middle East regions.
---

# 计算主播薪资

## 规则文档（必读）

计算前必须读取以下文档：
- `Payroll/核心业务规则.md` — 档位公式、超档计算、罚则
- `Payroll/AGENTS.md` — 数据库表结构、枚举值、用户验证

辅助参考：
- `Payroll/公会薪资计算规则.md` — 字段定义（主播/公会长视角）

## 输入

仅在请求未提供或无法从上下文可靠推断时，向用户确认：
- `user_number`（默认用户标识）、`region`（English / Middle East）、`policy`（free / bi-weekly）与结算周期
- 只有当用户明确说明输入是 `user_id` 时，才按 `user_id` 处理。

## 流程

1. 将任务限定为 `Payroll/` 规则范围，并加载必读规则文档；无需为当前工作目录另行询问。
2. 解析用户身份：
   - 默认把数字输入解释为 `app_user.user_number`。
   - 得出用户不存在结论前，检查 `app_user` 以及 `Payroll/AGENTS.md` 中说明的相关扩展/审核表。
   - 以 `app_user.user_number` 过滤并解析 `user_id`；后续按 `user_id` 关联的业务表，使用该已验证的关联键查询。
3. 每张表首次查询前，先执行 `SHOW COLUMNS FROM <table>`。
4. 每次数据查询后，预览列名和前 3 行。如出现空值、格式非法或数据偏移，在结论前输出 **异常声明**。
5. 从 `stay.app_payer_salary_v2_config` 查询档位配置（禁止硬编码）：

```sql
SELECT `level`, diamonds, host_salary, agency_owner_salary,
       host_tg_reward, agency_owner_tg_reward
FROM stay.app_payer_salary_v2_config
WHERE settlement_policy_type = ?   -- 1=双周, 2=自由
  AND region = ?                   -- 0=英语区, 2=中东区
ORDER BY `level` ASC
```

6. **数据字段映射**:
   - **主播薪资基数** → `gain_diamond + send_gain_diamond`（两者求和）
   - **公会长分成基数** → **调整后的本期 `period_gain_coin`**，由 `app_user_coin_detail` 计算；严禁直接使用 `app_user_account.gain_coin`（历史累计）

   主播薪资基数（通过 `user_number` 过滤身份）:
   ```sql
   SELECT a.gain_diamond, a.send_gain_diamond,
          a.gain_diamond + a.send_gain_diamond AS host_diamonds
   FROM app_user u
   JOIN app_user_account a ON a.user_id = u.user_id
   WHERE u.user_number = :user_number;
   ```

   公会长分成基数（使用半开区间 `[start, end_exclusive)`）:
   ```sql
   SELECT
     IFNULL(SUM(d.coin), 0) AS raw_period_gain_coin,
     IFNULL(SUM(CASE
       WHEN d.source_type = 18
        AND d.option_type = 203
        AND d.remark = 'host salary'
        AND d.coin < 0
        AND d.create_time >= :start
        AND d.create_time < DATE_ADD(:start, INTERVAL 10 MINUTE)
       THEN d.coin
       ELSE 0
     END), 0) AS excluded_settlement_deduction,
     IFNULL(SUM(
     CASE
       WHEN d.source_type = 18
        AND d.option_type = 203
        AND d.remark = 'host salary'
        AND d.coin < 0
        AND d.create_time >= :start
        AND d.create_time < DATE_ADD(:start, INTERVAL 10 MINUTE)
       THEN 0
       ELSE d.coin
     END
     ), 0) AS period_gain_coin,
     COUNT(*) AS record_count
   FROM app_user u
   JOIN app_user_coin_detail d ON d.user_id = u.user_id
   WHERE u.user_number = :user_number
     AND d.coin_type = 1
     AND d.create_time >= :start
     AND d.create_time < :end_exclusive;
   ```

   - 上述四项条件同时满足的负向流水是**上期结算清算扣减**，不属于本期分成基数。
   - 除此精确条件外，其他负向 `coin` 流水必须保留；若调整后 `period_gain_coin` 仍为负，先列出流水明细并标为待复核。
   - 查询后必须同时输出原始 `SUM(coin)`、被排除扣减金额、调整后 `period_gain_coin` 和记录数，便于审计。

7. **每个用户同时计算两项**（无关 role 值）:
   - **主播薪资**：用该用户的 `gain_diamond + send_gain_diamond` 查主播档位，计算主播薪资
   - **公会长分成**：用调整后的本期 `period_gain_coin` 查会长档位，计算公会长分成
   - 两项结果叠加为该用户的总收入

8. **档位独立判定**:
   - **主播档位**：根据 `gain_diamond + send_gain_diamond` 查档位，确定 `host_salary` / `host_tg_reward` / 超档门槛
   - **会长档位**：根据**调整后的本期 `period_gain_coin`**独立查档位，确定 `agency_owner_salary` / `agency_owner_tg_reward` / 超档门槛
   - 两者可处于不同档位，互不影响。

9. **无门槛规则（所有政策通用）**:
   - 当钻石数**未达到最低档位（Level 1）**时，基础薪资和 TG 奖励均为 0
   - 超档从 **0** 起算：`over = diamonds - 0 = diamonds`
   - 超档佣金按正常系数计算：自由政策 主播×0.75 / 会长×0.25，双周政策 主播×1.0 / 会长无佣金
   - 即：未达档 = 纯超档佣金，无基础+无TG

10. **达标判定（英语区+中东区双周政策）**:
   - 查 `stay.app_live_user_site_daily_summary` 表
   - 达标条件：**每日直播时长 ≥ 2 小时（7200 秒）**
   - **结算周期**：上半月 1-15 日 / 下半月 16-月末
   - 若 `app_user_agency_member.join_time` 在当前结算周期内 → **免于惩罚**

11. 应用罚则：
   - Bi-weekly policy (English + Middle East)：未达标成员（任意 role）→ 所有字段（base salary、over-tier、commission）统一 **0.7× penalty**。
   - Free policy：默认达标 (default qualified)。
   - 新成员（`join_time` 在当前结算周期内）：免罚。

## Precision（精度强制要求）

**所有涉及小数的计算必须使用 Python `Decimal`，严禁 `float`。**

### 标准写法

```python
from decimal import Decimal, ROUND_DOWN

def floor2(d: Decimal) -> Decimal:
    return d.quantize(Decimal('0.01'), rounding=ROUND_DOWN)

# ── 每个用户同时计算两项 ──

# 主播薪资（用 gain_diamond + send_gain_diamond）
host_diamonds = Decimal(str(user_gain_diamond + user_send_gain_diamond))
# ... 查档位得到 tier (可能为 None)
if tier:
    threshold = Decimal(str(tier['diamonds']))
    host_base = Decimal(str(tier['host_salary']))
    host_tg = Decimal(str(tier['host_tg_reward']))
else:
    # 未达最低档位：基础=0, TG=0, 超档从0起算
    threshold = Decimal('0')
    host_base = Decimal('0.00')
    host_tg = Decimal('0.00')

over = host_diamonds - threshold
over_unit = over / DENOM
if is_biweekly:
    host_commission = floor2(over_unit)           # 双周：不乘系数
else:
    host_commission = floor2(over_unit * Decimal('0.75'))  # 自由：×0.75
host_total = floor2(host_base + host_commission + host_tg)

# 公会长分成（使用调整后的本期 period_gain_coin）
president_diamonds = Decimal(str(period_gain_coin))

# ... 查档位得到 tier (可能为 None)
if tier:
    threshold = Decimal(str(tier['diamonds']))
    president_base = Decimal(str(tier['agency_owner_salary']))
    president_tg = Decimal(str(tier['agency_owner_tg_reward']))
else:
    # 未达最低档位：基础=0, TG=0, 超档从0起算
    threshold = Decimal('0')
    president_base = Decimal('0.00')
    president_tg = Decimal('0.00')

over = president_diamonds - threshold
over_unit = over / DENOM
if is_biweekly:
    president_commission = Decimal('0.00')         # 双周：无超档佣金
else:
    president_commission = floor2(over_unit * Decimal('0.25'))  # 自由：×0.25
president_total = floor2(president_base + president_commission + president_tg)

# 用户总收入
user_total = floor2(host_total + president_total)
```

### 关键规则

- 所有 `Decimal()` 构造必须传入**字符串**，禁止传入 `float`
- 每个独立字段计算完毕后调用 `floor2()` 截断
- 下游字段引用已截断的 `Decimal` 值

## 输出

返回完整、可审计的表格。主播与公会长必须分别成行，并提供总收入行：

| 收入项 | 计算基数 | Tier | 基础薪资 | TG 奖励 | 超档量 | 超档佣金 | 罚则系数 | 实发金额 |
|--------|----------|------|----------|----------|--------|----------|----------|----------|
| 主播收入 | `gain_diamond + send_gain_diamond` | | | | | | | |
| 公会长收入 | 调整后的本期 `period_gain_coin` | | | | | | | |
| 总收入 | - | - | - | - | - | - | - | |

如任一基数字段为空、档位缺失或数据格式非法，先输出 **异常声明**，再说明该用户无法安全结算或采用的经确认处理方式。
