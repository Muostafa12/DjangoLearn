"""
User models for the taskmaster application.
Demonstrates custom user model and one-to-one relationships.
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password"""
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model that uses email instead of username for authentication.
    This is a common pattern in modern web applications.
    """
    username = None  # Remove username field
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        db_table = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """Return the user's full name"""
        return f"{self.first_name} {self.last_name}".strip()


class UserProfile(models.Model):
    """
    Extended user profile information.
    Demonstrates one-to-one relationship with User model.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(_('bio'), blank=True, max_length=500)
    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/%Y/%m/%d/',
        blank=True,
        null=True
    )
    phone_number = models.CharField(
        _('phone number'),
        max_length=15,
        blank=True
    )
    location = models.CharField(
        _('location'),
        max_length=100,
        blank=True
    )
    website = models.URLField(_('website'), blank=True)
    github_username = models.CharField(
        _('GitHub username'),
        max_length=100,
        blank=True
    )

    # Preferences
    email_notifications = models.BooleanField(
        _('email notifications'),
        default=True,
        help_text=_('Receive email notifications for task updates')
    )
    theme = models.CharField(
        _('theme'),
        max_length=10,
        choices=[
            ('light', _('Light')),
            ('dark', _('Dark')),
            ('auto', _('Auto')),
        ],
        default='auto'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')

    def __str__(self):
        return f"{self.user.full_name}'s profile"
