"""
Session Manager for SMS Conversations
Stores conversation state for each phone number
"""
from typing import Dict, Optional, Any
from datetime import datetime
from enum import Enum

class ConversationStage(str, Enum):
    """Conversation stages"""
    NEW = "new"
    COLLECTING_INFO = "collecting_info"
    COMPLETED = "completed"
    ERROR = "error"

class SessionManager:
    """Manages conversation sessions for SMS clients"""

    def __init__(self):
        # In-memory storage: {phone_number: session_data}
        # For production, use Redis or a database
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, phone_number: str, initial_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a new session for a phone number"""
        session = {
            "phone_number": phone_number,
            "stage": ConversationStage.NEW,
            "started_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "messages": [],
            "collected_data": initial_data or {},
            "current_question_index": 0,
            "questions_asked": [],
            "answers": {}
        }
        self.sessions[phone_number] = session
        return session

    def get_session(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Get session for a phone number"""
        return self.sessions.get(phone_number)

    def update_session(self, phone_number: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update session data"""
        if phone_number not in self.sessions:
            self.create_session(phone_number)

        session = self.sessions[phone_number]
        session.update(updates)
        session["last_activity"] = datetime.now().isoformat()
        return session

    def add_message(self, phone_number: str, role: str, content: str):
        """Add a message to the conversation history"""
        if phone_number not in self.sessions:
            self.create_session(phone_number)

        message = {
            "role": role,  # "user" or "assistant"
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.sessions[phone_number]["messages"].append(message)
        self.sessions[phone_number]["last_activity"] = datetime.now().isoformat()

    def add_answer(self, phone_number: str, question: str, answer: str):
        """Record a question-answer pair"""
        if phone_number not in self.sessions:
            self.create_session(phone_number)

        self.sessions[phone_number]["answers"][question] = answer
        if question not in self.sessions[phone_number]["questions_asked"]:
            self.sessions[phone_number]["questions_asked"].append(question)

    def set_stage(self, phone_number: str, stage: ConversationStage):
        """Update conversation stage"""
        if phone_number not in self.sessions:
            self.create_session(phone_number)

        self.sessions[phone_number]["stage"] = stage
        self.sessions[phone_number]["last_activity"] = datetime.now().isoformat()

    def clear_session(self, phone_number: str):
        """Clear session for a phone number"""
        if phone_number in self.sessions:
            del self.sessions[phone_number]

    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get all active sessions"""
        return self.sessions

# Global session manager instance
session_manager = SessionManager()
