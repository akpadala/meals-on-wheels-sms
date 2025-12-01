#!/usr/bin/env python3
"""
Check data in Main Validation Sheet
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

    # Get Main Validation Sheet
    main_sheet = spreadsheet.worksheet("Main Validation Sheet")
    print("📋 Main Validation Sheet Data:\n")

    all_values = main_sheet.get_all_values()

    if all_values:
        headers = all_values[0]
        print(f"Headers ({len(headers)} columns):")
        for i, header in enumerate(headers[:22], 1):
            if header.strip():
                print(f"  {i}. {header}")
        print()

        print(f"Data Records: {len(all_values) - 1}")
        print()

        # Show all data entries
        for i, row in enumerate(all_values[1:], 1):
            if any(cell.strip() for cell in row):
                print(f"Record {i}:")
                print(f"  Timestamp: {row[0] if len(row) > 0 else 'N/A'}")
                print(f"  Name: {row[1] if len(row) > 1 else 'N/A'}")
                print(f"  Phone: {row[3] if len(row) > 3 else 'N/A'}")
                print(f"  Email: {row[4] if len(row) > 4 else 'N/A'}")
                print()

if __name__ == "__main__":
    main()
