from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Role, BusinessElement, AccessRule
from .serializers import (
    RoleSerializer, BusinessElementSerializer,
    AccessRuleSerializer, AccessRuleUpdateSerializer,
)
from core.permissions import require_auth, require_permission


def is_admin(user):
    return user and user.role and user.role.name == 'admin'


def admin_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        if not request.user:
            return Response({'error': 'Не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)
        if not is_admin(request.user):
            return Response({'error': 'Доступ запрещён. Требуется роль администратора.'}, status=status.HTTP_403_FORBIDDEN)
        return view_func(self, request, *args, **kwargs)
    return wrapper


# --- Roles ---

class RoleListView(APIView):
    @admin_required
    def get(self, request):
        roles = Role.objects.all()
        return Response(RoleSerializer(roles, many=True).data)

    @admin_required
    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        role = serializer.save()
        return Response(RoleSerializer(role).data, status=status.HTTP_201_CREATED)


class RoleDetailView(APIView):
    def _get_role(self, pk):
        try:
            return Role.objects.get(pk=pk)
        except Role.DoesNotExist:
            return None

    @admin_required
    def get(self, request, pk):
        role = self._get_role(pk)
        if not role:
            return Response({'error': 'Роль не найдена'}, status=404)
        return Response(RoleSerializer(role).data)

    @admin_required
    def patch(self, request, pk):
        role = self._get_role(pk)
        if not role:
            return Response({'error': 'Роль не найдена'}, status=404)
        serializer = RoleSerializer(role, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        role = serializer.save()
        return Response(RoleSerializer(role).data)

    @admin_required
    def delete(self, request, pk):
        role = self._get_role(pk)
        if not role:
            return Response({'error': 'Роль не найдена'}, status=404)
        role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- Business Elements ---

class ElementListView(APIView):
    @admin_required
    def get(self, request):
        elements = BusinessElement.objects.all()
        return Response(BusinessElementSerializer(elements, many=True).data)

    @admin_required
    def post(self, request):
        serializer = BusinessElementSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        element = serializer.save()
        return Response(BusinessElementSerializer(element).data, status=201)


# --- Access Rules ---

class AccessRuleListView(APIView):
    @admin_required
    def get(self, request):
        rules = AccessRule.objects.select_related('role', 'element').all()
        return Response(AccessRuleSerializer(rules, many=True).data)

    @admin_required
    def post(self, request):
        serializer = AccessRuleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        rule = serializer.save()
        return Response(AccessRuleSerializer(rule).data, status=201)


class AccessRuleDetailView(APIView):
    def _get_rule(self, pk):
        try:
            return AccessRule.objects.select_related('role', 'element').get(pk=pk)
        except AccessRule.DoesNotExist:
            return None

    @admin_required
    def get(self, request, pk):
        rule = self._get_rule(pk)
        if not rule:
            return Response({'error': 'Правило не найдено'}, status=404)
        return Response(AccessRuleSerializer(rule).data)

    @admin_required
    def patch(self, request, pk):
        rule = self._get_rule(pk)
        if not rule:
            return Response({'error': 'Правило не найдено'}, status=404)
        serializer = AccessRuleUpdateSerializer(rule, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        rule = serializer.save()
        return Response(AccessRuleSerializer(rule).data)

    @admin_required
    def delete(self, request, pk):
        rule = self._get_rule(pk)
        if not rule:
            return Response({'error': 'Правило не найдено'}, status=404)
        rule.delete()
        return Response(status=204)


# --- User Role Assignment (admin only) ---

class AssignRoleView(APIView):
    @admin_required
    def patch(self, request, user_id):
        from users.models import User
        from users.serializers import UserProfileSerializer
        role_id = request.data.get('role_id')
        if not role_id:
            return Response({'error': 'Укажите role_id'}, status=400)
        try:
            user = User.objects.get(pk=user_id)
            role = Role.objects.get(pk=role_id)
        except (User.DoesNotExist, Role.DoesNotExist):
            return Response({'error': 'Пользователь или роль не найдены'}, status=404)
        user.role = role
        user.save()
        return Response({'message': 'Роль назначена', 'user': UserProfileSerializer(user).data})
