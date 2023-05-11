from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import UserManager


# Create your models here.
class Organization(models.Model):
    org_id = models.AutoField(primary_key=True)
    org_name = models.CharField(max_length=50)
    org_description = models.CharField(max_length=50, default="")
    org_secret_key = models.CharField(max_length=50)
    org_is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.org_id


class User(AbstractBaseUser, PermissionsMixin):
    email = models.CharField(max_length=150, unique=True)
    token = models.CharField(max_length=150)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    org_id = models.CharField(max_length=100)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['password', 'org_id']

    objects = UserManager()

    def __str__(self):
        return {
            'org_id': self.org_id,
            'email': self.email,
            'id': self.id
        }