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
Feb 21 15:19:06 ChatTogether(callbacks=[<services.chat_model.MyCustomHandler object at 0x10e3854f0>], client=<openai.resources.chat.completions.completions.Completions object at 0x10e434e60>, async_client=<openai.resources.chat.completions.completions.AsyncCompletions object at 0x10e436990>, model_name='meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo', temperature=0.0, model_kwargs={}, max_tokens=1024, stop=['<|eot_id|>'], together_api_key=SecretStr('**********'), together_api_base='https://api.together.xyz/v1/')

Feb 21 15:19:23 CHAD: generate_response_langchain 8 chat_history.messages:
Feb 21 15:19:23 [HumanMessage(content='What is the weather in SF?\n\n', additional_kwargs={}, response_metadata={}),
Feb 21 15:19:23  AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_5cngzlncqauxffjclwkelkht', 'function': {'arguments': '{"location":"SF"}', 'name': 'get_weather'}, 'type': 'function', 'index': 0}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 14, 'prompt_tokens': 340, 'total_tokens': 354, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo', 'system_fingerprint': None, 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-477751aa-02d2-4d8c-95a4-cd8c8b29247c-0', tool_calls=[{'name': 'get_weather', 'args': {'location': 'SF'}, 'id': 'call_5cngzlncqauxffjclwkelkht', 'type': 'tool_call'}], usage_metadata={'input_tokens': 340, 'output_tokens': 14, 'total_tokens': 354, 'input_token_details': {}, 'output_token_details': {}}),
Feb 21 15:19:23  ToolMessage(content="It's 60 degrees and foggy in SF.", name='get_weather', tool_call_id='call_5cngzlncqauxffjclwkelkht'),
Feb 21 15:19:23  AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_twzl714f4uiyl8m9p65gzrv6', 'function': {'arguments': '{"location":"SF"}', 'name': 'get_weather'}, 'type': 'function', 'index': 0}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 14, 'prompt_tokens': 380, 'total_tokens': 394, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo', 'system_fingerprint': None, 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-cf62ad3f-0414-4be1-a306-b43e9de76152-0', tool_calls=[{'name': 'get_weather', 'args': {'location': 'SF'}, 'id': 'call_twzl714f4uiyl8m9p65gzrv6', 'type': 'tool_call'}], usage_metadata={'input_tokens': 380, 'output_tokens': 14, 'total_tokens': 394, 'input_token_details': {}, 'output_token_details': {}}),
Feb 21 15:19:23  ToolMessage(content="It's 60 degrees and foggy in SF.", name='get_weather', tool_call_id='call_twzl714f4uiyl8m9p65gzrv6'),
Feb 21 15:19:23  AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_ha9dbvnedv4gfbv241apcm1s', 'function': {'arguments': '{"location":"SF"}', 'name': 'get_weather'}, 'type': 'function', 'index': 0}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 14, 'prompt_tokens': 420, 'total_tokens': 434, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo', 'system_fingerprint': None, 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-7cf68236-b1aa-4101-8c3d-76d9e06a296c-0', tool_calls=[{'name': 'get_weather', 'args': {'location': 'SF'}, 'id': 'call_ha9dbvnedv4gfbv241apcm1s', 'type': 'tool_call'}], usage_metadata={'input_tokens': 420, 'output_tokens': 14, 'total_tokens': 434, 'input_token_details': {}, 'output_token_details': {}}),
Feb 21 15:19:23  ToolMessage(content="It's 60 degrees and foggy in SF.", name='get_weather', tool_call_id='call_ha9dbvnedv4gfbv241apcm1s'),
Feb 21 15:19:23  AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_ha9dbvnedv4gfbv241apcm1s', 'function': {'arguments': '{"location":"SF"}', 'name': 'get_weather'}, 'type': 'function', 'index': 0}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 14, 'prompt_tokens': 420, 'total_tokens': 434, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo', 'system_fingerprint': None, 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-7cf68236-b1aa-4101-8c3d-76d9e06a296c-0', tool_calls=[{'name': 'get_weather', 'args': {'location': 'SF'}, 'id': 'call_ha9dbvnedv4gfbv241apcm1s', 'type': 'tool_call'}], usage_metadata={'input_tokens': 420, 'output_tokens': 14, 'total_tokens': 434, 'input_token_details': {}, 'output_token_details': {}})]
```
