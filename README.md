# 🚀 Data Automation

Automated Python pipeline to process Offer Report ZIP files, extract candidate data, apply business rules, and generate filtered approval datasets.

---

## 📌 Project Overview

This project automates:
- Extracting the latest ZIP file from raw data folder
- Extracting CSV from ZIP
- Replacing Master Base Tracker
- Filtering candidates based on business logic
- Generating approval-ready dataset
- Avoiding duplicate approvals

The system is modular, scalable, and production-ready for future enhancements like Outlook integration and scheduling.

---

## 🏗 Project Structure

```
my_project/
├── data/
│  ├── raw_data/
│  │  └── YYYY-MM-DD/
│  │     ├── offer_report_1.zip
│  │     └── offer_report_2.zip
│  ├── master_base_tracker.csv
│  ├── offer_approved_data.csv
│  ├── offer_decline_data.csv
│  └── email_approval_data.csv
├── main.py
├── setup_dummy_data.py
├── requirements.txt
└── README.md
```

---

## 🔄 Process Flow

```
ZIP File (Raw Data)
↓
Extract Latest ZIP
↓
Replace Master Tracker
↓
Apply Business Filters
↓
Generate email_approval_data.csv
```

---

## 🧠 Business Logic

### Step 1 — Extract Latest ZIP
- Search recursively inside `data/raw_data/`
- Identify latest ZIP file (based on creation time)
- Extract CSV file

---

### Step 2 — Replace Master Base Tracker

Extracted CSV replaces:
```
data/master_base_tracker.csv
```

---

### Step 3 — Generate Email Approval Data

Filter Conditions:
- `candidate_status` must be `Offer` or `Offer In Process`
- `candidate_type_when_applying` must be `External`
- Primary Key: `req_id + candidate_id`
- Exclude records already present in `offer_approved_data.csv` and `offer_decline_data.csv`

Final output stored in:
```
data/email_approval_data.csv
```

---

## 📊 Data Schema

| Column Name | Description |
|-------------|------------|
| req_id | Requisition ID |
| candidate_id | Candidate Unique ID |
| candidate_status | Offer / Offer In Process / Decline / Withdrawed |
| candidate_type_when_applying | Internal / External |

---

## ⚙️ Setup Instructions

### 1️⃣ Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/bgv-offer-automation.git
```

---

### 2️⃣ Create Virtual Environment (Recommended)

Mac / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:
```bat
python -m venv venv
venv\\Scripts\\activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Generate Dummy Test Data

```bash
python setup_dummy_data.py
```

This creates:
```
data/raw_data/YYYY-MM-DD/offer_report_1.zip
```

---

### 5️⃣ Run Main Pipeline

```bash
python main.py
```

---

## 📁 Output Files

| File | Purpose |
|------|---------|
| master_base_tracker.csv | Latest extracted data |
| offer_approved_data.csv | Approved records (seeded by dummy data) |
| offer_decline_data.csv | Declined records (seeded by dummy data) |
| email_approval_data.csv | Filtered External Offer records |

---

## 🛠 Tech Stack

- Python 3.9+
- Pandas
- Zipfile
- Pathlib
- OS module

Optional (Future Outlook Integration):
- pywin32



## ⭐ Project Type

Internal automation project designed for scalable enterprise workflow automation.
