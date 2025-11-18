"""
Session Manager for SMS Conversations
Stores conversation state for each phone number with file-based persistence
"""
from typing import Dict, Optional, Any
from datetime import datetime
from enum import Enum
import json
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ConversationStage(str, Enum):
    """Conversation stages"""
    NEW = "new"
    COLLECTING_INFO = "collecting_info"
    COMPLETED = "completed"
    ERROR = "error"

class SessionManager:
    """Manages conversation sessions for SMS clients with file-based persistence"""

    def __init__(self, sessions_file: str = "data/sessions.json"):
        """
        Initialize session manager with file-based persistence

        Args:
            sessions_file: Path to JSON file for storing sessions
        """
        self.sessions_file = Path(sessions_file)
        self.sessions: Dict[str, Dict[str, Any]] = {}

        # Create data directory if it doesn't exist
        self.sessions_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing sessions from file
        self._load_sessions()

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
        self._save_sessions()
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
        self._save_sessions()
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
        self._save_sessions()

    def add_answer(self, phone_number: str, question: str, answer: str):
        """Record a question-answer pair"""
        if phone_number not in self.sessions:
            self.create_session(phone_number)

        self.sessions[phone_number]["answers"][question] = answer
        if question not in self.sessions[phone_number]["questions_asked"]:
            self.sessions[phone_number]["questions_asked"].append(question)
        self._save_sessions()

    def set_stage(self, phone_number: str, stage: ConversationStage):
        """Update conversation stage"""
        if phone_number not in self.sessions:
            self.create_session(phone_number)

        self.sessions[phone_number]["stage"] = stage
        self.sessions[phone_number]["last_activity"] = datetime.now().isoformat()
        self._save_sessions()

    def clear_session(self, phone_number: str):
        """Clear session for a phone number"""
        if phone_number in self.sessions:
            del self.sessions[phone_number]
            self._save_sessions()

    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get all active sessions"""
        return self.sessions

    def _load_sessions(self):
        """Load sessions from file"""
        try:
            if self.sessions_file.exists():
                with open(self.sessions_file, 'r') as f:
                    self.sessions = json.load(f)
                logger.info(f"Loaded {len(self.sessions)} sessions from {self.sessions_file}")
            else:
                logger.info("No existing sessions file found, starting fresh")
                self.sessions = {}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding sessions file: {e}")
            self.sessions = {}
        except Exception as e:
            logger.error(f"Error loading sessions: {e}")
            self.sessions = {}

    def _save_sessions(self):
        """Save sessions to file"""
        try:
            # Create backup of existing file
            if self.sessions_file.exists():
                backup_file = self.sessions_file.with_suffix('.json.bak')
                self.sessions_file.rename(backup_file)

            # Write new sessions file
            with open(self.sessions_file, 'w') as f:
                json.dump(self.sessions, f, indent=2)

            # Remove backup if write was successful
            backup_file = self.sessions_file.with_suffix('.json.bak')
            if backup_file.exists():
                backup_file.unlink()

        except Exception as e:
            logger.error(f"Error saving sessions: {e}")
            # Try to restore from backup
            backup_file = self.sessions_file.with_suffix('.json.bak')
            if backup_file.exists():
                backup_file.rename(self.sessions_file)

# Global session manager instance
session_manager = SessionManager()
