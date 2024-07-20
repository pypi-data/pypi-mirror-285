from __future__ import annotations

import os
from typing import AsyncGenerator, Type

import reflex as rx
from flexai import message


class Client:
    """A base class for language models."""

    async def stream_chat_lines(
        self,
        messages: list[message.Message],
        system: message.SystemMessage | None = None,
    ) -> AsyncGenerator[message.AIMessage, None]:
        """Stream the response from the chat model line by line.

        Args:
            messages: The messages to send to the model.

        Returns:
            An async generator yielding the response from the model line by line.
        """
        buffer = ""
        async for delta in self.stream_chat_response(messages, system=system):
            buffer += delta.content
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                yield message.AIMessage(line + "\n")

class AnthropicClient(Client):
    def __init__(
        self, model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620")
    ):
        from anthropic import AsyncAnthropic

        self.client = AsyncAnthropic()
        self.model = model
        self.max_tokens = 4096

    @classmethod
    def to_llm_messages(cls, messages: list[message.Message]) -> list[dict]:
        return [
            {"role": m.role, "content": m.content} for m in messages
        ]

    async def get_chat_response(
        self,
        messages: list[message.Message],
        system: message.SystemMessage | None = None,
    ) -> message.AIMessage:
        """Get the response from the chat model.

        Args:
            messages: The messages to send to the model.

        Returns:
            The response from the model.
        """
        system = system or message.SystemMessage(content="")
        response = await self.client.messages.create(
            max_tokens=self.max_tokens,
            messages=self.to_llm_messages(messages),
            model=self.model,
            system=system.content or "",
        )
        print(response)
        content = response.content[0].text
        return message.AIMessage(content=content)

    async def stream_chat_response(
        self,
        messages: list[message.Message],
        system: message.SystemMessage | None = None,
    ) -> AsyncGenerator[message.AIMessage, None]:
        """Stream the response from the chat model.

        Args:
            messages: The messages to send to the model.

        Returns:
            An async generator yielding the response from the model.
        """
        system = system or message.SystemMessage(content="")
        async with self.client.messages.stream(
            max_tokens=self.max_tokens,
            messages=self.to_llm_messages(messages),
            model=self.model,
            system=system.content or "",
        ) as stream:
            async for text in stream.text_stream:
                yield message.AIMessage(content=text)

    async def get_structured_response(
        self,
        messages: list[message.Message],
        model: Type[rx.Base],
        system: message.SystemMessage | None = None,
    ) -> Type[rx.Base]:
        """Get the structured response from the chat model.

        Args:
            messages: The messages to send to the model.
            model: The model to use for the response.

        Returns:
            The structured response from the model.
        """
        system = message.SystemMessage(
            content=f"""{system or ""}

Return your answer according to the 'properties' of the following schema:
{model.schema()}

Return only the JSON object with the properties filled in.
Do not include anything in your response other than the JSON object.
Do not begin your response with ```json or end it with ```.
"""
        )
        print("final system")
        print(system.content)
        response = await self.get_chat_response(messages, system=system)
        print(response)
        try:
            obj = model.parse_raw(response.content)
        except Exception as e:
            # Try again, printing the exception.
            messages = messages + [
                response,
                message.UserMessage(
                    content=f"There was an error while parsing. Make sure to only include the JSON. Error: {e}"
                ),
            ]
            return await self.get_structured_response(
                messages, model=model, system=system
            )
        return obj


llm = AnthropicClient()
