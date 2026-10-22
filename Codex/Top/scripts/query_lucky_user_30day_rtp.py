from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

import mysql.connector
import redis


ROOT = Path(__file__).resolve().parent.parent
USER_NO = "6658169"
RTP_KEY = "lucky_gift:config:rtp"
REDIS_DATABASES = (7, 10)
TABLES = (
    "ln_user",
    "ln_give_gift",
    "lucky_gift_draw_event",
    "ln_wallet_log",
    "lucky_gift_report_projection",
    "lucky_user_mode_day_agg",
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
        for table in TABLES:
            cursor.execute(f"SHOW COLUMNS FROM `{table}`")
            dump(cursor, f"SHOW_{table.upper()}")

        cursor.execute("SELECT user_id, user_no FROM ln_user WHERE user_no = %s", (USER_NO,))
        users = dump(cursor, "USER")
        if not users:
            return 0
        user_id = users[0]["user_id"]

        cursor.execute(
            """
            SELECT
                DATE_SUB(CURDATE(), INTERVAL 29 DAY) AS window_start,
                CURDATE() AS window_end,
                COALESCE(SUM(user_id = %s), 0) AS giver_lucky_gift_count,
                COALESCE(SUM(gift_user = %s), 0) AS recipient_lucky_gift_count
            FROM ln_give_gift
            WHERE type IN (35, 36)
              AND add_time >= UNIX_TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 29 DAY))
              AND add_time < UNIX_TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 1 DAY))
              AND (user_id = %s OR gift_user = %s)
            """,
            (user_id, user_id, user_id, user_id),
        )
        dump(cursor, "ROLE_COUNTS")

        cursor.execute(
            """
            SELECT give_gift_id, stat_date, play_mode, valid_wager_coin, giver_return_coin,
                   receiver_lucky_diamond, report_eligible, draw_event_count,
                   projection_state, exclusion_reason, source_settled_at
            FROM lucky_gift_report_projection
            WHERE giver_user_id = %s
              AND stat_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 29 DAY) AND CURDATE()
            ORDER BY stat_date, give_gift_id
            """,
            (user_id,),
        )
        projections = dump(cursor, "RTP_PROJECTIONS")

        cursor.execute(
            """
            SELECT projection_state, report_eligible, exclusion_reason,
                   COUNT(*) AS projection_count,
                   COALESCE(SUM(valid_wager_coin), 0) AS valid_wager_coin,
                   COALESCE(SUM(giver_return_coin), 0) AS giver_return_coin,
                   COALESCE(SUM(draw_event_count), 0) AS draw_event_count
            FROM lucky_gift_report_projection
            WHERE giver_user_id = %s
              AND stat_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 29 DAY) AND CURDATE()
            GROUP BY projection_state, report_eligible, exclusion_reason
            ORDER BY projection_state, report_eligible, exclusion_reason
            """,
            (user_id,),
        )
        dump(cursor, "RTP_PROJECTION_SUMMARY")

        if projections:
            gift_ids = [row["give_gift_id"] for row in projections]
            marks = ",".join(["%s"] * len(gift_ids))

            cursor.execute(
                f"""
                SELECT COUNT(*) AS gift_count, COALESCE(SUM(g.total_price), 0) AS total_price,
                       COALESCE(SUM(g.number), 0) AS unit_count
                FROM ln_give_gift g
                WHERE g.id IN ({marks})
                  AND g.user_id = %s
                  AND g.type IN (35, 36)
                """,
                tuple(gift_ids) + (user_id,),
            )
            dump(cursor, "PROJECTED_GIFT_FACTS")

            cursor.execute(
                f"""
                SELECT COUNT(*) AS draw_event_count,
                       COALESCE(SUM(accepted_unit_price), 0) AS accepted_wager_coin,
                       COALESCE(SUM(sender_coin_amount), 0) AS sender_coin_amount,
                       SUM(sender_result = 'WIN') AS sender_win_count,
                       SUM(sender_result = 'MISS') AS sender_miss_count,
                       SUM(status NOT IN ('RECIPIENT_DRAWN', 'NO_RECIPIENT_DRAW')) AS non_final_event_count
                FROM lucky_gift_draw_event
                WHERE give_gift_id IN ({marks}) AND sender_user_id = %s
                """,
                tuple(gift_ids) + (user_id,),
            )
            dump(cursor, "PROJECTED_DRAW_EVENTS")

            cursor.execute(
                f"""
                SELECT COUNT(*) AS success_reward_count,
                       COALESCE(SUM(w.coin), 0) AS success_reward_coin
                FROM ln_wallet_log w
                INNER JOIN lucky_gift_draw_event e ON e.id = w.bus_id
                WHERE e.give_gift_id IN ({marks})
                  AND e.sender_user_id = %s
                  AND w.user_id = %s
                  AND w.type = 1 AND w.bus_type = 10012 AND w.status = 1
                """,
                tuple(gift_ids) + (user_id, user_id),
            )
            dump(cursor, "PROJECTED_SENDER_REWARDS")

            cursor.execute(
                f"""
                SELECT w.type, w.bus_type, COUNT(*) AS success_log_count,
                       COALESCE(SUM(w.coin), 0) AS coin_sum
                FROM ln_wallet_log w
                WHERE w.user_id = %s AND w.status = 1 AND w.bus_id IN ({marks})
                GROUP BY w.type, w.bus_type
                ORDER BY w.type, w.bus_type
                """,
                (user_id,) + tuple(gift_ids),
            )
            dump(cursor, "PROJECTED_GIFT_WALLET_LOGS")

        cursor.execute(
            """
            WITH eligible_projection AS (
                SELECT give_gift_id, play_mode, valid_wager_coin, giver_return_coin
                FROM lucky_gift_report_projection
                WHERE giver_user_id = %s
                  AND stat_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 29 DAY) AND CURDATE()
                  AND projection_state = 1
                  AND report_eligible = 1
            ), event_coin_equiv AS (
                SELECT e.give_gift_id,
                       COALESCE(SUM(
                           CASE WHEN e.play_type = 'BILATERAL' THEN
                               FLOOR(GREATEST(
                                   e.recipient_diamond_amount - FLOOR(e.accepted_unit_price * 0.2),
                                   0
                               ) / 5)
                           ELSE 0 END
                       ), 0) AS receiver_lucky_coin_equiv
                FROM lucky_gift_draw_event e
                INNER JOIN eligible_projection p ON p.give_gift_id = e.give_gift_id
                GROUP BY e.give_gift_id
            )
            SELECT
                DATE_SUB(CURDATE(), INTERVAL 29 DAY) AS window_start,
                CURDATE() AS window_end,
                p.play_mode,
                COUNT(*) AS projection_count,
                COALESCE(SUM(p.valid_wager_coin), 0) AS valid_wager_coin,
                COALESCE(SUM(p.giver_return_coin), 0) AS giver_return_coin,
                COALESCE(SUM(e.receiver_lucky_coin_equiv), 0) AS receiver_lucky_coin_equiv,
                ROUND(COALESCE(SUM(p.giver_return_coin), 0) /
                    NULLIF(SUM(p.valid_wager_coin), 0) * 100, 4) AS giver_rtp_pct,
                CASE WHEN p.play_mode = 2 THEN ROUND(
                    (COALESCE(SUM(p.giver_return_coin), 0) +
                     COALESCE(SUM(e.receiver_lucky_coin_equiv), 0)) /
                    NULLIF(SUM(p.valid_wager_coin), 0) * 100,
                    4
                ) END AS bilateral_platform_rtp_pct,
                'draw_event_fallback' AS coin_equiv_source
            FROM eligible_projection p
            LEFT JOIN event_coin_equiv e ON e.give_gift_id = p.give_gift_id
            GROUP BY p.play_mode
            ORDER BY p.play_mode
            """,
            (user_id,),
        )
        dump(cursor, "THIRTY_DAY_PROJECTED_MODE_RTP")

        cursor.execute(
            """
            SELECT stat_date, play_mode, giver_valid_wager_coin, giver_return_coin,
                   receiver_lucky_diamond,
                   giver_valid_record_count, receiver_lucky_record_count,
                   source_max_settled_at, updated_at
            FROM lucky_user_mode_day_agg
            WHERE user_id = %s
              AND stat_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 29 DAY) AND CURDATE()
            ORDER BY stat_date, play_mode
            """,
            (user_id,),
        )
        dump(cursor, "DAILY_MODE_DATA")

        cursor.execute(
            """
            SELECT
                DATE_SUB(CURDATE(), INTERVAL 29 DAY) AS window_start,
                CURDATE() AS window_end,
                play_mode,
                COUNT(*) AS aggregation_day_count,
                COALESCE(SUM(giver_valid_wager_coin), 0) AS giver_valid_wager_coin,
                COALESCE(SUM(giver_return_coin), 0) AS giver_return_coin,
                COALESCE(SUM(receiver_lucky_diamond), 0) AS receiver_lucky_diamond,
                COALESCE(SUM(giver_valid_record_count), 0) AS giver_valid_record_count,
                COALESCE(SUM(receiver_lucky_record_count), 0) AS receiver_lucky_record_count,
                MAX(source_max_settled_at) AS source_max_settled_at,
                MAX(updated_at) AS updated_at,
                ROUND(COALESCE(SUM(giver_return_coin), 0) /
                    NULLIF(SUM(giver_valid_wager_coin), 0) * 100, 4) AS giver_rtp_pct
            FROM lucky_user_mode_day_agg
            WHERE user_id = %s
              AND stat_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 29 DAY) AND CURDATE()
            GROUP BY play_mode
            ORDER BY play_mode
            """,
            (user_id,),
        )
        dump(cursor, "THIRTY_DAY_MODE_RTP")

        cursor.execute(
            """
            SELECT
                DATE_SUB(CURDATE(), INTERVAL 29 DAY) AS window_start,
                CURDATE() AS window_end,
                COALESCE(SUM(giver_valid_wager_coin), 0) AS giver_valid_wager_coin,
                COALESCE(SUM(giver_return_coin), 0) AS giver_return_coin,
                ROUND(COALESCE(SUM(giver_return_coin), 0) /
                    NULLIF(SUM(giver_valid_wager_coin), 0) * 100, 4) AS giver_rtp_pct
            FROM lucky_user_mode_day_agg
            WHERE user_id = %s
              AND stat_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 29 DAY) AND CURDATE()
            """,
            (user_id,),
        )
        dump(cursor, "THIRTY_DAY_TOTAL_RTP")

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
