# Quick Start Guide

Follow these simple steps to get TaskMaster running in under 5 minutes!

## Prerequisites

- Docker and Docker Compose installed ([Get Docker](https://docs.docker.com/get-docker/))
- That's it! Docker will handle everything else.

## Step-by-Step Setup

### 1. Clone and Navigate
```bash
cd DjangoLearn
```

### 2. Create Environment File
```bash
cp .env.example .env
```
You can use the default values for local development.

### 3. Start All Services
```bash
docker-compose up -d
```
This starts:
- PostgreSQL database
- Redis cache
- Django web server
- Celery worker
- Celery beat scheduler

### 4. Wait for Services (about 30 seconds)
```bash
docker-compose logs -f web
```
Wait until you see "Starting development server"
Press `Ctrl+C` to exit logs

### 5. Run Database Migrations
```bash
docker-compose exec web python manage.py migrate
```

### 6. Create Admin User
```bash
docker-compose exec web python manage.py createsuperuser
```
Follow the prompts to create your admin account.

### 7. Access the Application

**You're done!** 🎉

Open your browser:
- **Home Page**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API Root**: http://localhost:8000/api/

## Quick Test

### Test the API

1. **Register a user**:
```bash
curl -X POST http://localhost:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "password": "TestPass123!",
    "password2": "TestPass123!"
  }'
```

2. **Get a token**:
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

3. **Use the token** (replace YOUR_TOKEN with the access token from step 2):
```bash
curl -X GET http://localhost:8000/api/accounts/users/me/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Useful Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Just Django
docker-compose logs -f web

# Just Celery
docker-compose logs -f celery_worker
```

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

### Access Django Shell
```bash
docker-compose exec web python manage.py shell
```

### Run Tests
```bash
docker-compose exec web python manage.py test
```

## Troubleshooting

### Port 8000 Already in Use
```bash
# Find what's using the port
lsof -i :8000

# Or change the port in docker-compose.yml
# Change "8000:8000" to "8080:8000" under web service
```

### Services Not Starting
```bash
# Check service health
docker-compose ps

# Rebuild containers
docker-compose down
docker-compose up --build
```

### Database Errors
```bash
# Reset database
docker-compose down -v  # WARNING: This deletes all data!
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## What's Next?

1. ✅ Log into the admin panel at http://localhost:8000/admin
2. ✅ Create a project
3. ✅ Create some tasks
4. ✅ Test the API endpoints (see README.md for full list)
5. ✅ Explore the code and learn Django!

For detailed documentation, API endpoints, and learning resources, see **README.md**.
