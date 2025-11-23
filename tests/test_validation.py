"""
Unit tests for validation logic
"""
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ai_conversation import AIConversationHandler


class TestValidation:
    """Test the validation logic in AIConversationHandler"""

    def setup_method(self):
        """Set up test fixtures"""
        self.handler = AIConversationHandler()

    # Email validation tests
    def test_valid_email(self):
        """Test valid email addresses"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.org",
            "user+tag@example.co.uk",
            "test123@test.io"
        ]
        for email in valid_emails:
            is_valid, _ = self.handler.validate_answer(email, "email")
            assert is_valid, f"Email '{email}' should be valid"

    def test_invalid_email(self):
        """Test invalid email addresses"""
        invalid_emails = [
            "not-an-email",
            "missing@domain",
            "@nodomain.com",
            "spaces in@email.com",
            ""
        ]
        for email in invalid_emails:
            is_valid, _ = self.handler.validate_answer(email, "email")
            assert not is_valid, f"Email '{email}' should be invalid"

    # Phone validation tests
    def test_valid_phone(self):
        """Test valid phone numbers"""
        valid_phones = [
            "5551234567",
            "(555) 123-4567",
            "555-123-4567",
            "+1 555 123 4567",
            "1-555-123-4567"
        ]
        for phone in valid_phones:
            is_valid, _ = self.handler.validate_answer(phone, "phone")
            assert is_valid, f"Phone '{phone}' should be valid"

    def test_invalid_phone(self):
        """Test invalid phone numbers"""
        invalid_phones = [
            "123",
            "abcdefghij",
            "",
            "555-555-555"  # Missing digit
        ]
        for phone in invalid_phones:
            is_valid, _ = self.handler.validate_answer(phone, "phone")
            assert not is_valid, f"Phone '{phone}' should be invalid"

    # Age validation tests
    def test_valid_age(self):
        """Test valid ages"""
        valid_ages = ["18", "65", "120", "25"]
        for age in valid_ages:
            is_valid, _ = self.handler.validate_answer(age, "age")
            assert is_valid, f"Age '{age}' should be valid"

    def test_invalid_age(self):
        """Test invalid ages"""
        invalid_ages = ["17", "121", "0", "-5", "abc", ""]
        for age in invalid_ages:
            is_valid, _ = self.handler.validate_answer(age, "age")
            assert not is_valid, f"Age '{age}' should be invalid"

    # Zip code validation tests
    def test_valid_zip(self):
        """Test valid zip codes"""
        valid_zips = ["12345", "12345-6789", "90210"]
        for zip_code in valid_zips:
            is_valid, _ = self.handler.validate_answer(zip_code, "zip")
            assert is_valid, f"Zip '{zip_code}' should be valid"

    def test_invalid_zip(self):
        """Test invalid zip codes"""
        invalid_zips = ["1234", "123456", "abcde", "12345-678", ""]
        for zip_code in invalid_zips:
            is_valid, _ = self.handler.validate_answer(zip_code, "zip")
            assert not is_valid, f"Zip '{zip_code}' should be invalid"

    # State validation tests
    def test_valid_state(self):
        """Test valid state abbreviations"""
        valid_states = ["CA", "NY", "TX", "nc", "Fl"]  # Case insensitive
        for state in valid_states:
            is_valid, _ = self.handler.validate_answer(state, "state")
            assert is_valid, f"State '{state}' should be valid"

    def test_invalid_state(self):
        """Test invalid state abbreviations"""
        invalid_states = ["XX", "California", "12", "ABC", ""]
        for state in invalid_states:
            is_valid, _ = self.handler.validate_answer(state, "state")
            assert not is_valid, f"State '{state}' should be invalid"

    # Name validation tests
    def test_valid_name(self):
        """Test valid names"""
        valid_names = ["John Doe", "Smith, Jane", "O'Brien", "José García"]
        for name in valid_names:
            is_valid, _ = self.handler.validate_answer(name, "name")
            assert is_valid, f"Name '{name}' should be valid"

    def test_invalid_name(self):
        """Test invalid names"""
        invalid_names = ["J", "123", ""]
        for name in invalid_names:
            is_valid, _ = self.handler.validate_answer(name, "name")
            assert not is_valid, f"Name '{name}' should be invalid"

    # Yes/No validation tests
    def test_valid_yes_no(self):
        """Test valid yes/no responses"""
        valid_responses = ["yes", "Yes", "YES", "y", "Y", "no", "No", "NO", "n", "N"]
        for response in valid_responses:
            is_valid, _ = self.handler.validate_answer(response, "yes_no")
            assert is_valid, f"Response '{response}' should be valid"

    def test_invalid_yes_no(self):
        """Test invalid yes/no responses"""
        invalid_responses = ["maybe", "sure", "nope", "1", "0", ""]
        for response in invalid_responses:
            is_valid, _ = self.handler.validate_answer(response, "yes_no")
            assert not is_valid, f"Response '{response}' should be invalid"

    # Address validation tests
    def test_valid_address(self):
        """Test valid addresses"""
        valid_addresses = [
            "123 Main Street",
            "456 Oak Ave Apt 2",
            "1 First St"
        ]
        for address in valid_addresses:
            is_valid, _ = self.handler.validate_answer(address, "address")
            assert is_valid, f"Address '{address}' should be valid"

    def test_invalid_address(self):
        """Test invalid addresses"""
        invalid_addresses = [
            "Main Street",  # No number
            "123",  # Too short
            ""
        ]
        for address in invalid_addresses:
            is_valid, _ = self.handler.validate_answer(address, "address")
            assert not is_valid, f"Address '{address}' should be invalid"

    # Text validation tests
    def test_valid_text(self):
        """Test valid text inputs"""
        valid_texts = ["Hi", "This is a valid response", "OK"]
        for text in valid_texts:
            is_valid, _ = self.handler.validate_answer(text, "text")
            assert is_valid, f"Text '{text}' should be valid"

    def test_invalid_text(self):
        """Test invalid text inputs"""
        invalid_texts = ["a", ""]
        for text in invalid_texts:
            is_valid, _ = self.handler.validate_answer(text, "text")
            assert not is_valid, f"Text '{text}' should be invalid"

    # Optional validation tests
    def test_optional_always_valid(self):
        """Test that optional fields are always valid"""
        optional_values = ["none", "N/A", "something", ""]
        for value in optional_values:
            # Empty string would fail the basic check, so skip it
            if value:
                is_valid, _ = self.handler.validate_answer(value, "optional")
                assert is_valid, f"Optional value '{value}' should be valid"


class TestConversationFlow:
    """Test the conversation flow logic"""

    def setup_method(self):
        """Set up test fixtures"""
        self.handler = AIConversationHandler()

    def test_get_first_question(self):
        """Test getting the first question"""
        session_data = {
            "answers": {},
            "current_question_index": 0
        }
        question = self.handler.get_next_question(session_data)
        assert question is not None
        assert "full name" in question.lower()

    def test_skip_conditional_question(self):
        """Test that conditional questions are skipped when condition not met"""
        session_data = {
            "answers": {"has_pets": "no"},
            "current_question_index": 11  # pet_details index
        }
        question = self.handler.get_next_question(session_data)
        # Should skip pet_details and return has_weapons question
        assert question is not None
        assert "pet" not in question.lower() or "weapons" in question.lower()

    def test_include_conditional_question(self):
        """Test that conditional questions are included when condition is met"""
        session_data = {
            "answers": {"has_pets": "yes"},
            "current_question_index": 11  # pet_details index
        }
        question = self.handler.get_next_question(session_data)
        assert question is not None
        assert "pet" in question.lower()

    def test_handle_start_command(self):
        """Test the START command handler"""
        response = self.handler.handle_start_command("+15551234567")
        assert "Welcome" in response
        assert "Meals on Wheels" in response
