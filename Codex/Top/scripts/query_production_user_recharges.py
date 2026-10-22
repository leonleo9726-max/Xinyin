from __future__ import annotations

from pathlib import Path
import sys

import mysql.connector


USER_NO = "8063006"
PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHANNEL_NAMES = {
    1: "Apple Pay",
    2: "Google Pay",
    3: "PayPal",
    4: "Bank",
}


def load_env(path: Path) -> dict[str, str]:
    settings: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        settings[name.strip()] = value.strip().strip('"').strip("'")
    return settings


def print_rows(label: str, cursor: mysql.connector.cursor.MySQLCursor) -> list[dict[str, object]]:
    columns = [column[0] for column in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    print(f"{label}_COLUMNS: {','.join(columns)}")
    print(f"{label}_ROW_COUNT: {len(rows)}")
    for row in rows:
        print(f"{label}_ROW: {row}")
    return rows


def main() -> int:
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
        for table in ("app.ln_user", "app.user_recharge_orders"):
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            print_rows(f"SHOW_{table.replace('.', '_').upper()}", cursor)

        cursor.execute(
            """
            SELECT user_id, user_no
            FROM app.ln_user
            WHERE user_no = %s
            """,
            (USER_NO,),
        )
        users = print_rows("USER", cursor)
        if not users:
            return 0
        user_id = users[0]["user_id"]

        cursor.execute(
            """
            SELECT
                channel,
                state,
                COUNT(*) AS order_count,
                COALESCE(SUM(CAST(price AS DECIMAL(20, 2))), 0) AS total_price,
                COALESCE(SUM(coin), 0) AS total_coin
            FROM app.user_recharge_orders
            WHERE user_id = %s
            GROUP BY channel, state
            ORDER BY channel, state
            """,
            (user_id,),
        )
        print_rows("RECHARGE_SUMMARY", cursor)

        cursor.execute(
            """
            SELECT
                id, order_id, remote_order_id, channel, product_id, price,
                coin, `desc`, state, created_at, updated_at, deleted_at
            FROM app.user_recharge_orders
            WHERE user_id = %s
            ORDER BY created_at DESC, id DESC
            """,
            (user_id,),
        )
        rows = print_rows("RECHARGE_ORDER", cursor)
        for row in rows:
            channel = row["channel"]
            print(f"CHANNEL_NAME: {channel}={CHANNEL_NAMES.get(channel, '待确认渠道')}")
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
