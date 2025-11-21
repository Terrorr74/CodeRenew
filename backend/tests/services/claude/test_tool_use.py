"""
Unit tests for Tool Use Integration
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.claude.client import ClaudeClient
from app.services.wordpress.scanner import WordPressScanner


@pytest.mark.asyncio
async def test_analyze_code_batch_with_tool():
    """Test that client calls API with correct tool parameters"""
    client = ClaudeClient(api_key="test_key")
    client.client = MagicMock()
    client.client.messages.create = MagicMock()
    
    # Mock response
    mock_response = MagicMock()
    mock_content = MagicMock()
    mock_content.type = "tool_use"
    mock_content.name = "report_compatibility_issues"
    mock_content.input = {
        "risk_level": "safe",
        "summary": "No issues",
        "issues": []
    }
    mock_response.content = [mock_content]
    client.client.messages.create.return_value = mock_response
    
    files = [{"filename": "test.php", "content": "<?php echo 'test'; ?>"}]
    result = await client.analyze_code_batch_with_tool(files, "5.0", "6.0")
    
    # Verify result
    assert result["risk_level"] == "safe"
    
    # Verify API call
    call_args = client.client.messages.create.call_args
    assert call_args is not None
    kwargs = call_args[1]
    
    assert "tools" in kwargs
    assert kwargs["tools"][0]["name"] == "report_compatibility_issues"
    assert kwargs["tool_choice"]["name"] == "report_compatibility_issues"
    assert "Report your findings" in kwargs["messages"][0]["content"]


@pytest.mark.asyncio
async def test_scanner_uses_tool_analysis():
    """Test that scanner uses the tool-based analysis method"""
    scanner = WordPressScanner("5.0", "6.0")
    scanner.claude_client = AsyncMock()
    scanner.claude_client.analyze_code_batch_with_tool.return_value = {
        "risk_level": "warning",
        "summary": "Issues found",
        "issues": []
    }
    
    files = [{"filename": "test.php", "content": "test"}]
    await scanner._analyze_with_claude_batch(files)
    
    # Verify scanner calls the correct method
    scanner.claude_client.analyze_code_batch_with_tool.assert_called_once()
    scanner.claude_client.analyze_code_batch.assert_not_called()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
