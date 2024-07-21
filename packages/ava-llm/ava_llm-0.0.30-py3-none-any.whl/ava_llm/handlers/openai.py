from openai import OpenAI as SyncOpenAI, AsyncOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

client = SyncOpenAI(api_key=openai_api_key)
aclient = AsyncOpenAI(api_key=openai_api_key)


class OpenAI:
    def __init__(self, model, temperature=None):
        self.model = model or "gpt-3.5-turbo"
        self.temperature = temperature

    def invoke(self, prompt, temperature=None, force_json=False, **kwargs):
        temperature = temperature if temperature is not None else self.temperature
        response = self._generate(prompt, temperature, force_json=force_json, **kwargs)
        response_dict = self._response_to_dict(response)
        return response_dict

    async def ainvoke(self, prompt, temperature=None, **kwargs):
        temperature = temperature if temperature is not None else self.temperature
        response = await self._agenerate(prompt, temperature, **kwargs)
        response_dict = self._response_to_dict(response)
        return response_dict

    def stream(self, prompt, temperature=None, **kwargs):
        temperature = temperature if temperature is not None else self.temperature
        response = self._generate(prompt, temperature, stream=True, **kwargs)
        for chunk in response:
            yield chunk.choices[0].delta.content

    async def astream(self, prompt, temperature=None, **kwargs):
        temperature = temperature if temperature is not None else self.temperature
        response = await self._agenerate(prompt, temperature, stream=True, **kwargs)
        async for chunk in response:
            yield chunk.choices[0].delta.content

    def _response_to_dict(self, response):
        # metadata dict
        metadata_dict = {}
        metadata_dict["input_tokens"] = response.usage.prompt_tokens
        metadata_dict["output_tokens"] = response.usage.completion_tokens
        metadata_dict["total_tokens"] = response.usage.total_tokens

        # response dict
        response_dict = {}
        response_dict["content"] = response.choices[0].message.content
        response_dict["response_metadata"] = {
            "token_usage": metadata_dict,
            "model": self.model,
        }
        return response_dict

    def _generate(
        self, prompt, temperature=1.0, stream=False, force_json=False, **kwargs
    ):
        if force_json:
            kwargs["response_format"] = {"type": "json_object"}

        prompt = self._format_prompt(prompt)

        response = client.chat.completions.create(
            model=self.model,
            messages=prompt,
            temperature=temperature,
            stream=stream,
            **kwargs
        )
        return response

    async def _agenerate(self, prompt, temperature=1.0, stream=False, **kwargs):
        prompt = self._format_prompt(prompt)
        response = await aclient.chat.completions.create(
            model=self.model,
            messages=prompt,
            temperature=temperature,
            stream=stream,
            **kwargs
        )
        return response

    def _format_prompt(self, prompt):
        if isinstance(prompt, str):
            return [{"role": "user", "content": prompt}]
        elif isinstance(prompt, list):
            return prompt
        else:
            raise TypeError("Unexpected prompt type")
