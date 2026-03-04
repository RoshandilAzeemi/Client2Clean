#!/usr/bin/env python3
"""
Generate a raw, uncleaned Excel file for testing Client2Clean.
Includes: duplicates, invalid emails/phones, extra spaces, mixed formats.
Expected columns: Client Name, Email, Phone
"""

import pandas as pd
from pathlib import Path

# Raw messy data designed to trigger dedup, validation, and fuzzy conflict features
RAW_ROWS = [
    # --- Valid-looking but with duplicates ---
    {"Client Name": "John Smith", "Email": "john.smith@example.com", "Phone": "5551234567"},
    {"Client Name": "  John Smith  ", "Email": "JOHN.SMITH@EXAMPLE.COM", "Phone": "(555) 123-4567"},  # duplicate, different format
    {"Client Name": "Jane Doe", "Email": "jane.doe@test.org", "Phone": "5559876543"},
    {"Client Name": "Jane Doe", "Email": "jane.doe@test.org", "Phone": "555-987-6543"},  # exact duplicate (different phone format)
    {"Client Name": "Bob Wilson", "Email": "bob@company.co", "Phone": "5551112233"},
    {"Client Name": "bob wilson", "Email": "bob@company.co", "Phone": "5551112233"},  # duplicate, different name case
    # --- Invalid emails ---
    {"Client Name": "Bad Email User", "Email": "notanemail", "Phone": "5552223344"},
    {"Client Name": "Another Bad", "Email": "missing@domain", "Phone": "5553334455"},
    {"Client Name": "No At Sign", "Email": "user.gmail.com", "Phone": "5554445566"},
    {"Client Name": "Empty Email", "Email": "", "Phone": "5555556677"},
    # --- Invalid phones (not 10 digits after stripping) ---
    {"Client Name": "Short Phone", "Email": "short@example.com", "Phone": "123"},
    {"Client Name": "Long Phone", "Email": "long@example.com", "Phone": "55512345678901"},
    {"Client Name": "Letters in Phone", "Email": "letters@example.com", "Phone": "555-CALL-NOW"},
    {"Client Name": "Empty Phone", "Email": "nophone@example.com", "Phone": ""},
    # --- Fuzzy name conflicts (similar names) ---
    {"Client Name": "Michael Johnson", "Email": "michael.j@example.com", "Phone": "5556667788"},
    {"Client Name": "Mike Johnson", "Email": "mike.j@other.com", "Phone": "5557778899"},
    {"Client Name": "Sarah Williams", "Email": "sarah.w@example.com", "Phone": "5558889900"},
    {"Client Name": "Sara Williams", "Email": "sara.w@example.com", "Phone": "5559990011"},
    {"Client Name": "Robert Brown", "Email": "robert.b@example.com", "Phone": "5550001122"},
    {"Client Name": "Rob Brown", "Email": "rob.brown@example.com", "Phone": "5551112234"},
    # --- Extra messy formatting ---
    {"Client Name": "  Alice   Cooper  ", "Email": "  alice.cooper@example.com  ", "Phone": " 5552223334 "},
    {"Client Name": "ALICE COOPER", "Email": "alice.cooper@example.com", "Phone": "+1 555-222-3334"},  # duplicate of above
    {"Client Name": "David Lee", "Email": "david.lee@test.com", "Phone": "1-555-333-4445"},
    {"Client Name": "David Lee", "Email": "david.lee@test.com", "Phone": "15553334445"},
]

def main():
    out_dir = Path(__file__).resolve().parent.parent
    out_path = out_dir / "test_data_raw_clients.xlsx"
    df = pd.DataFrame(RAW_ROWS)
    df.to_excel(out_path, index=False, sheet_name="Clients")
    print(f"Created: {out_path}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")

if __name__ == "__main__":
    main()
