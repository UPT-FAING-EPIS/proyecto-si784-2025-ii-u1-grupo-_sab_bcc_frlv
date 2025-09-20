#!/usr/bin/env python3
"""Create a cleaned features JSON by stripping whitespace from feature names.

Usage: python scripts/clean_features.py
"""
import json
from pathlib import Path


def main():
    repo = Path(__file__).resolve().parent.parent
    modelos = repo / "modelos"
    feats_files = list(modelos.glob("*features*.json"))
    if not feats_files:
        raise SystemExit("No features json found in modelos/")
    f_in = feats_files[0]
    data = json.loads(f_in.read_text(encoding="utf-8"))
    clean = [s.strip() for s in data]
    f_out = modelos / (f_in.stem + "_clean.json")
    f_out.write_text(json.dumps(clean, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Wrote:", f_out)


if __name__ == "__main__":
    main()
