# How to Verify the Project Runs

Follow these steps to test that everything works:

## Quick Test (Recommended)

```bash
# 1. Start Docker services
docker-compose up --build -d

# 2. Check all services are running
docker-compose ps

# You should see:
# - taskmaster_db (healthy)
# - taskmaster_redis (healthy)  
# - taskmaster_web (running)
# - taskmaster_celery_worker (running)
# - taskmaster_celery_beat (running)

# 3. Run migrations
docker-compose exec web python manage.py migrate

# 4. Create superuser
docker-compose exec web python manage.py createsuperuser

# 5. Test the web server
curl http://localhost:8000

# 6. Test the API
curl http://localhost:8000/api/accounts/register/ \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","first_name":"Test","last_name":"User","password":"TestPass123!","password2":"TestPass123!"}'

# 7. Open in browser
# Visit: http://localhost:8000
# Visit: http://localhost:8000/admin
```

## What You Should See

### In Terminal (docker-compose logs -f web)
```
Django version 5.0.1, using settings 'taskmaster.settings'
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

### In Browser (http://localhost:8000)
- Beautiful home page with API documentation
- Links to admin panel
- List of API endpoints

### In Admin (http://localhost:8000/admin)
- Login with superuser credentials
- See: Users, Projects, Tasks, Notifications
- Create test data

### API Test
```bash
# Register user
curl -X POST http://localhost:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "SecurePass123!",
    "password2": "SecurePass123!"
  }'

# Expected: JSON response with user data

# Get token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'

# Expected: JSON response with access and refresh tokens
```

## Verification Checklist

Run through this to confirm everything works:

- [ ] Docker services start without errors
- [ ] Database migrations complete successfully
- [ ] Superuser creation works
- [ ] Home page loads (http://localhost:8000)
- [ ] Admin panel accessible (http://localhost:8000/admin)
- [ ] Can register user via API
- [ ] Can get JWT token
- [ ] Celery worker is processing tasks (check logs)
- [ ] Redis is connected (docker-compose exec redis redis-cli ping)

## Troubleshooting

### If services don't start:
```bash
docker-compose down -v
docker-compose up --build
```

### If port 8000 is in use:
```bash
# Edit docker-compose.yml
# Change "8000:8000" to "8080:8000"
# Then access via http://localhost:8080
```

### To see detailed logs:
```bash
docker-compose logs -f
```

### To reset everything:
```bash
docker-compose down -v  # WARNING: Deletes all data!
docker-compose up --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## Success Indicators

✅ **Project runs successfully if:**
1. All 5 Docker containers are running
2. Web server responds on port 8000
3. Can create superuser
4. Can access admin panel
5. API endpoints return responses
6. Celery worker processes tasks

## Files to Review

After confirming it runs:
- **README.md** - Complete documentation
- **QUICKSTART.md** - Quick setup guide
- **VALIDATION_CHECKLIST.md** - All implemented features
- **taskmaster/** - All the Django code

Enjoy learning Django! 🚀
