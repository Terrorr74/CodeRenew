"""
Test WordPress theme with known compatibility issues
This file contains deprecated functions for testing the scanner
"""

# Deprecated function from WordPress 3.9 (removed in 6.1)
$page = get_page(123);

# Deprecated function
$page_by_path = get_page_by_path('/sample-page');

# Security issue - SQL injection vulnerability
$wpdb->query("SELECT * FROM wp_posts WHERE ID = " . $_GET['id']);

# Security issue - XSS vulnerability  
echo $_POST['user_input'];

# Deprecated jQuery method
jQuery(document).ready(function($) {
    $('.element').bind('click', function() {
        // This uses deprecated .bind()
    });
    
    $('.other').load('content.html');  // Deprecated .load()
});

# Missing nonce verification
add_action('admin_post_save_settings', 'handle_save_settings');
function handle_save_settings() {
    // No wp_verify_nonce() call - security issue
    update_option('my_setting', $_POST['value']);
}

# Missing sanitization
$user_input = $_GET['search'];  // No sanitization
echo $user_input;  // No escaping

# Direct database access (should use $wpdb)
$mysqli = new mysqli('localhost', 'user', 'pass', 'database');
$result = $mysqli->query("SELECT * FROM custom_table");
