from abc import ABC, abstractmethod
from typing import List, Sequence

from ava_llm.conversations.messages.base import BaseMessage
from ava_llm.utils.utils import get_buffer_string


class BaseChatMessageHistory(ABC):
    messages: List[BaseMessage]

    def add_message(self, message: BaseMessage) -> None:
        if type(self).add_messages != BaseChatMessageHistory.add_messages:
            self.add_messages([message])
        else:
            raise NotImplementedError(
                "add_message is not implemented for this class. "
                "Please implement add_message or add_messages."
            )

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        for message in messages:
            self.add_message(message)

    @abstractmethod
    def clear(self) -> None:
        """Remove all messages from the store"""

    def __str__(self) -> str:
        return get_buffer_string(self.messages)


class InMemoryChatMessageHistory(BaseChatMessageHistory):
    messages: List[BaseMessage]

    def __init__(self) -> None:
        self.messages = []

    def add_message(self, message: BaseMessage) -> None:
        self.messages.append(message)

    def clear(self) -> None:
        self.messages = []
