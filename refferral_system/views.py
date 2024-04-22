from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .serializers import CreateUserSerializer, VerificationSerializer, InviteCodeSerializer
from .models import CustomUserModel, Referral
from .utils import make_verification_code, create_invite_code, create_fake_code
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
import time
import datetime
from drf_yasg.utils import swagger_auto_schema


class PhoneVerificationView(APIView):
    """

    Ожидаемые параметры запроса:
    - phone: Строка, номер телефона пользователя для подтверждения.
    """
    @swagger_auto_schema(request_body=CreateUserSerializer, responses={
        status.HTTP_201_CREATED: "Пользователь успешно создан",
        status.HTTP_400_BAD_REQUEST: "Некорректные данные запроса",
        status.HTTP_400_BAD_REQUEST: "Введите правильно номер телефона"
    })
    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)

        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            verification_code = create_fake_code()
            last_try_login = timezone.now()
            created_at = timezone.now()
            time.sleep(2)
            try:
                user = CustomUserModel.objects.get(phone=phone)
                user.verification_code = verification_code
                user.last_try_login = last_try_login
                user.save()
            except CustomUserModel.DoesNotExist:
                user = CustomUserModel.objects.create(
                    phone=phone,
                    verification_code=verification_code,
                    last_try_login=last_try_login,
                    created_at=created_at
                )
            return Response({"detail": "Код подтверждения отправлен на ваш номер телефона."},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CodeVerificationView(APIView):
    """

    Ожидаемые параметры запроса:
    - phone: Строка, номер телефона пользователя для подтверждения.
    - verification_code: 4-значный код, для верификации.
    """
    @swagger_auto_schema(request_body=VerificationSerializer, responses={
        status.HTTP_200_OK: "Успешная авторизация",
        status.HTTP_400_BAD_REQUEST: "Некорректные данные запроса или другие ошибки",
        status.HTTP_404_NOT_FOUND: "Пользователь с указанным номером телефона не найден"
    })
    def post(self, request):
        serializer = VerificationSerializer(data=request.data)

        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            verification_code = serializer.validated_data['verification_code']
            try:
                user = CustomUserModel.objects.get(phone=phone)
                if verification_code != user.verification_code:
                    return Response({"error": "Неправильный код"},
                                    status=status.HTTP_400_BAD_REQUEST)
                if timezone.now() - user.last_try_login > datetime.timedelta(minutes=5):
                    time.sleep(2)
                    user.verification_code = create_fake_code()
                    user.last_try_login = timezone.now()
                    user.save()
                    return Response({"message": "Код истек, новый код уже выслан"},
                                    status=status.HTTP_400_BAD_REQUEST)
                if user.invite_code is None:
                    user.invite_code = create_invite_code()
                    user.save()
                try:
                    refresh = RefreshToken.for_user(user)
                    return Response({"message": "Авторизация успешна", "refresh": str(refresh),
                                     "access": str(refresh.access_token)},
                                    status=status.HTTP_200_OK)
                except TokenError as e:
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except CustomUserModel.DoesNotExist:
                return Response({"error": "Пользователь с указанным номером телефона не найден."},
                                status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=InviteCodeSerializer,
                         responses={status.HTTP_201_CREATED:
                                    "Реферрал успешно создан",
                                    status.HTTP_400_BAD_REQUEST:
                                    "Некорректные данные запроса или ошибка при проверке",
                                    status.HTTP_404_NOT_FOUND:
                                    "Реферальный код не найден"})
    def post(self, request):
        serializer = InviteCodeSerializer(data=request.data)

        if serializer.is_valid():

            user = request.user
            invite_code = serializer.validated_data['invite_code']
            if Referral.objects.filter(refferals_id=user.id).exists():
                return Response({"message": "Вы уже вводили код реферала"},
                                status=status.HTTP_400_BAD_REQUEST)
            if invite_code == user.invite_code:
                return Response({"message": "Нельзя использовать свой же код реферала"},
                                status=status.HTTP_400_BAD_REQUEST)
            try:
                referred_by = CustomUserModel.objects.get(invite_code=invite_code)
            except CustomUserModel.DoesNotExist:
                return Response({"error": "Неправильный реферальный код"},
                                status=status.HTTP_404_NOT_FOUND)
            Referral.objects.create(refferals=user, reffered_by=referred_by)

            return Response({"success": "Реферрал успешно создан"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        user = request.user
        response_data = {}
        try:
            referral_by = Referral.objects.get(refferals_id=user.id)
            reffered_by_id = referral_by.reffered_by_id
            ref_user = get_object_or_404(CustomUserModel, id=reffered_by_id)
            response_data["code_used"] = ref_user.invite_code
        except Referral.DoesNotExist:
            response_data["code_used"] = None

        my_refferals = Referral.objects.filter(reffered_by_id=user.id).values_list('refferals_id', flat=True)
        users_phones = CustomUserModel.objects.filter(id__in=my_refferals).values_list('phone', flat=True)
        response_data["referrals"] = users_phones
        response_data["my_refcode"] = user.invite_code

        return Response(response_data, status=status.HTTP_200_OK)
