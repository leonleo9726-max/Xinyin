#!/usr/bin/env python3
"""
Salary Validator — Deterministic payroll calculation with field-mapping assertions.

Usage:
    python salary_validator.py <user_id> [--date YYYY-MM-DD] [--pretty]

All business rules are enforced via code, not LLM interpretation.
Field mappings (gain_coin vs gain_diamond) are guarded by assertions that
prevent silent field swaps.
"""

import json
import sys
import calendar
from datetime import datetime, date, time, timedelta
from decimal import Decimal, ROUND_DOWN
from typing import Optional

import pymysql

# ============================================================
# Database Configuration
# ============================================================
DB_CONFIG = {
    "host": "internal.eastpointtest.com",
    "port": 30306,
    "user": "root",
    "password": "kj-mysql.2023",
    "database": "stay",
    "charset": "utf8mb4",
}

# ============================================================
# Business Rule Constants (DO NOT MODIFY without updating docs)
# ============================================================
LIBERAL_DENOM = Decimal("16026")        # 自由政策超档分母（固定值，非DB字段）
BIWEEKLY_DENOM = Decimal("25000")       # 双周政策超档分母
HOST_COMMISSION_RATE = Decimal("0.75")  # 自由政策：主播超档 ×0.75
PRESIDENT_COMMISSION_RATE = Decimal("0.25")  # 自由政策：会长超档 ×0.25
PENALTY_RATE = Decimal("0.7")           # 双周不合格惩罚
QUALIFICATION_SECONDS = 7200            # 每日达标时长（2小时，秒）

# ============================================================
# Field Mapping — single source of truth
# ============================================================
#   gain_diamond + send_gain_diamond → 主播薪资（档位判定 + 超档基数）
#   period_gain_coin                 → 公会长分成（档位判定 + 超档基数）
#
# These constants enable assertion checks that prevent field misuse.
FIELD_HOST = "gain_diamond + send_gain_diamond"
FIELD_PRESIDENT = "period_gain_coin (app_user_coin_detail)"

# The previous-cycle settlement cleanup is written immediately after a new
# cycle starts. It is not current-cycle commission income.
CYCLE_START_SETTLEMENT_WINDOW = timedelta(minutes=10)
CYCLE_START_SETTLEMENT_SOURCE_TYPE = 18
CYCLE_START_SETTLEMENT_OPTION_TYPE = 203
CYCLE_START_SETTLEMENT_REMARK = "host salary"

# ============================================================
# Enums
# ============================================================
POLICY_BIWEEKLY = 1
POLICY_LIBERAL = 2

REGION_ENGLISH = 0
REGION_MIDDLE_EAST = 2

ROLE_PRESIDENT = 0
ROLE_OPERATOR = 1
ROLE_HOST = 2


def get_conn():
    return pymysql.connect(**DB_CONFIG)


def floor2(d: Decimal) -> Decimal:
    """两位小数直接截断（非四舍五入）"""
    return d.quantize(Decimal("0.01"), rounding=ROUND_DOWN)


def dstr(v) -> Decimal:
    """安全构造 Decimal：仅接受 int/str/Decimal，拒绝 float"""
    if isinstance(v, float):
        raise TypeError(
            f"FLOAT_DETECTED: 禁止用 float 构造 Decimal (值={v})。请传入 str 或 int。"
        )
    return Decimal(str(v))


# ============================================================
# Settlement Period
# ============================================================
def get_settlement_period(ref_date: date):
    """
    结算周期：
      每月 1 号~15 号为上半月周期
      16 号~月末为下半月周期
    """
    day = ref_date.day
    if day <= 15:
        start = date(ref_date.year, ref_date.month, 1)
        end = date(ref_date.year, ref_date.month, 15)
    else:
        start = date(ref_date.year, ref_date.month, 16)
        _, last_day = calendar.monthrange(ref_date.year, ref_date.month)
        end = date(ref_date.year, ref_date.month, last_day)
    return start, end


# ============================================================
# User & Agency Data
# ============================================================
def fetch_user_data(user_id: int) -> dict:
    """
    查询用户账户、公会成员、公会信息。
    返回 None 表示用户不存在。
    """
    conn = get_conn()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(
                """
                SELECT a.user_id, a.gain_coin AS account_gain_coin,
                       a.gain_diamond, a.send_gain_diamond,
                       a.advance_salary_total_amount,
                       m.agency_id, m.role, m.settlement_policy_type AS member_policy,
                       m.join_time,
                       ag.settlement_policy_type AS agency_policy,
                       ag.region, ag.borrowed_amount
                FROM stay.app_user_account a
                LEFT JOIN stay.app_user_agency_member m
                  ON a.user_id = m.user_id AND m.status = 1
                LEFT JOIN stay.app_user_agency ag
                  ON m.agency_id = ag.agency_id AND ag.status = 1
                WHERE a.user_id = %s
                """,
                (user_id,),
            )
            row = cur.fetchone()
            if not row:
                return None

            # 政策类型优先级：成员级 → 公会级
            policy = row.get("member_policy") or row.get("agency_policy")
            return {
                "user_id": int(row["user_id"]),
                "account_gain_coin": int(row["account_gain_coin"] or 0),
                "gain_diamond": int(row["gain_diamond"] or 0),
                "send_gain_diamond": int(row["send_gain_diamond"] or 0),
                "advance_salary_total_amount": int(row["advance_salary_total_amount"] or 0),
                "agency_id": row.get("agency_id"),
                "role": row.get("role"),
                "policy": policy,
                "region": row.get("region"),
                "join_time": row.get("join_time"),
                "borrowed_amount": int(row.get("borrowed_amount") or 0),
            }
    finally:
        conn.close()


def is_cycle_start_settlement_cleanup(row: dict, period_start: datetime) -> bool:
    """Return whether a ledger row clears the prior cycle at cycle start."""
    create_time = row["create_time"]
    return (
        period_start <= create_time < period_start + CYCLE_START_SETTLEMENT_WINDOW
        and int(row["coin"] or 0) < 0
        and int(row["source_type"]) == CYCLE_START_SETTLEMENT_SOURCE_TYPE
        and int(row["option_type"]) == CYCLE_START_SETTLEMENT_OPTION_TYPE
        and row.get("remark") == CYCLE_START_SETTLEMENT_REMARK
    )


def summarize_period_gain_coin(rows: list[dict], period_start: datetime) -> dict:
    """Summarize current-period gain_coin while excluding prior-cycle cleanup."""
    raw_period_gain_coin = 0
    excluded_cycle_start_settlement_debit = 0
    included_record_count = 0
    excluded_record_count = 0

    for row in rows:
        coin = int(row["coin"] or 0)
        raw_period_gain_coin += coin
        if is_cycle_start_settlement_cleanup(row, period_start):
            excluded_cycle_start_settlement_debit += coin
            excluded_record_count += 1
        else:
            included_record_count += 1

    return {
        "period_gain_coin": raw_period_gain_coin - excluded_cycle_start_settlement_debit,
        "raw_period_gain_coin": raw_period_gain_coin,
        "excluded_cycle_start_settlement_debit": excluded_cycle_start_settlement_debit,
        "included_record_count": included_record_count,
        "excluded_record_count": excluded_record_count,
    }


def fetch_period_gain_coin(user_id: int, start: date, end: date) -> dict:
    """Fetch the current-cycle commission base from gain_coin ledger entries."""
    period_start = datetime.combine(start, time.min)
    period_end_exclusive = datetime.combine(end + timedelta(days=1), time.min)
    conn = get_conn()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(
                """
                SELECT coin, source_type, option_type, remark, create_time
                FROM stay.app_user_coin_detail
                WHERE user_id = %s
                  AND coin_type = 1
                  AND create_time >= %s
                  AND create_time < %s
                ORDER BY create_time, detail_id
                """,
                (user_id, period_start, period_end_exclusive),
            )
            return summarize_period_gain_coin(cur.fetchall(), period_start)
    finally:
        conn.close()


def fetch_tier_config(policy_type: int, region: int) -> list[dict]:
    """
    从 app_payer_salary_v2_config 实时查询档位配置。
    禁止硬编码档位值。
    """
    conn = get_conn()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(
                """
                SELECT `level`, diamonds, host_salary, agency_owner_salary,
                       host_tg_reward, agency_owner_tg_reward, excess_diamonds_rate
                FROM stay.app_payer_salary_v2_config
                WHERE settlement_policy_type = %s AND region = %s
                ORDER BY `level` ASC
                """,
                (policy_type, region),
            )
            return cur.fetchall()
    finally:
        conn.close()


def fetch_qualification_data(user_id: int, start: date, end: date) -> list[dict]:
    """查询结算周期内每日直播时长"""
    conn = get_conn()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(
                """
                SELECT dates, duration
                FROM stay.app_live_user_site_daily_summary
                WHERE user_id = %s
                  AND dates >= %s
                  AND dates <= %s
                ORDER BY dates ASC
                """,
                (user_id, start, end),
            )
            return cur.fetchall()
    finally:
        conn.close()


def fetch_borrow_data(user_id: int) -> dict:
    """
    从审计审批表查询借支数据（非 borrow_salary_log）。
    admin_content_official_coin_audit_detail 是权威数据源。
    """
    conn = get_conn()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(
                """
                SELECT SUM(COALESCE(borrow_salary_amount, 0)) AS total_borrow,
                       SUM(COALESCE(advance_salary_amount, 0)) AS total_advance_audit
                FROM stay.admin_content_official_coin_audit_detail
                WHERE user_id = %s AND status = 1
                """,
                (user_id,),
            )
            row = cur.fetchone()
            return {
                "total_borrow": int(row["total_borrow"] or 0),
                "total_advance_audit": int(row["total_advance_audit"] or 0),
            }
    finally:
        conn.close()


def fetch_audit_status(user_id: int) -> Optional[dict]:
    """从 app_user_flag 查询审核状态"""
    conn = get_conn()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(
                "SELECT audit_status, official FROM stay.app_user_flag WHERE user_id = %s",
                (user_id,),
            )
            return cur.fetchone()
    finally:
        conn.close()


# ============================================================
# Tier Resolution
# ============================================================
def resolve_tier(diamonds: int, tiers: list[dict]) -> Optional[dict]:
    """
    根据钻石数确定档位。
    返回 None 表示未达最低档位（Level 1）。
    """
    if not tiers:
        return None
    matched = None
    for t in tiers:
        if diamonds >= int(t["diamonds"]):
            matched = t
        else:
            break
    return matched


# ============================================================
# Assertion Guards
# ============================================================
def assert_field_usage(trace: dict) -> list[dict]:
    """
    验证所有字段使用符合映射规则。
    主播薪资必须用 gain_diamond，公会长分成必须用 gain_coin。
    """
    results = []
    rules = [
        ("host_tier_uses_gain_diamond", "主播档位判定",
         trace["host_tier_source"], FIELD_HOST, True),
        ("host_overtier_uses_gain_diamond", "主播超档计算",
         trace["host_overtier_source"], FIELD_HOST, True),
        ("president_tier_uses_gain_coin", "公会长档位判定",
         trace["president_tier_source"], FIELD_PRESIDENT, True),
        ("president_overtier_uses_gain_coin", "公会长超档计算",
         trace["president_overtier_source"], FIELD_PRESIDENT, True),
    ]
    for check_id, label, used, expected, must_match in rules:
        passed = (used == expected) if must_match else True
        results.append({
            "check": check_id,
            "label": label,
            "used_field": used,
            "expected_field": expected,
            "passed": passed,
        })
    return results


# ============================================================
# Core Calculation
# ============================================================
def calculate_host_salary(
    gain_diamond: int,
    tiers: list[dict],
    policy: int,
    penalty: bool,
) -> dict:
    """
    主播薪资计算（使用 gain_diamond）。
    - 档位判定 + 超档基数均基于 gain_diamond
    - 自由政策：超档 ×0.75
    - 双周政策：超档不乘系数（直接计为佣金）
    - 不合格惩罚：所有字段 ×0.7
    """
    diamonds = gain_diamond
    tier = resolve_tier(diamonds, tiers)
    is_below_min = tier is None

    if is_below_min:
        # 无门槛规则：未达最低档位 → 基础=0, TG=0, 超档从0起算
        tier_threshold = 0
        host_base = dstr("0.00")
        host_tg = dstr("0.00")
        tier_level = 0
    else:
        tier_threshold = int(tier["diamonds"])
        host_base = dstr(str(tier["host_salary"]))
        host_tg = dstr(str(tier["host_tg_reward"]))
        tier_level = int(tier["level"])

    over_diamonds = diamonds - tier_threshold

    if policy == POLICY_LIBERAL:
        denom = LIBERAL_DENOM
        over_units = dstr(over_diamonds) / denom
        commission = floor2(over_units * HOST_COMMISSION_RATE)
    else:  # POLICY_BIWEEKLY
        denom = BIWEEKLY_DENOM
        over_units = dstr(over_diamonds) / denom
        commission = floor2(over_units)  # 双周：不乘系数

    subtotal = floor2(host_base + commission + host_tg)

    penalty_applied = penalty  # 不合格惩罚适用所有字段（含未达档纯超档）
    if penalty:
        host_base = floor2(host_base * PENALTY_RATE)
        host_tg = floor2(host_tg * PENALTY_RATE)
        commission = floor2(commission * PENALTY_RATE)
        subtotal = floor2(host_base + commission + host_tg)

    return {
        "tier_level": tier_level,
        "tier_threshold": tier_threshold,
        "base_salary": float(host_base),
        "tg_reward": float(host_tg),
        "over_tier_diamonds": over_diamonds,
        "over_tier_units": float(floor2(over_units)),
        "over_tier_denominator": int(denom),
        "over_tier_commission": float(commission),
        "commission_rate": float(HOST_COMMISSION_RATE) if policy == POLICY_LIBERAL else 1.0,
        "penalty_applied": penalty_applied,
        "penalty_rate": float(PENALTY_RATE) if penalty_applied else None,
        "subtotal": float(subtotal),
        "total": float(subtotal),
        "calculation_field": FIELD_HOST,
    }


def calculate_president_share(
    gain_coin: int,
    tiers: list[dict],
    policy: int,
    penalty: bool,
) -> dict:
    """
    公会长分成计算（使用 gain_coin）。
    - 档位判定 + 超档基数均基于 gain_coin
    - 自由政策：超档 ×0.25
    - 双周政策：会长无超档佣金
    - 不合格惩罚：所有字段 ×0.7
    """
    coins = gain_coin
    tier = resolve_tier(coins, tiers)
    is_below_min = tier is None

    if is_below_min:
        tier_threshold = 0
        president_base = dstr("0.00")
        president_tg = dstr("0.00")
        tier_level = 0
    else:
        tier_threshold = int(tier["diamonds"])
        president_base = dstr(str(tier["agency_owner_salary"]))
        president_tg = dstr(str(tier["agency_owner_tg_reward"]))
        tier_level = int(tier["level"])

    over_coins = coins - tier_threshold

    if policy == POLICY_LIBERAL:
        denom = LIBERAL_DENOM
        over_units = dstr(over_coins) / denom
        commission = floor2(over_units * PRESIDENT_COMMISSION_RATE)
        total = floor2(president_base + commission + president_tg)
    else:  # POLICY_BIWEEKLY
        denom = BIWEEKLY_DENOM
        over_units = dstr(over_coins) / denom
        commission = dstr("0.00")  # 双周：会长无超档佣金
        total = floor2(president_base + president_tg)

    penalty_applied = penalty  # 不合格惩罚适用所有字段（含未达档纯超档）
    if penalty:
        president_base = floor2(president_base * PENALTY_RATE)
        president_tg = floor2(president_tg * PENALTY_RATE)
        commission = floor2(commission * PENALTY_RATE)
        total = floor2(president_base + commission + president_tg)

    return {
        "tier_level": tier_level,
        "tier_threshold": tier_threshold,
        "base_salary": float(president_base),
        "tg_reward": float(president_tg),
        "over_tier_coins": over_coins,
        "over_tier_units": float(floor2(over_units)),
        "over_tier_denominator": int(denom),
        "over_tier_commission": float(commission),
        "commission_rate": float(PRESIDENT_COMMISSION_RATE) if policy == POLICY_LIBERAL else 0.0,
        "penalty_applied": penalty_applied,
        "penalty_rate": float(PENALTY_RATE) if penalty_applied else None,
        "total": float(total),
        "calculation_field": FIELD_PRESIDENT,
    }


# ============================================================
# Qualification Check (Bi-weekly)
# ============================================================
def check_qualification(
    user_id: int,
    policy: int,
    join_time: Optional[datetime],
    period_start: date,
    period_end: date,
) -> dict:
    """
    双周政策达标判定：
    - 每日直播时长 ≥ 2 小时（7200秒）
    - 新成员（join_time 在当期周期内）免于惩罚
    - 自由政策默认达标
    """
    if policy == POLICY_LIBERAL:
        return {
            "policy": "liberal",
            "is_qualified": True,
            "is_new_member_exempt": False,
            "penalty_applies": False,
            "detail": "自由政策默认达标，不触发未达标罚则",
        }

    # Check new member exemption
    is_new_member = False
    if join_time:
        jt_date = join_time.date() if isinstance(join_time, datetime) else join_time
        if period_start <= jt_date <= period_end:
            is_new_member = True

    if is_new_member:
        return {
            "policy": "bi-weekly",
            "is_qualified": True,
            "is_new_member_exempt": True,
            "penalty_applies": False,
            "detail": f"新成员（加入时间 {join_time} 在当期结算周期内），免于惩罚",
        }

    # Check daily duration
    daily = fetch_qualification_data(user_id, period_start, period_end)
    if not daily:
        return {
            "policy": "bi-weekly",
            "is_qualified": False,
            "is_new_member_exempt": False,
            "penalty_applies": True,
            "detail": "无双周直播数据，判定为不合格",
            "daily_log": [],
        }

    qualified_days = 0
    total_days = 0
    daily_log = []
    for d in daily:
        day_str = str(d["dates"])
        dur = int(d["duration"] or 0)
        ok = dur >= QUALIFICATION_SECONDS
        if ok:
            qualified_days += 1
        total_days += 1
        daily_log.append({
            "date": day_str,
            "duration_seconds": dur,
            "threshold_seconds": QUALIFICATION_SECONDS,
            "qualified": ok,
        })

    is_qualified = qualified_days == total_days
    return {
        "policy": "bi-weekly",
        "is_qualified": is_qualified,
        "is_new_member_exempt": False,
        "penalty_applies": not is_qualified,
        "detail": (
            f"达标" if is_qualified
            else f"不合格 ({qualified_days}/{total_days} 天达标，需每日 ≥ 2 小时)"
        ),
        "daily_log": daily_log,
    }


# ============================================================
# Main Validator
# ============================================================
def validate_salary(user_id: int, ref_date: Optional[date] = None) -> dict:
    """
    对单个用户执行完整的薪资校验计算。
    返回结构化 JSON。
    """
    if ref_date is None:
        ref_date = date.today()

    period_start, period_end = get_settlement_period(ref_date)

    # ---- 1. Fetch user data ----
    user = fetch_user_data(user_id)
    if user is None:
        return {
            "error": f"用户 {user_id} 不存在",
            "user_id": user_id,
            "user_exists": False,
        }

    if user["policy"] is None:
        return {
            "error": f"用户 {user_id} 未配置结算政策类型",
            "user_id": user_id,
            "user_exists": True,
        }

    policy = user["policy"]
    region = user["region"]
    policy_label = {POLICY_BIWEEKLY: "bi-weekly", POLICY_LIBERAL: "liberal"}.get(policy, f"unknown({policy})")
    region_label = {REGION_ENGLISH: "english", REGION_MIDDLE_EAST: "middle_east"}.get(region, f"unknown({region})")

    # ---- 2. Fetch current-period commission base and tier config ----
    period_coin = fetch_period_gain_coin(user_id, period_start, period_end)
    tiers = fetch_tier_config(policy, region)

    # ---- 3. Qualification check ----
    qual = check_qualification(
        user_id, policy, user.get("join_time"), period_start, period_end
    )

    # ---- 4. Fetch borrow & audit data ----
    borrow = fetch_borrow_data(user_id)
    audit = fetch_audit_status(user_id)

    # ---- 5. Build field usage trace ----
    field_trace = {
        "host_tier_source": FIELD_HOST,
        "host_overtier_source": FIELD_HOST,
        "president_tier_source": FIELD_PRESIDENT,
        "president_overtier_source": FIELD_PRESIDENT,
    }

    # ---- 6. Calculate ----
    # 主播薪资：gain_diamond + send_gain_diamond
    host_result = calculate_host_salary(
        gain_diamond=user["gain_diamond"] + user["send_gain_diamond"],
        tiers=tiers,
        policy=policy,
        penalty=qual["penalty_applies"],
    )

    # 公会长分成：本期 period_gain_coin（独立档位判定）
    president_result = calculate_president_share(
        gain_coin=period_coin["period_gain_coin"],
        tiers=tiers,
        policy=policy,
        penalty=qual["penalty_applies"],
    )

    # ---- 7. Compute totals ----
    host_total = dstr(str(host_result["total"]))
    president_total = dstr(str(president_result["total"]))
    gross_income = floor2(host_total + president_total)

    advance_salary = user["advance_salary_total_amount"]
    net_income = floor2(gross_income - dstr(advance_salary))

    # ---- 8. Run assertions ----
    assertions = assert_field_usage(field_trace)

    # ---- 9. Assemble result ----
    return {
        "user_id": user_id,
        "user_exists": True,
        "calculation_time": datetime.now().isoformat(),
        "period": {
            "start": period_start.isoformat(),
            "end": period_end.isoformat(),
        },
        "input_data": {
            "account_gain_coin": user["account_gain_coin"],
            "period_gain_coin": period_coin["period_gain_coin"],
            "raw_period_gain_coin": period_coin["raw_period_gain_coin"],
            "excluded_cycle_start_settlement_debit": period_coin[
                "excluded_cycle_start_settlement_debit"
            ],
            "period_gain_coin_included_record_count": period_coin["included_record_count"],
            "period_gain_coin_excluded_record_count": period_coin["excluded_record_count"],
            "gain_diamond": user["gain_diamond"],
            "send_gain_diamond": user["send_gain_diamond"],
            "host_diamond_base": user["gain_diamond"] + user["send_gain_diamond"],
            "policy_type": policy_label,
            "policy_type_code": policy,
            "region": region_label,
            "region_code": region,
            "role": user["role"],
            "role_label": {0: "公会长", 1: "运营", 2: "主播"}.get(user["role"], "unknown"),
            "agency_id": user["agency_id"],
            "advance_salary_total_amount": advance_salary,
            "agency_borrowed_amount": user["borrowed_amount"],
            "audit_borrow_amount": borrow["total_borrow"],
            "audit_advance_amount": borrow["total_advance_audit"],
            "audit_status": audit["audit_status"] if audit else None,
            "join_time": user["join_time"].isoformat() if user.get("join_time") else None,
        },
        "tier_config": [
            {
                "level": int(t["level"]),
                "diamonds": int(t["diamonds"]),
                "host_salary": float(t["host_salary"]),
                "agency_owner_salary": float(t["agency_owner_salary"]),
                "host_tg_reward": float(t["host_tg_reward"]),
                "agency_owner_tg_reward": float(t["agency_owner_tg_reward"]),
            }
            for t in tiers
        ],
        "field_usage_trace": field_trace,
        "assertions": assertions,
        "all_assertions_passed": all(a["passed"] for a in assertions),
        "qualification": qual,
        "host_salary": host_result,
        "president_share": president_result,
        "totals": {
            "host_salary": float(host_total),
            "president_share": float(president_total),
            "gross_income": float(gross_income),
            "advance_salary_deduction": advance_salary,
            "net_income": float(net_income),
        },
    }


# ============================================================
# CLI
# ============================================================
def main():
    if len(sys.argv) < 2:
        print("Usage: python salary_validator.py <user_id> [--date YYYY-MM-DD] [--pretty]", file=sys.stderr)
        sys.exit(1)

    try:
        user_id = int(sys.argv[1])
    except ValueError:
        print(f"Error: user_id must be an integer, got '{sys.argv[1]}'", file=sys.stderr)
        sys.exit(1)

    ref_date = date.today()
    pretty = False
    for i, arg in enumerate(sys.argv[2:], start=2):
        if arg == "--date" and i + 1 < len(sys.argv):
            try:
                ref_date = datetime.strptime(sys.argv[i + 1], "%Y-%m-%d").date()
            except ValueError:
                print(f"Error: invalid date '{sys.argv[i+1]}', use YYYY-MM-DD", file=sys.stderr)
                sys.exit(1)
        elif arg == "--pretty":
            pretty = True

    result = validate_salary(user_id, ref_date)

    if pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    else:
        print(json.dumps(result, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
