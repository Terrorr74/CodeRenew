import sys
import os
from datetime import datetime
from unittest.mock import MagicMock

# Add backend to path
sys.path.append(os.getcwd())

try:
    from app.services.reporting.pdf_generator import PDFReportGenerator
    from app.models.scan import Scan, RiskLevel
    from app.models.scan_result import ScanResult
    from app.models.site import Site

    print("✅ Imports successful")

    # Mock data
    mock_site = MagicMock(spec=Site)
    mock_site.url = "https://example.com"

    mock_scan = MagicMock(spec=Scan)
    mock_scan.id = 123
    mock_scan.site = mock_site
    mock_scan.created_at = datetime.now()
    mock_scan.wordpress_version_from = "5.0"
    mock_scan.wordpress_version_to = "6.0"
    mock_scan.risk_level = RiskLevel.HIGH
    
    # Mock results
    r1 = MagicMock(spec=ScanResult)
    r1.severity = "critical"
    r1.issue_type = "security_vulnerability"
    r1.file_path = "/wp-content/plugins/unsafe.php"
    r1.description = "SQL Injection vulnerability found"
    
    r2 = MagicMock(spec=ScanResult)
    r2.severity = "medium"
    r2.issue_type = "deprecated_function"
    r2.file_path = "/wp-content/themes/old/functions.php"
    r2.description = "create_function() is deprecated"

    mock_scan.results = [r1, r2]

    # Generate PDF
    generator = PDFReportGenerator(mock_scan)
    pdf_content = generator.generate()

    if len(pdf_content) > 0 and pdf_content.startswith(b'%PDF'):
        print(f"✅ PDF generated successfully ({len(pdf_content)} bytes)")
        # Save for manual inspection if needed
        with open("test_report.pdf", "wb") as f:
            f.write(pdf_content)
        print("✅ Saved to test_report.pdf")
    else:
        print("❌ PDF generation failed or invalid output")
        sys.exit(1)

except Exception as e:
    print(f"\n❌ Verification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
