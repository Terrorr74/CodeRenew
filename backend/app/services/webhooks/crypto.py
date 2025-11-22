"""
Webhook URL encryption and masking utilities
"""
from cryptography.fernet import Fernet
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class WebhookCrypto:
    """
    Handles encryption/decryption of webhook URLs for secure storage
    
    Uses Fernet (symmetric encryption) from cryptography library
    """
    
    def __init__(self):
        """Initialize cipher with encryption key from settings"""
        if not settings.WEBHOOK_ENCRYPTION_KEY:
            raise ValueError("WEBHOOK_ENCRYPTION_KEY must be set in environment variables")
        
        try:
            self.cipher = Fernet(settings.WEBHOOK_ENCRYPTION_KEY.encode())
        except Exception as e:
            logger.error(f"Failed to initialize Fernet cipher: {e}")
            raise ValueError(f"Invalid WEBHOOK_ENCRYPTION_KEY: {e}")
    
    def encrypt_url(self, url: str) -> str:
        """
        Encrypt a webhook URL for storage
        
        Args:
            url: Plain text webhook URL
            
        Returns:
            Encrypted URL as base64 string
        """
        if not url:
            return ""
        
        try:
            encrypted_bytes = self.cipher.encrypt(url.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Failed to encrypt URL: {e}")
            raise ValueError(f"Encryption failed: {e}")
    
    def decrypt_url(self, encrypted_url: str) -> str:
        """
        Decrypt a webhook URL from storage
        
        Args:
            encrypted_url: Encrypted URL as base64 string
            
        Returns:
            Plain text webhook URL
        """
        if not encrypted_url:
            return ""
        
        try:
            decrypted_bytes = self.cipher.decrypt(encrypted_url.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt URL: {e}")
            raise ValueError(f"Decryption failed: {e}")
    
    @staticmethod
    def mask_url(url: str) -> str:
        """
        Mask a URL for logging (show only first 20 and last 10 chars)
        
        Args:
            url: Plain text URL
            
        Returns:
            Masked URL string
        """
        if not url:
            return ""
        
        if len(url) <= 30:
            # For short URLs, show less
            return url[:10] + "..." + url[-5:]
        
        return url[:20] + "..." + url[-10:]


# Singleton instance
_crypto_instance = None


def get_webhook_crypto() -> WebhookCrypto:
    """
    Get singleton instance of WebhookCrypto
    
    Returns:
        WebhookCrypto instance
    """
    global _crypto_instance
    if _crypto_instance is None:
        _crypto_instance = WebhookCrypto()
    return _crypto_instance
