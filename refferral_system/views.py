from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .serializers import CreateUserSerializer, VerificationSerializer
from .models import CustomUser
from .utils import make_verification_code, create_invite_code, create_fake_code
import time
import datetime


class PhoneVerificationView(APIView):
    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)

        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            verification_code = create_fake_code()
            last_try_login = timezone.now()
            created_at = timezone.now()
            time.sleep(2)
            try:
                user = CustomUser.objects.get(phone=phone)
                user.verification_code = verification_code
                user.last_try_login = last_try_login
                user.save()
            except CustomUser.DoesNotExist:
                user = CustomUser.objects.create(
                    phone=phone,
                    verification_code=verification_code,
                    last_try_login=last_try_login,
                    created_at=created_at
                )
            return Response({"detail": "Код подтверждения отправлен на ваш номер телефона."},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CodeVerificationView(APIView):
    def post(self, request):
        serializer = VerificationSerializer(data=request.data)

        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            verification_code = serializer.validated_data['verification_code']
            try:
                user = CustomUser.objects.get(phone=phone)
                if verification_code != user.verification_code:
                    return Response({"error": "Неправильный код"},
                                    status=status.HTTP_400_BAD_REQUEST)
                if timezone.now() - user.last_try_login > datetime.timedelta(minutes=5):
                    time.sleep(2)
                    return Response({"message": "Код истек, новый код уже выслан"},
                                    status=status.HTTP_400_BAD_REQUEST)
                if user.invite_code is None:
                    user.invite_code = create_invite_code()
                    user.save()
                # Авторизация
                return Response({"message": "Авторизация успешна."}, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({"error": "Пользователь с указанным номером телефона не найден."},
                                status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
