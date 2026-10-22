from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import mysql.connector


ROOT = Path(__file__).resolve().parent.parent
TABLE_NAME = "ln_user"


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
    for row in rows[:3]:
        print(f"{label}_SAMPLE: {json.dumps(row, ensure_ascii=True, default=str)}")
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

        cursor.execute(f"SHOW COLUMNS FROM `{TABLE_NAME}`")
        dump(cursor, "SHOW_LN_USER")

        cursor.execute(
            """
            SELECT column_name, column_comment, HEX(column_comment) AS comment_hex
            FROM information_schema.columns
            WHERE table_schema = DATABASE() AND table_name = %s
              AND column_comment LIKE '%?%'
            ORDER BY ordinal_position
            """,
            (TABLE_NAME,),
        )
        dump(cursor, "LN_USER_QUESTION_MARK_COMMENTS")

        cursor.execute(
            """
            SELECT table_name,
                   COUNT(*) AS questioned_column_count,
                   SUM(CHAR_LENGTH(column_comment)) AS questioned_comment_char_count,
                   SUM(LENGTH(column_comment) - LENGTH(REPLACE(column_comment, '?', '')))
                       AS question_mark_count
            FROM information_schema.columns
            WHERE table_schema = DATABASE() AND column_comment LIKE '%?%'
            GROUP BY table_name
            ORDER BY questioned_column_count DESC, table_name
            """
        )
        dump(cursor, "DATABASE_QUESTION_MARK_COMMENT_SUMMARY")

        cursor.execute(
            """
            SELECT table_comment, HEX(table_comment) AS table_comment_hex
            FROM information_schema.tables
            WHERE table_schema = DATABASE() AND table_name = %s
            """,
            (TABLE_NAME,),
        )
        dump(cursor, "LN_USER_TABLE_COMMENT")
        return 0
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
