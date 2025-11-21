"""
Email service
Handles sending emails using Resend
"""
import resend
from app.core.config import settings

# Initialize Resend
resend.api_key = settings.RESEND_API_KEY


def send_email(
    email_to: str,
    subject: str,
    html_content: str
) -> dict:
    """
    Send an email using Resend
    
    Args:
        email_to: Recipient email
        subject: Email subject
        html_content: HTML content of the email
        
    Returns:
        Resend API response
    """
    if not settings.RESEND_API_KEY:
        print(f"WARNING: RESEND_API_KEY not set. Email to {email_to} would have been: {subject}")
        return {"id": "mock-id"}
        
    params = {
        "from": f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>",
        "to": [email_to],
        "subject": subject,
        "html": html_content,
    }
    
    return resend.Emails.send(params)


def send_reset_password_email(email_to: str, token: str) -> dict:
    """
    Send password reset email
    
    Args:
        email_to: Recipient email
        token: Reset token
        
    Returns:
        Resend API response
    """
    # In a real app, this would be a frontend URL
    # For MVP/Local dev, we'll point to localhost
    reset_link = f"http://localhost:3000/auth/reset-password?token={token}"
    
    subject = "Reset your password - CodeRenew"
    
    html_content = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>Reset Your Password</h2>
        <p>You have requested to reset your password for your CodeRenew account.</p>
        <p>Please click the button below to set a new password. This link is valid for 1 hour.</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_link}" style="background-color: #2563EB; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold;">Reset Password</a>
        </div>
        <p>If you didn't request this, you can safely ignore this email.</p>
        <p>Or copy and paste this link into your browser:</p>
        <p><a href="{reset_link}">{reset_link}</a></p>
    </div>
    """
    
    return send_email(email_to, subject, html_content)


def send_account_locked_email(email_to: str, lockout_minutes: int) -> dict:
    """
    Send account lockout notification email

    Args:
        email_to: Recipient email
        lockout_minutes: Number of minutes account is locked for

    Returns:
        Resend API response
    """
    subject = "Security Alert: Your account has been locked - CodeRenew"

    html_content = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #DC2626;">Security Alert: Account Locked</h2>
        <p>Your CodeRenew account has been temporarily locked due to multiple failed login attempts.</p>

        <div style="background-color: #FEE2E2; border-left: 4px solid #DC2626; padding: 16px; margin: 20px 0;">
            <p style="margin: 0;"><strong>Lockout Duration:</strong> {lockout_minutes} minutes</p>
        </div>

        <h3>What happened?</h3>
        <p>We detected {5} consecutive failed login attempts on your account. To protect your security, we've temporarily locked your account.</p>

        <h3>What should you do?</h3>
        <ul>
            <li>Wait {lockout_minutes} minutes and try logging in again</li>
            <li>Make sure you're using the correct password</li>
            <li>If you forgot your password, use the "Forgot Password" link on the login page</li>
            <li>If you didn't attempt to log in, your account credentials may be compromised - please reset your password immediately</li>
        </ul>

        <div style="text-align: center; margin: 30px 0;">
            <a href="http://localhost:3000/auth/forgot-password" style="background-color: #2563EB; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold;">Reset Password</a>
        </div>

        <p style="color: #6B7280; font-size: 14px; margin-top: 30px;">
            If you have concerns about your account security, please contact our support team.
        </p>
    </div>
    """

    return send_email(email_to, subject, html_content)


def send_scan_complete_email(email_to: str, scan_id: int, risk_level: str, issue_count: int) -> dict:
    """
    Send email when a scan is completed
    
    Args:
        email_to: Recipient email
        scan_id: Scan ID
        risk_level: Risk level of the scan
        issue_count: Number of issues found
        
    Returns:
        Resend API response
    """
    # In a real app, this would be a frontend URL
    scan_url = f"http://localhost:3000/scans/{scan_id}"
    
    subject = f"Scan Complete: {issue_count} issues found - CodeRenew"
    
    color = "#2563EB" # Blue
    if risk_level == "critical":
        color = "#DC2626" # Red
    elif risk_level == "high":
        color = "#EA580C" # Orange
        
    html_content = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>Scan Complete</h2>
        <p>Your WordPress compatibility scan has finished processing.</p>
        
        <div style="background-color: #F3F4F6; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0 0 10px 0;"><strong>Risk Level:</strong> <span style="color: {color}; font-weight: bold;">{risk_level.upper()}</span></p>
            <p style="margin: 0;"><strong>Issues Found:</strong> {issue_count}</p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{scan_url}" style="background-color: #2563EB; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold;">View Results</a>
        </div>
        
        <p>You can also download a PDF report from the results page.</p>
    </div>
    """
    
    return send_email(email_to, subject, html_content)
