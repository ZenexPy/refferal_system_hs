import pytest
from django.utils import timezone
import datetime
from rest_framework import status
from rest_framework.test import APIClient
from refferral_system.models import CustomUserModel, Referral


client = APIClient()


@pytest.mark.django_db
def test_register_user():

    payload = dict(
        phone="-79969249541"
    )

    response = client.post("/referral/api/verify-phone/", payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.data
    try:
        user = CustomUserModel.objects.get(phone=payload["phone"])
        assert False
    except CustomUserModel.DoesNotExist:
        assert True

    payload = dict(
        phone="+79969249541222"
    )
    assert "error" in response.data
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Введите правильно номер телефона" in response.data["error"]
    try:
        user = CustomUserModel.objects.get(phone=payload["phone"])
        assert False
    except CustomUserModel.DoesNotExist:
        assert True
    payload = dict(
        phone="asdadasdasdasd"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    payload = dict(
        phone="+71123456782"
    )

    response = client.post("/referral/api/verify-phone/", payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert "Код подтверждения отправлен на ваш номер телефона." in response.data['detail']
    user = CustomUserModel.objects.get(phone=payload["phone"])
    assert user.verification_code is not None
    assert len(user.verification_code) == 4
    assert user.invite_code is None
    assert user.last_try_login is not None
    assert user.last_try_login >= timezone.now() - datetime.timedelta(minutes=1)

    response = client.post("/referral/api/verify-phone/", payload)
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_verification_user():
    payload = dict(phone="+71123456782", verification_code="5555")
    response = client.post("/referral/api/verify-phone/", dict(phone="+71123456782"))
    response = client.post("/referral/api/verify-code/", payload)  # verification_code - fake

    assert response.status_code == status.HTTP_200_OK
    user = CustomUserModel.objects.get(phone=payload["phone"])
    assert user.invite_code is not None
    assert len(user.invite_code) == 6
    assert len(user.verification_code) == 4
    assert "Авторизация успешна" in response.data["message"]
    assert response.data["refresh"] is not None
    assert response.data["access"] is not None

    payload = dict(phone="+71123456782", verification_code="1111")
    response = client.post("/referral/api/verify-code/", payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Неправильный код"
    user = CustomUserModel.objects.get(phone=payload["phone"])
    user.invite_code is None

    payload = dict(phone="+11111111111", verification_code="5555")
    response = client.post("/referral/api/verify-code/", payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["error"] == "Пользователь с указанным номером телефона не найден."


@pytest.mark.django_db
def test_profile_user(user):
    payload = dict(phone="+71123456782", verification_code="5555")
    response = client.post("/referral/api/verify-phone/", dict(phone="+71123456782"))
    response = client.post("/referral/api/verify-code/", payload)

    access = response.data["access"]

    headers = {'Authorization': f'Bearer {access}'}

    response = client.get("/referral/api/profile/", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["my_code"] is None
    assert len(response.data["referrals"]) == 0

    data_dict = dict(invite_code=user.invite_code)

    response = client.post("/referral/api/profile/", data_dict, headers=headers)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["success"] == "Реферрал успешно создан"

    response = client.post("/referral/api/profile/", data_dict, headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["message"] == "Вы уже вводили код реферала"

    response = client.post("/referral/api/verify-code/", dict(phone=user.phone,
                           verification_code=user.verification_code))
    response = client.post("/referral/api/verify-code/", dict(phone=user.phone,
                           verification_code=user.verification_code))  # для обновления истекшего кода
    access = response.data["access"]
    headers = {'Authorization': f'Bearer {access}'}
    response = client.get("/referral/api/profile/", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["my_code"] is None
    assert len(response.data["referrals"]) == 1

    response = client.post("/referral/api/profile/", dict(invite_code=user.invite_code), headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["message"] == "Нельзя использовать свой же код реферала"
    assert len(Referral.objects.filter(refferals_id=user.id)) == 0
