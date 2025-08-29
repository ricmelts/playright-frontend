#!/bin/bash

# PlayRight Full-Stack Startup Script

set -e

echo "🚀 Starting PlayRight Full-Stack Application"
echo "============================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if environment file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration and run again."
    echo "   Example: nano .env"
    exit 1
fi

echo "🔧 Setting up environment..."

# Create necessary directories
mkdir -p BACKEND/pocketbase/pb_data
mkdir -p logs

# Check if images need to be built
echo "🏗️  Building Docker images..."
docker-compose -f docker-compose.fullstack.yml build --parallel

# Start services in the correct order
echo "🔄 Starting backend services..."
docker-compose -f docker-compose.fullstack.yml up -d redis pocketbase

echo "⏳ Waiting for services to be ready..."
sleep 10

echo "🚀 Starting application services..."
docker-compose -f docker-compose.fullstack.yml up -d

echo "⏳ Waiting for all services to start..."
sleep 15

# Check service health
echo "🏥 Checking service health..."

services=("pocketbase:8090" "redis:6379" "api-server:8000" "ai-engine:8001" "frontend:3000")
for service in "${services[@]}"; do
    name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    
    if curl -f -s "http://localhost:$port" > /dev/null 2>&1 || curl -f -s "http://localhost:$port/health" > /dev/null 2>&1; then
        echo "✅ $name is healthy"
    else
        echo "⚠️  $name may not be ready yet"
    fi
done

echo ""
echo "🎉 PlayRight is now running!"
echo "================================"
echo ""
echo "📱 Frontend:      http://localhost:3000"
echo "🔧 API Server:    http://localhost:8000"
echo "🤖 AI Engine:     http://localhost:8001"  
echo "📊 PocketBase:    http://localhost:8090"
echo ""
echo "📋 Useful commands:"
echo "  View logs:      docker-compose -f docker-compose.fullstack.yml logs -f"
echo "  Stop services:  docker-compose -f docker-compose.fullstack.yml down"
echo "  Restart:        ./restart.sh"
echo ""
echo "🔍 To view real-time logs:"
echo "  docker-compose -f docker-compose.fullstack.yml logs -f [service-name]"
echo ""

# Optional: Open browser
if command -v open >/dev/null 2>&1; then
    read -p "🌐 Open browser to http://localhost:3000? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open "http://localhost:3000"
    fi
fi

echo "✨ Setup complete! Happy coding!"