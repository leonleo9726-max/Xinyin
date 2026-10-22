from pathlib import Path

import pandas as pd


def u(text):
    return text.encode("ascii").decode("unicode_escape")


def main():
    path = [p for p in Path.cwd().iterdir() if p.suffix.lower() == ".xlsx" and "6.1-6.15" in p.name][0]
    df = pd.read_excel(path, dtype=str, keep_default_na=False)
    user_col = u("\\u4e3b\\u64adid")
    number_col = u("\\u4e3b\\u64ad\\u9753\\u53f7")
    flow_col = u("\\u4e3b\\u64ad\\u4e0a\\u5468\\u671f\\u94bb\\u77f3\\u6d41\\u6c34")
    dup = df[df.duplicated([user_col], keep=False)].copy()
    dup[[user_col, number_col, flow_col]].to_csv("xlsx_1_15_duplicate_user_ids.csv", index=False, encoding="utf-8-sig")
    print("xlsx_1_15_duplicate_user_ids.csv")


if __name__ == "__main__":
    main()
