from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .models import VisitedAttraction
from .views import TripViewSet, ColumnViewSet, AttractionViewSet, VisitedAttractionViewSet

router = DefaultRouter()
router.register(r'trip', TripViewSet, basename='trip')
router.register(r'column', ColumnViewSet, basename='column')
router.register(r'attraction', AttractionViewSet, basename='attraction')
router.register(r'visited', VisitedAttractionViewSet, basename='visited')



urlpatterns = [
    path('', include(router.urls)),
]
