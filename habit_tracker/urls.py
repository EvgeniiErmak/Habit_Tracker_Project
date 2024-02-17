# habit_tracker/urls.py
from .views import HabitListCreateView, HabitDetailView
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import HabitViewSet


router = DefaultRouter()
router.register(r'habits', HabitViewSet)


urlpatterns = [
    path('habits/', HabitListCreateView.as_view(), name='habit-list-create'),
    path('habits/<int:pk>/', HabitDetailView.as_view(), name='habit-detail'),
]
