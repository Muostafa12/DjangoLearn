# TaskMaster - Learn Django with Redis

A comprehensive Django project designed to teach you Django development with Redis integration. This project demonstrates best practices, real-world patterns, and advanced features.

## What You'll Learn

### Core Django Concepts
- **Custom User Model**: Email-based authentication instead of username
- **Models & Relationships**:
  - One-to-One (User ↔ UserProfile)
  - Many-to-One (Task → Project)
  - Many-to-Many (Project ↔ Users through ProjectMember)
  - Self-referencing (Task → Parent Task, Comment → Parent Comment)
  - Generic Relations (Notification → Any Model)
- **Model Managers**: Custom querysets and reusable query logic
- **Signals**: Automatic actions on model events
- **Admin Customization**: Custom admin interfaces with inlines
- **Choices & Validators**: Structured data with validation

### Django REST Framework
- **Serializers**: Data validation and transformation
- **ViewSets**: Complete CRUD operations
- **Custom Actions**: Additional endpoints (@action decorator)
- **Permissions**: Authentication and authorization
- **Filtering & Search**: Query parameters and filtering
- **Pagination**: Efficient data loading

### Redis Integration
- **Caching**: Speed up database queries
- **Session Storage**: Redis-backed sessions
- **Celery Broker**: Asynchronous task queue

### Celery (Async Tasks)
- **Background Tasks**: Email notifications, data processing
- **Periodic Tasks**: Scheduled jobs with Celery Beat
- **Task Monitoring**: Track task execution

### Advanced Patterns
- **Query Optimization**: select_related, prefetch_related
- **File Uploads**: Handle images and attachments
- **Markdown Support**: Rich text content
- **Docker Deployment**: Containerized application

## Project Structure

```
taskmaster/
├── accounts/           # User authentication and profiles
│   ├── models.py      # User, UserProfile
│   ├── serializers.py # User serializers
│   ├── views.py       # User API views
│   └── signals.py     # Auto-create profiles
├── projects/          # Project management
│   ├── models.py      # Project, ProjectMember
│   ├── serializers.py
│   ├── views.py       # Project CRUD with caching
│   └── admin.py
├── tasks/             # Task management
│   ├── models.py      # Task, Comment, TaskAttachment
│   ├── serializers.py
│   ├── views.py       # Task operations
│   └── signals.py     # Auto-notifications
├── notifications/     # Notification system
│   ├── models.py      # Notification with GenericForeignKey
│   ├── tasks.py       # Celery tasks
│   └── views.py       # Notification API
├── static/            # Static files (CSS, JS)
├── media/             # User uploads
├── templates/         # HTML templates
└── settings.py        # Project configuration
```

## Setup Instructions

### Option 1: Docker Setup (Recommended)

The easiest way to get started. Docker handles all dependencies including PostgreSQL and Redis.

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd DjangoLearn
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Build and start services**
   ```bash
   docker-compose up --build
   ```

4. **Run migrations** (in a new terminal)
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

6. **Access the application**
   - Web: http://localhost:8000
   - Admin: http://localhost:8000/admin

### Option 2: Local Setup

For local development without Docker.

1. **Install Python 3.11+**
   ```bash
   python --version  # Should be 3.11 or higher
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install PostgreSQL**
   - macOS: `brew install postgresql`
   - Ubuntu: `sudo apt-get install postgresql`
   - Windows: Download from https://www.postgresql.org/download/

5. **Install Redis**
   - macOS: `brew install redis`
   - Ubuntu: `sudo apt-get install redis-server`
   - Windows: Download from https://github.com/microsoftarchive/redis/releases

6. **Create PostgreSQL database**
   ```bash
   createdb taskmaster_db
   createuser taskmaster_user
   psql -c "ALTER USER taskmaster_user WITH PASSWORD 'taskmaster_pass';"
   psql -c "GRANT ALL PRIVILEGES ON DATABASE taskmaster_db TO taskmaster_user;"
   ```

7. **Start Redis**
   ```bash
   redis-server
   ```

8. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

9. **Run migrations**
   ```bash
   python manage.py migrate
   ```

10. **Create superuser**
    ```bash
    python manage.py createsuperuser
    ```

11. **Start Django**
    ```bash
    python manage.py runserver
    ```

12. **Start Celery Worker** (new terminal)
    ```bash
    celery -A taskmaster worker --loglevel=info
    ```

13. **Start Celery Beat** (new terminal)
    ```bash
    celery -A taskmaster beat --loglevel=info
    ```

## Usage Examples

### Create a User (API)

```bash
curl -X POST http://localhost:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "SecurePass123!",
    "password2": "SecurePass123!"
  }'
```

### Get JWT Token

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

### Create a Project

```bash
curl -X POST http://localhost:8000/api/projects/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "name": "My First Project",
    "description": "Learning Django!",
    "status": "active"
  }'
```

### Create a Task

```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "title": "Implement user authentication",
    "description": "## Task Description\n\nAdd login functionality",
    "priority": "high",
    "project": 1,
    "assignee_ids": [1]
  }'
```

## Learning Path

### 1. Start with Models (Day 1-2)
- Explore `accounts/models.py` - Custom User Model
- Study `projects/models.py` - Relationships
- Review `tasks/models.py` - Custom Managers
- Understand `notifications/models.py` - Generic Relations

### 2. Admin Interface (Day 2)
- Check all `admin.py` files
- Create data via Django admin
- Customize admin views

### 3. Serializers & APIs (Day 3-4)
- Study serializers in each app
- Test API endpoints using curl or Postman
- Learn about validation and nested serializers

### 4. Views & ViewSets (Day 4-5)
- Explore ViewSets in `views.py` files
- Understand custom actions
- Learn about filtering and permissions

### 5. Caching with Redis (Day 5-6)
- Review caching in `views.py`
- Test cache performance
- Experiment with cache invalidation

### 6. Celery Tasks (Day 6-7)
- Study `notifications/tasks.py`
- Understand async task execution
- Learn about periodic tasks

### 7. Signals (Day 7)
- Review `signals.py` files
- Create custom signals
- Understand signal best practices

## API Endpoints

### Authentication
- `POST /api/token/` - Get JWT token
- `POST /api/token/refresh/` - Refresh token
- `POST /api/accounts/register/` - Register user

### Users
- `GET /api/accounts/users/` - List users
- `GET /api/accounts/users/me/` - Current user
- `PUT /api/accounts/users/update_profile/` - Update profile
- `POST /api/accounts/users/change_password/` - Change password

### Projects
- `GET /api/projects/` - List projects
- `POST /api/projects/` - Create project
- `GET /api/projects/{id}/` - Get project (cached)
- `PUT /api/projects/{id}/` - Update project
- `DELETE /api/projects/{id}/` - Delete project
- `POST /api/projects/{id}/add_member/` - Add member
- `POST /api/projects/{id}/remove_member/` - Remove member
- `GET /api/projects/{id}/statistics/` - Project stats

### Tasks
- `GET /api/tasks/` - List tasks (with filters)
- `POST /api/tasks/` - Create task
- `GET /api/tasks/{id}/` - Get task (cached)
- `PUT /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Delete task
- `POST /api/tasks/{id}/mark_completed/` - Complete task
- `POST /api/tasks/{id}/mark_in_progress/` - Start task
- `POST /api/tasks/{id}/add_comment/` - Add comment
- `POST /api/tasks/{id}/upload_attachment/` - Upload file

### Notifications
- `GET /api/notifications/` - List notifications
- `GET /api/notifications/{id}/` - Get notification
- `POST /api/notifications/{id}/mark_as_read/` - Mark read
- `POST /api/notifications/mark_all_as_read/` - Mark all read
- `GET /api/notifications/unread_count/` - Unread count

## Redis Usage in the Project

### 1. Caching
```python
# Cache user data for 5 minutes
cache_key = f'user_{user_id}'
cached_data = cache.get(cache_key)
if cached_data:
    return cached_data
cache.set(cache_key, data, 300)
```

### 2. Session Storage
Sessions are automatically stored in Redis (configured in settings.py)

### 3. Celery Broker
Redis manages the task queue for async operations

### 4. Cache Invalidation
```python
# Invalidate when data changes
cache.delete(f'project_{project_id}')
```

## Testing

### Test Redis Connection
```bash
docker-compose exec redis redis-cli ping
# Should return: PONG
```

### Test Celery Worker
```bash
docker-compose logs celery_worker
# Should show: [tasks ready]
```

### Test Cache
```python
from django.core.cache import cache
cache.set('test', 'hello', 300)
print(cache.get('test'))  # hello
```

## Common Commands

### Docker
```bash
# Start services
docker-compose up

# Stop services
docker-compose down

# View logs
docker-compose logs -f web

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Django shell
docker-compose exec web python manage.py shell
```

### Django
```bash
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Django shell
python manage.py shell

# Run tests
python manage.py test
```

### Celery
```bash
# Start worker
celery -A taskmaster worker --loglevel=info

# Start beat
celery -A taskmaster beat --loglevel=info

# View active tasks
celery -A taskmaster inspect active
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>
```

### Database Connection Error
- Check PostgreSQL is running: `pg_isready`
- Verify credentials in .env file
- Ensure database exists: `psql -l`

### Redis Connection Error
- Check Redis is running: `redis-cli ping`
- Verify Redis host/port in .env

### Celery Not Processing Tasks
- Check worker is running: `docker-compose logs celery_worker`
- Verify Redis connection
- Check task is registered: `celery -A taskmaster inspect registered`

## Project Features

### Custom User Model
- Email-based authentication
- Extended profile with avatar, bio, etc.
- Automatic profile creation via signals

### Project Management
- Create projects with teams
- Assign roles (Owner, Admin, Member, Viewer)
- Track project progress
- View statistics

### Task System
- Create tasks with subtasks
- Assign to multiple users
- Set priority and due dates
- Track time (estimated vs actual)
- Markdown descriptions
- File attachments
- Comments with replies

### Notifications
- Auto-notifications for task events
- Email notifications (configurable)
- Mark as read/unread
- Filter by type

### Caching
- Redis-based caching
- Cache user/project/task data
- Automatic invalidation
- Session storage

### Async Tasks
- Email sending
- Daily task reminders
- Notification cleanup
- Custom background jobs

## Next Steps

1. **Explore the Code**: Read through models, views, and serializers
2. **Test the APIs**: Use Postman or curl to interact with endpoints
3. **Customize**: Add new features, models, or endpoints
4. **Study Patterns**: Understand caching, signals, and async tasks
5. **Build Frontend**: Create a React/Vue frontend using the API
6. **Deploy**: Learn to deploy to production

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Redis Documentation](https://redis.io/documentation)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## License

This is a learning project. Feel free to use and modify as needed.

## Contributing

This is a learning project, but suggestions are welcome! Feel free to:
- Report issues
- Suggest improvements
- Share your learnings

Happy Learning! 🚀
