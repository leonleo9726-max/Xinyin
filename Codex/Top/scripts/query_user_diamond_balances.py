from __future__ import annotations

from pathlib import Path
from typing import Any

import mysql.connector


ROOT = Path(__file__).resolve().parent.parent
USER_NOS = ("4610696", "1550893")


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def dump(cursor: mysql.connector.cursor.MySQLCursor, label: str) -> list[dict[str, Any]]:
    columns = [column[0] for column in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    print(f"{label}_COLUMNS: {','.join(columns)}")
    print(f"{label}_COUNT: {len(rows)}")
    if label.startswith("SHOW_"):
        print(f"{label}_FIELDS: {','.join(str(row['Field']) for row in rows)}")
    if label == "SHOW_USER_WALLETS":
        print(f"{label}_SCHEMA: {rows}")
    for row in rows[:3]:
        print(f"{label}_SAMPLE: {row}")
    return rows


def main() -> int:
    settings = load_env()
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
        cursor.execute("SHOW COLUMNS FROM ln_user")
        dump(cursor, "SHOW_LN_USER")
        cursor.execute(
            """
            SELECT table_schema, table_name,
                   GROUP_CONCAT(column_name ORDER BY ordinal_position) AS columns_found
            FROM information_schema.columns
            WHERE table_schema NOT IN ('information_schema', 'mysql', 'performance_schema', 'sys')
              AND (column_name = 'user_id' OR column_name = 'balance' OR column_name LIKE '%diamond%')
            GROUP BY table_schema, table_name
            HAVING SUM(column_name = 'user_id') > 0
               AND SUM(column_name LIKE '%diamond%') > 0
            ORDER BY table_schema, table_name
            """
        )
        candidates = dump(cursor, "DIAMOND_TABLE_CANDIDATES")
        if not candidates:
            print("ERROR: no current-diamond table found")
            return 2

        current_balance_tables = [
            row
            for row in candidates
            if str(row["TABLE_NAME"]).lower() in {"user_wallet", "user_wallets"}
        ]
        if len(current_balance_tables) != 1:
            print("ERROR: current diamond-balance table not uniquely identified")
            return 2

        wallet_schema_name = str(current_balance_tables[0]["TABLE_SCHEMA"])
        wallet_table = str(current_balance_tables[0]["TABLE_NAME"])
        print(f"CURRENT_DIAMOND_TABLE: {wallet_schema_name}.{wallet_table}")
        cursor.execute(f"SHOW COLUMNS FROM `{wallet_schema_name}`.`{wallet_table}`")
        wallet_schema = dump(cursor, f"SHOW_{wallet_table.upper()}")
        wallet_columns = {row["Field"] for row in wallet_schema}
        required = {"user_id", "diamond"}
        missing = sorted(required - wallet_columns)
        if missing:
            print(f"ERROR: {wallet_table} missing fields: {','.join(missing)}")
            return 2

        cursor.execute("SHOW COLUMNS FROM ln_wallet_log")
        dump(cursor, "SHOW_LN_WALLET_LOG")

        marks = ",".join(["%s"] * len(USER_NOS))
        cursor.execute(
            f"""
            SELECT u.user_no, u.user_id, u.money_1111, u.earnings_1111
            FROM ln_user u
            WHERE u.user_no IN ({marks})
            ORDER BY u.user_no
            """,
            USER_NOS,
        )
        users = dump(cursor, "USER_ACCOUNT_FIELDS")
        if not users:
            return 0

        cursor.execute(
            f"""
            WITH latest_diamond_log AS (
                SELECT user_id, balance, created_at,
                       ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY id DESC) AS row_num
                FROM ln_wallet_log
                WHERE status = 1 AND diamond <> 0
            )
            SELECT u.user_no, u.user_id, w.diamond AS wallet_diamond,
                   d.balance AS fallback_diamond_snapshot,
                   d.created_at AS fallback_snapshot_at,
                   COALESCE(w.diamond, d.balance) AS diamond,
                   CASE
                       WHEN w.user_id IS NOT NULL THEN 'pay.user_wallets.diamond'
                       WHEN d.user_id IS NOT NULL THEN 'ln_wallet_log.balance fallback'
                       ELSE 'no balance source'
                   END AS balance_source
            FROM ln_user u
            LEFT JOIN `{wallet_schema_name}`.`{wallet_table}` w ON w.user_id = u.user_id
            LEFT JOIN latest_diamond_log d ON d.user_id = u.user_id AND d.row_num = 1
            WHERE u.user_no IN ({marks})
            ORDER BY u.user_no
            """,
            USER_NOS,
        )
        dump(cursor, "USER_DIAMOND_BALANCES")
        return 0
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
