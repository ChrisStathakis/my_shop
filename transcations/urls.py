from django.urls import path, include
from .views import *
from .ajax_views import *

app_name = 'billings'

urlpatterns = [
   path('homepage/', homepage, name='homepage'),
   path('bill-page/', bills_list_view, name='bill_list'),
   path('bill-page/edit/<int:pk>/<slug:slug>/', edit_bill, name='edit_bill'),
   #ajax
   path('ajax/popup/bill-category/', create_bill_category_popup, name='ajax_bill_cat_popup'),
   
]