"""Kios AI - WhatsApp retail automation platform."""
import asyncio
import logging
from src.agents.nlu import NLUAgent
from src.agents.handler import HandlerAgent
from src.agents.response import ResponseAgent
from src.agents.analytics import AnalyticsAgent
from src.integrations.whatsapp import WhatsAppClient
from src.integrations.inventory import InventoryDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KiosAI:
    def __init__(self, config_path: str = "config/config.yaml"):
        import yaml
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.nlu = NLUAgent(self.config["llm"])
        self.handler = HandlerAgent(self.config)
        self.response = ResponseAgent(self.config["llm"])
        self.analytics = AnalyticsAgent(self.config)
        self.wa = WhatsAppClient(self.config["whatsapp"])
        self.inventory = InventoryDB(self.config["inventory"])
    
    async def handle_message(self, phone: str, message: str):
        """Process incoming WhatsApp message through agent pipeline."""
        logger.info(f"Message from {phone}: {message[:50]}...")
        
        # Phase 1: Understand intent
        intent = await self.nlu.classify(message, phone)
        logger.info(f"Intent: {intent.type} (confidence: {intent.confidence:.2f})")
        
        # Phase 2: Execute business logic
        if intent.confidence < 0.6:
            # Low confidence - ask for clarification
            reply = await self.response.generate_clarification(message, intent)
        elif intent.requires_escalation:
            reply = await self._escalate(phone, message, intent)
        else:
            result = await self.handler.process(intent, phone)
            # Phase 3: Generate response
            reply = await self.response.generate(result, intent, phone)
        
        # Send reply
        await self.wa.send(phone, reply)
        logger.info(f"Reply sent to {phone}: {reply[:50]}...")
    
    async def _escalate(self, phone: str, message: str, intent):
        """Escalate to human operator with context."""
        context = f"Customer {phone} needs help.\nMessage: {message}\nDetected intent: {intent.type}"
        for admin in self.config.get("escalation", {}).get("admins", []):
            await self.wa.send(admin, f"[ESCALATION]\n{context}")
        return "Terima kasih kak, aku sambungkan ke tim kami ya. Mohon tunggu sebentar."
    
    async def run_nightly_analytics(self):
        """Run nightly analytics and send reports."""
        report = await self.analytics.generate_daily_report()
        for recipient in self.config["analytics"]["report_recipients"]:
            await self.wa.send(recipient, report)
        logger.info("Nightly analytics report sent")
    
    async def start(self):
        """Start the webhook server and scheduler."""
        from aiohttp import web
        import aiocron
        
        # Schedule nightly analytics
        cron_schedule = self.config["analytics"]["schedule"]
        aiocron.crontab(cron_schedule, func=self.run_nightly_analytics)
        
        # Webhook server
        app = web.Application()
        app.router.add_post("/webhook/wa", self._webhook_handler)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", 8080)
        await site.start()
        logger.info("Kios AI started on port 8080")
        
        # Keep running
        await asyncio.Event().wait()
    
    async def _webhook_handler(self, request):
        """Handle incoming WhatsApp webhook."""
        from aiohttp import web
        data = await request.json()
        phone = data.get("sender", "")
        message = data.get("message", "")
        if phone and message:
            asyncio.create_task(self.handle_message(phone, message))
        return web.json_response({"status": "ok"})


if __name__ == "__main__":
    kios = KiosAI()
    asyncio.run(kios.start())
