import numpy as np
import pytest


def test_recipe_identity_ignores_age_target_order_and_numeric_format(concrete_frame):
    from materialsense.data import recipe_ids

    frame = concrete_frame.iloc[:3].astype(object).copy()
    frame.loc[1, "cement"] = str(frame.loc[0, "cement"])
    frame.loc[2, "strength"] = 999
    ids = recipe_ids(frame)
    assert len(set(ids)) == 1
    assert recipe_ids(frame.iloc[::-1]).tolist() == ids[::-1].tolist()


def test_close_recipes_are_not_merged_and_signed_zero_is_normalized(concrete_frame):
    from materialsense.data import recipe_ids

    frame = concrete_frame.iloc[:3].copy()
    frame.loc[0, "slag"] = 0.0
    frame.loc[1, "slag"] = -0.0
    frame.loc[2, "slag"] = 1e-10
    ids = recipe_ids(frame)
    assert ids[0] == ids[1]
    assert ids[0] != ids[2]


def test_adjacent_float_strings_preserve_exact_recipe_identity(concrete_frame):
    from materialsense.data import recipe_ids, validate_frame

    frame = concrete_frame.iloc[:3].astype(object).copy()
    frame.loc[:, "cement"] = ["199.99999999999997", "200.0", "200.00000000000006"]
    clean = validate_frame(frame)
    assert clean.cement.tolist() == [199.99999999999997, 200.0, 200.00000000000006]
    assert len(set(recipe_ids(frame))) == 3
    assert recipe_ids(frame).tolist() == recipe_ids(clean).tolist()


def test_csv_round_trip_preserves_binary_recipe_keys(concrete_frame, tmp_path):
    from materialsense.data import load_data, recipe_ids

    frame = concrete_frame.iloc[:3].copy()
    frame.loc[:, "cement"] = [199.99999999999997, 200.0, 200.00000000000006]
    path = tmp_path / "numeric.csv"
    frame.to_csv(path, index=False)
    assert recipe_ids(load_data(path)).tolist() == recipe_ids(frame).tolist()


@pytest.mark.parametrize(
    "column,value",
    [
        ("water", np.nan),
        ("cement", np.inf),
        ("slag", -1),
        ("age", 0),
        ("strength", -3),
        ("water", "bad"),
    ],
)
def test_invalid_values_fail_early(concrete_frame, column, value):
    from materialsense.data import validate_frame

    frame = concrete_frame.astype(object)
    frame.loc[0, column] = value
    with pytest.raises(ValueError):
        validate_frame(frame)


def test_zero_binder_and_missing_column_rejected(concrete_frame):
    from materialsense.data import validate_frame

    frame = concrete_frame.copy()
    frame.loc[0, ["cement", "slag", "fly_ash"]] = 0
    with pytest.raises(ValueError, match="binder"):
        validate_frame(frame)
    with pytest.raises(ValueError, match="Missing"):
        validate_frame(concrete_frame.drop(columns="age"))


def test_group_split_and_cv_never_share_recipe(concrete_frame):
    from materialsense.data import recipe_ids
    from materialsense.splitting import group_cv, grouped_split

    groups = recipe_ids(concrete_frame)
    parts = grouped_split(groups, 42, [0.6, 0.2, 0.2])
    assert sorted(np.concatenate(list(parts.values())).tolist()) == list(range(180))
    sets = [set(groups[p]) for p in parts.values()]
    assert all(not sets[i] & sets[j] for i in range(3) for j in range(i))
    repeated = grouped_split(groups, 42, [0.6, 0.2, 0.2])
    assert all(np.array_equal(parts[k], repeated[k]) for k in parts)
    train_groups = groups[parts["train"]]
    for train, valid in group_cv(train_groups, 5):
        assert not set(train_groups[train]) & set(train_groups[valid])


def test_too_few_groups_and_bad_fractions_fail():
    from materialsense.splitting import group_cv, grouped_split

    with pytest.raises(ValueError):
        grouped_split(np.array(["a", "a"]), 1, [0.6, 0.2, 0.2])
    with pytest.raises(ValueError):
        grouped_split(np.array(list("abcdef")), 1, [0.6, 0.2, 0.3])
    with pytest.raises(ValueError):
        group_cv(np.array(["a", "b"]), 5)


def test_engineered_features_use_only_inputs_and_known_formulas(concrete_frame):
    from materialsense.features import material_features

    frame = concrete_frame.iloc[:1].copy()
    frame.loc[:, ["cement", "slag", "fly_ash", "water", "age"]] = [200, 50, 50, 150, 7]
    result = material_features(frame, True)
    assert result.loc[0, "water_binder"] == 0.5
    assert result.loc[0, "binder"] == 300
    assert result.loc[0, "log_age"] == pytest.approx(np.log(8))
    assert result.loc[0, "total_mass"] == 2154
    assert "strength" not in result.columns
    assert "mix_id" not in result.columns
    assert material_features(frame, False).shape[1] == 8


def test_csv_duplicate_headers_are_rejected_before_pandas_mangling(tmp_path):
    import pytest

    from materialsense.data import INPUTS, load_data

    path = tmp_path / "duplicate.csv"
    path.write_text(
        ",".join(INPUTS + ["strength", "cement"]) + "\n" + ",".join(["1"] * 10) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Duplicate CSV"):
        load_data(path)


@pytest.mark.parametrize("leading", ["\n", "  \n"])
def test_duplicate_csv_headers_after_blank_lines_are_rejected(tmp_path, leading):
    from materialsense.data import INPUTS, load_data

    path = tmp_path / "duplicate.csv"
    path.write_text(
        leading + ",".join(INPUTS + ["strength", "cement"]) + "\n" + ",".join(["1"] * 10) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Duplicate CSV"):
        load_data(path)


@pytest.mark.parametrize("count", [8, 10])
def test_inconsistent_csv_record_width_is_rejected(tmp_path, count):
    from materialsense.data import INPUTS, load_data

    path = tmp_path / "shifted.csv"
    path.write_text(
        ",".join(INPUTS + ["strength"]) + "\n" + ",".join(["1"] * count) + "\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="CSV record"):
        load_data(path)
