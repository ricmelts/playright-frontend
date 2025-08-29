#!/bin/bash

# PlayRight Full-Stack Restart Script

echo "🔄 Restarting PlayRight Full-Stack Application"
echo "==============================================="

echo "🛑 Stopping current services..."
docker-compose -f docker-compose.fullstack.yml down

echo "⏳ Waiting for services to stop..."
sleep 5

echo "🚀 Starting services..."
docker-compose -f docker-compose.fullstack.yml up -d

echo "⏳ Waiting for services to be ready..."
sleep 15

echo "✅ Restart complete!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 API: http://localhost:8000"
echo "📊 Admin: http://localhost:8090"