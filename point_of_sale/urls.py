from .views import *
from django.urls import path
from .ajax_views import ajax_products_search, ajax_edit_order_item, ajax_add_product, ajax_barcode_add
app_name = 'POS'

urlpatterns = [
    path('', HomePage.as_view(), name='homepage'),
    path('create-sale/', view=create_new_sales_order, name='create_sale'),
    path('sales/<int:pk>/', view=sales, name='sales'),
    path('sales/delete/order/<int:pk>/', cancel_or_delete_order, name='delete_order'),
    path('sales/retail_order_done/<int:pk>/', retail_order_done, name='retail_order_done'),
    path('sales/retail-unlock/<int:pk>/', retail_order_unlock, name='retail_unlock'),

    path('return-order/<int:pk>/', create_order_return_from_order_view, name='return_order_from_retail'),

    # return url
    path('homepage_return/', HomepageRetailReturnOrder.as_view(), name='homepage_return'),

    # ajax calls
    path('ajax/sales/search/<int:pk>/', view=ajax_products_search, name='ajax_products_search'),
    path('ajax/sales/edit-order/<int:pk>/<int:qty>/<slug:action>/', ajax_edit_order_item, name='ajax_edit_order_item'),
    path('ajax/sales/<int:pk>/<int:dk>/add', view=ajax_add_product, name='ajax_add_products'),
    path('ajax/sales/barcode/<int:pk>/add', ajax_barcode_add, name='ajax_barcode'),




    ]
