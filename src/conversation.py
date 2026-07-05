"""Conversation memory manager for storing chat history per session."""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional

CONVERSATIONS_DIR = Path(__file__).parent.parent / "conversations"
CONVERSATIONS_DIR.mkdir(exist_ok=True)


class ConversationMessage:
    """A message in the conversation."""

    def __init__(self, role: str, content: str, timestamp: Optional[str] = None):
        self.role = role  # "user" or "assistant"
        self.content = content
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ConversationMessage":
        return cls(data["role"], data["content"], data.get("timestamp"))


class Conversation:
    """A conversation session with history."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages: List[ConversationMessage] = []
        self.file_path = CONVERSATIONS_DIR / f"{session_id}.json"
        self._load()

    def _load(self):
        """Load conversation from file if it exists."""
        if self.file_path.exists():
            try:
                data = json.loads(self.file_path.read_text())
                self.messages = [ConversationMessage.from_dict(m) for m in data]
            except (json.JSONDecodeError, OSError):
                self.messages = []

    def _save(self):
        """Save conversation to file."""
        data = [m.to_dict() for m in self.messages]
        self.file_path.write_text(json.dumps(data, indent=2))

    def add_message(self, role: str, content: str):
        """Add a message to the conversation."""
        msg = ConversationMessage(role, content)
        self.messages.append(msg)
        self._save()

    def get_messages(self) -> List[tuple]:
        """Get messages in format for LangChain agent: [("role", "content"), ...]"""
        return [(m.role, m.content) for m in self.messages]

    def get_messages_for_llm(self) -> List[Dict]:
        """Get messages in LangChain message format."""
        from langchain_core.messages import HumanMessage, AIMessage

        llm_messages = []
        for msg in self.messages:
            if msg.role == "user":
                llm_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                llm_messages.append(AIMessage(content=msg.content))
        return llm_messages

    def get_last_n_messages(self, n: int) -> List[tuple]:
        """Get last N messages for context window."""
        return self.get_messages()[-n:]

    def clear(self):
        """Clear conversation history."""
        self.messages = []
        if self.file_path.exists():
            self.file_path.unlink()

    def summary(self) -> str:
        """Get a summary of the conversation."""
        count = len(self.messages)
        user_count = sum(1 for m in self.messages if m.role == "user")
        assistant_count = sum(1 for m in self.messages if m.role == "assistant")
        return f"Session {self.session_id}: {count} messages ({user_count} user, {assistant_count} assistant)"


# Global conversation cache
_conversations: Dict[str, Conversation] = {}


def get_conversation(session_id: str) -> Conversation:
    """Get or create a conversation."""
    if session_id not in _conversations:
        _conversations[session_id] = Conversation(session_id)
    return _conversations[session_id]


def list_conversations() -> List[str]:
    """List all session IDs with existing conversations."""
    return [f.stem for f in CONVERSATIONS_DIR.glob("*.json")]
