from django.urls import path, include
from .views import homepage


urlpatterns = [

    path('', homepage),
    path('inventory/', include('inventory_manager.api.urls')),
    path('auth/', include('accounts.urls')),
    path('transcations/', include('transcations.api.urls')),
    path('general/', include('site_settings.api.urls'))

]