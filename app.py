import io
from typing import List, Tuple

import pandas as pd
import streamlit as st
from pydantic import BaseModel, EmailStr, ValidationError, field_validator
from rapidfuzz import fuzz

from src.dedupe_clients import dedupe_clients


class ClientRecord(BaseModel):
    name: str
    email: EmailStr
    phone: str

    @field_validator("phone")
    @classmethod
    def normalize_and_validate_phone(cls, v: str) -> str:
        digits = "".join(ch for ch in str(v) if ch.isdigit())
        if len(digits) != 10:
            raise ValueError("phone must contain exactly 10 digits after normalization")
        return digits


def read_uploaded_file(upload) -> pd.DataFrame:
    """Read uploaded file (.csv, .xlsx, .xls, .json) into a DataFrame."""
    name = upload.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(upload)
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(upload)
    if name.endswith(".json"):
        return pd.read_json(upload)
    raise ValueError("Unsupported file type. Use .csv, .xlsx, .xls, or .json.")


def apply_pydantic_validation(
    df: pd.DataFrame,
    name_col: str = "Client Name",
    email_col: str = "Email",
    phone_col: str = "Phone",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Validate rows with Pydantic and split into valid vs invalid."""
    valid_rows: List[dict] = []
    invalid_rows: List[dict] = []

    for _, row in df.iterrows():
        raw = {
            "name": row.get(name_col, ""),
            "email": row.get(email_col, ""),
            "phone": row.get(phone_col, ""),
        }
        try:
            model = ClientRecord(**raw)
            valid_rows.append({**row.to_dict(), "phone_normalized": model.phone})
        except ValidationError as e:
            invalid_rows.append({**row.to_dict(), "validation_error": str(e)})

    df_valid = pd.DataFrame(valid_rows) if valid_rows else pd.DataFrame(columns=df.columns)
    df_invalid = pd.DataFrame(invalid_rows) if invalid_rows else pd.DataFrame(columns=list(df.columns) + ["validation_error"])
    return df_valid, df_invalid


def fuzzy_conflicts_on_name(
    df: pd.DataFrame, name_col: str = "Client Name", threshold: int = 90
) -> pd.DataFrame:
    """
    Simple fuzzy match on client name to detect potential conflicts.

    This runs an O(n^2) comparison on the name column, which is fine
    for small/medium client lists typical of manual uploads.
    """
    if name_col not in df.columns:
        return pd.DataFrame()

    conflicts: List[dict] = []
    names = df[name_col].astype(str).fillna("").tolist()
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            score = fuzz.token_set_ratio(names[i], names[j])
            if score >= threshold:
                conflicts.append(
                    {
                        "index_1": i,
                        "index_2": j,
                        "name_1": names[i],
                        "name_2": names[j],
                        "similarity_score": score,
                    }
                )

    return pd.DataFrame(conflicts)


def build_excel_workbook(
    cleaned: pd.DataFrame, duplicates: pd.DataFrame, conflicts: pd.DataFrame
) -> bytes:
    """Create an Excel file in memory with separate sheets."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        cleaned.to_excel(writer, index=False, sheet_name="Cleaned_Clients")
        duplicates.to_excel(writer, index=False, sheet_name="Duplicates_Report")
        conflicts.to_excel(writer, index=False, sheet_name="Conflicts")
    buffer.seek(0)
    return buffer.read()


def main() -> None:
    st.set_page_config(page_title="Client Deduper", layout="wide")
    st.title("Client Deduper")
    st.markdown(
        "Upload your messy client list, and this app will detect duplicates, "
        "validate records, and give you a clean Excel export."
    )

    with st.sidebar:
        st.header("Settings")
        fuzzy_enabled = st.checkbox("Enable fuzzy name matching", value=True)
        fuzzy_threshold = st.slider(
            "Fuzzy match threshold", min_value=70, max_value=100, value=90, step=1
        )

    upload = st.file_uploader(
        "Upload a client list (.csv, .xlsx, .xls, .json)", type=["csv", "xlsx", "xls", "json"]
    )

    if not upload:
        st.info("Upload a file to begin deduplication.")
        return

    try:
        df_raw = read_uploaded_file(upload)
    except Exception as e:
        st.error(f"Could not read file: {e}")
        return

    st.subheader("Raw Data Preview")
    st.dataframe(df_raw.head(50))

    # Transform: dedupe + validation + fuzzy conflicts
    try:
        df_clean, dupes = dedupe_clients(df_raw)
    except Exception as e:
        st.error(f"Error during deduplication: {e}")
        return

    df_valid, df_invalid = apply_pydantic_validation(df_clean)

    conflicts = pd.DataFrame()
    if fuzzy_enabled:
        conflicts = fuzzy_conflicts_on_name(df_valid, threshold=fuzzy_threshold)

    # Sidebar stats
    with st.sidebar:
        total_rows = len(df_raw)
        total_unique = len(df_clean)
        total_dupes = len(dupes)
        total_invalid = len(df_invalid)

        st.markdown("### Dataset Stats")
        st.metric("Total rows uploaded", total_rows)
        st.metric("Duplicate rows found", total_dupes)
        st.metric("Unique clients remaining", total_unique)
        st.metric("Invalid records (validation)", total_invalid)

    st.subheader("Cleaned Clients Preview")
    st.dataframe(df_valid.head(50))

    if not df_invalid.empty:
        st.subheader("Invalid Records (Pydantic Validation)")
        st.dataframe(df_invalid.head(50))

    if not conflicts.empty:
        st.subheader("Fuzzy Name Conflicts")
        st.caption(
            "These rows have very similar names and may represent the same client. "
            "Review before finalizing."
        )
        st.dataframe(conflicts.head(100))

    excel_bytes = build_excel_workbook(df_valid, dupes, conflicts)

    st.subheader("Download Cleaned Excel")
    st.download_button(
        label="Download Excel (Cleaned + Duplicates + Conflicts)",
        data=excel_bytes,
        file_name="clients_deduped.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


if __name__ == "__main__":
    main()

