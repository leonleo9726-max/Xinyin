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


def dump(
    cursor: mysql.connector.cursor.MySQLCursor, label: str, preview_limit: int = 3
) -> list[dict[str, Any]]:
    columns = [column[0] for column in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    print(f"{label}_COLUMNS: {','.join(columns)}")
    print(f"{label}_ROW_COUNT: {len(rows)}")
    for row in rows[:preview_limit]:
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
        cursor.execute("SHOW COLUMNS FROM app.ln_anchor_apply")
        anchor_apply_columns = dump(
            cursor, "SHOW_APP_LN_ANCHOR_APPLY", preview_limit=100
        )
        cursor.execute("SHOW COLUMNS FROM guild.guild_member_apply")
        dump(cursor, "SHOW_GUILD_MEMBER_APPLY")
        cursor.execute("SHOW COLUMNS FROM guild.guild_advance_record")
        dump(cursor, "SHOW_GUILD_ADVANCE_RECORD")
        cursor.execute("SHOW COLUMNS FROM guild.guild_withdraw_apply")
        withdraw_apply_columns = dump(
            cursor, "SHOW_GUILD_WITHDRAW_APPLY", preview_limit=100
        )

        cursor.execute(
            "SELECT user_no, user_id FROM app.ln_user WHERE user_no = %s",
            (USER_NO,),
        )
        users = dump(cursor, "USER")
        if not users:
            return 0
        user_id = users[0]["user_id"]

        anchor_fields = {str(row["Field"]) for row in anchor_apply_columns}
        anchor_preferred_fields = (
            "id",
            "user_id",
            "audit_status",
            "audit_time",
            "created_at",
            "updated_at",
        )
        if not {"user_id", "audit_status"}.issubset(anchor_fields):
            print("ERROR: anchor application table lacks user_id or audit_status", file=sys.stderr)
            return 2
        anchor_selected = ", ".join(
            f"`{field}`" for field in anchor_preferred_fields if field in anchor_fields
        )
        cursor.execute(
            f"""
            SELECT {anchor_selected}
            FROM app.ln_anchor_apply
            WHERE user_id = %s
            ORDER BY id DESC
            """,
            (user_id,),
        )
        dump(cursor, "ANCHOR_APPLICATIONS")

        cursor.execute(
            """
            SELECT id, apply_no, guild_id, user_id, pending_user_id, apply_type,
                   policy_type, apply_status, expired_at, created_at
            FROM guild.guild_member_apply
            WHERE (user_id = %s OR pending_user_id = %s) AND apply_status = 1
            ORDER BY id DESC
            """,
            (user_id, user_id),
        )
        dump(cursor, "PENDING_GUILD_APPLICATIONS")

        cursor.execute(
            """
            SELECT id, advance_no, guild_id, debtor_user_id, receiver_user_id,
                   advance_type, advance_amount, issue_currency, advance_status,
                   created_at
            FROM guild.guild_advance_record
            WHERE (debtor_user_id = %s OR receiver_user_id = %s) AND advance_status = 1
            ORDER BY id DESC
            """,
            (user_id, user_id),
        )
        dump(cursor, "PENDING_ADVANCE_RECORDS")

        available_fields = {str(row["Field"]) for row in withdraw_apply_columns}
        preferred_fields = (
            "id",
            "apply_no",
            "withdraw_no",
            "order_no",
            "user_id",
            "guild_id",
            "apply_amount",
            "withdraw_amount",
            "amount",
            "audit_status",
            "status",
            "audited_at",
            "audit_time",
            "created_at",
            "updated_at",
        )
        selected_fields = [field for field in preferred_fields if field in available_fields]
        if not {"user_id", "audit_status"}.issubset(available_fields):
            print("ERROR: guild withdrawal table lacks user_id or audit_status", file=sys.stderr)
            return 2
        selected_sql = ", ".join(f"`{field}`" for field in selected_fields)
        cursor.execute(
            f"""
            SELECT {selected_sql}
            FROM guild.guild_withdraw_apply
            WHERE user_id = %s
            ORDER BY id DESC
            """,
            (user_id,),
        )
        dump(cursor, "GUILD_WITHDRAW_APPLICATIONS")
        return 0
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
