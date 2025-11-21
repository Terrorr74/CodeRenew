"""
WordPress Deprecation Database
Maintains a database of deprecated functions, hooks, and breaking changes across WordPress versions
"""
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ChangeType(str, Enum):
    """Type of WordPress change"""
    DEPRECATED_FUNCTION = "deprecated_function"
    REMOVED_FUNCTION = "removed_function"
    DEPRECATED_HOOK = "deprecated_hook"
    BREAKING_CHANGE = "breaking_change"
    SECURITY_ISSUE = "security_issue"


@dataclass
class DeprecatedItem:
    """Represents a deprecated WordPress item"""
    name: str
    deprecated_in: str  # Version deprecated
    removed_in: Optional[str]  # Version removed (if applicable)
    replacement: Optional[str]  # Recommended replacement
    change_type: ChangeType
    severity: str  # critical, high, medium, low
    description: str
    documentation_url: Optional[str] = None


class WordPressDeprecationDB:
    """Database of WordPress deprecations and breaking changes"""
    
    def __init__(self):
        self._load_deprecations()
    
    def _load_deprecations(self):
        """Load deprecation data"""
        # This would ideally be loaded from a JSON file or database
        # For now, we'll define some common deprecations inline
        
        self.deprecations: List[DeprecatedItem] = [
            # WordPress 6.0+ deprecations
            DeprecatedItem(
                name="get_page",
                deprecated_in="3.9",
                removed_in="6.1",
                replacement="get_post",
                change_type=ChangeType.REMOVED_FUNCTION,
                severity="critical",
                description="Function get_page() was deprecated in 3.9 and removed in 6.1",
                documentation_url="https://developer.wordpress.org/reference/functions/get_page/"
            ),
            DeprecatedItem(
                name="get_page_by_path",
                deprecated_in="6.3",
                removed_in=None,
                replacement="WP_Query with pagename parameter",
                change_type=ChangeType.DEPRECATED_FUNCTION,
                severity="high",
                description="get_page_by_path() is deprecated, use WP_Query instead",
                documentation_url="https://developer.wordpress.org/reference/functions/get_page_by_path/"
            ),
            DeprecatedItem(
                name="utf8_uri_encode",
                deprecated_in="5.3",
                removed_in=None,
                replacement="Use urlencode or rawurlencode",
                change_type=ChangeType.DEPRECATED_FUNCTION,
                severity="medium",
                description="utf8_uri_encode() is deprecated",
                documentation_url="https://developer.wordpress.org/reference/functions/utf8_uri_encode/"
            ),
            
            # WordPress 5.9+ deprecations
            DeprecatedItem(
                name="get_page_template_slug",
                deprecated_in="4.7",
                removed_in=None,
                replacement="get_page_template",
                change_type=ChangeType.DEPRECATED_FUNCTION,
                severity="medium",
                description="Use get_page_template() instead",
                documentation_url="https://developer.wordpress.org/reference/functions/get_page_template_slug/"
            ),
            
            # jQuery deprecations (common in themes)
            DeprecatedItem(
                name="$.load",
                deprecated_in="5.5",
                removed_in="5.9",
                replacement="Use $.on('load', ...)",
                change_type=ChangeType.BREAKING_CHANGE,
                severity="high",
                description="jQuery .load() method removed in WordPress 5.9 (jQuery 3.x)",
                documentation_url="https://api.jquery.com/load-event/"
            ),
            DeprecatedItem(
                name="$.bind",
                deprecated_in="5.5",
                removed_in=None,
                replacement="Use $.on()",
                change_type=ChangeType.DEPRECATED_FUNCTION,
                severity="medium",
                description="jQuery .bind() is deprecated, use .on() instead",
                documentation_url="https://api.jquery.com/bind/"
            ),
            
            # Security-related deprecations
            DeprecatedItem(
                name="mysql_",
                deprecated_in="3.9",
                removed_in="5.5",
                replacement="Use wpdb or mysqli",
                change_type=ChangeType.SECURITY_ISSUE,
                severity="critical",
                description="mysql_* functions are deprecated and removed, major security risk",
                documentation_url="https://www.php.net/manual/en/intro.mysql.php"
            ),
            
            # Common hooks
            DeprecatedItem(
                name="add_contextual_help",
                deprecated_in="3.3",
                removed_in=None,
                replacement="get_current_screen()->add_help_tab()",
                change_type=ChangeType.DEPRECATED_HOOK,
                severity="medium",
                description="Deprecated hook for adding contextual help",
                documentation_url="https://developer.wordpress.org/reference/hooks/add_contextual_help/"
            ),
        ]
        
        # Build lookup indices for faster searching
        self._build_indices()
    
    def _build_indices(self):
        """Build lookup indices for faster searching"""
        self.by_name: Dict[str, DeprecatedItem] = {
            item.name: item for item in self.deprecations
        }
        
        self.by_version: Dict[str, List[DeprecatedItem]] = {}
        for item in self.deprecations:
            if item.deprecated_in not in self.by_version:
                self.by_version[item.deprecated_in] = []
            self.by_version[item.deprecated_in].append(item)
    
    def check_function(self, function_name: str) -> Optional[DeprecatedItem]:
        """
        Check if a function is deprecated
        
        Args:
            function_name: Name of the function to check
            
        Returns:
            DeprecatedItem if deprecated, None otherwise
        """
        return self.by_name.get(function_name)
    
    def get_deprecated_in_range(
        self,
        version_from: str,
        version_to: str
    ) -> List[DeprecatedItem]:
        """
        Get all items deprecated between two WordPress versions
        
        Args:
            version_from: Starting version (e.g., "5.9")
            version_to: Target version (e.g., "6.4")
            
        Returns:
            List of deprecated items in the version range
        """
        from_parts = self._parse_version(version_from)
        to_parts = self._parse_version(version_to)
        
        relevant_items = []
        for item in self.deprecations:
            deprecated_parts = self._parse_version(item.deprecated_in)
            
            # Check if deprecated version is in range
            if from_parts <= deprecated_parts <= to_parts:
                relevant_items.append(item)
            
            # Also check if removed in this range
            if item.removed_in:
                removed_parts = self._parse_version(item.removed_in)
                if from_parts <= removed_parts <= to_parts:
                    if item not in relevant_items:
                        relevant_items.append(item)
        
        return relevant_items
    
    def get_critical_changes(
        self,
        version_from: str,
        version_to: str
    ) -> List[DeprecatedItem]:
        """
        Get critical changes (removed functions, security issues) in version range
        
        Args:
            version_from: Starting version
            version_to: Target version
            
        Returns:
            List of critical deprecated items
        """
        all_changes = self.get_deprecated_in_range(version_from, version_to)
        return [
            item for item in all_changes
            if item.severity == "critical" or item.change_type == ChangeType.REMOVED_FUNCTION
        ]
    
    def get_breaking_changes(
        self,
        version_from: str,
        version_to: str
    ) -> List[DeprecatedItem]:
        """
        Get breaking changes in version range
        
        Args:
            version_from: Starting version
            version_to: Target version
            
        Returns:
            List of breaking changes
        """
        all_changes = self.get_deprecated_in_range(version_from, version_to)
        return [
            item for item in all_changes
            if item.change_type == ChangeType.BREAKING_CHANGE
        ]
    
    def _parse_version(self, version: str) -> Tuple[int, ...]:
        """
        Parse version string into tuple for comparison
        
        Args:
            version: Version string (e.g., "6.4.1")
            
        Returns:
            Tuple of version parts (e.g., (6, 4, 1))
        """
        try:
            return tuple(int(x) for x in version.split('.'))
        except (ValueError, AttributeError):
            return (0,)
    
    def get_replacement_suggestion(self, function_name: str) -> Optional[str]:
        """
        Get replacement suggestion for a deprecated function
        
        Args:
            function_name: Name of the deprecated function
            
        Returns:
            Replacement suggestion or None
        """
        item = self.check_function(function_name)
        return item.replacement if item else None
    
    def get_documentation_url(self, function_name: str) -> Optional[str]:
        """
        Get documentation URL for a function
        
        Args:
            function_name: Name of the function
            
        Returns:
            Documentation URL or None
        """
        item = self.check_function(function_name)
        return item.documentation_url if item else None
    
    def get_all_function_names(self) -> List[str]:
        """
        Get list of all deprecated function names
        
        Returns:
            List of function names
        """
        return list(self.by_name.keys())
    
    def get_version_summary(
        self,
        version_from: str,
        version_to: str
    ) -> Dict[str, int]:
        """
        Get summary of changes between versions
        
        Args:
            version_from: Starting version
            version_to: Target version
            
        Returns:
            Dictionary with counts by change type
        """
        changes = self.get_deprecated_in_range(version_from, version_to)
        
        summary = {
            "total": len(changes),
            "critical": sum(1 for c in changes if c.severity == "critical"),
            "high": sum(1 for c in changes if c.severity == "high"),
            "medium": sum(1 for c in changes if c.severity == "medium"),
            "low": sum(1 for c in changes if c.severity == "low"),
            "removed_functions": sum(1 for c in changes if c.change_type == ChangeType.REMOVED_FUNCTION),
            "deprecated_functions": sum(1 for c in changes if c.change_type == ChangeType.DEPRECATED_FUNCTION),
            "breaking_changes": sum(1 for c in changes if c.change_type == ChangeType.BREAKING_CHANGE),
            "security_issues": sum(1 for c in changes if c.change_type == ChangeType.SECURITY_ISSUE),
        }
        
        return summary
