"""
Unit tests for Validation Tools
"""
import pytest
from app.services.claude.validation_tools import get_compatibility_analysis_tool


def test_get_compatibility_analysis_tool():
    """Test tool definition structure"""
    tool = get_compatibility_analysis_tool()
    
    assert tool['name'] == 'report_compatibility_issues'
    assert 'input_schema' in tool
    
    schema = tool['input_schema']
    assert schema['type'] == 'object'
    assert 'risk_level' in schema['properties']
    assert 'issues' in schema['properties']
    
    # Check enums
    risk_enum = schema['properties']['risk_level']['enum']
    assert 'critical' in risk_enum
    assert 'safe' in risk_enum
    
    issue_schema = schema['properties']['issues']['items']
    severity_enum = issue_schema['properties']['severity']['enum']
    assert 'critical' in severity_enum
    assert 'info' in severity_enum


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
