#!/usr/bin/env python3

"""
dedupe_clients.py

Simple project to:
- Read a client list from Excel/CSV
- Normalize email + phone
- Automatically detect duplicate records
- Output:
    - a cleaned, deduplicated client file
    - a duplicates report showing what was kept and what was dropped
"""

import argparse
import os
import sys
import pandas as pd


def read_input_file(path: str) -> pd.DataFrame:
    """Read CSV or Excel into a DataFrame based on extension."""
    ext = os.path.splitext(path)[1].lower()

    if ext in [".xlsx", ".xls"]:
        return pd.read_excel(path)
    elif ext in [".csv", ".txt"]:
        return pd.read_csv(path)
    else:
        raise ValueError(
            f"Unsupported file type '{ext}'. Use .xlsx, .xls, .csv, or .txt."
        )


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize text columns used for deduplication.
    Change the column names here if your file uses different headers.
    """

    # 🔧 ADJUST THESE if your headers differ
    name_col = "Client Name"
    email_col = "Email"
    phone_col = "Phone"

    # Simple sanity check
    for col in [name_col, email_col, phone_col]:
        if col not in df.columns:
            raise KeyError(
                f"Expected column '{col}' not found in file. "
                f"Columns found: {list(df.columns)}"
            )

    df = df.copy()

    # Normalize name: lowercased, stripped
    df["name_norm"] = (
        df[name_col]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # Normalize email
    df["email_norm"] = (
        df[email_col]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # Normalize phone: keep only digits
    df["phone_norm"] = (
        df[phone_col]
        .astype(str)
        .str.replace(r"\D", "", regex=True)  # remove non-digits
    )

    return df


def dedupe_clients(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Deduplicate clients based on normalized email + phone.

    Logic:
    - Treat rows with the same (email_norm, phone_norm) as the same client.
    - Keep the first occurrence as the "master" record.
    - Mark the rest as duplicates in a report.
    """

    df = df.copy()

    # Normalize
    df = normalize_columns(df)

    # Rows that are part of ANY duplicate group (including the "kept" one)
    dup_group_mask = df.duplicated(
        subset=["email_norm", "phone_norm"], keep=False
    )

    # Rows that are actually dropped (not the first in their group)
    dropped_mask = df.duplicated(
        subset=["email_norm", "phone_norm"], keep="first"
    )

    # Cleaned DataFrame: keep first occurrence of each (email_norm, phone_norm) combo
    df_clean = df[~dropped_mask].copy()

    # Build duplicates report
    duplicates_report = df[dup_group_mask].copy()
    # Mark which row in each group was kept
    duplicates_report["is_kept"] = ~duplicates_report.duplicated(
        subset=["email_norm", "phone_norm"], keep="first"
    )

    # Drop helper columns from the outputs if you want them clean
    cols_to_drop = ["name_norm", "email_norm", "phone_norm"]
    df_clean = df_clean.drop(columns=cols_to_drop, errors="ignore")
    duplicates_report = duplicates_report  # you may keep norms here for debugging

    return df_clean, duplicates_report


def write_output(
    df_clean: pd.DataFrame,
    duplicates_report: pd.DataFrame,
    clean_path: str,
    dupes_path: str,
) -> None:
    """Write the cleaned data and duplicates report to Excel files."""
    os.makedirs(os.path.dirname(clean_path), exist_ok=True)
    os.makedirs(os.path.dirname(dupes_path), exist_ok=True)

    df_clean.to_excel(clean_path, index=False)
    duplicates_report.to_excel(dupes_path, index=False)

    print(f"[OK] Cleaned data written to: {clean_path}")
    print(f"[OK] Duplicates report written to: {dupes_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Automated client deduplication using Python + pandas."
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to input file (.xlsx, .xls, .csv, .txt).",
    )
    parser.add_argument(
        "--output-clean",
        "-oc",
        default="data/output/clients_clean.xlsx",
        help="Path to write deduplicated client file.",
    )
    parser.add_argument(
        "--output-dupes",
        "-od",
        default="data/output/duplicates_report.xlsx",
        help="Path to write duplicates report file.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        df = read_input_file(args.input)
    except Exception as e:
        print(f"[ERROR] Failed to read input file: {e}")
        sys.exit(1)

    try:
        df_clean, dupes = dedupe_clients(df)
    except Exception as e:
        print(f"[ERROR] Failed during deduplication: {e}")
        sys.exit(1)

    try:
        write_output(df_clean, dupes, args.output_clean, args.output_dupes)
    except Exception as e:
        print(f"[ERROR] Failed to write output files: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

'''
**In order to excecute process of removing duplicates, use this command in terminal: 
python src/dedupe_clients.py --input data/input/clients_raw.xlsx --output-clean data/output/clients_clean.xlsx --output-dupes data/output/duplicates_report.xlsx
'''