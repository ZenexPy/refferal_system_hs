from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class CustomUserModel(AbstractBaseUser):

    """
    Model for user in api

    """

    phone = models.CharField(max_length=12, unique=True)
    verification_code = models.CharField(max_length=4, null=True)
    invite_code = models.CharField(max_length=6, unique=True, null=True)
    created_at = models.DateTimeField(null=True)
    last_try_login = models.DateTimeField(null=True)

    USERNAME_FIELD = 'phone'


class Referral(models.Model):

    refferals = models.ForeignKey(CustomUserModel, on_delete=models.SET_NULL, null=True,
                                  related_name='my_refferals')

    reffered_by = models.ForeignKey(CustomUserModel, on_delete=models.SET_NULL, null=True,
                                    related_name='was_reffered')
