"""
Unit tests for WordPress static analyzer
"""
import pytest
from pathlib import Path
from app.services.wordpress.analyzer import WordPressAnalyzer


@pytest.fixture
def analyzer():
    """Create analyzer instance"""
    return WordPressAnalyzer()


@pytest.fixture
def sample_code():
    """Sample PHP code with issues"""
    return """
<?php
// Deprecated function
$page = get_page(123);

// Security issue - SQL injection
$wpdb->query("SELECT * FROM wp_posts WHERE ID = " . $_GET['id']);

// XSS vulnerability
echo $_POST['user_input'];

// jQuery deprecated method
jQuery('.element').bind('click', function() {});
?>
"""


def test_extract_functions(analyzer, sample_code):
    """Test function extraction"""
    functions = analyzer.extract_functions(sample_code)
    
    assert 'get_page' in functions
    assert 'query' in functions  # $wpdb->query
    assert 'echo' not in functions  # Should be filtered out


def test_find_deprecated_functions(analyzer, sample_code):
    """Test finding deprecated functions"""
    deprecated = analyzer.find_deprecated_functions(sample_code)
    
    # Should find get_page
    get_page_issues = [d for d in deprecated if d['function'] == 'get_page']
    assert len(get_page_issues) > 0
    
    # Check issue details
    issue = get_page_issues[0]
    assert issue['deprecated_in'] == '3.9'
    assert issue['replacement'] == 'get_post'
    assert issue['line'] > 0


def test_detect_security_issues(analyzer, sample_code):
    """Test security issue detection"""
    issues = analyzer.detect_security_issues(sample_code)
    
    # Should find SQL injection
    sql_issues = [i for i in issues if i['type'] == 'sql_injection']
    assert len(sql_issues) > 0
    
    # Should find XSS
    xss_issues = [i for i in issues if i['type'] == 'xss']
    assert len(xss_issues) > 0


def test_detect_patterns(analyzer):
    """Test pattern detection"""
    code_with_patterns = """
<?php
// Direct mysqli usage
$mysqli = new mysqli('localhost', 'user', 'pass', 'db');

// jQuery deprecated method
jQuery('.element').bind('click', function() {});
?>
"""
    
    patterns = analyzer.detect_patterns(code_with_patterns)
    
    # Should detect direct mysqli usage
    mysqli_patterns = [p for p in patterns if 'mysqli' in p['description'].lower()]
    assert len(mysqli_patterns) > 0


def test_quick_scan(analyzer, sample_code):
    """Test quick scan functionality"""
    result = analyzer.quick_scan(sample_code, '5.9', '6.4')
    
    assert 'risk_level' in result
    assert 'deprecated_functions_found' in result
    assert 'security_issues_found' in result
    
    # Should find issues
    assert result['deprecated_functions_found'] > 0
    assert result['security_issues_found'] > 0
    
    # Risk level should not be safe
    assert result['risk_level'] in ['warning', 'critical']


def test_get_file_priority(analyzer):
    """Test file priority calculation"""
    # High priority files
    assert analyzer.get_file_priority(Path('functions.php')) == 100
    assert analyzer.get_file_priority(Path('index.php')) == 100
    
    # Medium priority
    assert analyzer.get_file_priority(Path('header.php')) == 50
    
    # Low priority
    assert analyzer.get_file_priority(Path('inc/helper.php')) == 10
    
    # Default priority
    assert analyzer.get_file_priority(Path('custom.php')) == 25


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
