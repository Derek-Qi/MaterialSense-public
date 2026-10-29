"""CSV prediction from an explicitly supplied trusted local joblib artifact."""

import json
from hashlib import sha256
from pathlib import Path

import joblib

from .artifacts import validate_bundle
from .data import read_csv_inputs
from .inference import predict_bundle
from .safety import physical_warnings


def predict_csv(model_path, input_path, output_path):
    model_path, input_path, output_path = map(Path, [model_path, input_path, output_path])
    manifest_path = output_path.with_suffix(".manifest.json")
    if output_path.exists() or manifest_path.exists():
        raise FileExistsError(f"Output exists: {output_path}. Use a new filename.")
    bundle = validate_bundle(joblib.load(model_path))
    frame = read_csv_inputs(input_path, require_target=False)
    result = frame.join(predict_bundle(bundle, frame))
    result.insert(0, "row_id", range(len(result)))
    result["heuristic_warnings"] = [
        " | ".join(physical_warnings(frame.iloc[[i]], **bundle["config"]["heuristics"]))
        for i in range(len(frame))
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    manifest = {
        "rows": len(result),
        "input_sha256": sha256(input_path.read_bytes()).hexdigest(),
        "model_sha256": sha256(model_path.read_bytes()).hexdigest(),
        "output_sha256": sha256(output_path.read_bytes()).hexdigest(),
        "training_metadata": bundle["metadata"],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, allow_nan=False), encoding="utf-8")
    return result
