from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import mysql.connector


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


PROJECT_ROOT = Path(__file__).resolve().parents[4]
TABLES = (
    "guild.guild_info",
    "guild.guild_member",
    "app.ln_user",
    "guild.guild_salary_detail",
    "guild.guild_settlement_bill",
    "guild.guild_salary_detail_weekly",
    "guild.guild_settlement_bill_weekly",
    "guild.guild_balance_pool",
)


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def normalize(value: object) -> object:
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, datetime):
        return value.isoformat(sep=" ")
    if isinstance(value, date):
        return value.isoformat()
    return value


def fetch(cursor) -> list[dict[str, object]]:
    names = [column[0] for column in cursor.description]
    return [dict(zip(names, (normalize(value) for value in row))) for row in cursor.fetchall()]


def money(row: dict[str, object], *fields: str) -> Decimal:
    return sum((Decimal(str(row.get(field) or 0)) for field in fields), Decimal("0"))


def source_name(row: dict[str, object]) -> str:
    if not row["settlement_bill_id"]:
        return "realtime"
    return "settled_snapshot" if row["settle_status"] == 2 else "unconfirmed_settlement_bill"


def is_settled_snapshot(row: dict[str, object]) -> bool:
    return bool(row["settlement_bill_id"]) and row["settle_status"] == 2


def connection_settings(env: dict[str, str], environment: str) -> dict[str, object]:
    prefix = "" if environment == "test" else "PROD_"
    required = (
        f"{prefix}MYSQL_HOST",
        f"{prefix}MYSQL_PORT",
        f"{prefix}MYSQL_USER",
        f"{prefix}MYSQL_PASSWORD",
        f"{prefix}MYSQL_DATABASE",
    )
    missing = [key for key in required if not env.get(key)]
    if missing:
        raise SystemExit(
            f"{environment} database configuration is incomplete: {', '.join(missing)}"
        )
    if environment == "test" and env.get("APP_ENV") != "test":
        raise SystemExit("APP_ENV is not test; refusing salary query")
    if environment == "production" and env.get("PROD_MYSQL_READ_ONLY", "").lower() not in {
        "1",
        "true",
        "yes",
    }:
        raise SystemExit("PROD_MYSQL_READ_ONLY must be true for production salary queries")
    return {
        "host": env[f"{prefix}MYSQL_HOST"],
        "port": int(env[f"{prefix}MYSQL_PORT"]),
        "user": env[f"{prefix}MYSQL_USER"],
        "password": env[f"{prefix}MYSQL_PASSWORD"],
        "database": env[f"{prefix}MYSQL_DATABASE"],
        "connection_timeout": 20,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--guild-no", type=int)
    scope.add_argument("--user-no")
    parser.add_argument("--month", default=date.today().strftime("%Y-%m"))
    parser.add_argument(
        "--environment",
        choices=("test", "production"),
        default="test",
        help="database environment; defaults to test",
    )
    parser.add_argument(
        "--confirm-production",
        action="store_true",
        help="required together with --environment production",
    )
    parser.add_argument("--include-schema", action="store_true")
    args = parser.parse_args()
    if args.environment == "production" and not args.confirm_production:
        raise SystemExit(
            "production salary queries require --confirm-production"
        )
    try:
        month_start = date.fromisoformat(f"{args.month}-01")
    except ValueError as error:
        raise SystemExit("--month must use YYYY-MM") from error
    next_month = date(month_start.year + (month_start.month == 12), month_start.month % 12 + 1, 1)

    env = load_env(PROJECT_ROOT / ".env")
    settings = connection_settings(env, args.environment)
    connection = mysql.connector.connect(**settings)
    try:
        cursor = connection.cursor()
        if args.environment == "production":
            cursor.execute("SET SESSION TRANSACTION READ ONLY")
        schema_columns: dict[str, list[str]] = {}
        for table in TABLES:
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            schema_columns[table] = [row[0] for row in cursor.fetchall()]

        target_member_id: object | None = None
        target_user: dict[str, object] | None = None
        if args.guild_no is not None:
            cursor.execute(
                "SELECT id, guild_no, guild_name, owner_user_id, guild_status "
                "FROM guild.guild_info WHERE guild_no=%s",
                (args.guild_no,),
            )
            guilds = fetch(cursor)
            if len(guilds) != 1:
                raise SystemExit(f"guild_no resolved to {len(guilds)} rows")
            guild = guilds[0]
            guild_id = guild["id"]

            cursor.execute(
                """
                SELECT gm.id AS member_id, gm.user_id, u.user_no, gm.member_role,
                       gm.member_status, gm.policy_type, gm.joined_at, gm.left_at
                FROM guild.guild_member gm
                LEFT JOIN app.ln_user u ON u.user_id=gm.user_id
                WHERE gm.guild_id=%s
                ORDER BY gm.member_status, gm.member_role, gm.id
                """,
                (guild_id,),
            )
            members = fetch(cursor)
        else:
            cursor.execute(
                "SELECT user_id, user_no FROM app.ln_user WHERE user_no=%s",
                (args.user_no,),
            )
            users = fetch(cursor)
            if len(users) != 1:
                raise SystemExit(f"user_no resolved to {len(users)} rows in app.ln_user")
            target_user = users[0]

            cursor.execute(
                """
                SELECT gm.id AS member_id, gm.user_id, u.user_no, gm.member_role,
                       gm.member_status, gm.policy_type, gm.joined_at, gm.left_at,
                       gi.id AS guild_id, gi.guild_no, gi.guild_name,
                       gi.owner_user_id, gi.guild_status
                FROM guild.guild_member gm
                JOIN guild.guild_info gi ON gi.id=gm.guild_id
                LEFT JOIN app.ln_user u ON u.user_id=gm.user_id
                WHERE gm.user_id=%s AND gm.member_status=2
                ORDER BY gm.id
                """,
                (target_user["user_id"],),
            )
            members = fetch(cursor)
            if len(members) != 1:
                raise SystemExit(
                    f"user_no resolved to {len(members)} active guild memberships"
                )
            member = members[0]
            target_member_id = member["member_id"]
            guild_id = member["guild_id"]
            guild = {
                "id": guild_id,
                "guild_no": member["guild_no"],
                "guild_name": member["guild_name"],
                "owner_user_id": member["owner_user_id"],
                "guild_status": member["guild_status"],
            }

        active_member_rows = [
            row for row in members if row["member_status"] == 2
        ]
        active_user_ids = [row["user_id"] for row in active_member_rows]
        balance_rows: list[dict[str, object]] = []
        if active_user_ids:
            placeholders = ",".join(["%s"] * len(active_user_ids))
            cursor.execute(
                f"""
                SELECT user_id, pool_type, available_amount, frozen_amount,
                       pool_status
                FROM guild.guild_balance_pool
                WHERE user_id IN ({placeholders}) AND pool_status=1
                ORDER BY user_id, pool_type
                """,
                tuple(active_user_ids),
            )
            balance_rows = fetch(cursor)

        pool_names = {
            1: "个人薪资余额池",
            2: "金币工资余额池",
            3: "主播转入薪资余额池",
        }
        balances_by_user: dict[object, list[dict[str, object]]] = {}
        for row in balance_rows:
            balances_by_user.setdefault(row["user_id"], []).append(row)

        member_filter = " AND sd.member_id=%s" if target_member_id is not None else ""
        monthly_params: tuple[object, ...] = (guild_id, args.month)
        weekly_params: tuple[object, ...] = (guild_id, month_start, next_month)
        if target_member_id is not None:
            monthly_params += (target_member_id,)
            weekly_params += (target_member_id,)

        cursor.execute(
            """
            SELECT sd.id, sd.member_id, sd.user_id, u.user_no, sd.bill_owner_type,
                   sd.policy_type, sd.settlement_month, sd.settlement_bill_id,
                   sb.settle_status, sd.non_coin_reward_amount, sd.coin_reward_amount,
                   sd.guild_coin_reward_amount, sd.total_salary_amount,
                   sd.anchor_base_salary_amount, sd.anchor_tc_reward_amount,
                   sd.advance_deduction_amount, sd.valid_diamond_amount_total,
                   sd.valid_diamond_balance_amount, sd.calc_status, sd.calculated_at
            FROM guild.guild_salary_detail sd
            LEFT JOIN app.ln_user u ON u.user_id=sd.user_id
            LEFT JOIN guild.guild_settlement_bill sb ON sb.id=sd.settlement_bill_id
            WHERE sd.guild_id=%s AND sd.settlement_month=%s AND sd.policy_type IN (1,2)
            """
            + member_filter
            + """
            ORDER BY sd.bill_owner_type, sd.member_id, sd.id
            """,
            monthly_params,
        )
        monthly = fetch(cursor)

        cursor.execute(
            """
            SELECT sd.id, sd.period_start, sd.member_id, sd.user_id, u.user_no,
                   sd.bill_owner_type, sd.policy_type, sd.settlement_bill_id,
                   sb.settle_status, sd.non_coin_reward_amount, sd.coin_reward_amount,
                   sd.guild_coin_reward_amount, sd.total_salary_amount,
                   sd.anchor_base_salary_amount, sd.anchor_tc_reward_amount,
                   sd.advance_deduction_amount, sd.valid_diamond_amount_total,
                   sd.valid_diamond_balance_amount, sd.calc_status, sd.calculated_at
            FROM guild.guild_salary_detail_weekly sd
            LEFT JOIN app.ln_user u ON u.user_id=sd.user_id
            LEFT JOIN guild.guild_settlement_bill_weekly sb ON sb.id=sd.settlement_bill_id
            WHERE sd.guild_id=%s AND sd.policy_type=3
              AND sd.period_start >= %s AND sd.period_start < %s
            """
            + member_filter
            + """
            ORDER BY sd.period_start, sd.bill_owner_type, sd.member_id, sd.id
            """,
            weekly_params,
        )
        weekly = fetch(cursor)

        active_anchors = {
            row["member_id"]: row
            for row in members
            if row["member_status"] == 2
        }
        summary: dict[object, dict[str, object]] = {
            key: {
                "user_no": row["user_no"],
                "role": "主播" if row["member_role"] == 1 else "公会长",
                "policy_type": row["policy_type"],
                "monthly_salary": Decimal("0"),
                "weekly_salary": Decimal("0"),
                "weekly_settled_salary": Decimal("0"),
                "sources": [],
                "withdrawable_balance": Decimal("0"),
            }
            for key, row in active_anchors.items()
        }
        for row in monthly + weekly:
            if row["bill_owner_type"] != 1:
                continue
            if row["member_id"] not in summary:
                summary[row["member_id"]] = {
                    "user_no": row["user_no"],
                    "role": "主播",
                    "policy_type": row["policy_type"],
                    "monthly_salary": Decimal("0"),
                    "weekly_salary": Decimal("0"),
                    "weekly_settled_salary": Decimal("0"),
                    "sources": [],
                    "withdrawable_balance": Decimal("0"),
                }
            item = summary[row["member_id"]]
            total = money(row, "non_coin_reward_amount", "coin_reward_amount")
            if "period_start" in row:
                if is_settled_snapshot(row):
                    item["weekly_settled_salary"] += total
                else:
                    item["weekly_salary"] += total
                source = source_name(row)
                item["sources"].append(f"weekly:{row['period_start']}:{source}")
            else:
                item["monthly_salary"] += total
                item["sources"].append(
                    f"monthly:{source_name(row)}"
                )

        monthly_anchor_total = sum(
            (money(row, "non_coin_reward_amount", "coin_reward_amount")
             for row in monthly if row["bill_owner_type"] == 1),
            Decimal("0"),
        )
        weekly_anchor_total = sum(
            (money(row, "non_coin_reward_amount", "coin_reward_amount")
             for row in weekly
             if row["bill_owner_type"] == 1 and not is_settled_snapshot(row)),
            Decimal("0"),
        )
        monthly_owner_total = sum(
            (money(row, "total_salary_amount", "guild_coin_reward_amount")
             for row in monthly
             if row["bill_owner_type"] == 2 and row["member_id"] != 0),
            Decimal("0"),
        )
        weekly_owner_total = sum(
            (money(row, "total_salary_amount", "guild_coin_reward_amount")
             for row in weekly
             if row["bill_owner_type"] == 2
             and row["member_id"] != 0
             and not is_settled_snapshot(row)),
            Decimal("0"),
        )
        anchor_total = monthly_anchor_total + weekly_anchor_total
        owner_total = monthly_owner_total + weekly_owner_total
        role_by_user = {
            row["user_id"]: ("主播" if row["member_role"] == 1 else "公会长")
            for row in members
            if row["member_status"] == 2
        }

        monthly_owner_by_member = {
            row["member_id"]: row
            for row in monthly
            if row["bill_owner_type"] == 2 and row["member_id"] != 0
        }
        weekly_owner_by_member_period = {
            (row["member_id"], row["period_start"]): row
            for row in weekly
            if row["bill_owner_type"] == 2 and row["member_id"] != 0
        }

        def detail(
            row: dict[str, object], period_type: str, owner_row: dict[str, object] | None
        ) -> dict[str, object]:
            source = source_name(row)
            owner_management = money(
                owner_row or {}, "total_salary_amount", "guild_coin_reward_amount"
            )
            ordinary_components = row["policy_type"] == 1
            return {
                "user_no": row["user_no"],
                "role": role_by_user.get(row["user_id"], "主播"),
                "policy_type": row["policy_type"],
                "period_type": period_type,
                "period": row.get("period_start", args.month),
                "valid_diamond_amount_total": row["valid_diamond_amount_total"],
                "valid_diamond_balance_amount": row["valid_diamond_balance_amount"],
                "non_coin_reward_amount": row["non_coin_reward_amount"],
                "coin_reward_amount": row["coin_reward_amount"],
                "anchor_base_salary_amount": (
                    row["anchor_base_salary_amount"] if ordinary_components else "--"
                ),
                "anchor_tc_reward_amount": (
                    row["anchor_tc_reward_amount"] if ordinary_components else "--"
                ),
                "owner_management_salary": format(owner_management, "f"),
                "total_salary": format(
                    money(row, "non_coin_reward_amount", "coin_reward_amount"), "f"
                ),
                "advance_deduction_amount": row["advance_deduction_amount"],
                "salary_balance": format(
                    money(row, "non_coin_reward_amount", "coin_reward_amount")
                    - Decimal(str(row["advance_deduction_amount"] or 0)),
                    "f",
                ),
                "source": source,
                "settle_status": row["settle_status"],
            }

        salary_details = {
            "monthly": [
                detail(row, "monthly", owner_row)
                for row in monthly
                if row["bill_owner_type"] == 1
                for owner_row in [monthly_owner_by_member.get(row["member_id"])]
            ],
            "weekly": [
                detail(row, "weekly", owner_row)
                for row in weekly
                if row["bill_owner_type"] == 1
                for owner_row in [
                    weekly_owner_by_member_period.get((row["member_id"], row["period_start"]))
                ]
            ],
        }
        for item in summary.values():
            balance_items = balances_by_user.get(
                next(
                    (
                        row["user_id"]
                        for row in active_member_rows
                        if row["user_no"] == item["user_no"]
                    ),
                    None,
                ),
                [],
            )
            item["withdrawable_balance"] = format(
                sum(
                    (Decimal(str(row["available_amount"] or 0)) for row in balance_items),
                    Decimal("0"),
                ),
                "f",
            )
            item["monthly_salary"] = format(item["monthly_salary"], "f")
            item["weekly_salary"] = format(item["weekly_salary"], "f")
            item["weekly_settled_salary"] = format(item["weekly_settled_salary"], "f")
            item["total_salary"] = format(
                Decimal(item["monthly_salary"]) + Decimal(item["weekly_salary"]), "f"
            )
            item["status"] = "has_salary_detail" if item["sources"] else "no_salary_detail"

        balances = []
        for member in active_member_rows:
            items = balances_by_user.get(member["user_id"], [])
            balances.append(
                {
                    "user_no": member["user_no"],
                    "role": "主播" if member["member_role"] == 1 else "公会长",
                    "pools": [
                        {
                            "pool_type": row["pool_type"],
                            "pool_name": pool_names.get(row["pool_type"], "未知余额池"),
                            "available_amount": row["available_amount"],
                            "frozen_amount": row["frozen_amount"],
                        }
                        for row in items
                    ],
                    "withdrawable_balance": format(
                        sum(
                            (Decimal(str(row["available_amount"] or 0)) for row in items),
                            Decimal("0"),
                        ),
                        "f",
                    ),
                    "balance_status": "has_balance_pool" if items else "no_balance_pool_record",
                }
            )

        members_for_output = list(summary.values())
        monthly_members = [item for item in members_for_output if item["policy_type"] in (1, 2)]
        weekly_members = [item for item in members_for_output if item["policy_type"] == 3]

        output = {
            "environment": args.environment,
            "read_only": args.environment == "production",
            "query_scope": "user" if target_user else "guild",
            "month": args.month,
            "guild": guild,
            "active_member_count": sum(1 for row in members if row["member_status"] == 2),
            "monthly_row_count": len(monthly),
            "weekly_row_count": len(weekly),
            "monthly_members": monthly_members,
            "weekly_members": weekly_members,
            "salary_details": salary_details,
            "balances": balances,
            "anchors": members_for_output,
            "period_totals": {
                "monthly": {
                    "anchor_salary": format(monthly_anchor_total, "f"),
                    "owner_management_salary": format(monthly_owner_total, "f"),
                    "guild_salary": format(monthly_anchor_total + monthly_owner_total, "f"),
                },
                "weekly": {
                    "anchor_salary": format(weekly_anchor_total, "f"),
                    "owner_management_salary": format(weekly_owner_total, "f"),
                    "guild_salary": format(weekly_anchor_total + weekly_owner_total, "f"),
                },
            },
            "totals": {
                "anchor_salary": format(anchor_total, "f"),
                "owner_management_salary": format(owner_total, "f"),
                "guild_salary": format(anchor_total + owner_total, "f"),
            },
            "abnormal": [
                "no weekly policy_type=3 rows in month" if not weekly else None,
                "active weekly anchor without salary detail"
                if any(item["policy_type"] == 3 and not item["sources"] for item in summary.values())
                else None,
            ],
        }
        if target_user:
            output["target_user"] = {"user_no": target_user["user_no"]}
        if args.include_schema:
            output["schema_columns"] = schema_columns
        output["abnormal"] = [item for item in output["abnormal"] if item]
        print(json.dumps(output, ensure_ascii=False, indent=2))
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
