from django.contrib import admin
from django.urls import path, include, re_path
from .views import *


app_name = 'dashboard'

urlpatterns = [
    path('', DashBoard.as_view(), name='home'),

    path('products/', ProductsList.as_view(), name='products'),
    path('products/create/', ProductCreate.as_view(), name='product_create'),
    path('products/<int:pk>/', view=product_detail, name='product_detail'),
    path('products/add-images/<int:dk>/', ProductAddMultipleImages.as_view(), name='product_add_images'),
    path('products/delete-images/<int:pk>/', view=delete_product_image, name='delete_image'),
    path('products/add-sizes/<int:dk>/', view=product_add_sizechart, name='product_add_sizes'),
    path('products/add-sizes/create/<int:dk>/<int:pk>/', view=create_new_sizechart, name='create_product_sizechart'),
    path('products/add-related-products/<int:pk>/', RelatedProductsView.as_view(), name='product_related_view'),

    # popup and ajax calls
    # path('products/popup/create-brand/', view=createBrandPopup, name='brand_popup'),
    # path('products/popup/create-category/', view=createCategoryPopup, name='category_popup'),
    # path('products/popup/get_brand_id/', view=get_brand_id, name='get_brand_id'),
    # path('products/popup/create-color/', view=create_color_popup, name='color_popup'),


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
    path('brands/delete/<int:pk>/', view=delete_brand, name='delete_brand'),
    path('color/delete/<int:pk>/', view=delete_color, name='delete_color'),

    # edit url
    path('category/detail/<int:pk>/', CategoryDetail.as_view(), name='category_detail'),
    path('category/site/<int:pk>/', CategorySiteEdit.as_view(), name='edit_category_site'),
    path('brands/edit/<int:pk>', view=brandEditPage, name='edit_brand'),
    path('size/edit/<int:pk>', SizeEditPage.as_view(), name='edit_size'),
    path('color/edit/<int:pk>/', ColorEditPage.as_view(), name='edit_color'),


    # redirects
    path('product/copy/<int:pk>/', view=create_copy_item, name='copy_product'),

    path('site-settings', view=create_copy_item, name='site_view'),

    path('warehouse/home/', view=create_copy_item, name='warehouse_home'),

]

