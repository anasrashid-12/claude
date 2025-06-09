# Shopify AI Image Processing App

A powerful Shopify app that provides AI-powered image processing capabilities for e-commerce stores.

## Features

- Seamless Shopify integration
- AI-powered image processing
- Batch processing support
- Version control for images
- Real-time processing status
- Secure authentication and authorization

## Tech Stack

- **Frontend**: NextJS
- **Backend**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)
- **Task Queue**: Celery with Redis
- **Storage**: Supabase Storage / S3
- **AI Processing**: Custom AI Service

## Prerequisites

- Python 3.9+
- Node.js 18+
- Redis
- Shopify Partner Account
- Supabase Account

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/shopify-ai-image-app.git
cd shopify-ai-image-app
```

2. Set up backend environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a `.env` file in the backend directory:
```env
# Base Configuration
DEBUG=True
PROJECT_NAME="Shopify AI Image App"
VERSION="1.0.0"

# Shopify Configuration
SHOPIFY_API_KEY=your_api_key
SHOPIFY_API_SECRET=your_api_secret
SHOPIFY_APP_URL=https://your-app-url.com
SHOPIFY_SCOPES="write_products,write_files,read_files"

# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_JWT_SECRET=your_jwt_secret

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Security
JWT_SECRET_KEY=your_jwt_secret
JWT_ALGORITHM=HS256

# Storage Configuration
STORAGE_PROVIDER=supabase  # or 's3'
```

4. Start the backend server:
```bash
uvicorn app.main:app --reload
```

5. Start Redis server (required for Celery):
```bash
redis-server
```

6. Start Celery worker:
```bash
celery -A app.worker worker --loglevel=info
```

## Development

### Backend API Documentation

Once the backend server is running, you can access:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Database Migrations

The project uses Supabase migrations. To apply migrations:

1. Install Supabase CLI
2. Run:
```bash
supabase db reset
```

## Deployment

1. Set up your production environment variables
2. Deploy the backend to your chosen platform
3. Configure Shopify app settings in your Partner Dashboard
4. Update the OAuth redirect URLs

## Security

- All API endpoints are protected with JWT authentication
- Shopify webhooks are verified using HMAC validation
- Sensitive data is encrypted at rest
- Rate limiting is implemented on all endpoints

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
