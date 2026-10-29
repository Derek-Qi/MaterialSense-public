# Data and third-party notices

MaterialSense software is MIT licensed; the copyright holder is Derek Qi. The software license
does not replace the separate licenses and attribution requirements of data or dependencies.

## UCI Concrete Compressive Strength

Creator: I-Cheng Yeh. Citation: Yeh, I. (1998). *Concrete Compressive Strength* [Dataset].
UCI Machine Learning Repository. DOI: [10.24432/C5PK67](https://doi.org/10.24432/C5PK67).

The [official dataset page](https://archive.ics.uci.edu/dataset/165/concrete+compressive+strength)
identifies the dataset as [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Preserve attribution, the license link and an indication of changes when reusing the data.
`data/raw/Concrete_Data.xls` is the retained original workbook; `data/raw/concrete.csv` renames
columns and serializes parsed values without deliberate rounding or deduplication.
Source/download/conversion hashes and details are in `data/raw/source.json` and `data/README.md`.
No endorsement by Yeh or UCI, new data collection or external engineering validation is implied.

## Dependencies and methods

Dependencies are installed separately under their own terms; locked application/test versions are
in `requirements.txt`, with additional build-only tools in `requirements-ci.txt`.
`reports/dependency-licenses.csv` is the earlier RC environment's license-metadata inventory,
not a complete legal review of every distribution or bundled asset. The included CI workflow is
configured to retain an installed environment list. Check the GitHub Actions run for the current commit.
No third-party source vendoring was identified in the scoped file inventory;
the author remains responsible for accurately disclosing any incorporated external code.

The statistical methods and cited research are described in `docs/methodology.md`.
Using established models, conformal calibration or KNN does not imply original algorithm authorship.
