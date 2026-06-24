from django.urls import path
from .views import ProductListView, OrderListView, ShopListView

urlpatterns = [
    path('products/', ProductListView.as_view()),
    path('orders/', OrderListView.as_view()),
    path('shops/', ShopListView.as_view()),
]
