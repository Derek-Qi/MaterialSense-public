"""Build a model-free, checksum-verifiable result snapshot for source control."""

import argparse
import json
import shutil
from hashlib import sha256
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--run", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
source = args.run.resolve()
destination = args.output.resolve()
if destination.is_relative_to(source):
    raise SystemExit("Snapshot output must be outside the full run directory.")
manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
if manifest["status"] != "complete":
    raise SystemExit("Run is not complete.")
for name, expected in manifest["file_sha256"].items():
    path = (source / name).resolve()
    if not path.is_relative_to(source) or sha256(path.read_bytes()).hexdigest() != expected:
        raise SystemExit(f"Bad input artifact: {name}")
shutil.copytree(source, destination, ignore=shutil.ignore_patterns("*.joblib", "manifest.json"))
(destination / "README.md").write_text(
    "# Frozen model-free study evidence\n\n"
    "This snapshot includes all numerical predictions, configurations, splits and diagnostics.\n"
    "Fitted joblib models are omitted for source control. The full local run retains those models.\n"
    "Recompute with the README study command; verify with scripts/verify_results.py.\n"
    "Ten overlapping resplits are descriptive, not independent replications.\n",
    encoding="utf-8",
)
snapshot = {
    k: manifest[k]
    for k in [
        "status",
        "seeds",
        "settings",
        "source_code_sha256",
        "data_sha256_float64",
        "packages",
        "python",
        "platform",
    ]
}
snapshot["full_run_manifest_sha256"] = sha256((source / "manifest.json").read_bytes()).hexdigest()
snapshot["file_sha256"] = {
    str(p.relative_to(destination)).replace("\\", "/"): sha256(p.read_bytes()).hexdigest()
    for p in sorted(destination.rglob("*"))
    if p.is_file()
}
(destination / "manifest.json").write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
print(f"Snapshot: {len(snapshot['file_sha256'])} checked files; models excluded.")
