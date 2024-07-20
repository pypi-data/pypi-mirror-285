import reflex as rx


class Message(rx.Base):

    # The role of the message (user, system, AI, tool).
    role: str

    # The content of the message.
    content: str

class SystemMessage(Message):

    role = "system"

class UserMessage(Message):

    role = "user"

class AIMessage(Message):
    
    role = "assistant"
