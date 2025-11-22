"""
Main webhook service for triggering and managing webhook deliveries
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import logging

from app.models.webhook_config import WebhookConfig
from app.models.webhook_delivery import WebhookDelivery
from app.services.webhooks.crypto import get_webhook_crypto
from app.services.webhooks.templates import slack_template, teams_template

logger = logging.getLogger(__name__)


class WebhookService:
    """
    Service for managing webhook configurations and triggering deliveries
    """
    
    def __init__(self, db: Session):
        """
        Initialize webhook service
        
        Args:
            db: Database session
        """
        self.db = db
        self.crypto = get_webhook_crypto()
    
    async def trigger_webhooks(
        self,
        user_id: str,
        event_type: str,
        payload: Dict[str, Any]
    ) -> List[WebhookDelivery]:
        """
        Trigger all enabled webhooks for a user and event type
        
        Args:
            user_id: User ID
            event_type: Event type (scan_completed, vulnerability_found)
            payload: Event payload data
        
        Returns:
            List of created WebhookDelivery records
        """
        # Find all enabled webhooks for this user and event type
        webhooks = self.db.query(WebhookConfig).filter(
            WebhookConfig.user_id == user_id,
            WebhookConfig.enabled == True
        ).all()
        
        # Filter webhooks that subscribe to this event
        matching_webhooks = [
            wh for wh in webhooks
            if event_type in wh.events
        ]
        
        if not matching_webhooks:
            logger.info(f"No webhooks configured for user {user_id} and event {event_type}")
            return []
        
        deliveries = []
        
        # Create delivery records and enqueue tasks
        for webhook in matching_webhooks:
            delivery = self._create_delivery(webhook, event_type, payload)
            deliveries.append(delivery)
            
            # Enqueue Celery task for async delivery
            from app.tasks.webhook_tasks import deliver_webhook
            deliver_webhook.delay(
                delivery_id=delivery.id,
                webhook_config_id=webhook.id,
                event_type=event_type,
                payload=payload
            )
        
        logger.info(f"Triggered {len(deliveries)} webhooks for event {event_type}")
        return deliveries
    
    def _create_delivery(
        self,
        webhook: WebhookConfig,
        event_type: str,
        payload: Dict[str, Any]
    ) -> WebhookDelivery:
        """
        Create a webhook delivery record
        
        Args:
            webhook: WebhookConfig instance
            event_type: Event type
            payload: Event payload
        
        Returns:
            WebhookDelivery instance
        """
        delivery = WebhookDelivery(
            id=str(uuid.uuid4()),
            webhook_config_id=webhook.id,
            event_type=event_type,
            payload=payload,
            status='pending',
            attempts=0
        )
        
        self.db.add(delivery)
        self.db.commit()
        self.db.refresh(delivery)
        
        return delivery
    
    async def test_webhook(
        self,
        webhook_config: WebhookConfig,
        test_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Test a webhook configuration by sending a test message
        
        Args:
            webhook_config: WebhookConfig to test
            test_message: Optional custom test message
        
        Returns:
            Dictionary with test results
        """
        import httpx
        
        # Prepare test payload
        test_data = {
            'message': test_message or 'This is a test webhook from CodeRenew',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Format message based on webhook type
        if webhook_config.type == 'slack':
            formatted_message = slack_template.format_test_message(test_data)
        elif webhook_config.type == 'teams':
            formatted_message = teams_template.format_test_message(test_data)
        elif webhook_config.type == 'email':
            # Email will be handled separately
            return {
                'success': True,
                'message': 'Email test not yet implemented',
                'delivery_id': None
            }
        else:  # http
            formatted_message = test_data
        
        # Decrypt URL
        try:
            url = self.crypto.decrypt_url(webhook_config.url)
        except Exception as e:
            logger.error(f"Failed to decrypt webhook URL: {e}")
            return {
                'success': False,
                'message': f'Failed to decrypt URL: {str(e)}',
                'error': str(e)
            }
        
        # Send test request
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    json=formatted_message,
                    headers={'Content-Type': 'application/json'}
                )
                response.raise_for_status()
            
            logger.info(f"Test webhook successful for {webhook_config.id}")
            return {
                'success': True,
                'message': 'Test webhook delivered successfully',
                'response_code': response.status_code
            }
        
        except httpx.HTTPError as e:
            logger.error(f"Test webhook failed for {webhook_config.id}: {e}")
            return {
                'success': False,
                'message': f'Test webhook failed: {str(e)}',
                'error': str(e)
            }
    
    def get_delivery_history(
        self,
        webhook_config_id: str,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get delivery history for a webhook configuration
        
        Args:
            webhook_config_id: Webhook config ID
            page: Page number (1-indexed)
            per_page: Results per page
            status: Optional status filter
        
        Returns:
            Dictionary with deliveries and pagination info
        """
        query = self.db.query(WebhookDelivery).filter(
            WebhookDelivery.webhook_config_id == webhook_config_id
        )
        
        if status:
            query = query.filter(WebhookDelivery.status == status)
        
        total = query.count()
        
        deliveries = query.order_by(
            WebhookDelivery.created_at.desc()
        ).offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'deliveries': deliveries,
            'total': total,
            'page': page,
            'per_page': per_page
        }
