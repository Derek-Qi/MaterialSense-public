"""The partitions and CV folds are functions of recipe IDs, never labels."""

import numpy as np
from sklearn.model_selection import GroupKFold, GroupShuffleSplit, train_test_split


def validate_fractions(fractions):
    values = np.asarray(fractions, dtype=float)
    if values.shape != (3,) or not np.isfinite(values).all():
        raise ValueError("Specify three finite train/calibration/test fractions.")
    if (values <= 0).any() or not np.isclose(values.sum(), 1, atol=1e-10, rtol=0):
        raise ValueError("Split fractions must be positive and sum to one.")
    return values


def grouped_split(groups, seed: int, fractions) -> dict[str, np.ndarray]:
    fractions = validate_fractions(fractions)
    groups = np.asarray(groups)
    if len(np.unique(groups)) < 3:
        raise ValueError("At least three distinct recipes are required.")
    rows = np.arange(len(groups))
    train_cal, test = next(
        GroupShuffleSplit(n_splits=1, test_size=fractions[2], random_state=seed).split(
            rows, groups=groups
        )
    )
    train, calibration = next(
        GroupShuffleSplit(
            n_splits=1, test_size=fractions[1] / fractions[:2].sum(), random_state=seed + 1
        ).split(train_cal, groups=groups[train_cal])
    )
    parts = {
        "train": np.sort(train_cal[train]),
        "calibration": np.sort(train_cal[calibration]),
        "test": np.sort(test),
    }
    if any(len(part) == 0 for part in parts.values()):
        raise ValueError("A split is empty; use more recipes or different fractions.")
    return parts


def group_cv(groups, folds: int):
    groups = np.asarray(groups)
    if not isinstance(folds, int) or not 2 <= folds <= len(np.unique(groups)):
        raise ValueError("CV folds must be between two and the number of training recipes.")
    return list(GroupKFold(n_splits=folds).split(np.arange(len(groups)), groups=groups))


def random_split(n_rows: int, seed: int, fractions):
    fractions = validate_fractions(fractions)
    train_cal, test = train_test_split(np.arange(n_rows), test_size=fractions[2], random_state=seed)
    train, calibration = train_test_split(
        train_cal, test_size=fractions[1] / fractions[:2].sum(), random_state=seed + 1
    )
    return {"train": np.sort(train), "calibration": np.sort(calibration), "test": np.sort(test)}


def split_audit(groups, parts):
    sets = {name: set(groups[index]) for name, index in parts.items()}
    overlaps = {
        f"{a}_{b}": len(sets[a] & sets[b]) for i, a in enumerate(sets) for b in list(sets)[i + 1 :]
    }
    return {
        "rows": {k: len(v) for k, v in parts.items()},
        "groups": {k: len(v) for k, v in sets.items()},
        "pairwise_overlap": overlaps,
        "overlap_groups": sum(overlaps.values()),
    }
