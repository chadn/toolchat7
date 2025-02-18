import pytest
from services.chat_history import ChatHistoryManager
import json

def test_append_valid_message():
    manager = ChatHistoryManager()
    message = {"role": "user", "content": "Hello"}
    manager.append_message(message)
    assert len(manager.messages) == 1
    assert "dt" in manager.messages[0]

def test_append_invalid_message():
    manager = ChatHistoryManager()
    with pytest.raises(ValueError):
        manager.append_message("not a dict")
    
    with pytest.raises(ValueError):
        manager.append_message({"role": "user"})  # missing content
        
def test_export_import_json():
    manager = ChatHistoryManager()
    message = {"role": "user", "content": "Hello"}
    manager.append_message(message)
    
    json_str = manager.export_json()
    
    new_manager = ChatHistoryManager()
    new_manager.import_json(json_str)
    
    assert len(new_manager.messages) == 1
    assert new_manager.messages[0]["role"] == "user"
    assert new_manager.messages[0]["content"] == "Hello"

def test_import_invalid_json():
    manager = ChatHistoryManager()
    with pytest.raises(ValueError):
        manager.import_json('{"not": "a list"}') 