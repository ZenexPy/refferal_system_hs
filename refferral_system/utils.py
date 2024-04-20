import random
import string
from typing import List


random_chars_list = list(string.ascii_letters+string.digits)


def make_letters() -> List:
    string_chars = "".join(random.choices(random_chars_list, k=7))
    return string_chars
