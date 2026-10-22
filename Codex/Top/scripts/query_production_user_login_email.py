from __future__ import annotations

from pathlib import Path
import sys

import mysql.connector


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_env(path: Path) -> dict[str, str]:
    settings: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            settings[key.strip()] = value.strip().strip('"').strip("'")
    return settings


def print_rows(label: str, cursor: mysql.connector.cursor.MySQLCursor) -> list[dict[str, object]]:
    columns = [column[0] for column in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    print(f"{label}_COLUMNS: {','.join(columns)}")
    print(f"{label}_ROW_COUNT: {len(rows)}")
    for row in rows[:3]:
        print(f"{label}_ROW: {row}")
    return rows


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        raise SystemExit("Usage: query_production_user_login_email.py USER_NO")
    user_no = sys.argv[1]
    settings = load_env(PROJECT_ROOT / ".env")
    required = (
        "PROD_MYSQL_HOST",
        "PROD_MYSQL_PORT",
        "PROD_MYSQL_USER",
        "PROD_MYSQL_PASSWORD",
        "PROD_MYSQL_DATABASE",
    )
    missing = [key for key in required if not settings.get(key)]
    if missing:
        print(f"Missing production settings: {', '.join(missing)}", file=sys.stderr)
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
        cursor.execute("SHOW COLUMNS FROM app.ln_user")
        columns = print_rows("SHOW_APP_LN_USER", cursor)
        field_names = {str(row["Field"]) for row in columns}
        email_field = next(
            (field for field in ("email", "login_email", "mail") if field in field_names),
            None,
        )
        if email_field is None:
            print("LOGIN_EMAIL_FIELD_NOT_FOUND")
            return 0
        cursor.execute(
            f"SELECT user_id, user_no, {email_field} AS login_email "
            "FROM app.ln_user WHERE user_no = %s",
            (user_no,),
        )
        print_rows("USER_LOGIN_EMAIL", cursor)
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
