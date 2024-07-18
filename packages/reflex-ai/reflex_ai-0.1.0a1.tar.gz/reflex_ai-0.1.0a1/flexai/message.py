import datetime
import reflex as rx
from sqlmodel import Column, DateTime, Field, func, select


class Conversation(rx.Model, table=True):
    """A conversation between the user and the AI."""

    # The name of the conversation.
    name: str

    # The timestamp when the conversation was created.
    timestamp: datetime.datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )


class Message(rx.Model, table=True):
    """A message to send to the agent."""

    # The role of the message (user, system, AI, tool).
    role: str

    # The content of the message.
    content: str

    # The type of data in the content.
    type: str = "text"

    # The timestamp when the message was created.
    timestamp: datetime.datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    # The conversation ID the message belongs to.
    conversation_id: int | None = Field(default=None, foreign_key="conversation.id")

    def to_llm_message(self) -> dict:
        """Convert the message to a format that can be sent to the LLM."""
        return {
            "role": self.role,
            "content": self.content,
        }


def UserMessage(**kwargs):
    return Message(role="user", **kwargs)


def SystemMessage(**kwargs):
    return Message(role="system", **kwargs)


def AIMessage(**kwargs):
    return Message(role="assistant", **kwargs)


# class UserMessage(Message):
#     """A message from the user."""

#     role = "user"


# class SystemMessage(Message):
#     """A message from the system."""

#     role = "system"


# class AIMessage(Message):
#     """A message from the AI."""

#     role = "assistant"


# class ToolMessage(Message):
#     """A message from a tool."""

#     role = "tool"


def get_conversations(offset: int = 0, limit: int = 10):
    """Get a list of converations sorted from newest to oldest."""
    with rx.session() as session:
        return session.exec(
            select(Conversation)
            .order_by(Conversation.id.desc())
            .offset(offset)
            .limit(limit)
        ).all()


def get_messages(conversation_id: int, offset: int = 0, limit: int = 100):
    """Get the messages in a conversation."""
    with rx.session() as session:
        return session.exec(
            select(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.id)
            .offset(offset)
            .limit(limit)
        ).all()
