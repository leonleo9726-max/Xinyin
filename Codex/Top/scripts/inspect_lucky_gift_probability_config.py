from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any
from urllib.parse import urlparse

import mysql.connector


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / "outputs" / "lucky_gift_probability_before.json"


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in (PROJECT_ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def as_json(value: Any) -> Any:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value) if value is not None else None


def main() -> int:
    settings = load_env()
    required = ("MYSQL_HOST", "MYSQL_PORT", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE", "REDIS_URL")
    missing = [name for name in required if not settings.get(name)]
    if missing:
        print(f"Missing settings: {', '.join(missing)}", file=sys.stderr)
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
        cursor.execute("SHOW COLUMNS FROM lucky_gift_draw_rule")
        schema_columns = [column[0] for column in cursor.description]
        schema = [dict(zip(schema_columns, row)) for row in cursor.fetchall()]
        cursor.execute(
            """
            SELECT *
            FROM lucky_gift_draw_rule
            WHERE status = 'ACTIVE' AND enabled = 1
            ORDER BY play_type, reward_pool, id
            """
        )
        columns = [column[0] for column in cursor.description]
        rules = [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        connection.close()

    parsed_redis = urlparse(settings["REDIS_URL"])
    redis_db = int(parsed_redis.path.strip("/") or "0")
    try:
        import redis
    except ImportError as exc:
        print(f"Redis client unavailable: {exc}", file=sys.stderr)
        return 3
    client = redis.Redis.from_url(settings["REDIS_URL"], decode_responses=True, socket_timeout=10)
    redis_keys = sorted(client.scan_iter(match="lucky_gift:config:*", count=100))

    payload = {
        "environment": "test",
        "database": settings["MYSQL_DATABASE"],
        "redis_db": redis_db,
        "schema": [{key: as_json(value) for key, value in row.items()} for row in schema],
        "active_rules": [{key: as_json(value) for key, value in row.items()} for row in rules],
        "redis_config_keys": redis_keys,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"ENVIRONMENT: test")
    print(f"DATABASE: {settings['MYSQL_DATABASE']}")
    print(f"ACTIVE_RULE_COUNT: {len(rules)}")
    print(f"REDIS_DB: {redis_db}")
    print(f"REDIS_CONFIG_KEY_COUNT: {len(redis_keys)}")
    print(f"OUTPUT: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
