from django.urls import path
from .views import (BillCategoryListApiView, BillListApiView,
                    BillCategoryDetailApiView, BillDetailApiView,
                    transaction_homepage)

urlpatterns = [
    path('', transaction_homepage, name='api_homepage_transcation'),
    path('bill-category-list/', BillCategoryListApiView.as_view(), name='api_bill_category_list'),
    path('bill-list/', BillListApiView.as_view(), name='api_bill_list'),
    path('bill-category-detail/<int:pk>/', BillCategoryDetailApiView.as_view(), name='api_bill_category_detail'),
    path('bill-detail/<int:pk>/', BillDetailApiView.as_view(), name='api_bill_detail')
    ]