#!/usr/bin/env python3
import sys
from pathlib import Path
def strip_all_blank_lines(content: str) -> str:
    lines = [line for line in content.split('\n') if line.strip() != '']
    return '\n'.join(lines) + '\n'
def process_file(path: Path) -> bool:
    original = path.read_text(encoding='utf-8')
    cleaned = strip_all_blank_lines(original)
    if original != cleaned:
        path.write_text(cleaned, encoding='utf-8')
        removed = original.count('\n') - cleaned.count('\n')
        print(f"{path}: -{removed} lines")
        return True
    return False
def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("flexus_client_kit")
    if not target.exists():
        print(f"Path not found: {target}")
        sys.exit(1)
    files = list(target.rglob("*.py")) if target.is_dir() else [target]
    changed = sum(1 for f in files if process_file(f))
    print(f"Done: {changed}/{len(files)} files modified")
if __name__ == "__main__":
    main()
