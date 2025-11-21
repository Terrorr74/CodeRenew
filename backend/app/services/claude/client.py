"""
Claude API Client
Handles communication with Anthropic's Claude API with retry logic and circuit breaker
"""
from typing import Optional, List, Dict, Any
import logging
import anthropic
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    RetryError
)
import pybreaker

from app.core.config import settings
from app.core.circuit_breaker import claude_circuit_breaker
from app.core.exceptions import ClaudeAPIError, CircuitBreakerOpenError

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Client for interacting with Claude API with resilience patterns"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude client

        Args:
            api_key: Anthropic API key (defaults to settings)
        """
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.max_retries = settings.SCANNER_MAX_RETRIES

    def _is_retryable_error(self, exc: Exception) -> bool:
        """Check if error is retryable"""
        if isinstance(exc, anthropic.RateLimitError):
            return True
        if isinstance(exc, anthropic.APIConnectionError):
            return True
        if isinstance(exc, anthropic.InternalServerError):
            return True
        if isinstance(exc, anthropic.APIStatusError):
            return exc.status_code >= 500
        return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((
            anthropic.RateLimitError,
            anthropic.APIConnectionError,
            anthropic.InternalServerError,
        )),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def _call_claude_api(
        self,
        messages: List[Dict],
        tools: Optional[List[Dict]] = None,
        tool_choice: Optional[Dict] = None,
        max_tokens: int = 8192,
        temperature: float = 0
    ) -> anthropic.types.Message:
        """
        Make API call to Claude with retry logic

        Args:
            messages: List of message dicts
            tools: Optional tools for tool use
            tool_choice: Optional tool choice config
            max_tokens: Max tokens for response
            temperature: Temperature setting

        Returns:
            Claude API message response

        Raises:
            ClaudeAPIError: If API call fails after retries
        """
        try:
            kwargs = {
                "model": settings.CLAUDE_MODEL,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages
            }
            if tools:
                kwargs["tools"] = tools
            if tool_choice:
                kwargs["tool_choice"] = tool_choice

            return self.client.messages.create(**kwargs)

        except anthropic.AuthenticationError as e:
            logger.error(f"Claude API authentication error: {e}")
            raise ClaudeAPIError("Invalid API key", {"type": "authentication"})

        except anthropic.BadRequestError as e:
            logger.error(f"Claude API bad request: {e}")
            raise ClaudeAPIError(f"Bad request: {str(e)}", {"type": "bad_request"})

        except anthropic.RateLimitError as e:
            logger.warning(f"Claude API rate limited: {e}")
            raise  # Let tenacity retry

        except anthropic.APIConnectionError as e:
            logger.warning(f"Claude API connection error: {e}")
            raise  # Let tenacity retry

        except anthropic.InternalServerError as e:
            logger.warning(f"Claude API server error: {e}")
            raise  # Let tenacity retry

        except Exception as e:
            logger.error(f"Unexpected Claude API error: {type(e).__name__}: {e}")
            raise ClaudeAPIError(f"Unexpected error: {str(e)}")

    def _call_with_circuit_breaker(
        self,
        messages: List[Dict],
        tools: Optional[List[Dict]] = None,
        tool_choice: Optional[Dict] = None,
        max_tokens: int = 8192,
        temperature: float = 0
    ) -> anthropic.types.Message:
        """Call Claude API with circuit breaker protection"""
        try:
            return claude_circuit_breaker.call(
                self._call_claude_api,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                max_tokens=max_tokens,
                temperature=temperature
            )
        except pybreaker.CircuitBreakerError:
            logger.error("Circuit breaker open for Claude API")
            raise CircuitBreakerOpenError("claude_api")

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
      "severity": "critical|high|medium|low|info",
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

    async def analyze_code_batch_with_tool(
        self,
        files: List[Dict[str, str]],
        version_from: str,
        version_to: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze multiple WordPress files using Claude's tool use for structured output
        with retry logic and circuit breaker protection

        Args:
            files: List of file dictionaries
            version_from: Starting WordPress version
            version_to: Target WordPress version
            context: Additional context

        Returns:
            Validated analysis results
        """
        from .validation_tools import get_compatibility_analysis_tool

        prompt = self._build_batch_analysis_prompt(files, version_from, version_to, context, use_tool=True)
        tool = get_compatibility_analysis_tool()

        try:
            message = self._call_with_circuit_breaker(
                messages=[{"role": "user", "content": prompt}],
                tools=[tool],
                tool_choice={"type": "tool", "name": tool["name"]},
                max_tokens=8192,
                temperature=0
            )

            # Extract tool use content
            for content in message.content:
                if content.type == "tool_use" and content.name == tool["name"]:
                    return content.input

            # Fallback if no tool use found (shouldn't happen with tool_choice)
            logger.warning("No tool use found in response")
            return {
                "issues": [],
                "summary": "Analysis failed to produce structured output",
                "risk_level": "unknown",
                "recommendations": []
            }

        except CircuitBreakerOpenError:
            raise
        except ClaudeAPIError:
            raise
        except RetryError as e:
            logger.error(f"Claude API failed after retries: {e}")
            raise ClaudeAPIError(f"API failed after {self.max_retries} retries")
        except Exception as e:
            logger.error(f"Error calling Claude API with tool: {e}")
            raise ClaudeAPIError(f"Error analyzing batch: {str(e)}")

    def _build_batch_analysis_prompt(
        self,
        files: List[Dict[str, str]],
        version_from: str,
        version_to: str,
        context: Optional[str] = None,
        use_tool: bool = False
    ) -> str:
        """
        Build prompt for batch code analysis

        Args:
            files: List of file dictionaries
            version_from: Starting WordPress version
            version_to: Target WordPress version
            context: Additional context
            use_tool: If True, optimize prompt for tool use (no JSON instructions)

        Returns:
            Formatted prompt string
        """
        # Build files section
        files_section = []
        for file_info in files:
            filename = file_info.get('filename', 'unknown.php')
            content = file_info.get('content', '')
            files_section.append(f"""
### File: {filename}
```php
{content}
```
""")

        files_text = "\n".join(files_section)

        base_prompt = f"""
You are a WordPress compatibility expert. Analyze the following WordPress theme/plugin files for compatibility issues when upgrading from WordPress {version_from} to {version_to}.

{context if context else ""}

## Files to Analyze ({len(files)} files)

{files_text}

## Analysis Instructions

Please identify across ALL files:
1. Deprecated functions and hooks
2. Removed functions that will cause fatal errors
3. Breaking changes in WordPress core
4. Security vulnerabilities
5. Best practice violations

## Important Guidelines

- Focus on REAL compatibility issues between WordPress {version_from} and {version_to}
- Be conservative: only flag actual problems, not hypothetical ones
- Prioritize issues that will cause fatal errors or security vulnerabilities
- Consider the context of how files work together
- For deprecated functions, check if they're actually removed in the target version
"""

        if use_tool:
            # For tool use, we just tell it to use the tool
            return base_prompt + "\n\nReport your findings using the available tool."
        else:
            # Legacy JSON instructions
            return base_prompt + """
For each issue found, provide:
- **file**: The filename where the issue was found
- **severity**: critical (will break), high (likely to break), medium (may break), low (minor issue), info (suggestion)
- **issue_type**: deprecated_function, removed_function, breaking_change, security, or best_practice
- **line**: Line number in the file (if identifiable)
- **description**: Clear explanation of what's wrong
- **recommendation**: Specific actionable steps to fix it

Provide your analysis in the following valid JSON format ONLY. Do not include any explanatory text outside the JSON.

{{
  "risk_level": "safe|warning|critical",
  "summary": "Brief summary of findings across all files",
  "issues": [
    {{
      "file": "filename.php",
      "severity": "critical|high|medium|low|info",
      "issue_type": "deprecated_function|removed_function|breaking_change|security|best_practice",
      "line": 123,
      "description": "Clear explanation of the issue",
      "recommendation": "Specific steps to fix",
      "code_snippet": "optional code snippet showing the problem"
    }}
  ],
  "recommendations": [
      "General recommendation 1 for the entire codebase",
      "General recommendation 2"
  ]
}}
"""
