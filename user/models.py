from django.db import models
from main.models import TimeStampedModel
from django.contrib.auth.models import AbstractUser
import secrets


def generate_token():
    return secrets.token_hex(32)


class User(AbstractUser):
    pass


class AuthToken(TimeStampedModel):
    id = models.CharField(
        max_length=64, default=generate_token, unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} - {self.id}"


class SocialConnector(models.Model):
    SOCIAL_PROVIDER_CHOICES = (
        ('google', 'google'),
        ('kakao', 'kakao'),
        ('naver', 'naver'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    social_provider = models.CharField(
        max_length=100, choices=SOCIAL_PROVIDER_CHOICES)
    social_id = models.CharField(max_length=256)

    class Meta:
        unique_together = ['social_provider', 'social_id']
