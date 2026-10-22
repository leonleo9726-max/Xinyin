import json
from pathlib import Path


def main():
    data = json.loads(Path("compare_diamond_change_result.json").read_text(encoding="ascii"))
    lines = []
    for period in data["periods"]:
        s = period["summary"]
        lines.append("PERIOD %s" % s["period"])
        keys = [
            "csv_host_rows",
            "xlsx_rows",
            "matched_user_id_rows",
            "exact_match_rows",
            "value_mismatch_rows",
            "only_in_salary_csv_rows",
            "only_in_flow_xlsx_rows",
            "csv_duplicate_host_user_id_rows",
            "xlsx_duplicate_user_id_rows",
            "key_conflict_rows",
            "invalid_number_rows",
        ]
        for key in keys:
            lines.append("%s=%s" % (key, s[key]))
        lines.append("cause_counts:")
        for key, value in sorted(s["cause_counts"].items()):
            lines.append("  %s=%s" % (key, value))
        lines.append("")
    Path("compare_diamond_change_summary.txt").write_text("\n".join(lines), encoding="ascii")
    print("compare_diamond_change_summary.txt")


if __name__ == "__main__":
    main()
