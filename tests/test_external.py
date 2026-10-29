import importlib
import json

import pandas as pd
import pytest

from materialsense.data import INPUTS, TARGET


def audit(*args, **kwargs):
    return importlib.import_module("materialsense.external").audit_data(*args, **kwargs)


@pytest.fixture
def data_files(tmp_path):
    reference = pd.DataFrame(
        [[300, 0, 0, 180, 0, 1000, 700, 28, 30],
         [350, 20, 0, 170, 5, 950, 750, 90, 50]],
        columns=INPUTS + [TARGET], dtype=float,
    )
    ref = tmp_path / "reference.csv"
    candidate = tmp_path / "candidate.csv"
    reference.to_csv(ref, index=False)
    reference.iloc[[0]].to_csv(candidate, index=False)
    return reference, candidate, ref, tmp_path / "audit.json"


def test_recipe_overlap_survives_changed_age_label_and_duplicates(data_files):
    reference, candidate, ref, out = data_files
    rows = [
        [300, 0, 0, 180, 0, 1000, 700, 7, 20],
        [300, 0, 0, 180, 0, 1000, 700, 28, 40],
        [300, 0, 0, 180, 0, 1000, 700, 28, 40],
        [300.0625, 0, 0, 180, 0, 1000, 700, 28, 40],
        [450, 0, 0, 180, 0, 1000, 700, 28, 40],
    ]
    pd.DataFrame(rows, columns=reference.columns).to_csv(candidate, index=False)
    original = ref.read_bytes(), candidate.read_bytes()
    result = audit(candidate, ref, out, tolerance=.125)
    assert result["status"] == "numeric_screening_only"
    assert result["external_validation"] == "not_performed"
    assert result["source_independence"] == "not_assessed"
    assert result["model_operations"] == {"fits": 0, "predictions": 0}
    assert result["candidate"]["rows"] == 5
    assert result["candidate"]["recipes"] == 3
    assert result["candidate"]["duplicate_full_rows"] == 1
    assert result["overlap"]["exact_recipe"] == {"rows": 3, "recipes": 1}
    assert result["overlap"]["exact_inputs"]["rows"] == 2
    assert result["overlap"]["exact_rows"]["rows"] == 0
    assert result["overlap"]["near_recipe"] == {"rows": 4, "recipes": 2}
    assert json.loads(out.read_text()) == result
    assert (ref.read_bytes(), candidate.read_bytes()) == original
    assert len(result["candidate"]["sha256"]) == 64


def test_signed_zero_reordered_columns_and_conflicting_targets(data_files):
    frame, candidate, ref, out = data_files
    row = frame.iloc[0].tolist()
    row[4] = -0.0
    other = row.copy()
    other[-1] = 40
    pd.DataFrame([row, other], columns=frame.columns).loc[:, list(reversed(frame.columns))].to_csv(
        candidate, index=False
    )
    result = audit(candidate, ref, out, tolerance=0)
    assert result["candidate"]["recipes"] == 1
    assert result["candidate"]["duplicate_input_rows"] == 1
    assert result["candidate"]["conflicting_input_groups"] == 1
    assert result["overlap"]["exact_rows"]["rows"] == 1
    assert result["overlap"]["near_recipe"] == result["overlap"]["exact_recipe"]


def test_zero_overlap_never_approves_source_independence(data_files):
    frame, candidate, ref, out = data_files
    frame.loc[:, "cement"] += 100
    frame.to_csv(candidate, index=False)
    result = audit(candidate, ref, out)
    assert all(x == {"rows": 0, "recipes": 0} for x in result["overlap"].values())
    assert result["source_independence"] == "not_assessed"
    assert "does not prove" in result["interpretation"]


@pytest.mark.parametrize("column", ["silica_fume", "source_id"])
def test_extra_columns_are_not_silently_dropped(data_files, column):
    frame, candidate, ref, out = data_files
    frame[column] = 1
    frame.to_csv(candidate, index=False)
    with pytest.raises(ValueError, match="Unexpected.*column"):
        audit(candidate, ref, out)
    assert not out.exists()


@pytest.mark.parametrize("case", ["missing", "nonfinite", "negative", "duplicate_header"])
def test_invalid_canonical_data_produces_no_report(data_files, case):
    frame, candidate, ref, out = data_files
    if case == "missing":
        frame = frame.drop(columns="superplasticizer")
    elif case == "nonfinite":
        frame.loc[0, "age"] = float("inf")
    elif case == "negative":
        frame.loc[0, "strength"] = -1
    else:
        candidate.write_text("cement,cement\n300,300\n")
    if case != "duplicate_header":
        frame.to_csv(candidate, index=False)
    with pytest.raises(ValueError):
        audit(candidate, ref, out)
    assert not out.exists()


@pytest.mark.parametrize("tolerance", [-1, float("nan"), float("inf")])
def test_invalid_tolerance_is_rejected(data_files, tolerance):
    _, candidate, ref, out = data_files
    with pytest.raises(ValueError, match="tolerance"):
        audit(candidate, ref, out, tolerance)
    assert not out.exists()


def test_existing_output_and_input_paths_are_never_overwritten(data_files):
    _, candidate, ref, out = data_files
    out.write_text("keep this")
    for path in [out, candidate, ref]:
        before = path.read_bytes()
        with pytest.raises(FileExistsError):
            audit(candidate, ref, path)
        assert path.read_bytes() == before


def test_malformed_quoted_header_is_a_validation_error(data_files):
    _, candidate, ref, out = data_files
    candidate.write_text('"cement,slag\n300,0\n')
    with pytest.raises(ValueError, match="Malformed CSV"):
        audit(candidate, ref, out)
    assert not out.exists()


def test_cli_audits_without_experiments_or_model_loading(data_files, monkeypatch, capsys):
    import joblib

    from materialsense import cli

    _, candidate, ref, out = data_files

    def forbidden(*args, **kwargs):
        raise AssertionError("Numeric audit must not load a model or run an experiment")

    monkeypatch.setattr(joblib, "load", forbidden)
    monkeypatch.setattr(cli, "run_experiment", forbidden)
    monkeypatch.setattr(cli, "run_study", forbidden)
    monkeypatch.setattr("sys.argv", ["materialsense", "audit-data", "--candidate", str(candidate),
                                    "--reference", str(ref), "--output", str(out)])
    assert cli.main() == 0
    assert "numeric_screening_only" in capsys.readouterr().out
    assert json.loads(out.read_text())["overlap"]["exact_rows"]["rows"] == 1
