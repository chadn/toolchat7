# Bugs

Noting bugs here that currently exist in code.

## tool_results_pass_to_model Not working

Summary: Model is not getting tool responses correctly, making tool calls seem to be ignored.

Currently trying to figure out the best code for generate_response_langchain() in [chat_model.py](../src/services/chat_model.py),
which is where the code checks for `tool_calls`, executes them, and updates the chat history with the tool responses.

I'm guessing based on the `prompts` in debug output below that the id's for tool calls and responses are removed, even though `on_chat_model_start` callback shows langchain has the correct list of messages.

### tool_results_pass_to_model Approach

The current approach is based on the following from https://python.langchain.com/docs/how_to/tool_results_pass_to_model/

> Tool calling agents, like those in LangGraph, use this basic flow to answer queries and solve tasks.

```
for tool_call in ai_msg.tool_calls:
    selected_tool = {"add": add, "multiply": multiply}[tool_call["name"].lower()]
    tool_msg = selected_tool.invoke(tool_call)
    messages.append(tool_msg)

llm_with_tools.invoke(messages)
```

Debugging using custom code to output info as well as updating `.env` with `LANGCHAIN_VERBOSE=True` and `LANGCHAIN_DEBUG=True`.
Examples are from `streamlit run src/streamlit_app.py 2>&1 |ts |tee -a src/streamlit_app.py.log`

### tool_results_pass_to_model Example 1

In this example, we see that the AI appears to think the tool response is the human.

1. HumanMessage ask about the weather - `What is the weather in SF?`
1. AIMessage has tool_calls to get_weather, content is empty, `id=call_ia2uswft47a241a7nadsuvyy`
1. ToolMessage responds with info about the weather - `It's 60 degrees and foggy in SF.`
   `tool_call_id=call_ia2uswft47a241a7nadsuvyy`
1. AIMessage has no tool_calls, but content implies that AI thought tool message was from the human.
   `That's great! Foggy conditions are quite common in SF ...`

Note that our code uses a callback function, `on_chat_model_start` [API Docs](https://python.langchain.com/api_reference/core/callbacks/langchain_core.callbacks.base.BaseCallbackHandler.html#langchain_core.callbacks.base.BaseCallbackHandler.on_chat_model_start), confirming that ...

-   code is is correctly using a chat model and not a regular LLM model, else `on_llm_start` would be called.
-   code is sending the correct messages, where `tool_call_id` matches `id` from AIMessage.

DETAILED LOG OUTPUT:
Note that I added some whitespace below to make the output easier to read, and added `...` to represent removed content.

```
Feb 21 12:37:03 CHAD: on_chat_model_start 1.3 messages: [[

HumanMessage(content='What is the weather in SF?\n\n', additional_kwargs={}, response_metadata={}),

AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_ia2uswft47a241a7nadsuvyy', 'function': {'arguments': '{"location":"SF"}', 'name': 'get_weather'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 38, 'prompt_tokens': 642, 'total_tokens': 680, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'mistralai/Mixtral-8x7B-Instruct-v0.1', 'system_fingerprint': None, 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-577862d5-e0ef-44b1-a146-42a086883c8a-0', tool_calls=[{'name': 'get_weather', 'args': {'location': 'SF'}, 'id': 'call_ia2uswft47a241a7nadsuvyy', 'type': 'tool_call'}], usage_metadata={'input_tokens': 642, 'output_tokens': 38, 'total_tokens': 680, 'input_token_details': {}, 'output_token_details': {}}),

ToolMessage(content="It's 60 degrees and foggy in SF.", name='get_weather', tool_call_id='call_ia2uswft47a241a7nadsuvyy')

]]
Feb 21 12:37:03 [llm/start] [llm:ChatTogether] Entering LLM run with input:
Feb 21 12:37:03 {
Feb 21 12:37:03   "prompts": [
Feb 21 12:37:03     "Human: What is the weather in SF?\n\n\nAI: \nTool: It's 60 degrees and foggy in SF."
Feb 21 12:37:03   ]
Feb 21 12:37:03 }
Feb 21 12:37:03 [llm/end] [llm:ChatTogether] [634ms] Exiting LLM run with output:
Feb 21 12:37:03 {
Feb 21 12:37:03   "generations": [
Feb 21 12:37:03     [
Feb 21 12:37:03       {
Feb 21 12:37:03         "text": " That's great! Foggy conditions are quite common in SF, especially during the summer months. Fog can actually provide a cooling effect, so it might not feel as warm as the temperature would suggest. Enjoy your day!",
Feb 21 12:37:03         "generation_info": {
Feb 21 12:37:03           "finish_reason": "eos",
Feb 21 12:37:03           "logprobs": null
Feb 21 12:37:03         },...

Feb 21 12:37:03 CHAD: generate_response_langchain 4 chat_history.messages:
Feb 21 12:37:03 [
HumanMessage(content='What is the weather in SF?\n\n', additional_kwargs={}, response_metadata={}),

AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_ia2uswft47a241a7nadsuvyy', 'function': {'arguments': '{"location":"SF"}', 'name': 'get_weather'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 38, 'prompt_tokens': 642, 'total_tokens': 680, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'mistralai/Mixtral-8x7B-Instruct-v0.1', 'system_fingerprint': None, 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-577862d5-e0ef-44b1-a146-42a086883c8a-0', tool_calls=[{'name': 'get_weather', 'args': {'location': 'SF'}, 'id': 'call_ia2uswft47a241a7nadsuvyy', 'type': 'tool_call'}], usage_metadata={'input_tokens': 642, 'output_tokens': 38, 'total_tokens': 680, 'input_token_details': {}, 'output_token_details': {}}),

ToolMessage(content="It's 60 degrees and foggy in SF.", name='get_weather', tool_call_id='call_ia2uswft47a241a7nadsuvyy'),

AIMessage(content=" That's great! Foggy conditions are quite common in SF, especially during the summer months. Fog can actually provide a cooling effect, so it might not feel as warm as the temperature would suggest. Enjoy your day!", additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 48, 'prompt_tokens': 716, 'total_tokens': 764, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'mistralai/Mixtral-8x7B-Instruct-v0.1', 'system_fingerprint': None, 'finish_reason': 'eos', 'logprobs': None}, id='run-0d17f22b-9bf1-4f4c-b848-36b88f45b5b8-0', usage_metadata={'input_tokens': 716, 'output_tokens': 48, 'total_tokens': 764, 'input_token_details': {}, 'output_token_details': {}})

]
```

### tool_results_pass_to_model Example 2

In this example, we see the AI repeatedly making the same tool tool_calls to get_weather, and Tool responding with the same info.
The AI never sends text content, just tool_calls.
The 4th time the AI makes the tool call, the code does not respond because max_tool_turns = 3 in [chat_model.py](../src/services/chat_model.py).

```
Feb 21 12:53:41 CHAD: generate_response_langchain remaining_tool_turns=0 chat_history.messages length=5
Feb 21 12:53:41 CHAD: on_chat_model_start 1.5 messages: [[
  HumanMessage(content='What is the weather in SF?\n\n', additional_kwargs={}, response_metadata={}),
  AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_pq96spla7743mciqx8r5g3ur', 'function': {'arguments': '{"location":"SF"}', 'name': 'get_weather'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 38, 'prompt_tokens': 642, 'total_tokens': 680, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'mistralai/Mixtral-8x7B-Instruct-v0.1', 'system_fingerprint': None, 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-c40a1ced-6a53-42f5-9087-4bb6c41df5ba-0', tool_calls=[{'name': 'get_weather', 'args': {'location': 'SF'}, 'id': 'call_pq96spla7743mciqx8r5g3ur', 'type': 'tool_call'}], usage_metadata={'input_tokens': 642, 'output_tokens': 38, 'total_tokens': 680, 'input_token_details': {}, 'output_token_details': {}}),
  ToolMessage(content="It's 60 degrees and foggy in SF.", name='get_weather', tool_call_id='call_pq96spla7743mciqx8r5g3ur'),
  AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_nqkwy4k0wltcikqnxx0c7reo', 'function': {'arguments': '{"location":"SF"}', 'name': 'get_weather'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 38, 'prompt_tokens': 718, 'total_tokens': 756, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'mistralai/Mixtral-8x7B-Instruct-v0.1', 'system_fingerprint': None, 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-a4aef41f-f07a-4099-8a2a-4307b8029af2-0', tool_calls=[{'name': 'get_weather', 'args': {'location': 'SF'}, 'id': 'call_nqkwy4k0wltcikqnxx0c7reo', 'type': 'tool_call'}], usage_metadata={'input_tokens': 718, 'output_tokens': 38, 'total_tokens': 756, 'input_token_details': {}, 'output_token_details': {}}),
  ToolMessage(content="It's 60 degrees and foggy in SF.", name='get_weather', tool_call_id='call_nqkwy4k0wltcikqnxx0c7reo')
]]
Feb 21 12:53:43 [llm/start] [llm:ChatTogether] Entering LLM run with input:
Feb 21 12:53:43 {
Feb 21 12:53:43   "prompts": [
Feb 21 12:53:43     "Human: What is the weather in SF?\n\n\nAI: \nTool: It's 60 degrees and foggy in SF.\nAI: \nTool: It's 60 degrees and foggy in SF."
Feb 21 12:53:43   ]
Feb 21 12:53:43 }
Feb 21 12:53:43 [llm/end] [llm:ChatTogether] [1.69s] Exiting LLM run with output:
Feb 21 12:53:43 {
Feb 21 12:53:43   "generations": [
Feb 21 12:53:43     [
Feb 21 12:53:43       {
Feb 21 12:53:43         "text": "",
Feb 21 12:53:43         "generation_info": {
Feb 21 12:53:43           "finish_reason": "tool_calls",
Feb 21 12:53:43           "logprobs": null
Feb 21 12:53:43         },
...
Feb 21 12:53:43 CHAD: generate_response_langchain 8 chat_history.messages:

Feb 21 12:53:43 [HumanMessage(content='What is the weather in SF?\n\n', additional_kwargs={}, response_metadata={}),

Feb 21 12:53:43  AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_pq96spla7743mciqx8r5g3ur', 'function': {'arguments': '{"location":"SF"}', 'name': 'get_weather'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 38, 'prompt_tokens': 642, 'total_tokens': 680, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'mistralai/Mixtral-8x7B-Instruct-v0.1', 'system_fingerprint': None, 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-c40a1ced-6a53-42f5-9087-4bb6c41df5ba-0', tool_calls=[{'name': 'get_weather', 'args': {'location': 'SF'}, 'id': 'call_pq96spla7743mciqx8r5g3ur', 'type': 'tool_call'}], usage_metadata={'input_tokens': 642, 'output_tokens': 38, 'total_tokens': 680, 'input_token_details': {}, 'output_token_details': {}}),

Feb 21 12:53:43  ToolMessage(content="It's 60 degrees and foggy in SF.", name='get_weather', tool_call_id='call_pq96spla7743mciqx8r5g3ur'),

Feb 21 12:53:43  AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_nqkwy4k0wltcikqnxx0c7reo', 'function': {'arguments': '{"location":"SF"}', 'name': 'get_weather'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 38, 'prompt_tokens': 718, 'total_tokens': 756, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'mistralai/Mixtral-8x7B-Instruct-v0.1', 'system_fingerprint': None, 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-a4aef41f-f07a-4099-8a2a-4307b8029af2-0', tool_calls=[{'name': 'get_weather', 'args': {'location': 'SF'}, 'id': 'call_nqkwy4k0wltcikqnxx0c7reo', 'type': 'tool_call'}], usage_metadata={'input_tokens': 718, 'output_tokens': 38, 'total_tokens': 756, 'input_token_details': {}, 'output_token_details': {}}),

Feb 21 12:53:43  ToolMessage(content="It's 60 degrees and foggy in SF.", name='get_weather', tool_call_id='call_nqkwy4k0wltcikqnxx0c7reo'),

Feb 21 12:53:43  AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_moq2s5qmm2cs83jln1l5jv8h', 'function': {'arguments': '{"location":"SF"}', 'name': 'get_weather'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 38, 'prompt_tokens': 793, 'total_tokens': 831, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'mistralai/Mixtral-8x7B-Instruct-v0.1', 'system_fingerprint': None, 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-664d8584-7093-4c96-91ce-50b1167d97e7-0', tool_calls=[{'name': 'get_weather', 'args': {'location': 'SF'}, 'id': 'call_moq2s5qmm2cs83jln1l5jv8h', 'type': 'tool_call'}], usage_metadata={'input_tokens': 793, 'output_tokens': 38, 'total_tokens': 831, 'input_token_details': {}, 'output_token_details': {}}),

Feb 21 12:53:43  ToolMessage(content="It's 60 degrees and foggy in SF.", name='get_weather', tool_call_id='call_moq2s5qmm2cs83jln1l5jv8h'),

Feb 21 12:53:43  AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_moq2s5qmm2cs83jln1l5jv8h', 'function': {'arguments': '{"location":"SF"}', 'name': 'get_weather'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 38, 'prompt_tokens': 793, 'total_tokens': 831, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'mistralai/Mixtral-8x7B-Instruct-v0.1', 'system_fingerprint': None, 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-664d8584-7093-4c96-91ce-50b1167d97e7-0', tool_calls=[{'name': 'get_weather', 'args': {'location': 'SF'}, 'id': 'call_moq2s5qmm2cs83jln1l5jv8h', 'type': 'tool_call'}], usage_metadata={'input_tokens': 793, 'output_tokens': 38, 'total_tokens': 831, 'input_token_details': {}, 'output_token_details': {}})]
```

### tool_results_pass_to_model Example 3

This example has the same behaviour as Example 2. The only difference is this is using `Llama-3.1-405B` instead of `Mixtral-8x7B`.

```
Feb 23 16:15:30 ChatTogether(callbacks=[<services.chat_model.MyCustomHandler object at 0x1123d4920>], client=<openai.resources.chat.completions.completions.Completions object at 0x1124b9430>, async_client=<openai.resources.chat.completions.completions.AsyncCompletions object at 0x1124baf00>, model_name='meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo', temperature=0.0, model_kwargs={}, max_tokens=1024, stop=['<|eot_id|>'], together_api_key=SecretStr('**********'), together_api_base='https://api.together.xyz/v1/')

Feb 23 16:15:44 CHAD: generate_response_langchain 8 chat_history.messages:
Feb 23 16:15:44 [HumanMessage(content='What is the weather in SF?\n\n', additional_kwargs={}, response_metadata={}),
Feb 23 16:15:44  AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_fus0ucjka7nv5027jwy4hmd2', 'function': {'arguments': '{"location":"SF"}', 'name': 'get_weather'}, 'type': 'function', 'index': 0}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 14, 'prompt_tokens': 340, 'total_tokens': 354, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo', 'system_fingerprint': None, 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-af527fcb-1ebf-45d1-aea9-4fb34af9fd64-0', tool_calls=[{'name': 'get_weather', 'args': {'location': 'SF'}, 'id': 'call_fus0ucjka7nv5027jwy4hmd2', 'type': 'tool_call'}], usage_metadata={'input_tokens': 340, 'output_tokens': 14, 'total_tokens': 354, 'input_token_details': {}, 'output_token_details': {}}),
Feb 23 16:15:44  ToolMessage(content="It's 60 degrees and foggy in SF.", name='get_weather', tool_call_id='call_fus0ucjka7nv5027jwy4hmd2'),
Feb 23 16:15:44  AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_5eu6lqlc4udcka70p0ty2pkt', 'function': {'arguments': '{"location":"SF"}', 'name': 'get_weather'}, 'type': 'function', 'index': 0}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 14, 'prompt_tokens': 380, 'total_tokens': 394, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo', 'system_fingerprint': None, 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-e302b4fd-2ccd-4640-b505-a5cd88609ee5-0', tool_calls=[{'name': 'get_weather', 'args': {'location': 'SF'}, 'id': 'call_5eu6lqlc4udcka70p0ty2pkt', 'type': 'tool_call'}], usage_metadata={'input_tokens': 380, 'output_tokens': 14, 'total_tokens': 394, 'input_token_details': {}, 'output_token_details': {}}),
Feb 23 16:15:44  ToolMessage(content="It's 60 degrees and foggy in SF.", name='get_weather', tool_call_id='call_5eu6lqlc4udcka70p0ty2pkt'),
Feb 23 16:15:44  AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_u7v0m4oa34v7vl7dmjbcy6c2', 'function': {'arguments': '{"location":"SF"}', 'name': 'get_weather'}, 'type': 'function', 'index': 0}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 14, 'prompt_tokens': 420, 'total_tokens': 434, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo', 'system_fingerprint': None, 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-dfb2502d-3e88-476a-814c-a4ddeb7a51d8-0', tool_calls=[{'name': 'get_weather', 'args': {'location': 'SF'}, 'id': 'call_u7v0m4oa34v7vl7dmjbcy6c2', 'type': 'tool_call'}], usage_metadata={'input_tokens': 420, 'output_tokens': 14, 'total_tokens': 434, 'input_token_details': {}, 'output_token_details': {}}),
Feb 23 16:15:44  ToolMessage(content="It's 60 degrees and foggy in SF.", name='get_weather', tool_call_id='call_u7v0m4oa34v7vl7dmjbcy6c2'),
Feb 23 16:15:44  AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_u7v0m4oa34v7vl7dmjbcy6c2', 'function': {'arguments': '{"location":"SF"}', 'name': 'get_weather'}, 'type': 'function', 'index': 0}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 14, 'prompt_tokens': 420, 'total_tokens': 434, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo', 'system_fingerprint': None, 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-dfb2502d-3e88-476a-814c-a4ddeb7a51d8-0', tool_calls=[{'name': 'get_weather', 'args': {'location': 'SF'}, 'id': 'call_u7v0m4oa34v7vl7dmjbcy6c2', 'type': 'tool_call'}], usage_metadata={'input_tokens': 420, 'output_tokens': 14, 'total_tokens': 434, 'input_token_details': {}, 'output_token_details': {}})]
```

### Raw JSON HTTP request and response using langchain_together

SUMMARY: Confirmed that all messages are sent to `api.together.xyz` and that the `id` and `tool_call_id` are present and matching in the request. Using `ChatTogether` model from langchain_together.

Using https://github.com/cle-b/httpdbg to capture HTTP info like this:

```
pyhttpdbg -m streamlit.web.cli run src/streamlit_app.py 2>&1 |ts |tee -a src/streamlit_app.py.log
```

Was able to get the following info from http://localhost:4909/

```
POST https://api.together.xyz/v1/chat/completions
User-Agent: OpenAI/Python 1.63.2
Authorization: Bearer <TOGETHER_API_KEY>

status: 200 OK
start: 2025-02-24T00:15:43.588246+00:00
end:    2025-02-24T00:15:44.688619+00:00
```

REQUEST

```
{
  "messages": [
    {
      "content": "What is the weather in SF?\n\n",
      "role": "user"
    },
    {
      "content": null,
      "role": "assistant",
      "tool_calls": [
        {
          "type": "function",
          "id": "call_fus0ucjka7nv5027jwy4hmd2",
          "function": {
            "name": "get_weather",
            "arguments": "{\"location\": \"SF\"}"
          }
        }
      ]
    },
    {
      "content": "It's 60 degrees and foggy in SF.",
      "role": "tool",
      "tool_call_id": "call_fus0ucjka7nv5027jwy4hmd2"
    },
    {
      "content": null,
      "role": "assistant",
      "tool_calls": [
        {
          "type": "function",
          "id": "call_5eu6lqlc4udcka70p0ty2pkt",
          "function": {
            "name": "get_weather",
            "arguments": "{\"location\": \"SF\"}"
          }
        }
      ]
    },
    {
      "content": "It's 60 degrees and foggy in SF.",
      "role": "tool",
      "tool_call_id": "call_5eu6lqlc4udcka70p0ty2pkt"
    }
  ],
  "model": "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
  "max_tokens": 1024,
  "stop": [
    "<|eot_id|>"
  ],
  "stream": false,
  "temperature": 0.0,
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Call to get the current weather.",
        "parameters": {
          "properties": {
            "location": {
              "type": "string"
            }
          },
          "required": [
            "location"
          ],
          "type": "object"
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "get_coolest_cities",
        "description": "Get a list of coolest cities",
        "parameters": {
          "properties": {},
          "type": "object"
        }
      }
    }
  ]
}
```

RESPONSE

```
{
  "id": "916b43499ebd251d",
  "object": "chat.completion",
  "created": 1740356143,
  "model": "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
  "prompt": [],
  "choices": [
    {
      "finish_reason": "tool_calls",
      "seed": 11975339150697850000,
      "logprobs": null,
      "index": 0,
      "message": {
        "role": "assistant",
        "content": null,
        "tool_calls": [
          {
            "index": 0,
            "id": "call_u7v0m4oa34v7vl7dmjbcy6c2",
            "type": "function",
            "function": {
              "arguments": "{\"location\":\"SF\"}",
              "name": "get_weather"
            }
          }
        ]
      }
    }
  ],
  "usage": {
    "prompt_tokens": 420,
    "completion_tokens": 14,
    "total_tokens": 434
  }
}
```

excerpt from stack trace tab in httpdbg

```
File "/Users/chad/src/toolchat7/src/services/chat_model.py", line 93,
 93.             response_ai_msg = self.chat_llm.invoke(self.chat_history.messages)

File "/Users/chad/src/toolchat7/.venv/lib/python3.12/site-packages/langchain_core/runnables/base.py", line 5360,
 5360.         return self.bound.invoke(
 5361.             input,
 5362.             self._merge_configs(config),
 5363.             **{**self.kwargs, **kwargs},
 5364.         )

 ...

 File "/Users/chad/src/toolchat7/.venv/lib/python3.12/site-packages/langchain_core/language_models/chat_models.py", line 925,
 925.                 result = self._generate(
 926.                     messages, stop=stop, run_manager=run_manager, **kwargs
 927.                 )

File "/Users/chad/src/toolchat7/.venv/lib/python3.12/site-packages/langchain_openai/chat_models/base.py", line 783,
 783.             response = self.client.create(**payload)

File "/Users/chad/src/toolchat7/.venv/lib/python3.12/site-packages/openai/_utils/_utils.py", line 279,
 279.             return func(*args, **kwargs)

File "/Users/chad/src/toolchat7/.venv/lib/python3.12/site-packages/openai/resources/chat/completions/completions.py", line 879,
 879.         return self._post(
 880.             "/chat/completions",
 881.             body=maybe_transform(
 882.                 {
 883.                     "messages": messages,
 884.                     "model": model,
 885.                     "audio": audio,
 886.                     "frequency_penalty": frequency_penalty,
```

### Raw JSON HTTP request and response Together API

Similar to above, but instead of using langchain, using the `together` library directly to send HTTP requests to `api.together.xyz`.

This is included to show that langchain and together package both send HTTP POST requests to the same endpoint, both structure the json request the same way. The main difference is no tool calling on this example.

The code used for this can be viewed at [together-ai-api tag](https://github.com/chadn/toolchat7/tree/together-ai-api).

HTTP POST Headers to Together API

```
https://api.together.xyz/v1/chat/completions
User-Agent: Together/v1 PythonBindings/1.4.1
X-Together-Client-User-Agent: {"bindings_version": "1.4.1", "httplib": "requests", "lang": "python", "lang_version": "3.12.8", "platform": "macOS-15.3.1-arm64-arm-64bit", "publisher": "together", "uname": "Darwin 24.3.0 Darwin Kernel Version 24.3.0: Thu Jan 2 20:24:16 PST 2025; root:xnu-11215.81.4~3/RELEASE_ARM64_T6000 arm64 arm"}

status: 200 OK
start: 2025-02-24T15:53:34.231278+00:00
end:    2025-02-24T15:53:37.375537+00:00
```

REQUEST

```
{
    "messages": [
        {
            "role": "user",
            "content": "What is the weather in SF?\n\n"
        },
        {
            "role": "assistant",
            "content": "However, I'm a large language model, I don't have real-time access to current weather conditions. But I can suggest some ways for you to find out the current weather in San Francisco.\n\n1. Check online weather websites: You can check websites like AccuWeather, Weather.com, or the National Weather Service (NWS) for the current weather conditions in San Francisco.\n2. Use a mobile app: You can download mobile apps like Dark Sky, Weather Underground, or The Weather Channel to get the current weather conditions in San Francisco.\n3. Check social media: You can also check the social media accounts of local news stations or weather services in San Francisco to get updates on the current weather conditions.\n\nPlease note that the weather in San Francisco can be quite unpredictable and can change quickly, so it's always a good idea to check multiple sources for the most up-to-date information.\n\nIf you're looking for general information about the weather in San Francisco, I can tell you that the city has a Mediterranean climate with cool, wet winters and mild, dry summers. The average temperature in San Francisco ranges from 45°F (7°C) in January (the coldest month) to 67°F (19°C) in September (the warmest month)."
        },
        {
            "role": "user",
            "content": "What is cooler, SF or LA?\n"
        }
    ],
    "model": "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
    "max_tokens": 1024,
    "temperature": 0,
    "stream": false
}
```

RESPONSE

```
{
  "id": "9170a1152f2febe9",
  "object": "chat.completion",
  "created": 1740412414,
  "model": "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
  "prompt": [],
  "choices": [
    {
      "finish_reason": "eos",
      "seed": 4230294806757981,
      "logprobs": null,
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "San Francisco (SF) is generally cooler than Los Angeles (LA). San Francisco's climate is influenced by its proximity to the Pacific Ocean and the cool California Current, which keeps temperatures relatively mild and cool throughout the year.\n\nIn contrast, Los Angeles has a Mediterranean climate with warmer temperatures, especially during the summer months. LA's inland location and distance from the ocean contribute to its warmer temperatures.\n\nHere's a rough comparison of the average temperatures in SF and LA:\n\n* Summer (June to August):\n\t+ SF: Highs around 67-73°F (19-23°C), lows around 54-58°F (12-14°C)\n\t+ LA: Highs around 84-90°F (29-32°C), lows around 63-66°F (17-19°C)\n* Winter (December to February):\n\t+ SF: Highs around 58-62°F (14-17°C), lows around 45-50°F (7-10°C)\n\t+ LA: Highs around 68-72°F (20-22°C), lows around 48-52°F (9-11°C)\n\nOverall, San Francisco tends to be cooler than Los Angeles, especially during the summer months. However, both cities can experience temperature fluctuations, and microclimates within each city can vary significantly.",
        "tool_calls": []
      }
    }
  ],
  "usage": {
    "prompt_tokens": 313,
    "completion_tokens": 269,
    "total_tokens": 582
  }
}
```

Stack trace excerpt from httpdbg:

```
File "/Users/chad/src/toolchat7/src/services/chat_model.py", line 24,
 24.         response = self.together.chat.completions.create(
 25.             model=model or self.default_model,
 26.             messages=[
 27.                 {"role": m["role"], "content": m["content"]}
 28.                 for m in messages
 29.             ],
 30.             max_tokens=max_tokens,
 31.             temperature=temperature,

File "/Users/chad/src/toolchat7/.venv/lib/python3.12/site-packages/together/resources/chat/completions.py", line 141,
 141.         response, _, _ = requestor.request(
 142.             options=TogetherRequest(
 143.                 method="POST",
 144.                 url="chat/completions",
 145.                 params=parameter_payload,
 146.             ),
 147.             stream=stream,
 148.         )
```
