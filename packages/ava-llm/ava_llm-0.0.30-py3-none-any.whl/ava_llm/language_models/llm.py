import json
from typing import Any
from ava_llm.conversations.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from ava_llm.prompts.base import PromptTemplate
from ava_llm.prompts.template import ConversationTemplate
import uuid
from itertools import tee


class LLM:
    def __init__(self, model=None, handler=None, temperature=None) -> None:
        self.model = model or "gpt-3.5-turbo"
        self.handler = handler or self._get_handler()
        self.temperature = temperature if not None else self.handler.temperature

    def invoke(self, prompt, temperature=None, force_json=False, **kwargs):
        temperature = temperature if temperature is not None else self.temperature
        response = self.handler.invoke(
            prompt, temperature=temperature, force_json=force_json, **kwargs
        )
        return self._format_response(response)

    async def ainvoke(self, prompt, temperature=None, **kwargs):
        temperature = temperature if temperature is not None else self.temperature
        response = await self.handler.ainvoke(prompt, temperature=temperature, **kwargs)
        return self._format_response(response)

    def stream(self, prompt, **kwargs):
        for chunk in self.handler.stream(prompt, **kwargs):
            if chunk:
                if hasattr(chunk, "content"):
                    yield chunk
                elif isinstance(chunk, str):
                    yield chunk
                else:
                    raise TypeError("Unexpected response type")

    async def astream(self, prompt, **kwargs):
        async for chunk in self.handler.astream(prompt, **kwargs):
            if chunk:
                if hasattr(chunk, "content"):
                    yield chunk
                elif isinstance(chunk, str):
                    yield chunk
                else:
                    raise TypeError("Unexpected response type")

    def _format_response(self, response):

        # langchain response
        if hasattr(response, "content") and hasattr(response, "response_metadata"):
            return LLMResponse(response.content, response.response_metadata)

        # this library response
        if "content" in response and "response_metadata" in response:
            return LLMResponse(response["content"], response["response_metadata"])

        raise ValueError("Unexpected response type")

    def _get_handler(self):
        if (
            self.model == "gpt-3.5-turbo"
            or self.model == "gpt-4-turbo"
            or self.model == "gpt-4"
        ):
            from ava_llm.handlers.openai import OpenAI

            return OpenAI(model=self.model)
        elif self.model == "llama3-70b-8192" or self.model == "llama3-8b-8192":
            from ava_llm.handlers.meta import Meta

            return Meta(model=self.model)
        else:
            raise ValueError("Unsupported model")


class LLMResponse:
    def __init__(self, content, metadata=None):
        self.content = content
        self.metadata = metadata

    def __repr__(self):
        return f"LLMResponse(content='{self.content}', metadata={self.metadata})"


class ConversationChain:
    llm: LLM = None
    memory: BaseChatMessageHistory = None
    prompt: PromptTemplate = None
    _guid = str(uuid.uuid4())

    def __init__(
        self,
        llm: LLM,
        memory: BaseChatMessageHistory = InMemoryChatMessageHistory(),
        prompt: PromptTemplate = ConversationTemplate(),
    ) -> None:
        self.llm = llm
        self.memory = memory
        self.prompt = prompt

    @property
    def guid(self) -> str:
        return self._guid

    def stream(self, message: str, verbose=True, language="en", summary=None) -> Any:
        inputs = {"prompt": message}

        prompt = self.prompt.format(
            history=self.memory.buffer, input=message, language=language, summary=summary
        )

        chunks = []
        response, clean_response = tee(self.llm.stream(prompt))

        for chunk in response:
            yield chunk
            chunks.append(chunk)
            if verbose:
                print(chunk, end="", flush=True)

        outputs = {"response": "".join(chunks)}
        self.memory.save_context(inputs, outputs)

        return clean_response

    async def astream(
        self, message: str, verbose=True, ws_consumer=None, language="en", summary=None
    ) -> Any:
        inputs = {"prompt": message}

        prompt = self.prompt.format(
            history=self.memory.buffer, input=message, language=language, summary=summary
        )

        chunks = []

        async for chunk in self.llm.astream(prompt):
            yield chunk
            chunks.append(chunk)
            if ws_consumer is not None:
                await ws_consumer.send(text_data=json.dumps(chunk))
            if verbose:
                print(chunk, end="", flush=True)

        outputs = {"response": "".join(chunks)}
        self.memory.save_context(inputs, outputs)
