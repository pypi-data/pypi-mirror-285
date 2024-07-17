"""File for the DialogueSession Class."""

from typing import List

from db_copilot.contract import MemoryItem

PlaceholderMessage = "MASK"


class DialogueSession:
    """DialogueSession Class."""

    def __init__(self, messageHistory: List[MemoryItem] = []) -> None:
        """Initialize the class."""
        self.messageHistory: List[MemoryItem] = messageHistory
