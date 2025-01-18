# Generated by Django 5.1.4 on 2025-01-18 15:06

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('place', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('PENDING', '대기중'), ('ACCEPTED', '수락됨'), ('REJECTED', '거절됨'), ('CANCELED', '취소됨'), ('COMPLETED', '완료')], max_length=100)),
                ('origin_text', models.TextField(null=True)),
                ('summary', models.TextField(null=True)),
                ('mentee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appointment_as_mentee', to=settings.AUTH_USER_MODEL)),
                ('mentor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appointment_as_mentor', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'appointment',
            },
        ),
    ]
