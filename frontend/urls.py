from django.conf.urls import url
from django.urls import path
from django.contrib.auth.views import logout
from django.conf.urls.static import static


from accounts.views import register_or_login
from .views import *

urlpatterns = [
    path('', Homepage.as_view(), name='homepage'),
    path('fast-ordering/', FastOrdering.as_view(), name='fast_ordering'),
    path('offer/', OffersPage.as_view(), name='offers_page'),
    path('new_products/', NewProductsPage.as_view(), name='new_products_page'),

    path('search/', SearchPage.as_view(), name='search_page'),
    url(r'^category/(?P<slug>[-\w]+)/$', CategoryPageList.as_view(), name='category_page'),

    path('brands/', BrandsPage.as_view(), name='brands'),
    url(r'^brands/(?P<slug>[-\w]+)/$', BrandPage.as_view(), name='brand'),

    url(r'^product/(?P<slug>[-\w]+)/$', view=product_detail, name='product_page'),
    path('cart-page/', CartPage.as_view(), name='cart_page'),
    path('cart-page/ajax/update/<int:pk>/<int:qty>/', view=update_cart_page, name='update_cart_page'),
    path('checkout/',  view=checkout_page, name='checkout_page'),
    path('order-view/<slug:pk>/', order_detail_view, name='order_view'),
    path('checkout/ajax-view/', '', ''),


    path('profile-page/', user_profile_page, name='profile-page'),
    path('login-page/', register_or_login, name='login_page'),
    path('logout/', logout, {'next_page': '/',}, name='log_out'),


    path('coupon-remove/<int:dk>/', view=delete_coupon, name='remove_coupon'),
    # create database always stay commented if in production

    path('user-data/', view=user_download_page, name='user_data'),

    # test using
    path('reset-cart/', view=reset_cart),
] 



