import os
import zipfile
import pandas as pd
from pathlib import Path
from datetime import datetime

# ==============================
# CONFIGURATION
# ==============================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw_data" / datetime.today().strftime("%Y-%m-%d")

MASTER_FILE = DATA_DIR / "master_base_tracker.csv"
APPROVED_FILE = DATA_DIR / "offer_approved_data.csv"
DECLINE_FILE = DATA_DIR / "offer_decline_data.csv"
EMAIL_APPROVAL_FILE = DATA_DIR / "email_approval_data.csv"

# ==============================
# INITIAL FILE SETUP
# ==============================

def initialize_files():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not MASTER_FILE.exists():
        pd.DataFrame().to_csv(MASTER_FILE, index=False)

    if not APPROVED_FILE.exists():
        pd.DataFrame(columns=["req_id", "candidate_id"]).to_csv(APPROVED_FILE, index=False)

    if not DECLINE_FILE.exists():
        pd.DataFrame(columns=["req_id", "candidate_id"]).to_csv(DECLINE_FILE, index=False)

    if not EMAIL_APPROVAL_FILE.exists():
        pd.DataFrame().to_csv(EMAIL_APPROVAL_FILE, index=False)


# ==============================
# STEP 1 — Extract ZIP
# ==============================

def extract_latest_zip():
    raw_base_dir = DATA_DIR / "raw_data"

    if not raw_base_dir.exists():
        raise FileNotFoundError(f"raw_data folder does not exist: {raw_base_dir}")

    # Get all zip files recursively
    zip_files = list(raw_base_dir.rglob("*.zip"))

    if not zip_files:
        raise FileNotFoundError(f"No ZIP files found in: {raw_base_dir}")

    # Get latest by creation time
    latest_zip = max(zip_files, key=os.path.getctime)

    extract_folder = latest_zip.parent

    with zipfile.ZipFile(latest_zip, 'r') as z:
        z.extractall(extract_folder)

    # Find extracted csv
    extracted_csvs = list(extract_folder.glob("*.csv"))

    if not extracted_csvs:
        raise FileNotFoundError(f"No CSV found after extracting: {latest_zip}")

    latest_csv = max(extracted_csvs, key=os.path.getctime)

    print(f"Latest ZIP selected: {latest_zip}")
    print(f"Extracted CSV: {latest_csv}")

    return latest_csv

# ==============================
# STEP 2 — Replace Master Tracker
# ==============================

def replace_master_data(csv_path):
    df = pd.read_csv(csv_path)
    df.to_csv(MASTER_FILE, index=False)
    print("Master base tracker replaced.")


# ==============================
# STEP 3 — Filter Email Approval Data
# Condition:
# - candidate_status in (Offer, Offer In Process)
# - candidate_type_when_applying = External
# - Not already in approved or decline file
# ==============================

def _safe_read_csv(path, required_cols=None, default_cols=None):
    if not path.exists():
        if default_cols is None:
            return pd.DataFrame()
        return pd.DataFrame(columns=default_cols)
    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=default_cols or [])

    if required_cols:
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise KeyError(f"Missing columns in {path}: {missing}")
    return df


def generate_email_approval_data():
    master_required = [
        "req_id",
        "candidate_id",
        "candidate_status",
        "candidate_type_when_applying",
    ]
    master_df = _safe_read_csv(MASTER_FILE, required_cols=master_required)
    approved_df = _safe_read_csv(APPROVED_FILE, default_cols=["req_id", "candidate_id"])
    decline_df = _safe_read_csv(DECLINE_FILE, default_cols=["req_id", "candidate_id"])

    # Filter conditions
    filtered = master_df[
        (master_df["candidate_status"].isin(["Offer", "Offer In Process"])) &
        (master_df["candidate_type_when_applying"] == "External")
    ].copy()

    # Create primary key
    filtered["pk"] = filtered["req_id"].astype(str) + "_" + filtered["candidate_id"].astype(str)

    approved_df["pk"] = approved_df["req_id"].astype(str) + "_" + approved_df["candidate_id"].astype(str)
    decline_df["pk"] = decline_df["req_id"].astype(str) + "_" + decline_df["candidate_id"].astype(str)

    existing_pks = set(approved_df["pk"]).union(set(decline_df["pk"]))

    final_df = filtered[~filtered["pk"].isin(existing_pks)]

    final_df = final_df.drop(columns=["pk"])

    final_df.to_csv(EMAIL_APPROVAL_FILE, index=False)

    print("Email approval data generated.")


# ==============================
# FUTURE FUNCTION — FETCH FROM OUTLOOK
# (Currently commented as requested)
# ==============================

"""
def fetch_from_outlook():
    import win32com.client

    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    inbox = outlook.GetDefaultFolder(6)

    for mail in inbox.Items:
        if mail.SenderEmailAddress == "ta.natucalcesoucces@adani.com":
            if "Offer Report Including AP Plus" in mail.Subject:
                for attachment in mail.Attachments:
                    save_path = RAW_DIR / attachment.FileName
                    attachment.SaveAsFile(str(save_path))
                    print(f"Saved attachment: {save_path}")
"""

# ==============================
# MAIN EXECUTION
# ==============================

def main():
    try:
        initialize_files()

        csv_path = extract_latest_zip()
        replace_master_data(csv_path)
        generate_email_approval_data()

        print("Pipeline completed successfully.")
    except Exception as exc:
        print(f"Pipeline failed: {exc}")


if __name__ == "__main__":
    main()
