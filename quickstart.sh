#!/bin/bash
# Quick start script for TaskMaster Django project

set -e

echo "================================"
echo "TaskMaster Quick Start"
echo "================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "Starting Docker services..."
echo "This will start PostgreSQL, Redis, Django, and Celery"
echo ""

# Start Docker Compose
docker-compose up -d

echo ""
echo "Waiting for services to be ready..."
sleep 10

echo ""
echo "Running migrations..."
docker-compose exec -T web python manage.py migrate

echo ""
echo "Creating superuser..."
echo "Please enter the following information:"
docker-compose exec web python manage.py createsuperuser

echo ""
echo "================================"
echo "✓ Setup complete!"
echo "================================"
echo ""
echo "Your TaskMaster application is now running!"
echo ""
echo "  • Web Application: http://localhost:8000"
echo "  • Admin Panel: http://localhost:8000/admin"
echo "  • API Documentation: See README.md"
echo ""
echo "Useful commands:"
echo "  • View logs: docker-compose logs -f"
echo "  • Stop services: docker-compose down"
echo "  • Restart: docker-compose restart"
echo ""
echo "Check README.md for API endpoints and usage examples."
echo ""
