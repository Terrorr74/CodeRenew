"""
Token Optimizer for WordPress Code Analysis
Reduces token usage while preserving analysis accuracy through intelligent code processing
"""
from typing import List, Dict, Any, Set, Optional
from pathlib import Path
import re
import tiktoken


class TokenOptimizer:
    """Optimizes PHP code to reduce token usage while maintaining analysis quality"""
    
    # File patterns to skip (vendor/library code)
    SKIP_PATTERNS = [
        r'vendor/',
        r'node_modules/',
        r'bower_components/',
        r'\.min\.(js|css)$',
        r'\.bundle\.(js|css)$',
        r'/dist/',
        r'/build/',
        r'/libs?/',
        r'/packages/',
    ]
    
    # Patterns indicating third-party code (check file headers)
    THIRD_PARTY_INDICATORS = [
        r'@package\s+(jQuery|Bootstrap|Modernizr|Underscore)',
        r'Copyright.*\(c\).*(?:jQuery|Bootstrap|Facebook|Google)',
        r'MIT License.*(?:jQuery|Bootstrap)',
        r'@link\s+https?://(?:jquery|getbootstrap|npmjs)',
    ]
    
    # WordPress core file patterns (skip these)
    WP_CORE_PATTERNS = [
        r'wp-includes/',
        r'wp-admin/',
        r'wp-content/plugins/akismet/',
        r'wp-content/plugins/hello\.php',
    ]
    
    def __init__(self):
        """Initialize token optimizer with tiktoken encoder"""
        try:
            # Use cl100k_base encoding (same as GPT-4/Claude)
            self.encoder = tiktoken.get_encoding("cl100k_base")
        except Exception:
            # Fallback to simple estimation if tiktoken fails
            self.encoder = None
    
    def count_tokens(self, text: str) -> int:
        """
        Accurately count tokens in text
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        if self.encoder:
            return len(self.encoder.encode(text))
        else:
            # Fallback: rough estimate (1 token per 4 characters)
            return len(text) // 4
    
    def should_skip_file(self, file_path: Path) -> bool:
        """
        Determine if file should be skipped based on patterns
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file should be skipped
        """
        path_str = str(file_path)
        
        # Check skip patterns
        for pattern in self.SKIP_PATTERNS:
            if re.search(pattern, path_str, re.IGNORECASE):
                return True
        
        # Check WordPress core patterns
        for pattern in self.WP_CORE_PATTERNS:
            if re.search(pattern, path_str, re.IGNORECASE):
                return True
        
        return False
    
    def is_third_party_code(self, content: str) -> bool:
        """
        Check if code is third-party library based on file header
        
        Args:
            content: File content to check
            
        Returns:
            True if appears to be third-party code
        """
        # Check first 50 lines for indicators
        lines = content.split('\n')[:50]
        header = '\n'.join(lines)
        
        for pattern in self.THIRD_PARTY_INDICATORS:
            if re.search(pattern, header, re.IGNORECASE):
                return True
        
        return False
    
    def extract_file_patterns(self, content: str) -> Dict[str, Any]:
        """
        Extract reusable patterns from file for better context management
        
        Args:
            content: PHP file content
            
        Returns:
            Dictionary with extracted patterns
        """
        patterns = {
            'has_wordpress_hooks': False,
            'has_database_queries': False,
            'has_user_input': False,
            'has_deprecated_tags': False,
            'function_count': 0,
            'class_count': 0,
            'complexity': 'low',
        }
        
        # Check for WordPress hooks
        if re.search(r'add_(action|filter)\s*\(', content):
            patterns['has_wordpress_hooks'] = True
        
        # Check for database queries
        if re.search(r'\$wpdb->|mysql_|mysqli_', content):
            patterns['has_database_queries'] = True
        
        # Check for user input handling
        if re.search(r'\$_(GET|POST|REQUEST|COOKIE|SERVER)\[', content):
            patterns['has_user_input'] = True
        
        # Check for @deprecated tags
        if re.search(r'@deprecated', content, re.IGNORECASE):
            patterns['has_deprecated_tags'] = True
        
        # Count functions and classes
        patterns['function_count'] = len(re.findall(r'\bfunction\s+\w+\s*\(', content))
        patterns['class_count'] = len(re.findall(r'\bclass\s+\w+', content))
        
        # Determine complexity
        total_items = patterns['function_count'] + patterns['class_count']
        if total_items > 20:
            patterns['complexity'] = 'high'
        elif total_items > 10:
            patterns['complexity'] = 'medium'
        
        return patterns
    
    def optimize_code(
        self,
        php_code: str,
        preserve_structure: bool = False
    ) -> Dict[str, Any]:
        """
        Optimize PHP code to reduce tokens while preserving analysis value
        
        Args:
            php_code: Original PHP code
            preserve_structure: If True, keep more structure for context
            
        Returns:
            Dictionary with optimized code and statistics
        """
        original_tokens = self.count_tokens(php_code)
        
        # Extract patterns first (for context reusability)
        patterns = self.extract_file_patterns(php_code)
        
        # Step 1: Remove comments (except @deprecated)
        optimized = self._remove_comments(php_code, keep_deprecated=True)
        
        # Step 2: Collapse whitespace
        optimized = self._collapse_whitespace(optimized)
        
        # Step 3: Extract critical sections if file is large
        if not preserve_structure and len(optimized) > 10000:
            optimized = self._extract_critical_sections(optimized, patterns)
        
        optimized_tokens = self.count_tokens(optimized)
        tokens_saved = original_tokens - optimized_tokens
        reduction_percent = (tokens_saved / original_tokens * 100) if original_tokens > 0 else 0
        
        return {
            'optimized_code': optimized,
            'original_tokens': original_tokens,
            'optimized_tokens': optimized_tokens,
            'tokens_saved': tokens_saved,
            'reduction_percent': reduction_percent,
            'patterns': patterns,
        }
    
    def _remove_comments(self, code: str, keep_deprecated: bool = True) -> str:
        """
        Remove PHP comments while optionally preserving @deprecated tags
        
        Args:
            code: PHP code
            keep_deprecated: If True, keep @deprecated comments
            
        Returns:
            Code with comments removed
        """
        # Remove single-line comments (// and #)
        # But keep lines with @deprecated
        lines = []
        for line in code.split('\n'):
            if keep_deprecated and '@deprecated' in line.lower():
                lines.append(line)
            elif '//' in line:
                # Check if it's inside a string? (Simple heuristic for now)
                parts = line.split('//')
                code_part = parts[0]
                # If the code part has an odd number of quotes, the // might be inside a string
                # This is a basic check, a full parser would be better but slower
                if code_part.count("'") % 2 == 0 and code_part.count('"') % 2 == 0:
                    if code_part.strip():
                        lines.append(code_part)
                else:
                    lines.append(line)
            elif '#' in line and not line.strip().startswith('#!'):
                parts = line.split('#')
                code_part = parts[0]
                if code_part.count("'") % 2 == 0 and code_part.count('"') % 2 == 0:
                    if code_part.strip():
                        lines.append(code_part)
                else:
                    lines.append(line)
            else:
                lines.append(line)
        
        code = '\n'.join(lines)
        
        # Remove multi-line comments /* */
        # We use a custom function to preserve @deprecated blocks
        def replace_comment(match):
            comment = match.group(0)
            if keep_deprecated and '@deprecated' in comment.lower():
                return comment
            return ''
            
        code = re.sub(r'/\*.*?\*/', replace_comment, code, flags=re.DOTALL)
        
        return code
    
    def _collapse_whitespace(self, code: str) -> str:
        """
        Collapse excessive whitespace while maintaining readability
        
        Args:
            code: PHP code
            
        Returns:
            Code with collapsed whitespace
        """
        # First, strip every line to remove trailing/leading spaces where not needed
        # But we want to preserve indentation? The prompt said "maintain readability"
        # Actually, for token optimization, indentation is less critical than logic
        # But let's try to be smart.
        
        # Replace multiple newlines (possibly with spaces in between) with double newline
        code = re.sub(r'\n\s*\n\s*\n+', '\n\n', code)
        
        lines = []
        for line in code.split('\n'):
            # Collapse multiple spaces to single space, but preserve leading indentation
            stripped = line.lstrip()
            if not stripped:
                continue
                
            indentation = line[:len(line) - len(stripped)]
            # Collapse spaces inside the line
            collapsed_content = re.sub(r'[ \t]{2,}', ' ', stripped)
            lines.append(indentation + collapsed_content)
            
        return '\n'.join(lines)
    
    def _extract_critical_sections(
        self,
        code: str,
        patterns: Dict[str, Any]
    ) -> str:
        """
        Extract only critical sections for analysis
        
        Args:
            code: PHP code
            patterns: Extracted patterns from file
            
        Returns:
            Code with only critical sections
        """
        critical_sections = []
        
        # Always include file header (first 10 lines)
        lines = code.split('\n')
        critical_sections.append('\n'.join(lines[:10]))
        
        # Extract function signatures (not full bodies)
        for match in re.finditer(r'(function\s+\w+\s*\([^)]*\)[^{]*\{)', code):
            critical_sections.append(match.group(1) + '\n    // ... function body ...\n}')
        
        # Extract WordPress hooks (full context needed)
        for match in re.finditer(r'add_(action|filter)\s*\([^;]+;', code):
            critical_sections.append(match.group(0))
        
        # Extract database queries (security critical)
        if patterns['has_database_queries']:
            for match in re.finditer(r'(\$wpdb->|mysql_|mysqli_)[^;]+;', code):
                critical_sections.append(match.group(0))
        
        # Extract user input handling (security critical)
        if patterns['has_user_input']:
            for match in re.finditer(r'\$_(GET|POST|REQUEST|COOKIE)[^;]+;', code):
                critical_sections.append(match.group(0))
        
        return '\n\n'.join(critical_sections)
    
    def get_optimization_stats(
        self,
        files_processed: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate overall optimization statistics
        
        Args:
            files_processed: List of optimization results per file
            
        Returns:
            Aggregated statistics
        """
        total_original = sum(f['original_tokens'] for f in files_processed)
        total_optimized = sum(f['optimized_tokens'] for f in files_processed)
        total_saved = total_original - total_optimized
        
        return {
            'files_processed': len(files_processed),
            'total_original_tokens': total_original,
            'total_optimized_tokens': total_optimized,
            'total_tokens_saved': total_saved,
            'average_reduction_percent': (total_saved / total_original * 100) if total_original > 0 else 0,
            'files_by_complexity': {
                'low': sum(1 for f in files_processed if f['patterns']['complexity'] == 'low'),
                'medium': sum(1 for f in files_processed if f['patterns']['complexity'] == 'medium'),
                'high': sum(1 for f in files_processed if f['patterns']['complexity'] == 'high'),
            }
        }
