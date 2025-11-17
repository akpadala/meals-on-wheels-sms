"""
AI Conversation Handler
Manages the conversational flow for intake questions

TODO: Add OpenAI or Anthropic API integration once key is available
"""
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

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
        self.api_key = os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
        self.provider = None

        if os.getenv('OPENAI_API_KEY'):
            self.provider = "openai"
        elif os.getenv('ANTHROPIC_API_KEY'):
            self.provider = "anthropic"

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

        TODO: Add AI validation and adaptive follow-ups

        Returns:
            Dict with:
                - valid: bool
                - next_question: str or None
                - message: str (response to send)
        """
        current_index = session_data.get("current_question_index", 0)

        # Store the answer
        if current_index < len(INTAKE_QUESTIONS):
            question_data = INTAKE_QUESTIONS[current_index]
            session_data["answers"][question_data["key"]] = user_message

            # Move to next question
            session_data["current_question_index"] = current_index + 1

        # Get next question
        next_question = self.get_next_question(session_data)

        if next_question:
            return {
                "valid": True,
                "next_question": next_question,
                "message": f"Got it! {next_question}",
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

    def validate_answer(self, answer: str, validation_type: str) -> tuple[bool, Optional[str]]:
        """
        Validate user's answer

        TODO: Implement proper validation logic

        Returns:
            (is_valid, error_message)
        """
        # Basic validation - will be enhanced with AI
        if not answer or not answer.strip():
            return False, "Please provide an answer."

        return True, None


# Global AI handler instance
ai_handler = AIConversationHandler()
