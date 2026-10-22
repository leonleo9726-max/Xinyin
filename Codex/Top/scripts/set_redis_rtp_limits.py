from pathlib import Path
from urllib.parse import unquote, urlparse

import redis
from dotenv import dotenv_values


KEY = "lucky_gift:config:rtp"
DATABASE = 7
FIELDS = (
    "overall_rtp_limit",
    "non_bilateral_rtp_limit",
    "bilateral_rtp_limit",
)
VALUE = "60000"


def main() -> None:
    settings = dotenv_values(Path(__file__).resolve().parents[1] / ".env")
    redis_url = settings.get("REDIS_URL")
    if not redis_url:
        raise RuntimeError("缺少 REDIS_URL")

    parsed = urlparse(redis_url)
    client = redis.Redis(
        host=parsed.hostname,
        port=parsed.port or 6379,
        username=unquote(parsed.username) if parsed.username else None,
        password=unquote(parsed.password) if parsed.password else None,
        db=DATABASE,
        ssl=parsed.scheme == "rediss",
        decode_responses=True,
        socket_connect_timeout=10,
    )
    if not client.exists(KEY):
        raise RuntimeError(f"DB{DATABASE} 不存在 {KEY}")

    before = client.hgetall(KEY)
    if set(before) != set(FIELDS):
        raise RuntimeError(f"RTP Hash 字段异常: {sorted(before)}")

    client.hset(KEY, mapping={field: VALUE for field in FIELDS})
    after = client.hgetall(KEY)
    if any(after.get(field) != VALUE for field in FIELDS):
        raise RuntimeError(f"写入核验失败: {after}")

    print(f"database={DATABASE}")
    print(f"key={KEY}")
    print(f"ttl={client.ttl(KEY)}")
    print(f"before={before}")
    print(f"after={after}")


if __name__ == "__main__":
    main()
