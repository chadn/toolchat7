from typing import List, Dict
from together import Together

class ChatModelService:
    def __init__(self, api_key: str):
        self.together = Together(api_key=api_key)
        self.default_model = "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo"
    
    def generate_response(self, messages: List[Dict[str, str]], 
                         model: str = None,
                         max_tokens: int = 1024,
                         temperature: float = 0) -> str:
        """Generate a chat response using the Together API.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Model identifier (optional)
            max_tokens: Maximum tokens in response
            temperature: Response randomness (0-1)
            
        Returns:
            str: Generated response text
        """
        response = self.together.chat.completions.create(
            model=model or self.default_model,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in messages
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content 
    

#TODO use langchain https://python.langchain.com/v0.1/docs/integrations/chat/together/
