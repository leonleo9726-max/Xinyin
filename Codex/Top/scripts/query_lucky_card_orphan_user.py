from __future__ import annotations

from pathlib import Path

import mysql.connector


ROOT = Path(__file__).resolve().parent.parent


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


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
        print(f"CARD_COLUMNS: {','.join(column[0] for column in cursor.description)}")
        cursor.fetchall()
        cursor.execute("SHOW COLUMNS FROM ln_user")
        print(f"USER_COLUMNS: {','.join(column[0] for column in cursor.description)}")
        cursor.fetchall()
        cursor.execute(
            """
            SELECT c.user_id, COUNT(*) AS card_record_count,
                   MIN(c.business_date) AS first_business_date,
                   MAX(c.business_date) AS last_business_date
            FROM lucky_card_grant_record c
            LEFT JOIN ln_user u ON u.user_id = c.user_id
            WHERE u.user_id IS NULL
            GROUP BY c.user_id
            ORDER BY c.user_id
            """
        )
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            print(f"ORPHAN_CARD_USER: {dict(zip(columns, row))}")
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
