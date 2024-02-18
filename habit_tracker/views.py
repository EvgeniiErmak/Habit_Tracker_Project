# habit_tracker/views.py
from rest_framework import viewsets, permissions, pagination
from .models import Habit
from .serializers import HabitSerializer


class HabitPagination(pagination.PageNumberPagination):
    page_size = 5


class HabitViewSet(viewsets.ModelViewSet):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    pagination_class = HabitPagination

    def get_permissions(self):
        if self.action in ['list']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
