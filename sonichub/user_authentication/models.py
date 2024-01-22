from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid

class CustomUserManager(BaseUserManager):
  def create_user(self, email, password = None, **extra_fields):
    if not email:
      raise ValueError('Email should not be empty')
    email = self.normalize_email(email)
    username = email.split('@')[0]
    user = self.model(email=email, username = username, **extra_fields)
    
    user.is_active = False
    user.set_password(password)
    user.save(using = self._db)
    return user
  

  def create_superuser(self, email, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
        )

        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
  

class UserProfile(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=40, unique=True, blank=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=False, unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    referral_codes = models.UUIDField(default=uuid.uuid4, editable=False)
   

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email