from django.db import models
from django.contrib.auth.models import AbstractUser
from .utils import make_letters


class CustomUser(AbstractUser):

    """
    Model for user in api

    """
    phone = models.CharField(max_length=12, unique=True)
    verification_code = models.CharField(max_length=4)

    USERNAME_FIELD = ('phone')
    REQUIRED_FIELDS = []


class InviteCode(models.Model):

    """
    Model for invite code in api

    """

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    invite_code = models.CharField(max_length=6, unique=True)

    def create_code(self) -> str:

        random_string = make_letters()
        while len(InviteCode.objects.filter(invite_code=random_string)) != 0:
            random_string = make_letters()
        random_code = random_string

        return random_code

    def save(self, *args, **kwargs):
        self.invite_code = self.create_code()

        return super(InviteCode, self).save(*args, **kwargs)


class Referral(models.Model):

    refferals = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,
                                  related_name='my_refferals')

    reffered_by = models.OneToOneField(CustomUser, on_delete=models.SET_NULL, null=True,
                                       related_name='was_reffered')
