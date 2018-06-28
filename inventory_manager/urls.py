from django.urls import path, include, re_path
from .views import *

app_name = 'inventory'

urlpatterns = [
    path('home/', view=WareHouseOrderPage.as_view(), name='warehouse_home'),
    path('create-order/', view=create_new_warehouse_order, name='warehouse_create_order'),
    path('order/quick-vendor/', view=quick_vendor_create, name='warehouse_quick_vendor'),
    path('order/<int:dk>/', view=warehouse_order_detail, name='warehouse_order_detail'),
    path('order/add-item/<int:dk>/<int:pk>/', view=warehouse_add_order_item, name='add_order_item'),
    path('order/add-item/<int:dk>/edit/', view=edit_order_item, name='edit_order_item'),
    path('order/add-item/<int:dk>/delete/', view=delete_order_item, name='delete_order_item'),

    path('vendor-list/',  VendorPageList.as_view(), name='vendor_list'),
    path('vendor-detail/<int:pk>/', VendorPageDetail.as_view(), name='vendor_detail'),
    path('vendor-list/create/', VendorPageCreate.as_view(), name='vendor_create'), 
    path('vendor/create-check/<int:pk>/', WarehousePaymentOrderCreate.as_view(), name='create_check'),
    path('vendor/details/check-order-edit/<int:pk>/', view= edit_check_order, name='edit_check'),
    path('vendor/check/delete/<int:dk>/', view=delete_check_order, name='delete_check'),
    path('vendor/check-order/paid/<int:pk>/', view=check_order_paid , name='paid_check'),
    path('vendor-detail/convert-order/<int:dk>/<int:pk>/', view=warehouse_check_order_convert, name='order_convert'),

    path('payment/list/', WarehousePaymentPage.as_view(), name='payment_list'),
    path('payment/paid/<int:pk>/', view=warehouse_order_paid, name='ware_order_paid'),
    path('payment/detail/<int:pk>/', view=warehouser_order_paid_detail, name='ware_order_paid_detail'),
    path('payment/detail/edit-payment/<int:dk>/<int:pk>/', view=warehouse_edit_paid_order, name='ware_order_paid_edit'),
    path('payment/detail/delete-payment/<int:pk>/', view=warehouse_order_paid_delete, name='ware_order_paid_delete'),

    
]