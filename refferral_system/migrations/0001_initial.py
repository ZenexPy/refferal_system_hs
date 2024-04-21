# Generated by Django 4.2.10 on 2024-04-21 08:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUserModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('phone', models.CharField(max_length=12, unique=True)),
                ('verification_code', models.CharField(max_length=4, null=True)),
                ('invite_code', models.CharField(max_length=6, null=True, unique=True)),
                ('created_at', models.DateTimeField(null=True)),
                ('last_try_login', models.DateTimeField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('refferals', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='my_refferals', to=settings.AUTH_USER_MODEL)),
                ('reffered_by', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='was_reffered', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
