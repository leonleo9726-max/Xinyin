from __future__ import annotations

import json
from pathlib import Path

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


def emit(cursor: mysql.connector.cursor.MySQLCursor, label: str) -> None:
    columns = [column[0] for column in cursor.description]
    print(f"{label}_COLUMNS: {','.join(columns)}")
    for row in cursor.fetchall():
        data = {key: str(value) for key, value in zip(columns, row)}
        print(f"{label}: {json.dumps(data, ensure_ascii=True, sort_keys=True)}")


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
        cursor.execute("SHOW COLUMNS FROM lucky_card_reward_config")
        emit(cursor, "SHOW_LUCKY_CARD_REWARD_CONFIG")
        cursor.execute(
            """
            SELECT id, reward_type, reward_id, valid_days, probability, enabled, updated_at
            FROM lucky_card_reward_config
            ORDER BY enabled DESC, probability DESC, id
            """
        )
        emit(cursor, "CARD_REWARD_CONFIG")
        cursor.execute(
            """
            SELECT enabled, COUNT(*) AS reward_count, SUM(probability) AS probability_total
            FROM lucky_card_reward_config
            GROUP BY enabled ORDER BY enabled DESC
            """
        )
        emit(cursor, "CARD_REWARD_PROBABILITY_SUMMARY")
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
