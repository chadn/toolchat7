# To Do

-   :white_check_mark: Use Together AI instead of OpenAI (they are compatible)
-   :white_check_mark: Enable save and restore by providing links to download and upload messages  
    BUG: must click download button twice to get latest json, can be fixed once "Deferred data" download button is released.
-   :white_check_mark: decouple chat model from functions.
-   :white_check_mark: create some pytest unit tests for functions, maybe for chat model
-   :white_check_mark: use `uv` and `pyproject.toml`
-   use `ruff` for linting and formatting.
-   :white_check_mark: use langchain instead of Together AI
-   use langchain and tools to call my functions
    -   :white_check_mark: use langchain to interface with Together AI via `ChatTogether`
    -   :white_check_mark: use langchain to register `@tool` functions via `bind_tools`
    -   :white_check_mark: use langgraph's `ToolNode` to execute tool functions
    -   :heavy_exclamation_mark:see evidence that AI is receiving and understanding tool responses
-   use https://github.com/open-webui/open-webui instead of streamlit
