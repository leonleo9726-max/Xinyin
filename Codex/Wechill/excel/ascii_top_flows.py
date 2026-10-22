import csv
from pathlib import Path


def main():
    with Path("top_local_flows.csv").open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    lines = []
    for period in ["1-15", "16-30"]:
        lines.append("PERIOD %s" % period)
        for row in [r for r in rows if r["period"] == period][:20]:
            lines.append("%s,%s,%s" % (row["user_id"], row["user_number"], row["xlsx_flow"]))
        lines.append("")
    Path("top_local_flows_ascii.txt").write_text("\n".join(lines), encoding="ascii")
    print("top_local_flows_ascii.txt")


if __name__ == "__main__":
    main()
