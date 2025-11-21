from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from typing import List, Optional
import stripe
import os
from datetime import datetime
import logging

from app.db.session import get_db
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderResponse, OrderListResponse

router = APIRouter()

from app.core.config import settings

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Configure logging
logger = logging.getLogger(__name__)

# In-memory set to track processed webhook events (use Redis in production)
# This provides basic idempotency protection
processed_webhook_events = set()


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new order after payment is completed.
    Validates the Stripe session before creating the order.
    """
    # Validate Stripe session
    try:
        session = stripe.checkout.Session.retrieve(order_data.stripe_session_id)

        if session.payment_status != "paid":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment not completed. Session status: " + session.payment_status
            )

        # Check if order already exists for this session
        existing_order = db.query(Order).filter(
            Order.stripe_session_id == order_data.stripe_session_id
        ).first()

        if existing_order:
            # Return existing order instead of creating duplicate
            return existing_order

        # Create new order
        order = Order(
            stripe_session_id=order_data.stripe_session_id,
            stripe_payment_id=str(session.payment_intent) if session.payment_intent else None,
            payment_status="paid",
            amount_paid=session.amount_total or 0,
            agency_name=order_data.agency_name,
            contact_email=order_data.contact_email,
            site_name=order_data.site_name,
            site_url=order_data.site_url,
            wp_current_version=order_data.wp_current_version,
            wp_target_version=order_data.wp_target_version,
            plugin_list=order_data.plugin_list,
            theme_name=order_data.theme_name,
            theme_version=order_data.theme_version,
            custom_notes=order_data.custom_notes,
            analysis_status="pending"
        )

        db.add(order)
        db.commit()
        db.refresh(order)

        return order

    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating order: {str(e)}"
        )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific order by ID.
    """
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    return order


@router.get("/", response_model=OrderListResponse)
async def list_orders(
    page: int = 1,
    per_page: int = 20,
    analysis_status: str = None,
    db: Session = Depends(get_db)
):
    """
    List all orders with pagination and optional filtering.
    """
    query = db.query(Order)

    if analysis_status:
        query = query.filter(Order.analysis_status == analysis_status)

    total = query.count()

    orders = query.order_by(Order.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()

    return OrderListResponse(
        orders=orders,
        total=total,
        page=page,
        per_page=per_page
    )


@router.post("/webhooks/stripe", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="Stripe-Signature"),
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events with signature verification

    This endpoint receives and processes Stripe webhook events securely by:
    1. Verifying the webhook signature to ensure requests are from Stripe
    2. Implementing idempotency to prevent duplicate event processing
    3. Handling checkout.session.completed events to update order status

    SECURITY: This endpoint MUST verify webhook signatures to prevent
    unauthorized requests from malicious actors.

    Args:
        request: FastAPI Request object containing the raw webhook payload
        stripe_signature: Stripe-Signature header for verification
        db: Database session

    Returns:
        Success status

    Raises:
        HTTPException: 400 if signature is invalid or missing
    """
    # Get raw request body (required for signature verification)
    try:
        payload = await request.body()
    except Exception as e:
        logger.error(f"Error reading webhook payload: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload"
        )

    # Verify webhook signature if STRIPE_WEBHOOK_SECRET is configured
    if settings.STRIPE_WEBHOOK_SECRET:
        if not stripe_signature:
            logger.warning("Stripe webhook received without signature header")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing Stripe-Signature header"
            )

        try:
            # Verify the webhook signature and construct the event
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=stripe_signature,
                secret=settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            # Invalid payload
            logger.error(f"Invalid Stripe webhook payload: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payload"
            )
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            logger.error(f"Invalid Stripe webhook signature: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid signature"
            )
    else:
        # DEVELOPMENT ONLY: Parse event without signature verification
        # WARNING: This is insecure and should only be used in development
        logger.warning("STRIPE_WEBHOOK_SECRET not configured - webhook signature verification disabled")
        try:
            event = stripe.Event.construct_from(
                values=await request.json(),
                key=settings.STRIPE_SECRET_KEY
            )
        except Exception as e:
            logger.error(f"Error parsing webhook event: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event data"
            )

    # Implement idempotency: check if we've already processed this event
    event_id = event.get("id")
    if event_id in processed_webhook_events:
        logger.info(f"Duplicate webhook event {event_id} - already processed")
        return {"status": "success", "message": "Event already processed"}

    # Get event type and data
    event_type = event.get("type")
    event_data = event.get("data", {}).get("object", {})

    logger.info(f"Processing Stripe webhook event: {event_type} (ID: {event_id})")

    # Handle different event types
    if event_type == "checkout.session.completed":
        session_id = event_data.get("id")
        payment_intent = event_data.get("payment_intent")
        payment_status = event_data.get("payment_status")

        if session_id:
            # Update order payment status if it exists
            order = db.query(Order).filter(
                Order.stripe_session_id == session_id
            ).first()

            if order:
                # Only update if payment was successful
                if payment_status == "paid":
                    order.payment_status = "paid"
                    order.stripe_payment_id = payment_intent
                    order.updated_at = datetime.utcnow()
                    db.commit()
                    logger.info(f"Updated order {order.id} payment status to paid")
                else:
                    logger.warning(f"Checkout session {session_id} completed but payment status is {payment_status}")
            else:
                logger.warning(f"Order not found for Stripe session {session_id}")

    elif event_type == "payment_intent.payment_failed":
        # Handle failed payments
        payment_intent_id = event_data.get("id")
        logger.error(f"Payment failed for payment intent {payment_intent_id}")

        # Find and update order
        order = db.query(Order).filter(
            Order.stripe_payment_id == payment_intent_id
        ).first()

        if order:
            order.payment_status = "failed"
            order.updated_at = datetime.utcnow()
            db.commit()
            logger.info(f"Updated order {order.id} payment status to failed")

    # Mark event as processed
    processed_webhook_events.add(event_id)

    # Clean up old event IDs to prevent memory leak (keep last 1000)
    if len(processed_webhook_events) > 1000:
        # In production, use Redis with TTL instead
        processed_webhook_events.clear()
        logger.info("Cleared processed webhook events cache")

    return {"status": "success"}
