import json
import re
import sys
from pathlib import Path


def main():
    data = Path(sys.argv[1]).read_text(encoding="utf-8")
    pattern = re.compile(
        r'\\"parts\\",\[(\d+)\],\\"((?:\\\\.|[^"\\])*)\\",\\"role\\",\\"(assistant|user)\\"'
    )
    selected = []
    for match in pattern.finditer(data):
        try:
            text = json.loads('"' + match.group(2) + '"')
        except json.JSONDecodeError:
            continue
        if len(text) < 2:
            continue
        selected.append(f"[{match.group(3)}] {text}")
    if len(selected) < 5:
        for match in re.finditer(r'\\"((?:\\\\.|[^"\\])*)\\"', data):
            try:
                text = json.loads('"' + match.group(1) + '"')
            except json.JSONDecodeError:
                continue
            if len(text) >= 30 and re.search(r"[\u4e00-\u9fff]", text):
                selected.append(f"[message] {text}")
    Path(sys.argv[2]).write_text("\n\n---\n\n".join(selected), encoding="utf-8")


if __name__ == "__main__":
    main()
