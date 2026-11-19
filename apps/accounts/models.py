from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel

# Create your models here.
class UserManager(BaseUserManager):
    use_in_migrations = True

    def get_by_natural_key(self, email):
        # Used by the login backend: makes email login case-insensitive.
        return self.get(email__iexact=email)

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('An email address is required.')
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model that logs in with email. Personal details live on Profile."""

    username = None
    # unique=True is required by Django for the USERNAME_FIELD (system check auth.E003).
    # The Lower() constraint below additionally makes it case-insensitive.
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        constraints = [
            # Guards against Anna@x.se vs anna@x.se even for writes that skip save().
            models.UniqueConstraint(Lower('email'), name='unique_user_email_ci'),
        ]

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)


class Profile(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    display_name = models.CharField(_('display name'), max_length=80, blank=True)
    bio = models.TextField(_('bio'), max_length=500, blank=True)
    phone_number = models.CharField(_('phone number'), max_length=32, blank=True)
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', blank=True)

    def __str__(self):
        return self.name

    @property
    def name(self):
        return self.display_name or self.user.get_full_name() or self.user.email
