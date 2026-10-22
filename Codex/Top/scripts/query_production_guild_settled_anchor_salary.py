from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
import sys

import mysql.connector


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def settlement_month() -> str:
    today = date.today()
    first_day_of_current_month = today.replace(day=1)
    previous_month_last_day = first_day_of_current_month.fromordinal(
        first_day_of_current_month.toordinal() - 1
    )
    return previous_month_last_day.strftime("%Y-%m")


def load_env(path: Path) -> dict[str, str]:
    settings: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        settings[name.strip()] = value.strip().strip('"').strip("'")
    return settings


def normalize(value: object) -> object:
    if isinstance(value, Decimal):
        return format(value, "f")
    return value


def print_rows(label: str, cursor: mysql.connector.cursor.MySQLCursor) -> list[dict[str, object]]:
    columns = [column[0] for column in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    print(f"{label}_COLUMNS: {','.join(columns)}")
    print(f"{label}_ROW_COUNT: {len(rows)}")
    for row in rows[:3]:
        print(f"{label}_ROW: " + repr({key: normalize(value) for key, value in row.items()}))
    return rows


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        raise SystemExit("Usage: query_production_guild_settled_anchor_salary.py <guild_no>")

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
        for table in (
            "guild.guild_info",
            "guild.guild_member",
            "guild.guild_salary_detail",
            "guild.guild_settlement_bill",
            "app.ln_user",
        ):
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            print_rows(f"SHOW_{table.replace('.', '_').upper()}", cursor)

        month = settlement_month()
        cursor.execute(
            """
            SELECT gi.id, gi.guild_no, gi.guild_name
            FROM guild.guild_info AS gi
            WHERE gi.guild_no = %s
            """,
            (int(sys.argv[1]),),
        )
        guild_rows = print_rows("GUILD", cursor)
        if not guild_rows:
            return 0

        guild_id = guild_rows[0]["id"]
        cursor.execute(
            """
            SELECT
                sb.bill_no AS settlement_bill_no,
                sb.settled_at,
                sd.member_id,
                sd.user_id,
                u.user_no,
                u.register_client,
                sd.policy_type,
                sd.valid_diamond_amount_total,
                sd.valid_diamond_balance_amount,
                CASE WHEN sd.policy_type = 1 THEN sd.salary_level END AS salary_level,
                sd.effective_days,
                sd.required_effective_days,
                sd.effective_day_qualified,
                CASE WHEN sd.policy_type = 1 THEN sd.anchor_base_salary_amount END
                    AS anchor_base_salary_amount,
                CASE WHEN sd.policy_type = 1 THEN sd.anchor_tc_reward_amount END
                    AS anchor_tc_reward_amount,
                sd.effective_day_deduction_amount,
                sd.non_coin_reward_amount,
                sd.coin_reward_amount,
                sd.non_coin_reward_amount + sd.coin_reward_amount AS total_salary_amount,
                sd.advance_deduction_amount,
                sd.non_coin_reward_amount - sd.advance_deduction_amount
                    + sd.coin_reward_amount AS salary_balance_amount
            FROM guild.guild_salary_detail AS sd
            INNER JOIN guild.guild_settlement_bill AS sb
                ON sb.id = sd.settlement_bill_id
                AND sb.guild_id = sd.guild_id
                AND sb.settlement_month = sd.settlement_month
            LEFT JOIN app.ln_user AS u ON u.user_id = sd.user_id
            WHERE sd.guild_id = %s
              AND sd.settlement_month = %s
              AND sd.bill_owner_type = 1
              AND sd.settlement_bill_id <> 0
              AND sb.settle_status = 2
            ORDER BY u.user_no, sd.member_id, sd.id
            """,
            (guild_id, month),
        )
        rows = print_rows("SETTLED_ANCHOR_SALARY", cursor)
        print(f"SETTLEMENT_MONTH: {month}")
        print("RESULT_ROWS_BEGIN")
        for row in rows:
            print(repr({key: normalize(value) for key, value in row.items()}))
        print("RESULT_ROWS_END")
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
