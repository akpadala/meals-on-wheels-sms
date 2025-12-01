#!/usr/bin/env python3
"""
Check ALL columns to see what's there
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

    print("🔍 Checking ALL columns in the sheet:\n")

    # Get all values
    all_values = main_sheet.get_all_values()

    if not all_values:
        print("No data found!")
        return

    # Check header row
    headers = all_values[0]
    print(f"Total columns in sheet: {len(headers)}\n")

    # Find non-empty columns
    print("Non-empty columns in header row:")
    for i, header in enumerate(headers, 1):
        if header.strip():
            print(f"  Column {i}: {header[:50]}")

    print("\n" + "="*60)

    # Check a recent data row
    if len(all_values) > 1:
        print(f"\nChecking last data row (row {len(all_values)}):")
        last_row = all_values[-1]

        print(f"Total cells in last row: {len(last_row)}\n")

        print("Non-empty cells in last row:")
        for i, cell in enumerate(last_row, 1):
            if cell.strip():
                print(f"  Column {i}: {cell[:50]}")

if __name__ == "__main__":
    main()
