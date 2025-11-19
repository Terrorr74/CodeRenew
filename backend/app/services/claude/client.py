"""
Claude API Client
Handles communication with Anthropic's Claude API
"""
from typing import Optional, List, Dict, Any
import anthropic
from app.core.config import settings


class ClaudeClient:
    """Client for interacting with Claude API"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude client

        Args:
            api_key: Anthropic API key (defaults to settings)
        """
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.client = anthropic.Anthropic(api_key=self.api_key)

    async def analyze_code(
        self,
        code: str,
        version_from: str,
        version_to: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze WordPress code for compatibility issues

        Args:
            code: PHP code to analyze
            version_from: Starting WordPress version
            version_to: Target WordPress version
            context: Additional context for analysis

        Returns:
            Analysis results from Claude
        """
        prompt = self._build_analysis_prompt(code, version_from, version_to, context)

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                temperature=0,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract JSON content from response
            # Assuming Claude returns the JSON block as requested
            content = message.content[0].text
            
            # Basic cleanup if Claude wraps in markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            import json
            return json.loads(content)
            
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            return {
                "issues": [],
                "summary": f"Error analyzing code: {str(e)}",
                "recommendations": [],
                "risk_level": "unknown"
            }

    def _build_analysis_prompt(
        self,
        code: str,
        version_from: str,
        version_to: str,
        context: Optional[str] = None
    ) -> str:
        """
        Build prompt for code analysis

        Args:
            code: PHP code to analyze
            version_from: Starting WordPress version
            version_to: Target WordPress version
            context: Additional context

        Returns:
            Formatted prompt string
        """
        prompt = f"""
You are a WordPress compatibility expert. Analyze the following PHP code for compatibility issues when upgrading from WordPress {version_from} to {version_to}.

Please identify:
1. Deprecated functions and hooks
2. Removed functions
3. Breaking changes
4. Security concerns
5. Compatibility warnings

For each issue, provide:
- Issue type
- Severity (info, low, medium, high, critical)
- Line number (if applicable)
- Description
- Recommendation for fixing

Code to analyze:
```php
{code}
```

{f"Additional context: {context}" if context else ""}

Provide your analysis in the following valid JSON format ONLY. Do not include any other text.

{{
  "risk_level": "safe|warning|critical",
  "summary": "Brief summary of findings",
  "issues": [
    {{
      "severity": "critical|warning|info",
      "issue_type": "deprecated_function|breaking_change|security|best_practice",
      "line": 123,
      "description": "Clear explanation of the issue",
      "recommendation": "Specific steps to fix"
    }}
  ],
  "recommendations": [
      "General recommendation 1",
      "General recommendation 2"
  ]
}}
"""
        return prompt
