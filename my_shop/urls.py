from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import url
from point_of_sale.api.views import RetailOrderListApi, RetailRenderer


urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls', namespace='dashboard', )),
    path('cart/', include('carts.urls', namespace='cart')),
    path('', include('my_site.urls')),

    path('cookie-gdpr/', include('gdpr.urls')),
    path('api/', include('products.api.urls')),

    # third parties
    url(r'^oauth/', include('social_django.urls', namespace='social')),  # <--

    # api
    path('retail/api/', RetailOrderListApi.as_view()),
    path('retail/api/detail/<int:pk>/', RetailRenderer.as_view(), name='api_retail_detail'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


'''
path('dashboard/', include('dashboard.urls', namespace='dashboard',)),
path('dashboard/users/', include('account.urls', namespace='users',)),
path('reports/', include('reports.urls', namespace='reports',)),
path('pos/', include('point_of_sale.urls', namespace='pos',)),
path('billings/', include('transcations.urls', namespace='billings')),
path('inventory/', include('inventory_manager.urls', namespace='inventory')),
'''