from flexai.message import Message, AIMessage


class AgentCapability:
    """Base class to define cognitive capabilities of an agent."""

    async def modify_prompt(self, prompt: str) -> str:
        """Modify the system prompt."""
        return prompt

    async def modify_messages(self, messages: list[Message]) -> list[Message]:
        """Modify the messages before sending them to the LLM."""
        return messages

    async def modify_response(self, agent, messages, response: AIMessage) -> AIMessage:
        yield None
