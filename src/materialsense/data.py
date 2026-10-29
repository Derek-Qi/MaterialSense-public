"""Validated UCI ingestion and exact, age-independent recipe identity."""

import csv
import json
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen
from zipfile import ZipFile

import numpy as np
import pandas as pd

MATERIALS = [
    "cement",
    "slag",
    "fly_ash",
    "water",
    "superplasticizer",
    "coarse_aggregate",
    "fine_aggregate",
]
INPUTS = MATERIALS + ["age"]
TARGET = "strength"
UCI_URL = "https://archive.ics.uci.edu/static/public/165/concrete+compressive+strength.zip"
UCI_ZIP_SHA256 = "dad85d14de8aee4e07479daa774e6b569a313715b71a3b92c95a07cf91c2c9a7"
UCI_HEADERS = [
    "cement (component 1)(kg in a m^3 mixture)",
    "blast furnace slag (component 2)(kg in a m^3 mixture)",
    "fly ash (component 3)(kg in a m^3 mixture)",
    "water (component 4)(kg in a m^3 mixture)",
    "superplasticizer (component 5)(kg in a m^3 mixture)",
    "coarse aggregate (component 6)(kg in a m^3 mixture)",
    "fine aggregate (component 7)(kg in a m^3 mixture)",
    "age (day)",
    "concrete compressive strength(mpa, megapascals)",
]


def validate_frame(frame: pd.DataFrame, require_target: bool = True) -> pd.DataFrame:
    columns = INPUTS + ([TARGET] if require_target else [])
    missing = set(columns) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if frame.empty or not frame.columns.is_unique:
        raise ValueError("Data must be nonempty with unique column names.")
    try:
        # NumPy/Python's correctly rounded conversion preserves adjacent representable
        # values in numeric strings; pd.to_numeric can move or merge these values.
        clean = frame.loc[:, columns].astype("float64")
    except (ValueError, TypeError) as error:
        raise ValueError("All inputs and targets must be numeric.") from error
    if not np.isfinite(clean.to_numpy()).all():
        raise ValueError("Missing or infinite values are not permitted.")
    if (clean[MATERIALS] < 0).any().any():
        raise ValueError("Ingredient quantities cannot be negative.")
    if (clean[["cement", "slag", "fly_ash"]].sum(axis=1) <= 0).any():
        raise ValueError("Total binder must be positive.")
    if (clean[["water", "age"]] <= 0).any().any():
        raise ValueError("Water and age must be positive.")
    if require_target and (clean[TARGET] <= 0).any():
        raise ValueError("Measured strength must be positive.")
    return clean


def recipe_ids(frame: pd.DataFrame) -> np.ndarray:
    """Exact parsed float64 keys; no tolerance merging, rounding, age or labels."""
    values = validate_frame(frame, require_target=False)[MATERIALS].to_numpy(dtype="<f8")
    values[values == 0] = 0.0  # Normalize -0.0 without changing any nonzero quantity.
    return np.array([sha256(row.tobytes()).hexdigest() for row in values])


def read_csv_inputs(path, require_target=True):
    headers = None
    try:
        with Path(path).open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.reader(handle, strict=True):
                if not row or (len(row) == 1 and not row[0].strip()):
                    continue
                if headers is None:
                    headers = row
                    if len(headers) != len(set(headers)):
                        raise ValueError("Duplicate CSV column names are not permitted.")
                elif len(row) != len(headers):
                    raise ValueError("CSV record has a different field count from its header.")
    except csv.Error as error:
        raise ValueError(f"Malformed CSV record: {error}") from error
    return validate_frame(
        pd.read_csv(path, float_precision="round_trip", index_col=False), require_target
    ).reset_index(drop=True)


def load_data(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Data missing: {path}. Run 'materialsense download' first.")
    if path.suffix.lower() == ".csv":
        return read_csv_inputs(path)
    if path.suffix.lower() == ".xls":
        return read_uci_excel(path)
    raise ValueError("Use a canonical CSV or the original UCI .xls file.")


def read_uci_excel(source) -> pd.DataFrame:
    frame = pd.read_excel(source, engine="xlrd")
    headers = [" ".join(str(x).lower().split()) for x in frame.columns]
    if headers != UCI_HEADERS:
        raise ValueError("Unexpected UCI workbook schema; refusing positional column guessing.")
    frame.columns = INPUTS + [TARGET]
    return validate_frame(frame).reset_index(drop=True)


def prepare_data(source: Path, destination: Path) -> Path:
    """Convert a local official archive or workbook, with an auditable source manifest."""
    raw = source.read_bytes()
    if source.suffix.lower() == ".zip":
        if sha256(raw).hexdigest() != UCI_ZIP_SHA256:
            raise ValueError(
                "UCI archive checksum changed. Inspect it before updating the pinned hash."
            )
        with ZipFile(BytesIO(raw)) as archive:
            workbook = archive.read("Concrete_Data.xls")
    elif source.suffix.lower() == ".xls":
        workbook = raw
    else:
        raise ValueError("Manual source must be UCI's .zip or Concrete_Data.xls.")
    frame = read_uci_excel(BytesIO(workbook))
    if frame.shape != (1030, 9):
        raise ValueError(f"Official dataset expected 1030 x 9, received {frame.shape}.")
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "Concrete_Data.xls").write_bytes(workbook)
    csv = destination / "concrete.csv"
    frame.to_csv(csv, index=False)
    manifest = {
        "dataset": "UCI Concrete Compressive Strength (165)",
        "author": "I-Cheng Yeh",
        "doi": "10.24432/C5PK67",
        "license": "CC BY 4.0",
        "url": UCI_URL,
        "source_filename": source.name,
        "source_sha256": sha256(raw).hexdigest(),
        "workbook_sha256": sha256(workbook).hexdigest(),
        "csv_sha256": sha256(csv.read_bytes()).hexdigest(),
        "rows": len(frame),
        "conversion": "Original float64 values, canonical names, no deduplication or rounding",
    }
    (destination / "source.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return csv


def download_data(destination: Path) -> Path:
    csv = destination / "concrete.csv"
    if csv.exists():
        load_data(csv)
        manifest_path = destination / "source.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if sha256(csv.read_bytes()).hexdigest() != manifest["csv_sha256"]:
                raise ValueError("Local CSV differs from source.json; inspect before replacing it.")
        return csv
    try:
        with urlopen(UCI_URL, timeout=60) as response:
            raw = response.read(10_000_001)
    except (URLError, TimeoutError) as error:
        raise RuntimeError(
            "Download failed. Save UCI's ZIP manually, then run "
            "'materialsense download --source path/to/file.zip'."
        ) from error
    if len(raw) > 10_000_000:
        raise ValueError("Unexpectedly large archive; download stopped.")
    if sha256(raw).hexdigest() != UCI_ZIP_SHA256:
        raise ValueError("Downloaded archive does not match the pinned official SHA-256.")
    destination.mkdir(parents=True, exist_ok=True)
    source = destination / "concrete-source.zip"
    source.write_bytes(raw)
    return prepare_data(source, destination)
