from django.urls import path, include
from .views import *


app_name = 'billings'

urlpatterns = [
   path('homepage/', homepage, name='homepage'),
   path('bill-page/', BillListView.as_view(), name='bill_list'),
]