import stripe
from typing import Dict, Optional
import structlog
from app.core.config import settings

logger = structlog.get_logger()

class StripeService:
    """Service for handling payment processing via Stripe"""
    
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    
    async def create_payment_intent(self, amount: int, currency: str = "usd", 
                                  metadata: Dict = None) -> Dict:
        """Create a Stripe Payment Intent for deal payments"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount * 100,  # Stripe uses cents
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={'enabled': True}
            )
            
            logger.info("Payment intent created", 
                       intent_id=intent.id,
                       amount=amount,
                       currency=currency)
            
            return {
                "client_secret": intent.client_secret,
                "intent_id": intent.id,
                "amount": amount,
                "status": intent.status
            }
            
        except stripe.error.StripeError as e:
            logger.error("Stripe payment intent creation failed", error=str(e))
            raise Exception(f"Payment processing error: {str(e)}")
    
    async def confirm_payment(self, payment_intent_id: str) -> Dict:
        """Confirm a payment and update deal status"""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status == "succeeded":
                logger.info("Payment confirmed successfully", intent_id=payment_intent_id)
                return {
                    "status": "confirmed",
                    "amount_received": intent.amount_received / 100,
                    "payment_method": intent.payment_method
                }
            else:
                logger.warning("Payment confirmation pending", 
                              intent_id=payment_intent_id,
                              status=intent.status)
                return {
                    "status": intent.status,
                    "requires_action": intent.status == "requires_action"
                }
                
        except stripe.error.StripeError as e:
            logger.error("Payment confirmation failed", 
                        intent_id=payment_intent_id,
                        error=str(e))
            raise Exception(f"Payment confirmation error: {str(e)}")
    
    async def create_connected_account(self, brand_id: str, business_info: Dict) -> Dict:
        """Create Stripe Connected Account for brand payouts"""
        try:
            account = stripe.Account.create(
                type="express",
                country=business_info.get("country", "US"),
                email=business_info.get("email"),
                business_profile={
                    "name": business_info.get("business_name"),
                    "product_description": "NIL deals and athlete endorsements"
                },
                metadata={"brand_id": brand_id}
            )
            
            logger.info("Connected account created", 
                       account_id=account.id,
                       brand_id=brand_id)
            
            return {
                "account_id": account.id,
                "onboarding_url": self._create_account_link(account.id),
                "status": account.details_submitted
            }
            
        except stripe.error.StripeError as e:
            logger.error("Connected account creation failed", 
                        brand_id=brand_id,
                        error=str(e))
            raise Exception(f"Account setup error: {str(e)}")
    
    def _create_account_link(self, account_id: str) -> str:
        """Create account onboarding link"""
        try:
            account_link = stripe.AccountLink.create(
                account=account_id,
                refresh_url=f"{settings.FRONTEND_URL}/onboarding/refresh",
                return_url=f"{settings.FRONTEND_URL}/onboarding/complete",
                type="account_onboarding"
            )
            return account_link.url
        except stripe.error.StripeError:
            return ""
    
    async def process_athlete_payout(self, athlete_id: str, amount: float, 
                                   deal_id: str) -> Dict:
        """Process payout to athlete for completed deal"""
        try:
            # This would integrate with athlete's connected account or bank info
            # For now, create a transfer record
            
            transfer = {
                "athlete_id": athlete_id,
                "amount": amount,
                "deal_id": deal_id,
                "status": "processed",
                "processed_at": "2024-01-01T00:00:00Z"
            }
            
            logger.info("Athlete payout processed", 
                       athlete_id=athlete_id,
                       amount=amount,
                       deal_id=deal_id)
            
            return transfer
            
        except Exception as e:
            logger.error("Athlete payout failed",
                        athlete_id=athlete_id,
                        amount=amount,
                        error=str(e))
            raise
    
    async def handle_webhook(self, payload: str, sig_header: str) -> Dict:
        """Handle Stripe webhook events"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            
            logger.info("Stripe webhook received", event_type=event["type"])
            
            if event["type"] == "payment_intent.succeeded":
                await self._handle_payment_success(event["data"]["object"])
            elif event["type"] == "payment_intent.payment_failed":
                await self._handle_payment_failure(event["data"]["object"])
            
            return {"status": "processed"}
            
        except ValueError as e:
            logger.error("Invalid webhook payload", error=str(e))
            raise Exception("Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            logger.error("Invalid webhook signature", error=str(e))
            raise Exception("Invalid signature")
    
    async def _handle_payment_success(self, payment_intent: Dict):
        """Handle successful payment webhook"""
        deal_id = payment_intent.get("metadata", {}).get("deal_id")
        if deal_id:
            # Update deal status in PocketBase
            # This would be implemented with actual deal update logic
            logger.info("Payment success processed", deal_id=deal_id)
    
    async def _handle_payment_failure(self, payment_intent: Dict):
        """Handle failed payment webhook"""
        deal_id = payment_intent.get("metadata", {}).get("deal_id")
        if deal_id:
            # Handle payment failure
            logger.error("Payment failed for deal", deal_id=deal_id)