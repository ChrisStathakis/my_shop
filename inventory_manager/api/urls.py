from django.urls import path
from .views import (ApiWarehouseOrderListView, ApiWarehouseOrderItemListView,
                    ApiWarehouseOrderDetailView, ApiWarehouseOrderItemDetailView,
                    api_warehouse_homepage)


app_name = 'api_inventory'

urlpatterns = [
    path('warehouse/homepage', api_warehouse_homepage, name='api_warehouse_homepage'),
    path('warehouse/orders/', ApiWarehouseOrderListView.as_view(), name='warehouse_order_list'),
    path('warehouse/order-items/', ApiWarehouseOrderItemListView.as_view(), name='warehouse_order_item_list'),
    path('warehouse/order/<int:pk>/', ApiWarehouseOrderDetailView.as_view(), name='warehouse_order_detail'),
    path('warehouse/order-items/<int:pk>', ApiWarehouseOrderItemDetailView.as_view(), name='warehouse_order_item_detail')
]