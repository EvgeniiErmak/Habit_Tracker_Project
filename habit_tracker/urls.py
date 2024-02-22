# habit_tracker/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HabitViewSet,
    PublicHabitListView,
    UserHabitListView,
    HabitCreateView,
    HabitUpdateView,
    HabitDeleteView,
)

router = DefaultRouter()
router.register(r"habits", HabitViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("public-habits/", PublicHabitListView.as_view(), name="public-habits"),
    path("my-habits/", UserHabitListView.as_view(), name="my-habits"),
    path("create-habit/", HabitCreateView.as_view(), name="create-habit"),
    path("update-habit/<int:pk>/", HabitUpdateView.as_view(), name="update-habit"),
    path("delete-habit/<int:pk>/", HabitDeleteView.as_view(), name="delete-habit"),
]
