from typing import ClassVar, Union, Optional, List, Dict, Any
from uuid import UUID
import pprint
import traceback
from pydantic import BaseModel
from langchain_together import ChatTogether
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain.chat_models import init_chat_model
from services.tool_manager import ToolManager   
from services.chat_history import ChatHistoryManager
from utils import warn, error, success, dbg_important


# Mixtral 8x7B was deprecated 2024/11/30 according to https://docs.mistral.ai/getting-started/models/models_overview/
TOGETHERAI_MIXTRAL_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"
TOGETHERAI_LLAMA3_405B_MODEL = "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo"
TOGETHERAI_LLAMA33_70B_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
MIXTRAL_STOPS = ["</s>", "[INST]", "[/INST]"]
LLAMA3_STOPS = ["<|eot_id|>"]

class ChatModelService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        #self.chat_llm_no_tools = self.mixtral_model()
        #self.chat_llm_no_tools = self.llama_model_405b()
        try:
            self.chat_llm_no_tools = self.llama_model_70b()
            self.tool_manager = ToolManager()
            dbg_important(f"CHAD: ChatModelService self.chat_llm_no_tools before bind_tools: {self.chat_llm_no_tools}")
            self.chat_llm = self.chat_llm_no_tools.bind_tools(self.tool_manager.working_tools)
            success(f"CHAD: ChatModelService bind_tools() SUCCESS! tools={self.tool_manager.working_tools}\n")
        except Exception as e:
            error(f"CHAD: ChatModelService: {type(e)} Exception:\n{e}\n{repr(e)}\n")
            error(traceback.format_exc())
            print("\n\n")
            raise e


    def mixtral_model(self) -> ChatTogether:
        if not '_mixtral_model' in self.__dict__:      
            self._mixtral_model = ChatTogether(
                model=TOGETHERAI_MIXTRAL_MODEL,
                together_api_key=self.api_key,
                max_tokens=512,
                stop=MIXTRAL_STOPS,
                top_p=0.9,
                temperature=0,
                callbacks=[MyCustomHandler()],
            )
        return self._mixtral_model

    def llama_model_405b(self) -> ChatTogether:
        if not '_llama_model_405b' in self.__dict__:      
            self._llama_model_405b = ChatTogether(
                model=TOGETHERAI_LLAMA3_405B_MODEL,
                together_api_key=self.api_key,
                max_tokens=1024,
                stop=LLAMA3_STOPS,
                temperature=0,
                callbacks=[MyCustomHandler()],
            )
        return self._llama_model_405b

    def llama_model_70b(self) -> ChatTogether:
        if not '_llama_model_70b' in self.__dict__:        
            self._llama_model_70b = ChatTogether(
                model=TOGETHERAI_LLAMA33_70B_MODEL,
                together_api_key=self.api_key,
                max_tokens=1024,
                stop=LLAMA3_STOPS,
                temperature=0,
                callbacks=[MyCustomHandler()],
            )
        return self._llama_model_70b

    def get_system_message(self) -> str:
        system_prompt = """
        You are a helpful assistant that can access external tool functions without asking the human user.
        The responses from these function calls will be appended to this dialogue as a message from "tool". 
        Using these tool responses, Please provide responses to the human user based on the information from these function calls.
        """
        return ' '.join(system_prompt.split())


    def set_chat_history(self, chat_history: ChatHistoryManager, skip_system_message: bool = False):
        self.chat_history = chat_history
        if not skip_system_message:
            # should we check to see if a system message already exists? No, trust the boolean.
            self.chat_history.add_system_message(self.get_system_message())


    def generate_response_langchain(self, content: str = None) -> str:
        """Generate a chat response using the Langchain API.
        uses the chat_history and the chat_llm to generate a response.
        
        Updates the chat_history with the response, maybe multiple times.

        Args:
            content: Content of the message to generate a response for. If None, the last message in the chat_history is used.
        Returns:
            str: Generated response text
        """
        if content:
            self.chat_history.add_human_message(content)

        # this is how many turns we allow the AI to call tools.  3 for now while debugging, increase to 5 or 10 later.
        max_tool_turns = 3
        remaining_tool_turns = max_tool_turns
        while remaining_tool_turns > 0:
            remaining_tool_turns -= 1
            # response_ai_msg is a AI Message object, the response from AI to human.
            dbg_important(f"\nCHAD: generate_response_langchain remaining_tool_turns={remaining_tool_turns} chat_history.messages length={len(self.chat_history.messages)} ")
            response_ai_msg = self.chat_llm.invoke(self.chat_history.messages)
            tool_responses = []
            try:
                dbg_important("\nCHAD: generate_response_langchain() response_ai_msg: ")
                pprint.pp(response_ai_msg)
                tool_responses = self.tool_manager.execute_tool_calls(response_ai_msg)
            except Exception as e:
                error(f"\nCHAD: execute_tool_calls failed.\n{e}\n\n")
                raise e
            if (tool_responses and len(tool_responses) > 0):
                # add the AI message with tool_calls to the chat history before adding the response tool messages
                self.chat_history.add_ai_message(response_ai_msg)
                for toolmsg in tool_responses:
                    self.chat_history.add_tool_message(toolmsg)
            else:
                #max_tool_turns = 0
                break

        self.chat_history.add_ai_message(response_ai_msg)

        try:
            dbg_important(f"CHAD: generate_response_langchain {len(self.chat_history.messages)} chat_history.messages: ")
            pprint.pp(self.chat_history.messages)
            print("\n", flush=True)
        except:
            dbg_important("CHAD: generate_response_langchain() printing chat_history.messages failed")

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
    


# available callback functions listed here:
# https://python.langchain.com/api_reference/core/callbacks/langchain_core.callbacks.base.BaseCallbackHandler.html
# #langchain-core-callbacks-base-basecallbackhandler
class MyCustomHandler(BaseCallbackHandler):

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        print(f"My custom handler, token: {token}")

    def on_llm_start(self, serialized: dict[str, Any], prompts: list[str], *, run_id: UUID, 
                     parent_run_id: UUID | None = None, tags: list[str] | None = None, 
                     metadata: dict[str, Any] | None = None, **kwargs: Any) -> None:
        # ATTENTION: This method is called for non-chat models (regular LLMs). 
        # If you’re implementing a handler for a chat model, you should use on_chat_model_start instead.
        dbg_important(f"CHAD: on_llm_start")

    def on_chat_model_start(self, serialized: dict[str, Any], messages: list[list[BaseMessage]], *, run_id: UUID, 
                           parent_run_id: UUID | None = None, tags: list[str] | None = None, 
                           metadata: dict[str, Any] | None = None, **kwargs: Any) -> None:
        # ATTENTION: This method is called for chat models. 
        # If you’re implementing a handler for a non-chat model, you should use on_llm_start instead.
        dbg_important(f"CHAD: on_chat_model_start {len(messages)}.{len(messages[0])} messages: {messages}")


