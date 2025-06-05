# Deployment Guide

## Prerequisites
- Docker and Docker Compose
- Node.js 18+
- Python 3.9+
- Shopify Partner Account
- Cloudflare R2 Account
- Supabase Account

## Environment Setup

1. **Clone the Repository**
```bash
git clone <repository-url>
cd shopify-ai-image-app
```

2. **Configure Environment Variables**
```bash
# Backend
cp backend/env.template backend/.env
# Edit backend/.env with your credentials

# Frontend
cp frontend/.env.example frontend/.env
# Edit frontend/.env with your credentials
```

3. **Setup Infrastructure**

```bash
# Start all services
docker-compose up -d

# Initialize database
cd supabase
python setup.py

# Start monitoring
cd ../monitoring
./setup_monitoring.sh
```

## Development Deployment

1. **Start Backend**
```bash
cd backend
pip install -r requirements.txt
python run_dev.py
```

2. **Start Frontend**
```bash
cd frontend
npm install
npm run dev
```

## Production Deployment

1. **Build Images**
```bash
docker-compose -f docker-compose.prod.yml build
```

2. **Deploy**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **Monitor**
- Access Grafana: http://your-domain:3000
- Check logs: `docker-compose logs -f`

## SSL Configuration
- Configure SSL certificates using Let's Encrypt
- Update Nginx configuration

## Backup and Recovery
- Database backups are automated daily
- Images are backed up to Cloudflare R2
- Recovery procedures are documented in maintenance guide

## Scaling
- Horizontal scaling for workers
- Vertical scaling for database
- CDN for image delivery

## Security Checklist
- [ ] SSL certificates installed
- [ ] Firewall configured
- [ ] Rate limiting enabled
- [ ] Monitoring alerts set up
- [ ] Backup verification tested 