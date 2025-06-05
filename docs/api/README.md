# API Documentation

## Overview
This document describes the API endpoints for the Shopify AI Image Processing application.

## Authentication
All API requests require authentication using a Shopify session token.

## Base URL
```
http://localhost:8000/api/v1
```

## Endpoints

### Image Processing

#### GET /images
List processed images with pagination.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)

**Response:**
```json
{
  "data": [
    {
      "id": "string",
      "originalUrl": "string",
      "processedUrl": "string",
      "status": "completed",
      "createdAt": "string"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100
  }
}
```

#### POST /images/process
Process a new image.

**Request Body:**
```json
{
  "imageId": "string",
  "settings": {
    "quality": number,
    "format": "string",
    "backgroundRemoval": boolean
  }
}
```

### Queue Management

#### GET /queue
Get current processing queue status.

### Statistics

#### GET /stats
Get processing statistics.

## Error Handling
The API uses standard HTTP status codes and returns error details in the response body:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}
```

## Rate Limiting
- 100 requests per hour for image processing
- 1000 requests per hour for general API calls 