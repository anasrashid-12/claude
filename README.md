# Shopify AI Image Processing Application

A modern application that leverages AI to process and enhance product images, built with Next.js, FastAPI, and Supabase.

## Tech Stack

- Frontend: Next.js with Tailwind CSS
- Backend: FastAPI with Celery workers
- Database: Supabase
- Image Processing: rembg, OpenCV
- Infrastructure: Docker, Redis

## Project Structure

```
├── frontend/          # Next.js frontend application
├── backend/          # FastAPI backend service
├── supabase/         # Database migrations and configurations
├── docs/            # Documentation
└── monitoring/      # Monitoring configurations (Flower)
```

## Prerequisites

- Docker and Docker Compose
- Node.js 18.x or later (for local development)
- Python >=3.10,<3.12 (for local development)
- Supabase account
- Poetry (Python dependency management)

## Quick Start with Docker

1. Clone the repository:
```bash
git clone https://github.com/yourusername/shopify-ai-image-app.git
cd shopify-ai-image-app
```

2. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your Supabase credentials and other required variables

3. Start the application:
```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Celery Flower: http://localhost:5555

## Local Development Setup

1. Install dependencies:
```bash
# Frontend
cd frontend
npm install
cd ..

# Backend
cd backend
poetry install
cd ..
```

2. Start the services:
```bash
# Start all services with Docker
docker-compose up

# Or start services individually:
# Frontend
cd frontend
npm run dev

# Backend
cd backend
poetry run uvicorn app.main:app --reload

# Celery Worker
cd backend
poetry run celery -A app.core.celery_app worker -Q image_processing
```

## Environment Variables

Required environment variables:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase API key
- `SUPABASE_JWT_SECRET`: Your Supabase JWT secret
- `REDIS_HOST`: Redis host (default: redis)
- `NEXT_PUBLIC_API_URL`: Backend API URL

## Features

- AI-powered image processing:
  - Background removal
  - Image enhancement
  - Format conversion
- Real-time processing status updates
- Async task processing with Celery
- Secure file storage with Supabase
- Modern, responsive UI
- Docker-based deployment

## Monitoring

- Celery Flower dashboard available at http://localhost:5555
- Task status tracking through Supabase
- Processing logs available in Docker logs

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue in the GitHub repository.
