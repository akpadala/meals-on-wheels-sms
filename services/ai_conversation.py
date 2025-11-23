"""
AI Conversation Handler
Manages the conversational flow for intake questions
"""
import os
import re
import logging
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import phonenumbers
from phonenumbers import NumberParseException
from openai import OpenAI

load_dotenv()

logger = logging.getLogger(__name__)

# Intake questions to collect from clients
INTAKE_QUESTIONS = [
    {
        "key": "full_name",
        "question": "What is your full name? (Please provide Last Name, First Name)",
        "validation": "name"
    },
    {
        "key": "age",
        "question": "How old are you?",
        "validation": "age"
    },
    {
        "key": "email",
        "question": "What is your email address?",
        "validation": "email"
    },
    {
        "key": "street_address",
        "question": "What is your street address?",
        "validation": "address"
    },
    {
        "key": "apt_unit",
        "question": "Do you have an apartment or unit number? (Type 'none' if not applicable)",
        "validation": "optional"
    },
    {
        "key": "city",
        "question": "What city do you live in?",
        "validation": "text"
    },
    {
        "key": "state",
        "question": "What state do you live in? (2-letter abbreviation, e.g., NC)",
        "validation": "state"
    },
    {
        "key": "zip_code",
        "question": "What is your zip code?",
        "validation": "zip"
    },
    {
        "key": "referral_source",
        "question": "How did you hear about Meals on Wheels?",
        "validation": "text"
    },
    {
        "key": "request_reason",
        "question": "Why are you requesting Meals on Wheels services?",
        "validation": "text"
    },
    {
        "key": "has_pets",
        "question": "Do you have any pets? (Yes/No)",
        "validation": "yes_no"
    },
    {
        "key": "pet_details",
        "question": "What type of pet(s) do you have?",
        "validation": "text",
        "conditional": "has_pets"
    },
    {
        "key": "has_weapons",
        "question": "Do you own any weapons in your home? (Yes/No)",
        "validation": "yes_no"
    },
    {
        "key": "emergency_contact_name",
        "question": "Who is your emergency contact? (Last Name, First Name)",
        "validation": "name"
    },
    {
        "key": "emergency_contact_phone",
        "question": "What is your emergency contact's phone number?",
        "validation": "phone"
    }
]


class AIConversationHandler:
    """Handles AI-powered conversation flow"""

    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.openai_client = None

        if self.openai_key:
            try:
                self.openai_client = OpenAI(api_key=self.openai_key)
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI client: {e}")

        self.use_ai = self.openai_client is not None

    def get_next_question(self, session_data: Dict) -> Optional[str]:
        """
        Get the next question to ask based on conversation state

        For now, uses simple sequential flow
        TODO: Replace with AI-powered adaptive questioning
        """
        answers = session_data.get("answers", {})
        current_index = session_data.get("current_question_index", 0)

        # Check if we've asked all questions
        if current_index >= len(INTAKE_QUESTIONS):
            return None

        # Get the next question
        question_data = INTAKE_QUESTIONS[current_index]

        # Handle conditional questions (e.g., pet details only if has pets)
        if "conditional" in question_data:
            conditional_key = question_data["conditional"]
            conditional_answer = answers.get(conditional_key, "").lower()

            # Skip if condition not met
            if conditional_answer not in ["yes", "y"]:
                session_data["current_question_index"] = current_index + 1
                return self.get_next_question(session_data)

        return question_data["question"]

    def process_response(self, user_message: str, session_data: Dict) -> Dict:
        """
        Process user's response and determine next action

        Returns:
            Dict with:
                - valid: bool
                - next_question: str or None
                - message: str (response to send)
                - completed: bool
        """
        current_index = session_data.get("current_question_index", 0)

        # Validate the answer if we're still collecting questions
        if current_index < len(INTAKE_QUESTIONS):
            question_data = INTAKE_QUESTIONS[current_index]
            validation_type = question_data.get("validation", "text")

            # Validate the answer with AI-enhanced feedback if available
            is_valid, error_message = self.ai_validate_with_help(
                user_message,
                question_data["question"],
                validation_type
            )

            if not is_valid:
                # Return error message without advancing
                return {
                    "valid": False,
                    "next_question": question_data["question"],
                    "message": error_message,
                    "completed": False
                }

            # Store the answer
            session_data["answers"][question_data["key"]] = user_message

            # Move to next question
            session_data["current_question_index"] = current_index + 1

        # Get next question
        next_question = self.get_next_question(session_data)

        if next_question:
            # Use AI to create a more conversational response
            if current_index < len(INTAKE_QUESTIONS):
                question_key = INTAKE_QUESTIONS[current_index - 1]["key"]
                response_message = self.ai_enhance_response(
                    user_message,
                    question_key,
                    next_question
                )
            else:
                response_message = f"Got it! {next_question}"

            return {
                "valid": True,
                "next_question": next_question,
                "message": response_message,
                "completed": False
            }
        else:
            return {
                "valid": True,
                "next_question": None,
                "message": "Thank you! I've collected all the information. We'll review your application and get back to you soon.",
                "completed": True
            }

    def handle_start_command(self, phone_number: str) -> str:
        """Handle when user texts 'START'"""
        first_question = INTAKE_QUESTIONS[0]["question"]
        return f"Welcome to Meals on Wheels Orange County! I'm here to help you get started. {first_question}"

    def ai_enhance_response(self, user_answer: str, question_key: str, next_question: str) -> str:
        """
        Use AI to create a more natural, conversational response

        Args:
            user_answer: The user's previous answer
            question_key: The key of the question just answered
            next_question: The next question to ask

        Returns:
            An AI-enhanced conversational response
        """
        if not self.use_ai:
            # Fallback to simple response
            return f"Got it! {next_question}"

        try:
            system_prompt = """You are a friendly, empathetic assistant helping seniors apply for Meals on Wheels services via SMS.
Your role is to acknowledge their previous answer briefly and naturally transition to the next question.
Keep responses SHORT (1-2 sentences max) and conversational.
Be warm but professional. Never ask for information they already provided."""

            user_prompt = f"""The user just answered about their {question_key.replace('_', ' ')}: "{user_answer}"

Now ask them: {next_question}

Create a brief, warm transition (1-2 sentences max) that acknowledges their answer and asks the next question naturally."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.warning(f"AI enhancement failed: {e}")
            # Fallback to simple response
            return f"Got it! {next_question}"

    def ai_validate_with_help(self, answer: str, question: str, validation_type: str) -> Tuple[bool, Optional[str]]:
        """
        Use AI to provide helpful validation feedback

        Args:
            answer: The user's answer
            question: The question being answered
            validation_type: The type of validation needed

        Returns:
            (is_valid, helpful_message)
        """
        # First try rule-based validation
        is_valid, error_message = self.validate_answer(answer, validation_type)

        if is_valid or not self.use_ai:
            return is_valid, error_message

        # If invalid and AI is available, enhance the error message
        try:
            system_prompt = """You are helping a senior citizen fill out a form via SMS. They provided an invalid answer.
Give them a SHORT, friendly explanation of what went wrong and how to fix it (1 sentence).
Be encouraging and simple. Don't be technical."""

            user_prompt = f"""Question: {question}
Their answer: "{answer}"
Validation type: {validation_type}
Error: {error_message}

Rewrite the error message to be friendlier and more helpful (1 short sentence)."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=60,
                temperature=0.7
            )

            friendly_error = response.choices[0].message.content.strip()
            return False, f"{friendly_error} {question}"

        except Exception as e:
            logger.warning(f"AI validation enhancement failed: {e}")
            return is_valid, f"{error_message} {question}"

    def validate_answer(self, answer: str, validation_type: str) -> Tuple[bool, Optional[str]]:
        """
        Validate user's answer based on the validation type

        Returns:
            (is_valid, error_message)
        """
        # Basic empty check
        if not answer or not answer.strip():
            return False, "Please provide an answer."

        answer = answer.strip()

        # Validation logic by type
        if validation_type == "email":
            # Email regex pattern
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, answer):
                return False, "Please provide a valid email address (e.g., john@example.com)."

        elif validation_type == "phone":
            # Phone number validation using phonenumbers library
            try:
                parsed = phonenumbers.parse(answer, "US")
                if not phonenumbers.is_valid_number(parsed):
                    return False, "Please provide a valid phone number (e.g., 555-123-4567 or (555) 123-4567)."
            except NumberParseException:
                return False, "Please provide a valid phone number (e.g., 555-123-4567 or (555) 123-4567)."

        elif validation_type == "age":
            # Age must be a number between 18 and 120
            try:
                age = int(answer)
                if age < 18 or age > 120:
                    return False, "Age must be between 18 and 120."
            except ValueError:
                return False, "Please provide your age as a number."

        elif validation_type == "zip":
            # Zip code: 5 digits or 5+4 format
            if not re.match(r'^\d{5}(-\d{4})?$', answer):
                return False, "Please provide a valid zip code (e.g., 12345 or 12345-6789)."

        elif validation_type == "state":
            # State abbreviation: 2 uppercase letters
            us_states = {
                'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
                'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
                'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
                'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
                'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
            }
            if answer.upper() not in us_states:
                return False, "Please provide a valid 2-letter state abbreviation (e.g., NC, CA, NY)."

        elif validation_type == "name":
            # Name should have at least 2 characters and contain letters
            if len(answer) < 2:
                return False, "Name must be at least 2 characters long."
            if not re.search(r'[a-zA-Z]', answer):
                return False, "Name must contain at least one letter."

        elif validation_type == "yes_no":
            # Yes/No validation
            answer_lower = answer.lower()
            if answer_lower not in ['yes', 'y', 'no', 'n']:
                return False, "Please answer 'Yes' or 'No'."

        elif validation_type == "text":
            # General text: at least 2 characters
            if len(answer) < 2:
                return False, "Please provide at least 2 characters."

        elif validation_type == "address":
            # Address should have street number and name
            if len(answer) < 5:
                return False, "Please provide a complete street address."
            if not re.search(r'\d', answer):
                return False, "Address should include a street number."

        elif validation_type == "optional":
            # Optional fields always valid
            pass

        return True, None


# Global AI handler instance
ai_handler = AIConversationHandler()
