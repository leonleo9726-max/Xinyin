from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
import sys

import mysql.connector


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def previous_month() -> str:
    current_month_start = date.today().replace(day=1)
    return current_month_start.fromordinal(current_month_start.toordinal() - 1).strftime("%Y-%m")


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def render(value: object) -> object:
    if isinstance(value, Decimal):
        return format(value, "f")
    return value


def fetch(label: str, cursor: mysql.connector.cursor.MySQLCursor) -> list[dict[str, object]]:
    columns = [column[0] for column in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    print(f"{label}_COLUMNS: {','.join(columns)}")
    print(f"{label}_ROW_COUNT: {len(rows)}")
    for row in rows[:3]:
        print(f"{label}_ROW: " + repr({key: render(value) for key, value in row.items()}))
    return rows


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        raise SystemExit("Usage: query_production_guild_settled_owner_salary.py <guild_no>")

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
            "guild.guild_salary_detail",
            "guild.guild_settlement_bill",
            "app.ln_user",
        ):
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            fetch(f"SHOW_{table.replace('.', '_').upper()}", cursor)

        month = previous_month()
        cursor.execute(
            """
            SELECT id, guild_no, guild_name, owner_user_id
            FROM guild.guild_info
            WHERE guild_no = %s
            """,
            (int(sys.argv[1]),),
        )
        guild_rows = fetch("GUILD", cursor)
        if not guild_rows:
            return 0

        guild = guild_rows[0]
        cursor.execute(
            """
            SELECT
                owner.user_no AS owner_user_no,
                anchor.user_no AS anchor_user_no,
                sd.member_id,
                sb.bill_no AS settlement_bill_no,
                sb.settled_at,
                sd.policy_type,
                sd.valid_diamond_amount_total,
                sd.owner_share_amount,
                sd.owner_effective_day_deduction_amount,
                sd.guild_coin_reward_amount,
                sd.total_salary_amount AS owner_management_salary_amount
            FROM guild.guild_salary_detail AS sd
            INNER JOIN guild.guild_settlement_bill AS sb
                ON sb.id = sd.settlement_bill_id
                AND sb.guild_id = sd.guild_id
                AND sb.settlement_month = sd.settlement_month
            LEFT JOIN app.ln_user AS owner ON owner.user_id = sd.owner_user_id
            LEFT JOIN app.ln_user AS anchor ON anchor.user_id = sd.user_id
            WHERE sd.guild_id = %s
              AND sd.settlement_month = %s
              AND sd.bill_owner_type = 2
              AND sd.member_id <> 0
              AND sd.settlement_bill_id <> 0
              AND sb.settle_status = 2
            ORDER BY anchor.user_no, sd.member_id, sd.id
            """,
            (guild["id"], month),
        )
        rows = fetch("SETTLED_OWNER_SALARY_BY_ANCHOR", cursor)

        cursor.execute(
            """
            SELECT
                COUNT(*) AS settled_member_count,
                COALESCE(SUM(sd.owner_share_amount), 0) AS owner_share_amount,
                COALESCE(SUM(sd.owner_effective_day_deduction_amount), 0)
                    AS owner_effective_day_deduction_amount,
                COALESCE(SUM(sd.guild_coin_reward_amount), 0) AS guild_coin_reward_amount,
                COALESCE(SUM(sd.total_salary_amount), 0) AS owner_management_salary_amount
            FROM guild.guild_salary_detail AS sd
            INNER JOIN guild.guild_settlement_bill AS sb
                ON sb.id = sd.settlement_bill_id
                AND sb.guild_id = sd.guild_id
                AND sb.settlement_month = sd.settlement_month
            WHERE sd.guild_id = %s
              AND sd.settlement_month = %s
              AND sd.bill_owner_type = 2
              AND sd.member_id <> 0
              AND sd.settlement_bill_id <> 0
              AND sb.settle_status = 2
            """,
            (guild["id"], month),
        )
        fetch("OWNER_SALARY_TOTAL", cursor)
        print(f"SETTLEMENT_MONTH: {month}")
        print(f"GUILD_OWNER_USER_ID: {guild['owner_user_id']}")
        print("RESULT_ROWS_BEGIN")
        for row in rows:
            print(repr({key: render(value) for key, value in row.items()}))
        print("RESULT_ROWS_END")
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
