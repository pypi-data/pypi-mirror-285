from ava_llm.prompts.base import PromptTemplate


class CustomTemplate(PromptTemplate):
    template = """{text}"""


class ConversationTemplate(PromptTemplate):
    template = """The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know.
Key Insights:
{summary} 
Current conversation:
{history}
Human: {input}
AI:
"""
