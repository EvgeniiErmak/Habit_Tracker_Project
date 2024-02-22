# config/urls.py

from users.views import RegisterUserView
from habit_tracker.views import (
    PublicHabitListView,
    UserHabitListView,
    HabitCreateView,
    HabitUpdateView,
    HabitDeleteView,
)
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

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("habit_tracker.urls")),
    path(
        "api/schema/", SpectacularAPIView.as_view(), name="schema"
    ),  # Генерация схемы API
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),  # Swagger UI
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),  # Redoc
    path("api/register/", RegisterUserView.as_view(), name="register"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/users/", include("users.urls")),
    path("telegram/webhook/", webhook, name="telegram_webhook"),
    # Добавленные эндпоинты для документации
    path("api/public-habits/", PublicHabitListView.as_view(), name="public-habits"),
    path("api/my-habits/", UserHabitListView.as_view(), name="my-habits"),
    path("api/create-habit/", HabitCreateView.as_view(), name="create-habit"),
    path("api/update-habit/<int:pk>/", HabitUpdateView.as_view(), name="update-habit"),
    path("api/delete-habit/<int:pk>/", HabitDeleteView.as_view(), name="delete-habit"),
]
