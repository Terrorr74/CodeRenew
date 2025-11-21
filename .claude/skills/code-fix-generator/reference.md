# WordPress Deprecation Reference

## PHP 8.x Compatibility Issues

| Deprecated | Replacement | PHP Version |
|------------|-------------|-------------|
| `create_function()` | Anonymous functions | 7.2+ |
| `each()` | `foreach` loop | 7.2+ |
| `__autoload()` | `spl_autoload_register()` | 7.2+ |
| `$php_errormsg` | `error_get_last()` | 7.2+ |
| `assert()` with string | `assert()` with expression | 7.2+ |

## WordPress Function Deprecations

### WP 6.x Deprecations
| Deprecated | Replacement | Version |
|------------|-------------|---------|
| `_register_controls()` | `register_controls()` | 6.0 |
| `block_core_navigation_get_classic_menu_fallback()` | `WP_Navigation_Fallback` | 6.3 |

### WP 5.x Deprecations
| Deprecated | Replacement | Version |
|------------|-------------|---------|
| `wp_make_link_relative()` | Custom implementation | 5.9 |
| `_wp_register_meta_args_whitelist` | `_wp_register_meta_args_allowlist` | 5.5 |
| `whitelist_options` | `allowed_options` | 5.5 |

### Classic Deprecations
| Deprecated | Replacement | Version |
|------------|-------------|---------|
| `get_currentuserinfo()` | `wp_get_current_user()` | 4.5 |
| `get_userdatabylogin()` | `get_user_by('login', $login)` | 3.3 |
| `get_usermeta()` | `get_user_meta()` | 3.0 |
| `update_usermeta()` | `update_user_meta()` | 3.0 |
| `get_the_author_email()` | `get_the_author_meta('email')` | 2.8 |
| `get_the_author_ID()` | `get_the_author_meta('ID')` | 2.8 |
| `the_content_rss()` | `the_content_feed()` | 2.9 |
| `wp_specialchars()` | `esc_html()` | 2.8 |
| `sanitize_url()` | `esc_url()` | 2.8 |
| `clean_url()` | `esc_url()` | 3.0 |
| `attribute_escape()` | `esc_attr()` | 2.8 |

## Database Patterns

```php
// Always use prepared statements
$wpdb->prepare(
    "SELECT * FROM {$wpdb->posts} WHERE ID = %d AND post_status = %s",
    $post_id,
    'publish'
);

// Placeholders
// %d - integer
// %f - float
// %s - string
// %i - identifier (table/column name, WP 6.2+)
```

## Hook Migration Patterns

```php
// Old: Passing by reference deprecated
add_filter( 'filter', 'callback', 10, 1 );
function callback( &$value ) {} // WRONG

// New: Return modified value
add_filter( 'filter', 'callback', 10, 1 );
function callback( $value ) {
    return $modified_value;
}
```
