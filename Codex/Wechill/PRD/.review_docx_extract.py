import sys
from pathlib import Path

from docx import Document


def main():
    source = Path(sys.argv[1])
    target = Path(sys.argv[2])
    doc = Document(source)
    lines = []
    lines.append(f"PARAGRAPHS: {len(doc.paragraphs)}")
    lines.append(f"TABLES: {len(doc.tables)}")
    lines.append("")
    for index, paragraph in enumerate(doc.paragraphs, 1):
        text = paragraph.text.strip()
        if text:
            lines.append(f"P{index} [{paragraph.style.name}] {text}")
    for table_index, table in enumerate(doc.tables, 1):
        lines.append("")
        lines.append(f"TABLE {table_index} ROWS {len(table.rows)} COLS {len(table.columns)}")
        for row_index, row in enumerate(table.rows, 1):
            cells = [cell.text.replace("\n", " / ").strip() for cell in row.cells]
            lines.append(f"T{table_index}R{row_index}: " + " | ".join(cells))
    target.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
