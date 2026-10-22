from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import mysql.connector


ROOT = Path(__file__).resolve().parent.parent
USER_CODE = "KK123"
TODAY = datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()


def settings() -> dict[str, str]:
    values = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.lstrip().startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def fetch(cursor, label: str, sql: str, params=()):
    cursor.execute(sql, params)
    columns = [field[0] for field in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    print(f"{label} COLUMNS: {columns}")
    print(f"{label} COUNT: {len(rows)}")
    for row in rows[:3]:
        print(f"{label} FIRST_ROW: {row}")
    for row in rows[3:]:
        print(f"{label} ROW: {row}")
    return rows


def main():
    config = settings()
    if config.get("APP_ENV") != "test":
        raise RuntimeError("Refusing query: APP_ENV is not test")
    connection = mysql.connector.connect(
        host=config["MYSQL_HOST"],
        port=int(config["MYSQL_PORT"]),
        user=config["MYSQL_USER"],
        password=config["MYSQL_PASSWORD"],
        database=config["MYSQL_DATABASE"],
        connection_timeout=15,
    )
    try:
        cursor = connection.cursor()
        fetch(cursor, "ENV", "SELECT DATABASE() AS db, @@hostname AS server, @@session.time_zone AS tz, NOW() AS db_now, UTC_TIMESTAMP() AS utc_now")
        for table in ("ln_user", "ln_user_data", "ln_good_number", "ln_anchor_apply", "ln_game_detail", "ln_game"):
            fetch(cursor, f"SCHEMA_{table}", f"SHOW COLUMNS FROM `{table}`")
        users = fetch(cursor, "USER_NO", "SELECT user_id, user_no FROM ln_user WHERE user_no = %s", (USER_CODE,))
        profiles = fetch(cursor, "USER_CODE", "SELECT user_id, user_code, nickname FROM ln_user_data WHERE user_code = %s", (USER_CODE,)) if USER_CODE.isdecimal() else []
        good_numbers = fetch(cursor, "GOOD_NUMBER", "SELECT user_id, good_number, expired_time FROM ln_good_number WHERE good_number = %s AND (expired_time = 0 OR expired_time > UNIX_TIMESTAMP())", (USER_CODE,))
        nicknames = fetch(cursor, "NICKNAME_CANDIDATES", "SELECT user_id, user_code, nickname FROM ln_user_data WHERE nickname = %s LIMIT 10", (USER_CODE,))
        ids = sorted({row["user_id"] for row in users + profiles + good_numbers})
        if not ids:
            print("RESULT: no exact user_no, user_code, or active good_number match")
            return
        if len(ids) != 1:
            print(f"RESULT: ambiguous user IDs {ids}")
            return
        user_id = ids[0]
        fetch(cursor, "USER_PROFILE", "SELECT u.user_id, u.user_no, d.user_code, d.nickname FROM ln_user u LEFT JOIN ln_user_data d ON d.user_id = u.user_id WHERE u.user_id = %s", (user_id,))
        start_local = datetime.fromisoformat(TODAY).replace(tzinfo=ZoneInfo("Asia/Shanghai"))
        start = start_local.astimezone(ZoneInfo("Asia/Riyadh")).replace(tzinfo=None)
        end = (start_local + timedelta(days=1)).astimezone(ZoneInfo("Asia/Riyadh")).replace(tzinfo=None)
        print(f"BOUNDARY: Asia/Shanghai {TODAY}; game record Asia/Riyadh [{start}, {end})")
        fetch(cursor, "DETAIL_SAMPLE", "SELECT id, provider_type, game_config_id, game_name, provider_game_id, option_type, coin, amount_rate, created_at FROM ln_game_detail WHERE user_id = %s AND created_at >= %s AND created_at < %s ORDER BY created_at, id LIMIT 3", (user_id, start, end))
        fetch(cursor, "GAME_SUMMARY", """
            SELECT d.provider_type, d.game_config_id, COALESCE(NULLIF(d.game_name, ''), g.name, CONCAT('game_id:', d.provider_game_id)) AS game_name,
                   d.provider_game_id, COUNT(*) AS transaction_count,
                   SUM(d.option_type = 1) AS bet_count,
                   SUM(CASE WHEN d.option_type = 1 THEN -d.coin ELSE 0 END) AS bet_coin,
                   SUM(CASE WHEN d.option_type = 2 THEN d.coin ELSE 0 END) AS award_coin,
                   SUM(CASE WHEN d.option_type = 3 THEN d.coin ELSE 0 END) AS rollback_coin,
                   SUM(d.coin) AS net_coin,
                   SUM(d.option_type NOT IN (1, 2, 3)) AS unknown_type_count,
                   MIN(d.created_at) AS first_at, MAX(d.created_at) AS last_at
            FROM ln_game_detail d LEFT JOIN ln_game g ON g.id = d.game_config_id
            WHERE d.user_id = %s AND d.created_at >= %s AND d.created_at < %s
            GROUP BY d.provider_type, d.game_config_id, game_name, d.provider_game_id
            ORDER BY d.provider_type, game_name
        """, (user_id, start, end))
    finally:
        connection.close()


if __name__ == "__main__":
    main()
