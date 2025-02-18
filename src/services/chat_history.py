from datetime import datetime
from typing import Dict, List, Optional
import json

class ChatHistoryManager:
    def __init__(self):
        self.messages: List[Dict[str, str]] = []
        
    def append_message(self, message: Dict[str, str]) -> None:
        """Append a message to the chat history.
        
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
        
        self.messages.append(message)
        
    def export_json(self) -> str:
        """Export chat history as JSON string."""
        return json.dumps(self.messages)
        
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
            if not isinstance(msg, dict) or not all(key in msg for key in ['role', 'content']):
                raise ValueError("Each message must be a dictionary with 'role' and 'content' keys")
                
        self.messages = messages 