from django.urls import path, include

urlpatterns = [
    path('api/auth/', include('users.urls')),
    path('api/access/', include('access.urls')),
    path('api/business/', include('business.urls')),
]
