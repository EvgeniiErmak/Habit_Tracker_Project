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


# URL-пути для API
api_urlpatterns = [
    path("public-habits/", PublicHabitListView.as_view(), name="public-habits"),
    path("my-habits/", UserHabitListView.as_view(), name="my-habits"),
    path("create-habit/", HabitCreateView.as_view(), name="create-habit"),
    path("update-habit/<int:pk>/", HabitUpdateView.as_view(), name="update-habit"),
    path("delete-habit/<int:pk>/", HabitDeleteView.as_view(), name="delete-habit"),
]

# URL-пути для аутентификации и пользователей
auth_urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/", include("users.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include((api_urlpatterns, "habit_tracker"))),  # пространство имен "habit_tracker"
    path("api/", include(auth_urlpatterns)),  # подключаем URL-пути для аутентификации и пользователей
    path("telegram/webhook/", webhook, name="telegram_webhook"),
    # Добавленные эндпоинты для документации
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
