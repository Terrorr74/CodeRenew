"""
Microsoft Teams webhook message templates using Adaptive Cards
"""
from typing import Dict, Any
from datetime import datetime


def format_scan_completed(scan_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format scan completion event as Teams Adaptive Card
    
    Args:
        scan_data: Dictionary containing scan information
            - scan_id: Scan ID
            - site_name: Site name
            - risk_level: Risk level (low, medium, high, critical)
            - issues_found: Number of issues found
            - completed_at: Completion timestamp
            - dashboard_url: URL to view scan results
    
    Returns:
        Teams Adaptive Card formatted message
    """
    risk_level = scan_data.get('risk_level', 'unknown').lower()
    issues_found = scan_data.get('issues_found', 0)
    
    # Determine color based on risk level
    risk_colors = {
        'low': 'good',  # Green
        'medium': 'warning',  # Yellow
        'high': 'attention',  # Red
        'critical': 'attention',  # Red
        'unknown': 'default'  # Gray
    }
    
    color = risk_colors.get(risk_level, 'default')
    
    # Build Adaptive Card
    card = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "type": "AdaptiveCard",
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": "✅ WordPress Scan Completed",
                            "weight": "bolder",
                            "size": "large",
                            "wrap": True
                        },
                        {
                            "type": "FactSet",
                            "facts": [
                                {
                                    "title": "Site:",
                                    "value": scan_data.get('site_name', 'Unknown')
                                },
                                {
                                    "title": "Risk Level:",
                                    "value": risk_level.upper()
                                },
                                {
                                    "title": "Issues Found:",
                                    "value": str(issues_found)
                                },
                                {
                                    "title": "Completed:",
                                    "value": scan_data.get('completed_at', 'Unknown')
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }
    
    # Add action button if dashboard URL provided
    if scan_data.get('dashboard_url'):
        card["attachments"][0]["content"]["body"].append({
            "type": "ActionSet",
            "actions": [
                {
                    "type": "Action.OpenUrl",
                    "title": "View Scan Results",
                    "url": scan_data['dashboard_url'],
                    "style": "positive"
                }
            ]
        })
    
    # Add color indicator
    if color != 'default':
        card["attachments"][0]["content"]["body"].insert(0, {
            "type": "Container",
            "style": color,
            "items": [
                {
                    "type": "TextBlock",
                    "text": f"Risk Level: {risk_level.upper()}",
                    "weight": "bolder"
                }
            ]
        })
    
    return card


def format_vulnerability_found(vulnerability_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format vulnerability detection event as Teams Adaptive Card
    
    Args:
        vulnerability_data: Dictionary containing vulnerability information
            - cve_id: CVE identifier
            - severity: Severity level
            - description: Vulnerability description
            - affected_component: Affected plugin/theme
            - epss_score: EPSS exploitation score
            - dashboard_url: URL to view details
    
    Returns:
        Teams Adaptive Card formatted message
    """
    severity = vulnerability_data.get('severity', 'unknown').lower()
    
    # Build Adaptive Card
    card = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "type": "AdaptiveCard",
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "Container",
                            "style": "attention",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": "🚨 Vulnerability Detected",
                                    "weight": "bolder",
                                    "size": "large",
                                    "wrap": True
                                }
                            ]
                        },
                        {
                            "type": "FactSet",
                            "facts": [
                                {
                                    "title": "CVE ID:",
                                    "value": vulnerability_data.get('cve_id', 'N/A')
                                },
                                {
                                    "title": "Severity:",
                                    "value": severity.upper()
                                },
                                {
                                    "title": "Component:",
                                    "value": vulnerability_data.get('affected_component', 'Unknown')
                                },
                                {
                                    "title": "EPSS Score:",
                                    "value": str(vulnerability_data.get('epss_score', 'N/A'))
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }
    
    # Add description if available
    if vulnerability_data.get('description'):
        card["attachments"][0]["content"]["body"].append({
            "type": "TextBlock",
            "text": vulnerability_data['description'][:500],
            "wrap": True,
            "separator": True
        })
    
    # Add action button
    if vulnerability_data.get('dashboard_url'):
        card["attachments"][0]["content"]["body"].append({
            "type": "ActionSet",
            "actions": [
                {
                    "type": "Action.OpenUrl",
                    "title": "View Details",
                    "url": vulnerability_data['dashboard_url'],
                    "style": "destructive"
                }
            ]
        })
    
    return card


def format_test_message(test_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format test webhook message
    
    Args:
        test_data: Dictionary containing test information
            - message: Custom test message
            - timestamp: Test timestamp
    
    Returns:
        Teams Adaptive Card formatted message
    """
    return {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "type": "AdaptiveCard",
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": "🧪 Test Webhook from CodeRenew",
                            "weight": "bolder",
                            "size": "large",
                            "wrap": True
                        },
                        {
                            "type": "TextBlock",
                            "text": test_data.get('message', 'This is a test webhook from CodeRenew'),
                            "wrap": True
                        },
                        {
                            "type": "TextBlock",
                            "text": f"Sent at: {test_data.get('timestamp', datetime.utcnow().isoformat())}",
                            "size": "small",
                            "isSubtle": True,
                            "separator": True
                        }
                    ]
                }
            }
        ]
    }
