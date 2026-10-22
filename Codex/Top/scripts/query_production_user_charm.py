from __future__ import annotations

from pathlib import Path
import sys

import mysql.connector


USER_NO = "6873721"
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


def print_rows(
    label: str,
    cursor: mysql.connector.cursor.MySQLCursor,
    row_limit: int = 3,
) -> list[tuple[object, ...]]:
    columns = [column[0] for column in cursor.description]
    rows = cursor.fetchall()
    print(f"{label}_COLUMNS: {','.join(columns)}")
    print(f"{label}_ROW_COUNT: {len(rows)}")
    for row in rows[:row_limit]:
        print(f"{label}_ROW: {dict(zip(columns, row))}")
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
        cursor.execute("SHOW COLUMNS FROM app.ln_user_data")
        print_rows("SHOW_APP_LN_USER_DATA", cursor, row_limit=100)
        cursor.execute("SHOW COLUMNS FROM app.ln_user_exp")
        print_rows("SHOW_APP_LN_USER_EXP", cursor, row_limit=100)
        cursor.execute("SHOW COLUMNS FROM app.ln_user_charm_exp")
        print_rows("SHOW_APP_LN_USER_CHARM_EXP", cursor, row_limit=100)
        cursor.execute(
            """
            SELECT user_id, user_code
            FROM app.ln_user_data
            WHERE user_code = %s
            """,
            (USER_NO,),
        )
        mapped_users = print_rows("USER_MAPPING", cursor)
        if not mapped_users:
            print("USER_NOT_FOUND")
            return 0

        user_id = mapped_users[0][0]
        cursor.execute(
            "SELECT COALESCE(SUM(exp), 0) AS wealth_value FROM app.ln_user_exp WHERE user_id = %s",
            (user_id,),
        )
        print_rows("WEALTH_VALUE", cursor)
        cursor.execute(
            "SELECT COALESCE(SUM(exp), 0) AS charm_value FROM app.ln_user_charm_exp WHERE user_id = %s",
            (user_id,),
        )
        print_rows("CHARM_VALUE", cursor)
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
