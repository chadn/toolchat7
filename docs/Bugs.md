# Bugs

Noting bugs here that currently exist in code.

## tool_results_pass_to_model Not working

Summary: Model is not getting tool responses correctly, making tool calls seem to be ignored.

Currently trying to figure out the best code for generate_response_langchain() in [chat_model.py](../src/services/chat_model.py),
which is where the code checks for `tool_calls`, executes them, and updates the chat history with the tool responses.

I'm guessing based on the `prompts` in debug output below that the id's for tool calls and responses are removed.

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

### tool_results_pass_to_model Debug Output

Below is output with `LANGCHAIN_VERBOSE=True` and `LANGCHAIN_DEBUG=True` from `streamlit run src/streamlit_app.py 2>&1|ts|tee -a src/streamlit_app.py.log`

Before adding AI response to messages, AI heard both human and tool as human messages

```
CHAD: generate_response_langchain() chat_history.messages:
[
  HumanMessage(
    content='What is the weather in SF?\n\n', additional_kwargs={}, response_metadata={}),
 ToolMessage(
    content="It's 60 degrees and foggy in SF.", name='get_weather', tool_call_id='call_zh2g5cz16f557s7mo31ahsht'),
 AIMessage(
    content=" Thanks for letting me know! I'll make sure to dress accordingly.", additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 16, 'prompt_tokens': 663, 'total_tokens': 679, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'mistralai/Mixtral-8x7B-Instruct-v0.1', 'system_fingerprint': None, 'finish_reason': 'eos', 'logprobs': None}, id='run-beb5ea15-e457-43ea-9c3d-7c22a1543ecd-0', usage_metadata={'input_tokens': 663, 'output_tokens': 16, 'total_tokens': 679, 'input_token_details': {}, 'output_token_details': {}})
]
```

Similar, but this time adding AI messages that call tools to chat history (empty content).

NOTE: the messages seem to correctly match the documented approach, but the prompts seems to simplify messages down to single string.

```
[llm/start] [llm:ChatTogether] Entering LLM run with input:
{
  "prompts": [
    "Human: What is the weather in SF?\n\n\nAI: \nTool: It's 60 degrees and foggy in SF.\nAI: \nTool: It's 60 degrees and foggy in SF.\nAI: \nTool: It's 60 degrees and foggy in SF."
   ]
}
...
Feb 21 10:29:03 CHAD: generate_response_langchain chat_history.messages:
Feb 21 10:29:03
[HumanMessage(content='What is the weather in SF?\n\n', additional_kwargs={}, response_metadata={}),

AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_jmscs4ur1zgfai1n1xu262tb', 'function': {'arguments': '{"location":"SF"}', 'name': 'get_weather'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 38, 'prompt_tokens': 642, 'total_tokens': 680, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'mistralai/Mixtral-8x7B-Instruct-v0.1', 'system_fingerprint': None, 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-a610fbf4-ba70-4fa8-a250-f3716fc9c33f-0', tool_calls=[{'name': 'get_weather', 'args': {'location': 'SF'}, 'id': 'call_jmscs4ur1zgfai1n1xu262tb', 'type': 'tool_call'}], usage_metadata={'input_tokens': 642, 'output_tokens': 38, 'total_tokens': 680, 'input_token_details': {}, 'output_token_details': {}}),

ToolMessage(content="It's 60 degrees and foggy in SF.", name='get_weather', tool_call_id='call_jmscs4ur1zgfai1n1xu262tb'),

AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_2mrtvnq6vc4shtvxy95i0c3z', 'function': {'arguments': '{"location":"SF"}', 'name': 'get_weather'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 38, 'prompt_tokens': 718, 'total_tokens': 756, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'mistralai/Mixtral-8x7B-Instruct-v0.1', 'system_fingerprint': None, 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-186a8972-c943-4b1a-8b73-44514646d308-0', tool_calls=[{'name': 'get_weather', 'args': {'location': 'SF'}, 'id': 'call_2mrtvnq6vc4shtvxy95i0c3z', 'type': 'tool_call'}], usage_metadata={'input_tokens': 718, 'output_tokens': 38, 'total_tokens': 756, 'input_token_details': {}, 'output_token_details': {}}),

ToolMessage(content="It's 60 degrees and foggy in SF.", name='get_weather', tool_call_id='call_2mrtvnq6vc4shtvxy95i0c3z'),

AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_xiavy5q0nrfsazkkid6a5oox', 'function': {'arguments': '{"location":"SF"}', 'name': 'get_weather'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 38, 'prompt_tokens': 794, 'total_tokens': 832, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'mistralai/Mixtral-8x7B-Instruct-v0.1', 'system_fingerprint': None, 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-fd5d0803-206c-4bd2-af84-141b9fa70865-0', tool_calls=[{'name': 'get_weather', 'args': {'location': 'SF'}, 'id': 'call_xiavy5q0nrfsazkkid6a5oox', 'type': 'tool_call'}], usage_metadata={'input_tokens': 794, 'output_tokens': 38, 'total_tokens': 832, 'input_token_details': {}, 'output_token_details': {}}),

ToolMessage(content="It's 60 degrees and foggy in SF.", name='get_weather', tool_call_id='call_xiavy5q0nrfsazkkid6a5oox'),

AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_5h48u694o187cg5pwivpagry', 'function': {'arguments': '{"location":"SF"}', 'name': 'get_weather'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 38, 'prompt_tokens': 865, 'total_tokens': 903, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'mistralai/Mixtral-8x7B-Instruct-v0.1', 'system_fingerprint': None, 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-b3bd487c-3d05-4d4c-bb5b-5e93d4ea9cb6-0', tool_calls=[{'name': 'get_weather', 'args': {'location': 'SF'}, 'id': 'call_5h48u694o187cg5pwivpagry', 'type': 'tool_call'}], usage_metadata={'input_tokens': 865, 'output_tokens': 38, 'total_tokens': 903, 'input_token_details': {}, 'output_token_details': {}}),

```
