"""
Webhook configuration API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import logging

from app.db.session import get_db
from app.models.user import User
from app.models.webhook_config import WebhookConfig
from app.api.dependencies import get_current_user
from app.schemas.webhook import (
    WebhookConfigCreate,
    WebhookConfigUpdate,
    WebhookConfigResponse,
    WebhookDeliveryListResponse,
    WebhookTestRequest,
    WebhookTestResponse
)
from app.services.webhooks.crypto import get_webhook_crypto
from app.services.webhooks.webhook_service import WebhookService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=WebhookConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook_config(
    webhook_data: WebhookConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new webhook configuration
    
    Encrypts the webhook URL before storing in database
    """
    crypto = get_webhook_crypto()
    
    # Encrypt URL if provided
    encrypted_url = None
    if webhook_data.url:
        try:
            encrypted_url = crypto.encrypt_url(webhook_data.url)
        except Exception as e:
            logger.error(f"Failed to encrypt webhook URL: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to encrypt URL: {str(e)}"
            )
    
    # Create webhook config
    webhook_config = WebhookConfig(
        id=str(uuid.uuid4()),
        user_id=str(current_user.id),
        name=webhook_data.name,
        type=webhook_data.type,
        url=encrypted_url,
        enabled=webhook_data.enabled,
        events=webhook_data.events
    )
    
    db.add(webhook_config)
    db.commit()
    db.refresh(webhook_config)
    
    # Return response with masked URL
    response = WebhookConfigResponse.from_orm(webhook_config)
    response.url_masked = crypto.mask_url(webhook_data.url) if webhook_data.url else None
    
    logger.info(f"Created webhook config {webhook_config.id} for user {current_user.id}")
    
    return response


@router.get("/", response_model=List[WebhookConfigResponse])
async def list_webhook_configs(
    type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all webhook configurations for the current user
    
    Optional filter by webhook type
    """
    query = db.query(WebhookConfig).filter(
        WebhookConfig.user_id == str(current_user.id)
    )
    
    if type:
        query = query.filter(WebhookConfig.type == type)
    
    webhooks = query.order_by(WebhookConfig.created_at.desc()).all()
    
    # Mask URLs in response
    crypto = get_webhook_crypto()
    responses = []
    for webhook in webhooks:
        response = WebhookConfigResponse.from_orm(webhook)
        if webhook.url:
            try:
                decrypted_url = crypto.decrypt_url(webhook.url)
                response.url_masked = crypto.mask_url(decrypted_url)
            except Exception:
                response.url_masked = "***encrypted***"
        responses.append(response)
    
    return responses


@router.get("/{webhook_id}", response_model=WebhookConfigResponse)
async def get_webhook_config(
    webhook_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific webhook configuration
    """
    webhook = db.query(WebhookConfig).filter(
        WebhookConfig.id == webhook_id,
        WebhookConfig.user_id == str(current_user.id)
    ).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook configuration not found"
        )
    
    # Mask URL in response
    crypto = get_webhook_crypto()
    response = WebhookConfigResponse.from_orm(webhook)
    if webhook.url:
        try:
            decrypted_url = crypto.decrypt_url(webhook.url)
            response.url_masked = crypto.mask_url(decrypted_url)
        except Exception:
            response.url_masked = "***encrypted***"
    
    return response


@router.put("/{webhook_id}", response_model=WebhookConfigResponse)
async def update_webhook_config(
    webhook_id: str,
    webhook_data: WebhookConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a webhook configuration
    """
    webhook = db.query(WebhookConfig).filter(
        WebhookConfig.id == webhook_id,
        WebhookConfig.user_id == str(current_user.id)
    ).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook configuration not found"
        )
    
    crypto = get_webhook_crypto()
    
    # Update fields
    if webhook_data.name is not None:
        webhook.name = webhook_data.name
    
    if webhook_data.url is not None:
        try:
            webhook.url = crypto.encrypt_url(webhook_data.url)
        except Exception as e:
            logger.error(f"Failed to encrypt webhook URL: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to encrypt URL: {str(e)}"
            )
    
    if webhook_data.enabled is not None:
        webhook.enabled = webhook_data.enabled
    
    if webhook_data.events is not None:
        webhook.events = webhook_data.events
    
    db.commit()
    db.refresh(webhook)
    
    # Return response with masked URL
    response = WebhookConfigResponse.from_orm(webhook)
    if webhook.url:
        try:
            decrypted_url = crypto.decrypt_url(webhook.url)
            response.url_masked = crypto.mask_url(decrypted_url)
        except Exception:
            response.url_masked = "***encrypted***"
    
    logger.info(f"Updated webhook config {webhook_id}")
    
    return response


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook_config(
    webhook_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a webhook configuration
    """
    webhook = db.query(WebhookConfig).filter(
        WebhookConfig.id == webhook_id,
        WebhookConfig.user_id == str(current_user.id)
    ).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook configuration not found"
        )
    
    db.delete(webhook)
    db.commit()
    
    logger.info(f"Deleted webhook config {webhook_id}")
    
    return None


@router.post("/{webhook_id}/test", response_model=WebhookTestResponse)
async def test_webhook(
    webhook_id: str,
    test_request: WebhookTestRequest = WebhookTestRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Test a webhook configuration by sending a test message
    """
    webhook = db.query(WebhookConfig).filter(
        WebhookConfig.id == webhook_id,
        WebhookConfig.user_id == str(current_user.id)
    ).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook configuration not found"
        )
    
    # Test webhook delivery
    webhook_service = WebhookService(db)
    result = await webhook_service.test_webhook(
        webhook_config=webhook,
        test_message=test_request.test_message
    )
    
    return WebhookTestResponse(**result)


@router.get("/{webhook_id}/deliveries", response_model=WebhookDeliveryListResponse)
async def get_webhook_deliveries(
    webhook_id: str,
    page: int = 1,
    per_page: int = 20,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get delivery history for a webhook configuration
    """
    # Verify webhook belongs to user
    webhook = db.query(WebhookConfig).filter(
        WebhookConfig.id == webhook_id,
        WebhookConfig.user_id == str(current_user.id)
    ).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook configuration not found"
        )
    
    # Get delivery history
    webhook_service = WebhookService(db)
    result = webhook_service.get_delivery_history(
        webhook_config_id=webhook_id,
        page=page,
        per_page=per_page,
        status=status
    )
    
    return WebhookDeliveryListResponse(**result)
