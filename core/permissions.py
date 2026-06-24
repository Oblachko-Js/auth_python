from rest_framework.response import Response
from rest_framework import status
from access.models import Role, BusinessElement, AccessRule
from functools import wraps


def require_auth(view_func):
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        if not request.user:
            return Response({'error': 'Не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)
        return view_func(self, request, *args, **kwargs)
    return wrapper


def require_permission(element_name, permission):
    """
    element_name: str — name from BusinessElement
    permission: one of read, read_all, create, update, update_all, delete, delete_all
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            if not request.user:
                return Response({'error': 'Не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)
            if not has_permission(request.user, element_name, permission):
                return Response({'error': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)
            return view_func(self, request, *args, **kwargs)
        return wrapper
    return decorator


def has_permission(user, element_name, permission):
    try:
        role = user.role
        element = BusinessElement.objects.get(name=element_name)
        rule = AccessRule.objects.get(role=role, element=element)
        return getattr(rule, f'{permission}_permission', False)
    except Exception:
        return False
