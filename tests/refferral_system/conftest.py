import pytest
from refferral_system.models import CustomUserModel


@pytest.fixture
def user() -> CustomUserModel:

    user = CustomUserModel.objects.create(
        phone="+71123456770",
        verification_code="5555",
        invite_code="WvKBH1",
        created_at="2024-04-21 08:40:14.37448+00",
        last_try_login="2024-04-21 19:55:46.146441+00")

    return user
