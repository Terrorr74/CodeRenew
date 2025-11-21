"""
Hybrid Deprecation Database
Combines local database with real-time MCP server data
"""
from typing import List, Optional, Dict, Any
from cachetools import TTLCache
from .deprecation_db import WordPressDeprecationDB, DeprecatedItem
from .mcp_client import WordPressMCPClient


class HybridDeprecationDB(WordPressDeprecationDB):
    """
    Hybrid database that combines local data with MCP server data.
    Falls back to local data if MCP is unavailable.
    """
    
    def __init__(self):
        super().__init__()
        self.mcp_client = WordPressMCPClient()
        # Cache for 1 hour, max 1000 items
        self.cache = TTLCache(maxsize=1000, ttl=3600)
        
    async def get_deprecated_in_range_async(
        self,
        version_from: str,
        version_to: str
    ) -> List[DeprecatedItem]:
        """
        Get deprecations from both local DB and MCP server (async)
        
        Args:
            version_from: Starting version
            version_to: Target version
            
        Returns:
            Merged list of deprecated items
        """
        cache_key = f"range:{version_from}:{version_to}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        # Get local items first (fast)
        local_items = super().get_deprecated_in_range(version_from, version_to)
        
        # Get MCP items
        try:
            mcp_items = await self.mcp_client.get_deprecations(version_from, version_to)
        except Exception as e:
            print(f"Hybrid DB: MCP lookup failed: {e}")
            mcp_items = []
        
        # Merge items (prefer MCP for newer data, but keep local if MCP fails)
        # Use a dict by name to deduplicate
        merged_map = {item.name: item for item in local_items}
        
        for item in mcp_items:
            # Overwrite or add
            merged_map[item.name] = item
            
        result = list(merged_map.values())
        
        # Update cache
        self.cache[cache_key] = result
        return result

    def get_deprecated_in_range(
        self,
        version_from: str,
        version_to: str
    ) -> List[DeprecatedItem]:
        """
        Synchronous wrapper for backward compatibility.
        Note: This ONLY returns local data to avoid async issues in sync context.
        Use get_deprecated_in_range_async for full data.
        """
        print("Warning: Using synchronous get_deprecated_in_range, only local data will be returned.")
        return super().get_deprecated_in_range(version_from, version_to)

    async def check_function_async(self, function_name: str) -> Optional[DeprecatedItem]:
        """
        Check if a function is deprecated (async)
        """
        cache_key = f"func:{function_name}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        # Check local
        item = super().check_function(function_name)
        if item:
            self.cache[cache_key] = item
            return item
            
        # Check MCP (if not found locally)
        # Note: MCP client doesn't have check_function, but we can use get_function_info
        # or just rely on range queries. For now, we'll assume range queries populate the DB
        # or we could add a specific check if the MCP API supports it.
        # The current MCP client has get_function_info but it returns a dict, not DeprecatedItem.
        
        # For now, just return local result to be safe, or extend MCP client later.
        return None
