from __future__ import annotations

from pathlib import Path
from typing import Any

import mysql.connector


ROOT = Path(__file__).resolve().parent.parent
USER_NO = "6658169"


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
        print(f"{label}_SAMPLE: {row}")
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
        cursor.execute("SHOW COLUMNS FROM lucky_user_mode_day_agg")
        dump(cursor, "SHOW_LUCKY_USER_MODE_DAY_AGG")

        cursor.execute("SELECT user_id, user_no FROM ln_user WHERE user_no = %s", (USER_NO,))
        users = dump(cursor, "USER")
        if not users:
            return 0
        user_id = users[0]["user_id"]

        cursor.execute(
            """
            SELECT stat_date, play_mode, giver_valid_wager_coin, giver_return_coin,
                   receiver_lucky_diamond, receiver_lucky_coin_equiv,
                   giver_valid_record_count, receiver_lucky_record_count,
                   source_max_settled_at, updated_at
            FROM lucky_user_mode_day_agg
            WHERE user_id = %s
              AND stat_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 6 DAY) AND CURDATE()
            ORDER BY stat_date, play_mode
            """,
            (user_id,),
        )
        dump(cursor, "DAILY_MODE_DATA")

        cursor.execute(
            """
            SELECT
                DATE_SUB(CURDATE(), INTERVAL 6 DAY) AS window_start,
                CURDATE() AS window_end,
                play_mode,
                COUNT(*) AS aggregation_day_count,
                SUM(giver_valid_wager_coin) AS giver_valid_wager_coin,
                SUM(giver_return_coin) AS giver_return_coin,
                SUM(receiver_lucky_diamond) AS receiver_lucky_diamond,
                SUM(receiver_lucky_coin_equiv) AS receiver_lucky_coin_equiv,
                SUM(giver_valid_record_count) AS giver_valid_record_count,
                SUM(receiver_lucky_record_count) AS receiver_lucky_record_count,
                MAX(source_max_settled_at) AS source_max_settled_at,
                MAX(updated_at) AS updated_at,
                ROUND(
                    SUM(giver_return_coin) / NULLIF(SUM(giver_valid_wager_coin), 0) * 100,
                    4
                ) AS giver_rtp_pct
            FROM lucky_user_mode_day_agg
            WHERE user_id = %s
              AND stat_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 6 DAY) AND CURDATE()
            GROUP BY play_mode
            ORDER BY play_mode
            """,
            (user_id,),
        )
        dump(cursor, "SEVEN_DAY_MODE_RTP")
        return 0
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
