"""
URL configuration for tournaments app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TournamentViewSet

# Create router for ViewSets
router = DefaultRouter()
router.register(r'tournaments', TournamentViewSet, basename='tournament')

# URL patterns
urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]
