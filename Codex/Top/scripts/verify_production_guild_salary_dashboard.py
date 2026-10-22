from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
import sys

import mysql.connector


GUILD_NO = 71960192
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def settlement_month_from_args() -> str:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: verify_production_guild_salary_dashboard.py YYYY-MM")
    try:
        return date.fromisoformat(f"{sys.argv[1]}-01").strftime("%Y-%m")
    except ValueError as error:
        raise SystemExit("Usage: verify_production_guild_salary_dashboard.py YYYY-MM") from error


def load_env(path: Path) -> dict[str, str]:
    settings: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            settings[key.strip()] = value.strip().strip('"').strip("'")
    return settings


def print_rows(
    cursor: mysql.connector.cursor.MySQLCursor,
    label: str,
    preview_limit: int = 3,
) -> list[dict[str, object]]:
    columns = [column[0] for column in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    print(f"{label}_COLUMNS: {','.join(columns)}")
    print(f"{label}_ROW_COUNT: {len(rows)}")
    for row in rows[:preview_limit]:
        print(f"{label}_ROW: {row}")
    return rows


def value(row: dict[str, object], key: str) -> Decimal:
    return Decimal(str(row[key] or 0))


def main() -> int:
    month = settlement_month_from_args()
    settings = load_env(PROJECT_ROOT / ".env")
    required = (
        "PROD_MYSQL_HOST",
        "PROD_MYSQL_PORT",
        "PROD_MYSQL_USER",
        "PROD_MYSQL_PASSWORD",
        "PROD_MYSQL_DATABASE",
    )
    missing = [key for key in required if not settings.get(key)]
    if missing:
        print(f"Missing production settings: {', '.join(missing)}", file=sys.stderr)
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
        ):
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            print_rows(cursor, f"SHOW_{table.replace('.', '_').upper()}")

        cursor.execute(
            "SELECT id, guild_no, guild_name FROM guild.guild_info WHERE guild_no = %s",
            (GUILD_NO,),
        )
        guild_rows = print_rows(cursor, "GUILD")
        if not guild_rows:
            return 0
        guild_id = guild_rows[0]["id"]

        cursor.execute(
            """
            SELECT id, bill_no, settlement_month, member_id, user_id, bill_owner_type,
                   total_salary_amount, payable_amount, coin_reward_amount,
                   guild_coin_reward_amount, settle_status, settled_at
            FROM guild.guild_settlement_bill
            WHERE guild_id = %s AND settlement_month = %s
            ORDER BY id
            """,
            (guild_id, month),
        )
        bills = print_rows(cursor, "SETTLEMENT_BILL", preview_limit=100)

        cursor.execute(
            """
            SELECT sd.id, sd.settlement_bill_id, sd.member_id, sd.bill_owner_type,
                   u.user_no, sd.valid_diamond_amount_total,
                   sd.valid_diamond_balance_amount, sd.month_exchange_diamond,
                   sd.non_coin_reward_amount, sd.coin_reward_amount,
                   sd.guild_coin_reward_amount, sd.total_salary_amount,
                   sd.anchor_total_salary_amount, sd.owner_share_amount,
                   sd.advance_deduction_amount
            FROM guild.guild_salary_detail AS sd
            LEFT JOIN app.ln_user AS u ON u.user_id = sd.user_id
            WHERE sd.guild_id = %s
              AND sd.settlement_month = %s
              AND sd.settlement_bill_id > 0
            ORDER BY sd.bill_owner_type, sd.member_id, sd.id
            """,
            (guild_id, month),
        )
        snapshots = print_rows(cursor, "SETTLED_SALARY_SNAPSHOT", preview_limit=100)

        cursor.execute(
            """
            SELECT valid_diamond_amount_total, valid_diamond_balance_amount,
                   month_exchange_diamond, anchor_total_salary_amount,
                   owner_share_amount, total_salary_amount,
                   advance_deduction_amount, coin_reward_amount,
                   guild_coin_reward_amount, settlement_bill_id, calc_status
            FROM guild.guild_salary_detail
            WHERE guild_id = %s AND settlement_month = %s
              AND member_id = 0 AND bill_owner_type = 2
            """,
            (guild_id, month),
        )
        dashboard_rows = print_rows(cursor, "DASHBOARD_SUMMARY")

        anchor_rows = [row for row in snapshots if row["bill_owner_type"] == 1]
        owner_rows = [row for row in snapshots if row["bill_owner_type"] == 2]
        anchor_total = sum((value(row, "total_salary_amount") for row in anchor_rows), Decimal())
        owner_non_coin = sum((value(row, "total_salary_amount") for row in owner_rows), Decimal())
        owner_coin = sum((value(row, "guild_coin_reward_amount") for row in owner_rows), Decimal())
        anchor_coin = sum((value(row, "coin_reward_amount") for row in anchor_rows), Decimal())
        dashboard_total = anchor_total + owner_non_coin + owner_coin
        snapshots_by_bill = {
            int(row["settlement_bill_id"]): row for row in snapshots
        }
        for bill in bills:
            snapshot = snapshots_by_bill.get(int(bill["id"]))
            if snapshot is None:
                print(f"BILL_RECONCILIATION: bill_id={bill['id']};snapshot=missing")
                continue
            print(
                "BILL_RECONCILIATION: "
                f"bill_id={bill['id']};"
                f"total_delta={value(snapshot, 'total_salary_amount') - value(bill, 'total_salary_amount')};"
                f"coin_delta={value(snapshot, 'coin_reward_amount') - value(bill, 'coin_reward_amount')};"
                f"guild_coin_delta={value(snapshot, 'guild_coin_reward_amount') - value(bill, 'guild_coin_reward_amount')}"
            )
        print(
            "RECOMPUTED: "
            f"anchor_total={anchor_total};owner_non_coin={owner_non_coin};"
            f"anchor_coin={anchor_coin};owner_coin={owner_coin};"
            f"guild_coin={anchor_coin + owner_coin};dashboard_total={dashboard_total};"
            f"settled_snapshot_rows={len(snapshots)};settlement_bills={len(bills)}"
        )
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
