import pytest
from src.backend.llm_service import LLMCategorizer
import unittest.mock as mock

@pytest.mark.asyncio
async def test_categorize_transaction_mock():
    categorizer = LLMCategorizer()

    # Mock response from Ollama
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": '{"category": "Groceries", "category_group": "Food", "confidence": 0.95}'
    }

    with mock.patch("httpx.AsyncClient.post", return_value=mock_response):
        result = await categorizer.categorize_transaction(
            payee="Costco",
            amount=-150.0,
            date="2024-01-01",
            existing_categories=["Groceries", "Shopping"]
        )

        assert result is not None
        assert result["category"] == "Groceries"
        assert result["category_group"] == "Food"
        assert result["confidence"] == 0.95

def test_build_prompt():
    categorizer = LLMCategorizer()
    prompt = categorizer._build_prompt("Costco", -150.0, "2024-01-01", ["Groceries", "Shopping"])
    assert "Costco" in prompt
    assert "Groceries, Shopping" in prompt
