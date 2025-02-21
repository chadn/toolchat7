from typing import List, Dict
from langchain_core.messages import  ToolMessage, AIMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
import pprint


@tool
def get_weather(location: str):
    """Call to get the current weather."""
    if location.lower() in ["sf", "san francisco"]:
        return f"It's 60 degrees and foggy in {location}."
    else:
        return f"It's 90 degrees and sunny in {location}."


@tool
def get_coolest_cities():
    """Get a list of coolest cities"""
    return "nyc, sf"


class ToolManager:
    def __init__(self):
        self.working_tools = [get_weather, get_coolest_cities]
        self.tool_node = ToolNode(self.working_tools)
        print(f"CHAD: ToolManager init complete.")


    def execute_tool_calls(self, response_ai_msg: AIMessage) -> List[ToolMessage]:
        """Execute tool calls based on the parsed responses from the LLM.

        Args:
            response_ai_msg (AIMessage): The response from the chat llm 

        Returns:
            List[ToolMessage]: Results of executing each tool call
        """
        # https://langchain-ai.github.io/langgraph/how-tos/tool-calling/#using-with-chat-models
        tool_responses = self.tool_node.invoke({"messages": [response_ai_msg]})
        print("CHAD execute_tool_calls() ai_message.tool_calls, tool_responses: ")
        pprint.pp([response_ai_msg.tool_calls, tool_responses])
        print("\n\n")
        return tool_responses['messages'] if tool_responses and 'messages' in tool_responses else []


