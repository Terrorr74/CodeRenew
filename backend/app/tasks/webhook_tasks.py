"""
Celery tasks for webhook delivery with retry logic
"""
from celery import Task
from celery.exceptions import MaxRetriesExceededError
from requests.exceptions import RequestException, Timeout
from datetime import datetime
from typing import Dict, Any
import httpx
import logging
import json

from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.webhook_config import WebhookConfig
from app.models.webhook_delivery import WebhookDelivery
from app.services.webhooks.crypto import get_webhook_crypto
from app.services.webhooks.templates import slack_template, teams_template

logger = logging.getLogger(__name__)


class WebhookDeliveryTask(Task):
    """Base task for webhook delivery with error handling"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        delivery_id = kwargs.get('delivery_id')
        if delivery_id:
            db = SessionLocal()
            try:
                delivery = db.query(WebhookDelivery).filter(
                    WebhookDelivery.id == delivery_id
                ).first()
                
                if delivery:
                    delivery.status = 'failed'
                    delivery.error_message = str(exc)
                    delivery.last_attempt_at = datetime.utcnow()
                    db.commit()
                    logger.error(f"Webhook delivery {delivery_id} failed permanently: {exc}")
            finally:
                db.close()


@celery_app.task(
    bind=True,
    base=WebhookDeliveryTask,
    max_retries=3,
    autoretry_for=(RequestException, Timeout, httpx.HTTPError),
    retry_backoff=True,  # Exponential backoff: 2s, 4s, 8s
    retry_backoff_max=600,  # Max 10 minutes
    retry_jitter=True  # Add random jitter to prevent thundering herd
)
def deliver_webhook(
    self,
    delivery_id: str,
    webhook_config_id: str,
    event_type: str,
    payload: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Deliver webhook to external endpoint with retry logic
    
    Args:
        delivery_id: UUID of webhook_deliveries record
        webhook_config_id: UUID of webhook_configs record
        event_type: Event type (scan_completed, vulnerability_found)
        payload: Event payload data
    
    Returns:
        Dictionary with delivery status
    """
    db = SessionLocal()
    
    try:
        # Get webhook config and delivery record
        webhook_config = db.query(WebhookConfig).filter(
            WebhookConfig.id == webhook_config_id
        ).first()
        
        if not webhook_config:
            raise ValueError(f"Webhook config {webhook_config_id} not found")
        
        delivery = db.query(WebhookDelivery).filter(
            WebhookDelivery.id == delivery_id
        ).first()
        
        if not delivery:
            raise ValueError(f"Webhook delivery {delivery_id} not found")
        
        # Check idempotency using Redis
        from app.core.celery_app import celery_app as app
        redis_client = app.backend.client if hasattr(app.backend, 'client') else None
        
        if redis_client:
            idempotency_key = f"webhook_delivery:{delivery_id}"
            if redis_client.exists(idempotency_key):
                logger.info(f"Webhook delivery {delivery_id} already processed (idempotency)")
                return {"status": "skipped", "reason": "already_processed"}
        
        # Decrypt webhook URL
        crypto = get_webhook_crypto()
        try:
            url = crypto.decrypt_url(webhook_config.url)
        except Exception as e:
            logger.error(f"Failed to decrypt webhook URL: {e}")
            delivery.status = 'failed'
            delivery.error_message = f"URL decryption failed: {str(e)}"
            db.commit()
            return {"status": "failed", "error": "decryption_failed"}
        
        # Format message based on webhook type
        formatted_message = _format_message(webhook_config.type, event_type, payload)
        
        # Update delivery attempt count
        delivery.attempts += 1
        delivery.last_attempt_at = datetime.utcnow()
        db.commit()
        
        # Send HTTP request with timeout
        logger.info(f"Delivering webhook {delivery_id} to {crypto.mask_url(url)}")
        
        response = httpx.post(
            url,
            json=formatted_message,
            timeout=10.0,  # 10 second timeout
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        
        # Update delivery record: success
        delivery.status = 'delivered'
        delivery.response_code = response.status_code
        delivery.response_body = response.text[:1000]  # Truncate to 1000 chars
        db.commit()
        
        # Set idempotency key in Redis with 24h TTL
        if redis_client:
            redis_client.setex(idempotency_key, 86400, "1")
        
        logger.info(f"Webhook delivery {delivery_id} successful")
        
        return {
            "status": "delivered",
            "delivery_id": delivery_id,
            "response_code": response.status_code
        }
    
    except (RequestException, Timeout, httpx.HTTPError) as exc:
        # Update delivery record: retry
        delivery.error_message = str(exc)
        db.commit()
        
        logger.warning(f"Webhook delivery {delivery_id} failed (attempt {delivery.attempts}): {exc}")
        
        # Retry with exponential backoff
        try:
            raise self.retry(exc=exc)
        except MaxRetriesExceededError:
            # Max retries exceeded, mark as failed
            delivery.status = 'failed'
            db.commit()
            logger.error(f"Webhook delivery {delivery_id} failed after {delivery.attempts} attempts")
            raise
    
    except Exception as exc:
        # Non-retryable error
        delivery.status = 'failed'
        delivery.error_message = str(exc)
        db.commit()
        
        logger.error(f"Webhook delivery {delivery_id} failed with non-retryable error: {exc}")
        raise
    
    finally:
        db.close()


def _format_message(webhook_type: str, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format message based on webhook type and event type
    
    Args:
        webhook_type: Webhook type (slack, teams, email, http)
        event_type: Event type (scan_completed, vulnerability_found)
        payload: Event payload
    
    Returns:
        Formatted message dictionary
    """
    if webhook_type == 'slack':
        if event_type == 'scan_completed':
            return slack_template.format_scan_completed(payload)
        elif event_type == 'vulnerability_found':
            return slack_template.format_vulnerability_found(payload)
    
    elif webhook_type == 'teams':
        if event_type == 'scan_completed':
            return teams_template.format_scan_completed(payload)
        elif event_type == 'vulnerability_found':
            return teams_template.format_vulnerability_found(payload)
    
    # Default: return raw payload for HTTP webhooks
    return payload
