"""
Slack webhook message templates using Block Kit
"""
from typing import Dict, Any
from datetime import datetime


def format_scan_completed(scan_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format scan completion event as Slack Block Kit message
    
    Args:
        scan_data: Dictionary containing scan information
            - scan_id: Scan ID
            - site_name: Site name
            - risk_level: Risk level (low, medium, high, critical)
            - issues_found: Number of issues found
            - completed_at: Completion timestamp
            - dashboard_url: URL to view scan results
    
    Returns:
        Slack Block Kit formatted message
    """
    risk_level = scan_data.get('risk_level', 'unknown').lower()
    issues_found = scan_data.get('issues_found', 0)
    
    # Determine color and emoji based on risk level
    risk_colors = {
        'low': '#36a64f',  # Green
        'medium': '#ff9900',  # Orange
        'high': '#ff0000',  # Red
        'critical': '#8b0000',  # Dark red
        'unknown': '#808080'  # Gray
    }
    
    risk_emojis = {
        'low': '✅',
        'medium': '⚠️',
        'high': '🚨',
        'critical': '🔴',
        'unknown': '❓'
    }
    
    color = risk_colors.get(risk_level, risk_colors['unknown'])
    emoji = risk_emojis.get(risk_level, risk_emojis['unknown'])
    
    # Build Slack message with Block Kit
    message = {
        "text": f"{emoji} Scan Completed: {scan_data.get('site_name', 'Unknown Site')}",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} WordPress Scan Completed"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Site:*\n{scan_data.get('site_name', 'Unknown')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Risk Level:*\n{risk_level.upper()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Issues Found:*\n{issues_found}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Completed:*\n{scan_data.get('completed_at', 'Unknown')}"
                    }
                ]
            },
            {
                "type": "divider"
            }
        ]
    }
    
    # Add action button if dashboard URL provided
    if scan_data.get('dashboard_url'):
        message["blocks"].append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Scan Results"
                    },
                    "url": scan_data['dashboard_url'],
                    "style": "primary"
                }
            ]
        })
    
    # Add color to attachment for visual impact
    message["attachments"] = [{
        "color": color,
        "blocks": []
    }]
    
    return message


def format_vulnerability_found(vulnerability_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format vulnerability detection event as Slack Block Kit message
    
    Args:
        vulnerability_data: Dictionary containing vulnerability information
            - cve_id: CVE identifier
            - severity: Severity level
            - description: Vulnerability description
            - affected_component: Affected plugin/theme
            - epss_score: EPSS exploitation score
            - dashboard_url: URL to view details
    
    Returns:
        Slack Block Kit formatted message
    """
    severity = vulnerability_data.get('severity', 'unknown').lower()
    
    severity_emojis = {
        'critical': '🔴',
        'high': '🚨',
        'medium': '⚠️',
        'low': 'ℹ️',
        'unknown': '❓'
    }
    
    emoji = severity_emojis.get(severity, severity_emojis['unknown'])
    
    message = {
        "text": f"{emoji} Vulnerability Found: {vulnerability_data.get('cve_id', 'Unknown CVE')}",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} Vulnerability Detected"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*CVE ID:*\n{vulnerability_data.get('cve_id', 'N/A')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Severity:*\n{severity.upper()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Component:*\n{vulnerability_data.get('affected_component', 'Unknown')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*EPSS Score:*\n{vulnerability_data.get('epss_score', 'N/A')}"
                    }
                ]
            }
        ]
    }
    
    # Add description if available
    if vulnerability_data.get('description'):
        message["blocks"].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Description:*\n{vulnerability_data['description'][:500]}"
            }
        })
    
    # Add action button
    if vulnerability_data.get('dashboard_url'):
        message["blocks"].append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Details"
                    },
                    "url": vulnerability_data['dashboard_url'],
                    "style": "danger"
                }
            ]
        })
    
    return message


def format_test_message(test_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format test webhook message
    
    Args:
        test_data: Dictionary containing test information
            - message: Custom test message
            - timestamp: Test timestamp
    
    Returns:
        Slack Block Kit formatted message
    """
    return {
        "text": "🧪 Test Webhook from CodeRenew",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🧪 Test Webhook"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": test_data.get('message', 'This is a test webhook from CodeRenew')
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Sent at: {test_data.get('timestamp', datetime.utcnow().isoformat())}"
                    }
                ]
            }
        ]
    }
