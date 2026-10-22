from __future__ import annotations

from pathlib import Path
import sys

import mysql.connector


USER_NO = "6729461"
ROOT = Path(__file__).resolve().parent.parent


def env_values() -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def dump(cursor: mysql.connector.cursor.MySQLCursor, label: str) -> None:
    columns = [column[0] for column in cursor.description]
    print(f"{label}_COLUMNS: {','.join(columns)}")
    result = cursor.fetchall()
    print(f"{label}_COUNT: {len(result)}")
    for row in result:
        print(f"{label}: {dict(zip(columns, row))}")


def main() -> int:
    settings = env_values()
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
        for table in ("ln_user", "ln_give_gift", "ln_wallet_log", "lucky_gift_draw_event"):
            cursor.execute(f"SHOW COLUMNS FROM `{table}`")
            dump(cursor, f"SHOW_{table.upper()}")

        cursor.execute("SELECT user_id FROM ln_user WHERE user_no = %s", (USER_NO,))
        user = cursor.fetchone()
        if not user:
            print("USER_NOT_FOUND")
            return 0
        user_id = user[0]
        cursor.execute(
            """
            SELECT
                g.id AS give_gift_id,
                CASE WHEN g.user_id = %s THEN 'sender' ELSE 'recipient' END AS user_role,
                g.user_id AS sender_user_id,
                g.gift_user AS recipient_user_id,
                g.type,
                g.number,
                g.total_price,
                COUNT(e.id) AS event_count,
                COALESCE(SUM(e.accepted_unit_price), 0) AS accepted_price,
                COALESCE(SUM(e.sender_coin_amount), 0) AS sender_coin,
                COALESCE(SUM(e.recipient_diamond_amount), 0) AS recipient_diamond,
                COALESCE(SUM(e.base_recipient_diamond_amount), 0) AS base_diamond,
                COALESCE(SUM(CASE WHEN w.bus_type = 10000 AND w.user_id = g.user_id AND w.status = 1 THEN w.coin ELSE 0 END), 0) AS sender_debit,
                SUM(CASE WHEN w.bus_type = 10000 AND w.user_id = g.user_id AND w.status = 1 THEN 1 ELSE 0 END) AS sender_debit_count,
                SUM(CASE WHEN w.bus_type = 40002 AND w.status = 1 THEN 1 ELSE 0 END) AS diamond_log_count,
                COALESCE(SUM(CASE WHEN w.bus_type = 40002 AND w.status = 1 THEN w.diamond ELSE 0 END), 0) AS diamond_paid
            FROM ln_give_gift g
            LEFT JOIN lucky_gift_draw_event e ON e.give_gift_id = g.id
            LEFT JOIN ln_wallet_log w ON w.bus_id = g.id AND w.bus_type IN (10000, 40002)
            WHERE g.type IN (35, 36) AND (g.user_id = %s OR g.gift_user = %s)
            GROUP BY g.id, g.user_id, g.gift_user, g.type, g.number, g.total_price
            ORDER BY g.id
            """,
            (user_id, user_id, user_id),
        )
        dump(cursor, "GIFT_RECONCILIATION")

        cursor.execute(
            """
            SELECT w.user_id, w.bus_type, w.status, COUNT(*) AS records,
                   SUM(w.coin) AS coin_total, SUM(w.diamond) AS diamond_total
            FROM ln_wallet_log w
            JOIN ln_give_gift g ON g.id = w.bus_id
            WHERE g.type IN (35, 36) AND (g.user_id = %s OR g.gift_user = %s)
            GROUP BY w.user_id, w.bus_type, w.status
            ORDER BY w.user_id, w.bus_type, w.status
            """,
            (user_id, user_id),
        )
        dump(cursor, "WALLET_BY_USER_TYPE")
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
