# habit_tracker/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HabitViewSet

router = DefaultRouter()
router.register(r'habits', HabitViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
