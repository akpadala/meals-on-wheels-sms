"""
Google Sheets Service
Manages the two-tab structure for Questions and Client Responses
"""
import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]


class SheetsService:
    """Service for managing Google Sheets with two tabs"""

    def __init__(self):
        self.spreadsheet_id = os.getenv('SPREADSHEET_ID')
        if not self.spreadsheet_id:
            raise ValueError("SPREADSHEET_ID not found in environment variables")

        # Initialize Google Sheets client
        if os.getenv('GOOGLE_CREDENTIALS'):
            creds_dict = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
            creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        else:
            creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)

        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)

    def ensure_tabs_exist(self):
        """Ensure both required tabs exist"""
        try:
            # Try to get or create "Questions" tab
            try:
                questions_sheet = self.spreadsheet.worksheet("Questions")
                print("✓ 'Questions' tab already exists")
            except gspread.WorksheetNotFound:
                questions_sheet = self.spreadsheet.add_worksheet(title="Questions", rows=100, cols=10)
                self._setup_questions_tab(questions_sheet)
                print("✓ Created 'Questions' tab")

            # Try to get or create "Client Responses" tab
            try:
                responses_sheet = self.spreadsheet.worksheet("Client Responses")
                print("✓ 'Client Responses' tab already exists")
            except gspread.WorksheetNotFound:
                responses_sheet = self.spreadsheet.add_worksheet(title="Client Responses", rows=1000, cols=25)
                self._setup_responses_tab(responses_sheet)
                print("✓ Created 'Client Responses' tab")

            return questions_sheet, responses_sheet

        except Exception as e:
            print(f"Error ensuring tabs exist: {e}")
            raise

    def _setup_questions_tab(self, sheet):
        """Set up the Questions tab with headers and initial questions"""
        headers = [
            "Question ID",
            "Question Text",
            "Category",
            "Validation Type",
            "Required",
            "Order",
            "Active"
        ]

        # Sample questions
        questions = [
            ["Q1", "What is your full name? (Last Name, First Name)", "Personal Info", "name", "Yes", 1, "Yes"],
            ["Q2", "How old are you?", "Personal Info", "age", "Yes", 2, "Yes"],
            ["Q3", "What is your email address?", "Contact", "email", "Yes", 3, "Yes"],
            ["Q4", "What is your phone number?", "Contact", "phone", "Yes", 4, "Yes"],
            ["Q5", "What is your street address?", "Address", "address", "Yes", 5, "Yes"],
            ["Q6", "Apt/Unit number? (Type 'none' if not applicable)", "Address", "optional", "No", 6, "Yes"],
            ["Q7", "What city do you live in?", "Address", "text", "Yes", 7, "Yes"],
            ["Q8", "What state? (2-letter abbreviation)", "Address", "state", "Yes", 8, "Yes"],
            ["Q9", "What is your zip code?", "Address", "zip", "Yes", 9, "Yes"],
            ["Q10", "How did you hear about Meals on Wheels?", "Referral", "text", "Yes", 10, "Yes"],
            ["Q11", "Why are you requesting Meals on Wheels?", "Needs", "text", "Yes", 11, "Yes"],
            ["Q12", "Do you have any pets? (Yes/No)", "Safety", "yes_no", "Yes", 12, "Yes"],
            ["Q13", "What type of pet(s)?", "Safety", "text", "No", 13, "Yes"],
            ["Q14", "Do you own any weapons in your home? (Yes/No)", "Safety", "yes_no", "Yes", 14, "Yes"],
            ["Q15", "Emergency contact name? (Last Name, First Name)", "Emergency", "name", "Yes", 15, "Yes"],
            ["Q16", "Emergency contact phone number?", "Emergency", "phone", "Yes", 16, "Yes"],
        ]

        # Write headers
        sheet.update('A1:G1', [headers])

        # Format headers
        sheet.format('A1:G1', {
            "backgroundColor": {"red": 0.4, "green": 0.5, "blue": 0.9},
            "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
            "horizontalAlignment": "CENTER"
        })

        # Write questions
        sheet.update(f'A2:G{len(questions) + 1}', questions)

        print(f"✓ Set up Questions tab with {len(questions)} questions")

    def _setup_responses_tab(self, sheet):
        """Set up the Client Responses tab with headers"""
        headers = [
            "Timestamp",
            "Full Name",
            "Age",
            "Phone Number",
            "Email",
            "Street Address",
            "Apt/Unit",
            "City",
            "State",
            "Zip Code",
            "Referral Source",
            "Request Reason",
            "Has Pets",
            "Pet Details",
            "Has Weapons",
            "Emergency Contact Name",
            "Emergency Contact Phone",
            "Language Preference",
            "Eligibility Status",
            "Notes",
            "Conversation Stage",
            "AI Recommendation"
        ]

        # Write headers
        sheet.update('A1:V1', [headers])

        # Format headers
        sheet.format('A1:V1', {
            "backgroundColor": {"red": 0.2, "green": 0.7, "blue": 0.5},
            "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
            "horizontalAlignment": "CENTER"
        })

        # Freeze header row
        sheet.freeze(rows=1)

        print("✓ Set up Client Responses tab with headers")

    def save_client_response(self, client_data: Dict, ai_recommendation: Optional[str] = None):
        """Save a client response to the Client Responses tab"""
        try:
            sheet = self.spreadsheet.worksheet("Client Responses")

            row_data = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                client_data.get("full_name", ""),
                client_data.get("age", ""),
                client_data.get("phone_number", ""),
                client_data.get("email", ""),
                client_data.get("street_address", ""),
                client_data.get("apt_unit", ""),
                client_data.get("city", ""),
                client_data.get("state", ""),
                client_data.get("zip_code", ""),
                client_data.get("referral_source", ""),
                client_data.get("request_reason", ""),
                client_data.get("has_pets", ""),
                client_data.get("pet_details", ""),
                client_data.get("has_weapons", ""),
                client_data.get("emergency_contact_name", ""),
                client_data.get("emergency_contact_phone", ""),
                client_data.get("language_preference", "English"),
                client_data.get("eligibility_status", "pending"),
                client_data.get("notes", ""),
                client_data.get("conversation_stage", "completed"),
                ai_recommendation or ""
            ]

            sheet.append_row(row_data)
            print(f"✓ Saved response for {client_data.get('full_name', 'Unknown')}")

        except Exception as e:
            print(f"✗ Error saving client response: {e}")
            raise

    def get_questions(self) -> List[Dict]:
        """Get all active questions from the Questions tab"""
        try:
            sheet = self.spreadsheet.worksheet("Questions")
            records = sheet.get_all_records()

            # Filter for active questions and sort by order
            active_questions = [q for q in records if q.get("Active", "").lower() == "yes"]
            active_questions.sort(key=lambda x: x.get("Order", 999))

            return active_questions

        except Exception as e:
            print(f"✗ Error getting questions: {e}")
            return []


# Global sheets service instance
sheets_service = SheetsService()


# Initialize the tabs when module is imported
def initialize_sheets():
    """Initialize Google Sheets with required tabs"""
    try:
        sheets_service.ensure_tabs_exist()
        print("✓ Google Sheets initialized successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize sheets: {e}")


# Auto-initialize
initialize_sheets()
