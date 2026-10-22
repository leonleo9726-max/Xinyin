import csv
import json
from collections import defaultdict
from pathlib import Path


KEEP = [
    "period",
    "difference_type",
    "cause",
    "UserId",
    "CSV_UserNumber",
    "XLSX_UserNumber",
    "Policy",
    "DiamondChange",
    "PeriodDiamondFlow",
    "XlsxDiamondFlow",
    "Diff_CSV_Minus_XLSX",
    "SalaryCsvRole",
]


def main():
    groups = defaultdict(list)
    with Path("compare_diamond_change_diffs.csv").open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["period"], row["cause"])
            if len(groups[key]) < 3:
                groups[key].append({k: row.get(k, "") for k in KEEP})
    serializable = {"groups": [{"period": k[0], "cause": k[1], "rows": v} for k, v in sorted(groups.items())]}
    Path("compare_diamond_change_samples.json").write_text(
        json.dumps(serializable, ensure_ascii=True, indent=2), encoding="ascii"
    )
    print("compare_diamond_change_samples.json")


if __name__ == "__main__":
    main()
