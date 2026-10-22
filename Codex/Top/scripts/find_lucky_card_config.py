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
        cursor.execute("SHOW TABLES")
        table_names = [row[0] for row in cursor.fetchall()]
        matches = [
            table for table in table_names
            if "lucky" in table.lower() and ("card" in table.lower() or "config" in table.lower())
        ]
        print(f"MATCHED_TABLES: {','.join(matches)}")
        for table in matches:
            cursor.execute(f"SHOW COLUMNS FROM `{table}`")
            columns = [column[0] for column in cursor.description]
            print(f"TABLE: {table}")
            print(f"COLUMNS: {','.join(columns)}")
            for row in cursor.fetchall():
                print(f"COLUMN: {dict(zip(columns, row))}")
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
