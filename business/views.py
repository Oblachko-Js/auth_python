"""
Mock-Views для демонстрации бизнес-объектов.
Таблицы в БД не создаются — данные возвращаются «захардкоженными».
Проверка прав выполняется через таблицы ролей/правил.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.permissions import require_auth, has_permission


MOCK_PRODUCTS = [
    {'id': 1, 'name': 'Ноутбук Pro X', 'price': 89990, 'owner_id': 2},
    {'id': 2, 'name': 'Смартфон Ultra', 'price': 49990, 'owner_id': 3},
    {'id': 3, 'name': 'Планшет Lite', 'price': 29990, 'owner_id': 2},
]

MOCK_ORDERS = [
    {'id': 1, 'product_id': 1, 'customer': 'Иванов И.И.', 'status': 'new', 'owner_id': 2},
    {'id': 2, 'product_id': 2, 'customer': 'Петрова А.В.', 'status': 'shipped', 'owner_id': 3},
]

MOCK_SHOPS = [
    {'id': 1, 'name': 'Главный магазин', 'city': 'Москва', 'owner_id': 2},
    {'id': 2, 'name': 'Филиал Север', 'city': 'Санкт-Петербург', 'owner_id': 3},
]


class ProductListView(APIView):
    @require_auth
    def get(self, request):
        if has_permission(request.user, 'products', 'read_all'):
            return Response(MOCK_PRODUCTS)
        if has_permission(request.user, 'products', 'read'):
            own = [p for p in MOCK_PRODUCTS if p['owner_id'] == request.user.id]
            return Response(own)
        return Response({'error': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)

    @require_auth
    def post(self, request):
        if not has_permission(request.user, 'products', 'create'):
            return Response({'error': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)
        new_product = {
            'id': len(MOCK_PRODUCTS) + 1,
            'owner_id': request.user.id,
            **request.data,
        }
        return Response({'message': 'Товар создан (mock)', 'product': new_product}, status=201)


class OrderListView(APIView):
    @require_auth
    def get(self, request):
        if has_permission(request.user, 'orders', 'read_all'):
            return Response(MOCK_ORDERS)
        if has_permission(request.user, 'orders', 'read'):
            own = [o for o in MOCK_ORDERS if o['owner_id'] == request.user.id]
            return Response(own)
        return Response({'error': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)

    @require_auth
    def post(self, request):
        if not has_permission(request.user, 'orders', 'create'):
            return Response({'error': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)
        new_order = {
            'id': len(MOCK_ORDERS) + 1,
            'owner_id': request.user.id,
            **request.data,
        }
        return Response({'message': 'Заказ создан (mock)', 'order': new_order}, status=201)


class ShopListView(APIView):
    @require_auth
    def get(self, request):
        if has_permission(request.user, 'shops', 'read_all'):
            return Response(MOCK_SHOPS)
        if has_permission(request.user, 'shops', 'read'):
            own = [s for s in MOCK_SHOPS if s['owner_id'] == request.user.id]
            return Response(own)
        return Response({'error': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)
