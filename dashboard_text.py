"""Presentation-only translations; saved experiment data keeps its original schema."""

TEXT = {
    "prediction_csv": ("Download current prediction (CSV)", "下载当前预测（CSV）"),
    "benchmark_csv": ("Download benchmark metrics (CSV)", "下载模型评估指标（CSV）"),
    "tagline": (
        "Concrete strength, with uncertainty in view",
        "混凝土抗压强度预测与不确定性分析",
    ),
    "intro": (
        "Explore how a recipe and its curing age relate to predicted compressive strength. "
        "A reproducible case study in evaluating previously unseen concrete mixes.",
        "输入材料配方与养护龄期，查看抗压强度预测、预测区间和风险提示。"
        "本项目以未见过的混凝土配方为测试对象，展示可复现的模型评估流程。",
    ),
    "missing": (
        "No trained experiment found. From the project folder, run the data download and "
        "benchmark commands in README.md, then refresh this page.",
        "尚未找到已训练的实验结果。请在项目文件夹中按 README.md 下载数据并运行实验，然后刷新页面。",
    ),
    "load_error": (
        "The local experiment could not be loaded: {error}. Rerun the benchmark.",
        "无法加载本地实验结果：{error}。请重新运行实验。",
    ),
    "recipe": ("Your recipe", "材料配方"),
    "units": (
        "Ingredient quantities are kg/m³. Curing age is in days.",
        "材料用量单位为 kg/m³，养护龄期单位为天。",
    ),
    "cement": ("Cement", "水泥"),
    "slag": ("Blast furnace slag", "高炉矿渣"),
    "fly_ash": ("Fly ash", "粉煤灰"),
    "water": ("Water", "水"),
    "superplasticizer": ("Superplasticizer", "高效减水剂"),
    "coarse_aggregate": ("Coarse aggregate", "粗骨料"),
    "fine_aggregate": ("Fine aggregate", "细骨料"),
    "age": ("Curing age (days)", "养护龄期（天）"),
    "predict": ("Estimate strength", "预测抗压强度"),
    "example": (
        "The initial recipe is an example from training data, not an independent test.",
        "初始配方取自训练数据，仅供操作演示。",
    ),
    "estimate": ("Strength estimate", "预测结果"),
    "point": ("Predicted strength", "预测抗压强度"),
    "input_error": ("Check the recipe: {error}", "请检查配方：{error}"),
    "interval": (
        "**{nominal:.0%} nominal group-calibrated CQR interval:** {low:.1f} to {high:.1f} MPa",
        "**名义覆盖率 {nominal:.0%} 的配方分组校准 CQR 区间：** {low:.1f}～{high:.1f} MPa",
    ),
    "interval_note": (
        "The point estimate and interval use separate models; they may disagree. "
        "Coverage depends on exchangeable recipe clusters, including their measured ages.",
        "点预测与区间来自不同模型，二者可能不一致。覆盖率结论依赖配方组之间的可交换性，"
        "也包括各组龄期的测量方式。",
    ),
    "unbounded": (
        "The calibration set is too small for a finite interval at this nominal level.",
        "校准配方数量不足，在当前名义覆盖率下无法给出有限区间。",
    ),
    "ood": (
        "This recipe and age are far from training observations. Treat the prediction "
        "as extrapolation; interval coverage may fail here.",
        "OOD 提示：该配方与龄期远离训练数据，应视为外推预测；此时区间覆盖率可能失效。",
    ),
    "no_ood": (
        "Training-distance warning was not triggered. This does not establish reliability "
        "or physical feasibility.",
        "未触发 OOD 距离提示，但这并不代表预测一定可靠，或配方已通过物理可行性验证。",
    ),
    "distance": (
        "Nearest-neighbor distance: {distance:.2f}; training-based warning threshold: {threshold:.2f}.",
        "KNN 距离：{distance:.2f}；由训练数据确定的提示阈值：{threshold:.2f}。",
    ),
    "out_of_range": (
        "Outside individual training ranges: {names}.",
        "以下输入超出各自的训练范围：{names}。",
    ),
    "research_note": (
        "Research demonstration. Screening ranges are configurable heuristics, "
        "not design limits. Predictions do not certify structural safety.",
        "本页面用于研究演示。参考范围属于可调整的经验检查，不能替代工程设计规范；"
        "预测结果不构成结构安全认证。",
    ),
    "age_tab": ("Age response", "龄期响应"),
    "evidence_tab": ("Benchmark evidence", "实验结果"),
    "methods_tab": ("Method & limits", "方法与局限"),
    "age_title": ("Change age, hold this recipe fixed", "固定配方，观察龄期变化"),
    "strength_axis": ("Strength (MPa)", "抗压强度（MPa）"),
    "point_axis": ("Predicted strength (MPa)", "预测抗压强度（MPa）"),
    "lower": ("CQR lower bound (MPa)", "CQR 下限（MPa）"),
    "upper": ("CQR upper bound (MPa)", "CQR 上限（MPa）"),
    "age_note": (
        "Line: selected point model. Band: separately fitted CQR model. The age grid "
        "uses the training age range. This is a sensitivity probe, not a causal effect, "
        "a physical constraint, or simultaneous coverage for the entire curve.",
        "实线为所选模型的点预测，阴影为单独拟合的 CQR 区间。图中龄期限定在训练范围内。"
        "这是一项敏感性分析，不代表因果关系或物理约束，也不保证整条曲线同时被区间覆盖。",
    ),
    "selected": (
        "Model selected by training-only grouped CV: **{model} / {features} inputs**.",
        "仅使用训练数据进行分组 CV，选出的模型为：**{model} / {features}**。",
    ),
    "coverage": (
        "Measured CQR test coverage: {covered_rows}/{n_rows} observations; "
        "{covered_recipes}/{n_recipes} whole recipes.",
        "CQR 实测测试覆盖：{covered_rows}/{n_rows} 条记录；"
        "{covered_recipes}/{n_recipes} 个配方的全部测量记录。",
    ),
    "evidence_error": (
        "The saved evidence table could not be read: {error}. Rerun the benchmark.",
        "无法读取已保存的实验结果表：{error}。请重新运行实验。",
    ),
    "download": ("Download experiment metadata", "下载实验元数据"),
    "group_method": (
        "Recipe identity uses exact values of the first seven material quantities. Age and "
        "strength never enter the key. Train, calibration and test recipes are disjoint. "
        "Nearby recipes and missing laboratory identifiers remain a limitation.",
        "配方 ID 由前七项材料用量的精确数值确定，不包含龄期和强度。训练、校准和测试集的配方"
        "互不重叠。相近配方和缺失的实验室标识仍是本数据集的局限。",
    ),
    "calibration_method": (
        "Calibration uses one maximum score per recipe. A nominal coverage statement "
        "requires exchangeable calibration and future recipe clusters, including cluster "
        "sizes and age sampling. It does not guarantee every mix, age or OOD input.",
        "校准时，每个配方只贡献一个组内最大误差分数。名义覆盖率结论要求校准配方组与未来"
        "配方组可交换，包括组大小和龄期采样方式；不能据此保证每个配方、每个龄期或 OOD 输入。",
    ),
    "warning_method": (
        "KNN distance and physical screening are separate warnings; they do not enlarge "
        "the interval or restore its validity. Feature importance and age response are "
        "not causal evidence.",
        "KNN 距离与物理经验检查分别提供风险提示，不会自动扩大区间或恢复其有效性。"
        "特征重要性和龄期响应不能作为因果证据。",
    ),
    "source": ("Data", "数据来源"),
    "saved_run": ("Saved run: {date} | Seed {seed}", "实验保存时间：{date} | Seed {seed}"),
}

TEXT.update(
    {
        "lab_title": ("Explore concrete strength.", "探索混凝土强度。"),
        "lab_intro": (
            "Shape a recipe, move through curing time, and compare what the model predicts.",
            "调整配方、拖动龄期，直观比较模型预测与风险变化。",
        ),
        "lab_stats": (
            "{rows:,} measured observations / {recipes:,} exact recipes / {model}",
            "{rows:,} 条实测记录 / {recipes:,} 个精确配方 / {model}",
        ),
        "lab_tab": ("Live lab", "交互探索"),
        "data_tab": ("Data & evaluation", "数据与评估"),
        "record_tab": ("Research record", "研究记录"),
        "live_b": ("Live mix B", "当前配方 B"),
        "reference_a": ("Pinned mix A", "固定配方 A"),
        "slider_note": (
            "Adjust a slider to update the prediction automatically. Ingredients: kg/m³.",
            "调整滑块后自动更新预测。材料用量单位：kg/m³。",
        ),
        "preset": ("Starting recipe", "起始配方"),
        "preset_example": ("Training example", "训练样本示例"),
        "preset_water": ("Water stress test", "高水量外推测试"),
        "preset_custom": ("Custom mix", "自定义配方"),
        "reset": ("Reset mix", "重置配方"),
        "pin": ("Pin current mix as A", "将当前配方固定为 A"),
        "clear_a": ("Clear A", "清除 A"),
        "pin_hint": (
            "Pin A, then change B. The amber reference stays fixed, including its age.",
            "固定 A 后继续调整 B。琥珀色参考配方及其龄期保持不变。",
        ),
        "curve_title": ("Strength through curing time", "强度随养护龄期的变化"),
        "interval_method": ("Interval view", "预测区间"),
        "cqr_method": ("CQR", "CQR"),
        "residual_method": ("Residual conformal", "残差保形区间"),
        "interval_metric": ("{nominal:.0%} nominal {method}", "名义 {nominal:.0%} {method}"),
        "width_metric": ("Interval width", "区间宽度"),
        "unbounded_value": ("Unbounded", "无有限边界"),
        "curve_note": (
            "Sampled model response, 1–365 days. Shading is the selected prediction interval; "
            "it is not simultaneous coverage of the curve. OOD inputs may invalidate coverage.",
            "图示为 1～365 天的模型采样响应，阴影为所选预测区间，不保证整条曲线同时覆盖；"
            "OOD 输入可能导致覆盖率失效。",
        ),
        "composition": ("Ingredient composition", "材料组成"),
        "ingredient": ("Ingredient", "材料"),
        "mass_share": ("Mass share", "质量占比"),
        "mass_total": (
            "Total ingredient mass: {mass:.1f} kg/m³. Shares show mass, not volume.",
            "材料总用量：{mass:.1f} kg/m³。图中为质量占比，不是体积占比。",
        ),
        "risk_title": ("Domain checks", "适用范围检查"),
        "distance_meter": (
            "KNN distance {distance:.2f} / threshold {threshold:.2f}",
            "KNN 距离 {distance:.2f} / 阈值 {threshold:.2f}",
        ),
        "comparison": ("A / B comparison", "A / B 对比"),
        "mix": ("Mix", "配方"),
        "prediction": ("Prediction (MPa)", "预测值（MPa）"),
        "map_title": ("Find your mix among real measurements", "在真实测量数据中定位配方"),
        "map_hint": (
            "Click a measured point to inspect it; scroll to zoom and drag to pan. "
            "The amber diamond is B's prediction. This 2D view is not the KNN distance space.",
            "点击实测点查看配方，滚轮缩放、拖动平移。琥珀色菱形为 B 的预测位置。"
            "该二维视图不等同于 KNN 计算距离的特征空间。",
        ),
        "water_binder": ("Water / binder", "水胶比"),
        "measured_axis": ("Measured strength (MPa)", "实测抗压强度（MPa）"),
        "sample": ("Sample", "样本"),
        "load_sample": ("Explore this measured recipe", "将该实测配方载入探索台"),
        "selected_sample": (
            "Measured strength: {strength:.2f} MPa at {age:g} days. Dataset row #{row}.",
            "实测强度：{strength:.2f} MPa，龄期 {age:g} 天。数据行号 #{row}。",
        ),
        "data_unavailable": (
            "Measured-data view is unavailable. The live model remains usable.",
            "暂时无法显示实测数据视图，仍可使用实时预测。",
        ),
        "details": ("Technical details", "技术详情"),
        "split_title": ("See why recipe grouping matters", "直观看配方分组的作用"),
        "split_view": ("Evaluation protocol", "评估方式"),
        "grouped": ("Recipe grouped", "按配方分组"),
        "random": ("Row random (diagnostic)", "按记录随机划分（对照）"),
        "shared_recipes": ("Recipes shared by train & test", "训练与测试共享配方数"),
        "test_rmse": ("Selected model test RMSE", "所选模型测试 RMSE"),
        "partition": ("Partition", "数据分区"),
        "audit_recipe": ("Inspect a repeated recipe", "检查一个重复配方"),
        "split_note": (
            "The protocols use different test rows. This is a descriptive comparison, "
            "not a causal leakage estimate. Model selection used grouped training-only CV.",
            "两种方式的测试记录不同，此处仅作描述性比较，不是数据泄漏的因果效应估计。"
            "模型选择仅使用训练集内的分组 CV。",
        ),
        "assignments_unavailable": (
            "Saved split assignments could not be displayed.",
            "暂时无法显示已保存的数据划分。",
        ),
    }
)

MODELS = {
    "mean": ("Mean baseline", "均值基线"),
    "ridge": ("Ridge", "Ridge"),
    "random_forest": ("RandomForest", "RandomForest"),
    "gradient_boosting": ("GradientBoosting", "GradientBoosting"),
}
FEATURES = {"raw": ("Raw", "原始特征"), "engineered": ("Engineered", "工程特征")}
INPUT_ERRORS = {
    "Total binder must be positive.": "胶凝材料总量必须大于 0。",
    "Water and age must be positive.": "水用量和养护龄期必须大于 0。",
    "Ingredient quantities cannot be negative.": "材料用量不能为负数。",
    "Missing or infinite values are not permitted.": "输入不能包含缺失值或无穷大。",
    "All inputs and targets must be numeric.": "所有输入必须是数值。",
    "Engineered inputs overflowed; check ingredient magnitudes.": "计算超出数值范围，请检查材料用量。",
}


def text(key, language, **values):
    return TEXT[key][language == "zh"].format(**values)


def model_label(name, language):
    return MODELS.get(name, (name, name))[language == "zh"]


def feature_label(name, language):
    return FEATURES.get(name, (name, name))[language == "zh"]


def input_error(error, language):
    message = str(error)
    return INPUT_ERRORS.get(message, message) if language == "zh" else message


def physical_warning(message, language):
    if language != "zh":
        return message
    return (
        message.replace(
            "Total ingredient mass is outside the heuristic range", "材料总用量超出经验参考范围"
        )
        .replace("Water/binder is outside the heuristic range", "水胶比超出经验参考范围")
        .replace("kg/m3", "kg/m³")
        .removesuffix(".")
        + "。"
    )


def metrics_table(metrics, language):
    table = metrics.copy()
    table["model"] = table.model.map(lambda value: model_label(value, language))
    table["features"] = table.features.map(lambda value: feature_label(value, language))
    if language == "zh":
        table["protocol"] = table.protocol.replace(
            {"grouped": "配方分组", "row_random_diagnostic": "随机划分（对照）"}
        )
        table = table.rename(
            columns={
                "protocol": "划分方式",
                "model": "模型",
                "features": "特征",
                "rmse": "RMSE",
                "mae": "MAE",
                "r2": "R²",
                "group_rmse": "配方均衡 RMSE",
                "group_mae": "配方均衡 MAE",
                "n_rows": "记录数",
                "n_groups": "配方数",
            }
        )
    return table
