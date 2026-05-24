"""Analytics Agent - Nightly business intelligence."""
import httpx
from datetime import datetime, timedelta


class AnalyticsAgent:
    def __init__(self, config: dict):
        self.config = config
        self.model = config["llm"]["model"]
        self.base_url = config["llm"]["base_url"]
        import os
        self.api_key = os.environ.get("MIMO_API_KEY", "")
    
    async def generate_daily_report(self) -> str:
        """Generate daily business report."""
        # Fetch today's data
        today = datetime.now().strftime("%Y-%m-%d")
        
        # In production: query database for sales, inventory, interactions
        # Simplified for demo
        report_data = {
            "date": today,
            "total_sales": 0,
            "total_orders": 0,
            "total_interactions": 0,
            "top_products": [],
            "low_stock_alerts": [],
            "customer_satisfaction": 0,
        }
        
        prompt = f"""Generate a concise daily business report in Bahasa Indonesia for kiosk owners.

Data:
{report_data}

Format as WhatsApp message (plain text, use line breaks).
Include: total penjualan, jumlah order, produk terlaris, alert stok menipis, saran restock.
Keep it under 500 characters."""

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                },
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            result = response.json()
            return result["choices"][0]["message"]["content"]
