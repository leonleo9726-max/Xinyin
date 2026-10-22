from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

import mysql.connector


USER_NO = "4158590"
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


def fetch_rows(
    cursor: mysql.connector.cursor.MySQLCursor,
    label: str,
    query: str,
    params: tuple[Any, ...] = (),
) -> list[dict[str, Any]]:
    cursor.execute(query, params)
    columns = [column[0] for column in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    print(f"{label}_COLUMNS: {','.join(columns)}")
    print(f"{label}_ROW_COUNT: {len(rows)}")
    for row in rows[:3]:
        print(f"{label}_ROW: {row}")
    return rows


def table_columns(
    cursor: mysql.connector.cursor.MySQLCursor, qualified_table: str
) -> set[str]:
    cursor.execute(f"SHOW COLUMNS FROM {qualified_table}")
    rows = cursor.fetchall()
    fields = [str(row[0]) for row in rows]
    print(f"SHOW_{qualified_table.replace('.', '_').upper()}_COLUMNS: Field,Type,Null,Key,Default,Extra")
    print(f"SHOW_{qualified_table.replace('.', '_').upper()}_ROW_COUNT: {len(rows)}")
    for row in rows[:3]:
        print(f"SHOW_{qualified_table.replace('.', '_').upper()}_ROW: {row}")
    for row in rows[3:]:
        if row[0] == "identity":
            print(f"SHOW_{qualified_table.replace('.', '_').upper()}_IDENTITY_ROW: {row}")
    return set(fields)


def main() -> int:
    settings = load_env(PROJECT_ROOT / ".env")
    required = ("MYSQL_HOST", "MYSQL_PORT", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE")
    missing = [name for name in required if not settings.get(name)]
    if missing:
        print(f"Missing required test settings: {', '.join(missing)}", file=sys.stderr)
        return 2

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
        print("ENVIRONMENT: test (MYSQL_* settings)")
        print(f"DATABASE: {settings['MYSQL_DATABASE']}")

        schemas = {
            table: table_columns(cursor, table)
            for table in (
                "ln_user",
                "ln_user_data",
                "ln_anchor_apply",
                "guild.guild_member",
                "guild.guild_info",
            )
        }

        user_fields = ["user_id", "user_no", "role", "is_coin_agent", "disabled", "deleted"]
        if "identity" in schemas["ln_user"]:
            user_fields.append("identity")
        users = fetch_rows(
            cursor,
            "USER",
            f"SELECT {', '.join(user_fields)} FROM ln_user WHERE user_no = %s",
            (USER_NO,),
        )
        if not users:
            fetch_rows(
                cursor,
                "USER_DATA_FALLBACK",
                """
                SELECT user_id, user_code, nickname, anchor_type, is_internal_staff
                FROM ln_user_data
                WHERE user_code = %s
                """,
                (USER_NO,),
            )
            return 0

        user_id = users[0]["user_id"]
        fetch_rows(
            cursor,
            "USER_DATA",
            """
            SELECT user_id, user_code, nickname, anchor_type, anchor_level,
                   is_anchor_mvp, is_internal_staff, yzh_sign_status
            FROM ln_user_data
            WHERE user_id = %s
            """,
            (user_id,),
        )
        fetch_rows(
            cursor,
            "ANCHOR_APPLY",
            """
            SELECT id, user_id, skill, audit_status, attestation_status,
                   attestation_at, audit_time, deleted_at
            FROM ln_anchor_apply
            WHERE user_id = %s
            ORDER BY id DESC
            """,
            (user_id,),
        )
        fetch_rows(
            cursor,
            "GUILD_MEMBERSHIPS",
            """
            SELECT gm.id AS membership_id, gm.guild_id, gi.guild_no, gi.guild_name,
                   gm.member_role, gm.member_status, gi.guild_status,
                   gm.joined_at, gm.left_at
            FROM guild.guild_member gm
            LEFT JOIN guild.guild_info gi ON gi.id = gm.guild_id
            WHERE gm.user_id = %s
            ORDER BY gm.id DESC
            """,
            (user_id,),
        )
        fetch_rows(
            cursor,
            "OWNED_GUILDS",
            """
            SELECT id AS guild_id, guild_no, guild_name, owner_user_id, guild_status
            FROM guild.guild_info
            WHERE owner_user_id = %s
            ORDER BY id DESC
            """,
            (user_id,),
        )

        raw_identity = users[0].get("identity")
        if isinstance(raw_identity, str) and raw_identity:
            try:
                print(f"PARSED_STORED_IDENTITIES: {json.loads(raw_identity)}")
            except json.JSONDecodeError:
                print(f"PARSED_STORED_IDENTITIES: INVALID_JSON ({raw_identity!r})")
        else:
            print(f"PARSED_STORED_IDENTITIES: {raw_identity}")
        return 0
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
