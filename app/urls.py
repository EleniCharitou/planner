from django.urls import path
from . import views
from rest_framework import routers

# router = routers.DefaultRouter()

# router.register(r'trips', views.TripViewset, basename='trips')

urlpatterns = [
	path('', views.AppOverview, name='home'),
    path('create/', views.add_items, name='add-items'),
    path('all/', views.view_items, name='view-items'),
    path('update/<int:pk>', views.update_items, name='update-items'),
    path('item/<int:pk>/delete/', views.delete_items, name='delete-items'),
 
    # path('trips/', views.TripViewset, name='trips'),
]
