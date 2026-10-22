from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
import sys

import mysql.connector


GUILD_NO = 71960192
SETTLEMENT_MONTH = date.today().strftime("%Y-%m")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCREENSHOT_OWNER_SHARES = {
    "5227446": Decimal("11538.55"),
    "8259492": Decimal("17655.48"),
}


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for source_line in path.read_text(encoding="utf-8").splitlines():
        line = source_line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def decimal(value: object) -> Decimal:
    return Decimal(str(value or 0))


def main() -> int:
    settings = load_env(PROJECT_ROOT / ".env")
    required = (
        "PROD_MYSQL_HOST",
        "PROD_MYSQL_PORT",
        "PROD_MYSQL_USER",
        "PROD_MYSQL_PASSWORD",
        "PROD_MYSQL_DATABASE",
    )
    missing = [name for name in required if not settings.get(name)]
    if missing:
        print(f"Missing production settings: {', '.join(missing)}", file=sys.stderr)
        return 2

    connection = mysql.connector.connect(
        host=settings["PROD_MYSQL_HOST"],
        port=int(settings["PROD_MYSQL_PORT"]),
        user=settings["PROD_MYSQL_USER"],
        password=settings["PROD_MYSQL_PASSWORD"],
        database=settings["PROD_MYSQL_DATABASE"],
        connection_timeout=15,
    )
    try:
        cursor = connection.cursor(dictionary=True)
        for table in ("guild.guild_salary_detail", "guild.guild_member"):
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            columns = cursor.fetchall()
            print(f"{table}_COLUMNS: {','.join(row['Field'] for row in columns)}")
            for row in columns[:3]:
                print(f"{table}_PREVIEW: {row}")

        cursor.execute(
            "SELECT id FROM guild.guild_info WHERE guild_no = %s", (GUILD_NO,)
        )
        guild = cursor.fetchone()
        if not guild:
            print("GUILD_NOT_FOUND")
            return 0

        cursor.execute(
            """
            SELECT
                gm.id AS member_id, u.user_no, gm.base_share_rate,
                gm.tc_reward_rate, gm.owner_share_rate,
                anchor.total_salary_amount AS anchor_total_salary,
                anchor.non_coin_reward_amount AS anchor_non_coin_reward,
                anchor.coin_reward_amount AS anchor_coin_reward,
                owner.total_salary_amount AS owner_total_salary,
                owner.non_coin_reward_amount AS owner_non_coin_reward,
                owner.coin_reward_amount AS owner_coin_reward,
                owner.guild_coin_reward_amount AS owner_guild_coin_reward,
                owner.owner_share_amount AS owner_share_amount,
                owner.settlement_bill_id AS owner_settlement_bill_id
            FROM guild.guild_member AS gm
            INNER JOIN app.ln_user AS u ON u.user_id = gm.user_id
            LEFT JOIN guild.guild_salary_detail AS anchor
              ON anchor.guild_id = gm.guild_id
             AND anchor.member_id = gm.id
             AND anchor.settlement_month = %s
             AND anchor.bill_owner_type = 1
            LEFT JOIN guild.guild_salary_detail AS owner
              ON owner.guild_id = gm.guild_id
             AND owner.member_id = gm.id
             AND owner.settlement_month = %s
             AND owner.bill_owner_type = 2
            WHERE gm.guild_id = %s
            ORDER BY gm.id
            """,
            (SETTLEMENT_MONTH, SETTLEMENT_MONTH, guild["id"]),
        )
        rows = cursor.fetchall()
        print(f"DETAIL_COLUMNS: {','.join(rows[0].keys()) if rows else ''}")
        print(f"DETAIL_ROW_COUNT: {len(rows)}")
        for row in rows[:3]:
            denominator = decimal(row["base_share_rate"]) + decimal(row["tc_reward_rate"])
            displayed_owner_share = (
                decimal(row["anchor_total_salary"])
                * decimal(row["owner_share_rate"])
                / denominator
                if denominator
                else Decimal("0")
            )
            row["dashboard_recomputed_owner_share"] = displayed_owner_share.quantize(
                Decimal("0.01")
            )
            row["dashboard_minus_stored_owner_salary"] = (
                displayed_owner_share - decimal(row["owner_total_salary"])
            ).quantize(Decimal("0.01"))
            displayed_from_snapshot = (
                decimal(row["owner_total_salary"])
                + decimal(row["owner_guild_coin_reward"])
            ).quantize(Decimal("0.01"))
            expected = SCREENSHOT_OWNER_SHARES.get(row["user_no"])
            row["snapshot_display_owner_share"] = displayed_from_snapshot
            if expected is not None:
                row["screenshot_owner_share"] = expected
                row["snapshot_minus_screenshot"] = displayed_from_snapshot - expected
                if displayed_from_snapshot != expected:
                    raise AssertionError(
                        f"{row['user_no']} snapshot display {displayed_from_snapshot} "
                        f"does not match screenshot {expected}"
                    )
            print(f"DETAIL_ROW: {row}")
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
