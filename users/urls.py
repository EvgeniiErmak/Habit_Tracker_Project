# users/urls.py
from .views import RegisterUserView, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path

urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
