#!/bin/bash

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOL
# Shopify Configuration
SHOPIFY_API_KEY=your_api_key_here
SHOPIFY_API_SECRET=your_api_secret_here

# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_JWT_SECRET=your_jwt_secret

# GPU Configuration (leave empty for CPU only)
CUDA_VISIBLE_DEVICES=

# Redis Configuration (usually don't need to change)
REDIS_URL=redis://redis:6379/0
EOL
    echo ".env file created. Please update it with your credentials."
    exit 1
fi

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check GPU availability
check_gpu() {
    if command -v nvidia-smi &> /dev/null; then
        echo "GPU detected! Enabling GPU support..."
        export CUDA_VISIBLE_DEVICES=0
    else
        echo "No GPU detected. Running in CPU mode..."
        export CUDA_VISIBLE_DEVICES=""
    fi
}

# Main script
echo "🚀 Starting Shopify AI Image App development environment..."

# Check prerequisites
check_docker
check_gpu

# Build and start services
echo "🏗️  Building services..."
docker-compose build

echo "🌟 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
docker-compose ps

echo "
✅ Development environment is ready!

📝 Available services:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Flower (Task Monitor): http://localhost:5555

💡 Useful commands:
   - View logs: docker-compose logs -f
   - Stop services: docker-compose down
   - Restart services: docker-compose restart

🔧 To rebuild a specific service:
   docker-compose build <service_name>
   docker-compose up -d <service_name>
" 