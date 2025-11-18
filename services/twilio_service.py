"""
Twilio SMS Service
Handles sending and receiving SMS messages
"""
import os
from typing import Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from dotenv import load_dotenv
import phonenumbers
from phonenumbers import NumberParseException

load_dotenv()

class TwilioService:
    """Service for sending and receiving SMS via Twilio"""

    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.phone_number = os.getenv('TWILIO_PHONE_NUMBER')

        if not all([self.account_sid, self.auth_token, self.phone_number]):
            raise ValueError("Missing Twilio credentials in environment variables")

        self.client = Client(self.account_sid, self.auth_token)

    def send_message(self, to_number: str, message: str) -> Optional[str]:
        """
        Send an SMS message to a phone number

        Args:
            to_number: Recipient phone number (E164 format: +1234567890)
            message: Message content

        Returns:
            Message SID if successful, None otherwise
        """
        try:
            # Validate and format phone number to E164
            formatted_number = self.validate_phone_number(to_number)

            message_obj = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=formatted_number
            )

            print(f"✓ SMS sent to {formatted_number}: {message_obj.sid}")
            return message_obj.sid

        except ValueError as e:
            print(f"✗ Invalid phone number {to_number}: {e}")
            return None
        except TwilioRestException as e:
            print(f"✗ Twilio error sending to {to_number}: {e}")
            return None
        except Exception as e:
            print(f"✗ Error sending SMS to {to_number}: {e}")
            return None

    def send_welcome_message(self, to_number: str, first_name: Optional[str] = None) -> Optional[str]:
        """Send a welcome message to start the conversation"""
        if first_name:
            message = f"Hi {first_name}! 👋 Welcome to Meals on Wheels Orange County. I'm here to help you get started. Let me ask you a few quick questions to see how we can assist you."
        else:
            message = "Welcome to Meals on Wheels Orange County! 👋 I'm here to help you get started. Let me ask you a few quick questions to see how we can assist you."

        return self.send_message(to_number, message)

    def validate_phone_number(self, phone_number: str) -> str:
        """
        Validate and format phone number to E164 format using phonenumbers library

        Args:
            phone_number: Phone number in any format

        Returns:
            E164 formatted phone number (+1234567890)

        Raises:
            ValueError: If phone number is invalid
        """
        try:
            # Parse the phone number (default to US region)
            parsed = phonenumbers.parse(phone_number, "US")

            # Validate the number
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError(f"Invalid phone number: {phone_number}")

            # Format to E164 (+1234567890)
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

        except NumberParseException as e:
            raise ValueError(f"Could not parse phone number '{phone_number}': {e}")

# Global Twilio service instance
twilio_service = TwilioService()
