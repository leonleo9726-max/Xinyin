import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd


ROOT = Path.cwd()
PAIRS = [
    {
        "period": "2026-06-01..2026-06-15",
        "label": "1-15",
        "csv": "主播薪资结算数据1-15.csv",
        "xlsx": "主播在麦时长+钻石流水6.1-6.15.xlsx",
    },
    {
        "period": "2026-06-16..2026-06-30",
        "label": "16-30",
        "csv": "主播薪资结算数据16-30.csv",
        "xlsx": "主播在麦时长+钻石流水6.16-6.30.xlsx",
    },
]


def num(value):
    if pd.isna(value):
        return Decimal(0)
    text = str(value).strip()
    if text == "":
        return Decimal(0)
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def load_csv(path):
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    for col in ["UserId", "UserNumber", "AgencyId"]:
        df[col] = df[col].astype(str).str.strip()
    df["_exchange"] = df["ExchangeDiamond"].map(num)
    return df


def load_xlsx(path):
    df = pd.read_excel(path, dtype=str, keep_default_na=False)
    rename = {
        "主播id": "UserId",
        "主播靓号": "UserNumber",
        "公会id": "AgencyId",
        "主播上周期钻石流水": "XlsxDiamondFlow",
    }
    df = df.rename(columns=rename)
    for col in ["UserId", "UserNumber", "AgencyId"]:
        df[col] = df[col].astype(str).str.strip()
    df["_flow"] = df["XlsxDiamondFlow"].map(num)
    return df


def to_plain(value):
    if isinstance(value, Decimal):
        return str(value)
    if pd.isna(value):
        return ""
    return str(value)


def records_for(df, columns, max_rows=None):
    work = df[columns].copy()
    for col in columns:
        work[col] = work[col].map(to_plain)
    if max_rows is not None:
        work = work.head(max_rows)
    return work.to_dict(orient="records")


def compare_pair(pair):
    csv_df = load_csv(ROOT / pair["csv"])
    xlsx_df = load_xlsx(ROOT / pair["xlsx"])

    host_csv = csv_df[csv_df["Role"].astype(str).str.strip() == "主播"].copy()

    csv_dups_id = host_csv[host_csv.duplicated(["UserId"], keep=False)]
    xlsx_dups_id = xlsx_df[xlsx_df.duplicated(["UserId"], keep=False)]
    csv_dups_number = host_csv[host_csv.duplicated(["UserNumber"], keep=False)]
    xlsx_dups_number = xlsx_df[xlsx_df.duplicated(["UserNumber"], keep=False)]

    merged = host_csv.merge(
        xlsx_df,
        on="UserId",
        how="outer",
        suffixes=("_csv", "_xlsx"),
        indicator=True,
    )

    mismatches = []
    only_csv = []
    only_xlsx = []
    key_conflicts = []
    invalid_numbers = []

    for _, row in merged.iterrows():
        state = row["_merge"]
        if state == "both":
            exchange = row["_exchange"]
            flow = row["_flow"]
            diff = None if exchange is None or flow is None else exchange - flow
            if str(row.get("UserNumber_csv", "")).strip() != str(row.get("UserNumber_xlsx", "")).strip():
                key_conflicts.append(
                    {
                        "period": pair["label"],
                        "UserId": row["UserId"],
                        "csv_user_number": row.get("UserNumber_csv", ""),
                        "xlsx_user_number": row.get("UserNumber_xlsx", ""),
                    }
                )
            if exchange is None or flow is None:
                invalid_numbers.append(
                    {
                        "period": pair["label"],
                        "UserId": row["UserId"],
                        "UserNumber": row.get("UserNumber_csv", row.get("UserNumber_xlsx", "")),
                        "csv_exchange": row.get("ExchangeDiamond", ""),
                        "xlsx_flow": row.get("XlsxDiamondFlow", ""),
                    }
                )
            elif diff != 0:
                mismatches.append(
                    {
                        "period": pair["label"],
                        "UserId": row["UserId"],
                        "UserNumber": row.get("UserNumber_csv", ""),
                        "Nickname": row.get("Nickname", ""),
                        "AgencyId": row.get("AgencyId_csv", ""),
                        "AgencyName": row.get("AgencyName", ""),
                        "Policy": row.get("Policy", ""),
                        "csv_exchange": exchange,
                        "xlsx_flow": flow,
                        "diff_csv_minus_xlsx": diff,
                    }
                )
        elif state == "left_only":
            only_csv.append(
                {
                    "period": pair["label"],
                    "UserId": row["UserId"],
                    "UserNumber": row.get("UserNumber_csv", ""),
                    "Nickname": row.get("Nickname", ""),
                    "AgencyId": row.get("AgencyId_csv", ""),
                    "AgencyName": row.get("AgencyName", ""),
                    "Policy": row.get("Policy", ""),
                    "csv_exchange": row.get("_exchange", ""),
                }
            )
        elif state == "right_only":
            only_xlsx.append(
                {
                    "period": pair["label"],
                    "UserId": row["UserId"],
                    "UserNumber": row.get("UserNumber_xlsx", ""),
                    "AgencyId": row.get("AgencyId_xlsx", ""),
                    "xlsx_flow": row.get("_flow", ""),
                }
            )

    all_diffs = mismatches + only_csv + only_xlsx
    user_ids = sorted({str(item["UserId"]) for item in all_diffs if str(item.get("UserId", "")).strip()})
    user_numbers = sorted({str(item.get("UserNumber", "")) for item in all_diffs if str(item.get("UserNumber", "")).strip()})

    summary = {
        "period": pair["label"],
        "csv_file": pair["csv"],
        "xlsx_file": pair["xlsx"],
        "csv_rows_total": int(len(csv_df)),
        "csv_host_rows": int(len(host_csv)),
        "xlsx_rows": int(len(xlsx_df)),
        "matched_host_rows": int((merged["_merge"] == "both").sum()),
        "mismatch_value_rows": len(mismatches),
        "only_csv_host_rows": len(only_csv),
        "only_xlsx_rows": len(only_xlsx),
        "csv_duplicate_user_id_rows": int(len(csv_dups_id)),
        "xlsx_duplicate_user_id_rows": int(len(xlsx_dups_id)),
        "csv_duplicate_user_number_rows": int(len(csv_dups_number)),
        "xlsx_duplicate_user_number_rows": int(len(xlsx_dups_number)),
        "key_conflict_rows": len(key_conflicts),
        "invalid_number_rows": len(invalid_numbers),
        "csv_columns": list(csv_df.columns.drop(["_exchange"])),
        "xlsx_columns": list(xlsx_df.columns.drop(["_flow"])),
        "csv_preview": records_for(csv_df, list(csv_df.columns.drop(["_exchange"])), 3),
        "xlsx_preview": records_for(xlsx_df, list(xlsx_df.columns.drop(["_flow"])), 3),
        "diff_user_ids": user_ids,
        "diff_user_numbers": user_numbers,
    }

    diff_rows = []
    for item in mismatches:
        record = dict(item)
        record["difference_type"] = "value_mismatch"
        diff_rows.append(record)
    for item in only_csv:
        record = dict(item)
        record["difference_type"] = "only_in_salary_csv"
        record["xlsx_flow"] = ""
        record["diff_csv_minus_xlsx"] = ""
        diff_rows.append(record)
    for item in only_xlsx:
        record = dict(item)
        record["difference_type"] = "only_in_flow_xlsx"
        record["Nickname"] = ""
        record["AgencyName"] = ""
        record["Policy"] = ""
        record["csv_exchange"] = ""
        record["diff_csv_minus_xlsx"] = ""
        diff_rows.append(record)

    return {
        "summary": summary,
        "diff_rows": diff_rows,
        "key_conflicts": key_conflicts,
        "invalid_numbers": invalid_numbers,
    }


def main():
    result = {"pairs": []}
    all_diffs = []
    for pair in PAIRS:
        compared = compare_pair(pair)
        result["pairs"].append(compared)
        all_diffs.extend(compared["diff_rows"])

    out_json = ROOT / "compare_salary_diamond_result.json"
    out_json.write_text(json.dumps(result, ensure_ascii=True, indent=2, default=to_plain), encoding="ascii")

    if all_diffs:
        out_csv = ROOT / "compare_salary_diamond_diffs.csv"
        diff_df = pd.DataFrame(all_diffs)
        for col in diff_df.columns:
            diff_df[col] = diff_df[col].map(to_plain)
        diff_df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    print(str(out_json.name))


if __name__ == "__main__":
    main()
