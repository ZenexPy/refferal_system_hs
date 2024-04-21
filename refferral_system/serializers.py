from rest_framework import serializers

import re


class BaseUserSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=12)

    def validate(self, data):
        phone = data['phone']
        unknown = set(self.initial_data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError({"error": "Введены лишние данные"})

        if not re.match(r'\+\d{11}$', phone):
            raise serializers.ValidationError({"error": "Введите правильно номер телефона"})
        return data


class CreateUserSerializer(BaseUserSerializer):
    pass


class VerificationSerializer(BaseUserSerializer):
    verification_code = serializers.CharField(max_length=4)


class InviteCodeSerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=6)

    def validate(self, data):
        unknown = set(self.initial_data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError({"error": "Введены лишние данные"})

        return data
