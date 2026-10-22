from __future__ import annotations

from datetime import date
from pathlib import Path
import sys

import mysql.connector


GUILD_NO = 71960192
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def settlement_month_from_args() -> str:
    if len(sys.argv) == 1:
        return date.today().strftime("%Y-%m")
    if len(sys.argv) == 2:
        try:
            return date.fromisoformat(f"{sys.argv[1]}-01").strftime("%Y-%m")
        except ValueError as error:
            raise SystemExit("Usage: query_production_guild_salary.py [YYYY-MM]") from error
    raise SystemExit("Usage: query_production_guild_salary.py [YYYY-MM]")


def load_env(path: Path) -> dict[str, str]:
    settings: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        settings[name.strip()] = value.strip().strip('"').strip("'")
    return settings


def print_rows(
    label: str,
    cursor: mysql.connector.cursor.MySQLCursor,
    preview_limit: int = 3,
) -> list[dict[str, object]]:
    columns = [column[0] for column in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    print(f"{label}_COLUMNS: {','.join(columns)}")
    print(f"{label}_ROW_COUNT: {len(rows)}")
    for row in rows[:preview_limit]:
        print(f"{label}_ROW: {row}")
    return rows


def main() -> int:
    settlement_month = settlement_month_from_args()
    settings = load_env(PROJECT_ROOT / ".env")
    required = [
        "PROD_MYSQL_HOST",
        "PROD_MYSQL_PORT",
        "PROD_MYSQL_USER",
        "PROD_MYSQL_PASSWORD",
        "PROD_MYSQL_DATABASE",
    ]
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

        cursor.execute(
            """
            SELECT id, guild_no, guild_name, guild_status
            FROM guild.guild_info
            WHERE guild_no = %s
            """,
            (GUILD_NO,),
        )
        guild_rows = print_rows("GUILD", cursor)
        if not guild_rows:
            return 0
        guild_id = guild_rows[0]["id"]

        cursor.execute(
            """
            SELECT gm.id, gm.user_id, u.user_no, u.register_client,
                   gm.member_role, gm.member_status, gm.policy_type,
                   gm.joined_at
            FROM guild.guild_member AS gm
            LEFT JOIN app.ln_user AS u ON u.user_id = gm.user_id
            WHERE gm.guild_id = %s
            ORDER BY gm.id
            """,
            (guild_id,),
        )
        print_rows("GUILD_MEMBER", cursor, preview_limit=100)

        cursor.execute(
            """
            SELECT
                sd.settlement_month, sd.member_id, sd.user_id, u.user_no,
                u.register_client, sd.bill_owner_type,
                sd.policy_type AS settlement_policy_type,
                sd.valid_diamond_amount_total, sd.salary_level,
                sd.effective_days, sd.required_effective_days,
                sd.effective_day_qualified, sd.payable_amount,
                sd.total_salary_amount, sd.anchor_total_salary_amount,
                sd.owner_share_amount, sd.calc_status, sd.settlement_bill_id
            FROM guild.guild_salary_detail AS sd
            LEFT JOIN app.ln_user AS u ON u.user_id = sd.user_id
            WHERE sd.guild_id = %s AND sd.settlement_month = %s
            ORDER BY u.register_client, u.user_no, sd.bill_owner_type, sd.id
            """,
            (guild_id, settlement_month),
        )
        print_rows("SALARY_DETAIL", cursor, preview_limit=100)

        cursor.execute(
            """
            SELECT
                u.user_no,
                sd.member_id,
                sd.policy_type,
                sd.valid_diamond_amount_total,
                sd.valid_diamond_balance_amount,
                CASE WHEN sd.policy_type = 1 THEN sd.salary_level END
                    AS client_salary_level,
                sd.effective_days,
                sd.required_effective_days,
                sd.effective_day_qualified,
                CASE WHEN sd.policy_type = 1
                    THEN sd.salary_base_amount * sd.base_share_rate END
                    AS client_base_salary_before_deduction,
                CASE WHEN sd.policy_type = 1
                    THEN sd.salary_base_amount * sd.tc_reward_rate END
                    AS client_tc_reward_before_deduction,
                CASE WHEN sd.policy_type = 1 THEN sd.anchor_base_salary_amount END
                    AS client_anchor_base_salary_amount,
                CASE WHEN sd.policy_type = 1 THEN sd.anchor_tc_reward_amount END
                    AS client_anchor_tc_reward_amount,
                sd.effective_day_deduction_amount,
                sd.non_coin_reward_amount,
                sd.coin_reward_amount,
                sd.non_coin_reward_amount + sd.coin_reward_amount
                    AS client_total_salary_amount,
                sd.advance_deduction_amount,
                sd.non_coin_reward_amount - sd.advance_deduction_amount
                    + sd.coin_reward_amount AS client_salary_balance_amount,
                sd.settlement_bill_id,
                CASE WHEN sd.settlement_bill_id = 0 THEN 'realtime'
                    ELSE 'settled' END AS client_data_source
            FROM guild.guild_salary_detail AS sd
            INNER JOIN guild.guild_member AS gm ON gm.id = sd.member_id
            LEFT JOIN app.ln_user AS u ON u.user_id = gm.user_id
            WHERE sd.guild_id = %s
              AND sd.settlement_month = %s
              AND sd.bill_owner_type = 1
            ORDER BY u.user_no, sd.member_id, sd.id
            """,
            (guild_id, settlement_month),
        )
        print_rows("CLIENT_ANCHOR_SALARY", cursor, preview_limit=100)

        cursor.execute(
            """
            SELECT
                u.register_client,
                u.user_no,
                sd.member_id,
                MAX(sd.policy_type) AS settlement_policy_type,
                MAX(sd.valid_diamond_amount_total) AS valid_diamond_amount_total,
                MAX(sd.salary_level) AS salary_level,
                MAX(sd.effective_days) AS effective_days,
                MAX(sd.required_effective_days) AS required_effective_days,
                MAX(sd.effective_day_qualified) AS effective_day_qualified,
                COALESCE(SUM(CASE WHEN sd.bill_owner_type = 1
                    THEN sd.total_salary_amount ELSE 0 END), 0) AS anchor_salary_amount,
                COALESCE(SUM(CASE WHEN sd.bill_owner_type = 2 AND sd.member_id <> 0
                    THEN sd.total_salary_amount ELSE 0 END), 0) AS owner_management_amount,
                MAX(CASE WHEN sd.bill_owner_type = 1
                    THEN sd.calc_status END) AS anchor_calc_status
            FROM guild.guild_salary_detail AS sd
            INNER JOIN guild.guild_member AS gm ON gm.id = sd.member_id
            LEFT JOIN app.ln_user AS u ON u.user_id = gm.user_id
            WHERE sd.guild_id = %s AND sd.settlement_month = %s AND sd.member_id <> 0
            GROUP BY u.register_client, u.user_no, sd.member_id
            ORDER BY u.register_client, u.user_no, sd.member_id
            """,
            (guild_id, settlement_month),
        )
        print_rows("MEMBER_SALARY_BY_CLIENT", cursor, preview_limit=100)

        cursor.execute(
            """
            SELECT settle_status, COUNT(*) AS bill_count,
                   COALESCE(SUM(total_salary_amount), 0) AS bill_total_salary
            FROM guild.guild_settlement_bill
            WHERE guild_id = %s AND settlement_month = %s
            GROUP BY settle_status
            ORDER BY settle_status
            """,
            (guild_id, settlement_month),
        )
        print_rows("SETTLEMENT_STATUS", cursor)
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
