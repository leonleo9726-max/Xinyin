from __future__ import annotations

from pathlib import Path
import sys
from typing import Any
from urllib.parse import unquote, urlparse

import mysql.connector
import redis


USER_NO = "6658169"
ROOT = Path(__file__).resolve().parent.parent
TABLES = (
    "ln_user",
    "lucky_user_mode_day_agg",
    "lucky_daily_participant",
    "lucky_io_day_agg",
    "lucky_gift_rtp_config",
    "lucky_gift_report_projection",
)


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def dump(cursor: mysql.connector.cursor.MySQLCursor, label: str) -> list[dict[str, Any]]:
    columns = [item[0] for item in cursor.description]
    result = [dict(zip(columns, row)) for row in cursor.fetchall()]
    print(f"{label}_COLUMNS: {','.join(columns)}")
    print(f"{label}_COUNT: {len(result)}")
    for row in result[:3]:
        print(f"{label}_SAMPLE: {row}")
    return result


def show_columns(cursor: mysql.connector.cursor.MySQLCursor, table: str) -> list[str]:
    cursor.execute(f"SHOW COLUMNS FROM `{table}`")
    return [row[0] for row in cursor.fetchall()]


def fetch_today(
    cursor: mysql.connector.cursor.MySQLCursor,
    table: str,
    columns: list[str],
    user_id: int | None,
) -> list[dict[str, Any]]:
    conditions: list[str] = []
    params: list[Any] = []
    if "stat_date" in columns:
        conditions.append("stat_date = CURDATE()")
    elif "business_date" in columns:
        conditions.append("business_date = CURDATE()")
    if user_id is not None:
        if "user_id" in columns:
            conditions.append("user_id = %s")
            params.append(user_id)
        elif "giver_user_id" in columns and "receiver_user_id" in columns:
            conditions.append("(giver_user_id = %s OR receiver_user_id = %s)")
            params.extend((user_id, user_id))
    statement = f"SELECT * FROM `{table}`"
    if conditions:
        statement += " WHERE " + " AND ".join(conditions)
    cursor.execute(statement, tuple(params))
    return dump(cursor, f"TODAY_{table.upper()}")


def main() -> int:
    settings = load_env(ROOT / ".env")
    required = ("MYSQL_HOST", "MYSQL_PORT", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE")
    missing = [key for key in required if not settings.get(key)]
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
        print(f"DATABASE: {settings['MYSQL_DATABASE']}")
        print("ENVIRONMENT: test (MYSQL_* settings)")
        cursor.execute("SELECT CURDATE() AS database_today")
        dump(cursor, "DATABASE_DATE")

        schemas = {table: show_columns(cursor, table) for table in TABLES}
        for table, columns in schemas.items():
            print(f"SHOW_{table.upper()}_COLUMNS: {','.join(columns)}")

        cursor.execute("SELECT user_id, user_no FROM ln_user WHERE user_no = %s", (USER_NO,))
        users = dump(cursor, "USER")
        if not users:
            print("SUMMARY: user_no not found in ln_user")
            return 0

        user_id = users[0]["user_id"]
        fetch_today(cursor, "lucky_user_mode_day_agg", schemas["lucky_user_mode_day_agg"], user_id)
        fetch_today(cursor, "lucky_daily_participant", schemas["lucky_daily_participant"], user_id)
        fetch_today(cursor, "lucky_io_day_agg", schemas["lucky_io_day_agg"], None)

        cursor.execute("SELECT * FROM lucky_gift_rtp_config WHERE id = 1")
        dump(cursor, "RTP_CONFIG")

        cursor.execute(
            """
            WITH aggregate_window AS (
                SELECT
                    SUM(valid_wager_coin) AS total_wager_coin,
                    SUM(giver_return_coin) AS total_giver_return_coin,
                    SUM(double_receiver_coin_equiv) AS total_double_receiver_coin_equiv,
                    SUM(single_wager_coin) AS single_wager_coin,
                    SUM(single_giver_return_coin) AS single_giver_return_coin,
                    SUM(double_wager_coin) AS double_wager_coin,
                    SUM(double_giver_return_coin) AS double_giver_return_coin,
                    SUM(is_final = 0) AS non_final_day_count,
                    MAX(source_max_settled_at) AS source_max_settled_at
                FROM lucky_io_day_agg
                WHERE stat_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 29 DAY) AND CURDATE()
            )
            SELECT
                DATE_SUB(CURDATE(), INTERVAL 29 DAY) AS window_start,
                CURDATE() AS window_end,
                a.*,
                ROUND(
                    (a.total_giver_return_coin + a.total_double_receiver_coin_equiv)
                    / NULLIF(a.total_wager_coin, 0) * 100,
                    4
                ) AS overall_rtp_pct,
                ROUND(a.single_giver_return_coin / NULLIF(a.single_wager_coin, 0) * 100, 4)
                    AS non_bilateral_rtp_pct,
                ROUND(a.double_giver_return_coin / NULLIF(a.double_wager_coin, 0) * 100, 4)
                    AS bilateral_giver_rtp_pct,
                ROUND(
                    (a.double_giver_return_coin + a.total_double_receiver_coin_equiv)
                    / NULLIF(a.double_wager_coin, 0) * 100,
                    4
                ) AS bilateral_platform_rtp_pct,
                c.overall_rtp_limit * 100 AS overall_rtp_limit_pct,
                c.non_bilateral_rtp_limit * 100 AS non_bilateral_rtp_limit_pct,
                c.bilateral_rtp_limit * 100 AS bilateral_rtp_limit_pct
            FROM aggregate_window a
            CROSS JOIN lucky_gift_rtp_config c
            WHERE c.id = 1
            """
        )
        dump(cursor, "RTP_30_DAY_WINDOW")

        fetch_today(cursor, "lucky_gift_report_projection", schemas["lucky_gift_report_projection"], user_id)
    finally:
        connection.close()

    key = "lucky_gift:config:rtp"
    databases = [7, 10]
    for database in databases:
        redis_url = settings.get("REDIS_URL")
        if redis_url:
            parsed = urlparse(redis_url)
            redis_client = redis.Redis(
                host=parsed.hostname,
                port=parsed.port or 6379,
                username=unquote(parsed.username) if parsed.username else None,
                password=unquote(parsed.password) if parsed.password else None,
                db=database,
                ssl=parsed.scheme == "rediss",
                decode_responses=True,
                socket_connect_timeout=10,
            )
        else:
            redis_client = redis.Redis(
                host=settings["REDIS_HOST"],
                port=int(settings["REDIS_PORT"]),
                password=settings.get("REDIS_PASSWORD") or None,
                db=database,
                decode_responses=True,
                socket_connect_timeout=10,
            )
        try:
            print(f"REDIS_DATABASE: {database}")
            print(f"REDIS_RTP_CONFIG_KEY: {key}")
            print(f"REDIS_RTP_CONFIG_TTL: {redis_client.ttl(key)}")
            print(f"REDIS_RTP_CONFIG: {redis_client.hgetall(key)}")
        finally:
            redis_client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
