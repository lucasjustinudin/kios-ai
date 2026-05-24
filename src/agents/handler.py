"""Handler Agent - Business logic execution."""
from dataclasses import dataclass
from typing import Optional
from src.agents.nlu import Intent
from src.integrations.inventory import InventoryDB


@dataclass
class HandlerResult:
    success: bool
    action: str
    data: dict
    message_context: str = ""


class HandlerAgent:
    def __init__(self, config: dict):
        self.config = config
        self.inventory = InventoryDB(config["inventory"])
    
    async def process(self, intent: Intent, phone: str) -> HandlerResult:
        """Process classified intent and execute business logic."""
        if intent.type == "product_inquiry":
            return await self._handle_product_inquiry(intent)
        elif intent.type == "order":
            return await self._handle_order(intent, phone)
        elif intent.type == "tracking":
            return await self._handle_tracking(intent)
        elif intent.type == "complaint":
            return await self._handle_complaint(intent, phone)
        elif intent.type == "promo":
            return await self._handle_promo(intent)
        elif intent.type == "greeting":
            return HandlerResult(success=True, action="greeting", data={})
        else:
            return HandlerResult(success=False, action="unknown", data={})
    
    async def _handle_product_inquiry(self, intent: Intent) -> HandlerResult:
        """Check product availability across locations."""
        product = intent.entities.get("product", "")
        location = intent.entities.get("location")
        
        results = await self.inventory.search_product(product, location=location)
        
        return HandlerResult(
            success=bool(results),
            action="product_inquiry",
            data={"products": results, "query": product}
        )
    
    async def _handle_order(self, intent: Intent, phone: str) -> HandlerResult:
        """Create order and generate payment link."""
        product = intent.entities.get("product", "")
        quantity = int(intent.entities.get("quantity", 1))
        
        # Check stock
        stock = await self.inventory.check_stock(product)
        if not stock or stock["available"] < quantity:
            return HandlerResult(
                success=False,
                action="order_failed",
                data={"reason": "out_of_stock", "available": stock.get("available", 0) if stock else 0}
            )
        
        # Create order
        order = await self.inventory.create_order(phone, product, quantity)
        
        return HandlerResult(
            success=True,
            action="order_created",
            data={"order": order}
        )
    
    async def _handle_tracking(self, intent: Intent) -> HandlerResult:
        """Track delivery status."""
        order_id = intent.entities.get("order_id")
        # ... tracking logic
        return HandlerResult(success=True, action="tracking", data={})
    
    async def _handle_complaint(self, intent: Intent, phone: str) -> HandlerResult:
        """Log complaint and prepare resolution."""
        return HandlerResult(
            success=True,
            action="complaint_logged",
            data={"escalate": True}
        )
    
    async def _handle_promo(self, intent: Intent) -> HandlerResult:
        """Get active promotions."""
        promos = await self.inventory.get_active_promos()
        return HandlerResult(success=True, action="promo", data={"promos": promos})
