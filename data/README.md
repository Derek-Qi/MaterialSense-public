# Data provenance

**Original dataset:** I-Cheng Yeh, Concrete Compressive Strength (1998), UCI ID 165.
**Repository DOI:** https://doi.org/10.24432/C5PK67
**Dataset page:** https://archive.ics.uci.edu/dataset/165/concrete+compressive+strength
**License:** [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).

Official archive: `https://archive.ics.uci.edu/static/public/165/concrete+compressive+strength.zip`.
Pinned archive SHA-256: `dad85d14de8aee4e07479daa774e6b569a313715b71a3b92c95a07cf91c2c9a7`.

`raw/Concrete_Data.xls` is the unmodified original workbook. `raw/concrete.csv` renames its nine
columns and serializes the parsed numerical values without deliberate rounding or deduplication.
`raw/source.json` records the source, workbook and canonical CSV checksums. Preserve the original
workbook and source metadata when reusing the CSV. CC BY 4.0 applies to the source data; attribution
does not imply endorsement by the original author or UCI.

Canonical columns: cement, slag, fly_ash, water, superplasticizer, coarse_aggregate, fine_aggregate
(all kg/m³), age (days), strength (MPa). No missing values are imputed. Invalid/nonfinite values,
negative ingredients, nonpositive water/age/strength and zero binder are rejected. Recipe IDs use
the first seven numeric quantities and ignore age/strength.

