from django.conf.urls import url
from django.urls import path
from .views import *
from .views_transcations import *
from .ajax_calls.ajax_warehouse_calls import *
from .ajax_calls.ajax_sells_calls import ajax_sells_analysis
from .view_sells import OrderRetailReportView, HomepageSellView
from .viewa_cvs_pdf import product_csv_view
from .balance_sheet_views import balance_sheet, CachFlowReportView


app_name = 'reports'

urlpatterns = [
    url(r'^$', HomepageReport.as_view(), name='homepage'),
    path('homepage/product-warning/', HomepageProductWarning.as_view(), name='product_warning'),
    path('warning-billing-view/', WarningBillingView.as_view(), name='billing_warning'),

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
    path('general-image/', GenericReportView.as_view(), name='general_image'),

    path('transcations/bill-detail/<int:pk>/', BillCategoryDetailView.as_view(), name="bill_category"),

    # buys
    path('orders/', WarehouseOrderView.as_view(), name='warehouse_orders'),
    path('orders/<int:pk>/', WarehouseDetailView.as_view(), name='warehouse_order_detail'),
    path('warehouse-products-flow/', OrderItemFlowView.as_view(), name='order_items_flow'),

    # sells
    path('report-sales/', HomepageSellView.as_view(), name='homepage_sales'),
    path('report-sales/detail/<int:pk>/', OrderRetailReportView.as_view(), name='retail_order_detail'),

    # ajax_calls
    path('ajax/characteristics/analysis', ajax_size_analysis, name='ajax_size_analysis'),

    path('ajax/retail-sells/sell-points/', ajax_sells_analysis, name='ajax_sells_analysis'),

    path('balance-sheet/', balance_sheet, name='balance_sheet'),
    path('cash-report/', CachFlowReportView.as_view(), name='cash_report_view'),


    path('csv-products/', product_csv_view, name='csv_products'),

    ]


