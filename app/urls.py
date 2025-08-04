from django.urls import path, include
from rest_framework.routers import DefaultRouter

from planner import settings
from .views import TripViewSet, ColumnViewSet, AttractionViewSet, VisitedAttractionViewSet, PostViewSet, GroupedAttractionsViewSet

router = DefaultRouter()
router.register(r'trip', TripViewSet, basename='trip')
router.register(r'column', ColumnViewSet, basename='column')
router.register(r'attraction', AttractionViewSet, basename='attraction')
router.register(r'visited', VisitedAttractionViewSet, basename='visited')
router.register(r'posts', PostViewSet, basename='posts')

router.register(r'grouped_attractions', GroupedAttractionsViewSet, basename='grouped_attractions')



urlpatterns = [
    path('', include(router.urls)),
]
