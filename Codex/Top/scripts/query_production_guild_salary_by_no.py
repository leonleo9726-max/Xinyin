from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
import sys

import mysql.connector


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_TABLES = (
    "guild.guild_info",
    "guild.guild_member",
    "guild.guild_salary_detail",
    "guild.guild_settlement_bill",
    "app.ln_user",
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


def amount(value: object) -> Decimal:
    return Decimal(str(value or 0))


def source_for(row: dict[str, object]) -> str:
    if not row["settlement_bill_id"]:
        return "realtime"
    if row["settle_status"] == 2:
        return "settled_snapshot"
    return "unconfirmed_settlement_bill"


def print_summary(rows: list[dict[str, object]]) -> None:
    summaries: dict[str, dict[str, Decimal | int]] = defaultdict(
        lambda: {
            "anchor_total": Decimal(),
            "owner_management_non_coin": Decimal(),
            "owner_management_coin": Decimal(),
            "advance_deduction": Decimal(),
            "guild_valid_diamond_amount_total": Decimal(),
            "guild_valid_diamond_balance_amount": Decimal(),
            "anchor_row_count": 0,
            "owner_member_row_count": 0,
            "owner_summary_row_count": 0,
        }
    )
    for row in rows:
        summary = summaries[source_for(row)]
        if row["bill_owner_type"] == 1:
            summary["anchor_total"] += amount(row["non_coin_reward_amount"]) + amount(
                row["coin_reward_amount"]
            )
            summary["advance_deduction"] += amount(row["advance_deduction_amount"])
            summary["anchor_row_count"] += 1
        elif row["member_id"] == 0:
            summary["guild_valid_diamond_amount_total"] += amount(
                row["valid_diamond_amount_total"]
            )
            summary["guild_valid_diamond_balance_amount"] += amount(
                row["valid_diamond_balance_amount"]
            )
            summary["owner_summary_row_count"] += 1
        else:
            # total_salary_amount is the owner non-coin component; guild coin is separate.
            summary["owner_management_non_coin"] += amount(row["total_salary_amount"])
            summary["owner_management_coin"] += amount(row["guild_coin_reward_amount"])
            summary["advance_deduction"] += amount(row["advance_deduction_amount"])
            summary["owner_member_row_count"] += 1

    print(
        "GUILD_SALARY_SUMMARY_COLUMNS: data_source,anchor_total_salary,"
        "owner_management_non_coin,owner_management_coin,owner_management_total,"
        "guild_total_salary,advance_deduction,guild_salary_balance,"
        "guild_valid_diamond_amount_total,"
        "guild_valid_diamond_balance_amount,anchor_row_count,"
        "owner_member_row_count,owner_summary_row_count"
    )
    print(f"GUILD_SALARY_SUMMARY_ROW_COUNT: {len(summaries)}")
    for data_source, values in summaries.items():
        owner_total = values["owner_management_non_coin"] + values["owner_management_coin"]
        guild_total = values["anchor_total"] + owner_total
        guild_salary_balance = guild_total - values["advance_deduction"]
        result = {
            "data_source": data_source,
            "anchor_total_salary": format(values["anchor_total"], "f"),
            "owner_management_non_coin": format(values["owner_management_non_coin"], "f"),
            "owner_management_coin": format(values["owner_management_coin"], "f"),
            "owner_management_total": format(owner_total, "f"),
            "guild_total_salary": format(guild_total, "f"),
            "advance_deduction": format(values["advance_deduction"], "f"),
            "guild_salary_balance": format(guild_salary_balance, "f"),
            "guild_valid_diamond_amount_total": format(
                values["guild_valid_diamond_amount_total"], "f"
            ),
            "guild_valid_diamond_balance_amount": format(
                values["guild_valid_diamond_balance_amount"], "f"
            ),
            "anchor_row_count": values["anchor_row_count"],
            "owner_member_row_count": values["owner_member_row_count"],
            "owner_summary_row_count": values["owner_summary_row_count"],
        }
        print(f"GUILD_SALARY_SUMMARY_ROW: {repr(result)}")


def main() -> int:
    if len(sys.argv) not in (2, 3) or not sys.argv[1].isdigit():
        raise SystemExit("Usage: query_production_guild_salary_by_no.py <guild_no> [YYYY-MM]")
    guild_no = int(sys.argv[1])
    month = sys.argv[2] if len(sys.argv) == 3 else date.today().strftime("%Y-%m")
    try:
        month = date.fromisoformat(f"{month}-01").strftime("%Y-%m")
    except ValueError as error:
        raise SystemExit("Month must use YYYY-MM") from error

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
            print_rows(f"SHOW_{table.replace('.', '_').upper()}", fetch_rows(cursor))

        cursor.execute(
            "SELECT id, guild_no, guild_name, owner_user_id, guild_status FROM guild.guild_info WHERE guild_no = %s",
            (guild_no,),
        )
        guild_rows = fetch_rows(cursor)
        print_rows("GUILD", guild_rows)
        if len(guild_rows) != 1:
            print("ABNORMAL: guild_no did not map to exactly one guild record")
            return 0
        guild_id = guild_rows[0]["id"]

        cursor.execute(
            """
            SELECT member_status, member_role, COUNT(*) AS member_count
            FROM guild.guild_member
            WHERE guild_id = %s
            GROUP BY member_status, member_role
            ORDER BY member_status, member_role
            """,
            (guild_id,),
        )
        print_rows("MEMBER_STATUS", fetch_rows(cursor), preview_limit=100)

        cursor.execute(
            """
            SELECT sd.id, sd.settlement_month, sd.member_id, sd.user_id, u.user_no,
                   sd.bill_owner_type, sd.policy_type, sd.settlement_bill_id,
                   sb.bill_no, sb.settle_status, sb.settled_at,
                   sd.valid_diamond_amount_total, sd.valid_diamond_balance_amount,
                   sd.non_coin_reward_amount, sd.coin_reward_amount,
                   sd.guild_coin_reward_amount, sd.advance_deduction_amount,
                   sd.total_salary_amount, sd.calc_status, sd.calculated_at
            FROM guild.guild_salary_detail AS sd
            LEFT JOIN guild.guild_settlement_bill AS sb ON sb.id = sd.settlement_bill_id
            LEFT JOIN app.ln_user AS u ON u.user_id = sd.user_id
            WHERE sd.guild_id = %s AND sd.settlement_month = %s
            ORDER BY sd.bill_owner_type, sd.member_id, sd.settlement_bill_id, sd.id
            """,
            (guild_id, month),
        )
        salary_rows = fetch_rows(cursor)
        print_rows("SALARY_DETAIL", salary_rows, preview_limit=100)

        cursor.execute(
            """
            SELECT gm.id AS member_id, u.user_no, gm.policy_type, gm.joined_at,
                   sd.id AS salary_detail_id, sd.settlement_bill_id, sb.settle_status,
                   sd.valid_diamond_amount_total, sd.valid_diamond_balance_amount,
                   sd.salary_level, sd.effective_days, sd.required_effective_days,
                   sd.effective_day_qualified, sd.anchor_base_salary_amount,
                   sd.anchor_tc_reward_amount, sd.non_coin_reward_amount,
                   sd.coin_reward_amount, sd.advance_deduction_amount,
                   sd.total_salary_amount, sd.calc_status, sd.calculated_at
            FROM guild.guild_member AS gm
            INNER JOIN app.ln_user AS u ON u.user_id = gm.user_id
            LEFT JOIN guild.guild_salary_detail AS sd
                ON sd.member_id = gm.id
                AND sd.settlement_month = %s
                AND sd.bill_owner_type = 1
            LEFT JOIN guild.guild_settlement_bill AS sb ON sb.id = sd.settlement_bill_id
            WHERE gm.guild_id = %s
              AND gm.member_role = 1
              AND gm.member_status = 2
            ORDER BY gm.id, sd.settlement_bill_id, sd.id
            """,
            (month, guild_id),
        )
        anchor_rows = fetch_rows(cursor)
        print_rows("ACTIVE_ANCHOR_SALARY", anchor_rows, preview_limit=100)

        cursor.execute(
            """
            SELECT
                u.user_no, anchor.member_id, anchor.policy_type,
                anchor.valid_diamond_amount_total AS anchor_valid_diamond_amount_total,
                anchor.valid_diamond_balance_amount AS anchor_valid_diamond_balance_amount,
                anchor.target_diamond_amount AS anchor_target_diamond_amount,
                anchor.actual_diamond_amount AS anchor_actual_diamond_amount,
                anchor.over_target_diamond_amount AS anchor_over_target_diamond_amount,
                anchor.over_target_salary_amount AS anchor_over_target_salary_amount,
                anchor.salary_base_amount AS anchor_salary_base_amount,
                anchor.base_share_rate, anchor.tc_reward_rate, anchor.owner_share_rate,
                anchor.effective_days, anchor.required_effective_days,
                anchor.effective_day_qualified,
                anchor.anchor_base_salary_amount, anchor.anchor_tc_reward_amount,
                anchor.effective_day_deduction_amount,
                anchor.coin_reward_rate, anchor.non_coin_reward_amount,
                anchor.coin_reward_amount, anchor.total_salary_amount AS anchor_total_salary_amount,
                owner.valid_diamond_amount_total AS owner_valid_diamond_amount_total,
                owner.target_diamond_amount AS owner_target_diamond_amount,
                owner.actual_diamond_amount AS owner_actual_diamond_amount,
                owner.over_target_diamond_amount AS owner_over_target_diamond_amount,
                owner.over_target_salary_amount AS owner_over_target_salary_amount,
                owner.salary_base_amount AS owner_salary_base_amount,
                owner.owner_share_rate AS owner_snapshot_share_rate,
                owner.owner_share_amount, owner.owner_effective_day_deduction_amount,
                owner.guild_coin_reward_amount,
                owner.total_salary_amount AS owner_management_total_salary_amount
            FROM guild.guild_salary_detail AS anchor
            INNER JOIN app.ln_user AS u ON u.user_id = anchor.user_id
            LEFT JOIN guild.guild_salary_detail AS owner
                ON owner.guild_id = anchor.guild_id
                AND owner.member_id = anchor.member_id
                AND owner.settlement_month = anchor.settlement_month
                AND owner.bill_owner_type = 2
            WHERE anchor.guild_id = %s
              AND anchor.settlement_month = %s
              AND anchor.bill_owner_type = 1
            ORDER BY anchor.member_id, anchor.id
            """,
            (guild_id, month),
        )
        calculation_rows = fetch_rows(cursor)
        print_rows("SALARY_CALCULATION_SNAPSHOT", calculation_rows, preview_limit=100)
        print(f"SETTLEMENT_MONTH: {month}")
        print_summary(salary_rows)

        duplicate_keys: dict[tuple[object, object, object, object], int] = defaultdict(int)
        for row in salary_rows:
            if row["settlement_bill_id"]:
                duplicate_keys[
                    (row["member_id"], row["bill_owner_type"], row["settlement_bill_id"], row["user_id"])
                ] += 1
        duplicates = [key for key, count in duplicate_keys.items() if count > 1]
        if duplicates:
            print(f"ABNORMAL: duplicate settled salary snapshot keys: {duplicates}")
        missing_salary_members = [
            row["user_no"] for row in anchor_rows if row["salary_detail_id"] is None
        ]
        if missing_salary_members:
            print(
                "ABNORMAL: active anchors without salary detail: "
                + ",".join(str(user_no) for user_no in missing_salary_members)
            )
        if not salary_rows:
            print("ABNORMAL: no salary detail rows found for this settlement month")
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
