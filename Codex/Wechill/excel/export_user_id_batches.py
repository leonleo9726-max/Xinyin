import json
from pathlib import Path

import pandas as pd


def u(text):
    return text.encode("ascii").decode("unicode_escape")


ROOT = Path.cwd()


def find_file(suffix, marker):
    matches = [p for p in ROOT.iterdir() if p.suffix.lower() == suffix and marker in p.name]
    if len(matches) != 1:
        raise RuntimeError("file not found")
    return matches[0]


def ids_from_sources(csv_marker, xlsx_marker):
    csv_df = pd.read_csv(find_file(".csv", csv_marker), dtype=str, keep_default_na=False)
    xlsx_df = pd.read_excel(find_file(".xlsx", xlsx_marker), dtype=str, keep_default_na=False)
    host_csv = csv_df[csv_df["Role"].astype(str).str.strip() == u("\\u4e3b\\u64ad")]
    ids = set(host_csv["UserId"].astype(str).str.strip())
    ids.update(xlsx_df[u("\\u4e3b\\u64adid")].astype(str).str.strip())
    return sorted([x for x in ids if x])


def write_batches(label, ids, batch_size=700):
    batches = []
    for i in range(0, len(ids), batch_size):
        batch = ids[i : i + batch_size]
        batches.append(batch)
        Path("user_ids_%s_batch_%02d.txt" % (label, len(batches))).write_text(",".join(batch), encoding="ascii")
    return len(batches)


def main():
    meta = {}
    for label, csv_marker, xlsx_marker in [
        ("1_15", "1-15", "6.1-6.15"),
        ("16_30", "16-30", "6.16-6.30"),
    ]:
        ids = ids_from_sources(csv_marker, xlsx_marker)
        meta[label] = {"count": len(ids), "batches": write_batches(label, ids)}
    Path("user_id_batches_meta.json").write_text(json.dumps(meta, ensure_ascii=True, indent=2), encoding="ascii")
    print("user_id_batches_meta.json")


if __name__ == "__main__":
    main()
