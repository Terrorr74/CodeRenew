"""
Unit tests for WordPress MCP Client
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.wordpress.mcp_client import WordPressMCPClient
from app.services.wordpress.deprecation_db import ChangeType


@pytest.fixture
def mock_settings():
    with patch("app.services.wordpress.mcp_client.settings") as mock:
        mock.WORDPRESS_MCP_URL = "https://api.test.com"
        mock.WORDPRESS_MCP_API_KEY = "test_key"
        mock.WORDPRESS_MCP_ENABLED = True
        yield mock


@pytest.mark.asyncio
async def test_get_deprecations_success(mock_settings):
    """Test successful deprecation retrieval"""
    client = WordPressMCPClient()
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "name": "test_func",
            "deprecated_in": "5.0",
            "change_type": "deprecated_function",
            "severity": "medium",
            "description": "Test deprecation"
        }
    ]
    
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        
        items = await client.get_deprecations("4.9", "5.0")
        
        assert len(items) == 1
        assert items[0].name == "test_func"
        assert items[0].change_type == ChangeType.DEPRECATED_FUNCTION
        
        # Verify API call
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["params"] == {"from": "4.9", "to": "5.0"}
        assert kwargs["headers"]["Authorization"] == "Bearer test_key"


@pytest.mark.asyncio
async def test_get_deprecations_error(mock_settings):
    """Test error handling"""
    client = WordPressMCPClient()
    
    with patch("httpx.AsyncClient.get", side_effect=Exception("Network error")):
        items = await client.get_deprecations("4.9", "5.0")
        assert items == []


@pytest.mark.asyncio
async def test_disabled_client(mock_settings):
    """Test disabled client returns empty list"""
    mock_settings.WORDPRESS_MCP_ENABLED = False
    client = WordPressMCPClient()
    
    items = await client.get_deprecations("4.9", "5.0")
    assert items == []


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
