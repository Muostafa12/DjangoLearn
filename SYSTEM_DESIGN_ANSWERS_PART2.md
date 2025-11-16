# System Design Questions - Part 2 (Questions 21-40)

Continuation of comprehensive system design answers.

---

## Distributed Systems Patterns

### 21. What is the difference between Stateful and Stateless architecture?

**Stateless**: Server doesn't store client state between requests (each request independent)
**Stateful**: Server maintains client state across requests (session data stored)

```
STATELESS:
┌────────┐      ┌─────────┐      ┌────────┐
│Client 1│─────▶│ Server  │◀─────│Client 2│
└────────┘      │  (No    │      └────────┘
Request 1       │ memory  │      Request 2
{token:abc,     │   of    │      {token:xyz,
 data:...}      │ clients)│       data:...}
                └─────────┘

Every request contains ALL needed info
✓ Scalable (any server handles request)
✓ No session synchronization
✓ Easy load balancing

STATEFUL:
┌────────┐      ┌─────────┐      ┌────────┐
│Client 1│─────▶│ Server  │◀─────│Client 2│
└────────┘      │┌───────┐│      └────────┘
Request 1       ││Session││      Request 2
                ││ Data  ││
Session:abc     ││ abc:{}││      Session:xyz
                ││ xyz:{}││
                │└───────┘│
                └─────────┘

Server remembers client state
✗ Harder to scale (sticky sessions needed)
✗ Session synchronization complex
✓ Simpler client logic
```

**Django Stateless API (REST):**

```python
# Stateless - Every request includes auth token
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.authentication import TokenAuthentication

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def get_tasks(request):
    # No session - token contains all auth info
    user = request.user  # Extracted from token
    tasks = Task.objects.filter(owner=user)
    return Response(TaskSerializer(tasks, many=True).data)

# Client sends token with EVERY request
# GET /api/tasks/
# Authorization: Token abc123def456

# settings.py - Stateless configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# No SESSION_ENGINE needed
# No session cookies
# Any server can handle any request
```

**Django Stateful (Sessions):**

```python
# Stateful - Server stores session data
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    # Session data stored on server
    request.session['last_page'] = 'dashboard'
    request.session['visit_count'] = request.session.get('visit_count', 0) + 1

    # Server remembers user state
    user = request.user  # From session
    return render(request, 'dashboard.html')

# settings.py - Stateful configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Store in database
# or
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'  # Store in Redis

# Problem with multiple servers:
# User logs in on Server 1 (session stored there)
# Next request goes to Server 2 (no session!)
# Solution: Shared session store (Redis/Database)

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis-server:6379/1',
    }
}
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

**Comparison & Use Cases:**

| Aspect | Stateless | Stateful |
|--------|-----------|----------|
| **Scalability** | Excellent (horizontal) | Harder (sticky sessions) |
| **Session Data** | Client-side (token/cookie) | Server-side (memory/DB) |
| **Load Balancing** | Simple (any server) | Complex (sticky required) |
| **Server Crash** | No impact | Lose session data |
| **Example** | REST APIs, Microservices | Traditional web apps |
| **Auth** | JWT, OAuth tokens | Session cookies |

---

### 22. How does Circuit Breaker pattern work?

**Circuit Breaker** prevents cascading failures by stopping requests to failing services.

```
Circuit Breaker States:

CLOSED (Normal Operation):
Request ──▶ Service
           ✓ Success

OPEN (Service Failing):
Request ──X─▶ (Circuit Open)
Return error immediately
(Don't call failing service)

HALF-OPEN (Testing Recovery):
Request ──?─▶ Service
           Test if recovered

State Transitions:
          ┌─────────┐
     ┌───▶│ CLOSED  │──────┐
     │    └─────────┘      │
     │         │            │
  Success   Failures > N   │
     │         │            │
     │    ┌────▼─────┐     │
     │    │  OPEN    │     │
     │    └────┬─────┘     │
     │         │            │
     │    After timeout    │
     │         │            │
     │    ┌────▼──────┐    │
     └────│ HALF-OPEN │────┘
          └───────────┘
           Test request
```

**Implementation:**

```python
import time
from datetime import datetime, timedelta
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60, success_threshold=2):
        self.failure_threshold = failure_threshold  # Open after N failures
        self.timeout = timeout  # Seconds to wait before HALF_OPEN
        self.success_threshold = success_threshold  # Successes to CLOSE

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None

    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            # Check if timeout passed
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError("Service unavailable")

        try:
            # Call the service
            result = func(*args, **kwargs)

            # Success
            self._on_success()
            return result

        except Exception as e:
            # Failure
            self._on_failure()
            raise

    def _on_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self._close()
        else:
            self.failure_count = 0

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self._open()

    def _open(self):
        self.state = CircuitState.OPEN

    def _close(self):
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0

    def _should_attempt_reset(self):
        return (
            self.last_failure_time and
            datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout)
        )

class CircuitBreakerOpenError(Exception):
    pass

# Usage with external API
notification_circuit = CircuitBreaker(failure_threshold=3, timeout=30)

def send_notification_with_circuit_breaker(user_id, message):
    try:
        result = notification_circuit.call(
            send_notification_api,  # The actual function
            user_id,
            message
        )
        return result
    except CircuitBreakerOpenError:
        logger.warning("Circuit breaker open, notification skipped")
        return None  # Fallback behavior
    except Exception as e:
        logger.error(f"Notification failed: {e}")
        return None

def send_notification_api(user_id, message):
    # May fail if service is down
    response = requests.post(
        'https://notification-service/send',
        json={'user_id': user_id, 'message': message},
        timeout=5
    )
    response.raise_for_status()
    return response.json()
```

**Django Integration:**

```python
# Decorator version
def circuit_breaker(failure_threshold=5, timeout=60):
    breakers = {}

    def decorator(func):
        func_name = func.__name__
        if func_name not in breakers:
            breakers[func_name] = CircuitBreaker(failure_threshold, timeout)

        def wrapper(*args, **kwargs):
            breaker = breakers[func_name]
            return breaker.call(func, *args, **kwargs)

        return wrapper
    return decorator

# Usage
@circuit_breaker(failure_threshold=3, timeout=30)
def call_payment_service(amount):
    response = requests.post(
        'https://payment-service/charge',
        json={'amount': amount}
    )
    response.raise_for_status()
    return response.json()

# In view
def process_payment(request):
    try:
        result = call_payment_service(request.data['amount'])
        return Response({'status': 'success'})
    except CircuitBreakerOpenError:
        return Response(
            {'error': 'Payment service temporarily unavailable'},
            status=503
        )
```

**Benefits:**
- Prevents cascading failures
- Fast failure (no waiting for timeout)
- Automatic recovery testing
- Service isolation

---

### 23. What is the difference between Authentication and Authorization?

**Authentication**: Verifying WHO you are (identity)
**Authorization**: Verifying WHAT you can do (permissions)

```
Flow:
┌──────┐   1. Login    ┌────────────────┐
│ User │──────────────▶│ Authentication │
└──────┘   (Who?)      └────────┬───────┘
                                │
                         Verify identity
                          (password)
                                │
                                ✓
                       ┌────────▼────────┐
                       │   Authenticated │
                       │   User: Alice   │
                       └────────┬────────┘
                                │
┌──────────────────────┐        │
│ 2. Access Resource   │◀───────┘
└──────────┬───────────┘
           │
    ┌──────▼───────┐
    │Authorization │
    │   (What?)    │
    └──────┬───────┘
           │
    Check permissions
    Can Alice delete task?
           │
      ┌────▼────┐
      │ Allow / │
      │  Deny   │
      └─────────┘
```

**Django Implementation:**

```python
# AUTHENTICATION - Who are you?
from django.contrib.auth import authenticate, login

def login_view(request):
    # Verify identity
    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(request, username=username, password=password)

    if user is not None:
        # Authentication successful
        login(request, user)
        return redirect('dashboard')
    else:
        # Authentication failed
        return render(request, 'login.html', {'error': 'Invalid credentials'})

# JWT Authentication
from rest_framework_simplejwt.views import TokenObtainPairView

# POST /api/token/
# {"username": "alice", "password": "secret"}
# Response: {"access": "eyJ...", "refresh": "eyJ..."}

# AUTHORIZATION - What can you do?
from django.contrib.auth.decorators import login_required, permission_required

@login_required  # Must be authenticated
@permission_required('tasks.delete_task', raise_exception=True)  # Must have permission
def delete_task(request, task_id):
    task = Task.objects.get(id=task_id)

    # Object-level authorization
    if task.owner != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't own this task")

    task.delete()
    return redirect('task-list')

# Django Permissions
from django.contrib.auth.models import Permission

# Create custom permission
class Task(models.Model):
    class Meta:
        permissions = [
            ('can_publish', 'Can publish task'),
            ('can_archive', 'Can archive task'),
        ]

# Assign permission to user
user.user_permissions.add(
    Permission.objects.get(codename='can_publish')
)

# Check permission
if user.has_perm('tasks.can_publish'):
    # Allow

# DRF Authorization
from rest_framework.permissions import BasePermission

class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission to only allow owners to edit.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions allowed for any request
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        # Write permissions only for owner
        return obj.owner == request.user

class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrReadOnly]

# Role-Based Access Control (RBAC)
class Role(models.Model):
    name = models.CharField(max_length=50)  # admin, editor, viewer
    permissions = models.ManyToManyField(Permission)

class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'role', 'project']

def can_edit_task(user, task):
    """Check if user has editor role for task's project"""
    return UserRole.objects.filter(
        user=user,
        project=task.project,
        role__name__in=['admin', 'editor']
    ).exists()
```

**Comparison:**

| Aspect | Authentication | Authorization |
|--------|----------------|---------------|
| **Question** | Who are you? | What can you do? |
| **Process** | Verify identity | Check permissions |
| **Methods** | Password, Token, Biometric | Roles, Permissions, ACLs |
| **Happens** | Once (login) | Every request |
| **Response** | Identity confirmed | Access granted/denied |
| **HTTP Status** | 401 Unauthorized | 403 Forbidden |
| **Example** | Login with password | Delete only your own tasks |

---

### 24. How does Distributed Tracing work?

**Distributed Tracing** tracks requests across multiple services in microservices architecture.

```
Without Tracing:
User Request ──▶ Service A ──▶ Service B ──▶ Service C
                   ❌ Slow!
                (Which service is slow?)

With Distributed Tracing:
Trace ID: abc-123

User Request [abc-123, span-1] ──▶ Service A [abc-123, span-2] ──▶ Service B [abc-123, span-3] ──▶ Service C
     │                                  │ 50ms                           │ 200ms (SLOW!)               │ 30ms
     │                                  │                                │                              │
     └──────────────────────────────────┴────────────────────────────────┴──────────────────────────────┘
                                    Total: 280ms (Can see Service B is bottleneck)
```

**OpenTelemetry Integration:**

```python
# Install: pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-django

# settings.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor

# Setup tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Export to Jaeger
jaeger_exporter = JaegerExporter(
    agent_host_name='localhost',
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Auto-instrument Django
DjangoInstrumentor().instrument()

# Usage in code
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def create_task(request):
    # Automatically traced by Django instrumentation
    with tracer.start_as_current_span("create_task") as span:
        span.set_attribute("user.id", request.user.id)

        # Database query (auto-traced)
        task = Task.objects.create(**request.data)
        span.set_attribute("task.id", task.id)

        # Call external service (manual trace)
        with tracer.start_as_current_span("send_notification"):
            send_notification(task.id)

        return Response(TaskSerializer(task).data)

def send_notification(task_id):
    with tracer.start_as_current_span("notification_service_call") as span:
        span.set_attribute("service", "notification")

        response = requests.post(
            'https://notification-service/send',
            json={'task_id': task_id}
        )

        span.set_attribute("response.status", response.status_code)

# Propagate trace context across services
import requests
from opentelemetry.propagate import inject

def call_other_service(data):
    headers = {}
    inject(headers)  # Add trace context to headers

    response = requests.post(
        'https://other-service/api',
        json=data,
        headers=headers  # Propagate trace
    )
    return response.json()
```

**Jaeger/Zipkin Trace Visualization:**

```
Trace ID: abc-123
Duration: 280ms

┌─ User Request (span-1) ────────────────────────────────┐ 280ms
│  ┌─ Service A: create_task (span-2) ─────────────────┐│ 50ms
│  │  ├─ Database: INSERT task (span-3) ───────────────┤│ 20ms
│  │  └─ send_notification (span-4) ───────────────────┤│ 30ms
│  └──────────────────────────────────────────────────┘│
│  ┌─ Service B: notification_service_call (span-5) ───┐│ 200ms ⚠️
│  │  ├─ Database: SELECT user (span-6) ──────────────┤│ 150ms ⚠️
│  │  └─ SMTP: send email (span-7) ────────────────────┤│ 50ms
│  └──────────────────────────────────────────────────┘│
│  ┌─ Service C: analytics (span-8) ────────────────────┐│ 30ms
│  │  └─ Redis: INCR counter (span-9) ─────────────────┤│ 5ms
│  └──────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────┘

Issues found:
- Span-5 (notification_service): 200ms (71% of total time)
- Span-6 (database query): 150ms (needs optimization)
```

**Benefits:**
- Identify bottlenecks across services
- Debug complex microservice interactions
- Monitor service dependencies
- Root cause analysis for failures

---

### 25. What is the difference between ACID and BASE properties?

**ACID** (SQL databases): Strong consistency, strict guarantees
**BASE** (NoSQL databases): Eventual consistency, high availability

```
ACID:
A - Atomicity: All or nothing
C - Consistency: Valid state always
I - Isolation: Concurrent transactions don't interfere
D - Durability: Once committed, data persists

BASE:
BA - Basically Available: System responds (may be stale)
S  - Soft state: State may change without input (replication)
E  - Eventual consistency: Will become consistent eventually
```

**ACID Example (PostgreSQL/Django):**

```python
from django.db import transaction

# Atomicity: All or nothing
@transaction.atomic
def transfer_money(from_account, to_account, amount):
    # Both succeed or both fail
    from_acc = Account.objects.select_for_update().get(id=from_account)
    to_acc = Account.objects.select_for_update().get(id=to_account)

    from_acc.balance -= amount
    from_acc.save()  # Transaction not committed yet

    if from_acc.balance < 0:
        raise ValueError("Insufficient funds")  # Rollback both

    to_acc.balance += amount
    to_acc.save()

    # Both committed together (atomic)

# Consistency: Constraints enforced
class Account(models.Model):
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(balance__gte=0),
                name='balance_non_negative'
            )
        ]
# Database enforces balance >= 0

# Isolation: Transactions don't see each other's changes
# Read committed isolation level (default)
from_acc = Account.objects.select_for_update().get(id=1)
# Locks row, other transactions wait

# Durability: Data persists after commit
account.balance = 100
account.save()
# Even if server crashes, data is saved
```

**BASE Example (Cassandra/MongoDB):**

```python
# Basically Available: Always responds (even if stale)
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client.taskmaster

# Write with eventual consistency
db.users.update_one(
    {'_id': user_id},
    {'$inc': {'task_count': 1}},
    write_concern={'w': 1}  # Don't wait for all replicas
)
# Returns immediately, replicates in background

# Read might return stale data
user = db.users.find_one({'_id': user_id})
print(user['task_count'])  # Might be old value

# Soft state: State changes without input (background replication)
# Data syncing between replicas

# Eventual consistency: Eventually all replicas converge
time.sleep(0.5)  # Wait for replication
user = db.users.find_one({'_id': user_id})
print(user['task_count'])  # Now updated

# Conflict resolution with BASE
class Counter:
    """CRDT - Conflict-free Replicated Data Type"""
    def __init__(self):
        self.counts = {}

    def increment(self, node_id):
        self.counts[node_id] = self.counts.get(node_id, 0) + 1

    def value(self):
        return sum(self.counts.values())

    def merge(self, other):
        # Merge from another replica (no conflicts!)
        for node, count in other.counts.items():
            self.counts[node] = max(self.counts.get(node, 0), count)
```

**Comparison:**

| Property | ACID | BASE |
|----------|------|------|
| **Focus** | Consistency | Availability |
| **Guarantees** | Strong | Weak |
| **Performance** | Slower (locks) | Faster (no locks) |
| **Scalability** | Vertical | Horizontal |
| **Use Case** | Banking, E-commerce | Social media, Analytics |
| **Examples** | PostgreSQL, MySQL | Cassandra, DynamoDB |
| **Failures** | Rollback | Continue anyway |

---

### 26. How does Service Discovery work?

**Service Discovery** allows services to find each other dynamically in distributed systems.

```
Without Service Discovery:
Service A ──hardcoded──▶ http://service-b:8080
                         (What if Service B moves or scales?)

With Service Discovery:
Service A ──▶ Service Registry ──▶ Find Service B
                  │
                  ├─ Service B: 10.0.1.5:8080
                  ├─ Service B: 10.0.1.6:8080
                  └─ Service B: 10.0.1.7:8080
                 (Returns healthy instance)
```

**Consul Service Discovery:**

```python
# Register service with Consul
import consul
import socket

consul_client = consul.Consul(host='localhost', port=8500)

def register_service():
    """Register this service instance with Consul"""
    service_id = f"taskmaster-api-{socket.gethostname()}"

    consul_client.agent.service.register(
        name='taskmaster-api',
        service_id=service_id,
        address=socket.gethostbyname(socket.gethostname()),
        port=8000,
        check={
            'http': 'http://localhost:8000/health/',
            'interval': '10s',  # Check every 10 seconds
            'timeout': '5s',
        }
    )

# Discover other services
def discover_service(service_name):
    """Find healthy instances of a service"""
    _, services = consul_client.health.service(service_name, passing=True)

    if not services:
        raise ServiceNotFoundError(f"No healthy {service_name} instances")

    # Load balance across instances
    import random
    service = random.choice(services)

    address = service['Service']['Address']
    port = service['Service']['Port']

    return f"http://{address}:{port}"

# Usage
def call_notification_service(message):
    # Discover notification service dynamically
    service_url = discover_service('notification-service')

    response = requests.post(
        f"{service_url}/send",
        json={'message': message}
    )
    return response.json()

# Django integration
# settings.py
NOTIFICATION_SERVICE_URL = discover_service('notification-service')

# Health check endpoint
from rest_framework.decorators import api_view

@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy'}, status=200)
```

**Kubernetes Service Discovery:**

```yaml
# taskmaster-api-deployment.yaml
apiVersion: v1
kind: Service
metadata:
  name: taskmaster-api
spec:
  selector:
    app: taskmaster-api
  ports:
    - port: 8000
      targetPort: 8000
  type: ClusterIP

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: taskmaster-api
spec:
  replicas: 3
  template:
    metadata:
      labels:
        app: taskmaster-api
    spec:
      containers:
      - name: api
        image: taskmaster-api:latest
        ports:
        - containerPort: 8000

# Service discovery in code
# http://taskmaster-api:8000 (DNS name)
# Kubernetes routes to healthy pod
```

---

### 27. What is the difference between Push and Pull architecture?

**Push**: Server sends data to clients (proactive)
**Pull**: Clients request data from server (reactive)

```
PUSH:
Server ────▶ Client 1
       │
       ├───▶ Client 2
       │
       └───▶ Client 3

Server initiates (WebSocket, SSE)

PULL:
Client 1 ────▶ Server
Client 2 ────▶ Server
Client 3 ────▶ Server

Clients request (HTTP polling)
```

**Push Example (WebSocket):**

```python
# Django Channels - Push notifications
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        # Server pushes when events occur
        self.send_notifications_task.delay(self.channel_name)

    async def notification_event(self, event):
        # Server pushes notification to client
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message']
        }))

# When task created, server pushes to all connected clients
from channels.layers import get_channel_layer

def create_task(request):
    task = Task.objects.create(**request.data)

    # Push notification to all subscribers
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'notifications',
        {
            'type': 'notification_event',
            'message': f'New task: {task.title}'
        }
    )
```

**Pull Example (Polling):**

```python
# Client polls server for updates
@api_view(['GET'])
def get_notifications(request):
    # Client requests notifications
    notifications = Notification.objects.filter(
        recipient=request.user,
        created_at__gt=request.GET.get('since')
    )
    return Response(NotificationSerializer(notifications, many=True).data)

# JavaScript client polls every 30 seconds
setInterval(async () => {
    const response = await fetch('/api/notifications/?since=' + lastCheck);
    const notifications = await response.json();
    displayNotifications(notifications);
    lastCheck = Date.now();
}, 30000);
```

**Comparison:**

| Aspect | Push | Pull |
|--------|------|------|
| **Initiator** | Server | Client |
| **Real-time** | Yes (immediate) | No (polling delay) |
| **Resources** | Persistent connections | Repeated requests |
| **Complexity** | Higher | Lower |
| **Use Case** | Live updates, Chat | APIs, Periodic sync |
| **Examples** | WebSocket, SSE | HTTP REST |

---

### 28. How does Database Indexing work?

**Index** is a data structure that improves query speed at the cost of storage and write performance.

```
Without Index (Full Table Scan):
SELECT * FROM tasks WHERE status = 'active';

Table scan: Check ALL rows
┌────┬───────────┬────────┐
│ ID │   Title   │ Status │
├────┼───────────┼────────┤
│  1 │ Fix bug   │ active │ ✓ Check
│  2 │ Deploy    │ done   │ ✗ Check
│  3 │ Review    │ active │ ✓ Check
│... │    ...    │  ...   │   ...
│1M  │ Test      │ active │ ✓ Check
└────┴───────────┴────────┘
Time: O(n) - Check 1 million rows

With Index (B-Tree):
┌─────────────┐
│   Index     │
│  (status)   │
├─────────────┤
│ active → [1,3,5,7...]    │ Fast lookup
│ done   → [2,4,6,8...]    │
│ cancelled → [...]        │
└─────────────┘
Time: O(log n) - Check index, get matching IDs
```

**Django Indexes:**

```python
# Model-level indexes
class Task(models.Model):
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20)
    priority = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            # Single column index
            models.Index(fields=['status']),

            # Multi-column index (composite)
            models.Index(fields=['status', 'priority']),

            # Descending order index
            models.Index(fields=['-created_at']),

            # Named index
            models.Index(fields=['title'], name='task_title_idx'),

            # Partial index (PostgreSQL)
            models.Index(
                fields=['status'],
                condition=models.Q(status='active'),
                name='active_tasks_idx'
            ),
        ]

# Field-level indexes
class User(models.Model):
    email = models.EmailField(unique=True)  # Creates unique index
    username = models.CharField(max_length=100, db_index=True)  # Creates index

# Covering index (PostgreSQL)
from django.contrib.postgres.indexes import Index

class Task(models.Model):
    class Meta:
        indexes = [
            Index(fields=['status'], include=['title', 'priority'])
        ]
    # Index contains status + title + priority (no table lookup needed)

# Check index usage
from django.db import connection

def show_query_plan(queryset):
    """Show PostgreSQL query plan"""
    sql, params = queryset.query.sql_with_params()
    with connection.cursor() as cursor:
        cursor.execute(f"EXPLAIN ANALYZE {sql}", params)
        return cursor.fetchall()

# Example
tasks = Task.objects.filter(status='active')
print(show_query_plan(tasks))

# Output: Index Scan using task_status_idx
```

**Index Types:**

```python
# 1. B-Tree Index (default) - General purpose
models.Index(fields=['created_at'])  # Range queries, sorting

# 2. Hash Index - Equality only
# CREATE INDEX ON tasks USING HASH (status);

# 3. GIN Index - Full-text search, arrays, JSON
from django.contrib.postgres.indexes import GinIndex

class Task(models.Model):
    tags = ArrayField(models.CharField(max_length=50))

    class Meta:
        indexes = [
            GinIndex(fields=['tags'])  # Fast array containment
        ]

# 4. GiST Index - Geometric data, full-text
from django.contrib.postgres.indexes import GistIndex

# 5. BRIN Index - Very large tables with natural ordering
from django.contrib.postgres.indexes import BrinIndex

class LogEntry(models.Model):
    timestamp = models.DateTimeField()

    class Meta:
        indexes = [
            BrinIndex(fields=['timestamp'])  # Tiny index for time-series
        ]
```

**Best Practices:**

```python
# DO: Index foreign keys
class Task(models.Model):
    project = models.ForeignKey(Project)  # Auto-indexed

# DO: Index filter conditions
# If you often query: Task.objects.filter(status='active', priority='high')
class Meta:
    indexes = [models.Index(fields=['status', 'priority'])]

# DON'T: Over-index
# Each index slows writes and uses storage

# DO: Index columns used in ORDER BY
Task.objects.order_by('-created_at')  # Index on created_at

# DON'T: Index low-cardinality columns alone
# Bad: status (only 3-4 values)
# Better: Composite index with high-cardinality column

# DO: Monitor index usage
SELECT * FROM pg_stat_user_indexes WHERE schemaname='public';
```

---

### 29. What is the difference between Batch and Stream processing?

**Batch**: Process large volume of data at once (scheduled)
**Stream**: Process data continuously in real-time

```
BATCH (ETL Pipeline):
┌────────────────────────────────────┐
│  Data accumulates throughout day   │
└─────────────┬──────────────────────┘
              │
              ▼ Every night at 2 AM
┌─────────────────────────────────┐
│  Batch Job Processes All Data   │
│  - Read 1M records              │
│  - Transform                     │
│  - Aggregate                     │
│  - Write to warehouse            │
└─────────────┬───────────────────┘
              │
              ▼ 3 hours later
         ┌────────┐
         │ Done!  │
         └────────┘

STREAM (Real-time):
Data ──▶ Process ──▶ Output
Data ──▶ Process ──▶ Output
Data ──▶ Process ──▶ Output
(continuous, milliseconds latency)
```

**Batch Processing Example:**

```python
# Django management command - Daily batch job
# python manage.py generate_daily_report

from django.core.management.base import BaseCommand
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Generate daily task summary report'

    def handle(self, *args, **options):
        yesterday = datetime.now() - timedelta(days=1)

        # Process batch of data
        tasks = Task.objects.filter(
            created_at__date=yesterday.date()
        )

        # Aggregate
        stats = tasks.aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            avg_duration=Avg('duration')
        )

        # Generate report
        Report.objects.create(
            date=yesterday.date(),
            total_tasks=stats['total'],
            completed_tasks=stats['completed'],
            avg_duration=stats['avg_duration']
        )

        self.stdout.write(f"Processed {stats['total']} tasks")

# Celery Beat - Scheduled batch jobs
from celery import shared_task
from celery.schedules import crontab

@shared_task
def nightly_data_processing():
    """Process all day's data at midnight"""
    # Batch process large dataset
    users = User.objects.all()

    for user in users.iterator(chunk_size=1000):  # Batch in chunks
        calculate_user_metrics(user)

    send_daily_summary_email()

# Schedule
app.conf.beat_schedule = {
    'nightly-processing': {
        'task': 'tasks.nightly_data_processing',
        'schedule': crontab(hour=0, minute=0),  # Midnight
    },
}
```

**Stream Processing Example:**

```python
# Kafka + Real-time processing
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'task-events',
    bootstrap_servers=['kafka:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# Process stream continuously
for message in consumer:
    event = message.value

    # Real-time processing
    if event['type'] == 'task_created':
        # Immediate action (not batched)
        update_real_time_dashboard(event['task_id'])
        send_instant_notification(event['user_id'])
        increment_metrics_counter()

    # No accumulation, immediate processing

# Django + Server-Sent Events (real-time stream)
from django.http import StreamingHttpResponse
import time

def event_stream():
    """Stream events to browser"""
    while True:
        # Generate events in real-time
        tasks = Task.objects.filter(updated_at__gt=last_check)
        for task in tasks:
            yield f"data: {json.dumps({'id': task.id, 'title': task.title})}\n\n"

        time.sleep(1)  # Check every second

def stream_view(request):
    return StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )

# JavaScript client receives real-time updates
# const eventSource = new EventSource('/stream/');
# eventSource.onmessage = (e) => {
#     const task = JSON.parse(e.data);
#     updateUI(task);  // Update immediately
# };
```

**Comparison:**

| Aspect | Batch | Stream |
|--------|-------|--------|
| **Timing** | Periodic (hourly/daily) | Continuous (real-time) |
| **Latency** | Hours to days | Milliseconds to seconds |
| **Data Volume** | Large (GB to TB) | Small per event (KB) |
| **Use Case** | Reports, Analytics, ETL | Monitoring, Alerts, Live dashboards |
| **Tools** | Cron, Celery Beat, Airflow | Kafka, Flink, Storm |
| **Complexity** | Simple | Complex |
| **Cost** | Lower (scheduled resources) | Higher (always running) |

---

### 30. How does Consistent Hashing work?

**Consistent Hashing** distributes data across servers minimizing redistribution when servers are added/removed.

```
Traditional Hashing:
server = hash(key) % N  # N = number of servers

Problem:
3 servers → 5 servers
All keys redistributed! (60% move)

Consistent Hashing:
┌─────────────────────────────┐
│        Hash Ring            │
│         (0-360)             │
│                             │
│      S1 (45°)              │
│         ●                   │
│    K2 ●                     │
│                    ● K1     │
│                             │
│  ● S3 (270°)      S2 (180°)│
│                    ●        │
│     ● K3                    │
└─────────────────────────────┘

Key → Server (clockwise):
K1 (90°) → S2 (180°)
K2 (30°) → S1 (45°)
K3 (200°) → S3 (270°)

Add S4 (100°):
Only K1 moves from S2 to S4
K2, K3 stay same
(Only 25% redistribution instead of 60%)
```

**Implementation:**

```python
import hashlib
import bisect

class ConsistentHashRing:
    def __init__(self, nodes=None, virtual_nodes=150):
        """
        nodes: List of server names
        virtual_nodes: Number of virtual nodes per server (for even distribution)
        """
        self.virtual_nodes = virtual_nodes
        self.ring = {}
        self.sorted_keys = []

        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key):
        """Hash function to map keys to ring"""
        return int(hashlib.md5(str(key).encode()).hexdigest(), 16)

    def add_node(self, node):
        """Add server to ring"""
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:{i}"
            hash_value = self._hash(virtual_key)
            self.ring[hash_value] = node

        self.sorted_keys = sorted(self.ring.keys())

    def remove_node(self, node):
        """Remove server from ring"""
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:{i}"
            hash_value = self._hash(virtual_key)
            del self.ring[hash_value]

        self.sorted_keys = sorted(self.ring.keys())

    def get_node(self, key):
        """Find server for given key"""
        if not self.ring:
            return None

        hash_value = self._hash(key)

        # Find first server clockwise
        index = bisect.bisect_right(self.sorted_keys, hash_value)
        if index == len(self.sorted_keys):
            index = 0

        return self.ring[self.sorted_keys[index]]

# Usage with Django cache
class ConsistentHashCache:
    def __init__(self, cache_servers):
        self.ring = ConsistentHashRing(cache_servers)
        self.caches = {
            server: redis.Redis(host=server, port=6379)
            for server in cache_servers
        }

    def get(self, key):
        server = self.ring.get_node(key)
        return self.caches[server].get(key)

    def set(self, key, value, expire=3600):
        server = self.ring.get_node(key)
        return self.caches[server].setex(key, expire, value)

    def add_server(self, server):
        """Add new cache server (minimal key redistribution)"""
        self.ring.add_node(server)
        self.caches[server] = redis.Redis(host=server, port=6379)

# Example
cache = ConsistentHashCache(['cache1', 'cache2', 'cache3'])

# Keys distributed evenly
cache.set('user:123', user_data)  # → cache2
cache.set('user:456', user_data)  # → cache1
cache.set('user:789', user_data)  # → cache3

# Add new server
cache.add_server('cache4')
# Only ~25% of keys move (not 100%)

# Example with Django sharding
class ShardRouter:
    def __init__(self, shards):
        self.ring = ConsistentHashRing(shards)

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'tasks':
            user_id = hints.get('user_id')
            if user_id:
                return self.ring.get_node(user_id)
        return 'default'

# Add new shard
# Only fraction of data moves to new shard
```

**Benefits:**
- Minimal redistribution when scaling
- Even load distribution (virtual nodes)
- Fault tolerance (automatic rerouting)

---

*(Due to length, continuing with final 10 questions in conclusion...)*

Would you like me to continue with the remaining questions 31-40 to complete all 40 comprehensive system design questions?


### 31. What is the difference between RPC and REST?

**RPC (Remote Procedure Call)**: Call functions on remote server as if local
**REST (Representational State Transfer)**: Resource-based HTTP operations

```
RPC (Action-oriented):
POST /api/createUser
POST /api/deleteUser
POST /api/sendEmail

REST (Resource-oriented):
POST   /api/users      (create)
DELETE /api/users/123  (delete)
POST   /api/emails     (send)
```

**gRPC Example:**

```python
# Install: pip install grpcio grpcio-tools

# 1. Define service in .proto file
# task.proto
syntax = "proto3";

service TaskService {
  rpc CreateTask(CreateTaskRequest) returns (Task);
  rpc GetTask(GetTaskRequest) returns (Task);
  rpc ListTasks(ListTasksRequest) returns (TaskList);
}

message Task {
  int32 id = 1;
  string title = 2;
  string status = 3;
}

message CreateTaskRequest {
  string title = 1;
  int32 owner_id = 2;
}

# 2. Generate Python code
# python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. task.proto

# 3. Implement server
import grpc
from concurrent import futures
import task_pb2
import task_pb2_grpc

class TaskServicer(task_pb2_grpc.TaskServiceServicer):
    def CreateTask(self, request, context):
        # Direct function call style
        task = Task.objects.create(
            title=request.title,
            owner_id=request.owner_id
        )

        return task_pb2.Task(
            id=task.id,
            title=task.title,
            status=task.status
        )

    def GetTask(self, request, context):
        task = Task.objects.get(id=request.id)
        return task_pb2.Task(
            id=task.id,
            title=task.title,
            status=task.status
        )

# Start server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
task_pb2_grpc.add_TaskServiceServicer_to_server(TaskServicer(), server)
server.add_insecure_port('[::]:50051')
server.start()

# 4. Client
channel = grpc.insecure_channel('localhost:50051')
stub = task_pb2_grpc.TaskServiceStub(channel)

# Call like local function
response = stub.CreateTask(task_pb2.CreateTaskRequest(
    title="Fix bug",
    owner_id=123
))
print(f"Created task: {response.id}")
```

**REST Example (Django):**

```python
# Resource-oriented endpoints
from rest_framework import viewsets

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

# Auto-generated endpoints:
# GET    /api/tasks/       - List
# POST   /api/tasks/       - Create
# GET    /api/tasks/123/   - Retrieve
# PUT    /api/tasks/123/   - Update
# DELETE /api/tasks/123/   - Delete

# Client (HTTP/JSON)
import requests

# Create
response = requests.post(
    'http://api.example.com/tasks/',
    json={'title': 'Fix bug', 'owner_id': 123}
)

# Get
response = requests.get('http://api.example.com/tasks/123/')
```

**Comparison:**

| Feature | RPC (gRPC) | REST |
|---------|------------|------|
| **Style** | Function calls | HTTP resources |
| **Protocol** | HTTP/2, binary | HTTP/1.1, JSON |
| **Performance** | Faster (binary, multiplexing) | Slower (text, overhead) |
| **Contract** | Strong (.proto files) | Weak (documentation) |
| **Streaming** | Bidirectional | Limited |
| **Browser Support** | No (needs proxy) | Yes |
| **Caching** | Complex | HTTP caching |
| **Use Case** | Microservice-to-microservice | Public APIs, web clients |

**When to use RPC:**
- Internal microservices
- High performance required
- Strong typing needed
- Real-time bidirectional streams

**When to use REST:**
- Public APIs
- Web/mobile clients
- Standard HTTP features needed
- Simple CRUD operations

---

### 32. How does Leader Election work in distributed systems?

**Leader Election** chooses one node to coordinate operations among distributed nodes.

```
Before Election:
Node A │ Node B │ Node C  (All equal)

Election Process:
Node A: "I'll be leader" → Vote: 1
Node B: "I'll be leader" → Vote: 2
Node C: "I vote for B"  → Vote: 2

After Election:
Node A (Follower) │ Node B (LEADER) │ Node C (Follower)
         │                 │                │
         └────────────────▶│◀───────────────┘
                    All follow leader
```

**Raft Consensus Algorithm:**

```python
from enum import Enum
import random
import time

class NodeState(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"

class RaftNode:
    def __init__(self, node_id, cluster_nodes):
        self.node_id = node_id
        self.cluster_nodes = cluster_nodes
        self.state = NodeState.FOLLOWER

        self.current_term = 0
        self.voted_for = None
        self.leader_id = None

        self.election_timeout = random.uniform(150, 300)  # ms
        self.last_heartbeat = time.time()

    def run(self):
        """Main event loop"""
        while True:
            if self.state == NodeState.FOLLOWER:
                self.handle_follower()
            elif self.state == NodeState.CANDIDATE:
                self.handle_candidate()
            elif self.state == NodeState.LEADER:
                self.handle_leader()

            time.sleep(0.01)

    def handle_follower(self):
        """Wait for leader heartbeat or start election"""
        if time.time() - self.last_heartbeat > self.election_timeout:
            # No heartbeat from leader, start election
            self.start_election()

    def start_election(self):
        """Transition to candidate and request votes"""
        self.state = NodeState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id

        votes = 1  # Vote for self

        # Request votes from other nodes
        for node in self.cluster_nodes:
            if node != self.node_id:
                if self.request_vote(node):
                    votes += 1

        # Win if majority votes
        if votes > len(self.cluster_nodes) / 2:
            self.become_leader()
        else:
            # Lost election, return to follower
            self.state = NodeState.FOLLOWER

    def request_vote(self, node):
        """Ask node for vote"""
        # RPC call to other node
        response = rpc_call(node, 'request_vote', {
            'term': self.current_term,
            'candidate_id': self.node_id
        })

        return response.get('vote_granted', False)

    def become_leader(self):
        """Become cluster leader"""
        self.state = NodeState.LEADER
        self.leader_id = self.node_id
        print(f"Node {self.node_id} became leader for term {self.current_term}")

    def handle_leader(self):
        """Send heartbeats to followers"""
        for node in self.cluster_nodes:
            if node != self.node_id:
                self.send_heartbeat(node)

        time.sleep(0.05)  # Heartbeat interval

    def send_heartbeat(self, node):
        """Send heartbeat to prevent elections"""
        rpc_call(node, 'append_entries', {
            'term': self.current_term,
            'leader_id': self.node_id
        })

    def receive_heartbeat(self, leader_term, leader_id):
        """Receive heartbeat from leader"""
        if leader_term >= self.current_term:
            self.state = NodeState.FOLLOWER
            self.current_term = leader_term
            self.leader_id = leader_id
            self.last_heartbeat = time.time()
```

**Django Integration with Consul:**

```python
# Using Consul for leader election
import consul
import time

class ConsulLeaderElection:
    def __init__(self, service_name, node_id):
        self.consul = consul.Consul()
        self.service_name = service_name
        self.node_id = node_id
        self.session_id = None
        self.is_leader = False

    def start(self):
        """Start leader election process"""
        # Create session
        self.session_id = self.consul.session.create(
            name=f"{self.service_name}-{self.node_id}",
            ttl=10  # Session expires after 10s without renewal
        )

        # Try to acquire leadership
        while True:
            self.try_acquire_leadership()
            time.sleep(5)  # Check every 5 seconds

    def try_acquire_leadership(self):
        """Attempt to become leader"""
        key = f"service/{self.service_name}/leader"

        # Try to acquire lock
        acquired = self.consul.kv.put(
            key,
            self.node_id,
            acquire=self.session_id
        )

        if acquired:
            if not self.is_leader:
                self.on_become_leader()
            self.is_leader = True
            self.renew_session()
        else:
            if self.is_leader:
                self.on_lose_leadership()
            self.is_leader = False

    def on_become_leader(self):
        """Called when this node becomes leader"""
        print(f"Node {self.node_id} became leader")

        # Leader-specific tasks
        self.start_cron_jobs()
        self.coordinate_cluster()

    def on_lose_leadership(self):
        """Called when this node loses leadership"""
        print(f"Node {self.node_id} lost leadership")

        # Stop leader-specific tasks
        self.stop_cron_jobs()

    def renew_session(self):
        """Renew Consul session to maintain leadership"""
        self.consul.session.renew(self.session_id)

# Usage in Django
# celerybeat only runs on leader
from celery.schedules import crontab

leader_election = ConsulLeaderElection('taskmaster', node_id='node1')

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    if leader_election.is_leader:
        # Only leader runs scheduled tasks
        sender.add_periodic_task(
            crontab(hour=0, minute=0),
            cleanup_old_data.s(),
        )
```

**Use Cases:**
- **Cron/scheduled jobs** - Only leader runs jobs
- **Cache warming** - Leader warms cache for cluster
- **Data processing** - Leader coordinates work distribution
- **Cluster coordination** - Leader manages configuration

---

### 33. What is the difference between Optimistic and Pessimistic locking?

**Optimistic Locking**: Assume no conflicts, check before committing
**Pessimistic Locking**: Lock resource immediately, prevent conflicts

```
OPTIMISTIC:
User A reads (v1) ┐
User B reads (v1) ┤  Both read
                  ┘
User A updates (v1→v2) ✓ Success
User B updates (v1→v2) ✗ Conflict! (version changed)

PESSIMISTIC:
User A locks row   ┐
User B tries lock  │ WAITING...
User A updates     │
User A unlocks     ┘
User B locks       ✓ Now can proceed
```

**Optimistic Locking (Django):**

```python
# Using version field
class Task(models.Model):
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20)
    version = models.IntegerField(default=0)  # Version tracker

def update_task_optimistic(task_id, new_title, expected_version):
    """Optimistic locking with version check"""
    # Read current version
    task = Task.objects.get(id=task_id)

    if task.version != expected_version:
        raise ConcurrentModificationError(
            f"Task was modified by someone else. "
            f"Expected version {expected_version}, got {task.version}"
        )

    # Update with version increment
    updated = Task.objects.filter(
        id=task_id,
        version=expected_version
    ).update(
        title=new_title,
        version=expected_version + 1
    )

    if not updated:
        raise ConcurrentModificationError("Update failed")

    return Task.objects.get(id=task_id)

# DRF integration
from rest_framework import serializers

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'status', 'version']

    def update(self, instance, validated_data):
        # Check version from request
        request_version = validated_data.pop('version', None)

        if request_version != instance.version:
            raise serializers.ValidationError(
                "Task was modified concurrently"
            )

        # Update with new version
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.version += 1
        instance.save()

        return instance

# Client sends version with update
# PUT /api/tasks/123/
# {
#   "title": "Updated title",
#   "version": 5  ← Must match current version
# }
```

**Pessimistic Locking (Django):**

```python
# Using select_for_update()
from django.db import transaction

@transaction.atomic
def update_task_pessimistic(task_id, new_title):
    """Pessimistic locking with row lock"""
    # Lock the row (other transactions wait)
    task = Task.objects.select_for_update().get(id=task_id)

    # Now we have exclusive lock
    # Other transactions trying select_for_update() will wait

    task.title = new_title
    task.save()

    # Lock released when transaction commits

# Nowait variant (fail fast)
try:
    task = Task.objects.select_for_update(nowait=True).get(id=task_id)
except DatabaseError:
    raise ResourceLockedException("Task is being edited by someone else")

# Skip locked rows
available_tasks = Task.objects.select_for_update(skip_locked=True).filter(
    status='pending'
)
# Returns only unlocked tasks

# Lock specific fields (PostgreSQL)
task = Task.objects.select_for_update(of=('self',)).get(id=task_id)

# Distributed locking with Redis
import redis
from contextlib import contextmanager

class RedisLock:
    def __init__(self, redis_client, key, timeout=10):
        self.redis = redis_client
        self.key = f"lock:{key}"
        self.timeout = timeout

    @contextmanager
    def acquire(self):
        """Acquire distributed lock"""
        # Try to set lock
        acquired = self.redis.set(
            self.key,
            "locked",
            nx=True,  # Only if doesn't exist
            ex=self.timeout  # Auto-expire
        )

        if not acquired:
            raise LockNotAcquiredError(f"Could not acquire lock on {self.key}")

        try:
            yield
        finally:
            # Release lock
            self.redis.delete(self.key)

# Usage
redis_client = redis.Redis()
lock = RedisLock(redis_client, f"task:{task_id}")

with lock.acquire():
    # Exclusive access
    task = Task.objects.get(id=task_id)
    task.process()
```

**Comparison:**

| Aspect | Optimistic | Pessimistic |
|--------|-----------|-------------|
| **When locks** | At commit | At read |
| **Conflicts** | Detected on save | Prevented upfront |
| **Performance** | Better (no locks) | Slower (waiting) |
| **Concurrency** | Higher | Lower |
| **Use case** | Low conflict rate | High conflict rate |
| **Failure mode** | Retry needed | Waiting/timeout |
| **Example** | Web forms | Inventory updates |

---

### 34. How does Two Phase Commit work?

**Two Phase Commit (2PC)** ensures atomic commits across distributed databases.

```
Two Phase Commit:

PHASE 1: PREPARE
Coordinator ──▶ Participant A: "Can you commit?"
            ──▶ Participant B: "Can you commit?"
            ──▶ Participant C: "Can you commit?"

Responses:
Participant A: "Yes, ready"
Participant B: "Yes, ready"
Participant C: "Yes, ready"

PHASE 2: COMMIT
Coordinator ──▶ Participant A: "COMMIT"
            ──▶ Participant B: "COMMIT"
            ──▶ Participant C: "COMMIT"

All commit or all abort (atomic)
```

**Implementation:**

```python
from enum import Enum
import uuid

class TransactionState(Enum):
    PREPARED = "prepared"
    COMMITTED = "committed"
    ABORTED = "aborted"

class TwoPhaseCommitCoordinator:
    def __init__(self, participants):
        """
        participants: List of database connections
        """
        self.participants = participants
        self.transaction_id = str(uuid.uuid4())

    def execute_transaction(self, operations):
        """
        Execute distributed transaction
        operations: [(db_alias, sql, params), ...]
        """
        try:
            # PHASE 1: PREPARE
            if not self.prepare_phase(operations):
                self.abort()
                return False

            # PHASE 2: COMMIT
            self.commit_phase()
            return True

        except Exception as e:
            self.abort()
            raise

    def prepare_phase(self, operations):
        """Phase 1: Ask all participants to prepare"""
        from django.db import connections

        prepared = []

        for db_alias, sql, params in operations:
            connection = connections[db_alias]

            try:
                with connection.cursor() as cursor:
                    # Execute operation but don't commit
                    cursor.execute(sql, params)

                    # Ask if ready to commit
                    cursor.execute(f"PREPARE TRANSACTION '{self.transaction_id}'")

                prepared.append(db_alias)

            except Exception as e:
                # Prepare failed, abort all
                for db in prepared:
                    self.abort_participant(db)
                return False

        # All participants prepared successfully
        return True

    def commit_phase(self):
        """Phase 2: Tell all participants to commit"""
        from django.db import connections

        for db_alias in self.participants:
            connection = connections[db_alias]

            with connection.cursor() as cursor:
                cursor.execute(f"COMMIT PREPARED '{self.transaction_id}'")

    def abort(self):
        """Abort transaction on all participants"""
        from django.db import connections

        for db_alias in self.participants:
            self.abort_participant(db_alias)

    def abort_participant(self, db_alias):
        """Abort on single participant"""
        from django.db import connections
        connection = connections[db_alias]

        try:
            with connection.cursor() as cursor:
                cursor.execute(f"ROLLBACK PREPARED '{self.transaction_id}'")
        except:
            pass  # Already aborted or not prepared

# Usage
coordinator = TwoPhaseCommitCoordinator(['db1', 'db2', 'db3'])

operations = [
    ('db1', 'UPDATE accounts SET balance = balance - %s WHERE id = %s', [100, 1]),
    ('db2', 'UPDATE accounts SET balance = balance + %s WHERE id = %s', [100, 2]),
    ('db3', 'INSERT INTO transactions (from_id, to_id, amount) VALUES (%s, %s, %s)', [1, 2, 100]),
]

try:
    coordinator.execute_transaction(operations)
    print("Transaction committed across all databases")
except Exception as e:
    print(f"Transaction aborted: {e}")
```

**Problems with 2PC:**

1. **Blocking**: Participants hold locks during prepare (slow)
2. **Single point of failure**: Coordinator failure blocks all
3. **Not highly available**: Can't commit during partition

**Alternative: Saga Pattern (Better for Microservices)**

```python
class SagaOrchestrator:
    """
    Saga: Long-running transactions with compensating actions
    """

    def execute_booking_saga(self, booking_data):
        """Book flight + hotel + car (distributed transaction)"""

        completed_steps = []

        try:
            # Step 1: Book flight
            flight = self.book_flight(booking_data['flight'])
            completed_steps.append(('flight', flight['id']))

            # Step 2: Book hotel
            hotel = self.book_hotel(booking_data['hotel'])
            completed_steps.append(('hotel', hotel['id']))

            # Step 3: Book car
            car = self.book_car(booking_data['car'])
            completed_steps.append(('car', car['id']))

            # All steps successful
            return {
                'status': 'success',
                'flight': flight,
                'hotel': hotel,
                'car': car
            }

        except Exception as e:
            # Compensate (rollback) completed steps
            self.compensate(completed_steps)

            return {
                'status': 'failed',
                'error': str(e)
            }

    def book_flight(self, flight_data):
        """Book flight (can fail)"""
        response = requests.post(
            'http://flight-service/book',
            json=flight_data
        )
        response.raise_for_status()
        return response.json()

    def book_hotel(self, hotel_data):
        """Book hotel (can fail)"""
        response = requests.post(
            'http://hotel-service/book',
            json=hotel_data
        )
        response.raise_for_status()
        return response.json()

    def compensate(self, completed_steps):
        """Undo completed steps (compensating transactions)"""
        for step_type, step_id in reversed(completed_steps):
            try:
                if step_type == 'flight':
                    self.cancel_flight(step_id)
                elif step_type == 'hotel':
                    self.cancel_hotel(step_id)
                elif step_type == 'car':
                    self.cancel_car(step_id)
            except Exception as e:
                # Log compensation failure
                logger.error(f"Compensation failed for {step_type} {step_id}: {e}")

    def cancel_flight(self, flight_id):
        """Compensating action for flight booking"""
        requests.post(
            f'http://flight-service/cancel/{flight_id}'
        )
```

---

### 35. What is the difference between CAP theorem components?

**CAP Theorem**: Distributed system can have at most 2 of 3:
- **C**onsistency
- **A**vailability  
- **P**artition tolerance

```
         Consistency
              △
             /│\
            / │ \
           /  │  \
          /   │   \
         /  CP│AP  \
        /     │     \
       /      │      \
      /───────┼───────\
     /        │        \
Partition     │     Availability
Tolerance     │
              │
             CA
      (Single node only)
```

**Consistency (C):**
```python
# All nodes see same data at same time

# PostgreSQL (Strong Consistency)
@transaction.atomic
def transfer_money(from_account, to_account, amount):
    # All reads see latest data
    from_acc = Account.objects.select_for_update().get(id=from_account)
    to_acc = Account.objects.select_for_update().get(id=to_account)

    from_acc.balance -= amount
    from_acc.save()

    to_acc.balance += amount
    to_acc.save()

    # Any subsequent read sees updated balances
    # No stale data
```

**Availability (A):**
```python
# System always responds (even if stale)

# DynamoDB (High Availability)
# Read even during network partition
user = table.get_item(Key={'id': user_id})
# Always returns something (might be stale)

# Write accepted even if some nodes unreachable
table.put_item(
    Item={'id': user_id, 'status': 'active'},
    ConsistentRead=False  # Eventual consistency
)
# Write accepted, replicates eventually
```

**Partition Tolerance (P):**
```python
# System works despite network splits

# Cassandra (Partition Tolerant)
# Network splits cluster:
# US West nodes │ Network Partition │ US East nodes

# US West can still:
# - Accept writes
# - Serve reads
# - Function independently

# When partition heals:
# - Data reconciles
# - Conflicts resolved
# - System converges
```

**CAP Examples:**

```python
# CP System (MongoDB, HBase)
# Consistency + Partition Tolerance
# Sacrifices: Availability

# During partition:
# - Minority partition rejects writes ❌ (unavailable)
# - Majority partition accepts writes ✓
# - Guarantees consistency (all nodes agree)

class CPDatabase:
    def write(self, key, value):
        # Need majority of nodes to accept
        acks = 0
        required = len(self.nodes) // 2 + 1

        for node in self.nodes:
            try:
                node.write(key, value)
                acks += 1
            except NetworkError:
                pass

        if acks >= required:
            return "SUCCESS"
        else:
            return "UNAVAILABLE"  # Reject write (no majority)

# AP System (Cassandra, DynamoDB)
# Availability + Partition Tolerance
# Sacrifices: Consistency

# During partition:
# - All partitions accept writes ✓ (available)
# - May have conflicting data ❌
# - Resolves conflicts when partition heals

class APDatabase:
    def write(self, key, value):
        # Accept write even if only one node reachable
        for node in self.nodes:
            try:
                node.write(key, value)
                return "SUCCESS"  # Return immediately
            except NetworkError:
                continue

        return "SUCCESS"  # Even if all fail, queue for later

    def read(self, key):
        # Return any available data (might be stale)
        for node in self.nodes:
            try:
                return node.read(key)
            except NetworkError:
                continue

# CA System (Single PostgreSQL)
# Consistency + Availability
# Sacrifices: Partition Tolerance

# Single node:
# - Consistent ✓ (one source of truth)
# - Available ✓ (as long as node up)
# - Not partition tolerant ❌ (if network splits, can't work)
```

**Real-world Choices:**

```python
# Choose CP when:
# - Financial transactions (banking)
# - Inventory management
# - Strong consistency required

# Example: Django + PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # Single source of truth
        # ACID transactions
        # Strong consistency
    }
}

# Choose AP when:
# - Social media feeds
# - Analytics/metrics
# - User profiles
# - High availability critical

# Example: Django + Cassandra
from cassandra.cluster import Cluster

cluster = Cluster(['cassandra1', 'cassandra2', 'cassandra3'])
session = cluster.connect('taskmaster')

# Always available
# Eventual consistency
# Partition tolerant

# Hybrid approach:
# - Use PostgreSQL (CP) for critical data
# - Use Cassandra (AP) for metrics/analytics
# - Use Redis (CP with replication) for caching
```

---

### 36. How does Bloom Filter work?

**Bloom Filter** is a space-efficient probabilistic data structure to test set membership.

```
Bloom Filter:
- Can say: "Definitely NOT in set" (100% accurate)
- Can say: "Possibly in set" (may have false positives)
- Cannot say: "Definitely in set"

Add "hello":
1. Hash "hello" → positions [3, 7, 11]
2. Set bits at [3, 7, 11] to 1

Bit Array:
[0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0]
        ↑       ↑       ↑
       h3      h2      h1

Check "world":
1. Hash "world" → positions [2, 7, 14]
2. Check bits at [2, 7, 14]
3. Bit 7 is 1, but bits 2,14 are 0
4. "world" is NOT in set (accurate)

Check "hello":
1. Hash "hello" → positions [3, 7, 11]
2. All bits are 1
3. "hello" is POSSIBLY in set (might be false positive)
```

**Implementation:**

```python
import mmh3  # MurmurHash3
from bitarray import bitarray

class BloomFilter:
    def __init__(self, size=1000000, hash_count=7):
        """
        size: Bit array size
        hash_count: Number of hash functions
        """
        self.size = size
        self.hash_count = hash_count
        self.bit_array = bitarray(size)
        self.bit_array.setall(0)

    def add(self, item):
        """Add item to filter"""
        for seed in range(self.hash_count):
            # Generate multiple hashes
            index = mmh3.hash(item, seed) % self.size
            self.bit_array[index] = 1

    def check(self, item):
        """Check if item might be in set"""
        for seed in range(self.hash_count):
            index = mmh3.hash(item, seed) % self.size
            if self.bit_array[index] == 0:
                return False  # Definitely NOT in set

        return True  # Possibly in set (might be false positive)

# Usage
bloom = BloomFilter(size=1000000, hash_count=7)

# Add items
bloom.add("user:123")
bloom.add("user:456")
bloom.add("user:789")

# Check membership
if bloom.check("user:123"):
    print("Possibly exists")  # Check database to confirm

if not bloom.check("user:999"):
    print("Definitely doesn't exist")  # Skip database query

# Django caching with Bloom filter
class BloomCachedManager(models.Manager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bloom = BloomFilter(size=10000000)

        # Populate bloom filter with existing IDs
        for task_id in self.values_list('id', flat=True):
            self.bloom.add(str(task_id))

    def get(self, *args, **kwargs):
        task_id = kwargs.get('id')

        # Check bloom filter first
        if not self.bloom.check(str(task_id)):
            raise self.model.DoesNotExist(
                f"Task {task_id} definitely doesn't exist"
            )

        # Might exist, query database
        return super().get(*args, **kwargs)

class Task(models.Model):
    objects = BloomCachedManager()
```

**Use Cases:**

```python
# 1. Prevent database lookups for non-existent data
def check_username_available(username):
    # First check bloom filter (fast)
    if taken_usernames_bloom.check(username):
        # Might be taken, check database
        return not User.objects.filter(username=username).exists()
    else:
        # Definitely available
        return True

# 2. Duplicate detection in web crawler
class WebCrawler:
    def __init__(self):
        self.visited_bloom = BloomFilter(size=100000000)  # 100M URLs

    def crawl(self, url):
        # Quick check if already visited
        if self.visited_bloom.check(url):
            return  # Probably visited, skip

        # Definitely not visited, crawl
        self.crawl_url(url)
        self.visited_bloom.add(url)

# 3. Cache miss reduction
class CacheWithBloom:
    def __init__(self):
        self.cache = {}
        self.bloom = BloomFilter()

    def get(self, key):
        # Check bloom filter first (fast)
        if not self.bloom.check(key):
            # Definitely not in cache
            return None

        # Might be in cache, check actual cache
        return self.cache.get(key)

    def set(self, key, value):
        self.cache[key] = value
        self.bloom.add(key)

# 4. Spam filtering
spam_domains_bloom = BloomFilter()
# Add known spam domains
for domain in ['spam1.com', 'spam2.com', ...]:
    spam_domains_bloom.add(domain)

def is_spam(email_domain):
    if spam_domains_bloom.check(email_domain):
        # Possibly spam, do detailed check
        return detailed_spam_check(email_domain)
    else:
        # Definitely not spam
        return False
```

**False Positive Rate:**

```python
import math

def optimal_bloom_size(n, p):
    """
    Calculate optimal bloom filter size
    n: Expected number of items
    p: Desired false positive rate (e.g., 0.01 for 1%)
    """
    m = -(n * math.log(p)) / (math.log(2) ** 2)
    return int(m)

def optimal_hash_count(m, n):
    """
    Calculate optimal number of hash functions
    m: Bloom filter size
    n: Number of items
    """
    k = (m / n) * math.log(2)
    return int(k)

# Example: Store 1 million items with 1% false positive rate
n = 1000000  # 1 million items
p = 0.01  # 1% false positive rate

size = optimal_bloom_size(n, p)  # ~9.6 million bits (~1.2 MB)
hash_count = optimal_hash_count(size, n)  # ~7 hash functions

bloom = BloomFilter(size=size, hash_count=hash_count)
```

---

### 37. What is the difference between WebSocket and HTTP?

**HTTP**: Request-response protocol (client initiates)
**WebSocket**: Full-duplex communication (bidirectional, persistent)

```
HTTP (Request-Response):
Client ──Request──▶ Server
       ◀─Response── 

Connection closes after response

WebSocket (Persistent):
Client ──Upgrade──▶ Server
       ◀──Accept──
       │           │
       ├───Data───▶│  Bidirectional
       │◀──Data───┤  
       ├───Data───▶│  Real-time
       │◀──Data───┤
       │           │  Connection stays open
```

**HTTP Example:**

```python
# Client must poll for updates
import requests

def get_notifications():
    # New request every time
    response = requests.get('http://api.example.com/notifications/')
    return response.json()

# Polling: Check every 30 seconds
import time

while True:
    notifications = get_notifications()
    display(notifications)
    time.sleep(30)  # Wait 30 seconds

# Problems:
# - High latency (30 second delay)
# - Wasted requests (if no new data)
# - Server overhead (many requests)
```

**WebSocket Example:**

```python
# Django Channels
# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['user'].id

        # Join user-specific group
        await self.channel_layer.group_add(
            f'user_{self.user_id}',
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            f'user_{self.user_id}',
            self.channel_name
        )

    async def receive(self, text_data):
        """Receive message from WebSocket"""
        data = json.loads(text_data)
        # Process client message

    async def send_notification(self, event):
        """Send notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message']
        }))

# Send notification from Django
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def create_task(request):
    task = Task.objects.create(**request.data)

    # Push notification via WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{request.user.id}',
        {
            'type': 'send_notification',
            'message': f'Task "{task.title}" created'
        }
    )

# JavaScript client
const socket = new WebSocket('ws://localhost:8000/ws/notifications/');

socket.onmessage = (e) => {
    const data = JSON.parse(e.data);
    displayNotification(data.message);  // Real-time update!
};

socket.send(JSON.stringify({
    'action': 'subscribe',
    'topics': ['tasks', 'projects']
}));
```

**Comparison:**

| Feature | HTTP | WebSocket |
|---------|------|-----------|
| **Connection** | New per request | Persistent |
| **Direction** | Client → Server only | Bidirectional |
| **Overhead** | High (headers each request) | Low (established once) |
| **Latency** | Higher (request/response) | Lower (real-time) |
| **Use Case** | APIs, web pages | Chat, live updates, gaming |
| **Protocol** | http:// | ws:// or wss:// |
| **Scaling** | Easy (stateless) | Harder (stateful connections) |

**Long Polling (HTTP Alternative):**

```python
# Server holds request until data available
from django.http import JsonResponse
import time

def long_poll(request):
    last_id = int(request.GET.get('last_id', 0))
    timeout = 30  # 30 seconds
    start = time.time()

    while time.time() - start < timeout:
        # Check for new notifications
        notifications = Notification.objects.filter(
            user=request.user,
            id__gt=last_id
        )

        if notifications.exists():
            # Return immediately if data available
            return JsonResponse({
                'notifications': list(notifications.values())
            })

        time.sleep(1)  # Check every second

    # Timeout, return empty
    return JsonResponse({'notifications': []})

# Client immediately reconnects
async function poll() {
    const response = await fetch(`/poll/?last_id=${lastId}`);
    const data = await response.json();

    if (data.notifications.length > 0) {
        displayNotifications(data.notifications);
        lastId = data.notifications[data.notifications.length - 1].id;
    }

    poll();  // Immediately reconnect
}
```

**Server-Sent Events (SSE) - Simpler Alternative:**

```python
# One-way: Server → Client only
from django.http import StreamingHttpResponse
import time
import json

def event_stream():
    """Send server-sent events"""
    while True:
        # Get new data
        notifications = Notification.objects.filter(
            created_at__gt=datetime.now() - timedelta(seconds=1)
        )

        for notification in notifications:
            yield f"data: {json.dumps({'message': notification.message})}\n\n"

        time.sleep(1)

def sse_view(request):
    return StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )

# JavaScript client
const eventSource = new EventSource('/sse/');

eventSource.onmessage = (e) => {
    const data = JSON.parse(e.data);
    displayNotification(data.message);
};
```

---

### 38. How does Service Mesh work?

**Service Mesh** manages service-to-service communication in microservices (traffic, security, observability).

```
Without Service Mesh:
Service A ──▶ Service B
(Each service handles: routing, retries, security, monitoring)

With Service Mesh:
Service A ──▶ Sidecar Proxy ──▶ Sidecar Proxy ──▶ Service B
              (Handles all      (Handles all
               communication)     communication)

Service Mesh = Network of sidecar proxies
```

**Istio Service Mesh:**

```yaml
# 1. Install Istio
# kubectl apply -f istio-install.yaml

# 2. Enable sidecar injection
kubectl label namespace default istio-injection=enabled

# 3. Deploy Django application
apiVersion: apps/v1
kind: Deployment
metadata:
  name: taskmaster-api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: taskmaster:latest
        ports:
        - containerPort: 8000

# Istio automatically injects sidecar proxy

# 4. Traffic management
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: taskmaster
spec:
  hosts:
  - taskmaster-api
  http:
  - match:
    - headers:
        version:
          exact: v2
    route:
    - destination:
        host: taskmaster-api
        subset: v2
      weight: 100
  - route:
    - destination:
        host: taskmaster-api
        subset: v1
      weight: 90
    - destination:
        host: taskmaster-api
        subset: v2
      weight: 10  # 10% to new version (canary)

# 5. Retry policy
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: taskmaster
spec:
  http:
  - route:
    - destination:
        host: taskmaster-api
    retries:
      attempts: 3
      perTryTimeout: 2s
      retryOn: 5xx,reset,connect-failure

# 6. Circuit breaker
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: taskmaster
spec:
  host: taskmaster-api
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        maxRequestsPerConnection: 2
    outlierDetection:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s

# 7. Mutual TLS (mTLS) - Automatic encryption
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
spec:
  mtls:
    mode: STRICT  # All communication encrypted
```

**Django with Service Mesh:**

```python
# No code changes needed!
# Service mesh handles:
# - Load balancing
# - Retries
# - Circuit breaking
# - mTLS encryption
# - Distributed tracing
# - Metrics

# Just make normal HTTP calls
import requests

def call_notification_service(message):
    # Sidecar proxy handles:
    # - Service discovery
    # - Load balancing
    # - Retries (if fails)
    # - Circuit breaking (if service down)
    # - Encryption (mTLS)
    # - Tracing (automatic span creation)

    response = requests.post(
        'http://notification-service:8000/send',
        json={'message': message}
    )
    return response.json()

# Distributed tracing automatically captured
# Metrics automatically collected
# No application code changes!
```

**Service Mesh Features:**

1. **Traffic Management**
   - Load balancing
   - A/B testing
   - Canary deployments
   - Traffic splitting

2. **Security**
   - Mutual TLS (mTLS)
   - Authentication
   - Authorization

3. **Observability**
   - Distributed tracing
   - Metrics
   - Logging

4. **Resilience**
   - Retries
   - Timeouts
   - Circuit breaking
   - Fault injection

---

### 39. What is the difference between Blue Green and Canary deployment?

**Blue-Green**: Switch all traffic at once (instant rollback)
**Canary**: Gradual rollout (incremental traffic shift)

```
BLUE-GREEN:
┌──────────────────────────────────┐
│  OLD VERSION (Blue)              │
│  ┌─────┬─────┬─────┐            │
│  │ v1  │ v1  │ v1  │ ◀─ 100%    │
│  └─────┴─────┴─────┘            │
└──────────────────────────────────┘
              │ Deploy
              ▼
┌──────────────────────────────────┐
│  NEW VERSION (Green)             │
│  ┌─────┬─────┬─────┐            │
│  │ v2  │ v2  │ v2  │ ◀─ 100%    │
│  └─────┴─────┴─────┘            │
└──────────────────────────────────┘
Switch traffic instantly
Keep blue for rollback

CANARY:
Step 1: 5% to new version
┌─────┬─────┬─────┬─────┬─────┐
│ v1  │ v1  │ v1  │ v1  │ v2  │
└─────┴─────┴─────┴─────┴─────┘
 95%                      5%

Step 2: 25% to new version
┌─────┬─────┬─────┬─────┬─────┐
│ v1  │ v1  │ v1  │ v2  │ v2  │
└─────┴─────┴─────┴─────┴─────┘
 75%               25%

Step 3: 100% to new version
┌─────┬─────┬─────┬─────┬─────┐
│ v2  │ v2  │ v2  │ v2  │ v2  │
└─────┴─────┴─────┴─────┴─────┘
100%

Gradual, monitor metrics at each step
```

**Blue-Green with Kubernetes:**

```yaml
# Blue deployment (current production)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: taskmaster-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: taskmaster
      version: blue
  template:
    metadata:
      labels:
        app: taskmaster
        version: blue
    spec:
      containers:
      - name: api
        image: taskmaster:v1.0

---
# Service points to blue
apiVersion: v1
kind: Service
metadata:
  name: taskmaster
spec:
  selector:
    app: taskmaster
    version: blue  # Traffic to blue
  ports:
  - port: 80
    targetPort: 8000

---
# Green deployment (new version)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: taskmaster-green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: taskmaster
      version: green
  template:
    metadata:
      labels:
        app: taskmaster
        version: green
    spec:
      containers:
      - name: api
        image: taskmaster:v2.0  # New version

# Deploy green, test it
# When ready, switch service:
# kubectl patch service taskmaster -p '{"spec":{"selector":{"version":"green"}}}'
# Instant switch to green
# Keep blue running for quick rollback
```

**Canary with Istio:**

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: taskmaster
spec:
  hosts:
  - taskmaster
  http:
  # Step 1: 5% canary
  - match:
    - headers:
        canary:
          exact: "true"
    route:
    - destination:
        host: taskmaster
        subset: v2
      weight: 100
  - route:
    - destination:
        host: taskmaster
        subset: v1
      weight: 95
    - destination:
        host: taskmaster
        subset: v2
      weight: 5  # 5% to canary

---
# Step 2: Monitor metrics
# If good, increase to 25%
# Step 3: Increase to 50%
# Step 4: Increase to 100%

# Automated canary with Flagger
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: taskmaster
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: taskmaster
  service:
    port: 8000
  analysis:
    interval: 1m
    threshold: 5  # Number of checks
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99  # Must have 99% success rate
    - name: request-duration
      thresholdRange:
        max: 500  # Max 500ms latency
  canaryAnalysis:
    stepWeight: 10  # Increase by 10% each step
    maxWeight: 50  # Max 50% to canary
```

**Django Canary Implementation:**

```python
# Feature flag based canary
from django.conf import settings

def is_canary_user(user):
    """Determine if user should see new version"""
    # 1. Internal users first
    if user.email.endswith('@company.com'):
        return True

    # 2. Beta opt-in users
    if user.profile.beta_tester:
        return True

    # 3. Percentage rollout
    canary_percentage = settings.CANARY_PERCENTAGE  # e.g., 10
    user_hash = hash(user.id) % 100
    return user_hash < canary_percentage

# In view
def task_list(request):
    if is_canary_user(request.user):
        # New version
        return new_task_list_v2(request)
    else:
        # Old version
        return old_task_list_v1(request)

# Gradual rollout
# Day 1: CANARY_PERCENTAGE = 5   (5% users)
# Day 2: CANARY_PERCENTAGE = 10  (10% users)
# Day 3: CANARY_PERCENTAGE = 25  (25% users)
# Day 4: CANARY_PERCENTAGE = 50  (50% users)
# Day 5: CANARY_PERCENTAGE = 100 (all users)
```

**Comparison:**

| Aspect | Blue-Green | Canary |
|--------|------------|--------|
| **Rollout Speed** | Instant (all at once) | Gradual (incremental) |
| **Risk** | Higher (all users affected) | Lower (few users first) |
| **Rollback** | Instant (switch back) | Stop rollout |
| **Resource Cost** | 2x (both versions running) | 1-2x (overlapping period) |
| **Testing** | Staging environment | Production (real users) |
| **Complexity** | Simple | Complex (traffic splitting) |
| **Best For** | Low-risk changes | High-risk changes |

---

### 40. How does Distributed Cache work?

**Distributed Cache** spreads cache data across multiple servers for scalability.

```
Single Cache (Limited):
┌────────┐      ┌───────┐
│ Server │─────▶│ Redis │ (single point, limited capacity)
└────────┘      └───────┘

Distributed Cache (Scalable):
┌────────┐      ┌─────────┬─────────┬─────────┐
│ Server │─────▶│ Redis 1 │ Redis 2 │ Redis 3 │
└────────┘      └─────────┴─────────┴─────────┘
                 Key A       Key B      Key C
                (Sharded across nodes)
```

**Redis Cluster:**

```python
# Install: pip install redis-py-cluster

from rediscluster import RedisCluster

# Configure cluster
startup_nodes = [
    {"host": "redis1", "port": "6379"},
    {"host": "redis2", "port": "6379"},
    {"host": "redis3", "port": "6379"},
]

# Connect to cluster
cache = RedisCluster(
    startup_nodes=startup_nodes,
    decode_responses=True,
    skip_full_coverage_check=True
)

# Usage (same as single Redis)
cache.set('user:123', json.dumps(user_data))
user = json.loads(cache.get('user:123'))

# Data automatically sharded across nodes
# cache.set('key1', val)  → Redis 1
# cache.set('key2', val)  → Redis 2
# cache.set('key3', val)  → Redis 3

# Django integration
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': [
            'redis://redis1:6379/0',
            'redis://redis2:6379/0',
            'redis://redis3:6379/0',
        ],
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'REDIS_CLIENT_CLASS': 'rediscluster.RedisCluster',
        }
    }
}

# Use normally
from django.core.cache import cache

cache.set('task:123', task_data, timeout=3600)
task = cache.get('task:123')
```

**Memcached Cluster:**

```python
# pip install pymemcache

from pymemcache.client.hash import HashClient

# Configure servers
servers = [
    ('memcache1', 11211),
    ('memcache2', 11211),
    ('memcache3', 11211),
]

# Client automatically distributes keys
client = HashClient(servers)

# Set/Get (automatically routed to correct server)
client.set('user:123', user_data)
user = client.get('user:123')

# Django configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': [
            'memcache1:11211',
            'memcache2:11211',
            'memcache3:11211',
        ],
    }
}
```

**Consistent Hashing (Prevent Rehashing):**

```python
# Problem with simple hashing:
# server = hash(key) % num_servers
# If num_servers changes, ALL keys rehash!

# Solution: Consistent hashing
class DistributedCache:
    def __init__(self, servers):
        self.ring = ConsistentHashRing(servers)
        self.caches = {
            server: redis.Redis(host=server)
            for server in servers
        }

    def get(self, key):
        server = self.ring.get_node(key)
        return self.caches[server].get(key)

    def set(self, key, value, expire=3600):
        server = self.ring.get_node(key)
        return self.caches[server].setex(key, expire, value)

    def add_server(self, new_server):
        """Add new cache server (minimal rehashing)"""
        self.ring.add_node(new_server)
        self.caches[new_server] = redis.Redis(host=new_server)
        # Only ~1/N keys move (not all!)
```

**Cache Replication (High Availability):**

```python
# Redis Sentinel for automatic failover
from redis.sentinel import Sentinel

sentinel = Sentinel([
    ('sentinel1', 26379),
    ('sentinel2', 26379),
    ('sentinel3', 26379),
], socket_timeout=0.1)

# Get master for writes
master = sentinel.master_for('mymaster', socket_timeout=0.1)
master.set('key', 'value')

# Get slave for reads (load balancing)
slave = sentinel.slave_for('mymaster', socket_timeout=0.1)
value = slave.get('key')

# Automatic failover:
# If master dies, sentinel promotes slave to master
```

**Cache Invalidation Strategies:**

```python
# 1. Time-based (TTL)
cache.set('user:123', user, timeout=3600)  # Expires after 1 hour

# 2. Event-based (on update)
@receiver(post_save, sender=User)
def invalidate_user_cache(sender, instance, **kwargs):
    # Invalidate all related caches
    cache.delete(f'user:{instance.id}')
    cache.delete(f'user_tasks:{instance.id}')
    cache.delete('user_list')  # List cache

# 3. Write-through (update cache on write)
def update_user(user_id, data):
    user = User.objects.get(id=user_id)
    user.name = data['name']
    user.save()

    # Update cache immediately
    cache.set(f'user:{user_id}', user, timeout=3600)

# 4. Tagging (group invalidation)
from django.core.cache import cache

cache.set('task:1', task1, tags=['project:5', 'user:10'])
cache.set('task:2', task2, tags=['project:5', 'user:11'])

# Invalidate all tasks for project 5
cache.delete_pattern('*project:5*')
```

**Monitoring Distributed Cache:**

```python
def get_cache_stats():
    """Get stats from all cache nodes"""
    stats = []

    for server in cache_servers:
        client = redis.Redis(host=server)
        info = client.info('stats')

        stats.append({
            'server': server,
            'hits': info['keyspace_hits'],
            'misses': info['keyspace_misses'],
            'hit_rate': info['keyspace_hits'] / (info['keyspace_hits'] + info['keyspace_misses']),
            'memory_used': info['used_memory_human'],
            'connected_clients': info['connected_clients'],
        })

    return stats

# Alert if hit rate < 80%
for stat in get_cache_stats():
    if stat['hit_rate'] < 0.8:
        send_alert(f"Low cache hit rate on {stat['server']}: {stat['hit_rate']}")
```

---

## Summary & Conclusion

You now have comprehensive answers to all 40 system design questions! Each answer includes:

✅ **Clear explanations** of concepts  
✅ **ASCII diagrams** for visual understanding  
✅ **Python/Django code examples** with real implementations  
✅ **Comparison tables** highlighting differences  
✅ **Real-world use cases** and best practices  
✅ **Performance considerations** and trade-offs

### Quick Reference:

**Infrastructure (1-6):** API Gateway, Load Balancer, Proxies, Scaling, Partitioning, Rate Limiting  
**Security (7-10):** SSO, Kafka, Message Queues, Auth (JWT/OAuth/SAML)  
**Databases (11-14):** SQL vs NoSQL, CDN, Sync vs Async, Sharding  
**APIs (15-20):** REST vs GraphQL, Caching, Consistency, Message Queues, TCP vs UDP, Replication  
**Distributed Systems (21-30):** Stateful vs Stateless, Circuit Breaker, Auth vs Authz, Tracing, ACID vs BASE, Service Discovery, Push vs Pull, Indexing, Batch vs Stream, Consistent Hashing  
**Advanced Patterns (31-40):** RPC vs REST, Leader Election, Locking, 2PC, CAP Theorem, Bloom Filters, WebSockets, Service Mesh, Deployment Strategies, Distributed Cache

### Interview Preparation Tips:

1. **Practice drawing diagrams** - Interviewers love visual explanations
2. **Know trade-offs** - Understand when to use each pattern
3. **Real-world examples** - Reference your TaskMaster project
4. **Code samples** - Be ready to write code on whiteboard
5. **Ask clarifying questions** - Requirements affect design choices

Good luck with your interviews! 🚀

---

*All questions comprehensively answered with production-ready examples!*
