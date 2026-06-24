import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import User
from .serializers import RegisterSerializer, UpdateUserSerializer, UserProfileSerializer
from access.models import Role
from core.permissions import require_auth


def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.now(tz=timezone.utc) + timedelta(hours=settings.JWT_EXPIRY_HOURS),
        'iat': datetime.now(tz=timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        password_hash = bcrypt.hashpw(
            data['password'].encode('utf-8'), bcrypt.gensalt()
        ).decode('utf-8')

        default_role = Role.objects.filter(name='user').first()

        user = User.objects.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            patronymic=data.get('patronymic', ''),
            email=data['email'],
            password_hash=password_hash,
            role=default_role,
        )
        token = generate_token(user.id)
        return Response({
            'message': 'Регистрация успешна',
            'token': token,
            'user': UserProfileSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email', '').lower()
        password = request.data.get('password', '')

        if not email or not password:
            return Response({'error': 'Укажите email и пароль'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Неверный email или пароль'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({'error': 'Аккаунт деактивирован'}, status=status.HTTP_401_UNAUTHORIZED)

        if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return Response({'error': 'Неверный email или пароль'}, status=status.HTTP_401_UNAUTHORIZED)

        token = generate_token(user.id)
        return Response({
            'message': 'Вход выполнен',
            'token': token,
            'user': UserProfileSerializer(user).data,
        })


class LogoutView(APIView):
    @require_auth
    def post(self, request):
        # Stateless JWT — на клиенте нужно удалить токен.
        # При необходимости можно хранить blacklist токенов в Redis/БД.
        return Response({'message': 'Выход выполнен. Удалите токен на клиенте.'})


class ProfileView(APIView):
    @require_auth
    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)

    @require_auth
    def patch(self, request):
        serializer = UpdateUserSerializer(data=request.data, context={'user': request.user})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        user = request.user

        for field in ['first_name', 'last_name', 'patronymic', 'email']:
            if field in data:
                setattr(user, field, data[field])

        if 'password' in data:
            user.password_hash = bcrypt.hashpw(
                data['password'].encode('utf-8'), bcrypt.gensalt()
            ).decode('utf-8')

        user.save()
        return Response({'message': 'Профиль обновлён', 'user': UserProfileSerializer(user).data})

    @require_auth
    def delete(self, request):
        # Мягкое удаление
        user = request.user
        user.is_active = False
        user.save()
        return Response({'message': 'Аккаунт деактивирован'})
