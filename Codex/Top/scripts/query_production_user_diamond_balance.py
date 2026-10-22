from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import mysql.connector


USER_NO = "8063006"
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


def dump(cursor: mysql.connector.cursor.MySQLCursor, label: str) -> list[dict[str, Any]]:
    columns = [column[0] for column in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    print(f"{label}_COLUMNS: {','.join(columns)}")
    print(f"{label}_ROW_COUNT: {len(rows)}")
    for row in rows[:3]:
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
        print(f"DATABASE: {settings['PROD_MYSQL_DATABASE']}")
        print("ENVIRONMENT: production")

        cursor.execute("SHOW COLUMNS FROM app.ln_user")
        dump(cursor, "SHOW_APP_LN_USER")

        cursor.execute(
            "SELECT user_no, user_id FROM app.ln_user WHERE user_no = %s",
            (USER_NO,),
        )
        users = dump(cursor, "USER")
        if not users:
            return 0

        cursor.execute(
            """
            SELECT table_schema, table_name,
                   GROUP_CONCAT(column_name ORDER BY ordinal_position) AS columns_found
            FROM information_schema.columns
            WHERE table_schema NOT IN ('information_schema', 'mysql', 'performance_schema', 'sys')
              AND (column_name = 'user_id' OR column_name = 'diamond')
            GROUP BY table_schema, table_name
            HAVING SUM(column_name = 'user_id') > 0 AND SUM(column_name = 'diamond') > 0
            ORDER BY table_schema, table_name
            """
        )
        candidates = dump(cursor, "DIAMOND_TABLE_CANDIDATES")
        wallet_candidates = [
            row
            for row in candidates
            if str(row["TABLE_NAME"]).lower() in {"user_wallet", "user_wallets"}
        ]
        if len(wallet_candidates) != 1:
            print("ERROR: current diamond-balance table not uniquely identified", file=sys.stderr)
            return 2

        wallet_schema = str(wallet_candidates[0]["TABLE_SCHEMA"])
        wallet_table = str(wallet_candidates[0]["TABLE_NAME"])
        cursor.execute(f"SHOW COLUMNS FROM `{wallet_schema}`.`{wallet_table}`")
        wallet_columns = dump(cursor, "SHOW_WALLET")
        fields = {str(row["Field"]) for row in wallet_columns}
        if {"user_id", "diamond"} - fields:
            print("ERROR: wallet table lacks user_id or diamond", file=sys.stderr)
            return 2

        cursor.execute(
            f"SELECT user_id, diamond FROM `{wallet_schema}`.`{wallet_table}` WHERE user_id = %s",
            (users[0]["user_id"],),
        )
        dump(cursor, "DIAMOND_BALANCE")
        return 0
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
