import os
from pathlib import Path
from typing import Any

import mysql.connector


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in Path('.env').read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        values[key.strip()] = value.strip()
    return values


def fetch_all(cursor: Any, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    cursor.execute(sql, params)
    columns = [item[0] for item in cursor.description] if cursor.description else []
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def main() -> None:
    env = load_env()
    connection = mysql.connector.connect(
        host=env['MYSQL_HOST'],
        port=int(env['MYSQL_PORT']),
        user=env['MYSQL_USER'],
        password=env['MYSQL_PASSWORD'],
        database=env['MYSQL_DATABASE'],
    )
    try:
        cursor = connection.cursor()
        tables = [
            'guild.guild_info',
            'guild.guild_salary_detail',
            'guild.guild_settlement_bill',
            'guild.guild_salary_detail_weekly',
            'guild.guild_settlement_bill_weekly',
        ]
        for table in tables:
            print(f'=== SHOW COLUMNS {table} ===')
            print(fetch_all(cursor, f'SHOW COLUMNS FROM {table}'))

        print('=== GUILD RESOLUTION ===')
        guilds = fetch_all(
            cursor,
            'SELECT id, guild_no, guild_name, guild_status FROM guild.guild_info WHERE guild_no=%s',
            (1028,),
        )
        print(guilds)
        if len(guilds) != 1:
            raise RuntimeError(f'Expected exactly one guild for guild_no=1028, got {len(guilds)}')
        guild_id = guilds[0]['id']

        queries = [
            (
                'MONTHLY_DETAIL',
                '''SELECT COUNT(*) AS row_count,
                          COUNT(DISTINCT settlement_month) AS period_count,
                          COUNT(DISTINCT settlement_bill_id) AS bill_id_count,
                          MIN(settlement_month) AS first_period,
                          MAX(settlement_month) AS last_period,
                          SUM(total_salary_amount) AS total_salary
                   FROM guild.guild_salary_detail
                   WHERE guild_id=%s''',
            ),
            (
                'MONTHLY_BILL',
                '''SELECT COUNT(*) AS row_count,
                          COUNT(DISTINCT settlement_month) AS period_count,
                          MIN(settlement_month) AS first_period,
                          MAX(settlement_month) AS last_period,
                          SUM(total_salary_amount) AS total_salary,
                          SUM(CASE WHEN settle_status=2 THEN 1 ELSE 0 END) AS settled_count,
                          SUM(CASE WHEN settle_status<>2 THEN 1 ELSE 0 END) AS pending_count
                   FROM guild.guild_settlement_bill
                   WHERE guild_id=%s''',
            ),
            (
                'WEEKLY_DETAIL',
                '''SELECT COUNT(*) AS row_count,
                          COUNT(DISTINCT period_start) AS period_count,
                          COUNT(DISTINCT settlement_bill_id) AS bill_id_count,
                          MIN(period_start) AS first_period,
                          MAX(period_start) AS last_period,
                          SUM(total_salary_amount) AS total_salary
                   FROM guild.guild_salary_detail_weekly
                   WHERE guild_id=%s''',
            ),
            (
                'WEEKLY_BILL',
                '''SELECT COUNT(*) AS row_count,
                          COUNT(DISTINCT period_start) AS period_count,
                          MIN(period_start) AS first_period,
                          MAX(period_start) AS last_period,
                          SUM(total_salary_amount) AS total_salary,
                          SUM(CASE WHEN settle_status=2 THEN 1 ELSE 0 END) AS settled_count,
                          SUM(CASE WHEN settle_status<>2 THEN 1 ELSE 0 END) AS pending_count
                   FROM guild.guild_settlement_bill_weekly
                   WHERE guild_id=%s''',
            ),
        ]
        for label, sql in queries:
            print(f'=== {label} ===')
            print(fetch_all(cursor, sql, (guild_id,)))

        detail_queries = [
            ('MONTHLY_DETAIL_GROUP', '''SELECT sd.settlement_month, sb.settle_status, sd.source_type, sd.settlement_bill_id,
                                               sd.bill_owner_type, sd.policy_type, COUNT(*) AS row_count,
                                               SUM(sd.total_salary_amount) AS total_salary
                                        FROM guild.guild_salary_detail sd
                                        LEFT JOIN guild.guild_settlement_bill sb ON sb.id=sd.settlement_bill_id
                                        WHERE sd.guild_id=%s
                                        GROUP BY sd.settlement_month, sb.settle_status, sd.source_type, sd.settlement_bill_id,
                                                 sd.bill_owner_type, sd.policy_type
                                        ORDER BY sd.settlement_month, sd.settlement_bill_id, sd.bill_owner_type'''),
            ('WEEKLY_DETAIL_GROUP', '''SELECT sd.period_start, sb.settle_status, sd.source_type, sd.settlement_bill_id,
                                              sd.bill_owner_type, sd.policy_type, COUNT(*) AS row_count,
                                              SUM(sd.total_salary_amount) AS total_salary
                                       FROM guild.guild_salary_detail_weekly sd
                                       LEFT JOIN guild.guild_settlement_bill_weekly sb ON sb.id=sd.settlement_bill_id
                                       WHERE sd.guild_id=%s
                                       GROUP BY sd.period_start, sb.settle_status, sd.source_type, sd.settlement_bill_id,
                                                sd.bill_owner_type, sd.policy_type
                                       ORDER BY sd.period_start, sd.settlement_bill_id, sd.bill_owner_type'''),
        ]
        for label, sql in detail_queries:
            print(f'=== {label} ===')
            print(fetch_all(cursor, sql, (guild_id,)))

        print('=== REFERENTIAL CHECK ===')
        print(fetch_all(cursor, '''SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME,
                                          REFERENCED_TABLE_SCHEMA, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                                   FROM information_schema.KEY_COLUMN_USAGE
                                   WHERE (TABLE_SCHEMA='guild' AND TABLE_NAME IN
                                          ('guild_salary_detail','guild_settlement_bill',
                                           'guild_salary_detail_weekly','guild_settlement_bill_weekly'))
                                      OR (REFERENCED_TABLE_SCHEMA='guild' AND REFERENCED_TABLE_NAME IN
                                          ('guild_salary_detail','guild_settlement_bill',
                                           'guild_salary_detail_weekly','guild_settlement_bill_weekly'))
                                   ORDER BY TABLE_NAME, CONSTRAINT_NAME'''))
    finally:
        connection.close()


if __name__ == '__main__':
    main()
