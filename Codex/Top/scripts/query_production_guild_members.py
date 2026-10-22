from __future__ import annotations

import json
import sys
from pathlib import Path

import mysql.connector


ROOT = Path(__file__).resolve().parent.parent
TABLES = ("guild.guild_info", "guild.guild_member", "app.ln_user")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def load_env() -> dict[str, str]:
    values = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def rows(cursor: mysql.connector.cursor.MySQLCursor) -> list[dict[str, object]]:
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        raise SystemExit("Usage: query_production_guild_members.py <guild_no>")
    settings = load_env()
    if settings.get("PROD_MYSQL_READ_ONLY", "").lower() != "true":
        raise SystemExit("PROD_MYSQL_READ_ONLY must be true")
    required = ("HOST", "PORT", "USER", "PASSWORD", "DATABASE")
    missing = [name for name in required if not settings.get(f"PROD_MYSQL_{name}")]
    if missing:
        raise SystemExit(f"Missing production settings: {', '.join(missing)}")

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
        connection.start_transaction(readonly=True, consistent_snapshot=True)
        actual_columns = {}
        for table in TABLES:
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            actual_columns[table] = {row[0] for row in cursor.fetchall()}
        expected_columns = {
            "guild.guild_info": {"id", "guild_no", "guild_name", "guild_status"},
            "guild.guild_member": {"guild_id", "user_id", "member_status", "member_role"},
            "app.ln_user": {"user_id", "user_no", "tel_code", "mobile"},
        }
        for table, expected in expected_columns.items():
            if missing_columns := expected - actual_columns[table]:
                raise RuntimeError(f"{table} missing columns: {sorted(missing_columns)}")

        cursor.execute(
            "SELECT id, guild_no, guild_name, guild_status "
            "FROM guild.guild_info WHERE guild_no = %s",
            (int(sys.argv[1]),),
        )
        guilds = rows(cursor)
        if len(guilds) != 1:
            print(json.dumps({"guild_count": len(guilds)}, ensure_ascii=False))
            return 1
        guild = guilds[0]

        cursor.execute(
            "SELECT member_status, COUNT(*) AS count FROM guild.guild_member "
            "WHERE guild_id = %s GROUP BY member_status ORDER BY member_status",
            (guild["id"],),
        )
        status_counts = rows(cursor)
        cursor.execute(
            "SELECT gm.user_id, u.user_no, u.tel_code, u.mobile, gm.member_role "
            "FROM guild.guild_member AS gm "
            "LEFT JOIN app.ln_user AS u ON u.user_id = gm.user_id "
            "WHERE gm.guild_id = %s AND gm.member_status = 2 "
            "ORDER BY CAST(u.user_no AS UNSIGNED), gm.user_id",
            (guild["id"],),
        )
        members = rows(cursor)
        connection.rollback()
        print(json.dumps({"guild": guild, "status_counts": status_counts,
                          "columns": list(members[0]) if members else [],
                          "members": members}, ensure_ascii=False, default=str))
        return 0
    finally:
        connection.close()


if __name__ == "__main__":
    sys.exit(main())
