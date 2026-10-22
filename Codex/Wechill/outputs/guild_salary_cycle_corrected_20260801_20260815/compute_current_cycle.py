import json
import sys
from datetime import datetime
from decimal import Decimal, ROUND_DOWN
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "Payroll" / "scripts"))
from salary_validator import get_conn


PERIOD_START = datetime(2026, 8, 1, 0, 0, 0)
PERIOD_END_EXCLUSIVE = datetime(2026, 8, 16, 0, 0, 0)
FREE_DENOM = Decimal("16026")
BIWEEKLY_DENOM = Decimal("25000")
PENALTY = Decimal("0.70")


def floor2(value):
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_DOWN)


def to_decimal(value):
    return Decimal(str(value or 0))


def find_tier(amount, tiers):
    matched = None
    for tier in tiers:
        if amount >= int(tier["diamonds"]):
            matched = tier
        else:
            break
    return matched


def phone(area_code, phone_number):
    area = (area_code or "").strip()
    number = (phone_number or "").strip()
    if area and number:
        return f"+{area} {number}"
    return number or ""


def calculate_member(member, tiers_by_key):
    policy = int(member["member_policy"])
    region = int(member["region"])
    is_biweekly = policy == 1
    tiers = tiers_by_key[(policy, region)]
    host_base_value = int(member["host_diamond_base"])
    president_base_value = int(member["period_gain_coin"])

    if is_biweekly:
        join_time = member["join_time"]
        qualified = (
            join_time is not None and join_time > PERIOD_START
        ) or (
            int(member["effective_days"] or 0) >= 6
            and to_decimal(member["total_hours"]) >= Decimal("12")
        )
        ratio = Decimal("1.00") if qualified else PENALTY
    else:
        ratio = Decimal("1.00")

    host_tier = find_tier(host_base_value, tiers)
    if host_tier is None:
        host_threshold = Decimal("0")
        host_fixed = Decimal("0")
        host_tg = Decimal("0")
    else:
        host_threshold = to_decimal(host_tier["diamonds"])
        host_fixed = to_decimal(host_tier["host_salary"])
        host_tg = to_decimal(host_tier["host_tg_reward"])
    host_over = Decimal(host_base_value) - host_threshold
    host_denom = BIWEEKLY_DENOM if is_biweekly else FREE_DENOM
    host_commission = floor2(host_over / host_denom)
    if not is_biweekly:
        host_commission = floor2(host_commission * Decimal("0.75"))
    host_salary = floor2((host_fixed + host_commission) * ratio)
    host_tg_paid = floor2(host_tg * ratio)
    host_total = floor2((host_fixed + host_commission + host_tg) * ratio)

    president_tier = find_tier(president_base_value, tiers)
    if president_tier is None:
        president_threshold = Decimal("0")
        president_fixed = Decimal("0")
        president_tg = Decimal("0")
    else:
        president_threshold = to_decimal(president_tier["diamonds"])
        president_fixed = to_decimal(president_tier["agency_owner_salary"])
        president_tg = to_decimal(president_tier["agency_owner_tg_reward"])
    president_over = Decimal(president_base_value) - president_threshold
    if is_biweekly:
        president_commission = Decimal("0")
    else:
        president_commission = floor2((president_over / FREE_DENOM) * Decimal("0.25"))
    president_total = floor2((president_fixed + president_commission + president_tg) * ratio)
    advance = to_decimal(member["advance_salary_total_amount"])

    return {
        "host_tier": int(host_tier["level"]) if host_tier else 0,
        "president_tier": int(president_tier["level"]) if president_tier else 0,
        "salary_ratio": str(ratio),
        "host_salary": str(host_salary),
        "host_tg_reward": str(host_tg_paid),
        "host_total_salary": str(host_total),
        "president_commission": str(president_total),
        "member_total_salary": str(floor2(host_total + president_total)),
        "advance_salary": str(advance),
        "member_salary_balance": str(floor2(host_total + president_total - advance)),
    }


def fetch_rows():
    query = """
    WITH period_coin AS (
      SELECT d.user_id,
        SUM(d.coin) AS raw_period_gain_coin,
        SUM(CASE WHEN d.source_type = 18 AND d.option_type = 203
                       AND d.remark = 'host salary' AND d.coin < 0
                       AND d.create_time >= '2026-08-01 00:00:00'
                       AND d.create_time < '2026-08-01 00:10:00'
                 THEN d.coin ELSE 0 END) AS excluded_cycle_start_settlement_debit,
        SUM(CASE WHEN d.source_type = 18 AND d.option_type = 203
                       AND d.remark = 'host salary' AND d.coin < 0
                       AND d.create_time >= '2026-08-01 00:00:00'
                       AND d.create_time < '2026-08-01 00:10:00'
                 THEN 0 ELSE d.coin END) AS period_gain_coin,
        COUNT(*) AS coin_record_count
      FROM stay.app_user_coin_detail d
      WHERE d.coin_type = 1
        AND d.create_time >= '2026-08-01 00:00:00'
        AND d.create_time < '2026-08-16 00:00:00'
      GROUP BY d.user_id
    ), attendance AS (
      SELECT user_id,
        SUM(CASE WHEN duration >= 7200 THEN 1 ELSE 0 END) AS effective_days,
        ROUND(SUM(duration) / 3600, 2) AS total_hours
      FROM stay.app_live_user_site_daily_summary
      WHERE dates >= '2026-08-01 00:00:00'
        AND dates < '2026-08-16 00:00:00'
      GROUP BY user_id
    )
    SELECT ag.agency_id, ag.agency_name, ag.region, ag.owner_user_id,
      owner_u.user_number AS owner_user_number,
      owner_u.area_code AS owner_area_code, owner_u.phone_number AS owner_phone_number,
      ag.borrowed_amount AS agency_borrowed_amount, ag.borrowable_amount,
      m.user_id, u.user_number, u.nickname, m.role,
      COALESCE(m.settlement_policy_type, ag.settlement_policy_type) AS member_policy,
      m.join_time, COALESCE(a.gain_diamond, 0) AS gain_diamond,
      COALESCE(a.send_gain_diamond, 0) AS send_gain_diamond,
      COALESCE(a.gain_diamond, 0) + COALESCE(a.send_gain_diamond, 0) AS host_diamond_base,
      COALESCE(a.advance_salary_total_amount, 0) AS advance_salary_total_amount,
      COALESCE(pc.raw_period_gain_coin, 0) AS raw_period_gain_coin,
      COALESCE(pc.excluded_cycle_start_settlement_debit, 0) AS excluded_cycle_start_settlement_debit,
      COALESCE(pc.period_gain_coin, 0) AS period_gain_coin,
      COALESCE(pc.coin_record_count, 0) AS coin_record_count,
      COALESCE(att.effective_days, 0) AS effective_days,
      COALESCE(att.total_hours, 0) AS total_hours
    FROM stay.app_user_agency ag
    JOIN stay.app_user_agency_member m ON m.agency_id = ag.agency_id AND m.status = 1
    JOIN stay.app_user u ON u.user_id = m.user_id
    JOIN stay.app_user_account a ON a.user_id = m.user_id
    LEFT JOIN stay.app_user owner_u ON owner_u.user_id = ag.owner_user_id
    LEFT JOIN period_coin pc ON pc.user_id = m.user_id
    LEFT JOIN attendance att ON att.user_id = m.user_id
    WHERE ag.status = 1
      AND (COALESCE(a.gain_diamond, 0) + COALESCE(a.send_gain_diamond, 0) > 0
           OR COALESCE(pc.period_gain_coin, 0) > 0)
    ORDER BY ag.agency_id, m.user_id
    """
    tier_query = """
    SELECT settlement_policy_type, region, `level`, diamonds, host_salary,
      agency_owner_salary, host_tg_reward, agency_owner_tg_reward, excess_diamonds_rate
    FROM stay.app_payer_salary_v2_config
    WHERE settlement_policy_type IN (1, 2) AND region IN (0, 2)
    ORDER BY settlement_policy_type, region, `level`
    """
    conn = get_conn()
    try:
        import pymysql
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(query)
            rows = cur.fetchall()
            cur.execute(tier_query)
            tiers = cur.fetchall()
        return rows, tiers
    finally:
        conn.close()


def main():
    rows, tier_rows = fetch_rows()
    tiers_by_key = {}
    for tier in tier_rows:
        tiers_by_key.setdefault((int(tier["settlement_policy_type"]), int(tier["region"])), []).append(tier)

    seen_users = set()
    members = []
    for row in rows:
        if row["user_id"] in seen_users:
            raise ValueError(f"duplicate active user_id: {row['user_id']}")
        seen_users.add(row["user_id"])
        result = calculate_member(row, tiers_by_key)
        if Decimal(result["member_total_salary"]) <= 0:
            continue
        members.append({
            "agency_id": int(row["agency_id"]),
            "agency_name": row["agency_name"],
            "region": "English" if int(row["region"]) == 0 else "Middle East",
            "region_code": int(row["region"]),
            "owner_user_number": str(row["owner_user_number"]),
            "owner_phone": phone(row["owner_area_code"], row["owner_phone_number"]),
            "agency_borrowed_amount": str(to_decimal(row["agency_borrowed_amount"])),
            "borrowable_amount": str(to_decimal(row["borrowable_amount"])),
            "user_id": int(row["user_id"]),
            "user_number": str(row["user_number"]),
            "nickname": row["nickname"] or "",
            "role": {0: "Owner", 1: "Operator", 2: "Host"}.get(int(row["role"]), f"Role {row['role']}"),
            "policy": "Bi-weekly" if int(row["member_policy"]) == 1 else "Free",
            "host_diamond_base": int(row["host_diamond_base"]),
            "raw_period_gain_coin": int(row["raw_period_gain_coin"]),
            "excluded_cycle_start_settlement_debit": int(row["excluded_cycle_start_settlement_debit"]),
            "period_gain_coin": int(row["period_gain_coin"]),
            "coin_record_count": int(row["coin_record_count"]),
            "effective_days": int(row["effective_days"]),
            "total_hours": str(to_decimal(row["total_hours"])),
            **result,
        })

    output = {
        "period_start": "2026-08-01 00:00:00",
        "period_end_exclusive": "2026-08-16 00:00:00",
        "members": members,
        "member_count": len(members),
        "agency_count": len({m["agency_id"] for m in members}),
    }
    target = Path(__file__).with_name("salary_data.json")
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"member_count": output["member_count"], "agency_count": output["agency_count"]}))


if __name__ == "__main__":
    main()
