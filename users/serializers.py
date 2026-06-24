from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    patronymic = serializers.CharField(max_length=100, required=False, default='')
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email уже используется')
        return value.lower()

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Пароли не совпадают'})
        return data


class UpdateUserSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    patronymic = serializers.CharField(max_length=100, required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(min_length=6, required=False, write_only=True)

    def validate_email(self, value):
        user = self.context.get('user')
        qs = User.objects.filter(email=value.lower())
        if user:
            qs = qs.exclude(id=user.id)
        if qs.exists():
            raise serializers.ValidationError('Email уже используется')
        return value.lower()


class UserProfileSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'patronymic', 'email', 'role_name', 'created_at']
