"""WhatsApp Business API integration."""
import httpx


class WhatsAppClient:
    def __init__(self, config: dict):
        self.provider = config["provider"]
        import os
        self.api_key = os.environ.get("FONNTE_API_KEY", config.get("api_key", ""))
    
    async def send(self, phone: str, message: str):
        """Send WhatsApp message."""
        if self.provider == "fonnte":
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(
                    "https://api.fonnte.com/send",
                    json={"target": phone, "message": message},
                    headers={"Authorization": self.api_key}
                )
