"""
WordPress Scanner Service
Analyzes WordPress code for compatibility issues
"""
from typing import List, Dict, Any
from pathlib import Path


class WordPressScanner:
    """WordPress compatibility scanner"""

    def __init__(self, version_from: str, version_to: str):
        """
        Initialize scanner

        Args:
            version_from: Starting WordPress version
            version_to: Target WordPress version
        """
        self.version_from = version_from
        self.version_to = version_to

    async def scan_files(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """
        Scan WordPress files for compatibility issues

        Args:
            file_paths: List of file paths to scan

        Returns:
            List of detected issues
        """
        all_issues = []
        
        # For now, we'll scan files one by one. 
        # In production, we might want to batch them or concatenate related files.
        for file_path in file_paths:
            if not file_path.exists() or not file_path.suffix == '.php':
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Skip empty files
                if not content.strip():
                    continue
                    
                # Analyze with Claude
                analysis = await self.analyze_with_claude(content)
                
                # Add file context to issues
                file_issues = analysis.get('issues', [])
                for issue in file_issues:
                    issue['file'] = file_path.name
                    issue['file_path'] = str(file_path)
                    all_issues.append(issue)
                    
            except Exception as e:
                print(f"Error scanning file {file_path}: {e}")
                
        return all_issues

    async def analyze_with_claude(self, code: str) -> Dict[str, Any]:
        """
        Use Claude API to analyze code for compatibility issues

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
