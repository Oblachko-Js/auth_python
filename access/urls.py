from django.urls import path
from .views import (
    RoleListView, RoleDetailView,
    ElementListView,
    AccessRuleListView, AccessRuleDetailView,
    AssignRoleView,
)

urlpatterns = [
    path('roles/', RoleListView.as_view()),
    path('roles/<int:pk>/', RoleDetailView.as_view()),
    path('elements/', ElementListView.as_view()),
    path('rules/', AccessRuleListView.as_view()),
    path('rules/<int:pk>/', AccessRuleDetailView.as_view()),
    path('users/<int:user_id>/assign-role/', AssignRoleView.as_view()),
]
