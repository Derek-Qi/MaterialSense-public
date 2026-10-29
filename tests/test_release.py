"""Release regressions use no network and never edit the working repository."""

import shutil
import subprocess
import tomllib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def test_evidence_bytes_survive_clean_git_checkout(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    shutil.copy2(ROOT / ".gitattributes", source / ".gitattributes")
    evidence = {
        "data/raw/concrete.csv": b"cement,water\r\n300,180\r\n",
        "reports/benchmark-10/metrics.csv": b"seed,rmse\r\n42,5.2\r\n",
        "reports/reference/summary.md": b"# Frozen reference\r\n",
    }
    for name, content in evidence.items():
        path = source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    git("init", cwd=source)
    git("-c", "core.autocrlf=false", "add", ".", cwd=source)
    git(
        "-c",
        "user.name=Release regression",
        "-c",
        "user.email=release@example.invalid",
        "commit",
        "-m",
        "synthetic fixture",
        cwd=source,
    )
    clone = tmp_path / "clone"
    git("-c", "core.autocrlf=false", "clone", "--no-local", str(source), str(clone), cwd=tmp_path)
    for name, content in evidence.items():
        assert (clone / name).read_bytes() == content


def test_distribution_citation_and_runtime_version_agree():
    import materialsense

    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    citation = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    assert materialsense.__version__ == project["version"] == citation["version"]
    assert project["version"] == "0.2.0rc1"


def test_readme_does_not_link_to_ignored_model_outputs():
    # The Git source candidate excludes fitted models; figures must use tracked evidence.
    body = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "](artifacts/" not in body
