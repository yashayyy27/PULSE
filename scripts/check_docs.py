"""Check repository-local Markdown links; external destinations are not contacted."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def check():
    count = 0
    errors = []
    files = [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md"))]
    for file in files:
        text = file.read_text()
        for link in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
            if link.startswith(("http:", "https:", "#", "mailto:")):
                continue
            target = link.split("#")[0].strip("<>")
            if target and not (file.parent / target).exists():
                errors.append(f"{file.relative_to(ROOT)} -> {target}")
            count += 1
        if text.count("```") % 2:
            errors.append(f"{file.relative_to(ROOT)}: unclosed fence")
    if errors:
        raise ValueError("\n".join(errors))
    print(f"{count} local links across {len(files)} Markdown files: PASS")
    return {"links": count, "markdown_files": len(files), "failures": 0}


if __name__ == "__main__":
    try:
        check()
    except ValueError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
