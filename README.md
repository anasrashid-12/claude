# Shopify AI Image Processing App

A powerful Shopify application that provides AI-powered image processing capabilities for e-commerce stores.

## Features

- Background removal
- Image optimization
- Bulk processing
- Real-time progress tracking
- Automatic image backup
- Comprehensive monitoring

## Tech Stack

### Frontend
- Next.js with TypeScript
- Shopify Polaris components
- React Query for data fetching
- Zustand for state management

### Backend
- Python with FastAPI
- Celery for task queue
- Redis for caching and queue
- Supabase for database
- Cloudflare R2 for storage

### Monitoring
- Prometheus for metrics
- Grafana for visualization
- Custom alerting system

## Project Structure

```
.
├── frontend/                # Next.js frontend application
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── features/       # Feature-specific components
│   │   ├── services/       # API and auth services
│   │   ├── hooks/         # Custom React hooks
│   │   └── utils/         # Utility functions
│   └── public/            # Static assets
│
├── backend/               # Python/FastAPI backend
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── services/     # Business logic
│   │   ├── models/       # Database models
│   │   └── core/         # Core functionality
│   └── tests/            # Test suites
│
├── monitoring/           # Monitoring configuration
│   ├── prometheus/
│   └── grafana/
│
└── docs/                # Documentation
    ├── api/            # API documentation
    ├── deployment/     # Deployment guides
    └── maintenance/    # Maintenance guides
```

## Getting Started

1. **Prerequisites**
   - Node.js 18+
   - Python 3.9+
   - Docker and Docker Compose
   - Shopify Partner Account

2. **Installation**
   ```bash
   # Clone repository
   git clone <repository-url>
   cd shopify-ai-image-app

   # Install frontend dependencies
   cd frontend
   npm install

   # Install backend dependencies
   cd ../backend
   pip install -r requirements.txt
   ```

3. **Configuration**
   - Set up environment variables
   - Configure Shopify app credentials
   - Set up Cloudflare R2 bucket
   - Configure Supabase database

4. **Development**
   ```bash
   # Start frontend
   cd frontend
   npm run dev

   # Start backend
   cd backend
   python run_dev.py
   ```

## Documentation

- [API Documentation](docs/api/README.md)
- [Deployment Guide](docs/deployment/README.md)
- [Maintenance Guide](docs/maintenance/README.md)

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 
# Maxflow Gallery - Shopify Gallery App

Maxflow Gallery is a Shopify app that provides AI-powered image processing capabilities for e-commerce stores, featuring background removal, image rescaling, and quality optimization.

## Key Features

### Core Functionality
- **Shopify Store Integration**: OAuth connection and product synchronization
- **AI Image Processing**: Background removal, rescaling optimization
- **Bulk Operations**: Process multiple images with queue management
- **Real-time Progress**: Live status updates for processing operations
- **Image Management**: Backup, version control, and selective processing
- **Rate Limiting**: Robust rate limiting to prevent API abuse

### User Interface
- **Dashboard**: Processing statistics and recent activity overview
- **Image Gallery**: Grid view with processing status indicators
- **Processing Queue**: Real-time status of ongoing operations
- **Settings Panel**: Configuration for default processing options
- **Preview System**: Before/after image comparisons

## Repository Structure

```
maxflow-gallery/
├── README.md
├── docker-compose.yml
├── .gitignore
├── .env.example
│
├── frontend/                          # NextJS Shopify Embedded App
│   ├── package.json
│   ├── package-lock.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── .env.local.example
│   ├── public/
│   │   ├── favicon.ico
│   │   └── images/
│   ├── src/
│   │   ├── app/                       # App Router (Next.js 13+)
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── auth/
│   │   │   │   └── callback/
│   │   │   │       └── page.tsx
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx
│   │   │   ├── gallery/
│   │   │   │   └── page.tsx
│   │   │   ├── settings/
│   │   │   │   └── page.tsx
│   │   │   └── api/                   # API Routes
│   │   │       ├── auth/
│   │   │       │   └── shopify/
│   │   │       │       └── route.ts
│   │   │       ├── images/
│   │   │       │   ├── process/
│   │   │       │   │   └── route.ts
│   │   │       │   └── status/
│   │   │       │       └── route.ts
│   │   │       └── products/
│   │   │           └── route.ts
│   │   ├── components/
│   │   │   ├── ui/                    # shadcn/ui components
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── dialog.tsx
│   │   │   │   ├── progress.tsx
│   │   │   │   └── toast.tsx
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Layout.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── StatsOverview.tsx
│   │   │   │   └── RecentActivity.tsx
│   │   │   ├── gallery/
│   │   │   │   ├── ImageGrid.tsx
│   │   │   │   ├── ImageCard.tsx
│   │   │   │   ├── ImagePreview.tsx
│   │   │   │   └── BulkActions.tsx
│   │   │   ├── processing/
│   │   │   │   ├── ProcessingQueue.tsx
│   │   │   │   ├── ProgressBar.tsx
│   │   │   │   └── StatusIndicator.tsx
│   │   │   └── settings/
│   │   │       ├── ProcessingSettings.tsx
│   │   │       └── ShopifyConnection.tsx
│   │   ├── lib/
│   │   │   ├── auth.ts
│   │   │   ├── shopify.ts
│   │   │   ├── api.ts
│   │   │   └── utils.ts
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useImages.ts
│   │   │   └── useProcessing.ts
│   │   ├── types/
│   │   │   ├── shopify.ts
│   │   │   ├── image.ts
│   │   │   └── api.ts
│   │   └── styles/
│   │       └── globals.css
│   └── components.json                # shadcn/ui config
│
├── backend/                           # FastAPI Python Backend
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── Dockerfile
│   ├── .env.example
│   ├── alembic.ini                    # Database migrations
│   ├── alembic/
│   │   ├── versions/
│   │   └── env.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── config.py                  # Configuration settings
│   │   ├── dependencies.py            # Common dependencies
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── images.py
│   │   │   │   ├── products.py
│   │   │   │   ├── processing.py
│   │   │   │   └── webhooks.py
│   │   │   └── middleware/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py
│   │   │       ├── rate_limiting.py
│   │   │       └── cors.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── security.py
│   │   │   ├── config.py
│   │   │   └── exceptions.py
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── models/
│   │   │       ├── __init__.py
│   │   │       ├── user.py
│   │   │       ├── shop.py
│   │   │       ├── image.py
│   │   │       └── processing_job.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── shop.py
│   │   │   ├── image.py
│   │   │   └── processing.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── shopify_service.py
│   │   │   ├── image_service.py
│   │   │   ├── ai_service.py
│   │   │   └── processing_service.py
│   │   ├── tasks/                     # Celery tasks
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py
│   │   │   ├── image_processing.py
│   │   │   └── background_removal.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── image_utils.py
│   │   │   ├── validation.py
│   │   │   └── helpers.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── conftest.py
│   │       ├── test_auth.py
│   │       ├── test_images.py
│   │       └── test_processing.py
│   └── scripts/
│       ├── start.sh
│       └── migrate.py
│
├── redis/                             # Redis configuration
│   └── redis.conf
│
├── docs/                              # Documentation
│   ├── api/
│   │   ├── openapi.json
│   │   └── swagger.html
│   ├── deployment/
│   │   ├── docker.md
│   │   └── production.md
│   └── user-guide/
│       └── shopify-setup.md
│
├── scripts/                           # Deployment scripts
│   ├── setup.sh
│   ├── deploy.sh
│   └── backup.sh
│
└── monitoring/                        # Monitoring configuration
    ├── prometheus.yml
    └── grafana/
        └── dashboards/
```
