from __future__ import annotations

from pathlib import Path

import mysql.connector


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in (PROJECT_ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def print_result(cursor: mysql.connector.cursor.MySQLCursor, label: str) -> None:
    columns = [column[0] for column in cursor.description]
    rows = cursor.fetchall()
    print(f"{label}_COLUMNS: {','.join(columns)}")
    print(f"{label}_COUNT: {len(rows)}")
    for row in rows[:3]:
        print(f"{label}: {dict(zip(columns, row))}")


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
        cursor.execute("SHOW COLUMNS FROM lucky_card_grant_record")
        print_result(cursor, "SHOW_LUCKY_CARD_GRANT_RECORD")
        cursor.execute(
            """
            SELECT COUNT(*) AS record_count,
                   COUNT(DISTINCT user_id) AS user_count,
                   MIN(business_date) AS first_business_date,
                   MAX(business_date) AS last_business_date
            FROM lucky_card_grant_record
            """
        )
        print_result(cursor, "CARD_RECORD_SUMMARY")
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
