#!/usr/bin/env python3
"""
Check the exact column structure
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

    print("📋 Column Structure:\n")

    headers = main_sheet.row_values(1)

    print(f"Total columns: {len(headers)}\n")

    print("First 25 columns:")
    for i, header in enumerate(headers[:25], 1):
        if header.strip():
            print(f"  {i}. {header}")
        else:
            print(f"  {i}. [EMPTY]")

if __name__ == "__main__":
    main()
