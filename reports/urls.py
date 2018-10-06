from django.conf.urls import url
from django.urls import path
from .views import *
from .views_transcations import *
from .ajax_calls.ajax_warehouse_calls import *
from .view_sells import OrderRetailReportView, HomepageSellView
from .balance_sheet_views import balance_sheet


app_name = 'reports'

urlpatterns = [
    url(r'^$', HomepageReport.as_view(), name='homepage'),
    path('homepage/product-warning/', HomepageProductWarning.as_view(), name='product_warning'),

    # warehouse
    path('products/', ReportProducts.as_view(), name='products'),
    path('characteristic-analysis/', ProductSizeView.as_view(), name='products_size'),
    path('warehouse/products/ajax-analysis', view=ajax_products_analysis, name='ajax_products_analysis'),
    path('products/ajax-search/', view=ajax_product_search, name='ajax_product_search'),

    path('products/<int:pk>/', ProductDetail.as_view(), name='products_detail'),
    path('product/<int:pk>/ajax_analysis', view=ajax_product_detail, name='ajax_product_analysis'),

    path('brands/', BrandsPage.as_view(), name='brands'),
    path('brands/detail/<int:pk>/', BrandDetailView.as_view(), name='brands_detail'),

    path('vendors/', VendorsPage.as_view(), name='vendors'),
    path('vendors/ajax_analysis', view=ajax_vendors_page_analysis, name='ajax_vendors_page_analysis'),
    path('vendors/check-orders/', CheckOrderPage.as_view(), name='check_orders'),
    url(r'vendors/(?P<pk>\d+)/$', VendorDetailReportView.as_view(), name='vendor_detail'),

    path('warehouse-categories/', WarehouseCategoriesView.as_view(), name='warehouse_categories'),
    path('warehouse-categories/detail/<int:pk>/', WarehouseCategoryView.as_view(), name='warehouse_category'),
    path('warehouse-categories/ajax/', ajax_warehouse_category_analysis, name='ajax_ware_cate_ana'),
    # path('warehouse-category/<int:pk>', WarehouseCategoryReport.as_view(), name='warehouse_category_detail'),

    path('site-categories/', CategoriesSiteView.as_view(), name='site_categories'),
    # path('site-category/<int:pk>', WarehouseCategoryReport.as_view(), name='site_category_detail'),

    
    # transcations
    path('transcations/', transcations_homepage, name='transcation_homepage'),
    path('transcations/bill-list/', BillsReportView.as_view(), name='bills_report_view'),
    path('transcations/payroll-list/', PayrollReportView.as_view(), name='payroll_report_view'),
    path('transcations/expenses-list/', GenericExpenseView.as_view(), name='generic_expenses_view'),

    # buys
    path('orders/', WarehouseOrderView.as_view(), name='warehouse_orders'),
    path('orders/<int:pk>/', WarehouseDetailView.as_view(), name='warehouse_order_detail'),
    path('warehouse-products-flow/', OrderItemFlowView.as_view(), name='order_items_flow'),

    # sells
    path('report-sales/', HomepageSellView.as_view(), name='homepage_sales'),
    path('report-sales/detail/<int:pk>/', OrderRetailReportView.as_view(), name='retail_order_detail'),

    # ajax_calls
    path('ajax/characteristics/analysis', ajax_size_analysis, name='ajax_size_analysis'),

    path('balance-sheet/', balance_sheet, name='balance\-sheet'),

   
    ]

'''
#  outcomes_ajax_calls
    path('warehouse/products/ajax-analysis', view=ajax_products_analysis, name='ajax_products_analysis'),
    path('products/ajax-search/', view=ajax_product_search, name='ajax_product_search'),
    path('product/<int:pk>/ajax_analysis', view=ajax_product_detail, name='ajax_product_analysis'),
    path('vendors/ajax_analysis', view=ajax_vendors_page_analysis, name='ajax_vendors_page_analysis'),
    path('warehouse-orders/analyse/', view=ajax_analyse_vendors, name='ajax_analyse_vendors'),
    path('warehouse/products-flow/analysis/', view=ajax_warehouse_product_movement_vendor_analysis, name='ware_pro_flow_analysis'),
    path('warehouse/ajax-outcome/', view=ajax_outcomes, name='ajax_outcomes'),
    path('incomes/store-analysis/', view=ajax_incomes_per_store, name='ajax_incomes_store_analysis'),
    path('incomes/payment-analysis/', view=ajax_retail_orders_payment_analysis, name='ajax_payment_analysis'),
    path('balance-sheet/ajax/warehouse-orders', view=ajax_balance_sheet_warehouse_orders, name='ajax_balance_sheet_ware_orders'),
    path('balance-sheet/ajax/payroll', view=ajax_balance_sheet_payroll, name='ajax_balance_sheet_payroll'),
'''
