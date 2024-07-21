from typing import Literal
from ava_llm.conversations.messages.base import BaseMessage


class HumanMessage(BaseMessage):
    """Message from a human."""

    type: Literal["human"] = "human"
