import os
import pandas as pd
import random
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

# -----------------------------
# CONFIG
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_BASE_DIR = DATA_DIR / "raw_data"
RAW_BASE_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Generate Dummy Data
# -----------------------------
def generate_dummy_data(n=75):
    statuses = ["Offer", "Offer In Process", "Decline", "Withdrawed"]
    types = ["Internal", "External"]

    data = []

    for i in range(n):
        row = {
            "req_id": f"REQ{1000+i}",
            "candidate_id": f"CID{5000+i}",
            "candidate_status": random.choice(statuses),
            "candidate_type_when_applying": random.choice(types)
        }
        data.append(row)

    return pd.DataFrame(data)


def _create_zip_with_csv(dest_dir, file_index, rows=80):
    df = generate_dummy_data(rows)

    csv_name = f"offer_report_{file_index}.csv"
    zip_name = f"offer_report_{file_index}.zip"

    csv_path = dest_dir / csv_name
    zip_path = dest_dir / zip_name

    df.to_csv(csv_path, index=False)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(csv_path, arcname=csv_name)

    os.remove(csv_path)  # remove raw csv, keep only zip

    print(f"Dummy ZIP created at: {zip_path}")


def create_dummy_data_for_last_n_days(days=3, files_per_day=None, rows_per_file=80):
    """
    Create dummy ZIPs for the last N days ending today.
    Example structure (for 3 days):
      data/raw_data/2026-02-27/offer_report_1.zip
      data/raw_data/2026-02-28/offer_report_1.zip
      data/raw_data/2026-03-01/offer_report_1.zip
    """
    if days < 1:
        raise ValueError("days must be >= 1")

    if files_per_day is None:
        # Default: 2 files for the oldest day, 1 for middle, 1 for today
        files_per_day = {}

    today = datetime.today().date()

    for i in range(days - 1, -1, -1):
        day = today - timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        day_dir = RAW_BASE_DIR / day_str
        day_dir.mkdir(parents=True, exist_ok=True)

        count = files_per_day.get(day_str, 1)
        for idx in range(1, count + 1):
            _create_zip_with_csv(day_dir, idx, rows=rows_per_file)


def create_dummy_approved_decline_files():
    """
    Create small approved/decline datasets to test filtering logic.
    Columns:
      req_id,candidate_id,candidate_status,candidate_type_when_applying
    """
    approved_path = DATA_DIR / "offer_approved_data.csv"
    decline_path = DATA_DIR / "offer_decline_data.csv"

    approved_rows = [
        {
            "req_id": "REQ1001",
            "candidate_id": "CID5001",
            "candidate_status": "Offer",
            "candidate_type_when_applying": "External",
        },
        {
            "req_id": "REQ1002",
            "candidate_id": "CID5002",
            "candidate_status": "Offer In Process",
            "candidate_type_when_applying": "External",
        },
    ]

    decline_rows = [
        {
            "req_id": "REQ1003",
            "candidate_id": "CID5003",
            "candidate_status": "Decline",
            "candidate_type_when_applying": "External",
        },
        {
            "req_id": "REQ1004",
            "candidate_id": "CID5004",
            "candidate_status": "Withdrawed",
            "candidate_type_when_applying": "Internal",
        },
    ]

    pd.DataFrame(approved_rows).to_csv(approved_path, index=False)
    pd.DataFrame(decline_rows).to_csv(decline_path, index=False)

    print(f"Approved data created at: {approved_path}")
    print(f"Decline data created at: {decline_path}")


if __name__ == "__main__":
    # Example: last 3 days ending today.
    # Customize counts per day by date string.
    # files_per_day = {"2026-02-27": 2, "2026-02-28": 1, "2026-03-01": 1}
    create_dummy_data_for_last_n_days(days=3)
    create_dummy_approved_decline_files()
