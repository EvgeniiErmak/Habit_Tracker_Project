# habit_tracker/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HabitViewSet
from . import views

router = DefaultRouter()
router.register(r'habits', HabitViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/your-endpoint/', views.your_view_function, name='your-url-name'),
]
