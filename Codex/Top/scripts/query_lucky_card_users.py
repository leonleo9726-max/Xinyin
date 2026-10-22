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


def output(cursor: mysql.connector.cursor.MySQLCursor, label: str) -> None:
    columns = [item[0] for item in cursor.description]
    rows = cursor.fetchall()
    print(f"{label}_COLUMNS: {','.join(columns)}")
    print(f"{label}_COUNT: {len(rows)}")
    for row in rows:
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
        output(cursor, "SHOW_LUCKY_CARD_GRANT_RECORD")
        cursor.execute("SHOW COLUMNS FROM ln_user")
        output(cursor, "SHOW_LN_USER")
        cursor.execute(
            """
            SELECT u.user_id, u.user_no, u.tel_code, u.mobile,
                   COUNT(c.id) AS card_record_count
            FROM lucky_card_grant_record c
            JOIN ln_user u ON u.user_id = c.user_id
            GROUP BY u.user_id, u.user_no, u.tel_code, u.mobile
            ORDER BY u.user_id
            """
        )
        output(cursor, "CARD_USERS")
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
