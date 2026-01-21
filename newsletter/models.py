from django.db import models
from django.core.validators import EmailValidator


import uuid
from datetime import timedelta
from django.utils import timezone
class Email(models.Model):
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, unique=True, null=True, blank=True)
    verification_sent_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Subscriber Email"
        verbose_name_plural = "Subscriber Emails"
        ordering = ['-created_at']
