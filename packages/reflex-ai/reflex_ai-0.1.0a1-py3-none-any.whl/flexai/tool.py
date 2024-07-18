import reflex as rx
import datetime
import json
import inspect
from typing import Any, Dict, Callable

from flexai.capability import AgentCapability
from flexai.message import Message, AIMessage, UserMessage


class ToolInvocation(rx.Base):
    """Structure to specify a tool and arguments to invoke it with."""

    tool: str
    params: Dict[str, Any]

class ToolResponse(rx.Base):
    """Structure to specify the result of a tool invocation."""

    invocation: ToolInvocation
    result: Any
    error: str | None


class Tool(rx.Base):
    description: str | None
    params: Dict[str, Any]
    return_type: Any
    _func: Callable

    @classmethod
    def parse_function_annotations(cls, func: Callable) -> Dict[str, str]:
        """Parse function annotations into a more readable format."""
        signature = inspect.signature(func)
        params = {
            name: param.annotation.__name__ if hasattr(param.annotation, '__name__') else 'No annotation'
            for name, param in signature.parameters.items()
        }
        return_type = signature.return_annotation.__name__ if hasattr(signature.return_annotation, '__name__') else 'No annotation'
        description = inspect.getdoc(func) or 'No description'
        return {
            "name": func.__name__,
            "description": description,
            "params": params,
            "return_type": return_type
        }

    @classmethod
    def from_function(cls, func: Callable):
        """Create a tool from a function."""
        annotations = cls.parse_function_annotations(func)
        return cls(
            **annotations,
            _func=func,
        )

def send_message(message: str) -> None:
    """Send a final message to the user. This should be done after all internal processing is completed."""
    print(f"Sending message: {message}")


class ToolUse(AgentCapability):
    """Give an agent the ability to use tools."""

    def __init__(self, tools: list[Callable]):
        self.tools = [Tool.from_function(tool) for tool in tools]

    def init_agent(self, agent):
        agent.output_model = ToolInvocation

    async def modify_prompt(self, prompt: str) -> str:
        tool_info = "\n".join([json.dumps([tool.dict(exclude={"_func"}) for tool in self.tools], indent=2)])
        return f"""The current date and time is: {datetime.datetime.now()}.
{prompt}
You have the following tools available:
{tool_info}
Make sure your response includes only one of these valid tools.
"""

    async def modify_response(self, agent, messages, response: AIMessage) -> AIMessage:
        assert isinstance(response, ToolInvocation), f"Expected a ToolInvocation response, got {response}"
        # Base case
        if response.tool == "send_message":
            yield AIMessage(content=response.params["message"])
            return
        ai_message = AIMessage(content=json.dumps(response.dict(), indent=2))
        messages.append(ai_message)
        print(ai_message)

        yield ai_message
        tool = [tool for tool in self.tools if tool.name == response.tool][0]
        # Invoke the tool.
        try:
            result = tool._func(**response.params)
        except Exception as e:
            result = str(e)
        user_message = UserMessage(content=f"Tool invocation response: {result}")
        messages.append(user_message)
        yield user_message
        async for msg in agent.stream(messages):
            yield msg