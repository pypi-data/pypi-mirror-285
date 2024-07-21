from abc import ABC
from typing import Any, Dict, Optional, Tuple
import warnings

from ava_llm.conversations.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from ava_llm.conversations.memory import BaseMemory
from ava_llm.conversations.messages.ai import AIMessage
from ava_llm.conversations.messages.human import HumanMessage
from ava_llm.utils.utils import get_prompt_input_key


class BaseChatMemory(BaseMemory, ABC):
    """Abstract base class for chat memory."""

    chat_memory: BaseChatMessageHistory = None
    output_key: Optional[str] = None
    input_key: Optional[str] = None
    return_messages: bool = False

    def __init__(self) -> None:
        self.chat_memory = InMemoryChatMessageHistory()

    def _get_input_output(
        self, inputs: Dict[str, Any], outputs: Dict[str, str]
    ) -> Tuple[str, str]:
        if self.input_key is None:
            prompt_input_key = get_prompt_input_key(inputs)
        else:
            prompt_input_key = self.input_key
        if self.output_key is None:
            if len(outputs) == 1:
                output_key = list(outputs.keys())[0]
            elif "output" in outputs:
                output_key = "output"
                warnings.warn(
                    f"'{self.__class__.__name__}' got multiple output keys:"
                    f" {outputs.keys()}. The default 'output' key is being used."
                    f" If this is not desired, please manually set 'output_key'."
                )
            else:
                raise ValueError(
                    f"Got multiple output keys: {outputs.keys()}, cannot "
                    f"determine which to store in memory. Please set the "
                    f"'output_key' explicitly."
                )
        else:
            output_key = self.output_key
        return inputs[prompt_input_key], outputs[output_key]

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context from this conversation to buffer."""
        input_str, output_str = self._get_input_output(inputs, outputs)
        self.chat_memory.add_messages(
            [HumanMessage(content=input_str), AIMessage(content=output_str)]
        )

    def clear(self) -> None:
        """Clear memory contents."""
        self.chat_memory.clear()
