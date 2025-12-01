#!/usr/bin/env python3
"""
Debug script to check Google Sheets structure and data
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

    print(f"📊 Spreadsheet: {spreadsheet.title}")
    print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
    print()

    # List all worksheets
    print("📋 Available Worksheets:")
    for i, worksheet in enumerate(spreadsheet.worksheets(), 1):
        print(f"  {i}. {worksheet.title} ({worksheet.row_count} rows, {worksheet.col_count} cols)")

        # Get row count with data
        all_values = worksheet.get_all_values()
        data_rows = len([row for row in all_values if any(cell.strip() for cell in row)])
        print(f"     └─ Rows with data: {data_rows}")

        # Show headers if they exist
        if all_values:
            headers = all_values[0]
            print(f"     └─ Headers: {', '.join(headers[:5])}{'...' if len(headers) > 5 else ''}")

            # Show last few entries
            if len(all_values) > 1:
                print(f"     └─ Data entries: {len(all_values) - 1} records")
                if len(all_values) > 1:
                    last_row = all_values[-1]
                    print(f"     └─ Last entry: {last_row[0] if last_row and last_row[0] else 'Empty'}")
        print()

if __name__ == "__main__":
    main()
