from django.conf.urls import url
from .views import *
from django.urls import path
from .api.views import RetailOrderListApi
from .ajax_views import ajax_products_search, ajax_edit_order_item, ajax_add_product
app_name = 'POS'

urlpatterns = [
    path('', HomePage.as_view(), name='homepage'),
    path('create-sale/', view=create_new_sales_order, name='create_sale'),
    path('sales/<int:pk>/', view=sales, name='sales'),
    path('sales/action/<int:pk>/<int:qty>/<slug:type>/', edit_product_item_view, name='edit_product_item'),
    path('sales/retail-order/done/<int:pk>/', retail_order_done, name='retail_order_done'),

    path('sales/<int:pk>/pay-order/', view=order_paid, name='order_paid'),
    path('sales/delete-payment/<int:dk>/<int:pk>/', view=delete_payment_order, name='delete_payment_order'),
    path('sales/delete-order/<int:dk>/', view=delete_order_view, name='delete_order'),

    #actions
    path('sales/add/<int:dk>/<int:pk>/<int:qty>/', view=add_product_to_order_, name='add_to_order'),

    # return url
    path('create-return/', view=create_return_order, name='create_return_sale'),

    # ajax calls
    path('ajax/sales/search/<int:pk>/', view=ajax_products_search, name='ajax_products_search'),
    path('ajax/sales/edit-order/<int:pk>/<int:qty>/<slug:action>/', ajax_edit_order_item, name='ajax_edit_order_item'),
    path('ajax/sales/<int:pk>/<int:dk>/add', view=ajax_add_product, name='ajax_add_products'),


    # create costumer
    url(r'^author/create', AuthorCreatePopup, name="AuthorCreate"),
    url(r'^author/(?P<pk>\d+)/edit', AuthorEditPopup, name="AuthorEdit"),
    url(r'^author/ajax/get_author_id', get_author_id, name="get_author_id"),

    # create payment
    url(r'^payment/(?P<pk>\d+)/create/', ajax_payment_add, name="PaymentCreate"),
    url(r'^payment/(?P<pk>\d+)/edit', AuthorEditPopup, name="AuthorEdit"),
    url(r'^payment/ajax/get_author_id', get_author_id, name="get_author_id"),

    ]
