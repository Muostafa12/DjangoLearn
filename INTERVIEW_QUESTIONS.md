# Python & Django Interview Questions

## Table of Contents
1. [Python Fundamentals](#python-fundamentals)
2. [Django Basics](#django-basics)
3. [Django ORM & Models](#django-orm--models)
4. [Django REST Framework](#django-rest-framework)
5. [Authentication & Authorization](#authentication--authorization)
6. [Caching & Performance](#caching--performance)
7. [Celery & Async Tasks](#celery--async-tasks)
8. [Database & PostgreSQL](#database--postgresql)
9. [Project-Specific Questions](#project-specific-questions)
10. [Advanced Topics](#advanced-topics)
11. [Best Practices & Design Patterns](#best-practices--design-patterns)

---

## Python Fundamentals

### Basic Python
1. **What are Python decorators and how do you use them?**
   - Explain with examples of `@property`, `@staticmethod`, `@classmethod`

2. **Explain the difference between `__str__` and `__repr__` methods**

3. **What is the difference between `@staticmethod` and `@classmethod`?**

4. **What are Python's built-in data structures?**
   - List, Tuple, Set, Dictionary, frozenset

5. **Explain list comprehensions and generator expressions**

6. **What is the difference between `is` and `==` in Python?**

7. **Explain mutable vs immutable objects in Python**

8. **What are `*args` and `**kwargs`? When would you use them?**

9. **Explain Python's Global Interpreter Lock (GIL)**

10. **What are context managers? Explain `with` statement**

### Advanced Python
11. **What are metaclasses in Python?**

12. **Explain Python's method resolution order (MRO)**

13. **What is the difference between `@property` and `@cached_property`?**

14. **How does Python's garbage collection work?**

15. **Explain the difference between shallow copy and deep copy**

16. **What are Python descriptors?**

17. **Explain `__new__` vs `__init__`**

18. **What is duck typing in Python?**

19. **How do you handle exceptions in Python? Explain custom exceptions**

20. **What are Python's async/await keywords?**

---

## Django Basics

### Core Concepts
21. **What is Django and what are its main features?**
   - ORM, Admin interface, Authentication, URL routing, Template engine, etc.

22. **Explain Django's MTV (Model-Template-View) architecture**
   - How it differs from MVC

23. **What is the Django ORM and what advantages does it provide?**

24. **Explain the request-response cycle in Django**

25. **What is `settings.py` and what configurations go there?**

26. **What is the purpose of `manage.py`?**

27. **What are Django apps? How do they differ from a project?**

28. **Explain `INSTALLED_APPS` in Django settings**

29. **What is Django middleware? Name some common middleware**

30. **Explain `MIDDLEWARE` order and why it matters**

### URL Routing & Views
31. **How does Django URL routing work?**
   - `urls.py`, `path()`, `include()`, `re_path()`

32. **What is the difference between function-based views (FBV) and class-based views (CBV)?**

33. **Explain Django's generic views**
   - ListView, DetailView, CreateView, UpdateView, DeleteView

34. **What are URL namespaces and why use them?**

35. **How do you pass parameters in Django URLs?**

36. **What is `reverse()` and `reverse_lazy()`?**

### Templates
37. **What is Django's template language (DTL)?**

38. **Explain template inheritance with `{% extends %}` and `{% block %}`**

39. **What are template filters and custom template tags?**

40. **What is `{% csrf_token %}` and why is it important?**

---

## Django ORM & Models

### Model Basics
41. **What is a Django model?**

42. **Explain common Django field types**
   - CharField, TextField, IntegerField, DateTimeField, ForeignKey, etc.

43. **What is the difference between `null=True` and `blank=True`?**

44. **What are model Meta options?**
   - `ordering`, `verbose_name`, `db_table`, `indexes`, `constraints`

45. **Explain `on_delete` options for ForeignKey**
   - CASCADE, PROTECT, SET_NULL, SET_DEFAULT, DO_NOTHING

46. **What is the purpose of `related_name` in relationships?**

47. **How do you create a custom user model in Django?**
   - Reference: `taskmaster/accounts/models.py` - User model

48. **What is `AbstractUser` vs `AbstractBaseUser`?**

### Relationships
49. **Explain the three types of model relationships in Django**
   - One-to-One, Many-to-One (ForeignKey), Many-to-Many

50. **What is a "through" model in Many-to-Many relationships?**
   - Reference: `ProjectMember` model in `projects/models.py`

51. **How do you implement self-referencing relationships?**
   - Reference: Task's `parent_task` and Comment's `parent_comment`

52. **Explain `OneToOneField` and when to use it**
   - Reference: `UserProfile` relationship with `User`

### QuerySets & Queries
53. **What is a QuerySet in Django?**

54. **Explain `select_related()` vs `prefetch_related()`**
   - When to use each for performance optimization

55. **What is the N+1 query problem? How do you solve it?**

56. **Explain lazy loading in Django QuerySets**

57. **What are Django Q objects? When would you use them?**
   - Complex queries with OR logic

58. **What is the difference between `filter()` and `get()`?**

59. **Explain `annotate()` and `aggregate()` in Django**

60. **How do you create custom QuerySet managers?**
   - Reference: `TaskManager` in `tasks/models.py`

61. **What is `values()` vs `values_list()` in QuerySets?**

62. **Explain `exists()`, `count()`, and when to use each**

63. **How do you perform raw SQL queries in Django?**

64. **What is `defer()` and `only()` in QuerySets?**

### Model Methods & Properties
65. **What is the difference between model methods and properties?**

66. **Explain `@property` decorator in Django models**
   - Reference: `full_name` in User model, `is_overdue` in Task model

67. **What is `save()` method and when would you override it?**

68. **What is `clean()` method in Django models?**

69. **Explain `get_absolute_url()` method**

### Migrations
70. **What are Django migrations?**

71. **How do you create and apply migrations?**
   - `makemigrations`, `migrate`, `showmigrations`, `sqlmigrate`

72. **What is the difference between `makemigrations` and `migrate`?**

73. **How do you handle data migrations?**

74. **What happens when you have migration conflicts?**

75. **How do you rollback migrations?**

---

## Django REST Framework

### DRF Basics
76. **What is Django REST Framework (DRF)?**

77. **What are serializers in DRF?**

78. **Explain the difference between `Serializer` and `ModelSerializer`**

79. **What are DRF ViewSets?**
   - Reference: All viewsets in the project

80. **What is the difference between APIView, ViewSet, and ModelViewSet?**

81. **What are DRF routers? How do they work?**

82. **Explain different serializer fields**
   - SerializerMethodField, PrimaryKeyRelatedField, SlugRelatedField, etc.

### Authentication & Permissions
83. **What authentication methods does DRF support?**
   - Session, Token, JWT, OAuth

84. **What is JWT (JSON Web Token) authentication?**
   - Reference: Project uses `djangorestframework-simplejwt`

85. **Explain access tokens vs refresh tokens**

86. **What are DRF permission classes?**
   - IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny

87. **How do you create custom permission classes?**

88. **What is the difference between authentication and authorization?**

### API Design
89. **What are HTTP methods and their purposes?**
   - GET, POST, PUT, PATCH, DELETE

90. **What are status codes? Explain common ones**
   - 200, 201, 204, 400, 401, 403, 404, 500

91. **How do you implement pagination in DRF?**
   - PageNumberPagination, LimitOffsetPagination, CursorPagination

92. **What are filters in DRF? How do you implement them?**
   - Reference: `django-filter` usage in project

93. **Explain search and ordering in DRF**

94. **How do you handle file uploads in DRF?**
   - Reference: `TaskAttachment` model and `upload_attachment` action

95. **What are nested serializers? When would you use them?**

96. **How do you implement custom actions in ViewSets?**
   - Reference: `@action` decorator usage (mark_completed, add_member, etc.)

97. **What is content negotiation in DRF?**

98. **How do you version your API in DRF?**

99. **What are throttling and rate limiting in DRF?**

---

## Authentication & Authorization

### Django Auth
100. **What is Django's built-in authentication system?**

101. **How do you implement user registration in Django?**
    - Reference: `UserRegistrationView` in `accounts/views.py`

102. **What is `AUTH_USER_MODEL` setting?**
    - Reference: Custom User model in settings

103. **How do you implement password reset functionality?**

104. **What are Django's password validators?**

105. **How do you hash passwords in Django?**
    - `make_password()`, `check_password()`

106. **What is `is_authenticated` vs `is_active` vs `is_staff`?**

107. **How do you implement role-based access control?**
    - Reference: `ProjectMember` roles (owner, admin, member, viewer)

108. **What are permissions in Django? How do you create custom permissions?**

109. **What is the difference between `@login_required` decorator and `LoginRequiredMixin`?**

110. **How do you implement email-based authentication instead of username?**
    - Reference: Custom User model without username field

---

## Caching & Performance

### Caching
111. **What is caching and why is it important?**

112. **What caching backends does Django support?**
    - Memcached, Redis, Database, File-based, Local memory

113. **How do you configure Redis as a cache backend in Django?**
    - Reference: `settings.py` CACHES configuration

114. **What is `django-redis` and why use it?**

115. **Explain different caching strategies**
    - Per-view caching, Template fragment caching, Low-level cache API

116. **How do you use the `@cache_page` decorator?**

117. **What is cache invalidation? How do you handle it?**

118. **How do you cache QuerySets?**

119. **What is the difference between cache and session storage?**

120. **How do you use Redis for session storage?**
    - Reference: `SESSION_ENGINE` in settings

### Performance Optimization
121. **How do you optimize database queries in Django?**

122. **What is database indexing? How do you add indexes in Django models?**
    - Reference: `Meta.indexes` in Task and Notification models

123. **What is `django-debug-toolbar` and how does it help?**

124. **How do you identify and fix N+1 query problems?**

125. **What is query optimization? Explain `only()`, `defer()`, `select_related()`, `prefetch_related()`**

126. **How do you use `Prefetch` objects for complex prefetching?**

127. **What are database connection pooling strategies?**

128. **How do you handle large file uploads efficiently?**

129. **What is pagination and why is it important?**

130. **How do you implement database read replicas in Django?**

---

## Celery & Async Tasks

### Celery Basics
131. **What is Celery and why use it?**

132. **What is a message broker? What options does Celery support?**
    - RabbitMQ, Redis, Amazon SQS

133. **What is the difference between Celery and Django's async views?**

134. **How do you configure Celery with Django?**
    - Reference: `taskmaster/celery.py`

135. **What is the `@shared_task` decorator?**
    - Reference: All tasks in `notifications/tasks.py`

136. **What is a result backend in Celery?**

137. **How do you call Celery tasks?**
    - `delay()`, `apply_async()`, `apply()`

### Task Management
138. **What is Celery Beat? What is it used for?**
    - Reference: Periodic tasks configuration

139. **How do you schedule periodic tasks with Celery Beat?**
    - Reference: `send_daily_task_reminders` and `cleanup_old_notifications`

140. **What are Celery task states?**
    - PENDING, STARTED, SUCCESS, FAILURE, RETRY, REVOKED

141. **How do you handle task failures and retries in Celery?**

142. **What is `task_time_limit` and `task_soft_time_limit`?**

143. **How do you monitor Celery tasks?**
    - Flower, Celery events, task tracking

144. **What are Celery chains, groups, and chords?**

145. **How do you pass arguments to Celery tasks?**

146. **How do you implement task callbacks and error callbacks?**

147. **What is task routing in Celery?**

### Real-World Async Use Cases
148. **When should you use Celery tasks vs synchronous code?**

149. **How do you send notifications asynchronously?**
    - Reference: Notification tasks in the project

150. **How do you handle email sending in background tasks?**
    - Reference: `send_email_notification` task

---

## Database & PostgreSQL

### Database Basics
151. **Why use PostgreSQL over SQLite in production?**

152. **What are database transactions in Django?**
    - `transaction.atomic()`

153. **What is database connection pooling?**

154. **How do you handle database migrations in production?**

155. **What are database indexes and when should you use them?**

156. **What is a database constraint? What types exist in Django?**
    - UniqueConstraint, CheckConstraint

157. **Explain ACID properties in databases**

### PostgreSQL Specific
158. **What PostgreSQL-specific features does Django support?**
    - ArrayField, JSONField, HStoreField, full-text search

159. **How do you implement full-text search with PostgreSQL in Django?**

160. **What is `psycopg2` and `psycopg2-binary`?**

161. **How do you configure database connection pooling with PostgreSQL?**

162. **What are PostgreSQL indexes types?**
    - B-tree, Hash, GiST, GIN

---

## Project-Specific Questions

### TaskMaster Project Architecture
163. **Explain the overall architecture of the TaskMaster project**

164. **What are the four main Django apps in this project?**
    - accounts, projects, tasks, notifications

165. **Why use a custom User model instead of Django's default?**

166. **How does the project-member relationship work?**
    - Through model with roles

167. **Explain the task hierarchy with parent-child relationships**

168. **How are notifications triggered in the system?**
    - Django signals connecting to Celery tasks

### Models & Business Logic
169. **How is task completion percentage calculated?**

170. **What is the difference between task status and priority?**

171. **How do subtasks work in the Task model?**
    - Self-referencing ForeignKey with `parent_task`

172. **How are nested comments implemented?**
    - Self-referencing ForeignKey with `parent_comment`

173. **What is the purpose of the `content_html` property in Comment model?**
    - Converts markdown to HTML

174. **How do you check if a task is overdue?**
    - `is_overdue` property comparing due_date with current time

175. **What roles exist for project members and what can each do?**
    - owner, admin, member, viewer - different permission levels

### Signals & Automation
176. **What Django signals are used in the project?**
    - `post_save`, `m2m_changed`

177. **How does the project automatically create UserProfile for new users?**
    - Signal receiver on User post_save

178. **How are task notifications sent when a task is created?**
    - Signal triggers Celery task asynchronously

179. **How does the system notify users when they're assigned to a task?**
    - `m2m_changed` signal on Task.assignees

### API Endpoints & Viewsets
180. **What custom actions exist on the ProjectViewSet?**
    - add_member, remove_member, statistics

181. **What custom actions exist on the TaskViewSet?**
    - mark_completed, mark_in_progress, add_comment, upload_attachment

182. **How does the notification system work via the API?**

183. **How is the current user accessed in the UserViewSet?**
    - Custom `me` action

184. **How do you prevent a project owner from being removed?**
    - Validation in `remove_member` action

### Caching Strategy
185. **Where is caching implemented in the project?**
    - User, Project, and Task detail views

186. **What is the cache timeout configured in the project?**
    - 5 minutes (300 seconds)

187. **How would you implement cache invalidation when a task is updated?**

### Celery Tasks
188. **What periodic tasks run in the project?**
    - Daily task reminders at 9 AM
    - Old notification cleanup at midnight

189. **How does the daily task reminder work?**

190. **What notifications trigger async email sending?**

### Security & Validation
191. **How does the project handle CORS?**
    - django-cors-headers with allowed origins

192. **What JWT token lifetimes are configured?**
    - Access: 1 hour, Refresh: 7 days

193. **Does the project rotate refresh tokens?**
    - Yes, with blacklist after rotation

194. **What password validators are used?**

---

## Advanced Topics

### Django Signals
195. **What are Django signals? List common built-in signals**
    - pre_save, post_save, pre_delete, post_delete, m2m_changed

196. **What is the difference between `pre_save` and `post_save`?**

197. **When should you use signals vs overriding save()?**

198. **What are signal receivers and how do you connect them?**

199. **What is `sender` parameter in signals?**

200. **How do you disconnect signals?**

### Generic Relations
201. **What are Django's ContentTypes and Generic Relations?**
    - Reference: Notification model uses GenericForeignKey

202. **When would you use GenericForeignKey?**

203. **What is the difference between ForeignKey and GenericForeignKey?**

204. **What are the limitations of GenericForeignKey?**

### Testing
205. **How do you write unit tests in Django?**
    - TestCase, TransactionTestCase, SimpleTestCase

206. **What is the difference between TestCase and TransactionTestCase?**

207. **How do you test Django REST Framework APIs?**
    - APITestCase, APIClient

208. **What is factory_boy and why use it?**
    - Reference: Project includes factory_boy for test factories

209. **How do you use faker for test data?**

210. **What is coverage.py and why is it important?**

211. **How do you test Celery tasks?**

212. **How do you mock external services in tests?**

### Django Admin
213. **How do you customize the Django admin interface?**

214. **What are InlineModelAdmin classes?**
    - Reference: UserProfile inline in User admin

215. **How do you add custom actions to Django admin?**

216. **What is `list_display`, `list_filter`, `search_fields`?**

217. **How do you override admin templates?**

### File Handling
218. **How do you handle file uploads in Django?**

219. **What is `MEDIA_ROOT` and `MEDIA_URL`?**

220. **How do you serve media files in development vs production?**

221. **What is Pillow library used for?**
    - Image processing

222. **How do you implement image resizing on upload?**

### Markdown & Rich Text
223. **How is markdown support implemented in the project?**
    - Reference: Task descriptions and Comments use markdown

224. **What is the markdown library and how do you use it?**

225. **How do you sanitize HTML to prevent XSS attacks?**

---

## Best Practices & Design Patterns

### Code Organization
226. **What is the "fat models, thin views" principle?**

227. **When should you use class-based views vs function-based views?**

228. **What is Django's recommended project structure?**

229. **How do you organize reusable code in Django?**
    - Utils, managers, mixins, base classes

230. **What are Django mixins? Provide examples**

### Security Best Practices
231. **What are common security vulnerabilities in Django applications?**
    - SQL Injection, XSS, CSRF, clickjacking

232. **How does Django protect against SQL injection?**

233. **How does Django protect against CSRF attacks?**

234. **What is `SECRET_KEY` and why is it important?**

235. **How do you handle sensitive configuration data?**
    - Reference: Project uses python-decouple

236. **What is HTTPS and why is it important?**

237. **How do you implement rate limiting to prevent abuse?**

238. **What is CORS and why is it needed?**

### Deployment & Production
239. **What is the difference between `DEBUG = True` and `DEBUG = False`?**

240. **How do you serve static files in production?**
    - collectstatic, CDN, WhiteNoise

241. **What is a WSGI server? What options are available?**
    - Gunicorn, uWSGI, mod_wsgi

242. **What is Docker and why use it for Django projects?**
    - Reference: Project includes docker-compose.yml

243. **How do you configure environment variables in production?**

244. **What is a reverse proxy? Why use Nginx with Django?**

245. **How do you implement logging in Django?**
    - Reference: LOGGING configuration in settings

246. **What is the purpose of health checks in Docker?**

247. **How do you handle database backups in production?**

248. **What is continuous integration/deployment (CI/CD)?**

### Performance & Scalability
249. **How do you handle high traffic in Django applications?**

250. **What is horizontal vs vertical scaling?**

251. **How do you implement load balancing?**

252. **What is database replication and when to use it?**

253. **How do you implement API rate limiting?**

254. **What is lazy loading and how does Django use it?**

255. **How do you optimize static file delivery?**

256. **What are microservices? When should you use them?**

### Code Quality
257. **What is PEP 8 and why is it important?**

258. **What linting tools do you use for Python/Django?**
    - flake8, pylint, black

259. **What is code coverage and what's a good target?**

260. **How do you handle technical debt?**

261. **What is refactoring and when should you do it?**

262. **What are code reviews and why are they important?**

### API Design Best Practices
263. **What is RESTful API design?**

264. **How do you version your APIs?**

265. **What is HATEOAS?**

266. **How do you handle API deprecation?**

267. **What is API documentation? What tools exist?**
    - Swagger/OpenAPI, drf-spectacular

268. **How do you design API responses consistently?**

269. **What is idempotency in APIs?**

270. **How do you handle API errors consistently?**

---

## Behavioral & Scenario Questions

### Problem Solving
271. **How would you implement real-time notifications in Django?**
    - WebSockets, Django Channels, Server-Sent Events

272. **How would you implement a search feature across multiple models?**

273. **How would you implement audit logging for model changes?**

274. **How would you implement soft delete functionality?**

275. **How would you implement multi-tenancy in Django?**

276. **How would you handle time zones in a global application?**

277. **How would you implement a commenting system with nested replies?**
    - Reference: Project implementation with self-referencing FK

278. **How would you implement file versioning?**

279. **How would you implement a notification preference system?**

280. **How would you scale a Django application handling millions of users?**

### Debugging
281. **How do you debug Django applications?**
    - Django Debug Toolbar, logging, pdb, print statements

282. **How do you troubleshoot slow database queries?**

283. **How do you debug Celery tasks?**

284. **How do you handle memory leaks in Django?**

285. **What tools do you use for monitoring Django in production?**
    - Sentry, New Relic, Datadog

### Design Decisions
286. **Why did you choose PostgreSQL over MySQL?**

287. **Why use Redis for both caching and Celery broker?**

288. **Why use JWT instead of session-based authentication for APIs?**

289. **When would you use a NoSQL database instead of PostgreSQL?**

290. **How do you decide what to cache and for how long?**

---

## Coding Challenges

### Common Interview Problems
291. **Write a Django model for a blog with posts, comments, and tags**

292. **Write a serializer that handles nested relationships**

293. **Write a custom permission class that checks object-level permissions**

294. **Write a signal handler that logs all model changes**

295. **Write a custom Django management command**

296. **Write a middleware that logs request duration**

297. **Write a custom model manager with complex filters**

298. **Write a Celery task that handles retries and error logging**

299. **Write a custom authentication backend**

300. **Write unit tests for a Django API endpoint with authentication**

---

## Tips for Interview Success

### Preparation
- Review your project code thoroughly - be ready to explain any part
- Understand why you made specific design decisions
- Practice explaining complex concepts simply
- Be ready to write code on a whiteboard or shared editor
- Review Django and DRF documentation

### During Interview
- Ask clarifying questions before solving problems
- Think out loud - explain your thought process
- Consider edge cases and error handling
- Discuss trade-offs of different approaches
- Be honest if you don't know something
- Show willingness to learn

### Key Areas to Master
1. Django ORM queries and optimization
2. REST API design principles
3. Authentication and authorization
4. Caching strategies
5. Async task processing with Celery
6. Database design and relationships
7. Testing strategies
8. Security best practices
9. Performance optimization
10. Production deployment considerations

---

## Project Reference Locations

Key files to review before interview:

**Models:**
- `taskmaster/accounts/models.py` - Custom User & UserProfile
- `taskmaster/projects/models.py` - Project & ProjectMember
- `taskmaster/tasks/models.py` - Task, Comment, TaskAttachment
- `taskmaster/notifications/models.py` - Notification system

**Views & ViewSets:**
- `taskmaster/accounts/views.py` - User management
- `taskmaster/projects/views.py` - Project CRUD & member management
- `taskmaster/tasks/views.py` - Task CRUD & custom actions
- `taskmaster/notifications/views.py` - Notification handling

**Configuration:**
- `taskmaster/settings.py` - All Django settings
- `taskmaster/celery.py` - Celery configuration
- `docker-compose.yml` - Infrastructure setup
- `requirements.txt` - Dependencies

**Async Tasks:**
- `taskmaster/notifications/tasks.py` - All Celery tasks

**Signals:**
- `taskmaster/accounts/signals.py` - User signals
- `taskmaster/tasks/signals.py` - Task & comment signals

---

Good luck with your interview! 🚀
