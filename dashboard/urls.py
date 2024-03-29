from django.contrib import admin
from django.urls import path, include, re_path
from .views import *
from .view_sells import *
from .views_ajax import *
from .views_site import *
from .views_product_settings import *

app_name = 'dashboard'

urlpatterns = [
    path('', DashBoard.as_view(), name='home'),

    path('products/', ProductsList.as_view(), name='products'),
    path('products/create/', ProductCreate.as_view(), name='product_create'),
    path('products/<int:pk>/', view=product_detail, name='product_detail'),
    path('products/add-images/<int:dk>/', ProductAddMultipleImages.as_view(), name='product_add_images'),
    path('products/edit-image/<int:pk>/<slug:action>/', view=edit_product_image, name='edit_product_image'),
    path('products/delete-images/<int:pk>/', view=delete_product_image, name='delete_image'),
    path('products/add-sizes/<int:pk>/', view=product_add_sizechart, name='product_add_sizes'),
    path('products/delete-sizes/<int:pk>/', view=delete_product_size, name='product_delete_size'),
    path('products/category-site-manager/<int:pk>/', CategorySiteManagerView.as_view(), name='category_site_manager'),
    path('products/add-sizes/create/<int:dk>/<int:pk>/', view=create_new_sizechart, name='create_product_sizechart'),
    path('products/add-related-products/<int:pk>/', RelatedProductsView.as_view(), name='product_related_view'),
    path('products/similar-products/<int:pk>/', SimilarColorProductsView.as_view(), name='product_similar_color_view'),


    # popup and ajax calls
    path('products/popup/create-brand/', view=createBrandPopup, name='brand_popup'),
    path('products/popup/create-category/', view=createCategoryPopup, name='category_popup'),
    path('products/popup/get_brand_id/', view=get_brand_id, name='get_brand_id'),
    path('products/popup/create-color/', view=createColorPopup, name='color_popup'),
    path('producs/popup/create-vendor/', view=createVendorPopup, name='vendor_popup'),
    path('products/popup/create-cate-site/', view=createCategorySitePopup, name='category_site_popup'),

    path('products/add-related-products/<int:pk>/ajax/<int:dk>/', view=ajax_add_related_item, name='ajax_add_related_item'),
    path('products/delete-related-products/<int:pk>/ajax/<int:dk>/', view=ajax_delete_related_product, name='ajax_delete_related_product'),
    path('products/different-color/<int:pk>/ajax/<int:dk>/<int:choose>/', view=ajax_differenent_color_product_add_or_remove, name='ajax_add_remove_similar_color'),

    path('products/ajax/add-or-remove-category-site/<int:pk>/<int:dk>/<slug:choice>/', view=ajax_category_site_add, name='category_site_add_or_remove'),
    path('product/ajax/category-site-search/<int:pk>/', view=ajax_category_site_search, name='ajax_category_site_search'),


    path('category/', CategoryPage.as_view(), name='categories'),
    path('categories-site/', CategorySitePage.as_view(), name='categories_site'),
    path('brands/', BrandPage.as_view(), name='brands'),
    path('colors/', ColorPage.as_view(), name='colors'),
    path('sizes/', SizePage.as_view(), name='sizes'),


    #  create urls
    path('category/create/', CategoryCreate.as_view(), name='category_create'),
    path('brands/create/', BrandsCreate.as_view(), name='brands_create'),
    path('colors/create/', ColorCreate.as_view(), name='color_create'),
    path('sizes/create/', SizeCreate.as_view(), name='size_create'),
    path('category/site/create/', CategorySiteCreate.as_view(), name='category_site_create'),

    #  delete urls
    path('category/delete/<int:pk>/', view=delete_category, name='delete_category'),
    path('category-site/delete/<int:pk>/', view=delete_category_site, name='delete_category_site'),
    path('brands/delete/<int:pk>/', view=delete_brand, name='delete_brand'),
    path('color/delete/<int:pk>/', view=delete_color, name='delete_color'),

    # edit url
    path('category/detail/<int:pk>/', CategoryDetail.as_view(), name='category_detail'),
    path('category/site/<int:pk>/', CategorySiteEdit.as_view(), name='edit_category_site'),
    path('brands/edit/<int:pk>/', view=brandEditPage, name='edit_brand'),
    path('size/edit/<int:pk>/', SizeEditPageView.as_view(), name='edit_size'),
    path('color/edit/<int:pk>/', ColorEditPage.as_view(), name='edit_color'),


    # redirects
    path('product/copy/<int:pk>/', view=create_copy_item, name='copy_product'),

    path('site-more_settings', SiteView.as_view(), name='site_view'),

    

    # order section
    path('eshop-orders/', EshopOrdersPage.as_view(), name='eshop_orders_page'),
    path('eshop-orders/create/', view=create_eshop_order, name='eshop_order_create'),
    path('eshop-orders/edit/<int:pk>/', view=eshop_order_edit, name='eshop_order_edit'),
    path('eshop/order/delete/<int:pk>/', delete_eshop_order, name='delete_eshop_order'),


    path('eshop-orders/billing-profile/edit/<int:pk>/', edit_billing_profile_view, name='edit_billing_view'),
    path('eshop-orders/change-status/<int:pk>/<int:dk>/', order_change_status_fast, name='order_change_status'),
    path('eshop-orders/warehouse-found/<int:pk>/', warehouse_found, name='warehouse_found'),

    path('eshop-orders/add-or-edit/<int:dk>/<int:pk>/<int:qty>/', view=add_edit_order_item, name='add_or_create'),
    path('eshop-orders/add-with-size/<int:pk>/<int:dk>/', CreateOrderItemWithSizePage.as_view(), name='add_with_size'),
    path('eshop-orders/edit-order-item/<int:dk>/', view=edit_order_item, name='edit_order_item'),

    path('eshop-orders/delete-order-item/<int:dk>/', view=delete_order_item, name='delete_order_item'),
    path('eshop-orders/print/<int:pk>/', view=print_invoice, name='print_invoice'),
    path('eshop-orders/gifts/', gifts_view, name='gift_view'),
    path('eshop-orders/gifts/<int:pk>/', gifts_edit, name='gift_detail'),
    path('eshop-orders/gifts/actions/<int:pk>/<int:dk>/<int:type>/<int:sub>/',
         gift_edit_products, name='gift_detail_pro'),
    path('eshop-orders/create-return-or-cancel-order/<int:pk>/<slug:instance_type>/',
         return_or_cancel_order, name='return_or_cancel'),

    path('carts/', CartListPage.as_view(), name='carts'),
    path('carts-details/<int:pk>/', CartDetailView.as_view(), name='cart_detail'),

    path('warehouse/order/shipping/', ShippingPage.as_view(), name='shipping_view'),
    path('warehouse/order/shipping/detail/<int:pk>/', ShippingEditPage.as_view(), name='shipping_edit_view'),
    path('warehouse/order/shipping/delete/<int:pk>/', view=delete_shipping, name='shipping_delete_view'),
    path('warehouse/order/shipping/create/', ShippingCreatePage.as_view(), name='shipping_create_view'),

    path('warehouse/order/payment-method/', PaymentMethodPage.as_view(), name='payment_view'),
    path('warehouse/order/payment-method/detail/<int:pk>/', PaymentMethodEditPage.as_view(), name='payment_edit_view'),
    path('warehouse/order/payment-method/delete/<int:pk>/', view=delete_payment_method, name='payment_delete_view'),
    path('warehouse/order/payment-method/create/', PaymentMethodCreatePage.as_view(), name='payment_create_view'),

    path('eshop-order/fast-change-status/', view=order_choices, name='order_choices'),


  
    # ajax calls
    path('category/ajax/create/', view=category_create, name='ajax_create_category'),
    path('category/ajax/get_category_id', view=get_category_id, name="ajax_category_id"),

    
    # site pages
    path('site-more_settings', SiteView.as_view(), name='site_view'),
    path('site-more_settings/banners/', BannerView.as_view(), name='banner_view'),
    path('site-more_settings/banners/create', BannerCreateView.as_view(), name='banner_create'),
    path('site-more_settings/banners/edit/<int:pk>/', BannerEditView.as_view(), name='banner_edit'),
    path('site-more_settings/banners/delete/<int:pk>/', view=banner_delete, name='banner_delete'),

    path('site-more_settings/coupons/', CouponsView.as_view(), name='coupons_view'),
    path('size-more_settings/coupons/edit/<int:pk>/', view=edit_coupon_view, name='coupons_edit_view'),
    path('size-more_settings/coupons/ajax/<int:pk>/<int:dk>/<slug:slug>/', ajax_edit_coupon_view, name='ajax_coupon_edit'),

    # user urls
    path('users-list/', UserListView.as_view(), name='users_list'),
    path('users/create/', UserCreateView.as_view(), name='user_create'), 
    path('users/edit/<int:pk>/', edit_user_view, name='edit_user'),
    path('users/delete/<int:pk>/', user_delete_view, name='delete_user'),

    path('costumers-list/', CostumerListView.as_view(), name='costumers_list'),
    path('costumer/create/', CostumerAccountCreateView.as_view(), name='costumer_create'),
    path('costumer/<int:pk>/', CostumerAccountEditView.as_view(), name='costumer_edit'),
    path('costumer/delete/<int:pk>/', delete_profile_view, name='delete_profile'),

    #tools
    path('tools/discount-manager/', discount_manager, name='discount_manager'),

    # page config urls
    path('page-config/', PageConfigView.as_view(), name="page_config"),
    path('page-config/create-banner/', view=create_banner, name='create_banner'),
    path('page-config/edit-banner/<int:dk>/', view=edit_banner_page, name='edit_banner'),
    path('page-config/delete-banner/<int:dk>/', view=delete_banner, name='delete_banner'),

    path('page-config/create-first_page/', view=create_first_page, name='create_first_page'),
    path('page-config/edit-first_page/<int:dk>/', view=edit_first_page, name='edit_first_page'),
    path('page-config/delete-first_page/<int:dk>/', view=delete_first_page, name='delete_first_page'),
]

