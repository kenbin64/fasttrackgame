"""
ButterflyFX Stripe Payment Integration
======================================

Embedded Stripe Checkout - payments happen ON YOUR SITE.
Users never leave butterflyfx.us

Stripe Elements provides:
- Embedded card input (no redirect)
- Apple Pay / Google Pay support
- 3D Secure authentication
- PCI compliance handled by Stripe

Setup (Transaction fees only - no monthly cost):
1. Go to https://dashboard.stripe.com/
2. Create account → Get API keys
3. Set environment variables

Environment Variables:
    STRIPE_SECRET_KEY: sk_live_... or sk_test_...
    STRIPE_PUBLISHABLE_KEY: pk_live_... or pk_test_...
    STRIPE_WEBHOOK_SECRET: whsec_... (for webhooks)

Copyright (c) 2024-2026 Kenneth Bingham
All Rights Reserved
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum
import os
import json
import urllib.request
import urllib.error
import base64


class PaymentError(Exception):
    """Payment processing error"""
    pass


class SubscriptionStatus(Enum):
    """Stripe subscription status"""
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"


@dataclass
class StripeProduct:
    """Product in Stripe catalog"""
    id: str
    name: str
    description: str
    price_id: str              # Stripe Price ID
    price_cents: int           # Price in cents
    billing_interval: str      # "month", "year", "one_time"
    tier: str                  # "STARTER", "PROFESSIONAL", "ENTERPRISE"
    features: List[str] = field(default_factory=list)
    
    @property
    def price_dollars(self) -> float:
        return self.price_cents / 100


@dataclass
class PaymentIntent:
    """Represents a payment attempt"""
    id: str
    client_secret: str         # For frontend to confirm
    amount: int
    currency: str
    status: str
    customer_id: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class Subscription:
    """Active subscription"""
    id: str
    customer_id: str
    product_id: str
    price_id: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = False
    metadata: Dict[str, str] = field(default_factory=dict)


# =============================================================================
# BUTTERFLYFX PRODUCTS
# =============================================================================

BUTTERFLYFX_PRODUCTS: Dict[str, StripeProduct] = {
    # STARTER Tier - $9.99/month
    "starter_monthly": StripeProduct(
        id="starter_monthly",
        name="ButterflyFX Starter",
        description="Essential dimensional programming tools",
        price_id="",  # Set after creating in Stripe
        price_cents=999,
        billing_interval="month",
        tier="STARTER",
        features=[
            "Graphics Package (Pixel, Gradient, Shader substrates)",
            "CSS Animation Substrate",
            "Reports & Charts Substrate",
            "Database Connectors",
            "Email support",
            "Community Discord access",
        ],
    ),
    "starter_yearly": StripeProduct(
        id="starter_yearly",
        name="ButterflyFX Starter (Annual)",
        description="Essential dimensional programming tools - save 20%",
        price_id="",
        price_cents=9590,  # $95.90/year (~$7.99/month)
        billing_interval="year",
        tier="STARTER",
        features=[
            "Everything in Starter Monthly",
            "20% discount",
            "Priority email support",
        ],
    ),
    
    # PROFESSIONAL Tier - $29.99/month
    "professional_monthly": StripeProduct(
        id="professional_monthly",
        name="ButterflyFX Professional",
        description="Advanced dimensional computing suite",
        price_id="",
        price_cents=2999,
        billing_interval="month",
        tier="PROFESSIONAL",
        features=[
            "Everything in Starter",
            "Media Package (Audio, Video substrates)",
            "AI Substrate (LLM integration)",
            "3D Graphics Engine",
            "Priority support",
            "Early access to new features",
            "Commercial license",
        ],
    ),
    "professional_yearly": StripeProduct(
        id="professional_yearly",
        name="ButterflyFX Professional (Annual)",
        description="Advanced dimensional computing suite - save 20%",
        price_id="",
        price_cents=28790,  # $287.90/year (~$23.99/month)
        billing_interval="year",
        tier="PROFESSIONAL",
        features=[
            "Everything in Professional Monthly",
            "20% annual discount",
            "1:1 onboarding call",
            "Private Slack channel",
        ],
    ),
    
    # ENTERPRISE - Contact sales
    "enterprise": StripeProduct(
        id="enterprise",
        name="ButterflyFX Enterprise",
        description="Full platform access with enterprise support",
        price_id="",
        price_cents=0,  # Custom pricing
        billing_interval="custom",
        tier="ENTERPRISE",
        features=[
            "Everything in Professional",
            "Unlimited API calls",
            "Custom integrations",
            "Dedicated support engineer",
            "SLA guarantee",
            "On-premise deployment option",
            "Training sessions",
        ],
    ),
}


# =============================================================================
# STRIPE API CLIENT
# =============================================================================

class StripeClient:
    """
    Stripe API client for embedded checkout.
    
    Key endpoints used:
    - Payment Intents: For one-time payments
    - Checkout Sessions: For subscription setup
    - Customer Portal: For subscription management
    - Webhooks: For payment confirmation
    """
    
    API_BASE = "https://api.stripe.com/v1"
    API_VERSION = "2023-10-16"
    
    def __init__(self, secret_key: str = None, publishable_key: str = None):
        self.secret_key = secret_key or os.environ.get('STRIPE_SECRET_KEY', '')
        self.publishable_key = publishable_key or os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
        self.webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
        
        if not self.secret_key:
            print("⚠️  STRIPE_SECRET_KEY not set - payments will not work")
    
    @property
    def is_configured(self) -> bool:
        """Check if Stripe is properly configured"""
        return bool(self.secret_key and self.publishable_key)
    
    @property
    def is_test_mode(self) -> bool:
        """Check if using test keys"""
        return self.secret_key.startswith('sk_test_')
    
    def _request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make authenticated request to Stripe API"""
        url = f"{self.API_BASE}/{endpoint}"
        
        headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Stripe-Version': self.API_VERSION,
        }
        
        body = None
        if data:
            # Stripe uses form encoding, not JSON
            body = self._encode_data(data).encode('utf-8')
        
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            try:
                error_json = json.loads(error_body)
                error_msg = error_json.get('error', {}).get('message', error_body)
            except:
                error_msg = error_body
            raise PaymentError(f"Stripe API error: {error_msg}")
    
    def _encode_data(self, data: Dict, prefix: str = "") -> str:
        """Encode nested dict as Stripe form data"""
        pairs = []
        for key, value in data.items():
            full_key = f"{prefix}[{key}]" if prefix else key
            if isinstance(value, dict):
                pairs.append(self._encode_data(value, full_key))
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        pairs.append(self._encode_data(item, f"{full_key}[{i}]"))
                    else:
                        pairs.append(f"{full_key}[{i}]={urllib.parse.quote(str(item))}")
            else:
                pairs.append(f"{full_key}={urllib.parse.quote(str(value))}")
        return '&'.join(pairs)
    
    # -------------------------------------------------------------------------
    # CUSTOMERS
    # -------------------------------------------------------------------------
    
    def create_customer(self, email: str, name: str = "", metadata: Dict = None) -> Dict:
        """Create a Stripe customer"""
        data = {
            'email': email,
        }
        if name:
            data['name'] = name
        if metadata:
            data['metadata'] = metadata
        
        return self._request('POST', 'customers', data)
    
    def get_customer(self, customer_id: str) -> Dict:
        """Get customer details"""
        return self._request('GET', f'customers/{customer_id}')
    
    def find_customer_by_email(self, email: str) -> Optional[Dict]:
        """Find customer by email"""
        result = self._request('GET', f'customers?email={urllib.parse.quote(email)}&limit=1')
        customers = result.get('data', [])
        return customers[0] if customers else None
    
    # -------------------------------------------------------------------------
    # PAYMENT INTENTS (One-time payments)
    # -------------------------------------------------------------------------
    
    def create_payment_intent(self, amount_cents: int, currency: str = "usd",
                              customer_id: str = None, metadata: Dict = None) -> PaymentIntent:
        """
        Create a PaymentIntent for embedded checkout.
        
        The client_secret is used by Stripe.js on the frontend to confirm payment.
        """
        data = {
            'amount': amount_cents,
            'currency': currency,
            'automatic_payment_methods': {'enabled': 'true'},
        }
        if customer_id:
            data['customer'] = customer_id
        if metadata:
            data['metadata'] = metadata
        
        result = self._request('POST', 'payment_intents', data)
        
        return PaymentIntent(
            id=result['id'],
            client_secret=result['client_secret'],
            amount=result['amount'],
            currency=result['currency'],
            status=result['status'],
            customer_id=result.get('customer'),
            metadata=result.get('metadata', {}),
        )
    
    def get_payment_intent(self, payment_intent_id: str) -> Dict:
        """Get payment intent status"""
        return self._request('GET', f'payment_intents/{payment_intent_id}')
    
    # -------------------------------------------------------------------------
    # CHECKOUT SESSIONS (Subscriptions)
    # -------------------------------------------------------------------------
    
    def create_checkout_session(self, 
                                 price_id: str,
                                 success_url: str,
                                 cancel_url: str,
                                 customer_email: str = None,
                                 customer_id: str = None,
                                 mode: str = "subscription",
                                 metadata: Dict = None) -> Dict:
        """
        Create a Checkout Session for subscription.
        
        While this redirects to Stripe-hosted page, it returns to your site.
        For fully embedded, use create_subscription_intent instead.
        """
        data = {
            'mode': mode,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': [{'price': price_id, 'quantity': '1'}],
        }
        if customer_email:
            data['customer_email'] = customer_email
        if customer_id:
            data['customer'] = customer_id
        if metadata:
            data['metadata'] = metadata
        
        return self._request('POST', 'checkout/sessions', data)
    
    # -------------------------------------------------------------------------
    # EMBEDDED CHECKOUT (No redirect)
    # -------------------------------------------------------------------------
    
    def create_embedded_checkout(self,
                                  price_id: str,
                                  return_url: str,
                                  customer_email: str = None,
                                  mode: str = "subscription") -> Dict:
        """
        Create embedded checkout session.
        
        This uses Stripe's Embedded Checkout which renders completely on your site.
        The return_url is where users go after completing payment.
        """
        data = {
            'mode': mode,
            'ui_mode': 'embedded',
            'return_url': return_url + "?session_id={CHECKOUT_SESSION_ID}",
            'line_items': [{'price': price_id, 'quantity': '1'}],
        }
        if customer_email:
            data['customer_email'] = customer_email
        
        result = self._request('POST', 'checkout/sessions', data)
        
        return {
            'session_id': result['id'],
            'client_secret': result['client_secret'],  # Used by Stripe.js
        }
    
    # -------------------------------------------------------------------------
    # SUBSCRIPTIONS
    # -------------------------------------------------------------------------
    
    def get_subscription(self, subscription_id: str) -> Dict:
        """Get subscription details"""
        return self._request('GET', f'subscriptions/{subscription_id}')
    
    def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> Dict:
        """Cancel subscription"""
        data = {}
        if at_period_end:
            data['cancel_at_period_end'] = 'true'
        else:
            # Immediate cancellation
            return self._request('DELETE', f'subscriptions/{subscription_id}')
        
        return self._request('POST', f'subscriptions/{subscription_id}', data)
    
    def list_subscriptions(self, customer_id: str) -> List[Dict]:
        """List customer's subscriptions"""
        result = self._request('GET', f'subscriptions?customer={customer_id}')
        return result.get('data', [])
    
    # -------------------------------------------------------------------------
    # CUSTOMER PORTAL
    # -------------------------------------------------------------------------
    
    def create_portal_session(self, customer_id: str, return_url: str) -> Dict:
        """
        Create a Customer Portal session.
        
        Allows customers to manage their subscriptions, update payment methods, etc.
        """
        data = {
            'customer': customer_id,
            'return_url': return_url,
        }
        return self._request('POST', 'billing_portal/sessions', data)
    
    # -------------------------------------------------------------------------
    # WEBHOOKS
    # -------------------------------------------------------------------------
    
    def verify_webhook(self, payload: bytes, signature: str) -> Dict:
        """
        Verify webhook signature and parse payload.
        
        Args:
            payload: Raw request body bytes
            signature: Stripe-Signature header value
            
        Returns:
            Parsed webhook event
        """
        import hmac
        import hashlib
        
        if not self.webhook_secret:
            raise PaymentError("Webhook secret not configured")
        
        # Parse signature header
        parts = dict(part.split('=', 1) for part in signature.split(','))
        timestamp = parts.get('t', '')
        expected_sig = parts.get('v1', '')
        
        # Compute expected signature
        signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
        computed_sig = hmac.new(
            self.webhook_secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Constant-time comparison
        if not hmac.compare_digest(computed_sig, expected_sig):
            raise PaymentError("Invalid webhook signature")
        
        return json.loads(payload)


# =============================================================================
# PAYMENT SERVICE
# =============================================================================

class PaymentService:
    """
    High-level payment service for ButterflyFX.
    
    Handles:
    - Product catalog
    - Customer creation
    - Subscription management
    - Payment verification
    - User tier upgrades
    """
    
    def __init__(self):
        self.stripe = StripeClient()
        self.products = BUTTERFLYFX_PRODUCTS
    
    def get_checkout_data(self, product_id: str, user_email: str) -> Dict[str, Any]:
        """
        Get data needed for frontend to render embedded checkout.
        
        Returns:
            {
                'publishable_key': 'pk_...',
                'client_secret': '...',
                'product': {...},
            }
        """
        product = self.products.get(product_id)
        if not product:
            raise PaymentError(f"Unknown product: {product_id}")
        
        if not product.price_id:
            raise PaymentError(f"Product {product_id} not configured in Stripe")
        
        # Create embedded checkout session
        checkout = self.stripe.create_embedded_checkout(
            price_id=product.price_id,
            return_url=f"https://butterflyfx.us/payment/success",
            customer_email=user_email,
            mode="subscription" if product.billing_interval != "one_time" else "payment",
        )
        
        return {
            'publishable_key': self.stripe.publishable_key,
            'client_secret': checkout['client_secret'],
            'session_id': checkout['session_id'],
            'product': {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price_dollars,
                'interval': product.billing_interval,
                'tier': product.tier,
                'features': product.features,
            },
        }
    
    def handle_successful_payment(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """
        Handle successful payment - upgrade user tier.
        
        Args:
            session_id: Stripe checkout session ID
            user_id: ButterflyFX user ID
            
        Returns:
            Updated user info
        """
        # Get session details from Stripe
        session = self.stripe._request('GET', f'checkout/sessions/{session_id}')
        
        if session.get('payment_status') != 'paid':
            raise PaymentError("Payment not completed")
        
        # Get subscription/payment details
        subscription_id = session.get('subscription')
        customer_id = session.get('customer')
        
        # Determine which tier was purchased
        # (In production, store price_id → tier mapping in Stripe metadata)
        line_items = self.stripe._request(
            'GET', 
            f'checkout/sessions/{session_id}/line_items'
        )
        
        # Update user tier in ButterflyFX
        from .service import AuthService
        from .models import UserTier
        
        auth = AuthService()
        user = auth.users.get(user_id)
        
        if user:
            # Determine tier from product
            # This is simplified - in production use metadata
            price_id = line_items['data'][0]['price']['id'] if line_items.get('data') else ""
            
            # Upgrade user
            user.tier = UserTier.DEV  # DEV tier includes all paid features
            user.stripe_customer_id = customer_id
            user.subscription_id = subscription_id
            auth._save_users()
            
            return {
                'success': True,
                'user_id': user_id,
                'new_tier': user.tier.name,
                'subscription_id': subscription_id,
            }
        
        raise PaymentError("User not found")
    
    def get_user_subscription(self, user_id: str) -> Optional[Dict]:
        """Get user's current subscription status"""
        from .service import AuthService
        
        auth = AuthService()
        user = auth.users.get(user_id)
        
        if not user or not hasattr(user, 'subscription_id') or not user.subscription_id:
            return None
        
        try:
            sub = self.stripe.get_subscription(user.subscription_id)
            return {
                'id': sub['id'],
                'status': sub['status'],
                'current_period_end': sub['current_period_end'],
                'cancel_at_period_end': sub.get('cancel_at_period_end', False),
            }
        except:
            return None
    
    def create_portal_link(self, user_id: str) -> str:
        """Create link to Stripe Customer Portal for subscription management"""
        from .service import AuthService
        
        auth = AuthService()
        user = auth.users.get(user_id)
        
        if not user or not hasattr(user, 'stripe_customer_id'):
            raise PaymentError("User has no payment history")
        
        session = self.stripe.create_portal_session(
            customer_id=user.stripe_customer_id,
            return_url="https://butterflyfx.us/account"
        )
        
        return session['url']


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_payment_service: Optional[PaymentService] = None

def get_payment_service() -> PaymentService:
    """Get singleton PaymentService instance"""
    global _payment_service
    if _payment_service is None:
        _payment_service = PaymentService()
    return _payment_service
