from django.db import models
from main.models import TimeStampedModel
from django.contrib.auth.models import AbstractUser
import secrets
from django.core.exceptions import ValidationError
from main.sms import send_sms
from enum import Enum
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone


def generate_token():
    return secrets.token_hex(32)


def generate_sms_code():
    return str(secrets.randbelow(1000000)).zfill(6)


class User(AbstractUser):
    ROLE_CHOICES = (
        ('S', 'Senior'),
        ('J', 'Junior'),
        ('A', 'Admin'),
    )
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        # ('O', 'Other'),
    )
    name = models.CharField(max_length=100)
    birth = models.DateField(null=True)
    phone = models.CharField(max_length=20, null=True)
    career = models.CharField(max_length=100, null=True)
    category = models.JSONField(default=list, null=True)
    role = models.CharField(max_length=100, null=True, choices=ROLE_CHOICES)
    gender = models.CharField(max_length=10, null=True, choices=GENDER_CHOICES)
    credit = models.SmallIntegerField(default=5)

    def save(self, *args, **kwargs):
        if self.birth:
            if (self.birth.year - timezone.now().date().year) > 60:
                self.role = 'S'
            else:
                self.role = 'J'
        super().save(*args, **kwargs)


class CreditHistory(TimeStampedModel):
    credited_user = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True, related_name="credited_user")
    deducted_user = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True, related_name="deducted_user")
    credit = models.PositiveSmallIntegerField(default=0)
    reason = models.CharField(max_length=100, null=True)
    appointment = models.ForeignKey(
        "appointment.Appointment", on_delete=models.PROTECT, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.credited_user:
                self.credited_user.credit += self.credit
                self.credited_user.save()
            if self.deducted_user:
                self.deducted_user.credit -= self.credit
                self.deducted_user.save()
        super().save(*args, **kwargs)


class SmsAuthCode(TimeStampedModel):
    phone = models.CharField(max_length=20, unique=True)
    code = models.CharField(max_length=6, default=generate_sms_code)

    def __str__(self):
        return f"{self.phone} - {self.code}"

    def clean(self):
        self.phone = self.phone.replace("-", "").replace(" ", "")
        if not self.phone.startswith("010") or len(self.phone) != 11 or not self.phone.isdigit():
            raise ValidationError("Invalid phone number")

    def validate_code(self, code):
        return self.code == code

    def send_sms(self):
        send_sms(self.phone, f"인증번호는 {self.code}입니다.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


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
