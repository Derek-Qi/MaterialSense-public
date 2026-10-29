"""Synthetic source archives exercise release failures without downloading real data."""

import hashlib
import io
import json
import runpy
import tarfile
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def distribution(tmp_path):
    project = tmp_path / "project"
    files = {
        "pyproject.toml": '[project]\nname="materialsense"\nversion="0.2.0rc1"\n',
        "src/materialsense/__init__.py": '__version__ = "0.2.0rc1"\n',
        "README.md": "Synthetic archive fixture\n",
        "LICENSE": "Synthetic test fixture\n",
        "CITATION.cff": "cff-version: 1.2.0\n",
        "requirements.txt": "",
        "requirements-ci.txt": "",
        "app.py": "# synthetic app\n",
        "explorer_app.py": "# synthetic explorer app\n",
        "explorer.py": "# synthetic explorer data\n",
        "explorer_charts.py": "# synthetic explorer charts\n",
        "dashboard_text.py": "# synthetic bilingual text\n",
        ".streamlit/config.toml": "[server]\nheadless=true\n",
        "configs/experiment.yaml": "seed: 42\n",
        "configs/study.yaml": "seeds: [42]\n",
        "tests/conftest.py": "# synthetic fixture\n",
        ".gitattributes": "reports/benchmark-10/** -text\n",
        ".github/workflows/ci.yml": "name: Synthetic\n",
        "reports/benchmark-10/results.csv": "seed,synthetic\n42,1\n",
    }
    data = files["reports/benchmark-10/results.csv"].encode()
    files["reports/benchmark-10/manifest.json"] = json.dumps(
        {"status": "complete", "file_sha256": {"results.csv": hashlib.sha256(data).hexdigest()}}
    )
    for name, content in files.items():
        path = project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    dist = tmp_path / "dist"
    dist.mkdir()
    with zipfile.ZipFile(dist / "materialsense-0.2.0rc1-py3-none-any.whl", "w") as wheel:
        wheel.writestr("materialsense/__init__.py", files["src/materialsense/__init__.py"])
        wheel.writestr(
            "materialsense-0.2.0rc1.dist-info/METADATA",
            "Metadata-Version: 2.4\nName: materialsense\nVersion: 0.2.0rc1\n",
        )
    return project, dist, files


def build_tarball(distribution, omit=None, corrupt=False):
    project, dist, files = distribution
    with tarfile.open(dist / "materialsense-0.2.0rc1.tar.gz", "w:gz") as archive:
        for name, content in files.items():
            if name == omit:
                continue
            if corrupt and name.endswith("results.csv"):
                content = "seed,synthetic\n42,999\n"
            data = content.encode()
            member = tarfile.TarInfo("materialsense-0.2.0rc1/" + name)
            member.size = len(data)
            archive.addfile(member, io.BytesIO(data))
    return project, dist


def verifier():
    path = ROOT / "scripts/verify_distribution.py"
    assert path.exists(), "CI needs a real archive verifier for omitted fixtures and evidence drift"
    return runpy.run_path(str(path))["verify_distributions"]


def test_complete_synthetic_distribution_verifies(distribution):
    project, dist = build_tarball(distribution)
    result = verifier()(dist, project)
    assert result["frozen_files_verified"] == 1


def test_sdist_missing_test_fixtures_is_rejected(distribution):
    for missing in [
        "tests/conftest.py",
        "explorer_app.py",
        "explorer.py",
        "explorer_charts.py",
        "dashboard_text.py",
        ".streamlit/config.toml",
    ]:
        project, dist = build_tarball(distribution, omit=missing)
        with pytest.raises(ValueError, match=missing):
            verifier()(dist, project)


def test_sdist_changed_evidence_is_rejected(distribution):
    project, dist = build_tarball(distribution, corrupt=True)
    with pytest.raises(ValueError, match="Checksum mismatch"):
        verifier()(dist, project)
