from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token
from rest_framework_jwt.views import verify_jwt_token
from .api.views import ApiLoginView, RegisterUsers

urlpatterns = [
    path('auth-jwt/', obtain_jwt_token),
    path('auth-jwt-refresh', refresh_jwt_token),
    path('auth=jwt-verify', verify_jwt_token),



    path('api-token-auth', obtain_jwt_token, name='create-token'),
    path('login/', ApiLoginView.as_view(), name='auth-login'),
    path('register/', RegisterUsers.as_view(), name="auth-register")

]