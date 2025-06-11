# Shopify AI Image App Deployment Guide

This guide provides instructions for deploying the Shopify AI Image Processing application in both development and production environments.

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)
- Redis server
- Supabase account
- Shopify Partner account

## Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd shopify-ai-image-app
```

2. Copy and configure environment files:
```bash
# Backend
cp backend/env.template backend/.env
# Frontend
cp frontend/env.local.template frontend/.env.local
```

3. Configure environment variables in both `.env` files with your:
- Supabase credentials
- Shopify API credentials
- Redis configuration
- Storage settings

## Development Deployment

1. Start the development environment:
```bash
docker-compose -f docker-compose.dev.yml up --build
```

2. Initialize the database:
```bash
docker-compose exec backend python -m alembic upgrade head
```

3. Access the services:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics

## Production Deployment

### Infrastructure Requirements

- Container orchestration platform (e.g., Kubernetes, ECS)
- Managed Redis service
- Managed PostgreSQL database (or Supabase)
- Object storage service (e.g., S3, R2)
- Load balancer with SSL termination

### Deployment Steps

1. Build production images:
```bash
docker-compose -f docker-compose.prod.yml build
```

2. Push images to container registry:
```bash
docker-compose -f docker-compose.prod.yml push
```

3. Deploy using your container orchestration platform:
- Apply Kubernetes manifests or
- Deploy to ECS using task definitions

4. Configure SSL certificates and domain names

5. Initialize the production database:
```bash
kubectl exec -it <backend-pod> -- python -m alembic upgrade head
```

### Monitoring Setup

1. Deploy Prometheus:
```bash
helm install prometheus prometheus-community/prometheus
```

2. Deploy Grafana:
```bash
helm install grafana grafana/grafana
```

3. Configure Grafana dashboards for:
- API metrics
- Celery task metrics
- Image processing metrics
- Resource utilization

### Health Checks

Monitor the following endpoints:
- `/health` - API health check
- `/metrics` - Prometheus metrics
- Redis health
- Database connectivity
- Storage service status

### Backup and Recovery

1. Configure regular database backups
2. Set up object storage replication
3. Maintain deployment configuration backups
4. Document recovery procedures

## Security Considerations

1. Enable HTTPS only
2. Configure CORS properly
3. Set up rate limiting
4. Use secure environment variables
5. Regular security updates
6. Implement proper authentication

## Scaling Guidelines

1. Horizontal scaling:
- Frontend: Scale based on CPU/memory usage
- Backend API: Scale based on request rate
- Celery workers: Scale based on queue size

2. Vertical scaling:
- Increase resources for CPU-intensive operations
- Adjust memory for image processing tasks

3. Database scaling:
- Connection pooling
- Read replicas if needed
- Regular performance monitoring

## Troubleshooting

1. Check logs:
```bash
# Backend logs
kubectl logs -f <backend-pod>
# Celery worker logs
kubectl logs -f <worker-pod>
```

2. Monitor metrics:
- Request latency
- Error rates
- Queue sizes
- Resource utilization

3. Common issues:
- Redis connection issues
- Database connection problems
- Storage service availability
- Rate limiting conflicts

## Maintenance

1. Regular updates:
- Security patches
- Dependency updates
- Infrastructure updates

2. Monitoring:
- Set up alerts for critical metrics
- Regular performance reviews
- Capacity planning

3. Backup verification:
- Regular backup testing
- Recovery procedure validation
- Documentation updates 