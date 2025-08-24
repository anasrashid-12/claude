# 🧠 MaxFlow AI Image App

A production-ready Shopify app for AI-powered image processing. Upload images, remove backgrounds, upscale, and optimize them with advanced AI technology.

## 🚀 Features

- **AI Image Processing**: Remove backgrounds, upscale, and optimize images
- **Shopify Integration**: Seamless integration with Shopify Admin
- **Real-time Updates**: Live status updates via Supabase realtime
- **Credit System**: Pay-per-use credit management
- **Batch Upload**: Upload multiple images simultaneously
- **Progress Tracking**: Real-time upload and processing progress
- **Gallery View**: Browse and download processed images
- **Settings Management**: Customize app preferences and avatar
- **Dark/Light Mode**: Beautiful responsive UI with theme switching

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Shopify Polaris + Custom Components
- **State Management**: React Context + SWR
- **Real-time**: Supabase Realtime
- **Authentication**: Shopify App Bridge
- **Error Monitoring**: Sentry

### Backend
- **Framework**: FastAPI (Python)
- **Background Tasks**: Celery + Redis
- **Database**: Supabase (PostgreSQL)
- **File Storage**: Supabase Storage
- **AI Processing**: MakeIt3D API
- **Rate Limiting**: Production-grade with Redis
- **Security**: JWT, CORS, CSP headers
- **Monitoring**: Sentry + Prometheus metrics

## 📋 Prerequisites

Before you begin, ensure you have:

- Node.js 18+ installed
- Python 3.11+ installed
- npm or yarn package manager
- Shopify Partner account
- Supabase project
- Railway account (for deployment)
- MakeIt3D API key

## 🏗️ Project Structure

```
shopify-ai-image-app/
├── frontend/                 # Next.js frontend application
│   ├── src/
│   │   ├── app/             # Next.js App Router pages
│   │   ├── components/      # Reusable UI components
│   │   ├── hooks/          # Custom React hooks
│   │   └── utils/          # Utility functions
│   ├── public/             # Static assets
│   └── Dockerfile         # Frontend Docker configuration
├── backend/                # FastAPI backend application
│   ├── app/
│   │   ├── routers/       # API route handlers
│   │   ├── services/      # Business logic services
│   │   ├── tasks/         # Celery background tasks
│   │   └── middleware/    # Custom middleware
│   ├── Dockerfile.backend # Backend Docker configuration
│   └── requirements.txt   # Python dependencies
├── docker-compose.yml     # Local development setup
├── README.md             # This file
└── DEPLOYMENT.md         # Detailed deployment guide
```

## 🚀 Quick Start (Local Development)

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd shopify-ai-image-app

# Install frontend dependencies
cd frontend
npm install

# Install backend dependencies
cd ../backend
pip install -r requirements.txt
```

### 2. Environment Setup

Create environment files for both frontend and backend:

#### Frontend (.env.local)
```env
# Shopify Configuration
NEXT_PUBLIC_SHOPIFY_API_KEY=your_shopify_api_key

# Backend Configuration
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Frontend URL (for development)
NEXT_PUBLIC_FRONTEND_URL=http://localhost:3000

# JWT Secret (same as backend)
JWT_SECRET=your_jwt_secret_key
```

#### Backend (.env)
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

# Rate Limiting
RL_BURST_LIMIT=10
RL_BURST_WINDOW=1
RL_SUST_LIMIT=60
RL_SUST_WINDOW=60
```

### 3. Start Services

#### Option A: Docker Compose (Recommended)

```bash
# From project root
docker-compose up
```

#### Option B: Manual Start

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery Worker
cd backend
celery -A app.celery_app:celery_app worker --loglevel=info -Q image_queue,polling_queue

# Terminal 3: Start Backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 4: Start Frontend
cd frontend
npm run dev
```

### 4. Verify Installation

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🚀 Railway Deployment

For detailed deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md).

### Quick Deployment Overview

This app requires **4 separate services** on Railway:

1. **Frontend** (Next.js)
2. **Backend API** (FastAPI)
3. **Celery Worker** (Background tasks)
4. **Redis** (Message broker)

### Deployment Steps

1. **Deploy Redis** - Create a Redis service
2. **Deploy Backend** - Deploy FastAPI with Celery worker
3. **Deploy Frontend** - Deploy Next.js application
4. **Configure Shopify** - Update app URLs and webhooks

## 🔧 Configuration

### Environment Variables Reference

| Variable | Description | Required | Service |
|----------|-------------|----------|---------|
| `NEXT_PUBLIC_SHOPIFY_API_KEY` | Your Shopify app's API key | ✅ | Frontend |
| `NEXT_PUBLIC_BACKEND_URL` | Backend API URL | ✅ | Frontend |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL | ✅ | Frontend |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anonymous key | ✅ | Frontend |
| `NEXT_PUBLIC_FRONTEND_URL` | Frontend URL for redirects | ✅ | Frontend |
| `JWT_SECRET` | Secret for JWT token signing | ✅ | Frontend, Backend |
| `BACKEND_URL` | Backend URL for webhooks | ✅ | Backend |
| `FRONTEND_URL` | Frontend URL for redirects | ✅ | Backend |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key | ✅ | Backend, Celery |
| `REDIS_URL` | Redis connection URL | ✅ | Backend, Celery |
| `SHOPIFY_API_KEY` | Shopify app API key | ✅ | Backend |
| `SHOPIFY_API_SECRET` | Shopify app API secret | ✅ | Backend |
| `MAKEIT3D_API_KEY` | MakeIt3D API key | ✅ | Backend, Celery |

### Shopify App Configuration

1. **Required Scopes**:
   - `write_products`
   - `write_script_tags`
   - `read_products`

2. **App Bridge Configuration**:
   - API Key: Your Shopify app's API key
   - Host: Automatically provided by Shopify

## 📊 Monitoring & Logs

### Railway Dashboard
- Monitor resource usage for all services
- Check deployment status
- View logs and errors

### Service-Specific Logs
```bash
# Check Railway logs for each service
railway logs --service frontend
railway logs --service backend
railway logs --service celery
railway logs --service redis
```

### Sentry Integration
- Your app includes Sentry for error monitoring
- Check your Sentry dashboard for production errors

## 🔍 Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check all environment variables are set
   - Verify Node.js/Python versions
   - Clear build caches

2. **Authentication Issues**:
   - Verify Shopify app configuration
   - Check redirect URLs in Partner Dashboard
   - Ensure backend is accessible from frontend

3. **Celery Tasks Not Processing**:
   - Ensure Celery worker is running
   - Check Redis connection
   - Verify queue names match

4. **Real-time Not Working**:
   - Verify Supabase configuration
   - Check network connectivity
   - Review browser console for errors

### Debug Commands

```bash
# Check Railway logs
railway logs

# View environment variables
railway variables

# Restart deployment
railway up

# Check service status
railway status
```

## 📚 API Reference

### Key Endpoints

- `POST /upload` - Upload images
- `GET /images/{image_id}` - Get image status
- `GET /images` - List all images for shop
- `GET /credits/me` - Get user's credit balance
- `POST /credits/checkout` - Purchase credits
- `POST /image/dashboard-stats` - Get dashboard statistics

### Authentication

All API calls require session cookies set by the backend authentication flow.

## 🔄 Updates

### Automatic Updates
1. Push changes to your GitHub repository
2. Railway will automatically redeploy all services
3. Monitor deployment logs

### Manual Updates
1. Go to your Railway project
2. Click "Deploy" on the service you want to update
3. Check logs for any issues

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check this README and [DEPLOYMENT.md](./DEPLOYMENT.md)
- **Issues**: Create an issue in the GitHub repository
- **Shopify Support**: [Shopify Developer Documentation](https://shopify.dev/)
- **Railway Support**: [Railway Documentation](https://docs.railway.app)

## 🎉 Success!

Once deployed successfully, your app will be available at:
- **Frontend**: `https://your-frontend.railway.app`
- **Backend**: `https://your-backend.railway.app`
- **Celery Worker**: Running in background
- **Redis**: Managed by Railway

Your Shopify app is now ready for production use! 🚀

---

**Built with ❤️ using Next.js, FastAPI, Celery, and Shopify App Bridge**
