from pathlib import Path
from typing import Any

import mysql.connector


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in Path('.env').read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            values[key.strip()] = value.strip()
    return values


def rows(cursor: Any, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    cursor.execute(sql, params)
    names = [column[0] for column in cursor.description] if cursor.description else []
    return [dict(zip(names, row)) for row in cursor.fetchall()]


def main() -> None:
    env = load_env()
    connection = mysql.connector.connect(
        host=env['MYSQL_HOST'], port=int(env['MYSQL_PORT']), user=env['MYSQL_USER'],
        password=env['MYSQL_PASSWORD'], database=env['MYSQL_DATABASE'])
    try:
        cursor = connection.cursor()
        for table in ('guild.guild_balance_pool', 'guild.guild_balance_pool_flow',
                      'guild.guild_member_income_monthly', 'guild.guild_member_income_weekly'):
            print(f'=== SHOW COLUMNS {table} ===')
            print(rows(cursor, f'SHOW COLUMNS FROM {table}'))

        guild_id = 35
        print('=== BALANCE POOL FLOW SUMMARY ===')
        print(rows(cursor, '''SELECT biz_type, flow_type, pool_type, COUNT(*) AS row_count,
                                     SUM(change_amount) AS change_total,
                                     MIN(created_at) AS first_created, MAX(created_at) AS last_created
                              FROM guild.guild_balance_pool_flow
                              WHERE guild_id=%s AND biz_type IN (1,5)
                              GROUP BY biz_type, flow_type, pool_type
                              ORDER BY biz_type, flow_type, pool_type''', (guild_id,)))
        print('=== SETTLEMENT FLOWS ===')
        print(rows(cursor, '''SELECT id, pool_id, user_id, role_type, pool_type, flow_type, biz_type,
                                     biz_id, change_amount, available_before, available_after, created_at
                              FROM guild.guild_balance_pool_flow
                              WHERE guild_id=%s AND biz_type IN (1,5)
                              ORDER BY biz_type, biz_id, id''', (guild_id,)))
        print('=== BALANCE POOLS FOR GUILD USERS ===')
        print(rows(cursor, '''SELECT p.id, p.user_id, p.pool_type, p.available_amount, p.frozen_amount,
                                     p.total_in_amount, p.total_out_amount, p.pool_status
                              FROM guild.guild_balance_pool p
                              WHERE p.user_id IN (
                                  SELECT DISTINCT user_id FROM guild.guild_settlement_bill WHERE guild_id=%s
                                  UNION
                                  SELECT DISTINCT owner_user_id FROM guild.guild_settlement_bill WHERE guild_id=%s
                                  UNION
                                  SELECT DISTINCT user_id FROM guild.guild_settlement_bill_weekly WHERE guild_id=%s
                                  UNION
                                  SELECT DISTINCT owner_user_id FROM guild.guild_settlement_bill_weekly WHERE guild_id=%s
                              )
                              ORDER BY p.user_id, p.pool_type''', (guild_id, guild_id, guild_id, guild_id)))
        print('=== MONTHLY INCOME LOCKS ===')
        print(rows(cursor, '''SELECT member_id, settlement_month, diamond_amount_total,
                                     invalid_diamond_amount_total
                              FROM guild.guild_member_income_monthly
                              WHERE guild_id=%s AND settlement_month='2026-09'
                              ORDER BY member_id''', (guild_id,)))
        print('=== WEEKLY INCOME LOCKS ===')
        print(rows(cursor, '''SELECT member_id, period_start, diamond_amount_total,
                                     invalid_diamond_amount_total
                              FROM guild.guild_member_income_weekly
                              WHERE guild_id=%s AND period_start='2026-09-21'
                              ORDER BY member_id''', (guild_id,)))
    finally:
        connection.close()


if __name__ == '__main__':
    main()
