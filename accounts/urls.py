from django.urls import path
from rest_framework_simplejwt import views as jwt_views
# from rest_framework_jwt.views import obtain_jwt_token
# from rest_framework_jwt.views import refresh_jwt_token
# from rest_framework_jwt.views import verify_jwt_token
from .api.views import ApiLoginView, RegisterUsers, ApiStaffView

urlpatterns = [
    # path('auth-jwt/', obtain_jwt_token),
    # path('auth-jwt-refresh/', refresh_jwt_token),
    # path('auth-jwt-verify/', verify_jwt_token),

    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

    path('login/', ApiLoginView.as_view(), name='auth-login'),
    path('register/', RegisterUsers.as_view(), name="auth-register"),

    path('staff-members/', ApiStaffView.as_view(), name='staff_members'),

]