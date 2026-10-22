from pathlib import Path

import pandas as pd


def u(text):
    return text.encode("ascii").decode("unicode_escape")


def find_file(suffix, marker):
    matches = [p for p in Path.cwd().iterdir() if p.suffix.lower() == suffix and marker in p.name]
    if len(matches) != 1:
        raise RuntimeError("missing file")
    return matches[0]


def main():
    flow_col = u("\\u4e3b\\u64ad\\u4e0a\\u5468\\u671f\\u94bb\\u77f3\\u6d41\\u6c34")
    id_col = u("\\u4e3b\\u64adid")
    num_col = u("\\u4e3b\\u64ad\\u9753\\u53f7")
    name_col = u("\\u4e3b\\u64ad\\u540d")
    out_rows = []
    for label, marker in [("1-15", "6.1-6.15"), ("16-30", "6.16-6.30")]:
        df = pd.read_excel(find_file(".xlsx", marker), dtype=str, keep_default_na=False)
        df["_flow"] = pd.to_numeric(df[flow_col], errors="coerce").fillna(0).astype("int64")
        top = df.sort_values("_flow", ascending=False).head(30)
        for _, row in top.iterrows():
            out_rows.append(
                {
                    "period": label,
                    "user_id": str(row[id_col]).strip(),
                    "user_number": str(row[num_col]).strip(),
                    "name": str(row[name_col]).strip(),
                    "xlsx_flow": int(row["_flow"]),
                }
            )
    pd.DataFrame(out_rows).to_csv("top_local_flows.csv", index=False, encoding="utf-8-sig")
    print("top_local_flows.csv")


if __name__ == "__main__":
    main()
