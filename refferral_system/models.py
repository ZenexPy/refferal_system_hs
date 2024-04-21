from django.db import models


class CustomUser(models.Model):

    """
    Model for user in api

    """
    phone = models.CharField(max_length=12, unique=True)
    verification_code = models.CharField(max_length=4, null=True)
    invite_code = models.CharField(max_length=6, unique=True, null=True)
    created_at = models.DateTimeField(null=True)
    last_try_login = models.DateTimeField(null=True)


class Referral(models.Model):

    refferals = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,
                                  related_name='my_refferals')

    reffered_by = models.OneToOneField(CustomUser, on_delete=models.SET_NULL, null=True,
                                       related_name='was_reffered')
