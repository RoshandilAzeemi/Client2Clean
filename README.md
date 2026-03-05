Client2Clean is a professional-grade ETL (Extract, Transform, Load) pipeline designed to solve the common business problem of "Data Decay." It automates the process of cleaning, validating, and deduplicating messy client databases, transforming them into a verified "Golden Record."

Initially prototyped during my internship at Sohail Akhtar Enterprise Inc., this tool has evolved into a full-scale web application built with Python, Streamlit, and Pydantic.

🚀 Key Features
Intelligent Deduplication: Uses RapidFuzz (Token Set Ratio) to identify potential duplicates with minor typos or different word orders (e.g., "Apple Inc" vs. "Apple Incorporated").

Schema Validation: Leverages Pydantic to enforce data integrity, such as normalizing phone numbers to 10 digits and verifying email formats.

Dynamic Column Mapping: Flexible ingestion that allows users to map their own CSV/Excel columns to the tool's internal logic.

Audit-Ready Exports: Generates a multi-sheet Excel (.xlsx) workbook containing:

Cleaned Records: The final, validated "Golden" dataset.

Duplicate Report: A list of exactly matched rows removed.

Conflict Flags: A high-priority list of fuzzy matches for human review.

🛠️ Tech Stack
Frontend: Streamlit

Data Processing: Pandas, NumPy

Validation: Pydantic (Type hinting and data cleaning)

Fuzzy Matching: RapidFuzz (Levenshtein Distance algorithms)

Excel Engine: OpenPyXL

📖 How to Use
Upload: Drag and drop your messy .csv or .xlsx file into the dashboard.

Map: Select which columns in your file correspond to "Name," "Email," and "Phone."

Adjust: (Optional) Use the sidebar slider to change the Fuzzy Match Threshold (default is 90%).

Review: Preview the "Invalid Records" (those that failed Pydantic validation) and "Fuzzy Conflicts" directly in the browser.

Download: Click "Download Excel" to get your sanitized, ready-to-use dataset.

💻 Local Setup
If you want to run this project on your own machine (e.g., MacBook Pro or ASUS TUF):

Bash
# Clone the repository
git clone https://github.com/RoshandilAzeemi/Client2Clean.git

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
