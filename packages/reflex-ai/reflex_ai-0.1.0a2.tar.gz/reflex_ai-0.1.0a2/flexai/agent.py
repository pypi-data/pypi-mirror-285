from __future__ import annotations

from typing import TYPE_CHECKING
from flexai import llm, message
from flexai.tool import ToolInvocation

if TYPE_CHECKING:
    from flexai.capability import AgentCapability


class Agent:
    def __init__(self, prompt: str = "", capabilities: list[AgentCapability] = None):
        self.llm = llm.llm
        self.prompt = prompt
        self.capabilities = capabilities or []

    async def modify_messages(self, messages: list[message.Message]):
        for capability in self.capabilities:
            messages = await capability.modify_messages(messages)
        return messages

    async def get_system_message(self) -> message.SystemMessage:
        system = self.prompt
        for capability in self.capabilities:
            system = await capability.modify_prompt(system)
        return message.SystemMessage(content=system)

    async def stream(self, messages: list[message.Message]):
        messages = await self.modify_messages(messages)
        system = await self.get_system_message()
        response = await self.llm.get_structured_response(messages, model=ToolInvocation, system=system)
        for capability in self.capabilities:
            async for message in capability.modify_response(self, messages, response):
                if message is not None:
                    yield message

    async def get_response(self, messages: list[message.Message]):
        system = await self.get_system_message()
        messages = await self.modify_messages(messages)
        return await self.llm.get_chat_response(messages, system=system)


async def name_conversation(messages: list[message.Message]) -> str:
    assert len(messages) > 0, "No messages provided."
    first_message = messages[0].content
    prompt = f"""Given the following first message to this conversation, give it a short, succinct title: {first_message}.\n Include only the title, nothing else. Do not include any text other than the new title."""
    return (await llm.llm.get_chat_response([message.UserMessage(content=prompt)])).content