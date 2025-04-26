# PawPass API Documentation

## Overview

PawPass provides a comprehensive RESTful API that allows developers to interact with all aspects of the application programmatically. This document outlines the available endpoints, expected parameters, and response formats.

## Base URL

All API URLs referenced in this documentation have the following base:

```
https://[your-pawpass-instance]/api
```

## Authentication

API authentication will be implemented in future versions. Currently, the API endpoints are accessible without authentication, intended for internal application use.

Future authentication will use:
- OAuth 2.0 authentication flow
- JWT tokens for API authorization

## Response Format

All API responses are returned in JSON format with the following structure:

```json
{
  "success": true,
  "data": { ... } // Contains the actual response data
}
```

For error responses:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message"
  }
}
```

## Pet Endpoints

### Get All Pets

Retrieves a list of all pets in the system.

```
GET /pets
```

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| search | string | (Optional) Filter pets by name |
| species | string | (Optional) Filter pets by species |
| emergency | boolean | (Optional) Filter to show only emergency pets |

#### Response

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Buddy",
      "species": "Dog",
      "breed": "Golden Retriever",
      "age": 3,
      "gender": "Male",
      "description": "Friendly and energetic",
      "image_url": "/static/uploads/buddy.jpg",
      "is_emergency": false,
      "created_at": "2025-04-15T10:30:45Z",
      "updated_at": "2025-04-15T10:30:45Z"
    },
    ...
  ]
}
```

### Get Pet by ID

Retrieves detailed information about a specific pet.

```
GET /pets/{pet_id}
```

#### URL Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| pet_id | integer | The unique identifier of the pet |

#### Response

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Buddy",
    "species": "Dog",
    "breed": "Golden Retriever",
    "age": 3,
    "gender": "Male",
    "description": "Friendly and energetic",
    "image_url": "/static/uploads/buddy.jpg",
    "is_emergency": false,
    "created_at": "2025-04-15T10:30:45Z",
    "updated_at": "2025-04-15T10:30:45Z",
    "updates": [
      {
        "id": 1,
        "date": "2025-04-16",
        "time": "14:30",
        "note": "Went for a walk, very energetic today",
        "volunteer": "Jane Smith"
      }
    ],
    "checklists": [
      {
        "id": 1,
        "date": "2025-04-16",
        "time": "08:00",
        "notes": "Morning routine completed",
        "volunteer": "John Doe",
        "completed_items": [
          {
            "id": 1,
            "description": "Fed the pet"
          },
          {
            "id": 3,
            "description": "Refreshed water"
          }
        ]
      }
    ]
  }
}
```

### Add Pet Update

Adds a new update to a pet's record.

```
POST /pets/{pet_id}/update
```

#### URL Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| pet_id | integer | The unique identifier of the pet |

#### Request Body

```json
{
  "update": "Buddy had a great walk today and played with other dogs.",
  "volunteer_name": "Jane Smith"
}
```

#### Response

```json
{
  "success": true,
  "update": {
    "id": 2,
    "date": "2025-04-17",
    "time": "16:45",
    "note": "Buddy had a great walk today and played with other dogs.",
    "volunteer": "Jane Smith"
  }
}
```

### Complete Checklist

Records a completed checklist for a pet.

```
POST /pets/{pet_id}/checklist
```

#### URL Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| pet_id | integer | The unique identifier of the pet |

#### Request Body

```json
{
  "notes": "Evening routine completed without issues",
  "volunteer_name": "John Doe",
  "completed_items": [1, 2, 3, 5]
}
```

#### Response

```json
{
  "success": true,
  "checklist": {
    "id": 2,
    "date": "2025-04-17",
    "time": "19:30",
    "notes": "Evening routine completed without issues",
    "volunteer": "John Doe",
    "completed_items": [
      {
        "id": 1,
        "description": "Fed the pet"
      },
      {
        "id": 2,
        "description": "Gave medication"
      },
      {
        "id": 3,
        "description": "Refreshed water"
      },
      {
        "id": 5,
        "description": "Cleaned litter box/living area"
      }
    ]
  }
}
```

## Future API Endpoints

The following endpoints are planned for future implementation:

### Authentication

- `POST /auth/login`: Authenticate user
- `POST /auth/register`: Register new user
- `POST /auth/logout`: End user session
- `GET /auth/profile`: Get user profile information

### User Management

- `GET /users`: List all users (admin only)
- `GET /users/{id}`: Get user details
- `PUT /users/{id}`: Update user information
- `DELETE /users/{id}`: Remove a user (admin only)

### Notifications

- `GET /notifications`: Get user notifications
- `PUT /notifications/{id}/read`: Mark notification as read
- `POST /notifications/settings`: Update notification preferences

## Response Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | OK - The request was successful |
| 201 | Created - A new resource was successfully created |
| 400 | Bad Request - The request was invalid or cannot be served |
| 401 | Unauthorized - Authentication is required |
| 403 | Forbidden - The server understood the request but refuses to authorize it |
| 404 | Not Found - The requested resource could not be found |
| 500 | Internal Server Error - The server encountered an unexpected condition |

## Rate Limiting

Currently, there are no rate limits imposed on the API. However, as usage grows, rate limiting may be implemented to ensure system stability.

## Versioning

The API currently does not use explicit versioning. Future changes that may break compatibility will be announced in advance, and a versioning scheme will be implemented.

## Support

For API support, please contact the PawPass development team.