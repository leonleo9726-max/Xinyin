from pathlib import Path

import pandas as pd


def find_file(marker):
    matches = [p for p in Path.cwd().iterdir() if p.suffix.lower() == ".csv" and marker in p.name]
    if len(matches) != 1:
        raise RuntimeError("missing csv")
    return matches[0]


def main():
    lines = []
    for label, marker in [("1-15", "1-15"), ("16-30", "16-30")]:
        df = pd.read_csv(find_file(marker), dtype=str, keep_default_na=False)
        for col in ["StartDiamondBalance", "EndDiamondBalance", "DiamondChange"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int64")
        df["_calc"] = df["EndDiamondBalance"] - df["StartDiamondBalance"]
        mismatch = int((df["_calc"] != df["DiamondChange"]).sum())
        lines.append("%s,total_rows=%d,diamond_change_not_end_minus_start=%d" % (label, len(df), mismatch))
    Path("diamond_change_formula_check.txt").write_text("\n".join(lines), encoding="ascii")
    print("diamond_change_formula_check.txt")


if __name__ == "__main__":
    main()
