from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import mysql.connector


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
        print(f"DATABASE: {settings['PROD_MYSQL_DATABASE']}")
        print("ENVIRONMENT: production")
        cursor.execute(
            """
            SELECT table_schema, table_name,
                   GROUP_CONCAT(column_name ORDER BY ordinal_position) AS columns_found
            FROM information_schema.columns
            WHERE table_schema NOT IN ('information_schema', 'mysql', 'performance_schema', 'sys')
              AND column_name IN (
                  'user_id', 'user_number', 'status', 'state', 'apply_status',
                  'audit_status', 'review_status', 'order_id', 'apply_no',
                  'order_no', 'created_at', 'audit_time', 'audited_at'
              )
              AND table_name REGEXP 'order|withdraw|apply|audit|exchange|cashout|advance'
            GROUP BY table_schema, table_name
            HAVING SUM(column_name IN ('user_id', 'user_number')) > 0
               AND SUM(column_name IN ('status', 'state', 'apply_status', 'audit_status', 'review_status')) > 0
            ORDER BY table_schema, table_name
            """
        )
        dump(cursor, "PENDING_ORDER_TABLE_CANDIDATES")
        return 0
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
