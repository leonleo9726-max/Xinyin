from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import mysql.connector


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "outputs"
TABLE = "lucky_card_trigger_config"


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def fetch_rows(cursor: mysql.connector.cursor.MySQLCursor) -> list[dict[str, Any]]:
    cursor.execute(
        """
        SELECT id, play_type, enabled, updated_at
        FROM lucky_card_trigger_config
        ORDER BY play_type, id
        """
    )
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def write_snapshot(label: str, rows: list[dict[str, Any]]) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / f"lucky_card_trigger_{label}_{datetime.now():%Y%m%d_%H%M%S}.json"
    path.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    return path


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
        cursor.execute(f"SHOW COLUMNS FROM {TABLE}")
        schema_rows = cursor.fetchall()
        print(f"DATABASE: {settings['MYSQL_DATABASE']}")
        print("ENVIRONMENT: test (MYSQL_* settings)")
        print(f"SHOW_COLUMNS_FIRST_3: {schema_rows[:3]}")
        connection.commit()

        connection.start_transaction()
        before = fetch_rows(cursor)
        if not before:
            connection.rollback()
            raise RuntimeError("No lucky card trigger configurations found; no change applied.")
        before_path = write_snapshot("before_enable", before)

        cursor.execute("UPDATE lucky_card_trigger_config SET enabled = 1 WHERE enabled <> 1")
        changed_rows = cursor.rowcount
        after = fetch_rows(cursor)
        disabled_after = [row for row in after if row["enabled"] != 1]
        if disabled_after:
            connection.rollback()
            raise RuntimeError("Disabled lucky card triggers remain; transaction rolled back.")
        connection.commit()

        after_path = write_snapshot("after_enable", after)
        print(f"CONFIG_ROWS: {len(after)}")
        print(f"CONFIG_FIRST_3: {after[:3]}")
        print(f"UPDATED_ROWS: {changed_rows}")
        print(f"DISABLED_AFTER: {len(disabled_after)}")
        print(f"BEFORE_SNAPSHOT: {before_path}")
        print(f"AFTER_SNAPSHOT: {after_path}")
        return 0
    except Exception:
        if connection.in_transaction:
            connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
