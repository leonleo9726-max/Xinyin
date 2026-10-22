import csv
import json
from pathlib import Path

import pandas as pd


REASON_ZH = {
    "xlsx_matches_csv_period_diamond_flow_not_diamond_change": "XLSX流水等于CSV的PeriodDiamondFlow，不等于DiamondChange；字段口径不同。",
    "csv_period_diamond_flow_matches_diamond_change_xlsx_differs": "CSV的DiamondChange与PeriodDiamondFlow一致，但XLSX流水不同；两张表流水来源/周期不一致。",
    "csv_diamond_change_zero_but_xlsx_has_flow": "CSV的DiamondChange为0，但XLSX存在流水；DiamondChange是余额变动，不等同流水。",
    "xlsx_flow_greater_than_csv_diamond_change": "XLSX流水大于CSV的DiamondChange；字段口径或统计范围不同。",
    "csv_diamond_change_greater_than_xlsx_flow": "CSV的DiamondChange大于XLSX流水；字段口径或统计范围不同。",
    "salary_csv_has_period_flow_but_missing_in_xlsx": "薪资CSV有主播且PeriodDiamondFlow非0，但XLSX按主播id未找到该主播。",
    "salary_csv_zero_change_zero_period_flow_not_in_xlsx": "薪资CSV有主播，但DiamondChange和PeriodDiamondFlow均为0，XLSX未收录该主播。",
    "xlsx_has_host_but_salary_csv_missing_host_user_id": "XLSX有主播流水，但薪资CSV按UserId未找到主播行。",
    "xlsx_user_exists_in_salary_csv_as_non_host_role": "XLSX有主播流水，但该UserId在薪资CSV中是非主播角色，已被主播口径排除。",
    "xlsx_zero_flow_user_not_in_salary_csv_host": "XLSX流水为0，薪资CSV没有对应主播行。",
    "matched_by_user_id_but_user_number_differs": "UserId匹配成功，但靓号不一致。",
    "csv_diamond_change_not_equal_end_minus_start": "CSV的DiamondChange不等于EndDiamondBalance-StartDiamondBalance。",
}


def table(headers, rows):
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(h, "")) for h in headers) + " |")
    return "\n".join(lines)


def main():
    result = json.loads(Path("compare_diamond_change_result.json").read_text(encoding="ascii"))
    rows = []
    for period in result["periods"]:
        rows.extend(period["diffs"])

    for row in rows:
        row["差异原因"] = REASON_ZH.get(row.get("cause", ""), row.get("cause", ""))

    detail_path = Path("compare_diamond_change_diffs_zh.csv")
    pd.DataFrame(rows).to_csv(detail_path, index=False, encoding="utf-8-sig")

    summary_rows = []
    cause_rows = []
    for period in result["periods"]:
        s = period["summary"]
        summary_rows.append(
            {
                "周期": s["period"],
                "薪资CSV总行": s["csv_rows_total"],
                "薪资CSV主播行": s["csv_host_rows"],
                "已排除非主播行": s["csv_non_host_excluded_rows"],
                "XLSX行": s["xlsx_rows"],
                "UserId匹配行": s["matched_user_id_rows"],
                "完全一致行": s["exact_match_rows"],
                "数值不一致行": s["value_mismatch_rows"],
                "仅薪资CSV有": s["only_in_salary_csv_rows"],
                "仅XLSX有": s["only_in_flow_xlsx_rows"],
                "CSV主播UserId重复": s["csv_duplicate_host_user_id_rows"],
                "XLSX主播id重复": s["xlsx_duplicate_user_id_rows"],
                "靓号冲突": s["key_conflict_rows"],
                "非法数值": s["invalid_number_rows"],
            }
        )
        for cause, count in sorted(s["cause_counts"].items()):
            cause_rows.append(
                {
                    "周期": s["period"],
                    "差异原因": REASON_ZH.get(cause, cause),
                    "行数": count,
                }
            )

    summary_path = Path("compare_diamond_change_summary.csv")
    cause_path = Path("compare_diamond_change_cause_summary.csv")
    pd.DataFrame(summary_rows).to_csv(summary_path, index=False, encoding="utf-8-sig")
    pd.DataFrame(cause_rows).to_csv(cause_path, index=False, encoding="utf-8-sig")

    lines = ["# DiamondChange vs 主播上周期钻石流水 对比报告", ""]
    lines.append("## 汇总")
    lines.append(table(list(summary_rows[0].keys()), summary_rows))
    lines.append("")
    lines.append("## 差异原因")
    lines.append(table(list(cause_rows[0].keys()), cause_rows))
    lines.append("")
    lines.append("## 文件")
    lines.append("- compare_diamond_change_diffs_zh.csv")
    lines.append("- compare_diamond_change_summary.csv")
    lines.append("- compare_diamond_change_cause_summary.csv")
    Path("compare_diamond_change_report.md").write_text("\n".join(lines), encoding="utf-8")
    print("compare_diamond_change_report.md")
    print(str(detail_path))


if __name__ == "__main__":
    main()
