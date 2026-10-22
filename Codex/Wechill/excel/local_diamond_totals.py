from pathlib import Path

import pandas as pd


def u(text):
    return text.encode("ascii").decode("unicode_escape")


ROOT = Path.cwd()


def find_file(suffix, marker):
    matches = [p for p in ROOT.iterdir() if p.suffix.lower() == suffix and marker in p.name]
    if len(matches) != 1:
        raise RuntimeError("file not found for %s %s" % (suffix, marker))
    return matches[0]


def nsum(series):
    return int(pd.to_numeric(series, errors="coerce").fillna(0).sum())


def main():
    rows = []
    flow_col = u("\\u4e3b\\u64ad\\u4e0a\\u5468\\u671f\\u94bb\\u77f3\\u6d41\\u6c34")
    user_col = u("\\u4e3b\\u64adid")
    for label, csv_marker, xlsx_marker in [
        ("1-15", "1-15", "6.1-6.15"),
        ("16-30", "16-30", "6.16-6.30"),
    ]:
        csv_path = find_file(".csv", csv_marker)
        xlsx_path = find_file(".xlsx", xlsx_marker)
        csv_df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
        xlsx_df = pd.read_excel(xlsx_path, dtype=str, keep_default_na=False)
        host_df = csv_df[csv_df["Role"].astype(str).str.strip() == u("\\u4e3b\\u64ad")]
        rows.append(
            {
                "period": label,
                "csv_total_rows": len(csv_df),
                "csv_host_rows": len(host_df),
                "csv_host_unique_user_id": host_df["UserId"].astype(str).nunique(),
                "xlsx_rows": len(xlsx_df),
                "xlsx_unique_user_id": xlsx_df[user_col].astype(str).nunique(),
                "csv_sum_diamond_change": nsum(host_df["DiamondChange"]),
                "csv_sum_period_diamond_flow": nsum(host_df["PeriodDiamondFlow"]),
                "xlsx_sum_flow": nsum(xlsx_df[flow_col]),
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv("local_diamond_totals.csv", index=False, encoding="utf-8-sig")
    print("local_diamond_totals.csv")


if __name__ == "__main__":
    main()
