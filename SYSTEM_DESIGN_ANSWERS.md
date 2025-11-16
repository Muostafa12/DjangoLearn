# System Design & Distributed Systems Interview Questions - ANSWERS

Comprehensive answers to 40 system design questions with diagrams, examples, and real-world use cases.

---

## Table of Contents
1. [Infrastructure & Networking](#infrastructure--networking)
2. [Architecture Patterns](#architecture-patterns)
3. [Databases & Storage](#databases--storage)
4. [Communication Protocols](#communication-protocols)
5. [Distributed Systems](#distributed-systems)
6. [Security & Authentication](#security--authentication)
7. [Performance & Scalability](#performance--scalability)

---

## Infrastructure & Networking

### 1. What is the difference between API Gateway and Load Balancer?

**API Gateway** is an application layer service that manages, routes, and secures API requests.

**Load Balancer** is a network layer service that distributes traffic across multiple servers.

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT                               │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴────────────────┐
         │                                 │
    ┌────▼─────┐                    ┌─────▼────┐
    │   API    │                    │  LOAD    │
    │ GATEWAY  │                    │ BALANCER │
    └────┬─────┘                    └─────┬────┘
         │                                 │
         │ Features:                       │ Features:
         │ - Authentication                │ - Traffic distribution
         │ - Rate limiting                 │ - Health checks
         │ - Request routing               │ - SSL termination
         │ - Response transformation       │ - Session persistence
         │ - API versioning                │ - Simple routing
         │ - Logging/monitoring            │
         │                                 │
    ┌────┴──────────────┐           ┌─────┴──────────────┐
    │                   │           │                    │
┌───▼───┐  ┌───────┐  ┌▼────┐  ┌───▼───┐  ┌────────┐  ┌▼─────┐
│Auth   │  │Payment│  │User │  │Server1│  │Server2 │  │Server3│
│Service│  │Service│  │Svc  │  │       │  │        │  │       │
└───────┘  └───────┘  └─────┘  └───────┘  └────────┘  └───────┘
```

**API Gateway:**
```python
# Example: API Gateway routing
from flask import Flask, request
import requests

app = Flask(__name__)

# API Gateway handles routing, auth, rate limiting
@app.route('/api/<service>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def gateway(service, path):
    # 1. Authentication
    token = request.headers.get('Authorization')
    if not verify_token(token):
        return {'error': 'Unauthorized'}, 401

    # 2. Rate limiting
    if is_rate_limited(token):
        return {'error': 'Too many requests'}, 429

    # 3. Route to appropriate service
    service_urls = {
        'users': 'http://user-service:8001',
        'products': 'http://product-service:8002',
        'orders': 'http://order-service:8003',
    }

    if service not in service_urls:
        return {'error': 'Service not found'}, 404

    # 4. Forward request
    url = f"{service_urls[service]}/{path}"
    response = requests.request(
        method=request.method,
        url=url,
        headers=request.headers,
        data=request.get_data()
    )

    # 5. Transform response (if needed)
    return response.json(), response.status_code
```

**Load Balancer:**
```python
# Example: Simple Round Robin Load Balancer
class LoadBalancer:
    def __init__(self, servers):
        self.servers = servers
        self.current = 0

    def get_next_server(self):
        # Round robin algorithm
        server = self.servers[self.current]
        self.current = (self.current + 1) % len(self.servers)
        return server

    def health_check(self, server):
        try:
            response = requests.get(f"{server}/health", timeout=2)
            return response.status_code == 200
        except:
            return False

    def get_healthy_servers(self):
        return [s for s in self.servers if self.health_check(s)]

# Usage
lb = LoadBalancer([
    'http://server1:8000',
    'http://server2:8000',
    'http://server3:8000'
])

# Distribute request
server = lb.get_next_server()
response = requests.get(f"{server}/api/data")
```

**Key Differences:**

| Feature | API Gateway | Load Balancer |
|---------|-------------|---------------|
| Layer | Application (L7) | Network/Transport (L4/L7) |
| Purpose | API management | Traffic distribution |
| Authentication | Yes | No |
| Rate Limiting | Yes | Basic |
| Request Transformation | Yes | No |
| Protocol Translation | Yes (REST→gRPC) | No |
| Routing | Complex (path-based) | Simple (IP-based) |
| Use Case | Microservices API | Server clustering |

**Real-world Example:**
```
TaskMaster Project:

┌─────────┐
│ Client  │
└────┬────┘
     │
┌────▼────────┐
│ API Gateway │ ← Kong, AWS API Gateway, Azure API Management
├─────────────┤
│ - Auth JWT  │
│ - Rate limit│
│ - /api/v1/  │
└────┬────────┘
     │
┌────▼─────────┐
│Load Balancer │ ← Nginx, HAProxy, AWS ELB
├──────────────┤
│- Round robin │
│- Health check│
└───┬──────────┘
    │
    ├─────────┬─────────┐
    │         │         │
┌───▼───┐ ┌──▼────┐ ┌──▼────┐
│Django1│ │Django2│ │Django3│
└───────┘ └───────┘ └───────┘
```

---

### 2. What is the difference between Reverse Proxy and Forward Proxy?

**Forward Proxy** sits between clients and the internet (client-side).
**Reverse Proxy** sits between the internet and servers (server-side).

```
FORWARD PROXY (Client → Proxy → Internet)
┌─────────┐     ┌─────────┐     ┌──────────┐
│ Client1 │────▶│         │────▶│          │
├─────────┤     │ Forward │     │ Internet │
│ Client2 │────▶│  Proxy  │────▶│ (Google, │
├─────────┤     │         │     │  AWS)    │
│ Client3 │────▶│         │────▶│          │
└─────────┘     └─────────┘     └──────────┘
                    │
                    └─ Hides client identity
                    └─ Caching
                    └─ Content filtering
                    └─ Bypass geo-restrictions

REVERSE PROXY (Internet → Proxy → Servers)
┌──────────┐     ┌─────────┐     ┌─────────┐
│          │     │         │     │ Server1 │
│ Internet │────▶│ Reverse │────▶├─────────┤
│ Clients  │     │  Proxy  │     │ Server2 │
│          │     │ (Nginx) │────▶├─────────┤
│          │     │         │     │ Server3 │
└──────────┘     └─────────┘     └─────────┘
                    │
                    └─ Hides server identity
                    └─ Load balancing
                    └─ SSL termination
                    └─ Caching
                    └─ Compression
```

**Forward Proxy Example (Squid):**
```bash
# Client configuration
export HTTP_PROXY="http://proxy.company.com:3128"
export HTTPS_PROXY="http://proxy.company.com:3128"

# Now all requests go through proxy
curl https://google.com  # Goes through proxy

# Use cases:
# 1. Corporate networks (monitor/filter employee traffic)
# 2. Privacy (hide client IP)
# 3. Access control (block certain websites)
# 4. Caching (save bandwidth)
```

**Reverse Proxy Example (Nginx):**
```nginx
# /etc/nginx/nginx.conf
http {
    upstream django_app {
        server 127.0.0.1:8001;
        server 127.0.0.1:8002;
        server 127.0.0.1:8003;
    }

    server {
        listen 80;
        server_name taskmaster.com;

        # SSL termination
        listen 443 ssl;
        ssl_certificate /path/to/cert.pem;
        ssl_certificate_key /path/to/key.pem;

        # Caching
        proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m;

        location / {
            # Reverse proxy to Django
            proxy_pass http://django_app;

            # Headers
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Caching
            proxy_cache my_cache;
            proxy_cache_valid 200 60m;
        }

        location /static/ {
            alias /var/www/static/;
            expires 30d;
        }
    }
}
```

**Comparison:**

| Feature | Forward Proxy | Reverse Proxy |
|---------|---------------|---------------|
| Position | Client-side | Server-side |
| Purpose | Protect clients | Protect servers |
| Hides | Client IP | Server IP |
| Used by | Employees, users | Server administrators |
| Examples | Squid, TinyProxy | Nginx, HAProxy, Varnish |
| Common Uses | Content filtering, Privacy | Load balancing, SSL, Caching |

**Django Configuration with Reverse Proxy:**
```python
# settings.py
# Trust proxy headers
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Get real client IP
# In middleware or view:
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
```

---

### 3. What is the difference between Horizontal scaling and Vertical scaling?

**Vertical Scaling (Scale Up):** Add more power to existing server (CPU, RAM, Disk)
**Horizontal Scaling (Scale Out):** Add more servers

```
VERTICAL SCALING (Scale Up)
Before:                    After:
┌─────────────┐           ┌─────────────┐
│   Server    │           │   Server    │
│             │  ──────▶  │             │
│ 4 CPU       │           │ 16 CPU      │
│ 8 GB RAM    │           │ 64 GB RAM   │
│ 100 GB Disk │           │ 1 TB Disk   │
└─────────────┘           └─────────────┘

HORIZONTAL SCALING (Scale Out)
Before:                    After:
┌─────────────┐           ┌──────┐ ┌──────┐ ┌──────┐
│   Server    │           │Server│ │Server│ │Server│
│             │  ──────▶  │  1   │ │  2   │ │  3   │
│ 4 CPU       │           │4 CPU │ │4 CPU │ │4 CPU │
│ 8 GB RAM    │           │8 GB  │ │8 GB  │ │8 GB  │
│ 100 GB Disk │           │100 GB│ │100 GB│ │100 GB│
└─────────────┘           └──────┘ └──────┘ └──────┘
                                 ▲
                          Load Balancer
```

**Vertical Scaling Example:**
```bash
# Before: AWS EC2 t2.medium
# - 2 vCPUs
# - 4 GB RAM
# - $0.0464/hour

# Upgrade to t2.2xlarge
# - 8 vCPUs
# - 32 GB RAM
# - $0.3712/hour

# Pros:
# ✓ Simple (no code changes)
# ✓ No distributed system complexity
# ✓ Easier data consistency

# Cons:
# ✗ Single point of failure
# ✗ Downtime during upgrade
# ✗ Hardware limits (can't scale infinitely)
# ✗ Expensive at scale
```

**Horizontal Scaling Example:**
```python
# Django with horizontal scaling

# 1. Stateless application (required for horizontal scaling)
# settings.py
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'  # Not file-based
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis-server:6379/0',
    }
}

# 2. Shared database (all instances connect to same DB)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': 'postgres-server.example.com',  # Shared
        'PORT': '5432',
    }
}

# 3. Shared file storage (for media files)
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = 'taskmaster-media'

# 4. Celery for background tasks (multiple workers)
CELERY_BROKER_URL = 'redis://redis-server:6379/0'

# Docker Compose for horizontal scaling:
# docker-compose.yml
services:
  web:
    image: taskmaster-django
    deploy:
      replicas: 3  # 3 Django instances
    environment:
      - DATABASE_URL=postgresql://db:5432/taskmaster
      - REDIS_URL=redis://redis:6379/0

  nginx:
    image: nginx
    ports:
      - "80:80"
    depends_on:
      - web

# Kubernetes (auto-scaling)
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: taskmaster-web
spec:
  replicas: 3  # Start with 3 instances
  template:
    spec:
      containers:
      - name: django
        image: taskmaster:latest
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: taskmaster-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: taskmaster-web
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70  # Scale up if CPU > 70%
```

**Comparison:**

| Aspect | Vertical Scaling | Horizontal Scaling |
|--------|------------------|-------------------|
| Cost | Expensive at scale | More cost-effective |
| Limit | Hardware maximum | Nearly unlimited |
| Complexity | Simple | Complex (distributed system) |
| Downtime | Required | Zero-downtime possible |
| Failure | Single point | Fault-tolerant |
| Data Consistency | Easy | Challenging |
| Use Case | Databases, legacy apps | Web apps, microservices |
| Examples | Upgrading server | Adding more servers |

**When to use which:**

**Vertical Scaling:**
```python
# Good for:
# - Databases (PostgreSQL, MySQL)
# - Legacy monolithic applications
# - Applications requiring strong consistency
# - Quick temporary fixes

# Example: Database
# Instead of sharding (horizontal), upgrade to larger instance
# - Easier maintenance
# - ACID guarantees
# - No distributed queries
```

**Horizontal Scaling:**
```python
# Good for:
# - Stateless web applications
# - Microservices
# - High availability requirements
# - Handling massive traffic spikes

# Example: Web tier (Django)
# Add more Django instances behind load balancer
# - Handle more concurrent requests
# - Fault tolerance (one fails, others continue)
# - Cost-effective
```

**Real-world: TaskMaster Scaling Strategy**
```
┌──────────────────────────────────────────────────────────┐
│                   Load Balancer                          │
└─────────────────────┬────────────────────────────────────┘
                      │
          ┌───────────┴────────────┐
          │                        │
┌─────────▼─────────┐    ┌─────────▼─────────┐
│  Django Instance  │    │  Django Instance  │  ← Horizontal
│    (Stateless)    │    │    (Stateless)    │
└─────────┬─────────┘    └─────────┬─────────┘
          │                        │
          └───────────┬────────────┘
                      │
          ┌───────────▼────────────┐
          │   PostgreSQL Server    │  ← Vertical (upgrade RAM/CPU)
          │   (Stateful)           │
          └────────────────────────┘

          ┌────────────────────────┐
          │   Redis Cache          │  ← Horizontal (Redis Cluster)
          └────────────────────────┘
```

**Auto-scaling Script:**
```python
import boto3
import time

def auto_scale(metric_threshold=70, check_interval=60):
    """Auto-scale EC2 instances based on CPU usage"""
    cloudwatch = boto3.client('cloudwatch')
    autoscaling = boto3.client('autoscaling')

    while True:
        # Get average CPU usage
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'AutoScalingGroupName', 'Value': 'taskmaster-asg'}],
            StartTime=time.time() - 300,
            EndTime=time.time(),
            Period=300,
            Statistics=['Average']
        )

        cpu_avg = response['Datapoints'][0]['Average']

        if cpu_avg > metric_threshold:
            # Scale out
            autoscaling.set_desired_capacity(
                AutoScalingGroupName='taskmaster-asg',
                DesiredCapacity=current_capacity + 1
            )
            print(f"Scaling out: CPU {cpu_avg}% > {metric_threshold}%")

        elif cpu_avg < 30 and current_capacity > 2:
            # Scale in
            autoscaling.set_desired_capacity(
                AutoScalingGroupName='taskmaster-asg',
                DesiredCapacity=current_capacity - 1
            )
            print(f"Scaling in: CPU {cpu_avg}% < 30%")

        time.sleep(check_interval)
```

---

### 4. What is the difference between Microservices and Monolithic architecture?

**Monolithic:** Single large application with all features in one codebase.
**Microservices:** Multiple small, independent services communicating via APIs.

```
MONOLITHIC ARCHITECTURE
┌─────────────────────────────────────────┐
│         Single Application              │
│  ┌────────────────────────────────┐    │
│  │         Web UI Layer           │    │
│  ├────────────────────────────────┤    │
│  │      Business Logic Layer      │    │
│  │  ┌──────┐ ┌──────┐ ┌────────┐ │    │
│  │  │Users │ │Tasks │ │Projects│ │    │
│  │  └──────┘ └──────┘ └────────┘ │    │
│  ├────────────────────────────────┤    │
│  │       Data Access Layer        │    │
│  └────────────────────────────────┘    │
│                  │                      │
│         ┌────────▼─────────┐           │
│         │  Single Database │           │
│         └──────────────────┘           │
└─────────────────────────────────────────┘

MICROSERVICES ARCHITECTURE
┌──────────┐   ┌──────────┐   ┌──────────┐
│  User    │   │  Task    │   │ Project  │
│ Service  │   │ Service  │   │ Service  │
│          │   │          │   │          │
│ ┌──────┐ │   │ ┌──────┐ │   │ ┌──────┐ │
│ │  DB  │ │   │ │  DB  │ │   │ │  DB  │ │
│ └──────┘ │   │ └──────┘ │   │ └──────┘ │
└────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │
     └──────────────┴──────────────┘
              ▲
         API Gateway
```

**Monolithic Example (Current TaskMaster):**
```python
# Single Django project with multiple apps
taskmaster/
├── taskmaster/          # Main project
│   ├── settings.py      # Single config
│   ├── urls.py          # All routes
│   └── wsgi.py
├── accounts/            # User management
├── tasks/               # Task management
├── projects/            # Project management
└── notifications/       # Notifications

# All deployed together
# Single database
# Shared dependencies
# Deployed as one unit

# Pros:
# ✓ Simple development
# ✓ Easy debugging
# ✓ No network latency between components
# ✓ ACID transactions
# ✓ Simple deployment

# Cons:
# ✗ Tight coupling
# ✗ Scaling entire app for one feature
# ✗ Technology lock-in (all Python/Django)
# ✗ Longer deployment times
# ✗ Risk of cascading failures
```

**Microservices Example (Refactored TaskMaster):**
```python
# User Service (FastAPI - Python)
# user-service/main.py
from fastapi import FastAPI
from sqlalchemy import create_engine

app = FastAPI()
db = create_engine('postgresql://localhost/users_db')

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # Only handles user data
    return {"id": user_id, "name": "John"}

@app.post("/users/")
async def create_user(user: UserSchema):
    # User creation logic
    return user

# ==========================================

# Task Service (Node.js - JavaScript)
# task-service/index.js
const express = require('express');
const mongoose = require('mongoose');

const app = express();
mongoose.connect('mongodb://localhost/tasks_db');

app.get('/tasks/:id', async (req, res) => {
    // Only handles task data
    const task = await Task.findById(req.params.id);

    // Call User Service for user details
    const userResponse = await fetch(`http://user-service:8000/users/${task.owner_id}`);
    const user = await userResponse.json();

    res.json({ ...task, owner: user });
});

// ==========================================

# Notification Service (Go)
# notification-service/main.go
package main

import (
    "github.com/gin-gonic/gin"
)

func main() {
    r := gin.Default()

    r.POST("/notifications/send", func(c *gin.Context) {
        // Send notification
        // Listen to events from other services
    })

    r.Run(":8002")
}

# ==========================================

# API Gateway (Kong, AWS API Gateway, or custom)
# docker-compose.yml
services:
  api-gateway:
    image: kong
    ports:
      - "8000:8000"
    environment:
      - KONG_DATABASE=postgres

  user-service:
    build: ./user-service
    environment:
      - DATABASE_URL=postgresql://users_db

  task-service:
    build: ./task-service
    environment:
      - DATABASE_URL=mongodb://tasks_db

  notification-service:
    build: ./notification-service
    environment:
      - RABBITMQ_URL=amqp://rabbitmq
```

**Comparison:**

| Aspect | Monolithic | Microservices |
|--------|------------|---------------|
| **Codebase** | Single large codebase | Multiple small codebases |
| **Database** | Shared database | Database per service |
| **Deployment** | Deploy entire app | Deploy services independently |
| **Scaling** | Scale entire app | Scale services independently |
| **Technology** | Single stack (e.g., Django) | Polyglot (Python, Node, Go) |
| **Development** | Single team | Multiple teams |
| **Testing** | Test entire app | Test each service |
| **Communication** | In-process | Network (HTTP, gRPC, messaging) |
| **Transactions** | ACID | Eventual consistency |
| **Failure Impact** | Entire app down | Isolated to service |
| **Complexity** | Low | High |
| **Learning Curve** | Easy | Steep |

**Communication Between Microservices:**

```python
# 1. Synchronous (REST API)
import requests

class TaskService:
    def create_task(self, task_data):
        # Create task
        task = Task.objects.create(**task_data)

        # Call User Service to get user details
        user_response = requests.get(
            f"http://user-service:8000/users/{task_data['owner_id']}"
        )
        user = user_response.json()

        # Call Notification Service
        requests.post(
            "http://notification-service:8002/notifications/send",
            json={
                "user_id": user['id'],
                "message": f"Task '{task.title}' created"
            }
        )

        return task

# 2. Asynchronous (Message Queue)
import pika

class TaskService:
    def create_task(self, task_data):
        task = Task.objects.create(**task_data)

        # Publish event to RabbitMQ
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('rabbitmq')
        )
        channel = connection.channel()

        channel.basic_publish(
            exchange='task_events',
            routing_key='task.created',
            body=json.dumps({
                'task_id': task.id,
                'owner_id': task.owner_id,
                'title': task.title
            })
        )

        connection.close()
        return task

# Notification Service listens to events
class NotificationService:
    def start_listening(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('rabbitmq')
        )
        channel = connection.channel()

        def callback(ch, method, properties, body):
            event = json.loads(body)
            self.send_notification(
                user_id=event['owner_id'],
                message=f"Task '{event['title']}' created"
            )

        channel.basic_consume(
            queue='notification_queue',
            on_message_callback=callback,
            auto_ack=True
        )

        channel.start_consuming()

# 3. Event-Driven (Kafka)
from kafka import KafkaProducer, KafkaConsumer

producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Task Service publishes event
producer.send('task-events', {
    'event': 'task.created',
    'data': {'task_id': task.id, 'title': task.title}
})

# Notification Service consumes events
consumer = KafkaConsumer(
    'task-events',
    bootstrap_servers='kafka:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    event = message.value
    if event['event'] == 'task.created':
        send_notification(event['data'])
```

**When to use which:**

**Use Monolithic when:**
- Small team (< 10 developers)
- Simple application
- Tight deadlines
- Limited DevOps expertise
- Strong consistency required
- Early-stage startup

**Use Microservices when:**
- Large organization (multiple teams)
- Complex domain
- Different scaling requirements per feature
- Need technology diversity
- Independent deployment cycles
- High availability critical

**Migration Strategy (Monolith → Microservices):**

```python
# Step 1: Extract non-critical service first
# Start with Notification Service (least coupled)

# Step 2: Strangler Pattern
class TaskView(APIView):
    def create(self, request):
        # Create task in monolith
        task = Task.objects.create(**request.data)

        # Also send to new microservice (gradually migrate)
        try:
            requests.post(
                "http://notification-service:8002/notify",
                json={'task_id': task.id}
            )
        except Exception as e:
            # Log but don't fail (backward compatibility)
            logger.error(f"Notification service error: {e}")

        return Response(TaskSerializer(task).data)

# Step 3: Gradually move features
# Move one feature at a time
# Keep backward compatibility
# Monitor performance

# Step 4: Database separation
# Extract notification data to separate DB
# Use database views/replication during transition

# Step 5: Complete migration
# Remove old code
# Full microservice
```

**Challenges & Solutions:**

```python
# Challenge 1: Distributed Transactions
# Problem: Task creation + Project update must be atomic
# Solution: Saga Pattern

# Orchestration-based Saga
class CreateTaskSaga:
    def execute(self, task_data):
        # Step 1: Create task
        task = requests.post("http://task-service/tasks", json=task_data)

        try:
            # Step 2: Update project
            requests.put(
                f"http://project-service/projects/{task_data['project_id']}/task-count",
                json={'increment': 1}
            )

            # Step 3: Send notification
            requests.post(
                "http://notification-service/notify",
                json={'task_id': task['id']}
            )
        except Exception as e:
            # Compensating transaction (rollback)
            requests.delete(f"http://task-service/tasks/{task['id']}")
            raise

# Challenge 2: Data Consistency
# Solution: Event Sourcing
class TaskEventStore:
    def create_task(self, task_data):
        # Store event instead of state
        event = Event(
            type='TaskCreated',
            data=task_data,
            timestamp=timezone.now()
        )
        event.save()

        # Publish event
        publish_event(event)

        # Services build their own view of data
        return event

# Challenge 3: Service Discovery
# Solution: Use service mesh (Istio, Linkerd) or Consul

import consul

def get_service_url(service_name):
    c = consul.Consul()
    services = c.health.service(service_name, passing=True)[1]
    if services:
        service = services[0]
        return f"http://{service['Service']['Address']}:{service['Service']['Port']}"
    raise ServiceNotFoundError(service_name)

# Usage
user_service_url = get_service_url('user-service')
response = requests.get(f"{user_service_url}/users/123")
```

---

## Architecture Patterns

### 5. What is the difference between vertical and horizontal partitioning?

**Vertical Partitioning:** Split table by columns (different tables)
**Horizontal Partitioning (Sharding):** Split table by rows (different databases)

```
VERTICAL PARTITIONING (Split Columns)

Original Table: Users
┌────┬─────────┬──────┬──────────┬─────┬──────────┬─────────┐
│ ID │  Name   │Email │ Password │ Bio │ Avatar   │ Settings│
├────┼─────────┼──────┼──────────┼─────┼──────────┼─────────┤
│ 1  │ Alice   │ a@.. │ hash123  │ ... │ img1.jpg │ {...}   │
│ 2  │ Bob     │ b@.. │ hash456  │ ... │ img2.jpg │ {...}   │
└────┴─────────┴──────┴──────────┴─────┴──────────┴─────────┘

After Vertical Partitioning:

Table 1: User_Basic (frequently accessed)
┌────┬─────────┬──────┬──────────┐
│ ID │  Name   │Email │ Password │
├────┼─────────┼──────┼──────────┤
│ 1  │ Alice   │ a@.. │ hash123  │
│ 2  │ Bob     │ b@.. │ hash456  │
└────┴─────────┴──────┴──────────┘

Table 2: User_Profile (rarely accessed)
┌────┬─────┬──────────┬─────────┐
│ ID │ Bio │ Avatar   │ Settings│
├────┼─────┼──────────┼─────────┤
│ 1  │ ... │ img1.jpg │ {...}   │
│ 2  │ ... │ img2.jpg │ {...}   │
└────┴─────┴──────────┴─────────┘

HORIZONTAL PARTITIONING / SHARDING (Split Rows)

Original Table: Users (10M rows)
┌────┬───────┬────────┬──────┬────────┐
│ ID │ Name  │ Email  │ City │ Country│
├────┼───────┼────────┼──────┼────────┤
│ 1  │ Alice │ a@..   │ NYC  │ USA    │
│ 2  │ Bob   │ b@..   │ LON  │ UK     │
│ 3  │ Carol │ c@..   │ TOK  │ JP     │
│... │  ...  │  ...   │ ...  │  ...   │
└────┴───────┴────────┴──────┴────────┘

After Horizontal Partitioning:

Shard 1 (USA Users - 5M rows)
┌────┬───────┬────────┬──────┬────────┐
│ ID │ Name  │ Email  │ City │ Country│
├────┼───────┼────────┼──────┼────────┤
│ 1  │ Alice │ a@..   │ NYC  │ USA    │
└────┴───────┴────────┴──────┴────────┘

Shard 2 (EU Users - 3M rows)
┌────┬───────┬────────┬──────┬────────┐
│ ID │ Name  │ Email  │ City │ Country│
├────┼───────┼────────┼──────┼────────┤
│ 2  │ Bob   │ b@..   │ LON  │ UK     │
└────┴───────┴────────┴──────┴────────┘

Shard 3 (APAC Users - 2M rows)
┌────┬───────┬────────┬──────┬────────┐
│ ID │ Name  │ Email  │ City │ Country│
├────┼───────┼────────┼──────┼────────┤
│ 3  │ Carol │ c@..   │ TOK  │ JP     │
└────┴───────┴────────┴──────┴────────┘
```

**Vertical Partitioning Example:**

```python
# Django models - Vertical Partitioning

# Before: Single large User table
class User(models.Model):
    # Frequently accessed
    username = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=128)

    # Rarely accessed (large fields)
    bio = models.TextField()  # Large text
    avatar = models.ImageField()  # Large binary
    preferences = models.JSONField()  # Complex data
    activity_log = models.TextField()  # Large text

# After: Split into multiple tables
class User(models.Model):
    # Frequently accessed - kept in main table
    username = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=128)

class UserProfile(models.Model):
    # Rarely accessed - separate table
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    avatar = models.ImageField()
    preferences = models.JSONField()

class UserActivityLog(models.Model):
    # Large, write-heavy - separate table
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_log = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# Benefits:
# 1. Faster queries on User table (smaller row size)
# 2. Better caching (hot data separate from cold data)
# 3. Different storage engines (SSD for User, HDD for logs)

# Usage:
user = User.objects.get(id=1)  # Fast, small query
if need_profile:
    profile = user.userprofile  # Only load when needed
```

**Horizontal Partitioning (Sharding) Example:**

```python
# Sharding Strategy 1: Range-based (by user ID)
class ShardRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'users':
            user_id = hints.get('instance').id if hints.get('instance') else None
            if user_id:
                return self.get_shard(user_id)
        return 'default'

    def get_shard(self, user_id):
        # Range-based sharding
        if user_id < 1000000:
            return 'shard_1'
        elif user_id < 2000000:
            return 'shard_2'
        else:
            return 'shard_3'

# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'main_db',
    },
    'shard_1': {  # Users 0 - 999,999
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'users_shard_1',
        'HOST': 'db1.example.com',
    },
    'shard_2': {  # Users 1M - 1,999,999
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'users_shard_2',
        'HOST': 'db2.example.com',
    },
    'shard_3': {  # Users 2M+
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'users_shard_3',
        'HOST': 'db3.example.com',
    },
}

DATABASE_ROUTERS = ['path.to.ShardRouter']

# Sharding Strategy 2: Hash-based (by user ID)
import hashlib

def get_shard_by_hash(user_id, num_shards=4):
    # Consistent distribution
    hash_value = int(hashlib.md5(str(user_id).encode()).hexdigest(), 16)
    shard_num = hash_value % num_shards
    return f'shard_{shard_num}'

# Sharding Strategy 3: Geography-based
def get_shard_by_location(country):
    geography_shards = {
        'USA': 'shard_us',
        'UK': 'shard_eu',
        'IN': 'shard_apac',
    }
    return geography_shards.get(country, 'shard_default')

# Sharding Strategy 4: Entity-based (TaskMaster example)
# Shard by project_id (all tasks for a project in same shard)
class ProjectShardRouter:
    def db_for_read(self, model, **hints):
        if model._meta.model_name == 'task':
            instance = hints.get('instance')
            if instance and instance.project_id:
                return f'project_shard_{instance.project_id % 10}'
        return 'default'

# Query across shards (complex!)
def get_all_users_count():
    total = 0
    for shard in ['shard_1', 'shard_2', 'shard_3']:
        total += User.objects.using(shard).count()
    return total

# Join across shards (difficult!)
def get_user_with_orders(user_id):
    # User in one shard, Orders in another
    shard = get_shard_by_hash(user_id)
    user = User.objects.using(shard).get(id=user_id)

    # Orders might be in different shard
    orders = []
    for order_shard in ['shard_1', 'shard_2', 'shard_3']:
        orders.extend(
            Order.objects.using(order_shard).filter(user_id=user_id)
        )

    return {'user': user, 'orders': orders}
```

**Comparison:**

| Aspect | Vertical Partitioning | Horizontal Partitioning (Sharding) |
|--------|----------------------|-----------------------------------|
| **Splits** | By columns | By rows |
| **Purpose** | Separate hot/cold data | Distribute load |
| **Complexity** | Low | High |
| **Scalability** | Limited | High |
| **Query Complexity** | Simple (JOINs work) | Complex (cross-shard queries) |
| **Use Case** | Large columns, different access patterns | Large tables, high write load |
| **Implementation** | OneToOne relationships | Multiple databases |
| **Transactions** | Easy (same DB) | Difficult (distributed) |

**Real-world Example: TaskMaster Partitioning**

```python
# Vertical Partitioning: Split Task model
class Task(models.Model):
    # Frequently accessed
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20)
    priority = models.CharField(max_length=20)
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

class TaskDetails(models.Model):
    # Rarely accessed, large fields
    task = models.OneToOneField(Task, on_delete=models.CASCADE)
    description = models.TextField()  # Large
    detailed_notes = models.TextField()  # Large
    custom_fields = models.JSONField()  # Complex

class TaskAttachment(models.Model):
    # Separate table for files
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    file = models.FileField()  # Large binary
    uploaded_at = models.DateTimeField(auto_now_add=True)

# Horizontal Partitioning: Shard by project
# project_id 1-100 → db_shard_1
# project_id 101-200 → db_shard_2
# etc.

# settings.py
DATABASES = {
    'default': {...},
    'tasks_shard_1': {'NAME': 'tasks_db_1', 'HOST': 'db1.example.com'},
    'tasks_shard_2': {'NAME': 'tasks_db_2', 'HOST': 'db2.example.com'},
    'tasks_shard_3': {'NAME': 'tasks_db_3', 'HOST': 'db3.example.com'},
}

class TaskShardRouter:
    def db_for_read(self, model, **hints):
        if model._meta.model_name == 'task':
            project_id = hints.get('project_id')
            if project_id:
                shard_num = ((project_id - 1) // 100) + 1
                return f'tasks_shard_{shard_num}'
        return 'default'

    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)

# Usage
from django.db import router

# Create task in appropriate shard
task = Task(title="Fix bug", project_id=150)
db = router.db_for_write(Task, project_id=150)  # tasks_shard_2
task.save(using=db)

# Query tasks for project
project_id = 150
db = router.db_for_read(Task, project_id=project_id)
tasks = Task.objects.using(db).filter(project_id=project_id)
```

**Challenges and Solutions:**

```python
# Challenge 1: Auto-increment IDs across shards
# Problem: ID collision (shard_1 has ID=1, shard_2 also has ID=1)

# Solution 1: UUID
import uuid

class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

# Solution 2: Snowflake ID (Twitter's approach)
def generate_snowflake_id(shard_id):
    timestamp = int(time.time() * 1000)  # 41 bits
    shard = shard_id  # 10 bits
    sequence = get_sequence()  # 12 bits
    return (timestamp << 22) | (shard << 12) | sequence

# Challenge 2: Cross-shard queries
# Problem: Get all tasks for user (tasks spread across shards)

# Solution: Query all shards and merge
def get_user_tasks(user_id):
    all_tasks = []
    for shard in ['shard_1', 'shard_2', 'shard_3']:
        tasks = Task.objects.using(shard).filter(
            assignees__id=user_id
        )
        all_tasks.extend(tasks)

    # Sort and paginate in application layer
    all_tasks.sort(key=lambda t: t.created_at, reverse=True)
    return all_tasks[:20]

# Challenge 3: Rebalancing shards
# Problem: Shard 1 has 80% data, Shard 2 has 20%

# Solution: Virtual shards (consistent hashing)
class ConsistentHashRing:
    def __init__(self, nodes, virtual_nodes=150):
        self.ring = {}
        self.sorted_keys = []

        for node in nodes:
            for i in range(virtual_nodes):
                key = hashlib.md5(f"{node}:{i}".encode()).hexdigest()
                self.ring[key] = node

        self.sorted_keys = sorted(self.ring.keys())

    def get_node(self, key):
        hash_key = hashlib.md5(str(key).encode()).hexdigest()
        for ring_key in self.sorted_keys:
            if hash_key <= ring_key:
                return self.ring[ring_key]
        return self.ring[self.sorted_keys[0]]

# Usage
ring = ConsistentHashRing(['shard_1', 'shard_2', 'shard_3'])
shard = ring.get_node(user_id)  # Evenly distributed
```

---

### 6. What is Rate Limiter? How does it work?

A **Rate Limiter** controls the number of requests a client can make in a time window, preventing abuse and ensuring fair usage.

```
Rate Limiter Flow:
┌────────┐
│ Client │
└───┬────┘
    │ Request
    ▼
┌────────────────┐
│  Rate Limiter  │ ← Check: Has client exceeded limit?
├────────────────┤
│ Rules:         │
│ 100 req/minute │
│ 1000 req/hour  │
│ 10000 req/day  │
└───┬────────┬───┘
    │        │
    │ Yes    │ No
    │        │
┌───▼────┐   │
│ REJECT │   │
│ 429    │   │
│ Error  │   │
└────────┘   │
             │
        ┌────▼────┐
        │ ALLOW   │
        │ Process │
        │ Request │
        └─────────┘
```

**Algorithm 1: Token Bucket**

```python
import time
import redis

class TokenBucketRateLimiter:
    """
    Token Bucket Algorithm:
    - Bucket has max capacity of tokens
    - Tokens added at fixed rate
    - Each request consumes 1 token
    - If no tokens, request rejected
    """

    def __init__(self, capacity, refill_rate):
        """
        capacity: Max tokens in bucket
        refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.redis_client = redis.Redis(host='localhost', port=6379)

    def is_allowed(self, user_id):
        key = f"rate_limit:{user_id}"

        # Get current bucket state
        pipe = self.redis_client.pipeline()
        pipe.get(f"{key}:tokens")
        pipe.get(f"{key}:last_refill")
        tokens, last_refill = pipe.execute()

        now = time.time()

        # Initialize if first request
        if tokens is None:
            tokens = self.capacity
            last_refill = now
        else:
            tokens = float(tokens)
            last_refill = float(last_refill)

        # Refill tokens based on elapsed time
        elapsed = now - last_refill
        tokens_to_add = elapsed * self.refill_rate
        tokens = min(self.capacity, tokens + tokens_to_add)

        # Check if request can be allowed
        if tokens >= 1:
            tokens -= 1

            # Update Redis
            pipe = self.redis_client.pipeline()
            pipe.set(f"{key}:tokens", tokens)
            pipe.set(f"{key}:last_refill", now)
            pipe.expire(f"{key}:tokens", 3600)  # 1 hour expiry
            pipe.expire(f"{key}:last_refill", 3600)
            pipe.execute()

            return True
        else:
            return False

# Usage
limiter = TokenBucketRateLimiter(capacity=100, refill_rate=10)  # 10 tokens/sec

for i in range(150):
    if limiter.is_allowed(user_id=123):
        print(f"Request {i}: Allowed")
    else:
        print(f"Request {i}: Rate limited!")
```

**Algorithm 2: Leaky Bucket**

```python
class LeakyBucketRateLimiter:
    """
    Leaky Bucket Algorithm:
    - Requests enter bucket (queue)
    - Processed at constant rate (leak)
    - If bucket full, new requests rejected
    """

    def __init__(self, capacity, leak_rate):
        self.capacity = capacity
        self.leak_rate = leak_rate  # Requests processed per second
        self.redis_client = redis.Redis()

    def is_allowed(self, user_id):
        key = f"leaky_bucket:{user_id}"

        # Get current queue size and last leak time
        pipe = self.redis_client.pipeline()
        pipe.get(f"{key}:size")
        pipe.get(f"{key}:last_leak")
        queue_size, last_leak = pipe.execute()

        now = time.time()

        if queue_size is None:
            queue_size = 0
            last_leak = now
        else:
            queue_size = int(queue_size)
            last_leak = float(last_leak)

        # Leak (process) requests
        elapsed = now - last_leak
        leaked = int(elapsed * self.leak_rate)
        queue_size = max(0, queue_size - leaked)

        # Check if bucket has space
        if queue_size < self.capacity:
            queue_size += 1

            # Update Redis
            pipe = self.redis_client.pipeline()
            pipe.set(f"{key}:size", queue_size)
            pipe.set(f"{key}:last_leak", now)
            pipe.expire(f"{key}:size", 3600)
            pipe.expire(f"{key}:last_leak", 3600)
            pipe.execute()

            return True
        else:
            return False
```

**Algorithm 3: Fixed Window Counter**

```python
class FixedWindowRateLimiter:
    """
    Fixed Window Counter:
    - Count requests in fixed time windows
    - Window resets after duration
    - Simple but has edge case (burst at window boundary)
    """

    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.redis_client = redis.Redis()

    def is_allowed(self, user_id):
        now = time.time()
        window_key = int(now // self.window_seconds)
        key = f"fixed_window:{user_id}:{window_key}"

        # Increment counter
        count = self.redis_client.incr(key)

        if count == 1:
            # Set expiry on first request in window
            self.redis_client.expire(key, self.window_seconds)

        return count <= self.max_requests

# Usage
limiter = FixedWindowRateLimiter(max_requests=100, window_seconds=60)

# Problem: Burst at window boundary
# Window 1 (0-60s): 100 requests at t=59s
# Window 2 (60-120s): 100 requests at t=60s
# → 200 requests in 1 second!
```

**Algorithm 4: Sliding Window Log**

```python
class SlidingWindowLogRateLimiter:
    """
    Sliding Window Log:
    - Store timestamp of each request
    - Count requests in sliding window
    - Accurate but memory-intensive
    """

    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.redis_client = redis.Redis()

    def is_allowed(self, user_id):
        key = f"sliding_log:{user_id}"
        now = time.time()
        window_start = now - self.window_seconds

        # Remove old entries
        self.redis_client.zremrangebyscore(key, 0, window_start)

        # Count requests in current window
        count = self.redis_client.zcard(key)

        if count < self.max_requests:
            # Add current request timestamp
            self.redis_client.zadd(key, {str(now): now})
            self.redis_client.expire(key, self.window_seconds)
            return True
        else:
            return False
```

**Algorithm 5: Sliding Window Counter (Best Trade-off)**

```python
class SlidingWindowCounterRateLimiter:
    """
    Sliding Window Counter:
    - Combines fixed window + sliding window
    - Memory efficient + more accurate
    - Used by most production systems
    """

    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.redis_client = redis.Redis()

    def is_allowed(self, user_id):
        now = time.time()
        current_window = int(now // self.window_seconds)
        previous_window = current_window - 1

        # Keys for current and previous windows
        current_key = f"sliding_counter:{user_id}:{current_window}"
        previous_key = f"sliding_counter:{user_id}:{previous_window}"

        # Get counts
        pipe = self.redis_client.pipeline()
        pipe.get(current_key)
        pipe.get(previous_key)
        current_count, previous_count = pipe.execute()

        current_count = int(current_count) if current_count else 0
        previous_count = int(previous_count) if previous_count else 0

        # Calculate sliding window count
        elapsed_time_in_window = now % self.window_seconds
        weight = 1 - (elapsed_time_in_window / self.window_seconds)
        estimated_count = (previous_count * weight) + current_count

        if estimated_count < self.max_requests:
            # Increment counter
            self.redis_client.incr(current_key)
            self.redis_client.expire(current_key, self.window_seconds * 2)
            return True
        else:
            return False
```

**Django Integration:**

```python
# Django Rate Limiting Middleware
from django.core.cache import cache
from django.http import JsonResponse
import time

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get user identifier
        user_id = self.get_user_identifier(request)

        # Check rate limit
        if not self.is_allowed(user_id):
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please try again later.'
            }, status=429)

        response = self.get_response(request)

        # Add rate limit headers
        response['X-RateLimit-Limit'] = '100'
        response['X-RateLimit-Remaining'] = str(self.get_remaining(user_id))
        response['X-RateLimit-Reset'] = str(self.get_reset_time())

        return response

    def get_user_identifier(self, request):
        # Use authenticated user ID or IP address
        if request.user.is_authenticated:
            return f"user:{request.user.id}"
        else:
            return f"ip:{self.get_client_ip(request)}"

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def is_allowed(self, user_id, max_requests=100, window_seconds=60):
        key = f"rate_limit:{user_id}"

        # Get current count
        count = cache.get(key, 0)

        if count >= max_requests:
            return False

        # Increment counter
        if count == 0:
            cache.set(key, 1, window_seconds)
        else:
            cache.incr(key)

        return True

    def get_remaining(self, user_id, max_requests=100):
        key = f"rate_limit:{user_id}"
        count = cache.get(key, 0)
        return max(0, max_requests - count)

    def get_reset_time(self, window_seconds=60):
        now = int(time.time())
        return ((now // window_seconds) + 1) * window_seconds

# settings.py
MIDDLEWARE = [
    # ...
    'path.to.RateLimitMiddleware',
]

# Using django-ratelimit package
from django_ratelimit.decorators import ratelimit

@ratelimit(key='user', rate='100/h', method='POST')
def create_task(request):
    # Limited to 100 POST requests per hour per user
    pass

@ratelimit(key='ip', rate='1000/d')
def api_endpoint(request):
    # Limited to 1000 requests per day per IP
    pass

# DRF Throttling
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class TaskViewSet(viewsets.ModelViewSet):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    # User: 1000 req/day (settings.py)
    # Anon: 100 req/day (settings.py)

# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '1000/day',
        'anon': '100/day',
    }
}

# Custom throttle for TaskMaster
from rest_framework.throttling import SimpleRateThrottle

class TaskCreationThrottle(SimpleRateThrottle):
    scope = 'task_creation'

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            return f'throttle_task_{request.user.id}'
        return None  # No throttling for anonymous

# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'task_creation': '100/hour',  # 100 tasks per hour
    }
}

# Usage
class TaskViewSet(viewsets.ModelViewSet):
    def get_throttles(self):
        if self.action == 'create':
            return [TaskCreationThrottle()]
        return super().get_throttles()
```

**Distributed Rate Limiting:**

```python
# Using Redis for distributed rate limiting
import redis
from datetime import datetime, timedelta

class DistributedRateLimiter:
    """
    Rate limiter that works across multiple servers
    Uses Redis for centralized counter
    """

    def __init__(self):
        self.redis_client = redis.Redis(
            host='redis-cluster.example.com',
            port=6379,
            decode_responses=True
        )

    def is_allowed(self, user_id, max_requests=100, window_seconds=60):
        key = f"rate_limit:{user_id}"

        # Lua script for atomic increment + expire
        lua_script = """
        local key = KEYS[1]
        local max_requests = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])

        local current = redis.call('GET', key)

        if current == false then
            redis.call('SET', key, 1, 'EX', window)
            return 1
        end

        current = tonumber(current)

        if current < max_requests then
            redis.call('INCR', key)
            return current + 1
        else
            return -1
        end
        """

        result = self.redis_client.eval(
            lua_script,
            1,
            key,
            max_requests,
            window_seconds
        )

        return result != -1

# Multi-tier rate limiting
class MultiTierRateLimiter:
    """
    Different limits for different tiers
    """

    RATE_LIMITS = {
        'free': {'requests': 100, 'window': 3600},  # 100/hour
        'basic': {'requests': 1000, 'window': 3600},  # 1000/hour
        'premium': {'requests': 10000, 'window': 3600},  # 10k/hour
        'enterprise': {'requests': 100000, 'window': 3600},  # 100k/hour
    }

    def is_allowed(self, user_id, tier='free'):
        limits = self.RATE_LIMITS[tier]
        return self.check_limit(
            user_id,
            max_requests=limits['requests'],
            window_seconds=limits['window']
        )
```

**Real-world Example: API Rate Limiting Headers**

```python
# Implement GitHub-style rate limit headers
from django.http import JsonResponse
import time

class RateLimitResponse:
    @staticmethod
    def create_response(request, allowed, limit=100, window=3600):
        user_id = request.user.id if request.user.is_authenticated else request.META['REMOTE_ADDR']
        key = f"rate_limit:{user_id}"

        # Get current usage
        current = cache.get(key, 0)
        remaining = max(0, limit - current)

        # Calculate reset time
        reset_time = ((int(time.time()) // window) + 1) * window

        if not allowed:
            response = JsonResponse({
                'error': 'Rate limit exceeded',
                'message': f'API rate limit exceeded. Limit: {limit} requests per hour.',
                'documentation_url': 'https://docs.taskmaster.com/api/rate-limits'
            }, status=429)
        else:
            response = JsonResponse({'status': 'ok'})

        # Add headers (GitHub style)
        response['X-RateLimit-Limit'] = str(limit)
        response['X-RateLimit-Remaining'] = str(remaining)
        response['X-RateLimit-Reset'] = str(reset_time)
        response['X-RateLimit-Used'] = str(current)

        if not allowed:
            retry_after = reset_time - int(time.time())
            response['Retry-After'] = str(retry_after)

        return response

# Usage
@api_view(['POST'])
def create_task(request):
    limiter = RateLimiter()

    if not limiter.is_allowed(request.user.id):
        return RateLimitResponse.create_response(
            request,
            allowed=False,
            limit=100,
            window=3600
        )

    # Process request
    task = Task.objects.create(**request.data)
    return Response(TaskSerializer(task).data)
```

**Comparison of Algorithms:**

| Algorithm | Memory | Accuracy | Burst | Complexity |
|-----------|---------|----------|-------|------------|
| Token Bucket | Low | Medium | Allows small bursts | Medium |
| Leaky Bucket | Low | High | No bursts (smooth) | Medium |
| Fixed Window | Very Low | Low (edge burst) | High | Low |
| Sliding Log | High | Very High | Controlled | High |
| Sliding Counter | Low | High | Controlled | Medium |

**Best Practice: Sliding Window Counter** for production systems - good balance of accuracy, memory, and complexity.

---

*[This is getting quite long! I've completed 6 comprehensive questions with detailed explanations, code examples, diagrams, and real-world applications. Would you like me to continue with the remaining 34 questions, or should I create this as Part 1 and continue in subsequent parts? Each question deserves thorough coverage like this.]*

Let me know if you'd like me to:
1. Continue with all 40 questions in one file (will be very large)
2. Split into multiple parts (Part 1: Q1-10, Part 2: Q11-20, etc.)
3. Focus on specific questions you're most interested in

What would you prefer?
### 7. How does Single Sign-On (SSO) work?

**Single Sign-On** allows users to authenticate once and access multiple applications without re-entering credentials.

```
SSO Flow (SAML):
┌────────┐                    ┌─────────┐                    ┌────────────┐
│  User  │                    │   SP    │                    │    IdP     │
│        │                    │(Service │                    │(Identity   │
│        │                    │Provider)│                    │ Provider)  │
└───┬────┘                    └────┬────┘                    └──────┬─────┘
    │                              │                                │
    │ 1. Access App                │                                │
    ├─────────────────────────────▶│                                │
    │                              │                                │
    │    2. Redirect to IdP        │                                │
    │◀─────────────────────────────┤                                │
    │                              │                                │
    │ 3. Login (if not authenticated)                               │
    ├──────────────────────────────────────────────────────────────▶│
    │                              │                                │
    │                              │  4. Authenticate user          │
    │                              │                                │
    │    5. SAML Assertion         │                                │
    │◀──────────────────────────────────────────────────────────────┤
    │                              │                                │
    │ 6. Send Assertion to SP      │                                │
    ├─────────────────────────────▶│                                │
    │                              │                                │
    │                              │  7. Verify Assertion           │
    │                              │                                │
    │    8. Grant Access           │                                │
    │◀─────────────────────────────┤                                │
    │                              │                                │
```

**Implementation with Django and OAuth2/OpenID Connect:**

```python
# Using Django Social Auth for SSO
# settings.py
INSTALLED_APPS = [
    'social_django',  # Django Social Auth
]

AUTHENTICATION_BACKENDS = [
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.microsoft.MicrosoftOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

# OAuth Settings
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'your-client-id'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'your-client-secret'
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['email', 'profile']

# Redirect URLs
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/dashboard/'

# urls.py
urlpatterns = [
    path('auth/', include('social_django.urls', namespace='social')),
]

# Template
# <a href="{% url 'social:begin' 'google-oauth2' %}">Login with Google</a>
# <a href="{% url 'social:begin' 'github' %}">Login with GitHub</a>

# Custom SSO backend
from social_core.backends.oauth import BaseOAuth2

class CustomSSOBackend(BaseOAuth2):
    name = 'custom-sso'
    AUTHORIZATION_URL = 'https://sso.company.com/oauth/authorize'
    ACCESS_TOKEN_URL = 'https://sso.company.com/oauth/token'
    ACCESS_TOKEN_METHOD = 'POST'

    def get_user_details(self, response):
        return {
            'username': response.get('email'),
            'email': response.get('email'),
            'first_name': response.get('first_name'),
            'last_name': response.get('last_name'),
        }
```

**SAML SSO Implementation:**

```python
# Using python3-saml library
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from django.conf import settings
from django.http import HttpResponseRedirect
from django.views import View

class SAMLLoginView(View):
    def get(self, request):
        # Prepare SAML request
        saml_auth = OneLogin_Saml2_Auth(
            self.prepare_request(request),
            settings.SAML_SETTINGS
        )

        # Redirect to IdP for authentication
        return HttpResponseRedirect(saml_auth.login())

    def prepare_request(self, request):
        return {
            'https': 'on' if request.is_secure() else 'off',
            'http_host': request.META['HTTP_HOST'],
            'script_name': request.META['PATH_INFO'],
            'get_data': request.GET.copy(),
            'post_data': request.POST.copy()
        }

class SAMLCallbackView(View):
    def post(self, request):
        # Process SAML response
        saml_auth = OneLogin_Saml2_Auth(
            self.prepare_request(request),
            settings.SAML_SETTINGS
        )

        saml_auth.process_response()

        if saml_auth.is_authenticated():
            # Get user attributes from SAML assertion
            attributes = saml_auth.get_attributes()
            email = attributes['email'][0]
            name = attributes['name'][0]

            # Get or create user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'name': name}
            )

            # Log user in
            from django.contrib.auth import login
            login(request, user)

            return HttpResponseRedirect('/dashboard/')
        else:
            errors = saml_auth.get_errors()
            return HttpResponse(f"Authentication failed: {errors}")

# settings.py
SAML_SETTINGS = {
    "strict": True,
    "sp": {
        "entityId": "https://app.taskmaster.com/saml/metadata",
        "assertionConsumerService": {
            "url": "https://app.taskmaster.com/saml/acs",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
        },
    },
    "idp": {
        "entityId": "https://sso.company.com/saml/metadata",
        "singleSignOnService": {
            "url": "https://sso.company.com/saml/sso",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        },
        "x509cert": "MIIC..."  # IdP certificate
    }
}
```

**JWT-based SSO:**

```python
import jwt
from datetime import datetime, timedelta
from django.conf import settings

class JWTSSOAuthentication:
    """
    JWT-based SSO between multiple applications
    """

    def generate_sso_token(self, user):
        """Central SSO server generates token"""
        payload = {
            'user_id': user.id,
            'email': user.email,
            'name': user.get_full_name(),
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow(),
            'iss': 'https://sso.taskmaster.com',  # Issuer
            'aud': [  # Allowed applications
                'https://app1.taskmaster.com',
                'https://app2.taskmaster.com',
                'https://app3.taskmaster.com',
            ]
        }

        token = jwt.encode(
            payload,
            settings.SSO_SECRET_KEY,
            algorithm='HS256'
        )

        return token

    def verify_sso_token(self, token):
        """Application verifies token"""
        try:
            payload = jwt.decode(
                token,
                settings.SSO_SECRET_KEY,
                algorithms=['HS256'],
                audience='https://app1.taskmaster.com'
            )

            # Get or create user from token
            user, created = User.objects.get_or_create(
                email=payload['email'],
                defaults={'name': payload['name']}
            )

            return user

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired')
        except jwt.InvalidAudienceError:
            raise AuthenticationFailed('Invalid audience')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')

# SSO Login Flow
class SSOLoginView(View):
    def get(self, request):
        # Redirect to SSO server
        redirect_uri = request.build_absolute_uri('/sso/callback/')
        sso_url = f"https://sso.taskmaster.com/login?redirect_uri={redirect_uri}"
        return HttpResponseRedirect(sso_url)

class SSOCallbackView(View):
    def get(self, request):
        # Receive token from SSO server
        token = request.GET.get('token')

        # Verify token
        sso_auth = JWTSSOAuthentication()
        user = sso_auth.verify_sso_token(token)

        # Log user in
        from django.contrib.auth import login
        login(request, user)

        return HttpResponseRedirect('/dashboard/')
```

---

### 8. How does Apache Kafka work? Why is it so fast?

**Apache Kafka** is a distributed streaming platform for building real-time data pipelines and streaming applications.

```
Kafka Architecture:
┌─────────────────────────────────────────────────────────────┐
│                        PRODUCERS                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │ Service1 │    │ Service2 │    │ Service3 │              │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘              │
└───────┼───────────────┼───────────────┼──────────────────────┘
        │               │               │
        │   Messages    │               │
        └───────┬───────┴───────┬───────┘
                │               │
    ┌───────────▼───────────────▼───────────────┐
    │          KAFKA CLUSTER                    │
    │   ┌────────────────────────────────┐      │
    │   │  Topic: user-events           │      │
    │   │  ┌──────┬──────┬──────┬──────┐│      │
    │   │  │Part0 │Part1 │Part2 │Part3 ││      │
    │   │  └──────┴──────┴──────┴──────┘│      │
    │   └────────────────────────────────┘      │
    │                                           │
    │   ┌────────────────────────────────┐      │
    │   │  Topic: task-events           │      │
    │   │  ┌──────┬──────┬──────┐       │      │
    │   │  │Part0 │Part1 │Part2 │       │      │
    │   │  └──────┴──────┴──────┘       │      │
    │   └────────────────────────────────┘      │
    └───────────┬───────────────┬───────────────┘
                │               │
        ┌───────┴───────┬───────┴────────┐
        │               │                │
┌───────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│  Consumer    │ │  Consumer   │ │  Consumer   │
│  Group 1     │ │  Group 2    │ │  Group 3    │
│ ┌──────────┐ │ │┌──────────┐ │ │┌──────────┐ │
│ │Analytics │ │ ││Notif Svc │ │ ││Search Idx│ │
│ └──────────┘ │ │└──────────┘ │ │└──────────┘ │
└──────────────┘ └─────────────┘ └─────────────┘
```

**Why Kafka is Fast:**

1. **Sequential I/O**: Writes to disk sequentially (append-only log)
2. **Zero-copy**: OS-level optimization, bypasses application buffers
3. **Batch Processing**: Groups messages together
4. **Compression**: Compresses message batches
5. **Partitioning**: Parallel processing across partitions
6. **No Random Access**: Simple append-only log structure

**Django + Kafka Integration:**

```python
# Using kafka-python library
from kafka import KafkaProducer, KafkaConsumer
import json

# Producer - Send events to Kafka
class KafkaTaskProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['kafka1:9092', 'kafka2:9092', 'kafka3:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            # Performance optimizations
            compression_type='snappy',  # Compress messages
            batch_size=16384,  # Batch messages
            linger_ms=10,  # Wait 10ms to batch more messages
            acks='1',  # Leader acknowledgment (balance speed/reliability)
        )

    def send_task_created_event(self, task):
        event = {
            'event_type': 'task.created',
            'task_id': task.id,
            'title': task.title,
            'project_id': task.project_id,
            'created_by': task.created_by.id,
            'timestamp': task.created_at.isoformat(),
        }

        # Send to Kafka topic
        future = self.producer.send('task-events', event)

        # Optional: Wait for confirmation
        # record_metadata = future.get(timeout=10)

        return future

    def close(self):
        self.producer.close()

# Consumer - Process events from Kafka
class KafkaTaskConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer(
            'task-events',
            bootstrap_servers=['kafka1:9092', 'kafka2:9092', 'kafka3:9092'],
            group_id='notification-service',  # Consumer group
            auto_offset_reset='earliest',  # Start from beginning if no offset
            enable_auto_commit=True,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            # Performance optimizations
            fetch_min_bytes=1024,  # Minimum data before fetch
            fetch_max_wait_ms=500,  # Wait max 500ms for fetch_min_bytes
        )

    def consume_events(self):
        for message in self.consumer:
            event = message.value

            # Process event
            if event['event_type'] == 'task.created':
                self.handle_task_created(event)

            elif event['event_type'] == 'task.updated':
                self.handle_task_updated(event)

            # Commit offset (automatic if enable_auto_commit=True)
            # self.consumer.commit()

    def handle_task_created(self, event):
        # Send notification
        task_id = event['task_id']
        # ... notification logic ...

    def close(self):
        self.consumer.close()

# Django Signal → Kafka Producer
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Task)
def task_saved_handler(sender, instance, created, **kwargs):
    producer = KafkaTaskProducer()

    if created:
        producer.send_task_created_event(instance)
    else:
        # Send updated event
        pass

    producer.close()
```

**Advanced Kafka Patterns:**

```python
# Pattern 1: Event Sourcing with Kafka
class TaskEventStore:
    """Store all task events in Kafka (event sourcing)"""

    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['kafka:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def append_event(self, event_type, aggregate_id, data):
        event = {
            'event_type': event_type,
            'aggregate_id': aggregate_id,
            'data': data,
            'timestamp': datetime.utcnow().isoformat(),
            'version': self.get_next_version(aggregate_id),
        }

        # Use aggregate_id as key for partitioning
        # All events for same task go to same partition (ordered)
        self.producer.send(
            'task-event-store',
            key=str(aggregate_id).encode('utf-8'),
            value=event
        )

    def get_events(self, aggregate_id):
        """Rebuild state from events"""
        consumer = KafkaConsumer(
            'task-event-store',
            bootstrap_servers=['kafka:9092'],
            auto_offset_reset='earliest',
        )

        events = []
        for message in consumer:
            if message.key.decode('utf-8') == str(aggregate_id):
                events.append(json.loads(message.value))

        return events

# Pattern 2: CQRS (Command Query Responsibility Segregation)
class TaskCommandHandler:
    """Write side - handles commands"""

    def handle_create_task(self, command):
        # Validate command
        # ...

        # Create event
        event = {
            'event_type': 'TaskCreated',
            'task_id': generate_id(),
            'data': command['data']
        }

        # Store event in Kafka
        event_store.append_event(event)

class TaskQueryHandler:
    """Read side - handles queries"""

    def __init__(self):
        # Read model (materialized view)
        self.tasks = {}

        # Consume events and build read model
        consumer = KafkaConsumer('task-events')
        for message in consumer:
            self.update_read_model(message.value)

    def update_read_model(self, event):
        if event['event_type'] == 'TaskCreated':
            self.tasks[event['task_id']] = event['data']
        elif event['event_type'] == 'TaskUpdated':
            self.tasks[event['task_id']].update(event['data'])

    def get_task(self, task_id):
        return self.tasks.get(task_id)

# Pattern 3: Saga Pattern (Distributed Transactions)
class TaskCreationSaga:
    """
    Coordinate distributed transaction across services
    """

    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=['kafka:9092'])
        self.consumer = KafkaConsumer('saga-events')

    def execute(self, task_data):
        saga_id = generate_id()

        # Step 1: Create task
        self.send_command('CreateTask', saga_id, task_data)

        # Wait for response
        for message in self.consumer:
            event = json.loads(message.value)

            if event['saga_id'] == saga_id:
                if event['status'] == 'TaskCreated':
                    # Step 2: Update project
                    self.send_command('UpdateProject', saga_id, {
                        'project_id': task_data['project_id']
                    })

                elif event['status'] == 'ProjectUpdated':
                    # Step 3: Send notification
                    self.send_command('SendNotification', saga_id, {
                        'user_id': task_data['owner_id']
                    })

                elif event['status'] == 'NotificationSent':
                    # Saga complete
                    return {'status': 'success', 'saga_id': saga_id}

                elif event['status'].endswith('Failed'):
                    # Compensate (rollback)
                    self.compensate(saga_id)
                    return {'status': 'failed'}

    def send_command(self, command_type, saga_id, data):
        self.producer.send('saga-commands', {
            'command_type': command_type,
            'saga_id': saga_id,
            'data': data
        })

    def compensate(self, saga_id):
        # Send compensating transactions
        self.send_command('DeleteTask', saga_id, {})
```

**Kafka vs Other Message Queues:**

| Feature | Kafka | RabbitMQ | ActiveMQ |
|---------|-------|----------|----------|
| **Type** | Distributed log | Message broker | Message broker |
| **Throughput** | Very High (1M+ msg/sec) | Medium | Medium |
| **Latency** | Low (ms) | Very Low (μs) | Low |
| **Ordering** | Per partition | Per queue | Per queue |
| **Retention** | Configurable (days) | Until consumed | Until consumed |
| **Replay** | Yes | No | No |
| **Use Case** | Event streaming, logs | Task queues, RPC | Enterprise messaging |
| **Consumers** | Multiple (pub-sub) | Multiple | Multiple |
| **Persistence** | Disk (always) | Disk/Memory | Disk/Memory |

---

### 9. Difference between Kafka, ActiveMQ, and RabbitMQ?

**Quick Comparison:**

```
Use Kafka when:
- High throughput required (millions of messages/sec)
- Event streaming and log aggregation
- Need to replay messages
- Multiple consumers need same messages
- Building data pipelines

Use RabbitMQ when:
- Complex routing logic needed
- Guaranteed delivery with acknowledgments
- Task queues with worker pools
- Low latency critical (microseconds)
- Traditional messaging patterns

Use ActiveMQ when:
- Enterprise Java applications
- JMS (Java Message Service) required
- Need multiple protocols (AMQP, STOMP, MQTT)
- Legacy system integration
```

**Detailed Comparison:**

```python
# KAFKA - Event Streaming Platform
from kafka import KafkaProducer, KafkaConsumer

# Producer
producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
producer.send('user-events', b'user_registered')

# Consumer (can replay from beginning)
consumer = KafkaConsumer(
    'user-events',
    auto_offset_reset='earliest',  # Replay from start
    group_id='analytics-service'
)

for message in consumer:
    print(message.value)

# RABBITMQ - Message Broker
import pika

# Producer
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='tasks')
channel.basic_publish(exchange='', routing_key='tasks', body='Process order')

# Consumer (message deleted after consumption)
def callback(ch, method, properties, body):
    print(f"Received {body}")
    ch.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge

channel.basic_consume(queue='tasks', on_message_callback=callback)
channel.start_consuming()

# ACTIVEMQ - Enterprise Message Broker
import stomp

# Producer
conn = stomp.Connection([('localhost', 61613)])
conn.connect('admin', 'admin', wait=True)
conn.send(body='Process payment', destination='/queue/payments')

# Consumer
class MyListener(stomp.ConnectionListener):
    def on_message(self, frame):
        print(f'Received: {frame.body}')

conn.set_listener('', MyListener())
conn.subscribe(destination='/queue/payments', id=1, ack='auto')
```

---

### 10. Difference between JWT, OAuth, and SAML?

**JWT (JSON Web Token)**: Token format for authentication
**OAuth**: Authorization framework (delegated access)
**SAML**: XML-based SSO standard for enterprise

```
JWT Token Structure:
Header.Payload.Signature

eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9  ← Header (base64)
.
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6  ← Payload (base64)
.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_  ← Signature

OAuth 2.0 Flow:
┌────────┐               ┌──────────────┐
│  User  │──Login───────▶│ Auth Server  │
└───┬────┘               └──────┬───────┘
    │                           │
    │◀──Redirect with code──────┤
    │                           │
    │   Code                    │
    ├──────────────────────────▶│
    │                           │
    │◀──Access Token────────────┤
    │                           │
┌───▼────────┐          ┌───────▼──────┐
│   Client   │─ Token ─▶│  Resource    │
│Application │          │   Server     │
└────────────┘          └──────────────┘

SAML Assertion (XML):
<saml:Assertion>
  <saml:Subject>
    <saml:NameID>user@example.com</saml:NameID>
  </saml:Subject>
  <saml:Conditions>
    <saml:NotBefore>2025-01-01T00:00:00Z</saml:NotBefore>
    <saml:NotOnOrAfter>2025-01-01T01:00:00Z</saml:NotOnOrAfter>
  </saml:Conditions>
</saml:Assertion>
```

**Django Implementation:**

```python
# JWT Authentication
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email
        token['name'] = user.get_full_name()
        token['is_staff'] = user.is_staff

        return token

# settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}

# OAuth 2.0 (using django-oauth-toolkit)
INSTALLED_APPS = [
    'oauth2_provider',
]

OAUTH2_PROVIDER = {
    'SCOPES': {
        'read': 'Read scope',
        'write': 'Write scope',
    },
    'ACCESS_TOKEN_EXPIRE_SECONDS': 3600,
}

# SAML (using python3-saml)
# Already shown in question 7
```

**Comparison Table:**

| Feature | JWT | OAuth 2.0 | SAML |
|---------|-----|-----------|------|
| **Type** | Token format | Protocol | Protocol |
| **Format** | JSON | JSON | XML |
| **Size** | Small (~500 bytes) | Varies | Large (~5KB) |
| **Use Case** | API authentication | Delegated authorization | Enterprise SSO |
| **Mobile** | Excellent | Good | Poor (XML overhead) |
| **Complexity** | Simple | Medium | Complex |
| **Expiry** | Built-in (exp claim) | Refresh tokens | Session timeout |

*(Continuing with remaining questions in next message due to length...)*

---

## Databases & Storage

### 11. What is the difference between SQL and NoSQL databases?

**SQL (Relational)**: Structured data with predefined schema, ACID transactions
**NoSQL (Non-relational)**: Flexible schema, horizontal scalability, eventual consistency

```
SQL Database (PostgreSQL):
┌─────────────────────────────────────┐
│         Users Table                 │
├────┬─────────┬───────┬──────────────┤
│ ID │  Name   │ Email │    Created   │
├────┼─────────┼───────┼──────────────┤
│  1 │ Alice   │ a@... │ 2025-01-01   │
│  2 │ Bob     │ b@... │ 2025-01-02   │
└────┴─────────┴───────┴──────────────┘
         │
         │ Foreign Key
         ▼
┌─────────────────────────────────────┐
│         Tasks Table                 │
├────┬─────────┬─────────┬────────────┤
│ ID │  Title  │ User_ID │   Status   │
├────┼─────────┼─────────┼────────────┤
│ 1  │ Fix bug │    1    │  active    │
│ 2  │ Deploy  │    2    │ completed  │
└────┴─────────┴─────────┴────────────┘

NoSQL Database (MongoDB):
┌──────────────────────────────────────────┐
│  users collection                        │
│  {                                       │
│    "_id": "507f1f77bcf86cd799439011",   │
│    "name": "Alice",                      │
│    "email": "a@example.com",             │
│    "tasks": [                            │
│      {                                   │
│        "id": 1,                          │
│        "title": "Fix bug",               │
│        "status": "active"                │
│      }                                   │
│    ],                                    │
│    "profile": {                          │
│      "bio": "...",                       │
│      "location": "NYC"                   │
│    }                                     │
│  }                                       │
└──────────────────────────────────────────┘
```

**SQL Example (Django ORM with PostgreSQL):**

```python
# models.py - Structured schema
class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Task(models.Model):
    title = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relationship
    status = models.CharField(max_length=20)

# ACID transaction
from django.db import transaction

@transaction.atomic
def transfer_task(task_id, from_user, to_user):
    task = Task.objects.select_for_update().get(id=task_id)
    task.user = to_user
    task.save()

    # Both succeed or both fail (atomic)
    Log.objects.create(action='task_transferred')

# Complex JOINs
users_with_tasks = User.objects.select_related('tasks').filter(
    tasks__status='active'
).annotate(
    task_count=Count('tasks')
)
```

**NoSQL Example (MongoDB with Djongo/MongoEngine):**

```python
# Using MongoEngine
from mongoengine import Document, StringField, EmbeddedDocument, ListField

class TaskEmbed(EmbeddedDocument):
    title = StringField(required=True)
    status = StringField(default='todo')

class User(Document):
    name = StringField(required=True)
    email = StringField(required=True, unique=True)
    tasks = ListField(EmbeddedDocument(TaskEmbed))  # Embedded
    metadata = DictField()  # Flexible schema

    meta = {
        'collection': 'users',
        'indexes': ['email']
    }

# Flexible schema - add fields dynamically
user = User(
    name='Alice',
    email='alice@example.com',
    custom_field='anything'  # No migration needed!
)
user.save()

# No JOINs - embedded data
user = User.objects.get(email='alice@example.com')
for task in user.tasks:
    print(task.title)  # No separate query
```

**Comparison Table:**

| Feature | SQL (PostgreSQL, MySQL) | NoSQL (MongoDB, Cassandra, Redis) |
|---------|-------------------------|-----------------------------------|
| **Schema** | Fixed (predefined) | Flexible (dynamic) |
| **Relationships** | JOINs, Foreign Keys | Denormalized, embedded |
| **Transactions** | ACID (strong) | BASE (eventual consistency) |
| **Scaling** | Vertical (harder) | Horizontal (easier) |
| **Queries** | SQL (powerful) | API/query language (varies) |
| **Use Case** | Complex relationships, transactions | High-volume, unstructured data |
| **Performance** | Read-heavy workloads | Write-heavy workloads |
| **Data Integrity** | Enforced by constraints | Application-level |
| **Examples** | Banking, E-commerce | Social media, IoT, logging |

**When to use SQL:**
- Financial systems (banking, payments)
- Data integrity critical
- Complex queries with JOINs
- Well-defined schema
- ACID compliance required

**When to use NoSQL:**
- Massive scale (billions of rows)
- Flexible/evolving schema
- High write throughput
- Distributed globally
- Real-time analytics

---

### 12. How does Content Delivery Network (CDN) work?

**CDN** is a geographically distributed network of servers that cache and serve content from locations closer to users.

```
Without CDN:
┌──────────┐                           ┌──────────────┐
│ User     │                           │ Origin Server│
│ (Tokyo)  │───3000 km (300ms)────────▶│ (US West)    │
└──────────┘                           └──────────────┘

With CDN:
┌──────────┐     ┌────────────┐     ┌────────────┐     ┌──────────────┐
│ User     │─50km│ CDN Edge   │     │ CDN Edge   │     │ Origin Server│
│ (Tokyo)  │────▶│ (Tokyo)    │◀───▶│ (Other)    │◀───▶│ (US West)    │
└──────────┘5ms  └────────────┘     └────────────┘     └──────────────┘
                 Cache HIT ✓
                 (serves cached content immediately)
```

**How it works:**

1. **User requests** content (image, video, CSS, JS)
2. **DNS routes** request to nearest CDN edge server
3. **Edge server checks** cache:
   - If **cached** → serve immediately (cache hit)
   - If **not cached** → fetch from origin, cache, then serve (cache miss)
4. **Future requests** served from cache (fast)

**Django + CDN Integration:**

```python
# settings.py
# Using AWS CloudFront as CDN

# Static files (CSS, JS, images)
STATIC_URL = 'https://d111111abcdef8.cloudfront.net/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (user uploads)
MEDIA_URL = 'https://d111111abcdef8.cloudfront.net/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Using S3 + CloudFront
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'

AWS_STORAGE_BUCKET_NAME = 'taskmaster-static'
AWS_S3_CUSTOM_DOMAIN = 'd111111abcdef8.cloudfront.net'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',  # Cache for 1 day
}

# Template usage
# <img src="{{ MEDIA_URL }}{{ user.avatar }}" />
# Becomes: <img src="https://cdn.taskmaster.com/media/avatars/user1.jpg" />

# Manual CDN invalidation
import boto3

def invalidate_cdn_cache(paths):
    """Invalidate CDN cache for specific paths"""
    cloudfront = boto3.client('cloudfront')

    cloudfront.create_invalidation(
        DistributionId='E1234567890ABC',
        InvalidationBatch={
            'Paths': {
                'Quantity': len(paths),
                'Items': paths
            },
            'CallerReference': str(time.time())
        }
    )

# Invalidate after update
def update_product_image(product, new_image):
    old_path = product.image.url
    product.image = new_image
    product.save()

    # Invalidate CDN cache
    invalidate_cdn_cache([old_path])
```

**CDN Caching Strategies:**

```python
# 1. Cache-Control Headers
from django.views.decorators.cache import cache_control

@cache_control(max_age=3600, public=True)  # Cache for 1 hour
def static_asset(request):
    return FileResponse(open('static/logo.png', 'rb'))

# 2. Different caching for different file types
class S3StaticStorage(S3Boto3Storage):
    def __init__(self, *args, **kwargs):
        kwargs['custom_domain'] = 'cdn.taskmaster.com'
        super().__init__(*args, **kwargs)

    def get_object_parameters(self, name):
        params = super().get_object_parameters(name)

        # Cache images for 1 year (immutable)
        if name.endswith(('.jpg', '.png', '.gif', '.webp')):
            params['CacheControl'] = 'public, max-age=31536000, immutable'

        # Cache CSS/JS for 1 day (might change)
        elif name.endswith(('.css', '.js')):
            params['CacheControl'] = 'public, max-age=86400'

        # Cache HTML for 5 minutes
        elif name.endswith('.html'):
            params['CacheControl'] = 'public, max-age=300'

        return params

# 3. Versioned URLs (cache busting)
# Django automatically does this with ManifestStaticFilesStorage
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Before: /static/style.css
# After:  /static/style.abc123.css (hash in filename)
# CDN can cache forever, new version = new URL
```

**Benefits of CDN:**

1. **Reduced Latency**: Content served from nearby edge servers (ms vs seconds)
2. **Reduced Load**: Origin server handles fewer requests
3. **High Availability**: Multiple edge servers (redundancy)
4. **DDoS Protection**: Absorbs attack traffic
5. **Reduced Bandwidth Costs**: Less data transferred from origin

---

### 13. What is the difference between Synchronous and Asynchronous communication?

**Synchronous**: Caller waits for response before continuing (blocking)
**Asynchronous**: Caller continues immediately, response handled later (non-blocking)

```
SYNCHRONOUS (Request-Response):
┌────────┐                    ┌────────┐
│ Client │                    │ Server │
└───┬────┘                    └────┬───┘
    │  1. Request                  │
    ├─────────────────────────────▶│
    │                              │
    │  ⏳ WAITING (blocked)        │ Processing...
    │                              │
    │  2. Response                 │
    │◀─────────────────────────────┤
    │                              │
    │  3. Continue                 │
    ▼                              ▼

ASYNCHRONOUS (Message Queue):
┌────────┐      ┌───────┐      ┌────────┐
│ Client │      │ Queue │      │ Worker │
└───┬────┘      └───┬───┘      └────┬───┘
    │ 1. Send msg   │               │
    ├──────────────▶│               │
    │               │               │
    │ 2. Continue   │  3. Process   │
    │   immediately │◀──────────────┤
    ▼               │               │
                    │  4. Callback  │
                    │   (optional)  │
                    │──────────────▶│
                    ▼               ▼
```

**Synchronous Example (Django):**

```python
# View makes synchronous API call
import requests

def create_task(request):
    # 1. Save task to database (synchronous)
    task = Task.objects.create(
        title=request.data['title'],
        owner=request.user
    )

    # 2. Send notification (BLOCKS until complete)
    response = requests.post(
        'https://notification-service.com/send',
        json={'user_id': request.user.id, 'message': 'Task created'}
    )
    # ⏳ Waits for notification service to respond

    # 3. Update analytics (BLOCKS)
    requests.post(
        'https://analytics.com/track',
        json={'event': 'task_created'}
    )
    # ⏳ Waits again

    # 4. Finally return response
    return Response(TaskSerializer(task).data)
    # Total time: DB save + Notification call + Analytics call

# Problems:
# - Slow response time
# - If notification service down, entire request fails
# - User waits for external services
```

**Asynchronous Example (Celery):**

```python
# Asynchronous with Celery
from celery import shared_task

@shared_task
def send_notification_async(user_id, message):
    """Runs in background worker"""
    requests.post(
        'https://notification-service.com/send',
        json={'user_id': user_id, 'message': message}
    )

@shared_task
def track_analytics_async(event_type, data):
    """Runs in background worker"""
    requests.post(
        'https://analytics.com/track',
        json={'event': event_type, 'data': data}
    )

def create_task(request):
    # 1. Save task to database (fast)
    task = Task.objects.create(
        title=request.data['title'],
        owner=request.user
    )

    # 2. Queue background tasks (immediate)
    send_notification_async.delay(
        user_id=request.user.id,
        message='Task created'
    )
    track_analytics_async.delay(
        event_type='task_created',
        data={'task_id': task.id}
    )

    # 3. Return response immediately (fast!)
    return Response(TaskSerializer(task).data)
    # Total time: DB save only (notifications happen in background)

# Benefits:
# - Fast response
# - Failure-resistant (if notification fails, task still created)
# - Better user experience
```

**Python Async/Await:**

```python
# Asynchronous I/O with asyncio
import asyncio
import aiohttp

async def fetch_user(user_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.com/users/{user_id}') as response:
            return await response.json()

async def fetch_tasks(user_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.com/tasks?user={user_id}') as response:
            return await response.json()

# Synchronous (slow)
def get_user_data_sync(user_id):
    user = requests.get(f'https://api.com/users/{user_id}').json()  # Wait 200ms
    tasks = requests.get(f'https://api.com/tasks?user={user_id}').json()  # Wait 200ms
    return {'user': user, 'tasks': tasks}
    # Total: 400ms

# Asynchronous (fast)
async def get_user_data_async(user_id):
    # Run both requests concurrently
    user, tasks = await asyncio.gather(
        fetch_user(user_id),      # 200ms
        fetch_tasks(user_id)      # 200ms (parallel!)
    )
    return {'user': user, 'tasks': tasks}
    # Total: 200ms (50% faster!)

# Django async view
from django.http import JsonResponse

async def user_dashboard(request, user_id):
    data = await get_user_data_async(user_id)
    return JsonResponse(data)
```

**Comparison:**

| Aspect | Synchronous | Asynchronous |
|--------|-------------|--------------|
| **Execution** | Sequential (blocking) | Concurrent (non-blocking) |
| **Response** | Immediate | Delayed/callback |
| **Performance** | Slower (waits) | Faster (parallel) |
| **Complexity** | Simple | More complex |
| **Error Handling** | Direct | Callbacks/promises |
| **Use Case** | CRUD operations | Long-running tasks, I/O |
| **Examples** | HTTP request/response | Email sending, file processing |

---

### 14. How does Database Sharding work?

**Sharding** is horizontal partitioning where data is distributed across multiple databases.

```
Before Sharding (Single Database):
┌────────────────────────────────────┐
│         Single Database            │
│  ┌──────────────────────────────┐ │
│  │ Users Table (10M rows)       │ │
│  ├────┬─────────┬────────────────┤ │
│  │ ID │  Name   │  Country       │ │
│  ├────┼─────────┼────────────────┤ │
│  │ 1  │ Alice   │  USA           │ │
│  │ 2  │ Bob     │  UK            │ │
│  │... │  ...    │  ...           │ │
│  │10M │ Zara    │  JP            │ │
│  └────┴─────────┴────────────────┘ │
└────────────────────────────────────┘
   Problems:
   - Slow queries
   - Limited scalability
   - Single point of failure

After Sharding (Multiple Databases):
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Shard 1 (USA)  │ │  Shard 2 (EU)   │ │ Shard 3 (APAC)  │
│  Users: 1-3M    │ │  Users: 3M-6M   │ │  Users: 6M-10M  │
├────┬──────┬─────┤ ├────┬──────┬─────┤ ├────┬──────┬─────┤
│ 1  │Alice │ USA │ │ 4M │ Bob  │ UK  │ │ 7M │Carol │ JP  │
│... │ ...  │ ... │ │... │ ...  │ ... │ │... │ ...  │ ... │
└────┴──────┴─────┘ └────┴──────┴─────┘ └────┴──────┴─────┘
   Benefits:
   ✓ Faster queries (smaller datasets)
   ✓ Horizontal scalability
   ✓ Fault isolation
```

**Sharding Strategies:**

```python
# 1. RANGE-BASED SHARDING (by user ID)
def get_shard_by_range(user_id):
    if user_id < 1000000:
        return 'shard_1'
    elif user_id < 2000000:
        return 'shard_2'
    else:
        return 'shard_3'

# Pros: Simple, range queries efficient
# Cons: Uneven distribution (shard 3 might grow faster)

# 2. HASH-BASED SHARDING (by user ID)
import hashlib

def get_shard_by_hash(user_id, num_shards=4):
    hash_value = int(hashlib.md5(str(user_id).encode()).hexdigest(), 16)
    shard_num = hash_value % num_shards
    return f'shard_{shard_num}'

# Pros: Even distribution
# Cons: Range queries difficult, rebalancing hard

# 3. GEOGRAPHIC SHARDING (by location)
def get_shard_by_location(country):
    location_shards = {
        'US': 'shard_us_west',
        'UK': 'shard_eu_west',
        'JP': 'shard_apac_tokyo',
    }
    return location_shards.get(country, 'shard_default')

# Pros: Low latency (data near users), complies with data residency laws
# Cons: Uneven distribution

# 4. ENTITY-BASED SHARDING (by tenant/organization)
def get_shard_by_tenant(tenant_id):
    # All data for a tenant in same shard
    return f'shard_{tenant_id % 10}'

# Pros: Co-location (fast joins within tenant), easy tenant migration
# Cons: Hot shards if one tenant is huge
```

**Django Sharding Implementation:**

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'metadata_db',  # Stores routing info
    },
    'shard_0': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'shard_0',
        'HOST': 'db0.example.com',
    },
    'shard_1': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'shard_1',
        'HOST': 'db1.example.com',
    },
    'shard_2': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'shard_2',
        'HOST': 'db2.example.com',
    },
    'shard_3': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'shard_3',
        'HOST': 'db3.example.com',
    },
}

# Sharding Router
class ShardRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'tasks':
            user_id = hints.get('user_id')
            if user_id:
                return self.get_shard_for_user(user_id)
        return 'default'

    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)

    def get_shard_for_user(self, user_id):
        # Hash-based sharding
        import hashlib
        hash_value = int(hashlib.md5(str(user_id).encode()).hexdigest(), 16)
        shard_num = hash_value % 4
        return f'shard_{shard_num}'

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'tasks':
            # Don't migrate tasks on default DB
            return db.startswith('shard_')
        return db == 'default'

DATABASE_ROUTERS = ['path.to.ShardRouter']

# Using sharded database
def create_task(user_id, task_data):
    # Determine shard
    router = ShardRouter()
    shard = router.get_shard_for_user(user_id)

    # Create task in correct shard
    task = Task.objects.using(shard).create(**task_data)
    return task

def get_user_tasks(user_id):
    # Query from correct shard
    router = ShardRouter()
    shard = router.get_shard_for_user(user_id)

    tasks = Task.objects.using(shard).filter(owner_id=user_id)
    return tasks

# Cross-shard query (complex!)
def get_all_active_tasks():
    """Query all shards and merge results"""
    all_tasks = []

    for shard_name in ['shard_0', 'shard_1', 'shard_2', 'shard_3']:
        tasks = Task.objects.using(shard_name).filter(status='active')
        all_tasks.extend(tasks)

    # Sort in application layer
    all_tasks.sort(key=lambda t: t.created_at, reverse=True)
    return all_tasks[:100]  # Top 100
```

**Consistent Hashing (for rebalancing):**

```python
import hashlib
import bisect

class ConsistentHashRing:
    """
    Consistent hashing minimizes data movement when adding/removing shards
    """

    def __init__(self, nodes, virtual_nodes=150):
        self.ring = {}
        self.sorted_keys = []
        self.nodes = nodes

        # Create virtual nodes for even distribution
        for node in nodes:
            for i in range(virtual_nodes):
                virtual_key = f"{node}:{i}"
                hash_key = self._hash(virtual_key)
                self.ring[hash_key] = node

        self.sorted_keys = sorted(self.ring.keys())

    def _hash(self, key):
        return int(hashlib.md5(str(key).encode()).hexdigest(), 16)

    def get_node(self, key):
        """Find shard for given key"""
        if not self.ring:
            return None

        hash_key = self._hash(key)

        # Find first node clockwise
        idx = bisect.bisect_right(self.sorted_keys, hash_key)
        if idx == len(self.sorted_keys):
            idx = 0

        return self.ring[self.sorted_keys[idx]]

    def add_node(self, node):
        """Add new shard (minimal data movement)"""
        for i in range(150):
            virtual_key = f"{node}:{i}"
            hash_key = self._hash(virtual_key)
            self.ring[hash_key] = node

        self.sorted_keys = sorted(self.ring.keys())

    def remove_node(self, node):
        """Remove shard (redistribute its data)"""
        for i in range(150):
            virtual_key = f"{node}:{i}"
            hash_key = self._hash(virtual_key)
            del self.ring[hash_key]

        self.sorted_keys = sorted(self.ring.keys())

# Usage
ring = ConsistentHashRing(['shard_0', 'shard_1', 'shard_2'])

# Get shard for user
user_id = 12345
shard = ring.get_node(user_id)  # shard_1

# Add new shard (only ~25% data moves, not 100%!)
ring.add_node('shard_3')
new_shard = ring.get_node(user_id)  # Might change to shard_3
```

**Challenges and Solutions:**

```python
# Challenge 1: Global Unique IDs
# Problem: Auto-increment IDs conflict across shards

# Solution 1: UUID
import uuid

class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

# Solution 2: Snowflake ID (Twitter's approach)
def generate_snowflake_id(shard_id):
    """
    64-bit ID:
    - 41 bits: timestamp
    - 10 bits: shard ID
    - 12 bits: sequence
    """
    timestamp = int(time.time() * 1000) << 22
    shard = shard_id << 12
    sequence = get_sequence()  # Auto-increment per shard
    return timestamp | shard | sequence

# Challenge 2: Cross-shard JOINs
# Problem: User in shard_1, their tasks in shard_2

# Solution: Denormalization
class Task(models.Model):
    id = models.UUIDField(primary_key=True)
    title = models.CharField(max_length=200)
    owner_id = models.IntegerField()
    owner_name = models.CharField(max_length=100)  # Denormalized!
    owner_email = models.EmailField()  # Denormalized!

# Challenge 3: Distributed Transactions
# Solution: Two-Phase Commit or Saga pattern (see question 34)

# Challenge 4: Resharding (adding more shards)
# Solution: Consistent hashing + gradual migration

def reshard_user(user_id, old_shard, new_shard):
    """Migrate user data to new shard"""
    with transaction.atomic(using=old_shard):
        # Get all user data
        tasks = Task.objects.using(old_shard).filter(owner_id=user_id)

        # Copy to new shard
        for task in tasks:
            Task.objects.using(new_shard).create(**{
                f.name: getattr(task, f.name)
                for f in task._meta.fields
                if f.name != 'id'
            })

        # Delete from old shard
        tasks.delete()
```

---

*(To be continued with questions 15-40...)*
