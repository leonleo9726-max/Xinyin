from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

import mysql.connector


USER_NO = "6729461"
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_env(path: Path) -> dict[str, str]:
    settings: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        settings[name.strip()] = value.strip().strip('"').strip("'")
    return settings


def format_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat(sep=" ")
    return value


def print_rows(label: str, cursor: mysql.connector.cursor.MySQLCursor) -> list[dict[str, Any]]:
    columns = [column[0] for column in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    print(f"{label}_COLUMNS: {','.join(columns)}")
    print(f"{label}_ROW_COUNT: {len(rows)}")
    for row in rows[:3]:
        print(f"{label}_ROW: { {key: format_value(value) for key, value in row.items()} }")
    if len(rows) > 3:
        print(f"{label}_TRUNCATED_ROWS: {len(rows) - 3}")
    return rows


def table_columns(cursor: mysql.connector.cursor.MySQLCursor, table: str) -> set[str]:
    cursor.execute(f"SHOW COLUMNS FROM `{table}`")
    rows = print_rows(f"SHOW_{table.upper()}", cursor)
    return {str(row["Field"]) for row in rows}


def fetch_rows(
    cursor: mysql.connector.cursor.MySQLCursor,
    label: str,
    query: str,
    params: tuple[Any, ...] = (),
) -> list[dict[str, Any]]:
    cursor.execute(query, params)
    return print_rows(label, cursor)


def first_present(columns: set[str], candidates: tuple[str, ...]) -> str | None:
    return next((column for column in candidates if column in columns), None)


def main() -> int:
    settings = load_env(PROJECT_ROOT / ".env")
    required = ("MYSQL_HOST", "MYSQL_PORT", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE")
    missing = [name for name in required if not settings.get(name)]
    if missing:
        print(f"Missing required test settings: {', '.join(missing)}", file=sys.stderr)
        return 2

    connection = mysql.connector.connect(
        host=settings["MYSQL_HOST"],
        port=int(settings["MYSQL_PORT"]),
        user=settings["MYSQL_USER"],
        password=settings["MYSQL_PASSWORD"],
        database=settings["MYSQL_DATABASE"],
        connection_timeout=15,
    )
    try:
        cursor = connection.cursor()
        print(f"DATABASE: {settings['MYSQL_DATABASE']}")
        print("ENVIRONMENT: test (MYSQL_* settings)")

        columns = {
            table: table_columns(cursor, table)
            for table in (
                "ln_user",
                "ln_user_data",
                "ln_give_gift",
                "lucky_gift_draw_event",
                "ln_wallet_log",
                "lucky_gift_report_projection",
                "lucky_card_grant_record",
            )
        }

        users = fetch_rows(
            cursor,
            "USER",
            """
            SELECT user_id, user_no, disabled, deleted, role, vip_level, coin, earnings_coin,
                   register_time, last_login_time, last_online_time
            FROM ln_user
            WHERE user_no = %s
            """,
            (USER_NO,),
        )
        if not users:
            fetch_rows(
                cursor,
                "USER_DATA_BY_USER_CODE",
                """
                SELECT user_id, user_code, nickname, sex, anchor_level, wealth_level, charm_level,
                       active_value, locale, yzh_sign_status, is_internal_staff
                FROM ln_user_data
                WHERE user_code = %s
                """,
                (USER_NO,),
            )
            return 0

        user_id = users[0]["user_id"]
        fetch_rows(
            cursor,
            "USER_DATA",
            """
            SELECT user_id, user_code, nickname, sex, anchor_level, wealth_level, charm_level,
                   active_value, locale, yzh_sign_status, is_internal_staff
            FROM ln_user_data
            WHERE user_id = %s
            """,
            (user_id,),
        )

        gift_columns = columns["ln_give_gift"]
        sender_column = first_present(
            gift_columns,
            ("user_id", "sender_user_id", "send_user_id", "from_user_id"),
        )
        recipient_column = first_present(
            gift_columns,
            ("receive_user_id", "recipient_user_id", "to_user_id", "target_user_id"),
        )
        role_conditions: list[str] = []
        if sender_column:
            role_conditions.append(f"`{sender_column}` = %s")
        if recipient_column:
            role_conditions.append(f"`{recipient_column}` = %s")
        if not role_conditions:
            print("GIFT_LOOKUP_ERROR: no sender/recipient user column found")
            return 1

        gifts = fetch_rows(
            cursor,
            "LUCKY_GIFTS",
            "SELECT * FROM ln_give_gift WHERE type IN (35, 36) AND ("
            + " OR ".join(role_conditions)
            + ") ORDER BY id DESC",
            tuple(user_id for _ in role_conditions),
        )
        gift_ids = [row["id"] for row in gifts]

        if gift_ids:
            placeholders = ",".join(["%s"] * len(gift_ids))
            fetch_rows(
                cursor,
                "DRAW_EVENTS",
                f"SELECT * FROM lucky_gift_draw_event WHERE give_gift_id IN ({placeholders}) ORDER BY give_gift_id, unit_index",
                tuple(gift_ids),
            )
            fetch_rows(
                cursor,
                "REPORT_PROJECTIONS",
                f"SELECT * FROM lucky_gift_report_projection WHERE give_gift_id IN ({placeholders}) ORDER BY give_gift_id",
                tuple(gift_ids),
            )

            wallet_columns = columns["ln_wallet_log"]
            wallet_user_column = first_present(wallet_columns, ("user_id", "user_number"))
            if wallet_user_column:
                fetch_rows(
                    cursor,
                    "WALLET_LOGS_FOR_USER",
                    f"""
                    SELECT * FROM ln_wallet_log
                    WHERE `{wallet_user_column}` = %s
                      AND bus_type IN (10012, 40002)
                    ORDER BY id DESC
                    """,
                    (user_id,),
                )
            else:
                print("WALLET_LOGS_FOR_USER_ERROR: no user column found")

        card_columns = columns["lucky_card_grant_record"]
        card_user_column = first_present(card_columns, ("user_id", "user_number"))
        if card_user_column:
            fetch_rows(
                cursor,
                "CARD_GRANTS",
                f"SELECT * FROM lucky_card_grant_record WHERE `{card_user_column}` = %s ORDER BY id DESC",
                (user_id,),
            )
        else:
            print("CARD_GRANTS_ERROR: no user column found")
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
