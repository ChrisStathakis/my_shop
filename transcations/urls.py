from django.urls import path, include
from .views import *
from .ajax_views import *

app_name = 'billings'

urlpatterns = [
    path('homepage/', homepage, name='homepage'),

    path('bill-page/', bills_list_view, name='bill_list'),
    path('payroll-page/', payroll_list_view, name='payroll_list'),
    path('expenses-page/', expenses_list_view, name='expenses_list'),
    path('edit-page/<slug:mymodel>/<int:pk>/<slug:slug>/', edit_page, name='edit_page'),
    path('bill-page/save-as/<int:pk>/<slug:slug>/', save_as_view, name ='save_as_view'),

    #ajax
    path('ajax/popup/bill-category/', create_bill_category_popup, name='ajax_bill_cat_popup'),
    path('ajax/popup/payroll-person/', create_person_popup, name='ajax_payroll_person_popup'),
    path('ajax/popup/occupation/', create_occup_popup, name='ajax_occup_popup'),
    path('ajax/popup/expenses-category/', create_generic_category_popup, name='ajax_generic_cate_popup'),

    #settings
    path('settings/person-list/', PersonListView.as_view(), name='person_list'),
    path('settings/person-detail/<int:pk>/', PersonDetailView.as_view(), name='person_detail'),

    path('settings/occup-list/', OccupationListView.as_view(), name='occup_list'),
    path('settings/occup-detail/<int:pk>/', OccupationDetailView.as_view(), name='occup_detail'),

    path('settings/bills-category-list/', BillCategoryListView.as_view(), name='bill_cate_list'),
    path('settings/occup-detail/<int:pk>/', BillCategoryDetailView.as_view(), name='bill_cate_detail'),

    path('settings/expenses-list/', GenericExpenseCategoryListView.as_view(), name='expense_cate_list'),
    path('settings/occup-detail/<int:pk>/', GenericExpenseCategoryDetailView.as_view(), name='expense_cate_detail'),
   
]