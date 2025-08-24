# 🧠 MaxFlow AI Image App - Backend

A production-ready FastAPI backend for the MaxFlow AI Image App. This backend handles image processing, credit management, Shopify integration, and provides a robust API for the frontend.

## 🚀 Features

- **FastAPI** - High-performance async web framework
- **Celery + Redis** - Background task processing for image operations
- **Supabase** - Database and file storage
- **Shopify Integration** - OAuth, webhooks, and billing
- **Rate Limiting** - Production-grade rate limiting with Redis
- **Security** - JWT authentication, CORS, CSP headers
- **Monitoring** - Sentry integration and Prometheus metrics
- **Docker** - Containerized deployment

## 📋 Prerequisites

- Python 3.11+
- Redis instance
- Supabase project
- Shopify Partner account
- MakeIt3D API key

## 🛠️ Local Development

### 1. Clone and Setup

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the backend directory:

```env
# Core Configuration
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# Database & Storage
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_BUCKET=makeit3d-public

# Redis (for Celery and Rate Limiting)
REDIS_URL=redis://localhost:6379

# Shopify Configuration
SHOPIFY_API_KEY=your-shopify-api-key
SHOPIFY_API_SECRET=your-shopify-api-secret
SHOPIFY_SCOPES=read_products,write_products
SHOPIFY_API_VERSION=2025-07

# Authentication
JWT_SECRET=your-super-secure-jwt-secret

# AI Processing
MAKEIT3D_API_KEY=your-makeit3d-api-key

# Billing & Credits
CREDITS_CURRENCY=USD
SANDBOX_MODE=true

# Rate Limiting (Optional - defaults provided)
RL_BURST_LIMIT=10
RL_BURST_WINDOW=1
RL_SUST_LIMIT=60
RL_SUST_WINDOW=60
RL_ALLOWLIST=shop1.myshopify.com,shop2.myshopify.com

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

### 3. Start Services

#### Option A: Docker Compose (Recommended)

```bash
# From project root
docker-compose up backend redis
```

#### Option B: Manual Start

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery Worker
celery -A app.celery_app:celery_app worker --loglevel=info -Q image_queue,polling_queue

# Terminal 3: Start FastAPI Backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs
```

## 🚂 Railway Deployment

For detailed deployment instructions, see the main [DEPLOYMENT.md](../DEPLOYMENT.md).

Railway requires **two separate services** for this backend:

### Service 1: Backend API

**Service Name:** `maxflow-backend`

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4
```

**Environment Variables:**
```env
BACKEND_URL=https://maxflow-backend.railway.app
FRONTEND_URL=https://your-frontend.railway.app
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_BUCKET=makeit3d-public
REDIS_URL=redis://maxflow-redis.railway.app:6379
SHOPIFY_API_KEY=your-shopify-api-key
SHOPIFY_API_SECRET=your-shopify-api-secret
SHOPIFY_SCOPES=read_products,write_products
SHOPIFY_API_VERSION=2025-07
JWT_SECRET=your-super-secure-jwt-secret
MAKEIT3D_API_KEY=your-makeit3d-api-key
CREDITS_CURRENCY=USD
SANDBOX_MODE=false
RL_BURST_LIMIT=10
RL_BURST_WINDOW=1
RL_SUST_LIMIT=60
RL_SUST_WINDOW=60
SENTRY_DSN=your-sentry-dsn
```

### Service 2: Celery Worker

**Service Name:** `maxflow-celery`

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
celery -A app.celery_app:celery_app worker --loglevel=info -Q image_queue,polling_queue
```

**Environment Variables:**
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_BUCKET=makeit3d-public
REDIS_URL=redis://maxflow-redis.railway.app:6379
MAKEIT3D_API_KEY=your-makeit3d-api-key
SENTRY_DSN=your-sentry-dsn
```

### Service 3: Redis (Optional - Railway provides managed Redis)

If using Railway's managed Redis, create a Redis service and reference it in both services above.

## 📊 API Endpoints

### Authentication
- `GET /auth/install` - Shopify app installation
- `GET /auth/oauth` - OAuth authorization
- `GET /auth/callback` - OAuth callback

### Image Processing
- `POST /upload` - Upload and process image
- `GET /images/{image_id}` - Get image status
- `GET /images` - List all images for shop

### Credits & Billing
- `POST /credits/checkout` - Create checkout session
- `GET /credits/confirm` - Confirm purchase
- `GET /credits/me` - Get current credits

### Dashboard
- `POST /image/dashboard-stats` - Get dashboard statistics
- `GET /me` - Get current user info

### Settings
- `GET /settings` - Get shop settings
- `POST /settings` - Update shop settings
- `POST /settings/avatar` - Upload avatar

### File Serving
- `GET /fileserve/signed-url/{path}` - Generate signed URL
- `GET /fileserve/download` - Download image

### Webhooks
- `POST /webhooks/uninstall` - Handle app uninstall
- `POST /webhooks/app_purchases_one_time_update` - Handle billing

## 🔧 Configuration

### Rate Limiting

The backend includes production-grade rate limiting with dual-bucket sliding windows:

- **Burst Limit:** 10 requests per second
- **Sustained Limit:** 60 requests per minute
- **Per-path Limits:** Custom limits for specific endpoints
- **Allowlist:** Bypass limits for specific shops

### Security Features

- **JWT Authentication** - Secure session management
- **CORS Protection** - Configured for Shopify admin
- **CSP Headers** - Content Security Policy
- **Rate Limiting** - DDoS protection
- **Input Validation** - Request validation and sanitization

### Monitoring

- **Sentry Integration** - Error tracking and performance monitoring
- **Prometheus Metrics** - Available at `/metrics`
- **Health Checks** - Available at `/health`
- **Structured Logging** - JSON-formatted logs

## 📝 Database Schema

### Required Supabase Tables

1. **shops** - Store Shopify shop data and access tokens
2. **shop_credits** - Track credit balances per shop
3. **credit_transactions** - Credit transaction history
4. **credit_pending** - Pending credit purchases
5. **images** - Image processing records
6. **settings** - Shop-specific settings

### Required Supabase Storage Buckets

1. **makeit3d-public** - Store original and processed images

## 🔍 Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   - Verify `REDIS_URL` is correct
   - Check Redis service is running

2. **Supabase Connection Failed**
   - Verify `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`
   - Check network connectivity

3. **Celery Tasks Not Processing**
   - Ensure Celery worker is running
   - Check Redis connection
   - Verify queue names match

4. **Shopify Webhooks Not Working**
   - Verify webhook URLs are accessible
   - Check HMAC verification
   - Ensure proper Shopify app configuration

### Logs

```bash
# Backend logs
docker logs maxflow-backend

# Celery logs
docker logs maxflow-celery

# Railway logs
railway logs
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Supabase Documentation](https://supabase.com/docs)
- [Shopify API Documentation](https://shopify.dev/docs)
- [Railway Documentation](https://docs.railway.app/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
