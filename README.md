# Locus Bug Localization (Prototype)

This repository contains a prototype Python implementation of the
[Locus](https://doi.org/10.1145/2970276.2970320) bug localization method.
Locus locates buggy commits by combining textual similarity between bug
reports and code changes with historical change metrics.

The code in `locus/` is structured into a few modules:

- `data_acquisition.py` – fetches bug-fixing commits and bug report text.
- `preprocessing.py` – extracts diff hunks and prepares natural language
  and code entity tokens.
- `indexing.py` – builds TF‑IDF models for tokens.
- `ranking.py` – computes similarity scores and combines them.
- `evaluation.py` – simple evaluation metrics such as MRR and Top@N.
- `main.py` – example entry point to run the pipeline (incomplete).

This implementation is incomplete and intended only as a starting point
for experimenting with Locus. Network access may be required to mine the
project history and bug reports. See comments in the source for details.
