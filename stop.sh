#!/bin/bash

# PlayRight Full-Stack Stop Script

echo "🛑 Stopping PlayRight Full-Stack Application"
echo "============================================="

# Stop all services
echo "🔄 Stopping all services..."
docker-compose -f docker-compose.fullstack.yml down

# Optional: Remove volumes (uncomment if you want to reset data)
# echo "🧹 Removing volumes..."
# docker-compose -f docker-compose.fullstack.yml down -v

echo "✅ All services stopped successfully!"
echo ""
echo "💡 To start again: ./start.sh"
echo "🧹 To completely reset (remove data): docker-compose -f docker-compose.fullstack.yml down -v"