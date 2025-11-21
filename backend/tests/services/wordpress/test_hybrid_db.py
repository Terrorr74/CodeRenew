"""
Unit tests for Hybrid Deprecation DB
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.wordpress.hybrid_deprecation_db import HybridDeprecationDB
from app.services.wordpress.deprecation_db import DeprecatedItem, ChangeType


@pytest.mark.asyncio
async def test_hybrid_get_deprecations():
    """Test merging local and MCP data"""
    with patch("app.services.wordpress.hybrid_deprecation_db.WordPressMCPClient") as MockClient:
        # Setup mock client
        mock_client = MockClient.return_value
        mock_client.get_deprecations = AsyncMock()
        
        # Mock MCP data
        mcp_item = DeprecatedItem(
            name="mcp_func",
            deprecated_in="6.0",
            removed_in=None,
            replacement="new_func",
            change_type=ChangeType.DEPRECATED_FUNCTION,
            severity="medium",
            description="MCP deprecation"
        )
        mock_client.get_deprecations.return_value = [mcp_item]
        
        # Initialize DB
        db = HybridDeprecationDB()
        
        # Mock local data (via super)
        with patch("app.services.wordpress.deprecation_db.WordPressDeprecationDB.get_deprecated_in_range") as mock_local:
            local_item = DeprecatedItem(
                name="local_func",
                deprecated_in="5.0",
                removed_in=None,
                replacement="old_func",
                change_type=ChangeType.DEPRECATED_FUNCTION,
                severity="low",
                description="Local deprecation"
            )
            mock_local.return_value = [local_item]
            
            # Test async retrieval
            items = await db.get_deprecated_in_range_async("5.0", "6.0")
            
            assert len(items) == 2
            names = {item.name for item in items}
            assert "mcp_func" in names
            assert "local_func" in names
            
            # Verify cache
            assert "range:5.0:6.0" in db.cache
            
            # Verify second call hits cache (mock shouldn't be called again)
            mock_client.get_deprecations.reset_mock()
            items2 = await db.get_deprecated_in_range_async("5.0", "6.0")
            assert len(items2) == 2
            mock_client.get_deprecations.assert_not_called()


@pytest.mark.asyncio
async def test_hybrid_fallback_on_error():
    """Test fallback to local data when MCP fails"""
    with patch("app.services.wordpress.hybrid_deprecation_db.WordPressMCPClient") as MockClient:
        mock_client = MockClient.return_value
        mock_client.get_deprecations = AsyncMock(side_effect=Exception("MCP Down"))
        
        db = HybridDeprecationDB()
        
        # Mock local data
        with patch("app.services.wordpress.deprecation_db.WordPressDeprecationDB.get_deprecated_in_range") as mock_local:
            local_item = DeprecatedItem(
                name="local_func",
                deprecated_in="5.0",
                removed_in=None,
                replacement="old_func",
                change_type=ChangeType.DEPRECATED_FUNCTION,
                severity="low",
                description="Local deprecation"
            )
            mock_local.return_value = [local_item]
            
            items = await db.get_deprecated_in_range_async("5.0", "6.0")
            
            assert len(items) == 1
            assert items[0].name == "local_func"
