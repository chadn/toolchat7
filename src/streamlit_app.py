"""
Main Streamlit application for the chatbot interface.
"""
import os
import streamlit as st
from datetime import datetime
from io import StringIO
from typing import Optional
from dotenv import load_dotenv
import traceback

from services.chat_model import ChatModelService
from services.chat_history import ChatHistoryManager
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain.globals import set_verbose, set_debug




def dbg(msg):
    if st.session_state.dbg_print:
        print(f"{datetime.now().strftime('%H:%M:%S.%f')} {msg}", flush=True)

def init_session_state() -> None:
    """Initialize session state variables."""
    if "initialized" in st.session_state:
        return
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = ChatHistoryManager()
    if "dbg_print" not in st.session_state:
        st.session_state.dbg_print = os.getenv('DEBUG_PRINT')
    # Setting the verbose flag will print out inputs and outputs in a slightly more readable format 
    # and will skip logging certain raw outputs (like the token usage stats for an LLM call) 
    # so that you can focus on application logic.
    set_verbose(os.getenv('LANGCHAIN_VERBOSE', default=False))
    # Setting the global debug flag will cause all LangChain components with callback support 
    # (chains, models, agents, tools, retrievers) to print the inputs they receive and outputs 
    # they generate. This is the most verbose setting and will fully log raw inputs and outputs.
    set_debug(os.getenv('LANGCHAIN_DEBUG', default=False))
    st.session_state.initialized = True
    dbg(f"DEBUG_PRINT set to {st.session_state.dbg_print} session state initialized")


def setup_page() -> None:
    st.set_page_config(page_title="Tool Chat 7", page_icon="🐦")
    st.title("💬 Tool Chat 7 ")
    st.write("This is a simple chatbot that uses custom tools, or APIs.")
    st.write("What is the weather in SF?")

def get_api_key() -> Optional[str]:
    """Get API key from environment or user input.
    
    Returns:
        Optional[str]: API key if available, None otherwise
    """
    api_key = os.getenv('TOGETHER_API_KEY')
    if api_key:
        st.write("Using TOGETHER_API_KEY from env variable")
        return api_key
        
    api_key = st.text_input("Together API Key", type="password")
    if not api_key:
        st.info("Please add your Together API key to continue.", icon="🗝️")
        st.stop()
    return api_key

@st.cache_resource
def get_chat_model(api_key: str) -> ChatModelService:
    """Initialize and cache the chat model service.
    
    Args:
        api_key: Together AI API key
        
    Returns:
        ChatModelService: Initialized chat model service
    """
    return ChatModelService(api_key)

@st.fragment
def download_messages() -> None:
    """Create a download button to save chat messages as JSON file.
    
    Note:
        Currently requires clicking twice to get latest messages due to 
        Streamlit limitations with deferred data updates.
    """
    #TODO - should not have to click twice to get latest json, but we do for now.
    #TODO - Revisit once "Deferred data" is out, see roadmap.streamlit.app 
    # https://github.com/streamlit/streamlit/issues/5053
    # https://discuss.streamlit.io/t/generating-a-report-and-performing-download-on-download-button-click/53095/2
    #
    dbg("Initializing download_messages()")        
    now = datetime.now()
    fn = f"toolchat7_messages_{now.strftime('%Y-%m-%d')}_{int(now.timestamp())}.json"
    messages_json = st.session_state.chat_history.export_json()
    dbg(f"messages_json now {len(messages_json)} bytes, {len(st.session_state.chat_history.messages)} messages")
    st.markdown("Save chat messages by downloading.  \nClick twice to get latest (bug).")
    st.download_button(
        label="Download Messages as JSON",
        data=messages_json,
        on_click=lambda: dbg("Download button clicked"),
        file_name=fn,
        mime="application/json"
    )
    dbg(f"Initialized download_button {len(messages_json)} bytes for file_name={fn}")


def upload_messages() -> None:
    """Handle file upload to restore previous chat messages from JSON file.
    
    Allows users to upload a previously saved chat history JSON file.
    Updates st.session_state.messages with the uploaded content if successful.
    Displays error message if JSON parsing fails or format is invalid.
    """
    dbg("Initializing upload_messages()")
    # uploader_key https://discuss.streamlit.io/t/how-to-remove-the-uploaded-file/70346/3
    if "uploader_key" not in st.session_state:
        st.session_state["uploader_key"] = 1
    uploaded_file = st.file_uploader(
        "Restore Saved Chat Messages.\nChoose a File",
        key=st.session_state.uploader_key,
        type="json")    
    if uploaded_file is not None:
        try:
            dbg(f"Uploaded {uploaded_file.size} bytes from {uploaded_file.name}")
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            string_data = stringio.read()
            st.session_state.chat_history.import_json(string_data)
            uploaded_file = None
            st.session_state.uploader_key += 1
        except Exception as e:
            st.error("Error parsing JSON file. Please ensure the file is in the correct format.", icon="🚨")
            st.exception(e)

def render_message(msg: BaseMessage):
    with st.chat_message(msg.type):
        #st.write(msg.content)
        st.markdown(msg.content)
        #if isinstance(msg, TimeMessage):
        #    st.caption(f"{msg.time.strftime(readable_time_format)}")

def setup_sidebar() -> None:
    """Configure and display sidebar elements."""
    with st.sidebar:
        download_messages()
        upload_messages()

def display_chat_history() -> None:
    """Display all messages in the chat history."""
    for msg in st.session_state.chat_history.get_just_ai_human_message():
        render_message(msg)

def handle_user_input(chat_model: ChatModelService) -> None:
    """Handle user input and generate responses.
    
    Args:
        chat_model: Initialized chat model service
    """

    if prompt := st.chat_input("What can I answer for you today?"):
        # Add user message
        st.session_state.chat_history.add_human_message(prompt)
        render_message(st.session_state.chat_history.messages[-1])        
        # Generate and display response
        try:
            st.session_state.chat_model.generate_response_langchain()
            dbg(f"CHAD: generate_response_langchain returned")
            render_message(st.session_state.chat_history.messages[-1])
        except Exception as e:
            print(f"CHAD: generate_response_langchain failed. {type(e)} Exception:\n{e}\n{repr(e)}\n")
            print(f"CHAD: generate_response_langchain traceback:")
            print(traceback.format_exc())
            print("\n\n")
            st.error(f"Error generating response: {str(e)}", icon="🚨")


def main() -> None:
    """Main application function."""
    load_dotenv()
    init_session_state()
    setup_page()
    setup_sidebar()
    
    if "api_key" not in st.session_state:
        st.session_state.api_key = get_api_key()
    if st.session_state.api_key:
        try:
            if "chat_model" not in st.session_state:
                st.session_state.chat_model = get_chat_model(st.session_state.api_key)
                st.session_state.chat_model.set_chat_history(st.session_state.chat_history)
            display_chat_history()
            handle_user_input(st.session_state.chat_model)
        except Exception as e:
            print(f"CHAD: main() {type(e)} Exception:\n{e}\n{repr(e)}\n")
            print(f"CHAD: main() traceback:")
            print(traceback.format_exc())
            print("\n\n")

if __name__ == "__main__":
    main()




