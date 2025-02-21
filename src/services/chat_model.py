from typing import ClassVar, Union, Optional, List, Dict
import pprint
import traceback
from pydantic import BaseModel
from langchain_together import ChatTogether
from langchain_core.language_models.chat_models import BaseChatModel
from services.tool_manager import ToolManager   
from services.chat_history import ChatHistoryManager
from langchain.chat_models import init_chat_model



TOGETHERAI_MIXTRAL_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"
TOGETHERAI_LLAMA3_405B_MODEL = "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo"
MIXTRAL_STOPS = ["</s>", "[INST]", "[/INST]"]
LLAMA3_STOPS = ["<|eot_id|>"]

class ChatModelService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # self.chat_llm = self.llama_model()
        self._mixtral_model = None
        self._llama_model = None
        self.chat_llm = self.mixtral_model()
        self.tool_manager = ToolManager()
        print(f"CHAD: ChatModelService self.chat_llm before bind_tools:")
        pprint.pp(self.chat_llm)
        try:
            self.chat_llm = self.chat_llm.bind_tools(self.tool_manager.working_tools)
            print(f"CHAD: ChatModelService bind_tools() SUCCESS! tools={self.tool_manager.working_tools}\n")
        except Exception as e:
            print(f"CHAD: ChatModelService bind_tools() failed. {type(e)} Exception:\n{e}\n{repr(e)}\n")
            print(f"CHAD: ChatModelService self.chat_llm:")
            pprint.pp(self.chat_llm)
            print(f"CHAD: ChatModelService traceback:")
            print(traceback.format_exc())
            print("\n\n")


    def mixtral_model(self) -> ChatTogether:
        if not self._mixtral_model:        
            self._mixtral_model = ChatTogether(
                model=TOGETHERAI_MIXTRAL_MODEL,
                together_api_key=self.api_key,
                max_tokens=512,
                stop=MIXTRAL_STOPS,
                top_p=0.9,
                temperature=1.0,
            )
        return self._mixtral_model

    def llama_model(self) -> ChatTogether:
        if not self._llama_model:        
            self._llama_model = ChatTogether(
                model=TOGETHERAI_LLAMA3_405B_MODEL,
                together_api_key=self.api_key,
                max_tokens=1024,
                stop=LLAMA3_STOPS,
                temperature=0
            )
        return self._llama_model

    def set_chat_history(self, chat_history: ChatHistoryManager):
        self.chat_history = chat_history

    def generate_response_langchain(self, content: str = None) -> str:
        """Generate a chat response using the Langchain API.
        uses the chat_history and the chat_llm to generate a response, updating the chat_history with the response.
        Args:
            content: Content of the message to generate a response for. If None, the last message in the chat_history is used.
        Returns:
            str: Generated response text
        """
        if content:
            self.chat_history.add_human_message(content)
        max_iterations = 10
        while max_iterations > 0:
            max_iterations -= 1
            # response_ai_msg is a AI Message object, the response from AI to human.
            print(f"\nCHAD: generate_response_langchain() chat_history.messages length={len(self.chat_history.messages)} ")
            response_ai_msg = self.chat_llm.invoke(self.chat_history.messages)
            tool_responses = []
            try:
                print("\nCHAD: generate_response_langchain() response_ai_msg: ")
                pprint.pp(response_ai_msg)
                tool_responses = self.tool_manager.execute_tool_calls(response_ai_msg)
            except Exception as e:
                print(f"\nCHAD: execute_tool_calls failed.\n{e}\n\n")
                raise e
            if (tool_responses and len(tool_responses) > 0):
                for toolmsg in tool_responses:
                    self.chat_history.add_tool_message(toolmsg)
            else:
                max_iterations = 0

        self.chat_history.add_ai_message(response_ai_msg)

        try:
            print("CHAD: generate_response_langchain() chat_history.messages: ")
            pprint.pp(self.chat_history.messages)
        except:
            print("CHAD: generate_response_langchain() printing chat_history.messages failed")

        return response_ai_msg

    
    def generate_response_together(self, messages: List[Dict[str, str]], 
                         model: str = None,
                         max_tokens: int = 1024,
                         temperature: float = 0) -> str:
        """Generate a chat response using the Together API.
        DEPRECATED: use generate_response instead
        
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
