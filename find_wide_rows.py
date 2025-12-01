#!/usr/bin/env python3
"""
Find which rows have data extending beyond column 17
"""
import os
import json
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def main():
    # Load credentials
    creds_dict = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)

    # Open spreadsheet
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    spreadsheet = client.open_by_key(spreadsheet_id)
    main_sheet = spreadsheet.worksheet("Main Validation Sheet")

    print("🔍 Finding rows with data beyond column 17:\n")

    all_values = main_sheet.get_all_values()

    for row_num, row in enumerate(all_values, 1):
        # Check if there's any data beyond column 17
        data_beyond_17 = [cell for cell in row[17:] if cell.strip()]

        if data_beyond_17:
            # Find the rightmost non-empty column
            rightmost = 0
            for i, cell in enumerate(row):
                if cell.strip():
                    rightmost = i + 1

            print(f"Row {row_num}: Has data up to column {rightmost}")
            print(f"  Data beyond col 17: {len(data_beyond_17)} cells")

            # Show first few non-empty cells beyond 17
            shown = 0
            for i, cell in enumerate(row[17:], 18):
                if cell.strip() and shown < 3:
                    print(f"    Column {i}: {cell[:50]}")
                    shown += 1
            print()

if __name__ == "__main__":
    main()
