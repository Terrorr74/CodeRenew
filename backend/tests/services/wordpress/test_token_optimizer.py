"""
Unit tests for Token Optimizer
"""
import pytest
from pathlib import Path
from app.services.wordpress.token_optimizer import TokenOptimizer


@pytest.fixture
def optimizer():
    """Create optimizer instance"""
    return TokenOptimizer()


def test_should_skip_file(optimizer):
    """Test file skipping logic"""
    # Should skip
    assert optimizer.should_skip_file(Path('vendor/autoload.php')) is True
    assert optimizer.should_skip_file(Path('node_modules/jquery/dist/jquery.js')) is True
    assert optimizer.should_skip_file(Path('assets/js/script.min.js')) is True
    assert optimizer.should_skip_file(Path('wp-admin/includes/file.php')) is True
    
    # Should not skip
    assert optimizer.should_skip_file(Path('functions.php')) is False
    assert optimizer.should_skip_file(Path('header.php')) is False
    assert optimizer.should_skip_file(Path('inc/custom-functions.php')) is False


def test_count_tokens(optimizer):
    """Test token counting"""
    text = "function test() { return true; }"
    count = optimizer.count_tokens(text)
    assert count > 0
    # Simple text should have few tokens
    assert count < 20


def test_remove_comments(optimizer):
    """Test comment removal"""
    code = """
    <?php
    // This is a comment
    /* This is a 
       multi-line comment */
    
    /**
     * @deprecated 1.0.0 Use new_function() instead
     */
    function old_function() {}
    
    # Another comment
    $x = 1; // Inline comment
    ?>
    """
    
    cleaned = optimizer._remove_comments(code, keep_deprecated=True)
    
    # Should remove standard comments
    assert "This is a comment" not in cleaned
    assert "multi-line comment" not in cleaned
    assert "Another comment" not in cleaned
    assert "Inline comment" not in cleaned
    
    # Should keep deprecated tag
    assert "@deprecated" in cleaned
    assert "old_function" in cleaned


def test_collapse_whitespace(optimizer):
    """Test whitespace collapsing"""
    code = """
    function test() {
        
        
        $x =    1;
        return $x;
    }
    """
    
    collapsed = optimizer._collapse_whitespace(code)
    
    # Should reduce multiple newlines
    assert "\n\n\n" not in collapsed
    # Should reduce multiple spaces
    assert "$x = 1;" in collapsed or "$x = 1;" in collapsed.replace("    ", " ")


def test_optimize_code(optimizer):
    """Test full optimization"""
    code = """
    <?php
    /**
     * Main function
     * @author Me
     */
    function main() {
        // Initialize
        $x = 1;
        
        /* 
         * Complex logic here
         */
        if ($x > 0) {
            return true;
        }
        
        return false;
    }
    ?>
    """
    
    result = optimizer.optimize_code(code)
    
    assert 'optimized_code' in result
    assert 'original_tokens' in result
    assert 'optimized_tokens' in result
    assert 'tokens_saved' in result
    
    # Should save tokens
    assert result['tokens_saved'] > 0
    assert result['optimized_tokens'] < result['original_tokens']
    
    # Optimized code should still contain logic
    assert "function main" in result['optimized_code']
    assert "$x = 1" in result['optimized_code']


def test_extract_critical_sections(optimizer):
    """Test critical section extraction"""
    code = """
    <?php
    // Header
    
    function normal_function() {
        // Lots of logic
        $a = 1;
        $b = 2;
        return $a + $b;
    }
    
    add_action('init', 'my_init');
    
    $wpdb->query("SELECT * FROM table");
    
    $user_id = $_GET['id'];
    ?>
    """
    
    patterns = optimizer.extract_file_patterns(code)
    extracted = optimizer._extract_critical_sections(code, patterns)
    
    # Should keep function signature
    assert "function normal_function" in extracted
    # Should keep hooks
    assert "add_action" in extracted
    # Should keep db queries
    assert "$wpdb->query" in extracted
    # Should keep user input
    assert "$_GET" in extracted


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
