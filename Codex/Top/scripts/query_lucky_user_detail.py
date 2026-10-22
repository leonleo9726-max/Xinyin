from __future__ import annotations

from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path
import sys
from typing import Any

import mysql.connector


USER_NO = "6729461"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TABLES = (
    "ln_user",
    "ln_user_data",
    "ln_give_gift",
    "lucky_gift_draw_event",
    "ln_wallet_log",
    "lucky_gift_report_projection",
    "lucky_card_grant_record",
)


def load_env(path: Path) -> dict[str, str]:
    settings: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            settings[key.strip()] = value.strip().strip('"').strip("'")
    return settings


def rows(cursor: mysql.connector.cursor.MySQLCursor, label: str) -> list[dict[str, Any]]:
    columns = [item[0] for item in cursor.description]
    result = [dict(zip(columns, item)) for item in cursor.fetchall()]
    print(f"{label}_COLUMNS: {','.join(columns)}")
    print(f"{label}_COUNT: {len(result)}")
    for item in result[:3]:
        print(f"{label}_SAMPLE: {item}")
    return result


def query(
    cursor: mysql.connector.cursor.MySQLCursor,
    label: str,
    statement: str,
    params: tuple[Any, ...] = (),
) -> list[dict[str, Any]]:
    cursor.execute(statement, params)
    return rows(cursor, label)


def number(value: Any) -> Decimal:
    return Decimal(str(value or 0))


def main() -> int:
    settings = load_env(PROJECT_ROOT / ".env")
    required = ("MYSQL_HOST", "MYSQL_PORT", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE")
    absent = [key for key in required if not settings.get(key)]
    if absent:
        print(f"Missing required test settings: {', '.join(absent)}", file=sys.stderr)
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
        print(f"DATABASE: {settings['MYSQL_DATABASE']}")
        print("ENVIRONMENT: test (MYSQL_* settings)")
        for table in TABLES:
            query(cursor, f"SHOW_{table.upper()}", f"SHOW COLUMNS FROM `{table}`")

        users = query(
            cursor,
            "USER",
            """
            SELECT user_id, user_no, disabled, deleted, role, vip_level, coin, earnings_coin,
                   register_time, last_login_time, last_online_time
            FROM ln_user WHERE user_no = %s
            """,
            (USER_NO,),
        )
        if not users:
            query(
                cursor,
                "USER_DATA_BY_USER_CODE",
                "SELECT user_id, user_code, nickname FROM ln_user_data WHERE user_code = %s",
                (USER_NO,),
            )
            return 0

        user_id = users[0]["user_id"]
        query(
            cursor,
            "USER_DATA",
            """
            SELECT user_id, user_code, nickname, sex, anchor_level, wealth_level, charm_level,
                   active_value, locale, yzh_sign_status, is_internal_staff
            FROM ln_user_data WHERE user_id = %s
            """,
            (user_id,),
        )
        gifts = query(
            cursor,
            "LUCKY_GIFTS",
            """
            SELECT id, user_id, gift_user, gift_id, number, room_id, pit_number, add_time,
                   total_price, type, coin, guild_income_status
            FROM ln_give_gift
            WHERE type IN (35, 36) AND (user_id = %s OR gift_user = %s)
            ORDER BY id
            """,
            (user_id, user_id),
        )
        if not gifts:
            print("SUMMARY: no lucky-gift records for this user")
            return 0

        gift_ids = [item["id"] for item in gifts]
        marks = ",".join(["%s"] * len(gift_ids))
        events = query(
            cursor,
            "DRAW_EVENTS",
            f"""
            SELECT id, give_gift_id, unit_index, sender_user_id, recipient_user_id, gift_id,
                   play_type, accepted_unit_price, accepted_at, sender_multiplier,
                   sender_coin_amount, sender_result, sender_reward_status, recipient_pool,
                   recipient_multiplier, recipient_diamond_amount,
                   base_recipient_diamond_amount, status, failure_reason
            FROM lucky_gift_draw_event
            WHERE give_gift_id IN ({marks})
            ORDER BY give_gift_id, unit_index
            """,
            tuple(gift_ids),
        )
        event_ids = [item["id"] for item in events]
        event_marks = ",".join(["%s"] * len(event_ids)) or "NULL"
        wallet = query(
            cursor,
            "WALLET_LOGS",
            f"""
            SELECT id, user_id, coin, income, diamond, `show`, balance, type, bus_type,
                   bus_id, status, is_send, `desc`, created_at
            FROM ln_wallet_log
            WHERE (bus_type = 10012 AND bus_id IN ({event_marks}))
               OR (bus_type = 40002 AND bus_id IN ({marks}))
               OR (user_id = %s AND bus_id IN ({marks}))
            ORDER BY id
            """,
            tuple(event_ids) + tuple(gift_ids) + (user_id,) + tuple(gift_ids),
        )
        projections = query(
            cursor,
            "REPORT_PROJECTIONS",
            f"""
            SELECT give_gift_id, stat_date, play_mode, giver_user_id, receiver_user_id,
                   valid_wager_coin, giver_return_coin, receiver_lucky_diamond,
                   receiver_lucky_coin_equiv, report_eligible, draw_event_count,
                   projection_state, exclusion_reason, source_settled_at
            FROM lucky_gift_report_projection
            WHERE give_gift_id IN ({marks}) ORDER BY give_gift_id
            """,
            tuple(gift_ids),
        )
        cards = query(
            cursor,
            "CARD_GRANTS",
            f"""
            SELECT id, draw_event_id, give_gift_id, user_id, play_type, business_date,
                   decision, reason, wager_coin, user_return_coin, user_rtp, target_rtp,
                   experience_loss_coin, card_delta, available_card_after, drawn, im_status
            FROM lucky_card_grant_record
            WHERE give_gift_id IN ({marks}) ORDER BY id
            """,
            tuple(gift_ids),
        )

        events_by_gift: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for event in events:
            events_by_gift[event["give_gift_id"]].append(event)
        rewards_by_event: dict[int, list[dict[str, Any]]] = defaultdict(list)
        diamonds_by_gift: dict[int, list[dict[str, Any]]] = defaultdict(list)
        deductions_by_gift: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for log in wallet:
            if log["bus_type"] == 10012:
                rewards_by_event[log["bus_id"]].append(log)
            elif log["bus_type"] == 40002:
                diamonds_by_gift[log["bus_id"]].append(log)
            elif log["user_id"] == user_id and log["bus_id"] in gift_ids:
                deductions_by_gift[log["bus_id"]].append(log)
        projection_by_gift = {item["give_gift_id"]: item for item in projections}

        print("AUDIT_BEGIN")
        for gift in gifts:
            gift_id = gift["id"]
            gift_events = events_by_gift[gift_id]
            accepted = sum((number(item["accepted_unit_price"]) for item in gift_events), Decimal())
            reward_expected = sum((number(item["sender_coin_amount"]) for item in gift_events), Decimal())
            reward_paid = sum(
                (number(item["coin"]) for event in gift_events for item in rewards_by_event[event["id"]] if item["status"] == 1),
                Decimal(),
            )
            recipient_expected = sum((number(item["recipient_diamond_amount"]) for item in gift_events), Decimal())
            base_expected = sum((number(item["base_recipient_diamond_amount"]) for item in gift_events), Decimal())
            diamond_paid = sum(
                (number(item["diamond"]) for item in diamonds_by_gift[gift_id] if item["status"] == 1),
                Decimal(),
            )
            debit = sum((number(item["coin"]) for item in deductions_by_gift[gift_id] if item["status"] == 1), Decimal())
            projection = projection_by_gift.get(gift_id)
            issue: list[str] = []
            if len(gift_events) != gift["number"]:
                issue.append("event_count")
            if accepted != number(gift["total_price"]):
                issue.append("accepted_price")
            if reward_paid != reward_expected:
                issue.append("sender_reward")
            diamond_expected = recipient_expected if gift_events and gift_events[0]["play_type"] == "BILATERAL" else base_expected
            if diamond_expected and diamond_paid != diamond_expected:
                issue.append("recipient_diamond")
            if not projection:
                issue.append("projection_missing")
            print(
                "AUDIT: "
                f"give_gift_id={gift_id} type={gift['type']} units={gift['number']} "
                f"price={gift['total_price']} events={len(gift_events)} accepted={accepted} "
                f"sender_expected={reward_expected} sender_paid={reward_paid} "
                f"recipient_expected={diamond_expected} recipient_paid={diamond_paid} "
                f"sender_debit_log_sum={debit} projection_state={projection['projection_state'] if projection else None} "
                f"issues={','.join(issue) if issue else 'none'}"
            )
        print("AUDIT_END")
        print(
            "TOTALS: "
            f"gifts={len(gifts)} total_price={sum((number(item['total_price']) for item in gifts), Decimal())} "
            f"events={len(events)} sender_coin={sum((number(item['sender_coin_amount']) for item in events), Decimal())} "
            f"projections={len(projections)} cards={len(cards)} "
            f"gift_types={dict(Counter(item['type'] for item in gifts))} "
            f"play_types={dict(Counter(item['play_type'] for item in events))}"
        )
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
