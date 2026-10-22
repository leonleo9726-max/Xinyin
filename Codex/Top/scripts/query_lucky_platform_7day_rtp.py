from __future__ import annotations

from pathlib import Path
from typing import Any

import mysql.connector


ROOT = Path(__file__).resolve().parent.parent


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
        cursor.execute("SHOW COLUMNS FROM lucky_io_day_agg")
        dump(cursor, "SHOW_LUCKY_IO_DAY_AGG")

        cursor.execute(
            """
            SELECT stat_date, valid_wager_coin, giver_return_coin,
                   single_wager_coin, single_giver_return_coin,
                   double_wager_coin, double_giver_return_coin,
                   double_receiver_lucky_diamond, double_receiver_coin_equiv,
                   is_final, source_max_settled_at, updated_at
            FROM lucky_io_day_agg
            WHERE stat_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 6 DAY) AND CURDATE()
            ORDER BY stat_date
            """
        )
        dump(cursor, "DAILY_PLATFORM_DATA")

        cursor.execute(
            """
            SELECT
                DATE_SUB(CURDATE(), INTERVAL 6 DAY) AS window_start,
                CURDATE() AS window_end,
                COUNT(*) AS aggregation_day_count,
                SUM(is_final = 0) AS non_final_day_count,
                SUM(valid_wager_coin) AS total_valid_wager_coin,
                SUM(giver_return_coin) AS total_giver_return_coin,
                SUM(single_wager_coin) AS single_wager_coin,
                SUM(single_giver_return_coin) AS single_giver_return_coin,
                SUM(double_wager_coin) AS double_wager_coin,
                SUM(double_giver_return_coin) AS double_giver_return_coin,
                SUM(double_receiver_lucky_diamond) AS double_receiver_lucky_diamond,
                SUM(double_receiver_coin_equiv) AS double_receiver_coin_equiv,
                MAX(source_max_settled_at) AS source_max_settled_at,
                MAX(updated_at) AS updated_at,
                ROUND(
                    (SUM(giver_return_coin) + SUM(double_receiver_coin_equiv))
                    / NULLIF(SUM(valid_wager_coin), 0) * 100,
                    4
                ) AS overall_rtp_pct,
                ROUND(
                    SUM(single_giver_return_coin) / NULLIF(SUM(single_wager_coin), 0) * 100,
                    4
                ) AS non_bilateral_rtp_pct,
                ROUND(
                    SUM(double_giver_return_coin) / NULLIF(SUM(double_wager_coin), 0) * 100,
                    4
                ) AS bilateral_giver_rtp_pct,
                ROUND(
                    (SUM(double_giver_return_coin) + SUM(double_receiver_coin_equiv))
                    / NULLIF(SUM(double_wager_coin), 0) * 100,
                    4
                ) AS bilateral_platform_rtp_pct
            FROM lucky_io_day_agg
            WHERE stat_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 6 DAY) AND CURDATE()
            """
        )
        dump(cursor, "SEVEN_DAY_PLATFORM_RTP")
        return 0
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
