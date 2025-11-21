"""
Unit tests for WordPress deprecation database
"""
import pytest
from app.services.wordpress.deprecation_db import WordPressDeprecationDB, ChangeType


def test_check_function():
    """Test checking if a function is deprecated"""
    db = WordPressDeprecationDB()
    
    # Test deprecated function
    result = db.check_function('get_page')
    assert result is not None
    assert result.name == 'get_page'
    assert result.deprecated_in == '3.9'
    assert result.removed_in == '6.1'
    assert result.replacement == 'get_post'
    
    # Test non-deprecated function
    result = db.check_function('get_post')
    assert result is None


def test_get_deprecated_in_range():
    """Test getting deprecated items in version range"""
    db = WordPressDeprecationDB()
    
    # Test range that includes get_page removal
    items = db.get_deprecated_in_range('5.9', '6.4')
    
    # Should include items deprecated or removed in this range
    assert len(items) > 0
    
    # Check that get_page is included (removed in 6.1)
    get_page_items = [i for i in items if i.name == 'get_page']
    assert len(get_page_items) > 0


def test_get_critical_changes():
    """Test getting critical changes"""
    db = WordPressDeprecationDB()
    
    critical = db.get_critical_changes('5.9', '6.4')
    
    # Should include removed functions and critical severity items
    assert len(critical) > 0
    
    # All should be critical or removed
    for item in critical:
        assert item.severity == 'critical' or item.change_type == ChangeType.REMOVED_FUNCTION


def test_version_summary():
    """Test getting version summary"""
    db = WordPressDeprecationDB()
    
    summary = db.get_version_summary('5.9', '6.4')
    
    assert 'total' in summary
    assert 'critical' in summary
    assert 'removed_functions' in summary
    assert summary['total'] >= 0


def test_get_replacement_suggestion():
    """Test getting replacement suggestions"""
    db = WordPressDeprecationDB()
    
    replacement = db.get_replacement_suggestion('get_page')
    assert replacement == 'get_post'
    
    replacement = db.get_replacement_suggestion('nonexistent_function')
    assert replacement is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
