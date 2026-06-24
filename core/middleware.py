import jwt
from django.conf import settings
from django.http import JsonResponse
from users.models import User


class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = None
        token = self._extract_token(request)
        if token:
            user = self._authenticate(token)
            if user:
                request.user = user
        return self.get_response(request)

    def _extract_token(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header:
            auth_header = request.META.get('AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        return None

    def _authenticate(self, token):
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'], is_active=True)
            return user
        except Exception:
            return None
