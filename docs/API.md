# CodeRenew API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

## Endpoints

### Authentication

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}

Response: 201 Created
{
  "id": 1,
  "email": "user@example.com",
  "is_verified": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "email": "user@example.com",
  "is_verified": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Sites

#### List Sites
```http
GET /sites?skip=0&limit=100
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": 1,
    "user_id": 1,
    "name": "My WordPress Site",
    "url": "https://example.com",
    "description": "Production site",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Get Site
```http
GET /sites/{site_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "user_id": 1,
  "name": "My WordPress Site",
  "url": "https://example.com",
  "description": "Production site",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Create Site
```http
POST /sites
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "My WordPress Site",
  "url": "https://example.com",
  "description": "Production site"
}

Response: 201 Created
{
  "id": 1,
  "user_id": 1,
  "name": "My WordPress Site",
  "url": "https://example.com",
  "description": "Production site",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Update Site
```http
PUT /sites/{site_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Site Name",
  "description": "Updated description"
}

Response: 200 OK
{
  "id": 1,
  "user_id": 1,
  "name": "Updated Site Name",
  "url": "https://example.com",
  "description": "Updated description",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-02T00:00:00Z"
}
```

#### Delete Site
```http
DELETE /sites/{site_id}
Authorization: Bearer <token>

Response: 204 No Content
```

### Scans

#### List Scans
```http
GET /scans?skip=0&limit=100
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": 1,
    "site_id": 1,
    "user_id": 1,
    "wordpress_version_from": "6.3",
    "wordpress_version_to": "6.4",
    "status": "completed",
    "risk_level": "medium",
    "created_at": "2024-01-01T00:00:00Z",
    "completed_at": "2024-01-01T00:05:00Z",
    "results": []
  }
]
```

#### Get Scan
```http
GET /scans/{scan_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "site_id": 1,
  "user_id": 1,
  "wordpress_version_from": "6.3",
  "wordpress_version_to": "6.4",
  "status": "completed",
  "risk_level": "medium",
  "created_at": "2024-01-01T00:00:00Z",
  "completed_at": "2024-01-01T00:05:00Z",
  "results": [
    {
      "id": 1,
      "scan_id": 1,
      "issue_type": "deprecated_function",
      "severity": "medium",
      "file_path": "wp-content/themes/mytheme/functions.php",
      "line_number": 42,
      "description": "Function 'create_function' is deprecated",
      "recommendation": "Replace with anonymous function or arrow function",
      "code_snippet": "create_function('$a', 'return $a * 2;')"
    }
  ]
}
```

#### Create Scan
```http
POST /scans
Authorization: Bearer <token>
Content-Type: application/json

{
  "site_id": 1,
  "wordpress_version_from": "6.3",
  "wordpress_version_to": "6.4"
}

Response: 201 Created
{
  "id": 1,
  "site_id": 1,
  "user_id": 1,
  "wordpress_version_from": "6.3",
  "wordpress_version_to": "6.4",
  "status": "pending",
  "risk_level": null,
  "created_at": "2024-01-01T00:00:00Z",
  "completed_at": null,
  "results": []
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Invalid email address",
      "type": "value_error"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

Currently no rate limiting in MVP. Will be added in future versions.

## Pagination

List endpoints support pagination via query parameters:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100, max: 100)

## Interactive Documentation

Visit http://localhost:8000/docs for Swagger UI interactive documentation.
Visit http://localhost:8000/redoc for ReDoc documentation.
