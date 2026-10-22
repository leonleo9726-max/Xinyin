from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

import mysql.connector
import redis


ROOT = Path(__file__).resolve().parent.parent
RTP_KEY = "lucky_gift:config:rtp"
REDIS_DATABASES = (7, 10)
TABLES = (
    "lucky_io_day_agg",
    "lucky_gift_report_projection",
    "lucky_gift_draw_event",
    "lucky_gift_rtp_config",
)


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
    if label.startswith("SHOW_"):
        print(f"{label}_FIELDS: {','.join(str(row['Field']) for row in rows)}")
    for row in rows[:3]:
        print(f"{label}_SAMPLE: {row}")
    return rows


def redis_client(settings: dict[str, str], database: int) -> redis.Redis:
    redis_url = settings.get("REDIS_URL")
    if redis_url:
        parsed = urlparse(redis_url)
        return redis.Redis(
            host=parsed.hostname,
            port=parsed.port or 6379,
            username=unquote(parsed.username) if parsed.username else None,
            password=unquote(parsed.password) if parsed.password else None,
            db=database,
            ssl=parsed.scheme == "rediss",
            decode_responses=True,
            socket_connect_timeout=10,
        )
    return redis.Redis(
        host=settings["REDIS_HOST"],
        port=int(settings["REDIS_PORT"]),
        password=settings.get("REDIS_PASSWORD") or None,
        db=database,
        decode_responses=True,
        socket_connect_timeout=10,
    )


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
        schemas: dict[str, set[str]] = {}
        for table in TABLES:
            cursor.execute(f"SHOW COLUMNS FROM `{table}`")
            schemas[table] = {row["Field"] for row in dump(cursor, f"SHOW_{table.upper()}")}

        required = {
            "valid_wager_coin",
            "giver_return_coin",
            "single_wager_coin",
            "single_giver_return_coin",
            "double_wager_coin",
            "double_giver_return_coin",
            "stat_date",
        }
        missing = sorted(required - schemas["lucky_io_day_agg"])
        if missing:
            print(f"ERROR: missing lucky_io_day_agg fields: {','.join(missing)}")
            return 2

        cursor.execute(
            """
            SELECT *
            FROM lucky_io_day_agg
            WHERE stat_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 29 DAY) AND CURDATE()
            ORDER BY stat_date
            """
        )
        dump(cursor, "DAILY_PLATFORM_DATA")

        cursor.execute(
            """
            SELECT play_mode, projection_state, report_eligible, exclusion_reason,
                   COUNT(*) AS projection_count,
                   COALESCE(SUM(valid_wager_coin), 0) AS valid_wager_coin,
                   COALESCE(SUM(giver_return_coin), 0) AS giver_return_coin
            FROM lucky_gift_report_projection
            WHERE stat_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 29 DAY) AND CURDATE()
            GROUP BY play_mode, projection_state, report_eligible, exclusion_reason
            ORDER BY play_mode, projection_state, report_eligible, exclusion_reason
            """
        )
        dump(cursor, "PROJECTION_SUMMARY")

        if "double_receiver_coin_equiv" in schemas["lucky_io_day_agg"]:
            coin_equiv_cte = """
                SELECT stat_date, double_receiver_coin_equiv
                FROM lucky_io_day_agg
                WHERE stat_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 29 DAY) AND CURDATE()
            """
            coin_equiv_source = "lucky_io_day_agg"
        else:
            coin_equiv_cte = """
                SELECT p.stat_date,
                       COALESCE(SUM(
                           FLOOR(GREATEST(
                               e.recipient_diamond_amount - FLOOR(e.accepted_unit_price * 0.2),
                               0
                           ) / 5)
                       ), 0) AS double_receiver_coin_equiv
                FROM lucky_gift_report_projection p
                INNER JOIN lucky_gift_draw_event e ON e.give_gift_id = p.give_gift_id
                WHERE p.stat_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 29 DAY) AND CURDATE()
                  AND p.play_mode = 2
                  AND p.projection_state = 1
                  AND p.report_eligible = 1
                  AND e.play_type = 'BILATERAL'
                GROUP BY p.stat_date
            """
            coin_equiv_source = "draw_event_fallback"

        non_final_expression = "SUM(i.is_final = 0)" if "is_final" in schemas["lucky_io_day_agg"] else "0"
        cursor.execute(
            f"""
            WITH coin_equiv_by_day AS ({coin_equiv_cte}), aggregate_window AS (
                SELECT
                    COUNT(*) AS aggregation_day_count,
                    {non_final_expression} AS non_final_day_count,
                    COALESCE(SUM(i.valid_wager_coin), 0) AS total_valid_wager_coin,
                    COALESCE(SUM(i.giver_return_coin), 0) AS total_giver_return_coin,
                    COALESCE(SUM(i.single_wager_coin), 0) AS single_wager_coin,
                    COALESCE(SUM(i.single_giver_return_coin), 0) AS single_giver_return_coin,
                    COALESCE(SUM(i.double_wager_coin), 0) AS double_wager_coin,
                    COALESCE(SUM(i.double_giver_return_coin), 0) AS double_giver_return_coin,
                    COALESCE(SUM(c.double_receiver_coin_equiv), 0) AS double_receiver_coin_equiv,
                    MAX(i.source_max_settled_at) AS source_max_settled_at,
                    MAX(i.updated_at) AS updated_at
                FROM lucky_io_day_agg i
                LEFT JOIN coin_equiv_by_day c ON c.stat_date = i.stat_date
                WHERE i.stat_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 29 DAY) AND CURDATE()
            )
            SELECT
                DATE_SUB(CURDATE(), INTERVAL 29 DAY) AS window_start,
                CURDATE() AS window_end,
                a.*,
                ROUND((a.total_giver_return_coin + a.double_receiver_coin_equiv) /
                    NULLIF(a.total_valid_wager_coin, 0) * 100, 4) AS overall_rtp_pct,
                ROUND(a.single_giver_return_coin / NULLIF(a.single_wager_coin, 0) * 100, 4)
                    AS non_bilateral_rtp_pct,
                ROUND(a.double_giver_return_coin / NULLIF(a.double_wager_coin, 0) * 100, 4)
                    AS bilateral_giver_rtp_pct,
                ROUND((a.double_giver_return_coin + a.double_receiver_coin_equiv) /
                    NULLIF(a.double_wager_coin, 0) * 100, 4) AS bilateral_platform_rtp_pct,
                %s AS coin_equiv_source
            FROM aggregate_window a
            """,
            (coin_equiv_source,),
        )
        dump(cursor, "THIRTY_DAY_PLATFORM_RTP")

        cursor.execute("SELECT * FROM lucky_gift_rtp_config WHERE id = 1")
        dump(cursor, "MYSQL_RTP_CONFIG")
    finally:
        connection.close()

    for database in REDIS_DATABASES:
        client = redis_client(settings, database)
        try:
            print(f"REDIS_DATABASE: {database}")
            print(f"REDIS_KEY: {RTP_KEY}")
            print(f"REDIS_EXISTS: {bool(client.exists(RTP_KEY))}")
            print(f"REDIS_TTL: {client.ttl(RTP_KEY)}")
            print(f"REDIS_CONFIG: {client.hgetall(RTP_KEY)}")
        finally:
            client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
