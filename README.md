# 💬 Tool Chat 7

A Streamlit-based chatbot application that uses Together AI's language models and supports tool calling.

Demo the code in this repo here: https://toolchat7.streamlit.app/

## Setup

1. Clone the repository
2. Create a virtual environment:
    ```bash
    uv venv
    source .venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3. Install dependencies:
    ```bash
    uv pip install -e .
    ```
4. Copy `.env.template` to `.env` and add your Together API key:
    ```bash
    cp .env.template .env
    # Edit .env with your API key
    ```

## Running the Application

```bash
streamlit run src/streamlit_app.py
```

## Running Tests

Run all tests:

```bash
pytest tests/
```

For integration tests:

```bash
pytest tests/ -m integration
```

## Project Structure

```
/
├── .devcontainer/
│   └── devcontainer.json          # Configuration for development container
├── src/
│   ├── streamlit_app.py           # Main Streamlit application
│   ├── services/
│   │   ├── chat_history.py        # Chat history management
│   │   └── chat_model.py          # Together AI chat model integration
├── tests/
│   ├── test_chat_history.py       # Unit tests for chat history management
│   └── test_chat_model.py         # Unit tests for chat model integration
├── .env.template                  # Template for environment variables
├── .gitignore                     # Git ignore file
├── LICENSE                        # License file
├── README.md                      # Project README file
├── requirements.txt               # Python dependencies
├── run_app.py                     # Entry point script to run the app
├── setup.py                       # Setup script for the project
├── streamlit_app.py               # Main Streamlit application (duplicate, should be removed)
├── temp.json                      # Temporary JSON file with chat data
└── TODO.md                        # To-do list for the project
```

## Features

-   Chat interface with Together AI models
-   Chat history management
-   Export/Import chat history as JSON
-   Configurable model parameters
-   Debug print option

## Development

The application is structured into several key components:

-   `ChatModelService`: Handles interactions with Together AI's API
-   `ChatHistoryManager`: Manages chat history and persistence
-   Streamlit UI: Provides the user interface and interaction flow

## Environment Variables

-   `TOGETHER_API_KEY`: Your Together AI API key
-   `DEBUG_PRINT`: Enable/disable debug printing (True/False)

[Apache License 2.0](LICENSE)
