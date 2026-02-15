import pytest
import os
from unittest.mock import Mock, patch
from app.services.llm_service import LLMService
from app.services.csv_generator import CSVGenerator
from app.utils.config_loader import ConfigLoader
from app.utils.prompt_loader import PromptLoader


class TestConfigLoader:
    """Test configuration loader."""
    
    def test_load_config_success(self):
        """Test successful config loading."""
        loader = ConfigLoader("config/config.yaml")
        assert loader.get("app.name") == "tatarana-ocr-engine"
        assert loader.get("api.port") == 8000
    
    def test_get_with_default(self):
        """Test getting config value with default."""
        loader = ConfigLoader("config/config.yaml")
        assert loader.get("nonexistent.key", "default") == "default"


class TestPromptLoader:
    """Test prompt loader."""
    
    def test_load_prompts_success(self):
        """Test successful prompt loading."""
        loader = PromptLoader("config/prompts.yaml")
        identify_prompt = loader.get_prompt("identify_file")
        assert "Analyze this financial document" in identify_prompt
    
    def test_get_nonexistent_prompt(self):
        """Test getting nonexistent prompt."""
        loader = PromptLoader("config/prompts.yaml")
        with pytest.raises(ValueError):
            loader.get_prompt("nonexistent_prompt")


class TestCSVGenerator:
    """Test CSV generator."""
    
    def test_create_csv_from_llm_response_csv_format(self):
        """Test creating CSV from LLM response already in CSV format."""
        csv_input = "date,description,amount\n2023-01-01,Test,100.00"
        result = CSVGenerator.create_csv_from_llm_response(csv_input)
        assert "date,description,amount" in result
        assert "2023-01-01,Test,100.00" in result
    
    def test_create_csv_from_transactions(self):
        """Test creating CSV from transaction list."""
        transactions = [
            {"date": "2023-01-01", "description": "Test", "amount": "100.00"},
            {"date": "2023-01-02", "description": "Test2", "amount": "-50.00"}
        ]
        result = CSVGenerator.create_csv_from_transactions(transactions)
        assert "date,description,amount" in result
        assert "2023-01-01,Test,100.00" in result
    
    def test_generate_filename(self):
        """Test filename generation."""
        filename = CSVGenerator.generate_filename("picpay", "bank_statement", "statement.pdf")
        assert "picpay_bank_statement" in filename
        assert filename.endswith(".csv")


class TestLLMService:
    """Test LLM service."""
    
    @patch('app.services.llm_service.OpenAI')
    def test_llm_service_init(self, mock_openai):
        """Test LLM service initialization."""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        service = LLMService(api_key="test_key", model="gpt-4")
        
        assert service.api_key == "test_key"
        assert service.model == "gpt-4"
        mock_openai.assert_called_once_with(api_key="test_key")
    
    @patch('app.services.llm_service.OpenAI')
    def test_llm_service_init_with_base_url(self, mock_openai):
        """Test LLM service initialization with base URL."""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        service = LLMService(api_key="test_key", model="gpt-4", base_url="https://api.test.com")
        
        assert service.base_url == "https://api.test.com"
        mock_openai.assert_called_once_with(api_key="test_key", base_url="https://api.test.com")
