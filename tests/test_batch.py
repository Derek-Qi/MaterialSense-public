import json

import joblib
import pandas as pd
import pytest


def test_batch_prediction_exports_inputs_and_checks_artifact(concrete_frame, tiny_config, tmp_path):
    from materialsense.batch import predict_csv
    from materialsense.experiment import run_experiment

    run_experiment(concrete_frame, tiny_config, tmp_path / "run")
    source = tmp_path / "inputs.csv"
    concrete_frame.iloc[:3, :8].to_csv(source, index=False)
    output = tmp_path / "predictions.csv"
    predict_csv(tmp_path / "run/model.joblib", source, output)
    values = pd.read_csv(output)
    assert len(values) == 3 and "cement" in values and "cqr_lower_mpa" in values
    assert "heuristic_warnings" in values and values.row_id.tolist() == [0, 1, 2]
    manifest = json.loads(output.with_suffix(".manifest.json").read_text())
    assert manifest["rows"] == 3 and len(manifest["input_sha256"]) == 64
    with pytest.raises(FileExistsError):
        predict_csv(tmp_path / "run/model.joblib", source, output)
    source.write_text("cement,water\n1,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Missing required"):
        predict_csv(tmp_path / "run/model.joblib", source, tmp_path / "bad.csv")
    joblib.dump({}, tmp_path / "broken.joblib")
    with pytest.raises((ValueError, KeyError)):
        predict_csv(tmp_path / "broken.joblib", source, tmp_path / "broken.csv")
