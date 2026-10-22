import csv
from pathlib import Path

import pandas as pd


PERIOD_TIME = {"1-15": "2026-06-15 23:59:59", "16-30": "2026-06-30 23:59:59"}


def main():
    diffs = pd.read_csv("compare_diamond_change_diffs_zh.csv", dtype=str, keep_default_na=False)
    rows = []
    for period in ["1-15", "16-30"]:
        p = diffs[diffs["period"] == period].copy()
        p["abs_diff"] = pd.to_numeric(p["Diff_CSV_Minus_XLSX"], errors="coerce").abs().fillna(0)
        sample = p.sort_values("abs_diff", ascending=False).head(40)
        for _, row in sample.iterrows():
            rows.append(
                {
                    "period": period,
                    "user_id": row["UserId"],
                    "DiamondChange": row["DiamondChange"],
                    "PeriodDiamondFlow": row["PeriodDiamondFlow"],
                    "XlsxDiamondFlow": row["XlsxDiamondFlow"],
                    "settlement_time": PERIOD_TIME[period],
                }
            )
    pd.DataFrame(rows).to_csv("probe_users.csv", index=False, encoding="utf-8-sig")
    ids = ",".join(sorted(set(r["user_id"] for r in rows if r["user_id"])))
    Path("probe_user_ids.txt").write_text(ids, encoding="ascii")
    print("probe_users.csv")
    print("probe_user_ids.txt")


if __name__ == "__main__":
    main()
