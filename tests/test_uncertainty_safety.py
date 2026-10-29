import numpy as np
import pytest


def test_finite_sample_quantile_uses_n_plus_one_rank_and_handles_small_n():
    from materialsense.uncertainty import finite_sample_quantile

    assert finite_sample_quantile(np.arange(1, 10), 0.2) == 8
    assert np.isinf(finite_sample_quantile([1, 2, 3], 0.1))
    with pytest.raises(ValueError):
        finite_sample_quantile([], 0.1)
    with pytest.raises(ValueError):
        finite_sample_quantile([np.nan], 0.1)
    with pytest.raises(ValueError):
        finite_sample_quantile([1], 1.0)


def test_calibration_counts_groups_equally_and_uses_maximum():
    from materialsense.uncertainty import group_max_scores

    result = group_max_scores([1, 9, 3, 4], ["a", "a", "b", "c"])
    assert sorted(result.tolist()) == [3, 4, 9]


def test_cqr_crossing_is_sorted_and_intervals_never_shrink():
    from materialsense.uncertainty import cqr_interval, cqr_scores

    scores = cqr_scores(np.array([6, 8, 1]), [10, 4, 4], [2, 6, 6])
    assert scores.tolist() == [0, 2, 3]
    low, high = cqr_interval([10, 4], [2, 6], 2)
    assert low.tolist() == [0, 2]
    assert high.tolist() == [12, 8]


def test_ood_excludes_self_neighbors_and_flags_far_points():
    from materialsense.safety import KNNWarning

    detector = KNNWarning(neighbors=1, threshold_quantile=0.95).fit(np.array([[0.0], [2.0], [4.0]]))
    assert detector.threshold_ == pytest.approx(2 / np.std([0, 2, 4]))
    distance, flag = detector.predict([[2], [100]])
    assert not flag[0] and flag[1]
    assert distance[1] > distance[0]
    # A query must not refit or change the training-only threshold.
    assert detector.scaler_.mean_[0] == 2


def test_physical_warnings_are_heuristics_and_do_not_silently_change_input(concrete_frame):
    from materialsense.safety import physical_warnings

    frame = concrete_frame.iloc[:1].copy()
    frame.loc[0, "water"] = 900
    warnings = physical_warnings(frame, [2100, 2550], [0.2, 0.8])
    assert len(warnings) >= 2
    assert frame.loc[0, "water"] == 900


def test_whole_recipe_coverage_and_86_group_quantile():
    from materialsense.uncertainty import finite_sample_quantile, interval_metrics

    assert finite_sample_quantile(np.arange(86), 0.1) == 78
    result = interval_metrics([1, 2, 3], [0, 0, 0], [1, 1, 4], ["a", "a", "b"])
    assert result["row_coverage"] == pytest.approx(2 / 3)
    assert result["whole_recipe_coverage"] == 0.5
