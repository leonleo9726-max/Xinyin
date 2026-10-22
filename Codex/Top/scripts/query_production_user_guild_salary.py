from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
import sys

import mysql.connector


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_TABLES = (
    "app.ln_user",
    "guild.guild_info",
    "guild.guild_member",
    "guild.guild_salary_detail",
    "guild.guild_settlement_bill",
)


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def load_env(path: Path) -> dict[str, str]:
    settings: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        settings[key.strip()] = value.strip().strip('"').strip("'")
    return settings


def normalize(value: object) -> object:
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, (date, datetime)):
        return value.isoformat(sep=" ")
    return value


def fetch_rows(cursor: mysql.connector.cursor.MySQLCursor) -> list[dict[str, object]]:
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def print_rows(label: str, rows: list[dict[str, object]], preview_limit: int = 3) -> None:
    columns = list(rows[0]) if rows else []
    print(f"{label}_COLUMNS: {','.join(columns)}")
    print(f"{label}_ROW_COUNT: {len(rows)}")
    for row in rows[:preview_limit]:
        print(f"{label}_ROW: {repr({key: normalize(value) for key, value in row.items()})}")


def data_source(settlement_bill_id: object, settle_status: object) -> str:
    if not settlement_bill_id:
        return "realtime"
    if settle_status == 2:
        return "settled_snapshot"
    return "unconfirmed_settlement_bill"


def amount(value: object) -> Decimal:
    return Decimal(str(value or 0))


def print_monthly_summary(rows: list[dict[str, object]]) -> None:
    summary: dict[tuple[object, object, object, object], dict[str, Decimal]] = defaultdict(
        lambda: {"anchor_total": Decimal(), "owner_non_coin": Decimal(), "owner_coin": Decimal()}
    )
    for row in rows:
        key = (
            row["settlement_month"],
            row["guild_no"],
            row["bill_owner_type"],
            data_source(row["settlement_bill_id"], row["settle_status"]),
        )
        if row["bill_owner_type"] == 1:
            summary[key]["anchor_total"] += amount(row["non_coin_reward_amount"]) + amount(
                row["coin_reward_amount"]
            )
        else:
            summary[key]["owner_non_coin"] += amount(row["total_salary_amount"])
            summary[key]["owner_coin"] += amount(row["guild_coin_reward_amount"])

    print("MONTHLY_SUMMARY_COLUMNS: settlement_month,guild_no,bill_owner_type,data_source,anchor_total,owner_non_coin,owner_coin")
    print(f"MONTHLY_SUMMARY_ROW_COUNT: {len(summary)}")
    for key in sorted(summary, reverse=True):
        values = summary[key]
        print(
            "MONTHLY_SUMMARY_ROW: "
            + repr(
                {
                    "settlement_month": key[0],
                    "guild_no": key[1],
                    "bill_owner_type": key[2],
                    "data_source": key[3],
                    **{name: format(value, "f") for name, value in values.items()},
                }
            )
        )


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        raise SystemExit("Usage: query_production_user_guild_salary.py <user_no>")
    user_no = int(sys.argv[1])

    settings = load_env(PROJECT_ROOT / ".env")
    required = (
        "PROD_MYSQL_HOST",
        "PROD_MYSQL_PORT",
        "PROD_MYSQL_USER",
        "PROD_MYSQL_PASSWORD",
        "PROD_MYSQL_DATABASE",
    )
    missing = [name for name in required if not settings.get(name)]
    if missing:
        print(f"Missing required production settings: {', '.join(missing)}", file=sys.stderr)
        return 2

    connection = mysql.connector.connect(
        host=settings["PROD_MYSQL_HOST"],
        port=int(settings["PROD_MYSQL_PORT"]),
        user=settings["PROD_MYSQL_USER"],
        password=settings["PROD_MYSQL_PASSWORD"],
        database=settings["PROD_MYSQL_DATABASE"],
        connection_timeout=15,
    )
    try:
        cursor = connection.cursor()
        for table in SCHEMA_TABLES:
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            schema_rows = fetch_rows(cursor)
            print_rows(f"SHOW_{table.replace('.', '_').upper()}", schema_rows)

        cursor.execute(
            "SELECT user_id, user_no, register_client FROM app.ln_user WHERE user_no = %s",
            (user_no,),
        )
        user_rows = fetch_rows(cursor)
        print_rows("USER", user_rows)
        if len(user_rows) != 1:
            print("ABNORMAL: user_no did not map to exactly one app.ln_user record")
            return 0
        user_id = user_rows[0]["user_id"]

        cursor.execute(
            """
            SELECT gm.id AS member_id, gm.guild_id, gi.guild_no, gi.guild_name,
                   gm.member_role, gm.member_status, gm.policy_type, gm.joined_at
            FROM guild.guild_member AS gm
            LEFT JOIN guild.guild_info AS gi ON gi.id = gm.guild_id
            WHERE gm.user_id = %s
            ORDER BY gm.id
            """,
            (user_id,),
        )
        member_rows = fetch_rows(cursor)
        print_rows("GUILD_MEMBER", member_rows, preview_limit=100)

        cursor.execute(
            """
            SELECT
                sd.id, sd.settlement_month, gi.guild_no, gi.guild_name,
                sd.member_id, sd.user_id, sd.bill_owner_type, sd.policy_type,
                sd.settlement_bill_id, sb.bill_no, sb.settle_status, sb.settled_at,
                sd.valid_diamond_amount_total, sd.valid_diamond_balance_amount,
                sd.salary_level, sd.effective_days, sd.required_effective_days,
                sd.effective_day_qualified, sd.anchor_base_salary_amount,
                sd.anchor_tc_reward_amount, sd.non_coin_reward_amount,
                sd.coin_reward_amount, sd.guild_coin_reward_amount,
                sd.advance_deduction_amount, sd.total_salary_amount, sd.calc_status,
                sd.calculated_at
            FROM guild.guild_salary_detail AS sd
            LEFT JOIN guild.guild_info AS gi ON gi.id = sd.guild_id
            LEFT JOIN guild.guild_settlement_bill AS sb ON sb.id = sd.settlement_bill_id
            WHERE sd.user_id = %s
            ORDER BY sd.settlement_month DESC, sd.guild_id, sd.member_id,
                     sd.bill_owner_type, sd.settlement_bill_id, sd.id
            """,
            (user_id,),
        )
        salary_rows = fetch_rows(cursor)
        print_rows("SALARY_DETAIL", salary_rows, preview_limit=100)
        print_monthly_summary(salary_rows)

        duplicate_keys: dict[tuple[object, object, object, object, object], int] = defaultdict(int)
        for row in salary_rows:
            if row["settlement_bill_id"]:
                key = (
                    row["settlement_month"],
                    row["guild_no"],
                    row["member_id"],
                    row["bill_owner_type"],
                    row["settlement_bill_id"],
                )
                duplicate_keys[key] += 1
        duplicates = [key for key, count in duplicate_keys.items() if count > 1]
        if duplicates:
            print(f"ABNORMAL: duplicate settled salary snapshot keys: {duplicates}")
        if not salary_rows:
            print("ABNORMAL: no guild salary detail rows found for this user")
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
