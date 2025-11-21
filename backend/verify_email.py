import sys
import os
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.append(os.getcwd())

try:
    # Mock send_email to verify arguments
    with patch('app.services.email.send_email') as mock_send:
        mock_send.return_value = {"id": "test_email_id"}
        
        from app.services.email import send_scan_complete_email
        
        print("✅ Imports successful")
        
        # Test sending email
        response = send_scan_complete_email(
            email_to="test@example.com",
            scan_id=123,
            risk_level="critical",
            issue_count=42
        )
        
        # Verify call
        if mock_send.called:
            args, kwargs = mock_send.call_args
            email_to, subject, html_content = args
            
            print(f"✅ Email sent to: {email_to}")
            print(f"✅ Subject: {subject}")
            
            if "Critical" in html_content or "CRITICAL" in html_content:
                print("✅ Risk level correctly included in HTML")
            else:
                print("❌ Risk level missing from HTML")
                
            if "42" in html_content:
                print("✅ Issue count correctly included in HTML")
            else:
                print("❌ Issue count missing from HTML")
                
        else:
            print("❌ send_email was not called")
            sys.exit(1)

except Exception as e:
    print(f"\n❌ Verification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
