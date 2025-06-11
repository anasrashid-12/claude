# Shopify AI Image Processing App

A powerful AI-powered image processing application for Shopify stores. This application allows store owners to automatically process, optimize, and enhance their product images using advanced AI algorithms.

## Features

- Background removal
- Image optimization and resizing
- Bulk image processing
- Real-time processing status tracking
- Shopify integration
- Secure authentication and authorization
- Task queue management with Celery
- Monitoring dashboard with Flower

## Tech Stack

- **Frontend**: Next.js, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python
- **Database**: Supabase (PostgreSQL)
- **Task Queue**: Celery with Redis
- **Storage**: Supabase Storage / AWS S3
- **Monitoring**: Flower dashboard
- **Containerization**: Docker and Docker Compose

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- Shopify Partner account
- Supabase account
- (Optional) AWS account for S3 storage

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/shopify-ai-image-app.git
   cd shopify-ai-image-app
   ```

2. Create environment files:
   ```bash
   cp backend/env.template backend/.env
   cp frontend/.env.local.template frontend/.env.local
   ```

3. Configure environment variables:
   - Update `backend/.env` with your Supabase, Shopify, and other credentials
   - Update `frontend/.env.local` with your frontend configuration

4. Create a Shopify app in your Partner Dashboard:
   - Set the App URL to `http://localhost:3000`
   - Set the Allowed redirection URL(s) to `http://localhost:3000/auth/callback`
   - Copy the API key and secret to your environment files

5. Create a Supabase project:
   - Create a new project
   - Copy the project URL and anon key to your environment files
   - Run the database migrations from `supabase/migrations`

6. Build and start the services:
   ```bash
   docker-compose build
   docker-compose up -d
   ```

7. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001
   - Flower dashboard: http://localhost:5555

## Development

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Deployment

1. Update environment variables for production
2. Build the Docker images:
   ```bash
   docker-compose -f docker-compose.prod.yml build
   ```

3. Deploy the services:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## Monitoring

- Access the Flower dashboard at http://localhost:5555 to monitor Celery tasks
- Check the FastAPI docs at http://localhost:8001/docs for API documentation
- Monitor Supabase dashboard for database performance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
