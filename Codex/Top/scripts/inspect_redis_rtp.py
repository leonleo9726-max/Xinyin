from pathlib import Path
from urllib.parse import unquote, urlparse

import redis
from dotenv import dotenv_values


KEY = "lucky_gift:config:rtp"
DATABASES = (7, 10)


def redis_client(redis_url: str, database: int) -> redis.Redis:
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


def main() -> None:
    settings = dotenv_values(Path(__file__).resolve().parents[1] / ".env")
    redis_url = settings.get("REDIS_URL")
    if not redis_url:
        raise RuntimeError("缺少 REDIS_URL")

    for database in DATABASES:
        client = redis_client(redis_url, database)
        print(f"database={database}")
        print(f"key_exists={bool(client.exists(KEY))}")
        print(f"ttl={client.ttl(KEY)}")
        print(f"value={client.hgetall(KEY)}")


if __name__ == "__main__":
    main()
