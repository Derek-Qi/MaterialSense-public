"""Numeric external-data screening without model access or independence approval."""

import csv
import json
from collections import defaultdict
from hashlib import sha256
from pathlib import Path

import numpy as np

from .data import INPUTS, MATERIALS, TARGET, read_csv_inputs, recipe_ids


def _canonical_snapshot(path):
    before = sha256(path.read_bytes()).hexdigest()
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            headers = next(
                (row for row in csv.reader(handle, strict=True)
                 if row and not (len(row) == 1 and not row[0].strip())),
                [],
            )
    except csv.Error as error:
        raise ValueError(f"Malformed CSV header: {error}") from error
    extra = set(headers) - set(INPUTS + [TARGET])
    if extra:
        raise ValueError(
            f"Unexpected canonical CSV columns: {sorted(extra)}. "
            "Map materials explicitly and keep provenance in a separate source register."
        )
    frame = read_csv_inputs(path)
    if sha256(path.read_bytes()).hexdigest() != before:
        raise ValueError("Input file changed during screening; use a stable data snapshot.")
    return frame, before


def _keys(frame, columns):
    return [tuple(row) for row in frame[columns].to_numpy()]


def _summary(frame, path, digest):
    input_keys = _keys(frame, INPUTS)
    labels = defaultdict(set)
    for key, value in zip(input_keys, frame[TARGET], strict=True):
        labels[key].add(value)
    return {
        "filename": path.name,
        "sha256": digest,
        "rows": len(frame),
        "recipes": len(set(recipe_ids(frame))),
        "duplicate_full_rows": len(frame) - len(set(_keys(frame, INPUTS + [TARGET]))),
        "duplicate_input_rows": len(frame) - len(set(input_keys)),
        "conflicting_input_groups": sum(len(values) > 1 for values in labels.values()),
    }


def _overlap(candidate_keys, reference_keys, candidate_recipes):
    reference = set(reference_keys)
    matches = [i for i, key in enumerate(candidate_keys) if key in reference]
    return {
        "rows": len(matches),
        "recipes": len({candidate_recipes[i] for i in matches}),
    }


def audit_data(candidate_path, reference_path, output_path, tolerance=0.1):
    """Screen canonical CSVs; counts include all matching candidate occurrences.

    Source identity, license, units and target semantics require separate review.
    A numeric match is an exclusion warning; nonoverlap never proves independence.
    """
    candidate_path, reference_path, output_path = map(
        Path, [candidate_path, reference_path, output_path]
    )
    if output_path.exists():
        raise FileExistsError(f"Output exists: {output_path}. Use a new filename.")
    try:
        tolerance = float(tolerance)
    except (ValueError, TypeError) as error:
        raise ValueError("Recipe tolerance must be finite and nonnegative.") from error
    if not np.isfinite(tolerance) or tolerance < 0:
        raise ValueError("Recipe tolerance must be finite and nonnegative.")
    candidate, candidate_hash = _canonical_snapshot(candidate_path)
    reference, reference_hash = _canonical_snapshot(reference_path)
    candidate_recipes = recipe_ids(candidate)
    overlap = {
        name: _overlap(_keys(candidate, columns), _keys(reference, columns), candidate_recipes)
        for name, columns in [
            ("exact_recipe", MATERIALS), ("exact_inputs", INPUTS),
            ("exact_rows", INPUTS + [TARGET]),
        ]
    }
    # One reference-by-feature array at a time, never the full three-dimensional tensor.
    reference_materials = np.unique(reference[MATERIALS].to_numpy(), axis=0)
    unique_materials, inverse = np.unique(
        candidate[MATERIALS].to_numpy(), axis=0, return_inverse=True
    )
    near = np.array([
        np.any(np.all(np.abs(reference_materials - recipe) <= tolerance, axis=1))
        for recipe in unique_materials
    ])
    overlap["near_recipe"] = {"rows": int(near[inverse].sum()), "recipes": int(near.sum())}
    result = {
        "schema_version": 1,
        "status": "numeric_screening_only",
        "external_validation": "not_performed",
        "source_independence": "not_assessed",
        "model_operations": {"fits": 0, "predictions": 0},
        "candidate": _summary(candidate, candidate_path, candidate_hash),
        "reference": _summary(reference, reference_path, reference_hash),
        "overlap": overlap,
        "near_recipe_definition": {
            "columns": MATERIALS,
            "absolute_tolerance_kg_m3_per_component": tolerance,
            "age_and_strength_used": False,
        },
        "interpretation": (
            "Numeric nonoverlap does not prove source independence. Verify original sources, "
            "licensing, units, unmodelled ingredients, zero/missing values, specimen geometry "
            "and target statistics separately. No model has been loaded or evaluated."
        ),
    }
    encoded = json.dumps(result, indent=2, allow_nan=False) + "\n"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("x", encoding="utf-8") as handle:
        handle.write(encoded)
    return result
