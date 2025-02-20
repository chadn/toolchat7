# Architecture

This file gives an overview of the current architecture as well as the reasoning for architecture decisions.

Since the AI space evolves rapidly, the decisions made in the past may be worth reconsidering if new tech is available, this file should document those types of decisions.

## Data Concepts

When reviewing the code, it helps to understand the different types of data that are used in the project.

1. Conversations - chat history, or messages between user and AI where a user statement and AI response is considered 2 turns. Stored as `.tsv` files when used as test data. A conversation contains all the user specific history. Note that a user could be a human or LLM judge when testing.
1. Tool Calling - a way to get AI to do things or get information by calling functions with arguments. See [Tools.md](Tools.md) for more details.

Read more on
[Chat models](https://python.langchain.com/docs/concepts/chat_models/),
[Messages](https://python.langchain.com/docs/concepts/messages/),
[Chat history](https://python.langchain.com/docs/concepts/chat_history/),
[Tool calling](https://python.langchain.com/docs/concepts/tool_calling/),
[Retrieval Augmented Generation (RAG)](https://python.langchain.com/docs/concepts/rag/),
[Agents](https://python.langchain.com/docs/concepts/agents/),
[Tracing](https://python.langchain.com/docs/concepts/tracing/) (aka debugging),
[Evaluation](https://python.langchain.com/docs/concepts/evaluation/) vs [Testing](https://python.langchain.com/docs/concepts/testing/),
etc at https://python.langchain.com/docs/concepts/

## Key Components

1. This repo - determines the prompt text, which has a great effect on how the agent performs
    1. The agent - it is the system that uses the LLM as the reasoning engine to determine which actions to take and the inputs necessary to perform the action. Tools define possible actions, inputs, and outputs. The agent executes the tools when LLM requests it.
    1. The prompt - the text that is customized for the LLM to give the agent a personality and a specific role.
1. The API - Langchain is a stable framework that enables evaluating different providers and models without much code change
1. The provider - Together.ai is our provider, evaluated based on cost for services offered
1. The LLM used - Currently Mixtral model performs the best, but considering llama 3.2+. Evaluated based on many factors including how it performs as a coach. Models are defined in (heartwood/llm_settings.py)

## RAG and Tool Calling Overview

## Tool Calling Summary

Tool Calling is a way for an LLM (AI) to make function calls and receive responses without human interaction, then present the response to the human in a natural language way.
Or to put another way, It is a way for AI to interact with APIs to get precise information, process it, and then present the result to the human.

## Introducing Tool Calling

> By themselves, language models can't take actions - they just output text. A big use case for LangChain is creating agents. Agents are systems that use LLMs as reasoning engines to determine which actions to take and the inputs necessary to perform the action. After executing actions, the results can be fed back into the LLM to determine whether more actions are needed, or whether it is okay to finish. This is often achieved via tool-calling. - https://python.langchain.com/docs/tutorials/agents/

> Modern LLMs are typically accessed through a chat model interface that takes a list of messages as input and returns a message as output.
>
> The newest generation of chat models offer additional capabilities:
>
> -   Tool calling: Many popular chat models offer a native tool calling API. This API allows developers to build rich applications that enable LLMs to interact with external services, APIs, and databases. Tool calling can also be used to extract structured information from unstructured data and perform various other tasks.
> -   Structured output: A technique to make a chat model respond in a structured format, such as JSON that matches a given schema.
> -   Multimodality: The ability to work with data other than text; for example, images, audio, and video.
>
> https://python.langchain.com/docs/concepts/chat_models/

> Tool calling is a general technique that generates structured output from a model, and you can use it even when you don't intend to invoke any tools
>
> -   https://python.langchain.com/docs/how_to/tool_calling/

RAG, or

# Using Tools with Langchain

## Tool Schemas

AI is made aware of what tools are avaiable via tool schemas

> Chat models that support tool calling features implement a `.bind_tools()` method for passing tool schemas to the model
> Tool schemas can be passed in as
>
> -   Python functions (with typehints and docstrings),
> -   Pydantic models,
> -   TypedDict classes, or
> -   LangChain Tool objects

https://python.langchain.com/docs/how_to/tool_calling/

TODO: chad use .bind_tools() and experiment with best way to communicate tool schemas to the model.
Defining structured output: https://python.langchain.com/docs/how_to/structured_output/

## Tool Calling and Responses

Once a tool schema is defined, then the AI knows what tools are available and how to talk to the tools.

AI asking tool and getting response

-   Check AIMessage object for tool_calls, array of objects: name, args, id, type.
-   Response to AI should be ToolMessage containing name, content, tool_call_id (id from tool_calls)

https://python.langchain.com/docs/how_to/tool_calling/
https://python.langchain.com/docs/how_to/tool_results_pass_to_model/

## Models That Support Tool Calling

For Tool calling to work, it needs to be supported by Lanchain, a Provider, and the Model.

### Tool Support in Langchain

On Lanchain side, can view Providers that support Tool Calling here
https://python.langchain.com/docs/integrations/chat/#featured-providers

For example, the models used are those supported by the provider Together AI.

-   Overview https://python.langchain.com/docs/integrations/chat/together/
-   Examples of Together langchain tool calling found in the Langchain API reference for Together AI
    https://python.langchain.com/api_reference/together/chat_models/langchain_together.chat_models.ChatTogether.html

### Tool Support in Together AI

Here are the models that support tool calling according to Together AI Provider, from https://docs.together.ai/docs/function-calling

```
meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo
meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo
meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo
meta-llama/Llama-3.3-70B-Instruct-Turbo
mistralai/Mixtral-8x7B-Instruct-v0.1
mistralai/Mistral-7B-Instruct-v0.1
Qwen/Qwen2.5-7B-Instruct-Turbo
Qwen/Qwen2.5-72B-Instruct-Turbo
```

#### Together AI - Native Function Calling

> Llama 3.1 shipped natively with function calling support, but instead of specifying a tool_choice parameter like traditional function calling, it works with a special prompt syntax. Let's take a look at how to do function calling with Llama 3.1 models – strictly with a custom prompt

-   https://docs.together.ai/docs/llama-3-function-calling

The noteworthy difference between Native Function Calling and regular Function Calling (Tool Calling) is that Native Function Calling requires communicating tool schema as part of the custom prompt.

Regular Function Calling (Tool Calling) still works (just as good - to be confirmed) and is supported by more models,
