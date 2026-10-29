"""Verify a full run or model-free result snapshot without running estimators."""

import argparse
import json
from hashlib import sha256
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("directory", type=Path)
args = parser.parse_args()
root = args.directory.resolve()
manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
if manifest.get("status") != "complete":
    raise SystemExit("Result manifest is incomplete.")
for relative, expected in manifest["file_sha256"].items():
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise SystemExit("Manifest path escapes result directory.")
    if sha256(path.read_bytes()).hexdigest() != expected:
        raise SystemExit(f"Checksum mismatch: {relative}")
print(f"Verified {len(manifest['file_sha256'])} result files.")
