from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from rest_framework import routers

from .views import TripViewSet

router = DefaultRouter()
router.register(r'trip', TripViewSet, basename='trip')


urlpatterns = [
    path('', include(router.urls)),
	path('', views.app_overview, name='home'),
    path('create/', views.add_items, name='add-items'),
    path('all/', views.view_items, name='view-items'),
    path('update/<int:pk>', views.update_items, name='update-items'),
    path('item/<int:pk>/delete/', views.delete_items, name='delete-items'),
]
