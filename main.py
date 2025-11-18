from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import json
import logging
import traceback
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our services
from services.twilio_service import twilio_service
from services.session_manager import session_manager, ConversationStage
from services.ai_conversation import ai_handler

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="MOWOC SMS Intake System",
    description="API for managing Meals on Wheels client intake via SMS",
    version="1.0.0"
)

# Configure CORS origins from environment variable
# For development: CORS_ORIGINS="http://localhost:3000,http://localhost:8000"
# For production: Set to your actual domain(s)
cors_origins_str = os.getenv("CORS_ORIGINS", "*")
allowed_origins = cors_origins_str.split(",") if cors_origins_str != "*" else ["*"]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

logger.info(f"CORS configured with origins: {allowed_origins}")

# Google Sheets setup
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Initialize Google Sheets client
def get_sheets_client():
    """Initialize and return Google Sheets client"""
    if os.getenv('GOOGLE_CREDENTIALS'):
        creds_dict = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    return gspread.authorize(creds)

def get_worksheet():
    """Get the Main Validation Sheet worksheet"""
    try:
        client = get_sheets_client()
        spreadsheet_id = os.getenv('SPREADSHEET_ID')
        if not spreadsheet_id:
            raise ValueError("SPREADSHEET_ID environment variable not set")
        spreadsheet = client.open_by_key(spreadsheet_id)
        return spreadsheet.worksheet("Main Validation Sheet")
    except Exception as e:
        print(f"Error opening worksheet: {str(e)}")
        raise

# Pydantic models matching your exact sheet schema
class ClientData(BaseModel):
    """Complete client data model matching Google Sheet columns"""
    full_name: str = Field(..., description="Full Name (Last Name, First Name)")
    age: int = Field(..., description="Age")
    phone_number: str = Field(..., description="Phone Number (E.g. 1234567890)")
    email: str = Field(..., description="Email")
    street_address: str = Field(..., description="Street Address")
    apt_unit: Optional[str] = Field(None, description="Apt / Unit / Secondary (optional)")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State")
    zip_code: str = Field(..., description="Zip Code")
    referral_source: str = Field(..., description="How did you hear about Meals on Wheels?")
    request_reason: str = Field(..., description="Why are you requesting Meals on Wheels?")
    has_pets: str = Field(..., description="Do you have any pets?")
    pet_details: Optional[str] = Field(None, description="If yes, specify type of pet(s)")
    has_weapons: str = Field(..., description="Do you own any weapons in your home?")
    emergency_contact_name: str = Field(..., description="Emergency Contact Name (Last Name, First Name)")
    emergency_contact_phone: str = Field(..., description="Emergency Contact Phone (E.g. 1234567890)")
    # Optional tracking fields
    language_preference: Optional[str] = "English"
    eligibility_status: Optional[str] = "pending"
    notes: Optional[str] = None
    conversation_stage: Optional[str] = "new"

class ClientUpdate(BaseModel):
    """Model for updating client - requires email AND phone for verification"""
    email: str = Field(..., description="Email to find the client")
    phone_number: str = Field(..., description="Phone number to verify identity")
    updates: Dict[str, Any] = Field(..., description="Fields to update with their new values")

class ClientResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

# API Routes

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the intake form"""
    try:
        with open("templates/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return {"status": "online", "service": "MOWOC SMS Intake API"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "online", "service": "MOWOC SMS Intake API"}

@app.post("/api/clients/create", response_model=ClientResponse)
async def create_client(client: ClientData):
    """
    Create a new client record in Google Sheets
    
    Creates a new row with all client information
    """
    try:
        sheet = get_worksheet()
        
        # Get current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Prepare row data matching exact sheet column order
        row_data = [
            timestamp,                              # Column 1: Timestamp
            client.full_name,                       # Column 2: Full Name
            client.age,                             # Column 3: Age
            client.phone_number,                    # Column 4: Phone Number
            client.email,                           # Column 5: Email
            client.street_address,                  # Column 6: Street Address
            client.apt_unit or "",                  # Column 7: Apt/Unit (optional)
            client.city,                            # Column 8: City
            client.state,                           # Column 9: State
            client.zip_code,                        # Column 10: Zip Code
            client.referral_source,                 # Column 11: Referral Source
            client.request_reason,                  # Column 12: Request Reason
            client.has_pets,                        # Column 13: Has Pets
            client.pet_details or "",               # Column 14: Pet Details
            client.has_weapons,                     # Column 15: Has Weapons
            client.emergency_contact_name,          # Column 16: Emergency Contact Name
            client.emergency_contact_phone,         # Column 17: Emergency Contact Phone
            client.language_preference or "English", # Column 18: Language Preference
            client.eligibility_status or "pending",  # Column 19: Eligibility Status
            client.notes or "",                     # Column 20: Notes
            client.conversation_stage or "new"      # Column 21: Conversation Stage
        ]
        
        # Append to sheet
        sheet.append_row(row_data)
        
        return ClientResponse(
            success=True,
            message="Client created successfully",
            data={
                "email": client.email,
                "phone_number": client.phone_number,
                "full_name": client.full_name,
                "timestamp": timestamp
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating client: {str(e)}")

@app.get("/api/clients/{email}", response_model=ClientResponse)
async def get_client_by_email(email: str):
    """
    Get client data by email address
    
    Searches for the client using their email and returns all their information
    """
    try:
        sheet = get_worksheet()
        
        # Find the client by email (column 5)
        cell = sheet.find(email)
        
        if not cell:
            raise HTTPException(status_code=404, detail=f"Client with email '{email}' not found")
        
        # Get the entire row
        row_data = sheet.row_values(cell.row)
        
        # Map to readable format based on your sheet structure
        client_data = {
            "timestamp": row_data[0] if len(row_data) > 0 else None,
            "full_name": row_data[1] if len(row_data) > 1 else None,
            "age": row_data[2] if len(row_data) > 2 else None,
            "phone_number": row_data[3] if len(row_data) > 3 else None,
            "email": row_data[4] if len(row_data) > 4 else None,
            "street_address": row_data[5] if len(row_data) > 5 else None,
            "apt_unit": row_data[6] if len(row_data) > 6 else None,
            "city": row_data[7] if len(row_data) > 7 else None,
            "state": row_data[8] if len(row_data) > 8 else None,
            "zip_code": row_data[9] if len(row_data) > 9 else None,
            "referral_source": row_data[10] if len(row_data) > 10 else None,
            "request_reason": row_data[11] if len(row_data) > 11 else None,
            "has_pets": row_data[12] if len(row_data) > 12 else None,
            "pet_details": row_data[13] if len(row_data) > 13 else None,
            "has_weapons": row_data[14] if len(row_data) > 14 else None,
            "emergency_contact_name": row_data[15] if len(row_data) > 15 else None,
            "emergency_contact_phone": row_data[16] if len(row_data) > 16 else None,
            "language_preference": row_data[17] if len(row_data) > 17 else None,
            "eligibility_status": row_data[18] if len(row_data) > 18 else None,
            "notes": row_data[19] if len(row_data) > 19 else None,
            "conversation_stage": row_data[20] if len(row_data) > 20 else None,
        }
        
        return ClientResponse(
            success=True,
            message="Client retrieved successfully",
            data=client_data
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving client: {str(e)}")

@app.put("/api/clients/update", response_model=ClientResponse)
async def update_client(update: ClientUpdate):
    """
    Update client information using email and phone number for verification
    
    Requires both email and phone number to match for security.
    Updates the entire row with provided fields.
    
    Example request body:
    {
        "email": "john@example.com",
        "phone_number": "9195551234",
        "updates": {
            "full_name": "Doe, John",
            "age": 73,
            "eligibility_status": "eligible",
            "notes": "Approved for meal delivery"
        }
    }
    """
    try:
        sheet = get_worksheet()
        
        # Find the client by email (column 5)
        email_cell = sheet.find(update.email)
        
        if not email_cell:
            raise HTTPException(status_code=404, detail=f"Client with email '{update.email}' not found")
        
        # Get the row data to verify phone number
        row_data = sheet.row_values(email_cell.row)
        stored_phone = row_data[3] if len(row_data) > 3 else None
        
        # Verify phone number matches (security check)
        if stored_phone != update.phone_number:
            raise HTTPException(
                status_code=403, 
                detail="Phone number does not match the email. Both must match to update."
            )
        
        # Column mapping based on your sheet structure
        column_map = {
            "full_name": 2,
            "age": 3,
            "phone_number": 4,
            "email": 5,
            "street_address": 6,
            "apt_unit": 7,
            "city": 8,
            "state": 9,
            "zip_code": 10,
            "referral_source": 11,
            "request_reason": 12,
            "has_pets": 13,
            "pet_details": 14,
            "has_weapons": 15,
            "emergency_contact_name": 16,
            "emergency_contact_phone": 17,
            "language_preference": 18,
            "eligibility_status": 19,
            "notes": 20,
            "conversation_stage": 21
        }
        
        # Update each field
        updated_fields = []
        for field, value in update.updates.items():
            if field in column_map:
                col = column_map[field]
                sheet.update_cell(email_cell.row, col, value)
                updated_fields.append(field)
            else:
                print(f"Warning: Field '{field}' not found in column mapping")
        
        return ClientResponse(
            success=True,
            message=f"Client updated successfully. Updated {len(updated_fields)} field(s).",
            data={
                "email": update.email,
                "phone_number": update.phone_number,
                "updated_fields": updated_fields,
                "updates": update.updates
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating client: {str(e)}")

@app.post("/sms-webhook")
async def sms_webhook(From: str = Form(...), Body: str = Form(...)):
    """
    Twilio webhook endpoint for receiving SMS messages

    Twilio sends: From (phone number), Body (message text)
    """
    phone_number = None
    response_message = "We're sorry, something went wrong. Please try again later or call us directly."

    try:
        phone_number = From
        user_message = Body.strip()

        logger.info(f"📱 Received SMS from {phone_number}: {user_message[:50]}...")

        # Validate inputs
        if not phone_number or not user_message:
            logger.error("Missing phone number or message body")
            return Response(
                content="<?xml version='1.0' encoding='UTF-8'?><Response></Response>",
                media_type="application/xml"
            )

        # Get or create session
        session = session_manager.get_session(phone_number)

        # Handle START command or new conversation
        if user_message.upper() == "START" or not session:
            logger.info(f"Starting new conversation for {phone_number}")
            session = session_manager.create_session(phone_number)
            session_manager.set_stage(phone_number, ConversationStage.COLLECTING_INFO)
            response_message = ai_handler.handle_start_command(phone_number)

        else:
            # Add user message to session
            session_manager.add_message(phone_number, "user", user_message)

            # Process the response with AI
            try:
                result = ai_handler.process_response(user_message, session)

                if result["completed"]:
                    # Save to Google Sheets
                    try:
                        await save_conversation_to_sheets(phone_number, session)
                        response_message = result["message"]
                        session_manager.set_stage(phone_number, ConversationStage.COMPLETED)
                        logger.info(f"✅ Completed conversation for {phone_number}")
                    except gspread.exceptions.APIError as e:
                        logger.error(f"Google Sheets API error for {phone_number}: {e}")
                        response_message = "Thank you for providing your information. We'll review it and be in touch soon!"
                        session_manager.set_stage(phone_number, ConversationStage.ERROR)
                    except Exception as e:
                        logger.error(f"Error saving to sheets for {phone_number}: {e}")
                        traceback.print_exc()
                        response_message = "Thank you for providing your information. We'll be in touch soon!"
                        session_manager.set_stage(phone_number, ConversationStage.ERROR)
                else:
                    response_message = result["message"]

            except Exception as e:
                logger.error(f"Error processing response for {phone_number}: {e}")
                traceback.print_exc()
                response_message = "I didn't quite understand that. Could you please try again?"

        # Add assistant message to session
        try:
            session_manager.add_message(phone_number, "assistant", response_message)
        except Exception as e:
            logger.error(f"Error adding message to session for {phone_number}: {e}")

        # Send SMS response
        try:
            twilio_service.send_message(phone_number, response_message)
            logger.info(f"✅ Sent response to {phone_number}")
        except Exception as e:
            logger.error(f"Error sending SMS to {phone_number}: {e}")
            # Don't fail the request if SMS send fails
            # Twilio will handle retries

        # Return TwiML response (Twilio expects this)
        return Response(
            content="<?xml version='1.0' encoding='UTF-8'?><Response></Response>",
            media_type="application/xml"
        )

    except Exception as e:
        logger.error(f"❌ Critical error in SMS webhook: {e}")
        traceback.print_exc()

        # Try to send error message to user if we have their number
        if phone_number:
            try:
                twilio_service.send_message(
                    phone_number,
                    "We're experiencing technical difficulties. Please try again in a few minutes."
                )
            except Exception:
                pass  # Fail silently if we can't send error message

        # Always return valid TwiML to Twilio
        return Response(
            content="<?xml version='1.0' encoding='UTF-8'?><Response></Response>",
            media_type="application/xml"
        )


async def save_conversation_to_sheets(phone_number: str, session: Dict):
    """Save completed conversation to Google Sheets"""
    answers = session.get("answers", {})

    # Map answers to ClientData format
    client_data = ClientData(
        full_name=answers.get("full_name", ""),
        age=int(answers.get("age", 0)) if answers.get("age", "").isdigit() else 0,
        phone_number=phone_number,
        email=answers.get("email", ""),
        street_address=answers.get("street_address", ""),
        apt_unit=answers.get("apt_unit") if answers.get("apt_unit", "").lower() != "none" else None,
        city=answers.get("city", ""),
        state=answers.get("state", ""),
        zip_code=answers.get("zip_code", ""),
        referral_source=answers.get("referral_source", ""),
        request_reason=answers.get("request_reason", ""),
        has_pets=answers.get("has_pets", ""),
        pet_details=answers.get("pet_details") if answers.get("has_pets", "").lower() in ["yes", "y"] else None,
        has_weapons=answers.get("has_weapons", ""),
        emergency_contact_name=answers.get("emergency_contact_name", ""),
        emergency_contact_phone=answers.get("emergency_contact_phone", ""),
        conversation_stage="completed"
    )

    # Use existing create_client endpoint logic
    sheet = get_worksheet()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    row_data = [
        timestamp,
        client_data.full_name,
        client_data.age,
        client_data.phone_number,
        client_data.email,
        client_data.street_address,
        client_data.apt_unit or "",
        client_data.city,
        client_data.state,
        client_data.zip_code,
        client_data.referral_source,
        client_data.request_reason,
        client_data.has_pets,
        client_data.pet_details or "",
        client_data.has_weapons,
        client_data.emergency_contact_name,
        client_data.emergency_contact_phone,
        client_data.language_preference or "English",
        client_data.eligibility_status or "pending",
        client_data.notes or "",
        client_data.conversation_stage or "completed"
    ]

    sheet.append_row(row_data)
    print(f"✓ Saved conversation for {phone_number} to Google Sheets")


@app.post("/api/web-form-submit", response_model=ClientResponse)
async def web_form_submit(client: ClientData):
    """
    Handle web form submission and optionally start SMS conversation

    This endpoint:
    1. Saves client data to Google Sheets
    2. Optionally sends a welcome SMS to start the conversation
    """
    try:
        # Create client in Google Sheets
        result = await create_client(client)

        # Create a session for this client
        session_manager.create_session(
            client.phone_number,
            initial_data={
                "full_name": client.full_name,
                "email": client.email,
                "source": "web_form"
            }
        )

        # Send welcome SMS
        welcome_msg = f"Hi! Thank you for submitting the form. We'll follow up with you shortly to complete your intake. Reply START to begin the conversation now."
        twilio_service.send_message(client.phone_number, welcome_msg)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing web form: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)