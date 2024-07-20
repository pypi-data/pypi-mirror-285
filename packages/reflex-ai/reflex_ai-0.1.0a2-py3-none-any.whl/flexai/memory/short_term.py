from flexai.capability import AgentCapability
from flexai.message import Message, SystemMessage
from flexai.llm import llm


class TruncateMessages(AgentCapability):
    """Truncate the input messages to the LLM."""

    def __init__(self, max_messages: int):
        self.max_messages = max_messages

    async def modify_messages(self, messages: list[Message]) -> list[Message]:
        return messages[-self.max_messages:]


class UseEmotion(AgentCapability):
    """Add emotional context to the agent's responses."""

    def __init__(self):
        self.current_emotion = "I am excited to start helping!"

    async def modify_prompt(self, prompt: str) -> str:
        return f"""{prompt}

Your current emotional state is: {self.current_emotion}
Respond according to the emotional state.
"""


    async def modify_messages(self, messages: list[Message]) -> list[Message]:
        system = SystemMessage(content=f"""You are monitoring the emotional state of the ai agent.

        The current emotional state is: {self.current_emotion}

        Based on the current conversation, update the emotional state of the ai agent.
        Be descriptive but concise. Include only the new emotional state in your response, nothing else.
        """)
        self.emotional_state = (await llm.get_chat_response(system=system, messages=messages)).content
        print(f"New emotional state: {self.emotional_state}")
        return messages
