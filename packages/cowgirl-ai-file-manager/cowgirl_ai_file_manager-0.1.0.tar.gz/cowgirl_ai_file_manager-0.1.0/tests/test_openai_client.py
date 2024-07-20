import pytest
from unittest.mock import patch, MagicMock
from src.client import ConfigOpenAI, Client 

def test_config_openai():
    """
    Simple test framework. Patch simulates the expected behavior from os.getenv, 
    in order to pass it to the functions (as opposed to calling the module directly)
    """
    with patch('os.getenv', return_value='test_api_key'):
        config = ConfigOpenAI()
        assert config.open_ai_api_key == 'test_api_key'

def test_client_initialization():
    with patch('os.getenv', return_value='test_api_key'):
        with patch('src.client.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            client = Client()
            assert client.open_ai_api_key == 'test_api_key'
            
            mock_openai.assert_called_with(api_key='test_api_key')
            assert client.client == mock_client

if __name__ == "__main__":
    pytest.main()