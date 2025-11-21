"""
Test token estimation functionality
"""
import pytest
from pathlib import Path
from app.services.wordpress.scanner import WordPressScanner


def test_estimate_tokens_for_file(tmp_path):
    """Test token estimation for a single file"""
    scanner = WordPressScanner(version_from="5.9", version_to="6.4")
    
    # Create a test file
    test_file = tmp_path / "test.php"
    test_content = "<?php\n" + ("// Test line\n" * 100)  # ~1300 characters
    test_file.write_text(test_content)
    
    tokens = scanner._estimate_tokens_for_file(test_file)
    
    # Should estimate accurate tokens (around 300-450 for this content)
    # Previous estimate had +500 overhead, new one is accurate
    assert tokens > 100
    assert tokens < 500


def test_estimate_total_tokens(tmp_path):
    """Test total token estimation for a project"""
    scanner = WordPressScanner(version_from="5.9", version_to="6.4")
    
    # Create multiple test files
    files = []
    for i in range(5):
        test_file = tmp_path / f"file{i}.php"
        test_content = "<?php\n" + (f"// Test line {i}\n" * 50)
        test_file.write_text(test_content)
        files.append(test_file)
    
    estimate = scanner.estimate_total_tokens(files)
    
    # Verify structure
    assert 'total_files' in estimate
    assert 'total_tokens' in estimate
    assert 'estimated_batches' in estimate
    assert 'estimated_cost_usd' in estimate
    assert 'context_overflow_risk' in estimate
    
    # Verify values
    assert estimate['total_files'] == 5
    assert estimate['total_tokens'] > 0
    assert estimate['estimated_batches'] >= 1
    assert estimate['context_overflow_risk'] in ['low', 'medium', 'high']


def test_context_overflow_detection(tmp_path):
    """Test detection of context overflow risk"""
    scanner = WordPressScanner(version_from="5.9", version_to="6.4")
    
    # Create a very large file that would overflow context
    # Need to exceed 3 * MAX_TOKENS_PER_BATCH for 'medium' risk
    # MAX_TOKENS_PER_BATCH = 150000, so need > 450000 tokens
    # At 4 chars per token, need > 1.8M characters
    large_file = tmp_path / "large.php"
    large_content = "<?php\n" + ("// Test line with some content here\n" * 60000)  # ~2.1M characters
    large_file.write_text(large_content)
    
    estimate = scanner.estimate_total_tokens([large_file])
    
    # Should detect medium or high overflow risk
    assert estimate['context_overflow_risk'] in ['medium', 'high']
    assert estimate['estimated_batches'] > 1


def test_batching_respects_token_limits(tmp_path):
    """Test that batching respects token limits"""
    scanner = WordPressScanner(version_from="5.9", version_to="6.4")
    
    # Create files of varying sizes
    files = []
    for i in range(10):
        test_file = tmp_path / f"file{i}.php"
        # Create files with increasing sizes
        test_content = "<?php\n" + (f"// Test line {i}\n" * (100 * (i + 1)))
        test_file.write_text(test_content)
        files.append(test_file)
    
    batches = scanner._batch_files(files)
    
    # Verify each batch respects limits
    for batch in batches:
        batch_tokens = sum(scanner._estimate_tokens_for_file(f) for f in batch)
        assert batch_tokens <= scanner.MAX_TOKENS_PER_BATCH
        assert len(batch) <= 20  # Max files per batch


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
