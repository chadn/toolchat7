import pytest
from services.chat_model import ChatModelService
from unittest.mock import Mock, patch

def test_chat_model_initialization():
    service = ChatModelService("fake-api-key")
    assert service.default_model == "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo"

@patch('services.chat_model.Together')
def test_generate_response_mocked(mock_together):
    # Setup mock
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Test response"))]
    mock_together.return_value.chat.completions.create.return_value = mock_response
    
    # Test
    service = ChatModelService("fake-api-key")
    messages = [{"role": "user", "content": "Hello"}]
    response = service.generate_response(messages)
    
    # Verify
    assert response == "Test response"
    mock_together.return_value.chat.completions.create.assert_called_once()

@pytest.mark.integration
def test_generate_response_real():
    """Only run this test when specifically testing integration"""
    pytest.skip("Skipping integration test by default")
    service = ChatModelService("your-test-api-key")
    messages = [{"role": "user", "content": "Hello"}]
    response = service.generate_response(messages)
    assert isinstance(response, str)
    assert len(response) > 0 