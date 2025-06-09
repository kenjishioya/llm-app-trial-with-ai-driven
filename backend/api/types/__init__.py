"""
GraphQL型定義
"""

from .ask import AskInput, AskPayload
from .message import MessageType, MessageRole
from .session import SessionType, SessionInput

__all__ = [
    "AskInput",
    "AskPayload",
    "MessageType",
    "MessageRole",
    "SessionType",
    "SessionInput",
]
