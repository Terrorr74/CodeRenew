"""
WordPress Scanner Service
Analyzes WordPress code for compatibility issues
"""
from typing import List, Dict, Any, Tuple
from pathlib import Path
import asyncio
from .analyzer import WordPressAnalyzer
from .hybrid_deprecation_db import HybridDeprecationDB
from .token_optimizer import TokenOptimizer
from .token_optimizer import TokenOptimizer
from app.services.claude.client import ClaudeClient
from app.core.config import settings


class WordPressScanner:
    """
    Scanner for WordPress themes and plugins.
    Uses static analysis and AI to identify compatibility issues.
    """

    # Token limits for Claude API
    MAX_TOKENS_PER_BATCH = settings.SCANNER_MAX_TOKENS_PER_BATCH
    CHARS_PER_TOKEN = 4  # Rough estimate
    MAX_CHARS_PER_BATCH = MAX_TOKENS_PER_BATCH * CHARS_PER_TOKEN
    
    # Retry configuration
    MAX_RETRIES = settings.SCANNER_MAX_RETRIES
    RETRY_DELAY = 2  # seconds

    def __init__(self, version_from: str, version_to: str):
        """
        Initialize scanner
        
        Args:
            version_from: Current WordPress version (e.g. "5.0")
            version_to: Target WordPress version (e.g. "6.0")
        """
        self.version_from = version_from
        self.version_to = version_to
        self.claude_client = ClaudeClient()
        self.analyzer = WordPressAnalyzer()
        self.deprecation_db = HybridDeprecationDB()
        self.optimizer = TokenOptimizer()
        
        # Statistics
        self.stats = {
            "files_processed": 0,
            "total_files": 0,
            "batches_processed": 0,
            "static_issues_found": 0,
            "ai_issues_found": 0,
            # Token optimization stats
            "original_tokens": 0,
            "optimized_tokens": 0,
            "tokens_saved": 0,
            "files_skipped": 0,
            "optimization_enabled": True,
        }

    async def scan_files(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """
        Scan WordPress files for compatibility issues using intelligent batching

        Args:
            file_paths: List of file paths to scan

        Returns:
            List of detected issues
        """
        self.stats["total_files"] = len(file_paths)
        all_issues = []
        
        # Filter and prioritize PHP files
        php_files = []
        skipped_files = 0
        
        for f in file_paths:
            if f.suffix == '.php' and f.exists():
                if self.optimizer.should_skip_file(f):
                    skipped_files += 1
                    continue
                php_files.append(f)
        
        self.stats["files_skipped"] = skipped_files
        
        if not php_files:
            return all_issues
        
        # Sort by priority (high priority first)
        php_files.sort(key=lambda f: self.analyzer.get_file_priority(f), reverse=True)
        
        # First pass: Static analysis on all files
        print(f"Running static analysis on {len(php_files)} files...")
        static_issues = await self._run_static_analysis(php_files)
        all_issues.extend(static_issues)
        self.stats["static_issues_found"] = len(static_issues)
        
        # Second pass: Batch files for AI analysis
        print(f"Creating batches for AI analysis...")
        batches = self._batch_files(php_files)
        print(f"Created {len(batches)} batches for analysis")
        
        # Process each batch with AI
        for i, batch in enumerate(batches):
            print(f"Processing batch {i+1}/{len(batches)} ({len(batch)} files)...")
            
            try:
                batch_issues = await self._scan_batch(batch)
                all_issues.extend(batch_issues)
                self.stats["batches_processed"] += 1
                self.stats["ai_issues_found"] += len(batch_issues)
            except Exception as e:
                print(f"Error processing batch {i+1}: {str(e)}")
                # Log error details for debugging
                import traceback
                traceback.print_exc()
                # Continue with next batch even if one fails
                
        print(f"Scan complete: {len(all_issues)} total issues found")
        return all_issues

    async def _run_static_analysis(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """
        Run static analysis on all files
        
        Args:
            file_paths: List of PHP files to analyze
            
        Returns:
            List of issues found by static analysis
        """
        static_issues = []
        
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if not content.strip():
                    continue
                
                # Run quick scan
                scan_result = self.analyzer.quick_scan(
                    content,
                    self.version_from,
                    self.version_to
                )
                
                # Convert deprecated usage to issues
                for dep in scan_result.get('deprecated_usage', []):
                    static_issues.append({
                        'file': file_path.name,
                        'file_path': str(file_path),
                        'line': dep['line'],
                        'severity': dep['severity'],
                        'issue_type': 'deprecated_function',
                        'description': dep['description'],
                        'recommendation': f"Replace {dep['function']} with {dep['replacement']}" if dep['replacement'] else "Update this deprecated function",
                        'source': 'static_analysis',
                    })
                
                # Convert security issues
                for sec in scan_result.get('security_issues', []):
                    static_issues.append({
                        'file': file_path.name,
                        'file_path': str(file_path),
                        'line': sec['line'],
                        'severity': sec['severity'],
                        'issue_type': 'security',
                        'description': sec['description'],
                        'recommendation': 'Review and fix this security issue',
                        'code_snippet': sec.get('code_snippet'),
                        'source': 'static_analysis',
                    })
                
                self.stats["files_processed"] += 1
                
            except Exception as e:
                print(f"Error in static analysis of {file_path}: {e}")
                
        return static_issues

    def _batch_files(self, file_paths: List[Path]) -> List[List[Path]]:
        """
        Intelligently batch files for AI analysis
        
        Args:
            file_paths: List of file paths to batch
            
        Returns:
            List of batches (each batch is a list of file paths)
        """
        batches = []
        current_batch = []
        current_size = 0
        current_tokens = 0
        
        for file_path in file_paths:
            try:
                file_size = file_path.stat().st_size
                estimated_tokens = self._estimate_tokens_for_file(file_path)
                
                # Check if adding this file would exceed limits
                would_exceed_chars = current_size + file_size > self.MAX_CHARS_PER_BATCH
                would_exceed_tokens = current_tokens + estimated_tokens > self.MAX_TOKENS_PER_BATCH
                
                if (would_exceed_chars or would_exceed_tokens) and current_batch:
                    # Context window would be overloaded, start new batch
                    print(f"Batch full ({len(current_batch)} files, ~{current_tokens} tokens), starting new batch")
                    batches.append(current_batch)
                    current_batch = []
                    current_size = 0
                    current_tokens = 0
                
                current_batch.append(file_path)
                current_size += file_size
                current_tokens += estimated_tokens
                
                # Also limit batch size by number of files (max 20 files per batch)
                if len(current_batch) >= 20:
                    print(f"Batch reached max file count (20), starting new batch")
                    batches.append(current_batch)
                    current_batch = []
                    current_size = 0
                    current_tokens = 0
                    
            except Exception as e:
                print(f"Error getting file size for {file_path}: {e}")
        
        # Add remaining files
        if current_batch:
            batches.append(current_batch)
        
        return batches
    
    def _estimate_tokens_for_file(self, file_path: Path) -> int:
        """
        Estimate token count for a file using optimizer
        
        Args:
            file_path: Path to the file
            
        Returns:
            Estimated token count
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return self.optimizer.count_tokens(content)
        except Exception:
            return 1000  # Default estimate if we can't read file
    
    def estimate_total_tokens(self, file_paths: List[Path]) -> Dict[str, Any]:
        """
        Estimate total tokens needed for analyzing a project
        
        Args:
            file_paths: List of file paths to analyze
            
        Returns:
            Dictionary with token estimates and batch information
        """
        php_files = [f for f in file_paths if f.suffix == '.php' and f.exists()]
        
        total_tokens = 0
        file_estimates = []
        
        for file_path in php_files:
            tokens = self._estimate_tokens_for_file(file_path)
            total_tokens += tokens
            file_estimates.append({
                'file': str(file_path),
                'estimated_tokens': tokens,
                'size_bytes': file_path.stat().st_size if file_path.exists() else 0
            })
        
        # Estimate number of batches needed
        estimated_batches = max(1, (total_tokens // self.MAX_TOKENS_PER_BATCH) + 1)
        
        # Estimate API cost (rough estimate based on Claude pricing)
        # Claude 3.5 Sonnet: ~$3 per million input tokens, ~$15 per million output tokens
        # Assume 2k output tokens per batch
        input_cost = (total_tokens / 1_000_000) * 3.0
        output_cost = (estimated_batches * 2000 / 1_000_000) * 15.0
        estimated_cost = input_cost + output_cost
        
        return {
            'total_files': len(php_files),
            'total_tokens': total_tokens,
            'estimated_batches': estimated_batches,
            'tokens_per_batch_limit': self.MAX_TOKENS_PER_BATCH,
            'estimated_cost_usd': round(estimated_cost, 2),
            'file_estimates': sorted(file_estimates, key=lambda x: x['estimated_tokens'], reverse=True)[:10],  # Top 10 largest
            'context_overflow_risk': 'high' if total_tokens > self.MAX_TOKENS_PER_BATCH * 10 else 'medium' if total_tokens > self.MAX_TOKENS_PER_BATCH * 3 else 'low'
        }


    async def _scan_batch(self, batch: List[Path]) -> List[Dict[str, Any]]:
        """
        Scan a batch of files with Claude AI (with retry logic)
        
        Args:
            batch: List of file paths in this batch
            
        Returns:
            List of issues found in this batch
        """
        # Read all files in batch
        files_content = []
        for file_path in batch:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if content.strip():
                        # Optimize code if enabled
                        if self.stats.get("optimization_enabled", True):
                            optimization_result = self.optimizer.optimize_code(content)
                            optimized_content = optimization_result['optimized_code']
                            
                            # Update stats
                            self.stats["original_tokens"] += optimization_result['original_tokens']
                            self.stats["optimized_tokens"] += optimization_result['optimized_tokens']
                            self.stats["tokens_saved"] += optimization_result['tokens_saved']
                            
                            files_content.append({
                                'filename': file_path.name,
                                'filepath': str(file_path),
                                'content': optimized_content,
                                'original_content': content  # Keep original for reference if needed
                            })
                        else:
                            files_content.append({
                                'filename': file_path.name,
                                'filepath': str(file_path),
                                'content': content,
                            })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        if not files_content:
            return []
        
        # Try to analyze with retries
        for attempt in range(self.MAX_RETRIES):
            try:
                analysis = await self._analyze_with_claude_batch(files_content)
                
                # Add file context to issues
                batch_issues = []
                for issue in analysis.get('issues', []):
                    # Ensure file path is set
                    if 'file' not in issue or not issue['file']:
                        # Try to infer from filepath if available
                        if 'file_path' in issue:
                            issue['file'] = Path(issue['file_path']).name
                        else:
                            # Use first file in batch as fallback
                            issue['file'] = files_content[0]['filename']
                            issue['file_path'] = files_content[0]['filepath']
                    
                    issue['source'] = 'ai_analysis'
                    batch_issues.append(issue)
                
                return batch_issues
                
            except Exception as e:
                print(f"Attempt {attempt + 1}/{self.MAX_RETRIES} failed: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))  # Exponential backoff
                else:
                    print(f"Failed to analyze batch after {self.MAX_RETRIES} attempts")
                    return []
        
        return []

    async def _analyze_with_claude_batch(self, files: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analyze a batch of files with Claude using tool use
        
        Args:
            files: List of file dictionaries with filename and content
            
        Returns:
            Analysis results
        """
        # Build context from deprecation DB
        context_parts = []
        
        # Add version-specific context
        # Use async method if available, otherwise sync
        if hasattr(self.deprecation_db, 'get_deprecated_in_range_async'):
            deprecations = await self.deprecation_db.get_deprecated_in_range_async(self.version_from, self.version_to)
        else:
            deprecations = self.deprecation_db.get_deprecated_in_range(self.version_from, self.version_to)
            
        if deprecations:
            context_parts.append(f"## Deprecations in WordPress {self.version_from} to {self.version_to}")
            for dep in deprecations[:50]:  # Limit context size
                context_parts.append(f"- {dep.name} ({dep.change_type}): {dep.description}")
        
        context = "\n".join(context_parts)
        
        # Use tool-based analysis for structured output
        return await self.claude_client.analyze_code_batch_with_tool(
            files=files,
            version_from=self.version_from,
            version_to=self.version_to,
            context=context
        )

    def _build_batch_context(self, files: List[Dict[str, str]]) -> str:
        """
        Build context string for batch analysis
        
        Args:
            files: List of file dictionaries
            
        Returns:
            Context string
        """
        # Get version-specific deprecations
        deprecated_items = self.deprecation_db.get_deprecated_in_range(
            self.version_from,
            self.version_to
        )
        
        # Build context
        context_parts = [
            f"Analyzing {len(files)} files from a WordPress theme/plugin",
            f"Upgrading from WordPress {self.version_from} to {self.version_to}",
            f"\nKnown deprecations in this version range: {len(deprecated_items)}",
        ]
        
        # Add critical changes
        critical = self.deprecation_db.get_critical_changes(
            self.version_from,
            self.version_to
        )
        
        if critical:
            context_parts.append("\nCritical changes to watch for:")
            for item in critical[:5]:  # Limit to top 5
                context_parts.append(f"- {item.name}: {item.description}")
        
        return "\n".join(context_parts)

    async def analyze_with_claude(self, code: str) -> Dict[str, Any]:
        """
        Use Claude API to analyze code for compatibility issues (legacy single-file method)

        Args:
            code: PHP code to analyze

        Returns:
            Analysis results from Claude
        """
        from app.services.claude.client import ClaudeClient
        
        client = ClaudeClient()
        return await client.analyze_code(
            code=code,
            version_from=self.version_from,
            version_to=self.version_to
        )

    def calculate_risk_level(self, issues: List[Dict[str, Any]]) -> str:
        """
        Calculate overall risk level based on detected issues

        Args:
            issues: List of detected issues

        Returns:
            Risk level: safe, warning, critical
        """
        if not issues:
            return "safe"
            
        critical_count = sum(1 for i in issues if i.get('severity') == 'critical')
        high_count = sum(1 for i in issues if i.get('severity') == 'high')
        
        if critical_count > 0:
            return "critical"
        if high_count > 0:
            return "warning"
            
        return "safe"
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get scanning statistics
        
        Returns:
            Dictionary of statistics
        """
        return self.stats.copy()
