# Generated by Django 4.2.10 on 2024-04-21 02:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=12, unique=True)),
                ('verification_code', models.CharField(max_length=4, null=True)),
                ('invite_code', models.CharField(max_length=6, null=True, unique=True)),
                ('created_at', models.DateTimeField(null=True)),
                ('last_try_login', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('refferals', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='my_refferals', to='refferral_system.customuser')),
                ('reffered_by', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='was_reffered', to='refferral_system.customuser')),
            ],
        ),
    ]
