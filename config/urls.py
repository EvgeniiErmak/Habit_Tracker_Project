# config/urls.py
from users.views import RegisterUserView
from django.contrib import admin
from django.urls import path, include
from telegram_integration.views import webhook
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from habit_tracker.urls import urlpatterns as habit_tracker_urls


# URL-пути для аутентификации и пользователей
auth_urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/", include("users.urls")),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(habit_tracker_urls)),  # Используем импортированные эндпоинты
    path("api/", include(auth_urlpatterns)),  # подключаем URL-пути для аутентификации и пользователей
    path("telegram/webhook/", webhook, name="telegram_webhook"),
    # Добавленные эндпоинты для документации
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
