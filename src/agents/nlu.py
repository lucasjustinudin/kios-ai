"""NLU Agent - Intent classification and entity extraction."""
import httpx
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Intent:
    type: str  # product_inquiry, order, complaint, tracking, promo, greeting, other
    confidence: float
    entities: dict = field(default_factory=dict)  # product, quantity, location, etc.
    requires_escalation: bool = False
    context: str = ""


class NLUAgent:
    def __init__(self, llm_config: dict):
        self.model = llm_config["model"]
        self.base_url = llm_config["base_url"]
        import os
        self.api_key = os.environ.get("MIMO_API_KEY", llm_config.get("api_key", ""))
        self.conversation_history = {}  # phone -> last N messages
    
    async def classify(self, message: str, phone: str) -> Intent:
        """Classify customer message intent with entity extraction."""
        history = self.conversation_history.get(phone, [])
        history_text = "\n".join([f"- {m}" for m in history[-3:]]) if history else "No previous messages"
        
        prompt = f"""Classify this Indonesian customer message for a retail kiosk:

Message: "{message}"
Previous messages from this customer:
{history_text}

Classify intent as ONE of:
- product_inquiry: asking about product availability, price, specs
- order: wants to buy/order something
- complaint: unhappy about product/service
- tracking: asking about delivery status
- promo: asking about discounts/promotions
- greeting: just saying hi/thanks
- escalation: needs human help (complex issue, angry customer)
- other: doesn't fit above categories

Extract entities:
- product: product name/description mentioned
- quantity: number of items
- location: kiosk location or delivery address
- order_id: if tracking

Return JSON: {{"type": str, "confidence": float, "entities": {{}}, "requires_escalation": bool}}

Handle informal Bahasa: "ga" = "tidak", "dong" = emphasis, "kak" = polite address, "brp" = "berapa", "mau" = "want"."""

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                },
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            result = response.json()
            content = result["choices"][0]["message"]["content"]
        
        # Update history
        if phone not in self.conversation_history:
            self.conversation_history[phone] = []
        self.conversation_history[phone].append(message)
        if len(self.conversation_history[phone]) > 10:
            self.conversation_history[phone] = self.conversation_history[phone][-10:]
        
        return self._parse_intent(content)
    
    def _parse_intent(self, content: str) -> Intent:
        """Parse LLM output into Intent object."""
        import json
        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            data = json.loads(content)
            return Intent(
                type=data.get("type", "other"),
                confidence=data.get("confidence", 0.5),
                entities=data.get("entities", {}),
                requires_escalation=data.get("requires_escalation", False)
            )
        except:
            return Intent(type="other", confidence=0.3)
