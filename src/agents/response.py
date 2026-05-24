"""Response Agent - Generate contextual replies in Bahasa Indonesia."""
import httpx
from src.agents.nlu import Intent


class ResponseAgent:
    def __init__(self, llm_config: dict):
        self.model = llm_config["model"]
        self.base_url = llm_config["base_url"]
        import os
        self.api_key = os.environ.get("MIMO_API_KEY", llm_config.get("api_key", ""))
    
    async def generate(self, result, intent: Intent, phone: str) -> str:
        """Generate customer-facing response."""
        prompt = f"""Generate a WhatsApp reply for a retail kiosk customer service bot.

Context:
- Intent: {intent.type}
- Action result: {result.action}
- Data: {result.data}
- Success: {result.success}

Rules:
- Reply in casual Bahasa Indonesia (use "kak" as address)
- Keep it short (max 3 sentences for simple queries)
- Be helpful and friendly but not overly formal
- Include relevant product info (price, stock, location)
- If order: include total price and payment options
- Use Indonesian number format (titik for thousands: 85.000)
- NO emoji overuse, max 1-2 per message

Generate the reply text only, no explanation."""

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                },
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
    
    async def generate_clarification(self, message: str, intent: Intent) -> str:
        """Generate clarification question when intent is unclear."""
        return "Maaf kak, aku kurang paham maksudnya. Bisa dijelasin lagi? Aku bisa bantu cek stok, order, atau tracking pengiriman."
