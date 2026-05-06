import json
import httpx
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class LLMCategorizer:
    """Service to categorize transactions using a local Ollama instance."""

    def __init__(self, model: str = "qwen2.5:latest", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"

    async def categorize_transaction(
        self, payee: str, amount: float, date: str, existing_categories: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Send a transaction to Ollama for categorization.
        Returns a dict with 'category', 'category_group', and 'confidence'.
        """
        prompt = self._build_prompt(payee, amount, date, existing_categories)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    json={"model": self.model, "prompt": prompt, "stream": False, "format": "json"},
                )

                if response.status_code != 200:
                    logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                    return None

                result = response.json()
                response_text = result.get("response", "{}")

                try:
                    category_data = json.loads(response_text)
                    # Basic validation of expected keys
                    if "category" in category_data and "category_group" in category_data:
                        return {
                            "category": category_data["category"],
                            "category_group": category_data["category_group"],
                            "confidence": category_data.get("confidence", 0.5),
                        }
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse LLM response as JSON: {response_text}")

        except Exception as e:
            logger.error(f"Error calling LLM service: {e}")

        return None

    def _build_prompt(
        self, payee: str, amount: float, date: str, existing_categories: List[str]
    ) -> str:
        categories_str = ", ".join(existing_categories)
        return f"""
        Analyze this financial transaction and categorize it.

        Transaction:
        - Payee: {payee}
        - Amount: {amount}
        - Date: {date}

        Available Categories: {categories_str}

        Respond with ONLY a JSON object in this format:
        {{
            "category": "Selected Category",
            "category_group": "Parent Group",
            "confidence": 0.9
        }}

        Rules:
        1. If it's a known store like Costco, decide between 'Groceries' or 'Shopping' based on the amount and context.
        2. Prefer using one of the 'Available Categories' if it fits.
        3. 'category_group' should be the broad category (e.g., 'Food', 'Housing', 'Transport').
        4. 'category' should be the specific sub-category.
        """
