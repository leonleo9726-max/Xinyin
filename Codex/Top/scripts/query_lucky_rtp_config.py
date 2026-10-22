from __future__ import annotations

from pathlib import Path
from urllib.parse import unquote, urlparse

import mysql.connector
import redis


ROOT = Path(__file__).resolve().parent.parent
RTP_KEY = "lucky_gift:config:rtp"
REDIS_DATABASES = (7, 10)


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


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
        cursor.execute("SHOW COLUMNS FROM lucky_gift_rtp_config")
        columns = [row[0] for row in cursor.fetchall()]
        print(f"DATABASE: {settings['MYSQL_DATABASE']}")
        print("ENVIRONMENT: test (MYSQL_* settings)")
        print(f"MYSQL_COLUMNS: {','.join(columns)}")

        cursor.execute("SELECT * FROM lucky_gift_rtp_config WHERE id = 1")
        result_columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        print(f"MYSQL_CONFIG_COUNT: {len(rows)}")
        for row in rows[:3]:
            print(f"MYSQL_CONFIG: {dict(zip(result_columns, row))}")
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
