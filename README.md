<div align="center">

# 🧹 Client2Clean

### Automated Client List Deduplication & Validation Engine

*Upload messy client data. Get a clean, validated, deduplicated Excel export in seconds.*

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![RapidFuzz](https://img.shields.io/badge/RapidFuzz-Fuzzy_Matching-00A98F?style=for-the-badge)](https://github.com/rapidfuzz/RapidFuzz)

</div>

---

## Overview

Client2Clean cleans up messy client lists exported from spreadsheets, forms, or legacy systems. It combines three complementary data-quality checks:

1. **Deterministic deduplication** — matches on normalized email + phone to catch exact duplicates across formatting variations.
2. **Pydantic validation** — enforces valid email format and exactly-10-digit phone numbers, separating valid from invalid records.
3. **Fuzzy conflict detection** — surfaces near-duplicate names (e.g., "Michael Johnson" vs. "Mike Johnson") that exact matching misses, via RapidFuzz.

Two interfaces share the same engine: a **Streamlit web UI** for interactive use, and a **CLI** for batch/scripted processing. Output is a multi-sheet Excel workbook (cleaned records, duplicates report, conflicts) — no database or server required.

## Features

- Upload `.csv`, `.xlsx`, `.xls`, or `.json` and preview raw + cleaned data in-browser
- Duplicate detection on normalized `(email, phone)`, with a report showing what was kept vs. dropped
- Pydantic-based validation with per-record error messages for invalid emails/phones
- Configurable fuzzy-match threshold (70–100) for near-duplicate names
- One-click multi-sheet Excel export (`Cleaned_Clients`, `Duplicates_Report`, `Conflicts`)
- Headless CLI for scripts/CI pipelines, sharing the same dedup logic as the UI

## Project Structure

```
Client2Clean/
├── app.py                      # Streamlit web app
├── src/dedupe_clients.py       # Core dedup engine + CLI entry point
├── scripts/generate_test_data.py   # Generates sample messy test data
├── imghdr.py                   # Compat shim: stdlib imghdr was removed in Python 3.13,
│                                # but older Streamlit still imports it
├── requirements.txt
└── test_data_raw_clients.csv/.xlsx # Sample messy data for testing
```

## Getting Started

**Prerequisites:** Python 3.11+

```bash
git clone https://github.com/RoshandilAzeemi/Client2Clean.git
cd Client2Clean

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### Web UI

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`. Upload `test_data_raw_clients.csv` (included) to try it out.

### CLI

```bash
python src/dedupe_clients.py \
    --input test_data_raw_clients.csv \
    --output-clean data/output/clients_clean.xlsx \
    --output-dupes data/output/duplicates_report.xlsx
```

| Argument | Short | Default | Description |
|---|---|---|---|
| `--input` | `-i` | required | Path to input file (`.xlsx`, `.xls`, `.csv`, `.txt`) |
| `--output-clean` | `-oc` | `data/output/clients_clean.xlsx` | Path for deduplicated output |
| `--output-dupes` | `-od` | `data/output/duplicates_report.xlsx` | Path for duplicates report |

### Generating fresh test data

```bash
python scripts/generate_test_data.py
```

Regenerates `test_data_raw_clients.xlsx` with known duplicates, invalid records, and fuzzy-conflict name pairs.

## Input Schema

Files must contain these columns (case-sensitive):

| Column | Required | Notes |
|---|---|---|
| `Client Name` | Yes | Used for display and fuzzy matching |
| `Email` | Yes | Part of the dedup key; must be RFC-5322 valid to pass validation |
| `Phone` | Yes | Any format accepted; normalized to digits, must be exactly 10 |

## Deployment

Easiest path is [Streamlit Community Cloud](https://share.streamlit.io/): push to GitHub, connect the repo, set the main file to `app.py`, deploy. It auto-installs from `requirements.txt`.

## Roadmap

- [ ] Unit test suite (`dedupe_clients`, validation, fuzzy matching)
- [ ] Configurable column mapping in the UI (currently hardcoded to `Client Name`/`Email`/`Phone`)
- [ ] Phonetic blocking to reduce fuzzy-match cost on large datasets

## Credits

Built by [Roshandil Azeemi](https://github.com/RoshandilAzeemi).

Built with Streamlit, Pandas, Pydantic, and RapidFuzz.
