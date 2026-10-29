"""Inspect built archives without importing the checkout or fitting any estimator."""

import argparse
import json
import tarfile
import tomllib
import zipfile
from email.parser import BytesParser
from hashlib import sha256
from pathlib import Path, PurePosixPath

REQUIRED = (
    "pyproject.toml",
    "README.md",
    "LICENSE",
    "CITATION.cff",
    "requirements.txt",
    "requirements-ci.txt",
    "app.py",
    "explorer_app.py",
    "explorer.py",
    "explorer_charts.py",
    "dashboard_text.py",
    ".streamlit/config.toml",
    "configs/experiment.yaml",
    "configs/study.yaml",
    "tests/conftest.py",
    ".gitattributes",
    ".github/workflows/ci.yml",
    "reports/benchmark-10/manifest.json",
)


def verify_distributions(directory, project_root):
    directory, project_root = Path(directory), Path(project_root)
    project = tomllib.loads((project_root / "pyproject.toml").read_text(encoding="utf-8"))
    version = project["project"]["version"]
    wheels, sources = list(directory.glob("*.whl")), list(directory.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sources) != 1:
        raise ValueError("Build exactly one wheel and source tarball into a clean destination.")
    source_files = sorted((project_root / "src/materialsense").glob("*.py"))
    with zipfile.ZipFile(wheels[0]) as wheel:
        if wheel.testzip() is not None:
            raise ValueError("Wheel CRC check failed.")
        metadata_files = [n for n in wheel.namelist() if n.endswith(".dist-info/METADATA")]
        if len(metadata_files) != 1:
            raise ValueError("Wheel needs one METADATA record.")
        metadata = BytesParser().parsebytes(wheel.read(metadata_files[0]))
        if metadata["Name"] != "materialsense" or metadata["Version"] != version:
            raise ValueError("Wheel distribution name/version mismatch.")
        for path in source_files:
            if wheel.read("materialsense/" + path.name) != path.read_bytes():
                raise ValueError(f"Wheel source mismatch: {path.name}")
    prefix = f"materialsense-{version}/"
    with tarfile.open(sources[0]) as archive:
        members = {m.name: m for m in archive.getmembers()}
        for name, member in members.items():
            relative = PurePosixPath(name)
            if (
                relative.is_absolute()
                or ".." in relative.parts
                or not name.startswith(prefix.rstrip("/"))
                or not (member.isfile() or member.isdir())
                or name.endswith((".joblib", ".pyc"))
                or any(part in {".git", ".venv", "__pycache__"} for part in relative.parts)
                or "/artifacts/" in name
                or "/reports/runs/" in name
            ):
                raise ValueError(f"Unexpected source archive member: {name}")

        def content(name):
            member = members.get(prefix + name)
            if member is None or not member.isfile():
                raise ValueError(f"Source distribution missing required file: {name}")
            return archive.extractfile(member).read()

        for name in REQUIRED:
            if content(name) != (project_root / name).read_bytes():
                raise ValueError(f"Source distribution differs from checkout: {name}")
        manifest = json.loads(content("reports/benchmark-10/manifest.json"))
        if manifest.get("status") != "complete":
            raise ValueError("Frozen evidence manifest is incomplete.")
        for name, expected in manifest["file_sha256"].items():
            if sha256(content("reports/benchmark-10/" + name)).hexdigest() != expected:
                raise ValueError(f"Checksum mismatch: {name}")
    return {
        "version": version,
        "wheel": wheels[0].name,
        "source_distribution": sources[0].name,
        "package_modules_verified": len(source_files),
        "required_source_resources_verified": len(REQUIRED),
        "frozen_files_verified": len(manifest["file_sha256"]),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify_distributions(args.directory, Path(__file__).resolve().parents[1]), indent=2))
