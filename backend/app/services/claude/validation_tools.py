"""
Claude Tool Definitions for Validation
Defines structured output schemas for tool use
"""
from typing import Dict, Any


def get_compatibility_analysis_tool() -> Dict[str, Any]:
    """
    Returns Claude tool definition for structured WordPress compatibility analysis
    
    Returns:
        Tool definition dictionary
    """
    return {
        "name": "report_compatibility_issues",
        "description": "Report WordPress compatibility issues found in the analyzed code",
        "input_schema": {
            "type": "object",
            "properties": {
                "risk_level": {
                    "type": "string",
                    "enum": ["safe", "warning", "critical"],
                    "description": "Overall risk assessment for the analyzed code"
                },
                "summary": {
                    "type": "string",
                    "description": "Brief summary of the compatibility findings"
                },
                "issues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "file": {
                                "type": "string",
                                "description": "Filename where the issue was found"
                            },
                            "severity": {
                                "type": "string",
                                "enum": ["critical", "high", "medium", "low", "info"],
                                "description": "Severity of the issue"
                            },
                            "issue_type": {
                                "type": "string",
                                "enum": [
                                    "deprecated_function", 
                                    "removed_function", 
                                    "breaking_change", 
                                    "security", 
                                    "best_practice"
                                ],
                                "description": "Type of compatibility issue"
                            },
                            "line": {
                                "type": "integer",
                                "description": "Line number where the issue occurs (if known)"
                            },
                            "description": {
                                "type": "string",
                                "description": "Clear explanation of what is wrong"
                            },
                            "recommendation": {
                                "type": "string",
                                "description": "Specific actionable steps to fix the issue"
                            },
                            "code_snippet": {
                                "type": "string",
                                "description": "The problematic code snippet (optional)"
                            }
                        },
                        "required": ["file", "severity", "issue_type", "description", "recommendation"]
                    },
                    "description": "List of specific compatibility issues found"
                },
                "recommendations": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "General recommendations for the entire codebase"
                }
            },
            "required": ["risk_level", "summary", "issues"]
        }
    }
