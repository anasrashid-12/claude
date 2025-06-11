# Getting Started

This guide will help you set up the Shopify AI Image Processing App for local development.

## Initial Setup

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/shopify-ai-image-app.git
cd shopify-ai-image-app
```

2. **Set Up Supabase**
- Create a new project at https://supabase.com
- Go to Project Settings > API to get your credentials
- Save the following values:
  - Project URL
  - anon/public key
  - service_role key
  - JWT secret

3. **Configure Environment Variables**
Create a `.env` file in the root directory with:
```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_role_key
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_JWT_SECRET=your_supabase_jwt_secret

# Security
JWT_SECRET_KEY=your_jwt_secret_key

# Shopify Configuration (for production)
SHOPIFY_API_KEY=your_shopify_api_key
SHOPIFY_API_SECRET=your_shopify_api_secret
SHOPIFY_APP_URL=https://your-app-url.com
SHOPIFY_SCOPES=write_products,write_files,read_files
```

4. **Apply Database Migrations**
```bash
cd supabase
supabase db reset
```

5. **Start the Development Environment**
```bash
docker-compose up --build
```

## Verify Setup

1. **Check Services**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001/docs
- Flower Dashboard: http://localhost:5555
- Redis: localhost:6379

2. **Verify Database**
- Check Supabase dashboard for tables
- Verify RLS policies are in place
- Test database connections from services

3. **Test Image Processing**
- Upload a test image through the frontend
- Monitor task progress in Flower
- Verify processed image in Supabase storage

## Common Issues and Solutions

1. **Redis Connection Issues**
```bash
# Check Redis container
docker-compose ps redis
# View Redis logs
docker-compose logs redis
```

2. **Backend Service Issues**
```bash
# Check backend logs
docker-compose logs ai-service
# Restart backend
docker-compose restart ai-service
```

3. **Worker Issues**
```bash
# Check worker logs
docker-compose logs ai-worker
# Restart worker
docker-compose restart ai-worker
```

4. **Frontend Issues**
```bash
# Check frontend logs
docker-compose logs frontend
# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

## Development Workflow

1. **Making Changes**
- Frontend changes will hot-reload
- Backend changes will trigger auto-reload
- Database changes require migration updates

2. **Adding Dependencies**
- Frontend: Add to package.json and rebuild
- Backend: Add to requirements.txt and rebuild
- Update Dockerfiles if system dependencies change

3. **Testing**
- Run frontend tests: `docker-compose exec frontend npm test`
- Run backend tests: `docker-compose exec ai-service pytest`
- Check API docs at http://localhost:8001/docs

4. **Debugging**
- Use Flower dashboard for task monitoring
- Check container logs with `docker-compose logs [service]`
- Use browser dev tools for frontend debugging 