# Python & Django Interview Questions - ANSWERS

Complete answer guide for all 300 interview questions with code examples and detailed explanations.

---

## Python Fundamentals

### Basic Python

**1. What are Python decorators and how do you use them?**

Decorators are functions that modify the behavior of other functions or classes. They use the `@` syntax.

```python
# Basic decorator
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Before function")
        result = func(*args, **kwargs)
        print("After function")
        return result
    return wrapper

@my_decorator
def greet(name):
    print(f"Hello {name}")

# @property - converts method to attribute
class User:
    def __init__(self, first, last):
        self.first = first
        self.last = last

    @property
    def full_name(self):
        return f"{self.first} {self.last}"

# @staticmethod - doesn't receive self or cls
class Math:
    @staticmethod
    def add(x, y):
        return x + y

# @classmethod - receives cls instead of self
class Person:
    count = 0

    @classmethod
    def increment_count(cls):
        cls.count += 1
```

**2. Explain the difference between `__str__` and `__repr__` methods**

- `__str__()`: Returns human-readable string representation (for end users)
- `__repr__()`: Returns unambiguous string representation (for developers/debugging)

```python
class Task:
    def __init__(self, title, status):
        self.title = title
        self.status = status

    def __str__(self):
        return f"{self.title} - {self.status}"

    def __repr__(self):
        return f"Task(title='{self.title}', status='{self.status}')"

task = Task("Fix bug", "in_progress")
print(str(task))   # "Fix bug - in_progress" (readable)
print(repr(task))  # "Task(title='Fix bug', status='in_progress')" (recreatable)
```

**3. What is the difference between `@staticmethod` and `@classmethod`?**

- `@staticmethod`: Doesn't receive implicit first argument. Can't access class or instance data.
- `@classmethod`: Receives class as first argument (`cls`). Can access/modify class state.

```python
class MyClass:
    class_var = 10

    @staticmethod
    def static_method():
        return "Static - no access to class/instance"

    @classmethod
    def class_method(cls):
        return f"Class method - can access {cls.class_var}"

    def instance_method(self):
        return f"Instance method - can access {self.class_var}"
```

**4. What are Python's built-in data structures?**

- **List**: Ordered, mutable collection: `[1, 2, 3]`
- **Tuple**: Ordered, immutable collection: `(1, 2, 3)`
- **Set**: Unordered, unique elements: `{1, 2, 3}`
- **Dictionary**: Key-value pairs: `{"key": "value"}`
- **frozenset**: Immutable set: `frozenset([1, 2, 3])`

**5. Explain list comprehensions and generator expressions**

```python
# List comprehension - creates entire list in memory
squares = [x**2 for x in range(10)]
evens = [x for x in range(10) if x % 2 == 0]

# Generator expression - lazy evaluation, memory efficient
squares_gen = (x**2 for x in range(10))
evens_gen = (x for x in range(10) if x % 2 == 0)

# Nested comprehension
matrix = [[i*j for j in range(3)] for i in range(3)]

# Dictionary comprehension
word_lengths = {word: len(word) for word in ['apple', 'banana', 'cherry']}
```

**6. What is the difference between `is` and `==` in Python?**

- `==` compares values (equality)
- `is` compares object identity (memory address)

```python
a = [1, 2, 3]
b = [1, 2, 3]
c = a

a == b  # True (same values)
a is b  # False (different objects)
a is c  # True (same object)

# Special case: small integers and strings are cached
x = 256
y = 256
x is y  # True (cached)

x = 1000
y = 1000
x is y  # False (not cached)
```

**7. Explain mutable vs immutable objects in Python**

- **Immutable**: Cannot be changed after creation (int, float, str, tuple, frozenset)
- **Mutable**: Can be modified (list, dict, set, custom objects)

```python
# Immutable - creates new object
s = "hello"
s += " world"  # New string created

# Mutable - modifies in place
lst = [1, 2, 3]
lst.append(4)  # Same object modified

# Important for default arguments
def bad_function(lst=[]):  # DON'T DO THIS
    lst.append(1)
    return lst

def good_function(lst=None):  # DO THIS
    if lst is None:
        lst = []
    lst.append(1)
    return lst
```

**8. What are `*args` and `**kwargs`? When would you use them?**

- `*args`: Accepts variable number of positional arguments (tuple)
- `**kwargs`: Accepts variable number of keyword arguments (dict)

```python
def flexible_function(*args, **kwargs):
    print("Args:", args)
    print("Kwargs:", kwargs)

flexible_function(1, 2, 3, name="John", age=30)
# Args: (1, 2, 3)
# Kwargs: {'name': 'John', 'age': 30}

# Use case: wrapper functions
def logged_function(*args, **kwargs):
    print("Calling function")
    return original_function(*args, **kwargs)

# Use case: flexible initialization
class Task:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
```

**9. Explain Python's Global Interpreter Lock (GIL)**

The GIL is a mutex that protects access to Python objects, preventing multiple threads from executing Python bytecode simultaneously.

**Impact**:
- Only one thread executes Python code at a time
- CPU-bound multi-threaded programs don't get speedup
- I/O-bound programs benefit from threading
- Multiprocessing bypasses GIL (separate processes)

```python
# GIL limits this (CPU-bound)
import threading
def cpu_task():
    sum([i**2 for i in range(10000000)])

# This works well (I/O-bound)
def io_task():
    response = requests.get(url)
    return response.text

# Bypass GIL with multiprocessing
from multiprocessing import Pool
with Pool(4) as pool:
    results = pool.map(cpu_task, range(4))
```

**10. What are context managers? Explain `with` statement**

Context managers handle resource setup and cleanup automatically using `__enter__` and `__exit__` methods.

```python
# Built-in context manager
with open('file.txt', 'r') as f:
    content = f.read()
# File automatically closed

# Custom context manager
class DatabaseConnection:
    def __enter__(self):
        self.conn = connect_to_db()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        return False  # Don't suppress exceptions

# Using contextlib
from contextlib import contextmanager

@contextmanager
def timer():
    start = time.time()
    yield
    end = time.time()
    print(f"Elapsed: {end - start}")

with timer():
    time.sleep(1)
```

### Advanced Python

**11. What are metaclasses in Python?**

Metaclasses are "classes of classes" that define how classes behave. The default metaclass is `type`.

```python
# type creates classes
MyClass = type('MyClass', (object,), {'x': 5})

# Custom metaclass
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    pass

# Both reference same instance
db1 = Database()
db2 = Database()
print(db1 is db2)  # True
```

**12. Explain Python's method resolution order (MRO)**

MRO determines the order in which base classes are searched when executing a method. Python uses C3 Linearization.

```python
class A:
    def method(self):
        print("A")

class B(A):
    def method(self):
        print("B")

class C(A):
    def method(self):
        print("C")

class D(B, C):
    pass

# MRO: D -> B -> C -> A -> object
print(D.mro())
d = D()
d.method()  # Prints "B" (B comes before C in MRO)
```

**13. What is the difference between `@property` and `@cached_property`?**

- `@property`: Computed every time it's accessed
- `@cached_property`: Computed once, then cached (Django's version)

```python
class Task:
    @property
    def description_html(self):
        # Computed every time
        return markdown.markdown(self.description)

    @cached_property
    def completion_percentage(self):
        # Computed once, cached
        completed = self.subtasks.filter(status='completed').count()
        total = self.subtasks.count()
        return (completed / total * 100) if total > 0 else 0
```

**14. How does Python's garbage collection work?**

Python uses reference counting + generational garbage collection:

1. **Reference Counting**: Object deleted when refcount reaches 0
2. **Cycle Detection**: Generational GC handles circular references
3. **Three Generations**: 0 (young), 1 (middle), 2 (old)

```python
import gc

# Manual control
gc.collect()  # Force collection
gc.disable()  # Disable GC
gc.enable()   # Enable GC

# Check references
import sys
x = []
sys.getrefcount(x)  # Returns reference count
```

**15. Explain the difference between shallow copy and deep copy**

```python
import copy

# Shallow copy - copies object, but not nested objects
original = [[1, 2], [3, 4]]
shallow = copy.copy(original)
shallow[0][0] = 999
print(original)  # [[999, 2], [3, 4]] - MODIFIED!

# Deep copy - copies everything recursively
original = [[1, 2], [3, 4]]
deep = copy.deepcopy(original)
deep[0][0] = 999
print(original)  # [[1, 2], [3, 4]] - UNCHANGED
```

**16. What are Python descriptors?**

Descriptors are objects that define `__get__`, `__set__`, and/or `__delete__` methods. They control attribute access.

```python
class Validator:
    def __init__(self, min_value):
        self.min_value = min_value

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        return obj.__dict__.get(self.name)

    def __set__(self, obj, value):
        if value < self.min_value:
            raise ValueError(f"{self.name} must be >= {self.min_value}")
        obj.__dict__[self.name] = value

class Task:
    priority = Validator(min_value=1)
```

**17. Explain `__new__` vs `__init__`**

- `__new__`: Creates instance (class method, returns new instance)
- `__init__`: Initializes instance (instance method, returns None)

```python
class MyClass:
    def __new__(cls, *args):
        print("Creating instance")
        instance = super().__new__(cls)
        return instance

    def __init__(self, value):
        print("Initializing instance")
        self.value = value

# Use __new__ for immutable types or singletons
class PositiveInt(int):
    def __new__(cls, value):
        if value < 0:
            raise ValueError("Must be positive")
        return super().__new__(cls, value)
```

**18. What is duck typing in Python?**

"If it walks like a duck and quacks like a duck, it's a duck." Type is determined by behavior, not inheritance.

```python
# Both work because they have read() method
def read_data(file_like):
    return file_like.read()

# Works with file
with open('file.txt') as f:
    data = read_data(f)

# Works with StringIO
from io import StringIO
fake_file = StringIO("Hello")
data = read_data(fake_file)

# Protocol in Python 3.8+
from typing import Protocol

class Readable(Protocol):
    def read(self) -> str: ...
```

**19. How do you handle exceptions in Python? Explain custom exceptions**

```python
# Basic exception handling
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
else:
    print("Success")
finally:
    print("Always executes")

# Custom exceptions
class TaskValidationError(Exception):
    """Raised when task validation fails"""
    pass

class TaskNotFoundError(Exception):
    """Raised when task doesn't exist"""
    def __init__(self, task_id):
        self.task_id = task_id
        super().__init__(f"Task {task_id} not found")

# Re-raising with context
try:
    task = Task.objects.get(id=task_id)
except Task.DoesNotExist:
    raise TaskNotFoundError(task_id) from None
```

**20. What are Python's async/await keywords?**

Used for asynchronous programming with coroutines.

```python
import asyncio

# Async function (coroutine)
async def fetch_data(url):
    # Await pauses execution until complete
    response = await aiohttp.get(url)
    return await response.text()

# Running async code
async def main():
    # Run concurrently
    results = await asyncio.gather(
        fetch_data(url1),
        fetch_data(url2),
        fetch_data(url3)
    )
    return results

# Execute
asyncio.run(main())

# Django async views
async def async_view(request):
    data = await database_query()
    return JsonResponse(data)
```

---

## Django Basics

### Core Concepts

**21. What is Django and what are its main features?**

Django is a high-level Python web framework that encourages rapid development and clean design.

**Key Features**:
- **ORM**: Database abstraction layer
- **Admin Interface**: Auto-generated admin panel
- **Authentication**: Built-in user authentication
- **URL Routing**: Clean URL patterns
- **Template Engine**: Django Template Language
- **Forms**: Form handling and validation
- **Security**: CSRF, XSS, SQL injection protection
- **Middleware**: Request/response processing
- **Internationalization**: Multi-language support
- **Caching**: Multiple caching backends

**22. Explain Django's MTV (Model-Template-View) architecture**

Django uses MTV pattern:
- **Model**: Data layer (database)
- **Template**: Presentation layer (HTML)
- **View**: Business logic layer (Python functions/classes)

```
Request → URLs → View → Model (database)
                  ↓
              Template → Response
```

**Comparison to MVC**:
- Django's View = MVC's Controller
- Django's Template = MVC's View
- Django's Model = MVC's Model

**23. What is the Django ORM and what advantages does it provide?**

Object-Relational Mapping (ORM) translates Python code to SQL.

**Advantages**:
- Database-agnostic code
- Protection against SQL injection
- Easier to read and maintain
- Supports relationships naturally
- Query optimization tools
- Migrations handling

```python
# ORM (clean, safe)
tasks = Task.objects.filter(status='completed', priority='high')

# Raw SQL (verbose, injection risk)
cursor.execute("SELECT * FROM tasks WHERE status = %s AND priority = %s",
               ['completed', 'high'])
```

**24. Explain the request-response cycle in Django**

1. **Request arrives** → Web server forwards to Django
2. **Middleware** → Request middleware processes request
3. **URL Router** → Matches URL pattern, finds view
4. **View** → Executes business logic
5. **Model** → View queries database if needed
6. **Template** → View renders template with data
7. **Middleware** → Response middleware processes response
8. **Response** → Sent back to client

```python
# Flow example
# 1. URL: /tasks/5/
# 2. urls.py matches: path('tasks/<int:pk>/', TaskDetailView.as_view())
# 3. View: TaskDetailView.get() executes
# 4. Model: Task.objects.get(pk=5)
# 5. Template: task_detail.html rendered
# 6. Response: HTML sent to browser
```

**25. What is `settings.py` and what configurations go there?**

Central configuration file for Django project.

```python
# Key configurations:
DEBUG = False  # Development vs Production
SECRET_KEY = 'secret'  # Cryptographic signing
ALLOWED_HOSTS = ['example.com']  # Security
INSTALLED_APPS = [...]  # Apps to use
MIDDLEWARE = [...]  # Request/response processing
DATABASES = {...}  # Database connections
STATIC_URL = '/static/'  # Static files
MEDIA_ROOT = BASE_DIR / 'media'  # User uploads
AUTH_USER_MODEL = 'accounts.User'  # Custom user
CACHES = {...}  # Caching configuration
CELERY_BROKER_URL = 'redis://...'  # Task queue
```

**26. What is the purpose of `manage.py`?**

Command-line utility for administrative tasks.

```bash
# Common commands
python manage.py runserver        # Start dev server
python manage.py makemigrations  # Create migrations
python manage.py migrate         # Apply migrations
python manage.py createsuperuser # Create admin user
python manage.py shell           # Interactive shell
python manage.py test            # Run tests
python manage.py collectstatic   # Gather static files
python manage.py dbshell         # Database shell

# Custom management commands in:
# myapp/management/commands/mycommand.py
```

**27. What are Django apps? How do they differ from a project?**

- **Project**: Entire website (collection of apps + configuration)
- **App**: Specific functionality module (reusable component)

```
myproject/              # PROJECT
├── manage.py
├── myproject/          # Project configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/           # APP (users)
├── tasks/              # APP (task management)
└── notifications/      # APP (notifications)
```

**28. Explain `INSTALLED_APPS` in Django settings**

Lists all apps Django should load.

```python
INSTALLED_APPS = [
    # Built-in Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'django_filters',
    'corsheaders',

    # Your apps
    'taskmaster.accounts',
    'taskmaster.tasks',
    'taskmaster.projects',
    'taskmaster.notifications',
]
```

**29. What is Django middleware? Name some common middleware**

Middleware processes requests/responses globally before reaching views.

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # Security headers
    'django.contrib.sessions.middleware.SessionMiddleware',  # Sessions
    'corsheaders.middleware.CorsMiddleware',  # CORS headers
    'django.middleware.common.CommonMiddleware',  # Common processing
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Auth
    'django.contrib.messages.middleware.MessageMiddleware',  # Flash messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Clickjacking
]

# Custom middleware
class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration = time.time() - start
        response['X-Request-Duration'] = duration
        return response
```

**30. Explain `MIDDLEWARE` order and why it matters**

Middleware executes in order for requests, reverse order for responses.

```
REQUEST:
1. SecurityMiddleware
2. SessionMiddleware
3. AuthenticationMiddleware
4. View executes
RESPONSE:
4. AuthenticationMiddleware
3. SessionMiddleware
2. SecurityMiddleware
1. Return to client
```

**Important**: Auth middleware must come after Session middleware (needs session data).

---

### URL Routing & Views

**31. How does Django URL routing work?**

```python
# myproject/urls.py (main)
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/tasks/', include('tasks.urls')),  # Include app URLs
    path('api/accounts/', include('accounts.urls')),
]

# tasks/urls.py (app-specific)
from django.urls import path
from . import views

app_name = 'tasks'  # Namespace

urlpatterns = [
    path('', views.TaskListView.as_view(), name='task-list'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('<int:pk>/complete/', views.complete_task, name='task-complete'),

    # Regex patterns for complex matching
    re_path(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$', views.archive),
]

# In views/templates
reverse('tasks:task-detail', kwargs={'pk': 5})  # /api/tasks/5/
```

**32. What is the difference between function-based views (FBV) and class-based views (CBV)?**

```python
# FUNCTION-BASED VIEW
def task_list(request):
    if request.method == 'GET':
        tasks = Task.objects.all()
        return render(request, 'tasks.html', {'tasks': tasks})
    elif request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('task-list')
        return render(request, 'task_form.html', {'form': form})

# CLASS-BASED VIEW
class TaskListView(ListView):
    model = Task
    template_name = 'tasks.html'
    context_object_name = 'tasks'
    paginate_by = 20

    def get_queryset(self):
        return Task.objects.filter(status='active')

# Pros/Cons:
# FBV: Simpler, explicit, easier for beginners
# CBV: Reusable, DRY, built-in features, harder to trace
```

**33. Explain Django's generic views**

```python
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)

# ListView - display list of objects
class TaskListView(ListView):
    model = Task
    template_name = 'task_list.html'
    context_object_name = 'tasks'
    paginate_by = 20

    def get_queryset(self):
        return Task.objects.select_related('project')

# DetailView - display single object
class TaskDetailView(DetailView):
    model = Task
    template_name = 'task_detail.html'

# CreateView - create new object
class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'
    success_url = reverse_lazy('task-list')

# UpdateView - update existing object
class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'

# DeleteView - delete object
class TaskDeleteView(DeleteView):
    model = Task
    success_url = reverse_lazy('task-list')
```

**34. What are URL namespaces and why use them?**

Namespaces prevent URL name collisions between apps.

```python
# tasks/urls.py
app_name = 'tasks'
urlpatterns = [
    path('list/', views.TaskList.as_view(), name='list'),
]

# projects/urls.py
app_name = 'projects'
urlpatterns = [
    path('list/', views.ProjectList.as_view(), name='list'),
]

# Now both 'list' names can coexist:
reverse('tasks:list')     # /tasks/list/
reverse('projects:list')  # /projects/list/

# In templates:
{% url 'tasks:list' %}
{% url 'projects:list' %}
```

**35. How do you pass parameters in Django URLs?**

```python
urlpatterns = [
    # Path converters
    path('task/<int:pk>/', views.task_detail),  # int
    path('user/<str:username>/', views.user_profile),  # str
    path('post/<slug:slug>/', views.post_detail),  # slug
    path('file/<uuid:file_id>/', views.download),  # uuid
    path('archive/<path:file_path>/', views.archive),  # path (with /)

    # Regex patterns
    re_path(r'^articles/(?P<year>[0-9]{4})/$', views.year_archive),
]

# In view:
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'task.html', {'task': task})

# Custom path converter
class FourDigitYearConverter:
    regex = '[0-9]{4}'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '%04d' % value

# Register converter
from django.urls import register_converter
register_converter(FourDigitYearConverter, 'yyyy')

path('articles/<yyyy:year>/', views.year_archive)
```

**36. What is `reverse()` and `reverse_lazy()`?**

Both convert URL names to actual URLs, but timing differs.

```python
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect

# reverse() - evaluates immediately
def my_view(request):
    url = reverse('task-detail', kwargs={'pk': 5})
    return redirect(url)  # /tasks/5/

# reverse_lazy() - evaluates when used (lazy evaluation)
# Use in class attributes (when URLconf not loaded yet)
class TaskCreateView(CreateView):
    model = Task
    success_url = reverse_lazy('task-list')  # Must use lazy here

# reverse() would fail here (URLconf not ready)
class TaskDeleteView(DeleteView):
    model = Task
    # success_url = reverse('task-list')  # ERROR!
    success_url = reverse_lazy('task-list')  # CORRECT
```

---

### Templates

**37. What is Django's template language (DTL)?**

Simple, powerful template system for generating HTML.

```django
{# task_list.html #}
<!DOCTYPE html>
<html>
<head>
    <title>{{ page_title }}</title>
</head>
<body>
    <h1>Tasks</h1>

    {% if tasks %}
        <ul>
        {% for task in tasks %}
            <li class="{% cycle 'odd' 'even' %}">
                {{ task.title|upper }}
                {% if task.is_overdue %}
                    <span class="warning">OVERDUE</span>
                {% endif %}
            </li>
        {% endfor %}
        </ul>
    {% else %}
        <p>No tasks found.</p>
    {% endif %}

    {# Comments #}
    {{ task.title|truncatewords:10 }}  {# Filter #}
    {% now "Y-m-d" %}  {# Tag #}
</body>
</html>
```

**38. Explain template inheritance with `{% extends %}` and `{% block %}`**

```django
{# base.html #}
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Default Title{% endblock %}</title>
    {% block extra_head %}{% endblock %}
</head>
<body>
    <nav>{% block navigation %}Default Nav{% endblock %}</nav>

    <main>
        {% block content %}
            Default content
        {% endblock %}
    </main>

    <footer>{% block footer %}© 2025{% endblock %}</footer>
</body>
</html>

{# task_list.html - child template #}
{% extends "base.html" %}

{% block title %}Task List{% endblock %}

{% block content %}
    <h1>All Tasks</h1>
    {% for task in tasks %}
        <div>{{ task.title }}</div>
    {% endfor %}

    {{ block.super }}  {# Include parent block content #}
{% endblock %}

{% block extra_head %}
    <link rel="stylesheet" href="tasks.css">
{% endblock %}
```

**39. What are template filters and custom template tags?**

```django
{# Built-in filters #}
{{ task.title|lower }}
{{ task.description|truncatewords:30 }}
{{ task.created_at|date:"Y-m-d" }}
{{ task.price|floatformat:2 }}
{{ task.description|linebreaks }}
{{ task.title|default:"No title" }}

{# Chaining filters #}
{{ task.title|lower|truncatewords:10 }}

{# Custom filter: tasks/templatetags/task_extras.py #}
from django import template

register = template.Library()

@register.filter
def priority_badge(priority):
    colors = {'low': 'green', 'medium': 'yellow', 'high': 'red'}
    return f'<span class="{colors[priority]}">{priority}</span>'

# Usage: {{ task.priority|priority_badge|safe }}

{# Custom tag #}
@register.simple_tag
def task_count(status):
    return Task.objects.filter(status=status).count()

# Usage: {% task_count 'completed' %}

{# Inclusion tag - renders template #}
@register.inclusion_tag('task_summary.html')
def show_task_summary(task):
    return {'task': task, 'comments': task.comments.all()}

# Usage: {% show_task_summary task %}
```

**40. What is `{% csrf_token %}` and why is it important?**

CSRF (Cross-Site Request Forgery) token prevents malicious form submissions.

```django
{# Always include in forms that POST data #}
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Submit</button>
</form>

{# How it works: #}
1. Django generates unique token for each session
2. Token embedded in form and cookie
3. On POST, Django compares form token with cookie token
4. If mismatch, request rejected (403 Forbidden)

{# AJAX requests #}
<script>
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

fetch(url, {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrftoken
    },
    body: JSON.stringify(data)
});
</script>
```

---

## Django ORM & Models

### Model Basics

**41. What is a Django model?**

A model is a Python class that defines database table structure and behavior.

```python
from django.db import models

class Task(models.Model):
    # Fields = database columns
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Meta options
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'tasks'

    # Methods
    def __str__(self):
        return self.title

    def mark_complete(self):
        self.status = 'completed'
        self.save()
```

**42. Explain common Django field types**

```python
class MyModel(models.Model):
    # Text fields
    char_field = models.CharField(max_length=100)  # Limited text
    text_field = models.TextField()  # Unlimited text
    slug_field = models.SlugField()  # URL-friendly text
    email_field = models.EmailField()  # Email validation
    url_field = models.URLField()  # URL validation

    # Numeric fields
    integer_field = models.IntegerField()
    positive_int = models.PositiveIntegerField()
    decimal_field = models.DecimalField(max_digits=10, decimal_places=2)
    float_field = models.FloatField()

    # Date/Time fields
    date_field = models.DateField()
    time_field = models.TimeField()
    datetime_field = models.DateTimeField()
    auto_now_add = models.DateTimeField(auto_now_add=True)  # Set on create
    auto_now = models.DateTimeField(auto_now=True)  # Update on save

    # Boolean
    boolean_field = models.BooleanField(default=False)

    # File fields
    file_field = models.FileField(upload_to='files/')
    image_field = models.ImageField(upload_to='images/')

    # JSON (PostgreSQL)
    json_field = models.JSONField(default=dict)

    # Relationships
    foreign_key = models.ForeignKey('OtherModel', on_delete=models.CASCADE)
    many_to_many = models.ManyToManyField('OtherModel')
    one_to_one = models.OneToOneField('OtherModel', on_delete=models.CASCADE)

    # Special
    uuid_field = models.UUIDField(default=uuid.uuid4, editable=False)
```

**43. What is the difference between `null=True` and `blank=True`?**

- `null=True`: Database-level (allows NULL in database)
- `blank=True`: Validation-level (allows empty in forms)

```python
class Task(models.Model):
    # Both null and blank
    description = models.TextField(null=True, blank=True)
    # Database: NULL allowed
    # Forms: Can be left empty

    # Only blank (recommended for CharFields)
    title = models.CharField(max_length=200, blank=True, default='')
    # Database: Empty string '' stored (not NULL)
    # Forms: Can be left empty

    # Neither (required)
    name = models.CharField(max_length=100)
    # Database: NOT NULL
    # Forms: Must provide value

    # Only null (rare, usually wrong)
    # Avoid this combination

# Best practices:
# - Use blank=True (without null) for CharFields/TextFields
# - Use null=True, blank=True for ForeignKey, DateField, etc.
# - Avoid null=True on CharFields (use blank=True with default='')
```

**44. What are model Meta options?**

```python
class Task(models.Model):
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ordering
        ordering = ['-created_at', 'title']  # Default sort

        # Database table name
        db_table = 'custom_task_table'

        # Human-readable names
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

        # Indexes for performance
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['-created_at']),
        ]

        # Constraints
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'title'],
                name='unique_task_per_project'
            ),
            models.CheckConstraint(
                check=models.Q(priority__in=['low', 'medium', 'high']),
                name='valid_priority'
            ),
        ]

        # Permissions
        permissions = [
            ('can_publish', 'Can publish tasks'),
        ]

        # Others
        abstract = False  # Abstract base class?
        proxy = False  # Proxy model?
        managed = True  # Django manages migrations?
        get_latest_by = 'created_at'
```

**45. Explain `on_delete` options for ForeignKey**

```python
class Task(models.Model):
    # CASCADE - Delete tasks when project deleted
    project = models.ForeignKey(
        'Project',
        on_delete=models.CASCADE
    )

    # PROTECT - Prevent project deletion if tasks exist
    protected_project = models.ForeignKey(
        'Project',
        on_delete=models.PROTECT
    )

    # SET_NULL - Set to NULL when project deleted
    nullable_project = models.ForeignKey(
        'Project',
        on_delete=models.SET_NULL,
        null=True
    )

    # SET_DEFAULT - Set to default value
    default_project = models.ForeignKey(
        'Project',
        on_delete=models.SET_DEFAULT,
        default=1
    )

    # SET() - Set to specific value
    def get_default_project():
        return Project.objects.get(name='Unassigned')

    custom_project = models.ForeignKey(
        'Project',
        on_delete=models.SET(get_default_project)
    )

    # DO_NOTHING - No action (can cause database errors)
    dangerous = models.ForeignKey(
        'Project',
        on_delete=models.DO_NOTHING
    )
```

**46. What is the purpose of `related_name` in relationships?**

`related_name` defines the reverse relationship name.

```python
class Project(models.Model):
    name = models.CharField(max_length=200)

class Task(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'  # Custom reverse name
    )

# Usage:
project = Project.objects.get(id=1)

# Without related_name: task_set (auto-generated)
# tasks = project.task_set.all()

# With related_name='tasks':
tasks = project.tasks.all()  # Cleaner!

# Prevent reverse relation
class Log(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='+'  # No reverse relation
    )

# Related query name
class Comment(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments',
        related_query_name='comment'  # For filtering
    )

# Filter using related_query_name:
Task.objects.filter(comment__content__icontains='bug')
```

**47. How do you create a custom user model in Django?**

```python
# accounts/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'  # Login field
    REQUIRED_FIELDS = ['first_name', 'last_name']  # For createsuperuser

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

# settings.py
AUTH_USER_MODEL = 'accounts.User'

# IMPORTANT: Must set AUTH_USER_MODEL before first migration!
```

**48. What is `AbstractUser` vs `AbstractBaseUser`?**

```python
# AbstractUser - extends default User (easiest)
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Inherits: username, first_name, last_name, email, password, etc.
    # Just add custom fields
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

# AbstractBaseUser - complete customization (more work)
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class User(AbstractBaseUser, PermissionsMixin):
    # Must define everything yourself
    email = models.EmailField(unique=True)
    # Must create custom manager
    # Must set USERNAME_FIELD
    # Must implement is_active, is_staff, etc.

# Choose AbstractUser if: You want to keep username/email structure
# Choose AbstractBaseUser if: You want email-only login, completely custom fields
```

---

### Relationships

**49. Explain the three types of model relationships in Django**

```python
# ONE-TO-ONE: Each user has exactly one profile
class User(models.Model):
    username = models.CharField(max_length=100)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()

# Usage:
user = User.objects.get(id=1)
profile = user.userprofile  # Reverse: lowercase model name

# MANY-TO-ONE (ForeignKey): Many tasks belong to one project
class Project(models.Model):
    name = models.CharField(max_length=200)

class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)

# Usage:
task = Task.objects.get(id=1)
project = task.project  # Forward
tasks = project.tasks.all()  # Reverse

# MANY-TO-MANY: Tasks can have multiple assignees, users can have multiple tasks
class User(models.Model):
    name = models.CharField(max_length=100)

class Task(models.Model):
    title = models.CharField(max_length=200)
    assignees = models.ManyToManyField(User, related_name='assigned_tasks')

# Usage:
task = Task.objects.get(id=1)
task.assignees.add(user1, user2)  # Add relationships
task.assignees.remove(user1)  # Remove
users = task.assignees.all()  # Get all

user = User.objects.get(id=1)
tasks = user.assigned_tasks.all()  # Reverse
```

**50. What is a "through" model in Many-to-Many relationships?**

Through models add extra fields to M2M relationships.

```python
# WITHOUT through model (simple M2M)
class Project(models.Model):
    name = models.CharField(max_length=200)
    members = models.ManyToManyField(User)
# Can only store: Project ↔ User

# WITH through model (extra data)
class Project(models.Model):
    name = models.CharField(max_length=200)
    members = models.ManyToManyField(
        User,
        through='ProjectMember',
        related_name='projects'
    )

class ProjectMember(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    ])
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['project', 'user']]

    @property
    def can_manage_project(self):
        return self.role in ['owner', 'admin']

# Usage:
# Can't use add/remove directly with through model
# project.members.add(user)  # ERROR!

# Create membership explicitly
ProjectMember.objects.create(
    project=project,
    user=user,
    role='admin'
)

# Query
project.members.all()  # Get users
user.projects.all()  # Get projects

# Query through model
ProjectMember.objects.filter(
    project=project,
    role='admin'
)

# Access through data
membership = ProjectMember.objects.get(project=project, user=user)
print(membership.role, membership.joined_at)
```

**51. How do you implement self-referencing relationships?**

```python
# TASK HIERARCHY (parent-child tasks)
class Task(models.Model):
    title = models.CharField(max_length=200)
    parent_task = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subtasks'
    )

    @property
    def subtask_count(self):
        return self.subtasks.count()

    @property
    def completed_subtask_count(self):
        return self.subtasks.filter(status='completed').count()

# Usage:
parent = Task.objects.create(title="Build feature")
child1 = Task.objects.create(title="Write tests", parent_task=parent)
child2 = Task.objects.create(title="Write code", parent_task=parent)

parent.subtasks.all()  # Returns [child1, child2]
child1.parent_task  # Returns parent

# NESTED COMMENTS
class Comment(models.Model):
    content = models.TextField()
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    @property
    def reply_count(self):
        return self.replies.count()

# Usage:
comment = Comment.objects.create(content="Great post!")
reply = Comment.objects.create(
    content="Thanks!",
    parent_comment=comment
)

comment.replies.all()  # Get all replies
reply.parent_comment  # Get parent comment

# TREE TRAVERSAL
def get_all_descendants(task):
    """Get all subtasks recursively"""
    descendants = []
    for subtask in task.subtasks.all():
        descendants.append(subtask)
        descendants.extend(get_all_descendants(subtask))
    return descendants
```

**52. Explain `OneToOneField` and when to use it**

```python
# Use OneToOneField when:
# 1. Extending user model
# 2. Splitting large models
# 3. Optional related data

class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()

class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    github_username = models.CharField(max_length=100, blank=True)

    # Settings
    email_notifications = models.BooleanField(default=True)
    theme = models.CharField(
        max_length=10,
        choices=[('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto')],
        default='auto'
    )

# Auto-create profile with signals
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# Usage:
user = User.objects.get(id=1)
user.profile.bio  # Access related profile
user.profile.theme

# vs ForeignKey (which would be one-to-many)
# ForeignKey would allow multiple profiles per user (wrong!)
```

---

### QuerySets & Queries

**53. What is a QuerySet in Django?**

A QuerySet is a lazy, database-efficient collection of database queries.

```python
# Create QuerySet (doesn't hit database yet)
tasks = Task.objects.filter(status='active')  # Lazy!

# QuerySet operations (still lazy)
tasks = tasks.filter(priority='high')
tasks = tasks.order_by('-created_at')
tasks = tasks[:10]

# Database hit occurs when:
list(tasks)  # Convert to list
for task in tasks:  # Iterate
    print(task)
if tasks:  # Boolean evaluation
    print("Has tasks")
len(tasks)  # Count
tasks[0]  # Index access
tasks.exists()  # Existence check

# QuerySet is immutable (returns new QuerySet)
qs1 = Task.objects.filter(status='active')
qs2 = qs1.filter(priority='high')  # New QuerySet
# qs1 unchanged, qs2 is filtered

# Common methods:
Task.objects.all()  # All objects
Task.objects.filter(status='active')  # Filter
Task.objects.exclude(status='cancelled')  # Exclude
Task.objects.get(id=1)  # Single object (or error)
Task.objects.first()  # First or None
Task.objects.last()  # Last or None
Task.objects.count()  # Count
Task.objects.exists()  # Boolean
Task.objects.values('title', 'status')  # Dicts
Task.objects.values_list('title', flat=True)  # List
```

**54. Explain `select_related()` vs `prefetch_related()`**

Both optimize database queries but work differently.

```python
# WITHOUT optimization (N+1 problem)
tasks = Task.objects.all()
for task in tasks:  # 1 query
    print(task.project.name)  # N queries (one per task)
# Total: 1 + N queries

# select_related() - for ForeignKey/OneToOne (SQL JOIN)
tasks = Task.objects.select_related('project', 'created_by')
for task in tasks:  # 1 query with JOIN
    print(task.project.name)  # No additional query!
    print(task.created_by.email)  # No additional query!
# Total: 1 query

# SQL generated:
# SELECT * FROM tasks
# INNER JOIN projects ON tasks.project_id = projects.id
# INNER JOIN users ON tasks.created_by_id = users.id

# prefetch_related() - for ManyToMany/reverse ForeignKey (separate queries)
tasks = Task.objects.prefetch_related('assignees', 'comments')
for task in tasks:  # 1 query for tasks
    for user in task.assignees.all():  # 1 query for all assignees (cached)
        print(user.name)
    for comment in task.comments.all():  # 1 query for all comments (cached)
        print(comment.content)
# Total: 3 queries (regardless of N)

# Combining both
tasks = Task.objects.select_related(
    'project',
    'created_by'
).prefetch_related(
    'assignees',
    'comments__author'  # Nested prefetch
)

# Prefetch with custom queryset
from django.db.models import Prefetch

tasks = Task.objects.prefetch_related(
    Prefetch(
        'comments',
        queryset=Comment.objects.select_related('author').order_by('-created_at')
    )
)

# When to use which:
# select_related: Following ForeignKey/OneToOne (forward relations)
# prefetch_related: ManyToMany, reverse ForeignKey, or GenericRelation
```

**55. What is the N+1 query problem? How do you solve it?**

```python
# THE PROBLEM: N+1 queries
tasks = Task.objects.all()  # 1 query
for task in tasks:  # Loop N times
    print(task.project.name)  # N queries
# Total: 1 + N queries (BAD for large N)

# SOLUTION 1: select_related (for ForeignKey)
tasks = Task.objects.select_related('project')
for task in tasks:
    print(task.project.name)  # No extra queries!
# Total: 1 query

# SOLUTION 2: prefetch_related (for M2M)
tasks = Task.objects.prefetch_related('assignees')
for task in tasks:
    for user in task.assignees.all():  # No extra queries!
        print(user.name)
# Total: 2 queries (tasks + assignees)

# SOLUTION 3: values() (if only need specific fields)
tasks = Task.objects.values('id', 'title', 'project__name')
for task in tasks:
    print(task['project__name'])
# Total: 1 query

# Detecting N+1 problems:
# 1. Use Django Debug Toolbar
# 2. Enable SQL logging
import logging
logging.basicConfig()
logging.getLogger('django.db.backends').setLevel(logging.DEBUG)

# 3. Use django-silk or django-nplusone
# 4. Monitor query count in tests
from django.test.utils import override_settings
from django.db import connection

with override_settings(DEBUG=True):
    connection.queries = []  # Reset
    # Your code here
    print(f"Queries: {len(connection.queries)}")
```

**56. Explain lazy loading in Django QuerySets**

```python
# Lazy evaluation: QuerySet doesn't hit database until needed

# These DON'T execute queries:
qs = Task.objects.all()  # No query yet
qs = qs.filter(status='active')  # Still no query
qs = qs.order_by('-created_at')  # Still no query!

# Query executes when:

# 1. Iteration
for task in qs:  # Query executes here
    print(task)

# 2. Slicing with step
first_10 = qs[:10]  # No query (slicing)
task = first_10[0]  # Query executes
every_other = qs[::2]  # Query executes (step parameter)

# 3. Explicit evaluation
list(qs)  # Query
bool(qs)  # Query
len(qs)  # Query
str(qs)  # Query

# 4. Pickling/Serialization
import pickle
pickle.dumps(qs)  # Query

# 5. Checking existence
if qs:  # Query
    print("Has results")

# Benefits:
# 1. Build complex queries step by step
# 2. Reuse querysets
# 3. Optimize before execution

def get_filtered_tasks(status=None, priority=None, assigned_to=None):
    qs = Task.objects.all()

    if status:
        qs = qs.filter(status=status)
    if priority:
        qs = qs.filter(priority=priority)
    if assigned_to:
        qs = qs.filter(assignees=assigned_to)

    # Still no query executed!
    # Can optimize before use
    qs = qs.select_related('project')

    return qs  # Query executes when caller uses it

# Caching:
# QuerySet caches results after first evaluation
qs = Task.objects.all()
list(qs)  # Query executes, results cached
list(qs)  # Uses cache, no query!

# But re-filtering breaks cache:
qs = Task.objects.all()
list(qs)  # Query
qs = qs.filter(status='active')  # New QuerySet
list(qs)  # New query
```

**57. What are Django Q objects? When would you use them?**

Q objects allow complex queries with OR, AND, NOT logic.

```python
from django.db.models import Q

# Simple filter (implicit AND)
tasks = Task.objects.filter(status='active', priority='high')
# SQL: WHERE status='active' AND priority='high'

# OR queries with Q
tasks = Task.objects.filter(
    Q(status='active') | Q(status='in_progress')
)
# SQL: WHERE status='active' OR status='in_progress'

# Complex combinations
tasks = Task.objects.filter(
    (Q(status='active') | Q(status='in_progress')) &
    Q(priority='high')
)
# SQL: WHERE (status='active' OR status='in_progress') AND priority='high'

# NOT queries
tasks = Task.objects.filter(~Q(status='cancelled'))
# SQL: WHERE NOT status='cancelled'

# Building queries dynamically
def search_tasks(status_list, priority, exclude_cancelled=True):
    # Start with all tasks
    query = Q()

    # Add status conditions (OR)
    if status_list:
        status_query = Q()
        for status in status_list:
            status_query |= Q(status=status)
        query &= status_query

    # Add priority
    if priority:
        query &= Q(priority=priority)

    # Exclude cancelled
    if exclude_cancelled:
        query &= ~Q(status='cancelled')

    return Task.objects.filter(query)

# Search across multiple fields
search_term = "bug"
tasks = Task.objects.filter(
    Q(title__icontains=search_term) |
    Q(description__icontains=search_term) |
    Q(comments__content__icontains=search_term)
).distinct()

# Conditional filters
def get_tasks(include_completed=False):
    query = Q()
    if not include_completed:
        query &= ~Q(status='completed')
    return Task.objects.filter(query)
```

**58. What is the difference between `filter()` and `get()`?**

```python
# filter() - Returns QuerySet (0 or more results)
tasks = Task.objects.filter(status='active')
# Always returns QuerySet (even if 0 or 1 result)
print(type(tasks))  # QuerySet
for task in tasks:
    print(task)

# Returns empty QuerySet if no match
tasks = Task.objects.filter(id=999)  # No error
print(tasks.count())  # 0

# get() - Returns single object or raises exception
task = Task.objects.get(id=1)
print(type(task))  # Task instance

# Raises DoesNotExist if no match
try:
    task = Task.objects.get(id=999)
except Task.DoesNotExist:
    print("Task not found")

# Raises MultipleObjectsReturned if multiple matches
try:
    task = Task.objects.get(status='active')  # Multiple active tasks!
except Task.MultipleObjectsReturned:
    print("Multiple tasks found")

# Safe alternatives to get():

# 1. get_object_or_404 (in views)
from django.shortcuts import get_object_or_404
task = get_object_or_404(Task, id=1)  # Returns 404 if not found

# 2. first() (returns None if no match)
task = Task.objects.filter(id=1).first()
if task:
    print(task.title)

# 3. try/except
try:
    task = Task.objects.get(id=1)
except Task.DoesNotExist:
    task = None

# When to use which:
# get(): When expecting exactly one result (primary key, unique field)
# filter(): When expecting 0 or more results
# first(): When wanting first result or None
# last(): When wanting last result or None
```

**59. Explain `annotate()` and `aggregate()` in Django**

```python
from django.db.models import Count, Avg, Sum, Max, Min, F, Q

# aggregate() - Calculate across entire QuerySet (returns dict)
stats = Task.objects.aggregate(
    total=Count('id'),
    avg_hours=Avg('estimated_hours'),
    total_hours=Sum('actual_hours'),
    max_priority=Max('priority')
)
# Returns: {'total': 100, 'avg_hours': 5.5, ...}
# Returns DICT, not QuerySet!

# annotate() - Add calculated field to each object (returns QuerySet)
projects = Project.objects.annotate(
    task_count=Count('tasks'),
    completed_count=Count('tasks', filter=Q(tasks__status='completed')),
    total_hours=Sum('tasks__estimated_hours')
)

for project in projects:
    print(f"{project.name}: {project.task_count} tasks")
    print(f"Completed: {project.completed_count}")
    print(f"Total hours: {project.total_hours}")

# Filtering on annotations
projects = Project.objects.annotate(
    task_count=Count('tasks')
).filter(task_count__gt=10)  # Projects with >10 tasks

# Complex annotations
from django.db.models import Case, When, Value, IntegerField

tasks = Task.objects.annotate(
    priority_score=Case(
        When(priority='urgent', then=Value(4)),
        When(priority='high', then=Value(3)),
        When(priority='medium', then=Value(2)),
        When(priority='low', then=Value(1)),
        default=Value(0),
        output_field=IntegerField()
    )
).order_by('-priority_score')

# F expressions (refer to field values)
tasks = Task.objects.annotate(
    hours_difference=F('actual_hours') - F('estimated_hours')
).filter(hours_difference__gt=0)  # Tasks over estimate

# Aggregating annotations
stats = Task.objects.annotate(
    assignee_count=Count('assignees')
).aggregate(
    avg_assignees=Avg('assignee_count'),
    max_assignees=Max('assignee_count')
)

# Grouping with values()
status_stats = Task.objects.values('status').annotate(
    count=Count('id'),
    avg_hours=Avg('estimated_hours')
).order_by('-count')
# Returns: [
#     {'status': 'active', 'count': 50, 'avg_hours': 5.2},
#     {'status': 'completed', 'count': 30, 'avg_hours': 4.8},
# ]
```

**60. How do you create custom QuerySet managers?**

Reference: `TaskManager` in `tasks/models.py`

```python
# Custom QuerySet
class TaskQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status__in=['todo', 'in_progress', 'review'])

    def high_priority(self):
        return self.filter(priority__in=['high', 'urgent'])

    def overdue(self):
        from django.utils import timezone
        return self.filter(
            due_date__lt=timezone.now(),
            status__in=['todo', 'in_progress']
        )

    def for_user(self, user):
        return self.filter(
            Q(created_by=user) | Q(assignees=user)
        ).distinct()

    def with_details(self):
        """Optimize queries"""
        return self.select_related(
            'project', 'created_by'
        ).prefetch_related(
            'assignees', 'comments__author'
        )

# Custom Manager
class TaskManager(models.Manager):
    def get_queryset(self):
        return TaskQuerySet(self.model, using=self._db)

    # Proxy methods to QuerySet
    def active(self):
        return self.get_queryset().active()

    def high_priority(self):
        return self.get_queryset().high_priority()

    def overdue(self):
        return self.get_queryset().overdue()

    def for_user(self, user):
        return self.get_queryset().for_user(user)

# Model with custom manager
class Task(models.Model):
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20)
    priority = models.CharField(max_length=20)
    due_date = models.DateTimeField(null=True)

    # Default manager
    objects = TaskManager()

    # Additional managers
    active_tasks = TaskManager()  # Can have multiple

    class Meta:
        base_manager_name = 'objects'  # Default for related queries

# Usage:
Task.objects.active()  # Active tasks
Task.objects.high_priority().overdue()  # Chainable!
Task.objects.for_user(request.user).with_details()

# In related queries
project.tasks.active()  # Uses base_manager_name

# QuerySet methods also work
Task.objects.active().filter(priority='high').count()
```

**61. What is `values()` vs `values_list()` in QuerySets?**

```python
# Regular QuerySet - returns model instances
tasks = Task.objects.all()
for task in tasks:
    print(task.title, task.status)  # Task object
# Memory intensive for large datasets

# values() - returns dictionaries
tasks = Task.objects.values('title', 'status', 'priority')
for task in tasks:
    print(task)  # {'title': 'Fix bug', 'status': 'active', 'priority': 'high'}
    print(task['title'])  # Access as dict

# values() with relationships (double underscore)
tasks = Task.objects.values('title', 'project__name', 'created_by__email')
# {'title': 'Fix bug', 'project__name': 'MyProject', 'created_by__email': 'user@example.com'}

# values() without arguments - all fields
tasks = Task.objects.values()

# values_list() - returns tuples
tasks = Task.objects.values_list('title', 'status')
for title, status in tasks:
    print(f"{title}: {status}")
# ('Fix bug', 'active')

# flat=True - single field as flat list
titles = Task.objects.values_list('title', flat=True)
# ['Fix bug', 'Add feature', 'Write docs']

# named=True - named tuples
from collections import namedtuple
tasks = Task.objects.values_list('title', 'status', named=True)
for task in tasks:
    print(task.title, task.status)  # Attribute access

# Performance comparison:
# Model instances: Full object with all methods/properties
# values(): Dictionary, lighter, no model methods
# values_list(): Tuple, lightest, fastest

# Use cases:
# Model instances: When you need model methods/properties
Task.objects.all()

# values(): API responses, JSON serialization
tasks_data = list(Task.objects.values('id', 'title', 'status'))
return JsonResponse({'tasks': tasks_data})

# values_list(): Simple data extraction, CSV export
titles = Task.objects.values_list('title', flat=True)
csv_data = list(Task.objects.values_list('title', 'status', 'priority'))
```

**62. Explain `exists()`, `count()`, and when to use each**

```python
# count() - Returns number of rows
task_count = Task.objects.filter(status='active').count()
# SQL: SELECT COUNT(*) FROM tasks WHERE status='active'

# exists() - Returns boolean (faster than count)
has_tasks = Task.objects.filter(status='active').exists()
# SQL: SELECT 1 FROM tasks WHERE status='active' LIMIT 1

# Comparison:

# WRONG - Inefficient
if len(Task.objects.filter(status='active')):  # Fetches ALL objects!
    print("Has tasks")

if Task.objects.filter(status='active').count() > 0:  # Counts all
    print("Has tasks")

# RIGHT - Efficient
if Task.objects.filter(status='active').exists():  # Stops at first match
    print("Has tasks")

# When to use count():
# - Need exact number
if Task.objects.filter(assignees=user).count() > 10:
    print("User has too many tasks")

# - Displaying count to user
context = {'task_count': Task.objects.count()}

# When to use exists():
# - Just checking if any exist
if Task.objects.filter(id=task_id).exists():
    print("Task exists")

# - Boolean checks
if project.tasks.filter(status='in_progress').exists():
    print("Project has tasks in progress")

# - Validation
if not Task.objects.filter(id=task_id, assignees=user).exists():
    raise PermissionDenied("Not your task")

# Performance:
# exists() > count() > len(queryset) > bool(queryset)

# In templates (auto-uses bool):
# {% if tasks %}...{% endif %}  # Evaluates entire QuerySet
# Better: pass exists() result from view

# Exists with complex queries
has_overdue = Task.objects.filter(
    assignees=user,
    due_date__lt=timezone.now(),
    status__in=['todo', 'in_progress']
).exists()
```

**63. How do you perform raw SQL queries in Django?**

```python
# Method 1: raw() - Maps to model
tasks = Task.objects.raw('SELECT * FROM tasks WHERE status = %s', ['active'])
for task in tasks:
    print(task.title)  # Returns Task instances

# raw() with custom SELECT
tasks = Task.objects.raw(
    'SELECT id, title, status FROM tasks WHERE priority = %s',
    ['high']
)

# raw() with JOINs
tasks = Task.objects.raw('''
    SELECT tasks.*, projects.name as project_name
    FROM tasks
    JOIN projects ON tasks.project_id = projects.id
    WHERE projects.status = %s
''', ['active'])

# Method 2: connection.cursor() - Raw results
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute(
        "SELECT title, COUNT(*) FROM tasks GROUP BY title HAVING COUNT(*) > %s",
        [1]
    )
    rows = cursor.fetchall()
    for row in rows:
        print(row)  # Tuple

# Named parameters (with cursor)
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT * FROM tasks
        WHERE status = %(status)s AND priority = %(priority)s
    """, {'status': 'active', 'priority': 'high'})

    columns = [col[0] for col in cursor.description]
    results = [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

# Method 3: execute with return values
from django.db import connection

def get_task_statistics():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                status,
                COUNT(*) as count,
                AVG(estimated_hours) as avg_hours
            FROM tasks
            GROUP BY status
        """)

        # fetchone() - single row
        row = cursor.fetchone()

        # fetchall() - all rows
        rows = cursor.fetchall()

        # fetchmany(size) - specified number
        rows = cursor.fetchmany(10)

    return rows

# IMPORTANT: Use parameterized queries (prevent SQL injection)
# GOOD
Task.objects.raw('SELECT * FROM tasks WHERE id = %s', [task_id])

# BAD - SQL Injection vulnerability!
Task.objects.raw(f'SELECT * FROM tasks WHERE id = {task_id}')

# When to use raw SQL:
# - Complex queries ORM can't handle
# - Performance-critical queries
# - Database-specific features
# - Legacy database schemas
# - Bulk operations

# Alternative: Use ORM when possible
# Raw SQL:
tasks = Task.objects.raw('''
    SELECT tasks.*
    FROM tasks
    JOIN projects ON tasks.project_id = projects.id
    WHERE projects.status = 'active'
''')

# ORM equivalent:
tasks = Task.objects.filter(project__status='active').select_related('project')
```

**64. What is `defer()` and `only()` in QuerySets?**

Both optimize queries by limiting fields fetched.

```python
# Regular query - fetches ALL fields
tasks = Task.objects.all()
# SQL: SELECT id, title, description, status, priority, ... FROM tasks

# only() - Fetch ONLY specified fields
tasks = Task.objects.only('id', 'title', 'status')
# SQL: SELECT id, title, status FROM tasks

for task in tasks:
    print(task.title)  # No extra query
    print(task.description)  # Extra query! (deferred field accessed)

# defer() - Fetch ALL EXCEPT specified fields
tasks = Task.objects.defer('description', 'notes')
# SQL: SELECT id, title, status, priority, ... FROM tasks
# (excludes description and notes)

for task in tasks:
    print(task.title)  # No extra query
    print(task.description)  # Extra query! (deferred field accessed)

# Use cases:

# 1. List views (don't need full content)
tasks = Task.objects.only('id', 'title', 'status', 'priority')

# 2. Skip large text fields
tasks = Task.objects.defer('description', 'detailed_notes')

# 3. API optimization
# Bad: Fetch everything
tasks = Task.objects.all()

# Good: Only what's needed for API
tasks = Task.objects.only(
    'id', 'title', 'status', 'priority', 'due_date'
)

# With relationships:
tasks = Task.objects.only(
    'title',
    'project__name',  # Only project name, not all project fields
    'created_by__email'
).select_related('project', 'created_by')

# Combining defer/only:
tasks = Task.objects.defer('description').only('id', 'title')
# only() takes precedence

# Important notes:
# - Primary key always fetched
# - Foreign keys always fetched (for relationships)
# - Accessing deferred field triggers separate query
# - Use for performance optimization
# - Profile queries to verify improvement

# Don't over-optimize:
# Bad (too granular):
tasks = Task.objects.only('title')
for task in tasks:
    print(task.title, task.status, task.priority)  # 3 extra queries per task!

# Good (fetch what you need):
tasks = Task.objects.only('title', 'status', 'priority')
```

---

*[Continuing with remaining sections... This document is very comprehensive. Should I continue with the remaining sections (Model Methods, Django REST Framework, Authentication, Caching, Celery, etc.), or would you like me to focus on specific sections first?]*

---

## Model Methods & Properties

**65. What is the difference between model methods and properties?**

```python
class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20)
    due_date = models.DateTimeField()

    # METHOD - called with parentheses, can accept arguments
    def mark_as_completed(self):
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()

    def assign_to(self, user):
        self.assignees.add(user)

    # PROPERTY - accessed like an attribute, no parentheses
    @property
    def is_overdue(self):
        if not self.due_date:
            return False
        return timezone.now() > self.due_date and self.status != 'completed'

    @property
    def days_until_due(self):
        if not self.due_date:
            return None
        delta = self.due_date - timezone.now()
        return delta.days

# Usage:
task = Task.objects.get(id=1)

# Method (with parentheses)
task.mark_as_completed()  # Called like a function
task.assign_to(user)

# Property (no parentheses)
if task.is_overdue:  # Accessed like an attribute
    print("Task is overdue!")
print(f"Days until due: {task.days_until_due}")

# When to use which:
# Method: Actions that modify state, accept parameters
# Property: Computed values, read-only attributes
```

**66. Explain `@property` decorator in Django models**

```python
class User(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    @property
    def full_name(self):
        """Computed attribute"""
        return f"{self.first_name} {self.last_name}"

class Task(models.Model):
    description = models.TextField()
    due_date = models.DateTimeField()
    status = models.CharField(max_length=20)

    @property
    def is_overdue(self):
        """Boolean check"""
        if not self.due_date or self.status == 'completed':
            return False
        return timezone.now() > self.due_date

    @property
    def description_html(self):
        """Convert markdown to HTML"""
        import markdown
        return markdown.markdown(self.description)

    @property
    def completion_percentage(self):
        """Calculate completion"""
        total = self.subtasks.count()
        if total == 0:
            return 100 if self.status == 'completed' else 0
        completed = self.subtasks.filter(status='completed').count()
        return int(completed / total * 100)

# Usage:
task = Task.objects.get(id=1)
print(task.full_name)  # No parentheses
print(task.is_overdue)  # Boolean
print(task.description_html)  # HTML string

# Properties in templates:
# {{ task.full_name }}
# {% if task.is_overdue %}...{% endif %}

# Properties in serializers:
class TaskSerializer(serializers.ModelSerializer):
    is_overdue = serializers.ReadOnlyField()  # Includes property

    class Meta:
        model = Task
        fields = ['id', 'title', 'is_overdue']  # Property included

# Cached property (compute once):
from django.utils.functional import cached_property

class Task(models.Model):
    @cached_property
    def expensive_calculation(self):
        # Complex calculation, cached after first access
        return some_expensive_operation()
```

**67. What is `save()` method and when would you override it?**

```python
class Task(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    status = models.CharField(max_length=20)
    completed_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # 1. Auto-generate slug from title
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)

        # 2. Set completed_at when status changes to completed
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()

        # 3. Validation
        if self.status == 'completed' and not self.assignees.exists():
            raise ValidationError("Cannot complete task without assignees")

        # 4. Call parent save
        super().save(*args, **kwargs)

        # 5. Post-save actions (after object saved)
        if self.status == 'completed':
            self.notify_completion()

    def notify_completion(self):
        # Send notifications
        pass

# Common use cases for overriding save():

# 1. Auto-populate fields
class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

# 2. Conditional logic
class Order(models.Model):
    status = models.CharField(max_length=20)
    shipped_at = models.DateTimeField(null=True)

    def save(self, *args, **kwargs):
        if self.status == 'shipped' and not self.shipped_at:
            self.shipped_at = timezone.now()
        super().save(*args, **kwargs)

# 3. Audit trail
class AuditModel(models.Model):
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        # Get user from thread local or kwargs
        user = kwargs.pop('user', None)
        if user:
            self.modified_by = user
        super().save(*args, **kwargs)

    class Meta:
        abstract = True

# IMPORTANT: Always call super().save()
# NEVER do: def save(self): return  # Database won't update!

# Force insert/update:
# force_insert=True - Always INSERT (fail if exists)
# force_update=True - Always UPDATE (fail if doesn't exist)
task.save(force_update=True)

# Update specific fields:
task.save(update_fields=['status', 'updated_at'])

# Signals vs save():
# Use save(): Simple logic, directly related to model
# Use signals: Decoupled logic, affects other models
```

**68. What is `clean()` method in Django models?**

```python
from django.core.exceptions import ValidationError
from django.utils import timezone

class Task(models.Model):
    title = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20)
    priority = models.CharField(max_length=20)
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2)

    def clean(self):
        """Model-level validation"""
        # 1. Validate date range
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError({
                    'end_date': 'End date must be after start date'
                })

        # 2. Cross-field validation
        if self.status == 'completed' and self.estimated_hours == 0:
            raise ValidationError(
                'Completed tasks must have estimated hours'
            )

        # 3. Business logic validation
        if self.priority == 'urgent' and not self.end_date:
            raise ValidationError({
                'end_date': 'Urgent tasks must have an end date'
            })

        # 4. Complex validation
        if self.status == 'in_progress':
            active_count = Task.objects.filter(
                assignees__in=self.assignees.all(),
                status='in_progress'
            ).exclude(id=self.id).count()

            if active_count >= 5:
                raise ValidationError(
                    'Assignees already have 5 tasks in progress'
                )

    def save(self, *args, **kwargs):
        # Call clean before saving
        self.full_clean()  # Runs clean() and field validation
        super().save(*args, **kwargs)

# Field-level clean methods:
class Task(models.Model):
    title = models.CharField(max_length=200)

    def clean_title(self):
        """Clean specific field"""
        title = self.title
        if 'spam' in title.lower():
            raise ValidationError('Title cannot contain spam')
        return title.strip().title()

# In forms (automatic):
from django import forms

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'

    # Form submission automatically calls model.clean()

# Manual validation:
task = Task(title="Fix bug", start_date=date(2025, 1, 10), end_date=date(2025, 1, 5))
try:
    task.full_clean()  # Validates everything
    task.save()
except ValidationError as e:
    print(e.message_dict)

# Note: save() does NOT call clean() automatically!
# Must call full_clean() explicitly or use ModelForm
```

**69. Explain `get_absolute_url()` method**

```python
from django.urls import reverse

class Task(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def get_absolute_url(self):
        """Returns canonical URL for this object"""
        return reverse('tasks:task-detail', kwargs={'pk': self.pk})
        # Or: return f'/tasks/{self.pk}/'
        # Or: return reverse('tasks:task-detail', kwargs={'slug': self.slug})

class Project(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def get_absolute_url(self):
        return reverse('projects:project-detail', kwargs={'slug': self.slug})

# Usage:

# 1. In views (redirect after create/update)
from django.views.generic import CreateView

class TaskCreateView(CreateView):
    model = Task
    fields = ['title', 'description']
    # Automatically redirects to get_absolute_url() after save

# 2. In templates
# <a href="{{ task.get_absolute_url }}">View Task</a>

# 3. In code
task = Task.objects.get(id=1)
url = task.get_absolute_url()
return redirect(url)

# 4. With Django admin
class TaskAdmin(admin.ModelAdmin):
    # "View on site" link uses get_absolute_url()
    pass

# Benefits:
# - DRY principle (single source of truth for URLs)
# - Easier refactoring (change URLs in one place)
# - Works with generic views automatically
```

---

### Migrations

**70. What are Django migrations?**

Migrations are Django's way of propagating model changes to the database schema.

```python
# Migrations track:
# - Creating models
# - Adding/removing fields
# - Changing field types
# - Adding indexes/constraints
# - Data migrations

# Migration file example: 0001_initial.py
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('status', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
```

**71. How do you create and apply migrations?**

```bash
# 1. makemigrations - Create migration files from model changes
python manage.py makemigrations
python manage.py makemigrations tasks  # Specific app
python manage.py makemigrations --name add_priority_field tasks  # Named

# 2. migrate - Apply migrations to database
python manage.py migrate
python manage.py migrate tasks  # Specific app
python manage.py migrate tasks 0003  # To specific migration

# 3. showmigrations - Show migration status
python manage.py showmigrations
# [X] = applied, [ ] = not applied

# 4. sqlmigrate - Show SQL for migration (without executing)
python manage.py sqlmigrate tasks 0001

# 5. Check for issues
python manage.py makemigrations --check  # CI/CD
python manage.py migrate --plan  # Show what will happen

# 6. Create empty migration (for data migrations)
python manage.py makemigrations --empty tasks
```

**72. What is the difference between `makemigrations` and `migrate`?**

```bash
# makemigrations:
# - Scans models.py files
# - Detects changes since last migration
# - Creates Python migration files in migrations/
# - Does NOT touch database
# - Files should be committed to version control

python manage.py makemigrations
# Creates: tasks/migrations/0001_initial.py

# migrate:
# - Reads migration files
# - Executes SQL against database
# - Updates django_migrations table
# - Actually modifies database schema

python manage.py migrate
# Executes SQL: CREATE TABLE tasks...

# Workflow:
# 1. Change models.py
# 2. Run makemigrations (creates migration file)
# 3. Review migration file
# 4. Run migrate (applies to database)
# 5. Commit migration file to git
```

**73. How do you handle data migrations?**

```python
# Create empty migration
# python manage.py makemigrations --empty tasks --name populate_default_priorities

from django.db import migrations

def populate_priorities(apps, schema_editor):
    """Forward migration - add data"""
    Task = apps.get_model('tasks', 'Task')
    for task in Task.objects.all():
        if not task.priority:
            task.priority = 'medium'
            task.save()

def reverse_priorities(apps, schema_editor):
    """Reverse migration - undo"""
    Task = apps.get_model('tasks', 'Task')
    for task in Task.objects.all():
        task.priority = None
        task.save()

class Migration(migrations.Migration):
    dependencies = [
        ('tasks', '0005_task_priority'),
    ]

    operations = [
        migrations.RunPython(
            populate_priorities,
            reverse_code=reverse_priorities
        ),
    ]

# Complex data migration example:
def migrate_user_data(apps, schema_editor):
    OldUser = apps.get_model('accounts', 'OldUser')
    NewUser = apps.get_model('accounts', 'User')

    for old_user in OldUser.objects.all():
        NewUser.objects.create(
            email=old_user.username + '@example.com',
            first_name=old_user.name.split()[0],
            last_name=' '.join(old_user.name.split()[1:]),
        )

# Bulk operations for performance:
def bulk_update_status(apps, schema_editor):
    Task = apps.get_model('tasks', 'Task')
    tasks = Task.objects.filter(status='open')
    tasks.update(status='todo')  # Efficient bulk update

# Important notes:
# - Use apps.get_model() not direct import
# - Historical models (may not have current methods)
# - Always provide reverse_code
# - Test thoroughly before production
```

**74. What happens when you have migration conflicts?**

```bash
# Conflict occurs when:
# - Two people create migrations with same number
# - Parallel branches both add migrations

# Example conflict:
# Branch A: 0003_add_priority.py
# Branch B: 0003_add_due_date.py

# Detect conflicts:
python manage.py makemigrations --check

# Fix conflicts:
# 1. Identify conflicting migrations
python manage.py showmigrations tasks
# [ ] 0003_add_priority
# [ ] 0003_add_due_date  # CONFLICT!

# 2. Merge migrations
python manage.py makemigrations --merge
# Creates: 0004_merge_20250113_1234.py

# The merge migration:
class Migration(migrations.Migration):
    dependencies = [
        ('tasks', '0003_add_priority'),
        ('tasks', '0003_add_due_date'),
    ]
    operations = []  # Empty, just declares dependencies

# 3. Apply merged migration
python manage.py migrate

# Prevention:
# - Pull latest code before makemigrations
# - Communicate with team
# - Use feature branches
# - Run makemigrations on main branch only
```

**75. How do you rollback migrations?**

```bash
# Rollback to specific migration
python manage.py migrate tasks 0002  # Rollback to 0002
python manage.py migrate tasks zero  # Rollback all (delete tables)

# Show migration before rolling back
python manage.py sqlmigrate tasks 0003 --backwards

# Rollback and delete migration file
# 1. Rollback:
python manage.py migrate tasks 0002

# 2. Delete migration file:
rm tasks/migrations/0003_add_field.py

# 3. Recreate if needed:
python manage.py makemigrations

# Fake migrations (dangerous!)
# Use when migrations out of sync with database

# Mark as applied without running SQL:
python manage.py migrate --fake tasks 0003

# Mark as unapplied:
python manage.py migrate --fake tasks 0002

# Fake initial (for existing databases):
python manage.py migrate --fake-initial

# Squashing migrations (clean up history):
python manage.py squashmigrations tasks 0001 0010
# Combines migrations 0001-0010 into single file

# Production rollback strategy:
# 1. Backup database first!
# 2. Test rollback in staging
# 3. Rollback application code
# 4. Rollback migrations
# 5. Verify data integrity
```

---

## Django REST Framework

### DRF Basics

**76. What is Django REST Framework (DRF)?**

DRF is a powerful toolkit for building Web APIs in Django.

**Features:**
- Serialization (Python ↔ JSON)
- Authentication (Token, JWT, OAuth, Session)
- Permissions (IsAuthenticated, IsAdminUser, custom)
- ViewSets (CRUD operations)
- Routers (automatic URL routing)
- Pagination
- Filtering, Searching, Ordering
- Throttling (rate limiting)
- API browsing (web UI)

```python
# Simple API example:
from rest_framework import serializers, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Serializer
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'status', 'priority']

# ViewSet
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

# Router (generates URLs automatically)
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('tasks', TaskViewSet)

# urls.py
urlpatterns = [
    path('api/', include(router.urls)),
]

# Generated endpoints:
# GET    /api/tasks/         # List
# POST   /api/tasks/         # Create
# GET    /api/tasks/{id}/    # Retrieve
# PUT    /api/tasks/{id}/    # Update
# PATCH  /api/tasks/{id}/    # Partial update
# DELETE /api/tasks/{id}/    # Delete
```

**77. What are serializers in DRF?**

Serializers convert complex data (QuerySets, model instances) to Python datatypes that can be rendered as JSON/XML.

```python
from rest_framework import serializers

# Basic serializer
class TaskSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=200)
    status = serializers.ChoiceField(choices=['todo', 'in_progress', 'completed'])
    created_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return Task.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

# Usage:
# Serialize (Python → JSON)
task = Task.objects.get(id=1)
serializer = TaskSerializer(task)
serializer.data  # {'id': 1, 'title': 'Fix bug', ...}

# Deserialize (JSON → Python)
data = {'title': 'New task', 'status': 'todo'}
serializer = TaskSerializer(data=data)
if serializer.is_valid():
    task = serializer.save()
else:
    print(serializer.errors)
```

**78. Explain the difference between `Serializer` and `ModelSerializer`**

```python
# Serializer - Manual field definition
class TaskSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=200)
    description = serializers.CharField()
    status = serializers.CharField()

    def create(self, validated_data):
        return Task.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

# ModelSerializer - Automatic from model (DRY)
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status']
        # Or: fields = '__all__'
        # Or: exclude = ['internal_notes']

        read_only_fields = ['created_at', 'id']

        extra_kwargs = {
            'description': {'required': False},
            'status': {'default': 'todo'},
        }

    # Automatically generates:
    # - All field definitions
    # - create() method
    # - update() method

# When to use which:
# Serializer: Non-model data, complete control
# ModelSerializer: Model-based APIs (95% of cases)

# Custom fields in ModelSerializer:
class TaskSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'owner_name', 'is_overdue']
```

**79. What are DRF ViewSets?**

ViewSets combine logic for multiple related views in a single class.

```python
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

# ModelViewSet - Full CRUD
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    # Provides these actions automatically:
    # - list() - GET /tasks/
    # - create() - POST /tasks/
    # - retrieve() - GET /tasks/{id}/
    # - update() - PUT /tasks/{id}/
    # - partial_update() - PATCH /tasks/{id}/
    # - destroy() - DELETE /tasks/{id}/

# ReadOnlyModelViewSet - Only list and retrieve
class TaskViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    # Only list() and retrieve()

# Custom actions
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    # Custom action: POST /tasks/{id}/complete/
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = 'completed'
        task.save()
        return Response({'status': 'task completed'})

    # Custom list action: GET /tasks/overdue/
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        overdue_tasks = Task.objects.filter(
            due_date__lt=timezone.now(),
            status__in=['todo', 'in_progress']
        )
        serializer = self.get_serializer(overdue_tasks, many=True)
        return Response(serializer.data)

# Mixins for custom combinations
from rest_framework import mixins

class TaskViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin,
                   viewsets.GenericViewSet):
    # List, Retrieve, Create only (no update/delete)
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
```

**80. What is the difference between APIView, ViewSet, and ModelViewSet?**

```python
# 1. APIView - Most control, most code
from rest_framework.views import APIView

class TaskList(APIView):
    def get(self, request):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class TaskDetail(APIView):
    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def put(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

# URLs:
urlpatterns = [
    path('tasks/', TaskList.as_view()),
    path('tasks/<int:pk>/', TaskDetail.as_view()),
]

# 2. ViewSet - Less code, use with router
from rest_framework import viewsets

class TaskViewSet(viewsets.ViewSet):
    def list(self, request):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def create(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

# URLs (with router):
router = DefaultRouter()
router.register('tasks', TaskViewSet, basename='task')

# 3. ModelViewSet - Least code, most automation
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    # That's it! Full CRUD implemented

# Comparison:
# APIView: Maximum control, explicit, verbose
# ViewSet: Middle ground, works with routers
# ModelViewSet: Quickest, automatic CRUD, less control

# Choose:
# APIView: Non-standard behavior, simple endpoints
# ViewSet: Custom actions, standard patterns
# ModelViewSet: Standard CRUD for models (most common)
```

**81. What are DRF routers? How do they work?**

Routers automatically generate URL patterns for ViewSets.

```python
from rest_framework.routers import DefaultRouter, SimpleRouter

# DefaultRouter - includes API root view
router = DefaultRouter()
router.register('tasks', TaskViewSet)
router.register('projects', ProjectViewSet)

# urls.py
urlpatterns = [
    path('api/', include(router.urls)),
]

# Generated URLs:
# GET    /api/                 # API root (DefaultRouter only)
# GET    /api/tasks/           # TaskViewSet.list()
# POST   /api/tasks/           # TaskViewSet.create()
# GET    /api/tasks/{pk}/      # TaskViewSet.retrieve()
# PUT    /api/tasks/{pk}/      # TaskViewSet.update()
# PATCH  /api/tasks/{pk}/      # TaskViewSet.partial_update()
# DELETE /api/tasks/{pk}/      # TaskViewSet.destroy()

# Custom actions:
class TaskViewSet(viewsets.ModelViewSet):
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        pass

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        pass

# Generates:
# POST /api/tasks/{pk}/complete/
# GET  /api/tasks/overdue/

# SimpleRouter - no API root
router = SimpleRouter()

# Custom URL prefix/basename
router.register('my-tasks', TaskViewSet, basename='mytask')
# /api/my-tasks/

# Nested routers (with drf-nested-routers package)
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('projects', ProjectViewSet)

# Nest tasks under projects
project_router = routers.NestedDefaultRouter(router, 'projects', lookup='project')
project_router.register('tasks', TaskViewSet)

# Generates:
# /api/projects/{project_pk}/tasks/
# /api/projects/{project_pk}/tasks/{pk}/

# Multiple routers
router_v1 = DefaultRouter()
router_v1.register('tasks', TaskViewSetV1)

router_v2 = DefaultRouter()
router_v2.register('tasks', TaskViewSetV2)

urlpatterns = [
    path('api/v1/', include(router_v1.urls)),
    path('api/v2/', include(router_v2.urls)),
]
```

**82. Explain different serializer fields**

```python
from rest_framework import serializers

class TaskSerializer(serializers.ModelSerializer):
    # SerializerMethodField - custom computed field
    days_until_due = serializers.SerializerMethodField()

    def get_days_until_due(self, obj):
        if not obj.due_date:
            return None
        delta = obj.due_date - timezone.now()
        return delta.days

    # PrimaryKeyRelatedField - show/set by ID
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all()
    )
    # Input/Output: {"project": 5}

    # SlugRelatedField - show/set by slug
    project = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Project.objects.all()
    )
    # Input/Output: {"project": "My Project"}

    # StringRelatedField - read-only __str__
    created_by = serializers.StringRelatedField()
    # Output: "John Doe"

    # Nested serializer - full object
    created_by = UserSerializer(read_only=True)
    # Output: {"id": 1, "email": "john@example.com", "first_name": "John"}

    # HyperlinkedRelatedField - show as URL
    project = serializers.HyperlinkedRelatedField(
        view_name='project-detail',
        queryset=Project.objects.all()
    )
    # Output: {"project": "http://example.com/api/projects/5/"}

    # ListField - list of items
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50)
    )
    # Input/Output: {"tags": ["bug", "urgent", "backend"]}

    # JSONField - arbitrary JSON data
    metadata = serializers.JSONField()
    # Input/Output: {"metadata": {"key": "value", "nested": {...}}}

    # ReadOnlyField - read-only property
    is_overdue = serializers.ReadOnlyField()

    # HiddenField - set value programmatically
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Task
        fields = ['id', 'title', 'project', 'created_by', 'days_until_due',
                  'tags', 'metadata', 'is_overdue', 'owner']

# Many-to-many relationships
class ProjectSerializer(serializers.ModelSerializer):
    # Show related objects
    tasks = TaskSerializer(many=True, read_only=True)

    # Or just IDs
    task_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Task.objects.all(),
        source='tasks'
    )

    class Meta:
        model = Project
        fields = ['id', 'name', 'tasks', 'task_ids']

# File fields
class AttachmentSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
    image = serializers.ImageField()

    class Meta:
        model = Attachment
        fields = ['id', 'file', 'image']
```

---

*[This is a massive document! I've completed significant portions covering Python fundamentals, Django basics, ORM, DRF basics. Would you like me to continue with the remaining sections (Authentication, Caching, Celery, Databases, Project-specific questions, Advanced topics, etc.)? Or would you prefer I focus on specific sections that are most important for your interview?]*

Due to length constraints, I recommend breaking this into multiple files or focusing on specific topics. Should I continue with specific sections you're most interested in?