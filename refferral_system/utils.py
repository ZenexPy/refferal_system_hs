import random
import string
from typing import List
from .models import CustomUserModel


random_chars_list = list(string.ascii_letters+string.digits)


def make_letters() -> List:
    string_chars = "".join(random.choices(random_chars_list, k=6))
    return string_chars


def make_verification_code() -> int:
    random_code = random.randint(1000, 9999)

    return random_code


def create_invite_code() -> str:

    random_string = make_letters()
    while len(CustomUserModel.objects.filter(invite_code=random_string)) != 0:
        random_string = make_letters()
    random_code = random_string

    return random_code


def create_fake_code() -> str:
    f = 5555
    return f
