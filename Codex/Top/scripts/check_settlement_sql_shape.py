from pathlib import Path
from typing import Any

import mysql.connector


def env_values() -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in Path('.env').read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            values[key.strip()] = value.strip()
    return values


def fetch(cursor: Any, sql: str) -> list[tuple[Any, ...]]:
    cursor.execute(sql)
    return cursor.fetchall()


def main() -> None:
    env = env_values()
    connection = mysql.connector.connect(
        host=env['MYSQL_HOST'], port=int(env['MYSQL_PORT']), user=env['MYSQL_USER'],
        password=env['MYSQL_PASSWORD'], database=env['MYSQL_DATABASE'])
    try:
        cursor = connection.cursor()
        for table in ('guild_salary_detail', 'guild_salary_detail_weekly'):
            print(f'=== SHOW INDEX {table} ===')
            print(fetch(cursor, f'SHOW INDEX FROM guild.{table}'))
        print('=== DUPLICATE TARGET SHAPE MONTHLY ===')
        print(fetch(cursor, '''SELECT guild_id, member_id, settlement_month, bill_owner_type,
                                      source_type, COUNT(*) AS row_count
                               FROM guild.guild_salary_detail
                               WHERE guild_id=35
                               GROUP BY guild_id, member_id, settlement_month, bill_owner_type, source_type
                               HAVING COUNT(*) > 1'''))
        print('=== DUPLICATE TARGET SHAPE WEEKLY ===')
        print(fetch(cursor, '''SELECT guild_id, member_id, period_start, bill_owner_type,
                                      source_type, COUNT(*) AS row_count
                               FROM guild.guild_salary_detail_weekly
                               WHERE guild_id=35
                               GROUP BY guild_id, member_id, period_start, bill_owner_type, source_type
                               HAVING COUNT(*) > 1'''))
    finally:
        connection.close()


if __name__ == '__main__':
    main()
