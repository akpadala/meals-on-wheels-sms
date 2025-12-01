#!/usr/bin/env python3
"""
Check the actual contents of the last row
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

    print("📋 Checking last rows in Main Validation Sheet:\n")

    all_values = main_sheet.get_all_values()

    print(f"Total rows: {len(all_values)}")
    print(f"Total columns: {len(all_values[0]) if all_values else 0}")
    print()

    # Show last 5 rows
    print("Last 5 rows:")
    for i, row in enumerate(all_values[-5:], len(all_values) - 4):
        non_empty_cells = [cell for cell in row if cell.strip()]
        print(f"\nRow {i}: {len(non_empty_cells)} non-empty cells")
        if non_empty_cells:
            print(f"  First few values: {non_empty_cells[:5]}")
        else:
            print(f"  ALL EMPTY")

if __name__ == "__main__":
    main()
