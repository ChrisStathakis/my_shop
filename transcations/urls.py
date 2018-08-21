from django.urls import path, include
from .views import *
from .ajax_views import *

app_name = 'billings'

urlpatterns = [
    path('homepage/', homepage, name='homepage'),

    path('bill-page/', bills_list_view, name='bill_list'),
    path('bill-page/edit/<int:pk>/<slug:slug>/', edit_bill, name='edit_bill'),
    path('bill-page/edit/actions/<int:pk>/<slug:slug>/', edit_bills_actions, name='edit_bill_actions'),

    path('payroll-page/', payroll_list_view, name='payroll_list'),
    path('payroll-page/edit/<int:pk>/<slug:slug>/', edit_payroll, name='edit_payroll'),
    #ajax
    path('ajax/popup/bill-category/', create_bill_category_popup, name='ajax_bill_cat_popup'),
    path('ajax/popup/payroll-person/', create_person_popup, name='ajax_payroll_person_popup'),
   
]