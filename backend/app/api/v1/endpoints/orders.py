from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import stripe
import os
from datetime import datetime

from app.db.session import get_db
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderResponse, OrderListResponse

router = APIRouter()

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


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
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events.
    This endpoint should be called by Stripe when payment events occur.
    """
    # Note: In production, you should verify the webhook signature
    # For now, this is a simplified implementation

    event_type = request.get("type")

    if event_type == "checkout.session.completed":
        session = request.get("data", {}).get("object", {})
        session_id = session.get("id")

        if session_id:
            # Update order payment status if it exists
            order = db.query(Order).filter(
                Order.stripe_session_id == session_id
            ).first()

            if order:
                order.payment_status = "paid"
                order.stripe_payment_id = session.get("payment_intent")
                order.updated_at = datetime.utcnow()
                db.commit()

    return {"status": "success"}
