"""
WordPress Static Code Analyzer
Performs static analysis on PHP code to detect common patterns, deprecated functions, and issues
"""
from typing import List, Dict, Any, Set
import re
from pathlib import Path
from .deprecation_db import WordPressDeprecationDB, DeprecatedItem


class WordPressAnalyzer:
    """Static analyzer for WordPress PHP code"""
    
    def __init__(self):
        self.deprecation_db = WordPressDeprecationDB()
    
    def analyze_file(self, file_path: Path, content: str) -> Dict[str, Any]:
        """
        Perform static analysis on a PHP file
        
        Args:
            file_path: Path to the file
            content: File content
            
        Returns:
            Analysis results with detected issues
        """
        results = {
            "file": str(file_path),
            "functions": self.extract_functions(content),
            "hooks": self.extract_hooks(content),
            "deprecated_usage": self.find_deprecated_functions(content),
            "security_issues": self.detect_security_issues(content),
            "patterns": self.detect_patterns(content),
        }
        
        return results
    
    def extract_functions(self, php_code: str) -> List[str]:
        """
        Extract all function calls from PHP code
        
        Args:
            php_code: PHP source code
            
        Returns:
            List of function names found
        """
        # Pattern to match function calls: function_name(
        # This is a simple regex and won't catch all cases, but good enough for common patterns
        pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        matches = re.findall(pattern, php_code)
        
        # Filter out common control structures that aren't functions
        control_structures = {'if', 'while', 'for', 'foreach', 'switch', 'elseif', 'array', 'echo', 'print', 'isset', 'empty', 'unset', 'die', 'exit', 'return'}
        functions = [m for m in matches if m not in control_structures]
        
        # Return unique functions
        return list(set(functions))
    
    def extract_hooks(self, php_code: str) -> List[Dict[str, Any]]:
        """
        Extract WordPress hooks (actions and filters)
        
        Args:
            php_code: PHP source code
            
        Returns:
            List of hooks with details
        """
        hooks = []
        
        # Pattern for add_action and add_filter
        action_pattern = r'add_action\s*\(\s*[\'"]([^\'"]+)[\'"]'
        filter_pattern = r'add_filter\s*\(\s*[\'"]([^\'"]+)[\'"]'
        
        # Find all actions
        for match in re.finditer(action_pattern, php_code):
            hooks.append({
                "type": "action",
                "name": match.group(1),
                "line": php_code[:match.start()].count('\n') + 1
            })
        
        # Find all filters
        for match in re.finditer(filter_pattern, php_code):
            hooks.append({
                "type": "filter",
                "name": match.group(1),
                "line": php_code[:match.start()].count('\n') + 1
            })
        
        return hooks
    
    def find_deprecated_functions(self, php_code: str) -> List[Dict[str, Any]]:
        """
        Find usage of deprecated WordPress functions
        
        Args:
            php_code: PHP source code
            
        Returns:
            List of deprecated function usages
        """
        deprecated_usages = []
        
        # Get all function calls
        functions = self.extract_functions(php_code)
        
        # Check each against deprecation database
        for func_name in functions:
            deprecated_item = self.deprecation_db.check_function(func_name)
            if deprecated_item:
                # Find all occurrences in the code
                pattern = rf'\b{re.escape(func_name)}\s*\('
                for match in re.finditer(pattern, php_code):
                    line_num = php_code[:match.start()].count('\n') + 1
                    
                    deprecated_usages.append({
                        "function": func_name,
                        "line": line_num,
                        "deprecated_in": deprecated_item.deprecated_in,
                        "removed_in": deprecated_item.removed_in,
                        "replacement": deprecated_item.replacement,
                        "severity": deprecated_item.severity,
                        "description": deprecated_item.description,
                    })
        
        return deprecated_usages
    
    def detect_security_issues(self, php_code: str) -> List[Dict[str, Any]]:
        """
        Detect common security issues in PHP code
        
        Args:
            php_code: PHP source code
            
        Returns:
            List of potential security issues
        """
        issues = []
        
        # Check for direct SQL queries (potential SQL injection)
        sql_patterns = [
            (r'\$wpdb->query\s*\(\s*["\'].*?\$', "Direct SQL query with variable interpolation - potential SQL injection"),
            (r'mysql_query\s*\(', "Deprecated mysql_query usage - security risk"),
            (r'mysqli_query\s*\(.*?\$', "Direct mysqli query with variables - use prepared statements"),
        ]
        
        for pattern, description in sql_patterns:
            for match in re.finditer(pattern, php_code, re.IGNORECASE):
                line_num = php_code[:match.start()].count('\n') + 1
                issues.append({
                    "type": "sql_injection",
                    "line": line_num,
                    "severity": "critical",
                    "description": description,
                    "code_snippet": self._get_line_context(php_code, line_num),
                })
        
        # Check for XSS vulnerabilities (unescaped output)
        xss_patterns = [
            (r'echo\s+\$_(GET|POST|REQUEST)\[', "Direct output of user input - potential XSS"),
            (r'print\s+\$_(GET|POST|REQUEST)\[', "Direct output of user input - potential XSS"),
        ]
        
        for pattern, description in xss_patterns:
            for match in re.finditer(pattern, php_code, re.IGNORECASE):
                line_num = php_code[:match.start()].count('\n') + 1
                issues.append({
                    "type": "xss",
                    "line": line_num,
                    "severity": "high",
                    "description": description,
                    "code_snippet": self._get_line_context(php_code, line_num),
                })
        
        # Check for file inclusion vulnerabilities
        file_patterns = [
            (r'include\s*\(\s*\$_(GET|POST|REQUEST)', "Dynamic file inclusion - potential RFI/LFI"),
            (r'require\s*\(\s*\$_(GET|POST|REQUEST)', "Dynamic file inclusion - potential RFI/LFI"),
        ]
        
        for pattern, description in file_patterns:
            for match in re.finditer(pattern, php_code, re.IGNORECASE):
                line_num = php_code[:match.start()].count('\n') + 1
                issues.append({
                    "type": "file_inclusion",
                    "line": line_num,
                    "severity": "critical",
                    "description": description,
                    "code_snippet": self._get_line_context(php_code, line_num),
                })
        
        return issues
    
    def detect_patterns(self, php_code: str) -> List[Dict[str, Any]]:
        """
        Detect common WordPress coding patterns and anti-patterns
        
        Args:
            php_code: PHP source code
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # Check for direct database access (should use $wpdb)
        if re.search(r'new\s+mysqli\s*\(', php_code, re.IGNORECASE):
            patterns.append({
                "type": "anti_pattern",
                "severity": "medium",
                "description": "Direct mysqli usage detected - use $wpdb instead",
                "recommendation": "Use WordPress $wpdb object for database queries"
            })
        
        # Check for proper nonce verification
        if re.search(r'add_action\s*\(\s*[\'"]admin_post_', php_code):
            if not re.search(r'wp_verify_nonce', php_code):
                patterns.append({
                    "type": "security",
                    "severity": "high",
                    "description": "Admin POST handler without nonce verification",
                    "recommendation": "Add wp_verify_nonce() to verify form submissions"
                })
        
        # Check for proper data sanitization
        if re.search(r'\$_(GET|POST|REQUEST)\[', php_code):
            has_sanitization = any([
                re.search(r'sanitize_text_field', php_code),
                re.search(r'sanitize_email', php_code),
                re.search(r'absint', php_code),
                re.search(r'intval', php_code),
            ])
            
            if not has_sanitization:
                patterns.append({
                    "type": "security",
                    "severity": "high",
                    "description": "User input without sanitization detected",
                    "recommendation": "Use sanitize_text_field(), sanitize_email(), or other sanitization functions"
                })
        
        # Check for proper escaping on output
        if re.search(r'echo\s+\$', php_code) or re.search(r'print\s+\$', php_code):
            has_escaping = any([
                re.search(r'esc_html', php_code),
                re.search(r'esc_attr', php_code),
                re.search(r'esc_url', php_code),
            ])
            
            if not has_escaping:
                patterns.append({
                    "type": "security",
                    "severity": "medium",
                    "description": "Output without escaping detected",
                    "recommendation": "Use esc_html(), esc_attr(), or esc_url() when outputting variables"
                })
        
        # Check for jQuery deprecated methods
        jquery_deprecated = [
            ('$.load', '$.on("load", ...)'),
            ('$.bind', '$.on'),
            ('$.unbind', '$.off'),
            ('$.delegate', '$.on'),
            ('$.undelegate', '$.off'),
        ]
        
        for old_method, new_method in jquery_deprecated:
            if old_method in php_code:
                patterns.append({
                    "type": "deprecated",
                    "severity": "medium",
                    "description": f"Deprecated jQuery method {old_method} detected",
                    "recommendation": f"Replace with {new_method}"
                })
        
        return patterns
    
    def quick_scan(
        self,
        php_code: str,
        version_from: str,
        version_to: str
    ) -> Dict[str, Any]:
        """
        Perform a quick static scan before sending to Claude
        
        Args:
            php_code: PHP source code
            version_from: Starting WordPress version
            version_to: Target WordPress version
            
        Returns:
            Quick scan results
        """
        # Get deprecated items in version range
        deprecated_items = self.deprecation_db.get_deprecated_in_range(
            version_from,
            version_to
        )
        
        # Find deprecated function usage
        deprecated_usage = self.find_deprecated_functions(php_code)
        
        # Detect security issues
        security_issues = self.detect_security_issues(php_code)
        
        # Calculate quick risk assessment
        critical_count = sum(1 for d in deprecated_usage if d['severity'] == 'critical')
        critical_count += sum(1 for s in security_issues if s['severity'] == 'critical')
        
        risk_level = "safe"
        if critical_count > 0:
            risk_level = "critical"
        elif len(deprecated_usage) > 0 or len(security_issues) > 0:
            risk_level = "warning"
        
        return {
            "risk_level": risk_level,
            "deprecated_functions_found": len(deprecated_usage),
            "security_issues_found": len(security_issues),
            "critical_issues": critical_count,
            "deprecated_usage": deprecated_usage,
            "security_issues": security_issues,
            "version_summary": self.deprecation_db.get_version_summary(version_from, version_to),
        }
    
    def _get_line_context(self, code: str, line_num: int, context_lines: int = 2) -> str:
        """
        Get code snippet with context around a line
        
        Args:
            code: Full code
            line_num: Line number (1-indexed)
            context_lines: Number of lines before/after to include
            
        Returns:
            Code snippet with context
        """
        lines = code.split('\n')
        start = max(0, line_num - context_lines - 1)
        end = min(len(lines), line_num + context_lines)
        
        snippet_lines = lines[start:end]
        return '\n'.join(snippet_lines)
    
    def get_file_priority(self, file_path: Path) -> int:
        """
        Determine priority of a file for analysis
        Higher priority files are analyzed first
        
        Args:
            file_path: Path to the file
            
        Returns:
            Priority score (higher = more important)
        """
        filename = file_path.name.lower()
        
        # High priority files (core theme/plugin files)
        high_priority = ['functions.php', 'index.php', 'plugin.php', 'class-', 'init.php']
        if any(p in filename for p in high_priority):
            return 100
        
        # Medium priority (template files)
        medium_priority = ['template', 'header.php', 'footer.php', 'sidebar.php']
        if any(p in filename for p in medium_priority):
            return 50
        
        # Low priority (assets, includes)
        low_priority = ['inc/', 'includes/', 'assets/', 'vendor/']
        if any(p in str(file_path) for p in low_priority):
            return 10
        
        # Default priority
        return 25
