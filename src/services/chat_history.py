from datetime import datetime
from typing import Dict, List, Optional
import json
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage, SystemMessage

class ChatHistoryManager(StreamlitChatMessageHistory):
    def __init__(self):
        super().__init__(key="langchain_messages")
        print(f"CHAD: ChatHistoryManager init complete.")
    
    def add_human_message(self, content: str) -> None:
        self.add_message(HumanMessage(content=content))

    def add_ai_message(self, content: str | AIMessage) -> None:
        if type(content) == AIMessage:
            self.add_message(content)
        elif type(content) == str:
            self.add_message(AIMessage(content=content))
        else:
            raise ValueError(f"add_ai_message() Invalid content type: {type(content)}")

    def add_tool_message(self, toolmsg: ToolMessage) -> None:
        self.add_message(toolmsg)

    def add_system_message(self, content: str) -> None:
        self.add_message(SystemMessage(content=content))

    def append_message(self, message: Dict[str, str]) -> None:
        """Append a message to the chat history.
        DEPRECATED: use add_human_message or add_ai_message instead
        
        Args:
            message: Dict containing 'role' and 'content' keys
            
        Raises:
            ValueError: If message format is invalid
        """
        if not isinstance(message, dict):
            raise ValueError("Message must be a dictionary")
            
        required_keys = ['role', 'content']
        if not all(key in message for key in required_keys):
            raise ValueError(f"Message missing required keys: {required_keys}")
            
        if not all(isinstance(message[key], str) for key in required_keys):
            raise ValueError("Message 'role' and 'content' must be strings")
            
        if "dt" not in message:
            message["dt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
        
        self.append(message)


    def get_just_ai_human_message(self) -> List[BaseMessage]:
        """
        Get all  AI or Human messages from the chat history.
        Skip system, tool, and any messages without content.

        Returns:
            List[BaseMessage]: A list of BaseMessage objects
        """
        messages = []
        for msg in self.messages:
            if msg.type in ["ai", "human"]:
                if msg.content:
                    messages.append(BaseMessage(content=msg.content, type=msg.type))
        print(f"CHAD: get_just_ai_human_message() returning {len(messages)} of {len(self.messages)} messages")
        return messages

    
    def export_json(self) -> str:
        """Export chat history as JSON string."""
        # TODO fix this
        #return json.dumps(self.messages)
        return '[]'
        
    def import_json(self, json_str: str) -> None:
        """Import chat history from JSON string.
        
        Args:
            json_str: JSON string containing chat messages
            
        Raises:
            ValueError: If JSON format is invalid
        """
        messages = json.loads(json_str)
        if not isinstance(messages, list):
            raise ValueError("JSON must contain a list of messages")
            
        for msg in messages:
            if not isinstance(msg, dict) or not all(key in msg for key in ['type', 'content']):
                raise ValueError("Each message must be a dictionary with at least 'type' and 'content' keys")
            
        self.clear()
        for msg in messages:
            self.add_message(BaseMessage(
                content=msg["content"],
                type=msg["type"],
            ))

        self.messages = messages 