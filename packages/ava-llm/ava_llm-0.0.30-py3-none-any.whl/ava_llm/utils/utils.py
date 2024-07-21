from typing import Any, Dict, List, Sequence

from ava_llm.conversations.messages.ai import AIMessage
from ava_llm.conversations.messages.base import BaseMessage
from ava_llm.conversations.messages.human import HumanMessage


def get_buffer_string(
    messages: Sequence[BaseMessage], human_prefix: str = "Human", ai_prefix: str = "AI"
) -> str:
    """Convert a sequence of Messages to strings and concatenate them into one string.

    Args:
        messages: Messages to be converted to strings.
        human_prefix: The prefix to prepend to contents of HumanMessages.
        ai_prefix: THe prefix to prepend to contents of AIMessages.

    Returns:
        A single string concatenation of all input messages.

    """
    string_messages = []
    for m in messages:
        if isinstance(m, HumanMessage):
            role = human_prefix
        elif isinstance(m, AIMessage):
            role = ai_prefix
        else:
            raise ValueError(f"Got unsupported message type: {m}")
        message = f"{role}: {m.content}"
        string_messages.append(message)

    return "\n".join(string_messages)


def get_prompt_input_key(inputs: Dict[str, Any]) -> str:
    """
    Get the prompt input key.

    Args:
        inputs: Dict[str, Any]

    Returns:
        A prompt input key.
    """
    if len(inputs) != 1:
        raise ValueError(f"Exactly one input key expected, got {len(inputs)}")
    return next(iter(inputs))
