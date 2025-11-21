"""
WordPress MCP Client
Client for interacting with WordPress Model Context Protocol (MCP) servers
to retrieve real-time deprecation and function information.
"""
from typing import List, Dict, Any, Optional
import httpx
from app.core.config import settings
from .deprecation_db import DeprecatedItem, ChangeType


class WordPressMCPClient:
    """Client for WordPress MCP server"""
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize MCP client
        
        Args:
            base_url: Base URL of the MCP server
            api_key: API key for authentication
        """
        self.base_url = base_url or getattr(settings, "WORDPRESS_MCP_URL", "https://wordpress.com/mcp")
        self.api_key = api_key or getattr(settings, "WORDPRESS_MCP_API_KEY", None)
        self.enabled = getattr(settings, "WORDPRESS_MCP_ENABLED", True)
        
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "CodeRenew-MCP-Client/1.0"
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
            
    async def get_deprecations(
        self,
        version_from: str,
        version_to: str
    ) -> List[DeprecatedItem]:
        """
        Query MCP for deprecations in version range
        
        Args:
            version_from: Starting version
            version_to: Target version
            
        Returns:
            List of deprecated items
        """
        if not self.enabled:
            return []
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/deprecations",
                    params={"from": version_from, "to": version_to},
                    headers=self.headers,
                    timeout=5.0
                )
                
                if response.status_code != 200:
                    print(f"MCP Error: {response.status_code} - {response.text}")
                    return []
                
                data = response.json()
                return self._parse_deprecations(data)
                
        except Exception as e:
            print(f"Error querying MCP server: {e}")
            return []
            
    async def get_function_info(self, function_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed function information
        
        Args:
            function_name: Name of the function
            
        Returns:
            Function information dictionary or None
        """
        if not self.enabled:
            return None
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/functions/{function_name}",
                    headers=self.headers,
                    timeout=3.0
                )
                
                if response.status_code == 200:
                    return response.json()
                return None
                
        except Exception as e:
            print(f"Error querying MCP server for function {function_name}: {e}")
            return None

    def _parse_deprecations(self, data: List[Dict[str, Any]]) -> List[DeprecatedItem]:
        """
        Parse raw JSON data into DeprecatedItem objects
        
        Args:
            data: List of dictionaries from API
            
        Returns:
            List of DeprecatedItem objects
        """
        items = []
        for item in data:
            try:
                # Map string change type to Enum
                change_type_str = item.get("change_type", "deprecated_function")
                try:
                    change_type = ChangeType(change_type_str)
                except ValueError:
                    change_type = ChangeType.DEPRECATED_FUNCTION
                
                items.append(DeprecatedItem(
                    name=item.get("name", ""),
                    deprecated_in=item.get("deprecated_in", ""),
                    removed_in=item.get("removed_in"),
                    replacement=item.get("replacement"),
                    change_type=change_type,
                    severity=item.get("severity", "medium"),
                    description=item.get("description", ""),
                    documentation_url=item.get("documentation_url")
                ))
            except Exception as e:
                print(f"Error parsing MCP item: {e}")
                continue
                
        return items
