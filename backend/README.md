# Shopify AI Image Processing Backend

This is the backend service for the Shopify AI Image Processing application. It provides APIs for image processing, Shopify integration, and task management.

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Supabase**: PostgreSQL database with real-time capabilities
- **Redis**: In-memory data store for caching and task queue
- **Celery**: Distributed task queue for background processing
- **Docker**: Containerization for consistent development and deployment

## Project Structure

```
backend/
├── app/
│   ├── api/              # API routes and dependencies
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py
│   │   │   │   ├── stores.py
│   │   │   │   ├── images.py
│   │   │   │   └── tasks.py
│   │   │   └── router.py
│   │   └── deps.py
│   ├── core/            # Core functionality
│   │   ├── config.py
│   │   ├── celery.py
│   │   ├── database.py
│   │   ├── redis.py
│   │   └── exceptions.py
│   ├── models/          # Pydantic models
│   │   ├── store.py
│   │   ├── image.py
│   │   └── task.py
│   ├── repositories/    # Database operations
│   │   ├── base.py
│   │   ├── store.py
│   │   ├── image.py
│   │   └── task.py
│   ├── services/       # Business logic
│   │   ├── base.py
│   │   ├── store.py
│   │   ├── image.py
│   │   └── task.py
│   └── db/            # Database migrations
│       └── schema.sql
├── scripts/          # Utility scripts
│   └── start.sh
├── tests/           # Test suite
│   ├── conftest.py
│   └── api/
│       └── test_auth.py
├── Dockerfile
├── requirements.txt
└── .env.example
```

## Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in the required values
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Development

Start the development server:

```bash
./scripts/start.sh api
```

Start Celery worker:

```bash
./scripts/start.sh worker
```

Start Celery beat:

```bash
./scripts/start.sh beat
```

Start Flower monitoring:

```bash
./scripts/start.sh flower
```

## Docker

Build and run with Docker Compose:

```bash
docker-compose up -d
```

## Testing

Run tests:

```bash
pytest
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Monitoring

- Flower dashboard: http://localhost:5555

## License

MIT 