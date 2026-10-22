import json
from pathlib import Path

import pandas as pd


def pick_files():
    root = Path.cwd()
    files = {}
    for path in root.iterdir():
        name = path.name
        if path.suffix.lower() == ".csv":
            if "1-15" in name:
                files["csv_1_15"] = path
            elif "16-30" in name:
                files["csv_16_30"] = path
        elif path.suffix.lower() == ".xlsx":
            if "6.1-6.15" in name:
                files["xlsx_1_15"] = path
            elif "6.16-6.30" in name:
                files["xlsx_16_30"] = path
    return files


def preview_csv(path):
    df = pd.read_csv(path, nrows=3)
    return {
        "file": path.name,
        "rows_previewed": len(df),
        "columns": list(df.columns),
        "preview": df.fillna("").astype(str).to_dict(orient="records"),
    }


def preview_xlsx(path):
    book = pd.ExcelFile(path)
    sheets = []
    for sheet in book.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet, nrows=3)
        sheets.append(
            {
                "sheet": sheet,
                "rows_previewed": len(df),
                "columns": [str(c) for c in df.columns],
                "preview": df.fillna("").astype(str).to_dict(orient="records"),
            }
        )
    return {"file": path.name, "sheets": sheets}


def main():
    files = pick_files()
    result = {"files": {k: v.name for k, v in files.items()}, "previews": {}}
    for key, path in files.items():
        if path.suffix.lower() == ".csv":
            result["previews"][key] = preview_csv(path)
        else:
            result["previews"][key] = preview_xlsx(path)
    output = Path("source_preview.json")
    output.write_text(json.dumps(result, ensure_ascii=True, indent=2), encoding="ascii")
    print(str(output))


if __name__ == "__main__":
    main()
