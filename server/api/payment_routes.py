"""
ButterflyFX Payment API Routes
==============================

REST API endpoints for payment processing.

Routes:
    GET  /api/payment/config          - Get Stripe publishable key
    POST /api/payment/create-subscription - Create subscription for user
    POST /api/payment/webhook         - Handle Stripe webhooks
    GET  /api/payment/subscription    - Get user's subscription status
    POST /api/payment/portal          - Create customer portal link

Copyright (c) 2024-2026 Kenneth Bingham
All Rights Reserved
"""

from typing import Dict, Any, Optional
import json
import os

# Import payment service
from ..auth.stripe_checkout import (
    get_payment_service,
    PaymentService,
    PaymentError,
    BUTTERFLYFX_PRODUCTS,
)
from ..auth.service import AuthService, SessionExpiredError


def handle_payment_config(request: Dict) -> Dict[str, Any]:
    """
    GET /api/payment/config
    
    Returns Stripe publishable key for frontend.
    """
    service = get_payment_service()
    
    return {
        'success': True,
        'publishable_key': service.stripe.publishable_key,
        'test_mode': service.stripe.is_test_mode,
    }


def handle_create_subscription(request: Dict) -> Dict[str, Any]:
    """
    POST /api/payment/create-subscription
    
    Creates a subscription for the authenticated user.
    
    Request body:
        {
            "tier": "starter" | "professional",
            "billing": "monthly" | "yearly"
        }
    
    Returns client_secret for Stripe.js to confirm payment.
    """
    # Validate session
    auth = AuthService()
    session_token = request.get('session_token')
    
    if not session_token:
        return {'error': 'Authentication required', 'success': False}
    
    try:
        session = auth.validate_session(session_token)
        user = auth.users.get(session.user_id)
    except SessionExpiredError:
        return {'error': 'Session expired', 'success': False}
    
    if not user:
        return {'error': 'User not found', 'success': False}
    
    # Get subscription parameters
    body = request.get('body', {})
    tier = body.get('tier', 'starter')
    billing = body.get('billing', 'monthly')
    
    # Map to product ID
    product_id = f"{tier}_{billing}"
    
    if product_id not in BUTTERFLYFX_PRODUCTS:
        return {'error': f'Unknown product: {product_id}', 'success': False}
    
    product = BUTTERFLYFX_PRODUCTS[product_id]
    
    try:
        service = get_payment_service()
        
        # Find or create Stripe customer
        customer = service.stripe.find_customer_by_email(user.email)
        if not customer:
            customer = service.stripe.create_customer(
                email=user.email,
                name=getattr(user, 'display_name', user.username),
                metadata={'butterflyfx_user_id': user.id}
            )
        
        customer_id = customer['id']
        
        # Store customer ID on user
        user.stripe_customer_id = customer_id
        auth._save_users()
        
        # Create payment intent for initial payment
        payment_intent = service.stripe.create_payment_intent(
            amount_cents=product.price_cents,
            currency='usd',
            customer_id=customer_id,
            metadata={
                'butterflyfx_user_id': user.id,
                'product_id': product_id,
                'tier': tier,
                'billing': billing,
            }
        )
        
        return {
            'success': True,
            'client_secret': payment_intent.client_secret,
            'payment_intent_id': payment_intent.id,
            'amount': product.price_cents,
            'product': {
                'id': product.id,
                'name': product.name,
                'price': product.price_dollars,
                'interval': product.billing_interval,
            }
        }
        
    except PaymentError as e:
        return {'error': str(e), 'success': False}
    except Exception as e:
        return {'error': f'Payment setup failed: {str(e)}', 'success': False}


def handle_webhook(request: Dict) -> Dict[str, Any]:
    """
    POST /api/payment/webhook
    
    Handle Stripe webhook events.
    
    Events handled:
        - payment_intent.succeeded
        - customer.subscription.created
        - customer.subscription.updated
        - customer.subscription.deleted
    """
    service = get_payment_service()
    
    payload = request.get('raw_body', b'')
    signature = request.get('headers', {}).get('Stripe-Signature', '')
    
    try:
        event = service.stripe.verify_webhook(payload, signature)
    except PaymentError as e:
        return {'error': str(e), 'success': False}
    
    event_type = event.get('type', '')
    data = event.get('data', {}).get('object', {})
    
    # Handle events
    if event_type == 'payment_intent.succeeded':
        _handle_payment_success(data)
    elif event_type == 'customer.subscription.created':
        _handle_subscription_created(data)
    elif event_type == 'customer.subscription.updated':
        _handle_subscription_updated(data)
    elif event_type == 'customer.subscription.deleted':
        _handle_subscription_deleted(data)
    
    return {'success': True, 'received': True}


def _handle_payment_success(payment_intent: Dict):
    """Process successful payment"""
    from ..auth.service import AuthService
    from ..auth.models import UserTier
    
    metadata = payment_intent.get('metadata', {})
    user_id = metadata.get('butterflyfx_user_id')
    tier = metadata.get('tier', 'starter')
    
    if not user_id:
        return
    
    auth = AuthService()
    user = auth.users.get(user_id)
    
    if user:
        # Upgrade user tier
        user.tier = UserTier.DEV
        user.payment_status = 'PAID'
        user.subscription_tier = tier
        auth._save_users()


def _handle_subscription_created(subscription: Dict):
    """Handle new subscription"""
    customer_id = subscription.get('customer')
    subscription_id = subscription.get('id')
    
    # Find user by customer ID and update
    from ..auth.service import AuthService
    
    auth = AuthService()
    for user in auth.users.values():
        if hasattr(user, 'stripe_customer_id') and user.stripe_customer_id == customer_id:
            user.subscription_id = subscription_id
            user.subscription_status = subscription.get('status')
            auth._save_users()
            break


def _handle_subscription_updated(subscription: Dict):
    """Handle subscription update (upgrade/downgrade/renewal)"""
    subscription_id = subscription.get('id')
    status = subscription.get('status')
    
    from ..auth.service import AuthService
    from ..auth.models import UserTier
    
    auth = AuthService()
    for user in auth.users.values():
        if hasattr(user, 'subscription_id') and user.subscription_id == subscription_id:
            user.subscription_status = status
            
            # If subscription is no longer active, downgrade user
            if status not in ('active', 'trialing'):
                user.tier = UserTier.USER
                user.payment_status = 'EXPIRED'
            
            auth._save_users()
            break


def _handle_subscription_deleted(subscription: Dict):
    """Handle subscription cancellation"""
    subscription_id = subscription.get('id')
    
    from ..auth.service import AuthService
    from ..auth.models import UserTier
    
    auth = AuthService()
    for user in auth.users.values():
        if hasattr(user, 'subscription_id') and user.subscription_id == subscription_id:
            user.tier = UserTier.USER
            user.payment_status = 'CANCELLED'
            user.subscription_status = 'canceled'
            auth._save_users()
            break


def handle_get_subscription(request: Dict) -> Dict[str, Any]:
    """
    GET /api/payment/subscription
    
    Get current user's subscription status.
    """
    auth = AuthService()
    session_token = request.get('session_token')
    
    if not session_token:
        return {'error': 'Authentication required', 'success': False}
    
    try:
        session = auth.validate_session(session_token)
        user = auth.users.get(session.user_id)
    except SessionExpiredError:
        return {'error': 'Session expired', 'success': False}
    
    if not user:
        return {'error': 'User not found', 'success': False}
    
    subscription = None
    if hasattr(user, 'subscription_id') and user.subscription_id:
        service = get_payment_service()
        subscription = service.get_user_subscription(user.id)
    
    return {
        'success': True,
        'tier': user.tier.name if hasattr(user.tier, 'name') else str(user.tier),
        'subscription': subscription,
        'payment_status': getattr(user, 'payment_status', 'UNPAID'),
    }


def handle_create_portal(request: Dict) -> Dict[str, Any]:
    """
    POST /api/payment/portal
    
    Create a Stripe Customer Portal link for subscription management.
    """
    auth = AuthService()
    session_token = request.get('session_token')
    
    if not session_token:
        return {'error': 'Authentication required', 'success': False}
    
    try:
        session = auth.validate_session(session_token)
        user = auth.users.get(session.user_id)
    except SessionExpiredError:
        return {'error': 'Session expired', 'success': False}
    
    if not user:
        return {'error': 'User not found', 'success': False}
    
    if not hasattr(user, 'stripe_customer_id') or not user.stripe_customer_id:
        return {'error': 'No payment history found', 'success': False}
    
    try:
        service = get_payment_service()
        url = service.create_portal_link(user.id)
        return {'success': True, 'url': url}
    except PaymentError as e:
        return {'error': str(e), 'success': False}


# Route handler mapping
PAYMENT_ROUTES = {
    ('GET', '/api/payment/config'): handle_payment_config,
    ('POST', '/api/payment/create-subscription'): handle_create_subscription,
    ('POST', '/api/payment/webhook'): handle_webhook,
    ('GET', '/api/payment/subscription'): handle_get_subscription,
    ('POST', '/api/payment/portal'): handle_create_portal,
}
