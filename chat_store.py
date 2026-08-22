"""
Chat Store for Customer Support AI
In-memory chat history storage with session support.
"""

from datetime import datetime


class ChatStore:
    """Stores chat history per session in memory."""

    def __init__(self):
        self._sessions = {}

    def _ensure_session(self, session_id):
        """Create a session if it doesn't exist."""
        if session_id not in self._sessions:
            self._sessions[session_id] = []

    def add_message(self, session_id, role, content, metadata=None):
        """
        Add a message to a session's history.

        Args:
            session_id: Unique session identifier
            role: 'user' or 'bot'
            content: Message text
            metadata: Optional dict with extra info (confidence, category, type)
        """
        self._ensure_session(session_id)
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        self._sessions[session_id].append(message)
        return message

    def get_history(self, session_id, limit=50):
        """Get chat history for a session, most recent last."""
        self._ensure_session(session_id)
        return self._sessions[session_id][-limit:]

    def get_recent_context(self, session_id, num_messages=6):
        """Get recent messages for conversation context."""
        self._ensure_session(session_id)
        return self._sessions[session_id][-num_messages:]

    def clear_session(self, session_id):
        """Clear all messages in a session."""
        self._sessions[session_id] = []

    def get_session_count(self):
        """Get the number of active sessions."""
        return len(self._sessions)
