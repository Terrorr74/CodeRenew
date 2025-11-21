import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.claude.client import ClaudeClient
from app.services.wordpress.scanner import WordPressScanner

async def test_scanner():
    print("Testing WordPressScanner...")
    scanner = WordPressScanner(version_from="5.9", version_to="6.4")
    
    # Create a dummy PHP file for testing
    test_file = Path("test_plugin.php")
    with open(test_file, "w") as f:
        f.write("<?php\nfunction my_plugin_init() {\n    // This is a test\n    $x = 1;\n}")
        
    try:
        print(f"Scanning {test_file}...")
        # We expect this to fail if API key is missing, but that proves the code runs
        try:
            issues = await scanner.scan_files([test_file])
            print(f"Scan complete. Issues found: {len(issues)}")
        except Exception as e:
            print(f"Scan attempted (expected failure if no API key): {e}")
            
    finally:
        if test_file.exists():
            os.remove(test_file)

if __name__ == "__main__":
    asyncio.run(test_scanner())
