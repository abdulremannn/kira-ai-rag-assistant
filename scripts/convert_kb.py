"""
One-time migration: safely converts an old kb.py (KBDocument(...) calls) into
data/kb.json, WITHOUT executing the file. Uses ast parsing only.

Usage:
    python scripts/convert_kb.py path/to/kb.py data/kb.json
"""
import ast
import json
import sys


def convert(src_path: str, dst_path: str):
    with open(src_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    docs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "KBDocument":
            args = [ast.literal_eval(a) for a in node.args]
            if len(args) == 4:
                docs.append(
                    {"id": args[0], "category": args[1], "title": args[2], "content": args[3]}
                )

    if not docs:
        print("No KBDocument(...) calls found — check the source file format.")
        sys.exit(1)

    with open(dst_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)

    print(f"Converted {len(docs)} documents -> {dst_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scripts/convert_kb.py <input kb.py> <output kb.json>")
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2])
