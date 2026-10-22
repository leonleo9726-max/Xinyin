import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd


ROOT = Path.cwd()


def u(text):
    return text.encode("ascii").decode("unicode_escape")


PERIODS = [
    {
        "label": "1-15",
        "csv_marker": "1-15",
        "xlsx_marker": "6.1-6.15",
    },
    {
        "label": "16-30",
        "csv_marker": "16-30",
        "xlsx_marker": "6.16-6.30",
    },
]

COL_ROLE = "Role"
COL_HOST_ROLE = u("\\u4e3b\\u64ad")
COL_X_USER_ID = u("\\u4e3b\\u64adid")
COL_X_USER_NUMBER = u("\\u4e3b\\u64ad\\u9753\\u53f7")
COL_X_AGENCY_ID = u("\\u516c\\u4f1aid")
COL_X_AGENCY_NAME = u("\\u516c\\u4f1a\\u540d")
COL_X_HOST_NAME = u("\\u4e3b\\u64ad\\u540d")
COL_X_VALID_DAYS = u("\\u4e3b\\u64ad\\u4e0a\\u4e2a\\u5468\\u671f\\u7684\\u6709\\u6548\\u5929\\u6570")
COL_X_HOURS = u(
    "\\u4e3b\\u64ad\\u4e0a\\u5468\\u671f\\u7684\\u4e0a\\u9ea6\\u65f6\\u95f4\\u603b\\u548c(\\u5c0f\\u65f6)"
)
COL_X_FLOW = u("\\u4e3b\\u64ad\\u4e0a\\u5468\\u671f\\u94bb\\u77f3\\u6d41\\u6c34")


def find_file(suffix, marker):
    matches = sorted([p for p in ROOT.iterdir() if p.suffix.lower() == suffix and marker in p.name])
    if len(matches) != 1:
        raise RuntimeError("expected one %s file for marker %s, got %d" % (suffix, marker, len(matches)))
    return matches[0]


def as_text(value):
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0") and text[:-2].isdigit():
        text = text[:-2]
    return text


def as_decimal(value):
    text = as_text(value)
    if text == "":
        return Decimal("0")
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def dec_out(value):
    if value is None:
        return ""
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return str(value.quantize(Decimal("1")))
        return format(value.normalize(), "f")
    return as_text(value)


def load_csv(path):
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    for col in ["UserId", "UserNumber", "AgencyId"]:
        if col in df.columns:
            df[col] = df[col].map(as_text)
    df["_diamond_change"] = df["DiamondChange"].map(as_decimal)
    df["_balance_check"] = df.apply(
        lambda row: as_decimal(row.get("EndDiamondBalance", "")) - as_decimal(row.get("StartDiamondBalance", ""))
        if as_decimal(row.get("EndDiamondBalance", "")) is not None
        and as_decimal(row.get("StartDiamondBalance", "")) is not None
        else None,
        axis=1,
    )
    return df


def load_xlsx(path):
    df = pd.read_excel(path, dtype=str, keep_default_na=False)
    rename = {
        COL_X_USER_ID: "UserId",
        COL_X_USER_NUMBER: "UserNumber",
        COL_X_AGENCY_ID: "XlsxAgencyId",
        COL_X_AGENCY_NAME: "XlsxAgencyName",
        COL_X_HOST_NAME: "XlsxHostName",
        COL_X_VALID_DAYS: "XlsxValidDays",
        COL_X_HOURS: "XlsxHours",
        COL_X_FLOW: "XlsxDiamondFlow",
    }
    missing = [col for col in rename if col not in df.columns]
    if missing:
        raise RuntimeError("xlsx missing columns: %s" % ",".join(missing))
    df = df.rename(columns=rename)
    for col in ["UserId", "UserNumber", "XlsxAgencyId"]:
        df[col] = df[col].map(as_text)
    df["_xlsx_flow"] = df["XlsxDiamondFlow"].map(as_decimal)
    return df


def row_text(row, col):
    if col not in row:
        return ""
    return as_text(row[col])


def build_preview(df, cols, n=3):
    preview = []
    for _, row in df.head(n).iterrows():
        preview.append({col: row_text(row, col) for col in cols})
    return preview


def cause_for(row, diff_type, diff, csv_role_by_user_id=None):
    csv_role_by_user_id = csv_role_by_user_id or {}
    if diff_type == "only_in_salary_csv":
        csv_change = row["_diamond_change"]
        period_flow = as_decimal(row.get("PeriodDiamondFlow", ""))
        if csv_change == Decimal("0") and period_flow == Decimal("0"):
            return "salary_csv_zero_change_zero_period_flow_not_in_xlsx"
        if period_flow == Decimal("0") and csv_change != Decimal("0"):
            return "salary_csv_balance_change_without_period_flow_not_in_xlsx"
        if period_flow is not None and period_flow != Decimal("0"):
            return "salary_csv_has_period_flow_but_missing_in_xlsx"
        return "salary_csv_has_host_but_xlsx_missing_user_id"
    if diff_type == "only_in_flow_xlsx":
        user_id = row_text(row, "UserId")
        role = csv_role_by_user_id.get(user_id, "")
        if role and role != COL_HOST_ROLE:
            return "xlsx_user_exists_in_salary_csv_as_non_host_role"
        if row["_xlsx_flow"] == Decimal("0"):
            return "xlsx_zero_flow_user_not_in_salary_csv_host"
        return "xlsx_has_host_but_salary_csv_missing_host_user_id"
    if row_text(row, "UserNumber_csv") and row_text(row, "UserNumber_xlsx") and row_text(row, "UserNumber_csv") != row_text(row, "UserNumber_xlsx"):
        return "matched_by_user_id_but_user_number_differs"
    csv_change = row["_diamond_change"]
    balance_check = row["_balance_check"]
    xlsx_flow = row["_xlsx_flow"]
    period_flow = as_decimal(row.get("PeriodDiamondFlow", ""))
    if balance_check is not None and csv_change != balance_check:
        return "csv_diamond_change_not_equal_end_minus_start"
    if period_flow is not None and period_flow == xlsx_flow and csv_change != xlsx_flow:
        return "xlsx_matches_csv_period_diamond_flow_not_diamond_change"
    if period_flow is not None and period_flow == csv_change and csv_change != xlsx_flow:
        return "csv_period_diamond_flow_matches_diamond_change_xlsx_differs"
    if csv_change == Decimal("0") and xlsx_flow != Decimal("0"):
        return "csv_diamond_change_zero_but_xlsx_has_flow"
    if csv_change != Decimal("0") and xlsx_flow == Decimal("0"):
        return "xlsx_flow_zero_but_csv_diamond_change_nonzero"
    if diff is not None and diff < 0:
        return "xlsx_flow_greater_than_csv_diamond_change"
    if diff is not None and diff > 0:
        return "csv_diamond_change_greater_than_xlsx_flow"
    return "value_mismatch"


def compare_period(period):
    csv_path = find_file(".csv", period["csv_marker"])
    xlsx_path = find_file(".xlsx", period["xlsx_marker"])
    csv_df = load_csv(csv_path)
    xlsx_df = load_xlsx(xlsx_path)

    host_csv = csv_df[csv_df[COL_ROLE].map(as_text) == COL_HOST_ROLE].copy()
    non_host_csv = csv_df[csv_df[COL_ROLE].map(as_text) != COL_HOST_ROLE].copy()
    csv_role_by_user_id = {}
    for _, csv_row in csv_df.iterrows():
        csv_role_by_user_id.setdefault(row_text(csv_row, "UserId"), row_text(csv_row, COL_ROLE))

    merged = host_csv.merge(
        xlsx_df,
        on="UserId",
        how="outer",
        suffixes=("_csv", "_xlsx"),
        indicator=True,
    )

    diffs = []
    invalid_rows = []
    key_conflicts = []

    for _, row in merged.iterrows():
        merge_state = row["_merge"]
        if merge_state == "both":
            csv_val = row["_diamond_change"]
            xlsx_val = row["_xlsx_flow"]
            if csv_val is None or xlsx_val is None:
                invalid_rows.append(row)
                continue
            diff = csv_val - xlsx_val
            if row_text(row, "UserNumber_csv") != row_text(row, "UserNumber_xlsx"):
                key_conflicts.append(row)
            if diff != 0:
                cause = cause_for(row, "value_mismatch", diff, csv_role_by_user_id)
                diffs.append(
                    {
                        "period": period["label"],
                        "difference_type": "value_mismatch",
                        "cause": cause,
                        "UserId": row_text(row, "UserId"),
                        "CSV_UserNumber": row_text(row, "UserNumber_csv"),
                        "XLSX_UserNumber": row_text(row, "UserNumber_xlsx"),
                        "Nickname": row_text(row, "Nickname"),
                        "AgencyId": row_text(row, "AgencyId"),
                        "AgencyName": row_text(row, "AgencyName"),
                        "Policy": row_text(row, "Policy"),
                        "StartDiamondBalance": dec_out(as_decimal(row.get("StartDiamondBalance", ""))),
                        "EndDiamondBalance": dec_out(as_decimal(row.get("EndDiamondBalance", ""))),
                        "DiamondChange": dec_out(csv_val),
                        "PeriodDiamondFlow": dec_out(as_decimal(row.get("PeriodDiamondFlow", ""))),
                        "XlsxDiamondFlow": dec_out(xlsx_val),
                        "Diff_CSV_Minus_XLSX": dec_out(diff),
                        "XlsxValidDays": row_text(row, "XlsxValidDays"),
                        "XlsxHours": row_text(row, "XlsxHours"),
                    }
                )
        elif merge_state == "left_only":
            csv_val = row["_diamond_change"]
            diffs.append(
                {
                    "period": period["label"],
                    "difference_type": "only_in_salary_csv",
                    "cause": cause_for(row, "only_in_salary_csv", None, csv_role_by_user_id),
                    "UserId": row_text(row, "UserId"),
                    "CSV_UserNumber": row_text(row, "UserNumber_csv"),
                    "XLSX_UserNumber": "",
                    "Nickname": row_text(row, "Nickname"),
                    "AgencyId": row_text(row, "AgencyId"),
                    "AgencyName": row_text(row, "AgencyName"),
                    "Policy": row_text(row, "Policy"),
                    "StartDiamondBalance": dec_out(as_decimal(row.get("StartDiamondBalance", ""))),
                    "EndDiamondBalance": dec_out(as_decimal(row.get("EndDiamondBalance", ""))),
                    "DiamondChange": dec_out(csv_val),
                    "PeriodDiamondFlow": dec_out(as_decimal(row.get("PeriodDiamondFlow", ""))),
                    "XlsxDiamondFlow": "",
                    "Diff_CSV_Minus_XLSX": "",
                    "XlsxValidDays": "",
                    "XlsxHours": "",
                    "SalaryCsvRole": row_text(row, COL_ROLE),
                }
            )
        elif merge_state == "right_only":
            xlsx_val = row["_xlsx_flow"]
            diffs.append(
                {
                    "period": period["label"],
                    "difference_type": "only_in_flow_xlsx",
                    "cause": cause_for(row, "only_in_flow_xlsx", None, csv_role_by_user_id),
                    "UserId": row_text(row, "UserId"),
                    "CSV_UserNumber": "",
                    "XLSX_UserNumber": row_text(row, "UserNumber_xlsx"),
                    "Nickname": row_text(row, "XlsxHostName"),
                    "AgencyId": row_text(row, "XlsxAgencyId"),
                    "AgencyName": row_text(row, "XlsxAgencyName"),
                    "Policy": "",
                    "StartDiamondBalance": "",
                    "EndDiamondBalance": "",
                    "DiamondChange": "",
                    "PeriodDiamondFlow": "",
                    "XlsxDiamondFlow": dec_out(xlsx_val),
                    "Diff_CSV_Minus_XLSX": "",
                    "XlsxValidDays": row_text(row, "XlsxValidDays"),
                    "XlsxHours": row_text(row, "XlsxHours"),
                    "SalaryCsvRole": csv_role_by_user_id.get(row_text(row, "UserId"), ""),
                }
            )

    exact_match = int(((merged["_merge"] == "both") & (merged["_diamond_change"] == merged["_xlsx_flow"])).sum())
    value_mismatch = len([r for r in diffs if r["difference_type"] == "value_mismatch"])
    only_csv = len([r for r in diffs if r["difference_type"] == "only_in_salary_csv"])
    only_xlsx = len([r for r in diffs if r["difference_type"] == "only_in_flow_xlsx"])

    cause_counts = {}
    for item in diffs:
        cause_counts[item["cause"]] = cause_counts.get(item["cause"], 0) + 1

    summary = {
        "period": period["label"],
        "csv_file": csv_path.name,
        "xlsx_file": xlsx_path.name,
        "csv_rows_total": int(len(csv_df)),
        "csv_host_rows": int(len(host_csv)),
        "csv_non_host_excluded_rows": int(len(non_host_csv)),
        "xlsx_rows": int(len(xlsx_df)),
        "matched_user_id_rows": int((merged["_merge"] == "both").sum()),
        "exact_match_rows": exact_match,
        "value_mismatch_rows": value_mismatch,
        "only_in_salary_csv_rows": only_csv,
        "only_in_flow_xlsx_rows": only_xlsx,
        "csv_duplicate_host_user_id_rows": int(host_csv[host_csv.duplicated(["UserId"], keep=False)].shape[0]),
        "xlsx_duplicate_user_id_rows": int(xlsx_df[xlsx_df.duplicated(["UserId"], keep=False)].shape[0]),
        "key_conflict_rows": len(key_conflicts),
        "invalid_number_rows": len(invalid_rows),
        "cause_counts": cause_counts,
        "csv_columns": [str(c) for c in csv_df.columns if not str(c).startswith("_")],
        "xlsx_columns": [str(c) for c in xlsx_df.columns if not str(c).startswith("_")],
        "csv_preview": build_preview(csv_df, [c for c in csv_df.columns if not str(c).startswith("_")]),
        "xlsx_preview": build_preview(xlsx_df, [c for c in xlsx_df.columns if not str(c).startswith("_")]),
    }
    return summary, diffs


def write_outputs(result):
    json_path = ROOT / "compare_diamond_change_result.json"
    json_path.write_text(json.dumps(result, ensure_ascii=True, indent=2), encoding="ascii")
    all_diffs = []
    for period in result["periods"]:
        all_diffs.extend(period["diffs"])
    csv_path = ROOT / "compare_diamond_change_diffs.csv"
    if all_diffs:
        pd.DataFrame(all_diffs).to_csv(csv_path, index=False, encoding="utf-8-sig")
    else:
        pd.DataFrame([]).to_csv(csv_path, index=False, encoding="utf-8-sig")
    return json_path, csv_path


def main():
    result = {"periods": []}
    for period in PERIODS:
        summary, diffs = compare_period(period)
        result["periods"].append({"summary": summary, "diffs": diffs})
    json_path, csv_path = write_outputs(result)
    print(json_path.name)
    print(csv_path.name)


if __name__ == "__main__":
    main()
