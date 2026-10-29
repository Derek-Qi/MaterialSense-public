# Wu 2019 cross-source exploration

## Scope and source

This is exploratory assessment of one research source using an existing frozen seed42 MaterialSense model. It is not harmonized external validation or an engineering qualification. No Wu labels were used for training, model selection, tuning, strength conversion, or interval recalibration.

The source is [Wu et al. (2019)](https://doi.org/10.3390/app9112266), CC BY 4.0. The retained transcription contains seven recipes at five ages: 35 means of three specimens, not 35 independent recipes or 105 acquired raw measurements. Ingredient amounts are kg/m³, age is days, and strength is MPa. The accompanying [predictions.csv](predictions.csv) and [summary.json](summary.json) identify their source checksum. UCI training data are credited separately to [I-Cheng Yeh](https://doi.org/10.24432/C5PK67), CC BY 4.0.

## Recorded outcomes

All 35/35 means were underpredicted. MAE is 15.327213 MPa and RMSE 15.684915 MPa. Residual intervals cover 2/35 observations and CQR covers 11/35; both cover all recorded ages of 0/7 recipes. Of the 16 observations without a distance warning, mean absolute error is 14.959584 MPa.

For F3R2 at 14 days, the reported mean is 61.5 MPa and the frozen prediction 40.514747 MPa; no distance warning fires. A small statistical input distance therefore does not certify a small prediction error. The denominators above are retained directly rather than treating these aggregate observations as independent replications.

## Unresolved comparability and transcription limits

- Wu used 100×200 mm cylinders and three-specimen means. The provenance, geometry and target-aggregation definitions of all 1,030 UCI records have not been aligned to this source.
- Slag=0 is a structural inference supported by the described ingredient list and complete mix table, not a separately printed measured zero. Water remains the table's 180 kg/m³ value and was not back-calculated.
- The audit did not confirm the statistical meaning of the original ± values. They are not assumed to be SD, SE, noise limits or error-normalization denominators.
- At 91 days the table gives F3R1=77.9 and F3R2=76.5 MPa, while the prose identifies the latter as highest. The original table values remain the primary inputs; this does not adjudicate the true measurement.
- The error cannot be attributed to fineness, superplasticizer, specimen size, curing or laboratory differences from these residuals alone.

## Evidence identity

The Phase 5 predictions were recomputed by a separate Phase 6 calculation, using the same underlying records. This is not independent human blind review or a new laboratory experiment. Historical Phase 6 logs record 86 software tests passing; this publication does not rerun or rebrand those tests.

No model, original paper PDF, classroom document, workstation path or team roster is included in this evidence subset.

## 中文范围说明

这是冻结模型在单研究来源上的跨来源探索，不是正式同口径外部验证。数据为 7 个配方、5 个龄期的 35 个三试件均值。35/35 均被低估；MAE 15.327 MPa，RMSE 15.685 MPa。残差区间覆盖 2/35，CQR 覆盖 11/35，整组覆盖均为 0/7。未触发距离警告的 16 条记录 MAE 仍为 14.960 MPa。

必须保留试件与统计口径未对齐、矿渣零值的结构性推断、原文最高值冲突及 ± 含义未确认等限制。本次整理不重训、调参、再校准，也不把历史 86 项软件测试当成本轮新测试。
