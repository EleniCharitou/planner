from rest_framework import serializers
from .models import *
 
class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('category', 'subcategory', 'name', 'amount')

class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ('destination', 'duration', 'company')

class AttractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attraction
        fields = ('title', 'location', 'category', 'mapUrl', 'ticket', 'date', 'cost', 'visited')

class VisitedAttractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitedAttraction
        fields = ('attractionTitle', 'actualCost', 'description', 'images', 'moment')

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('attraction', 'rating')

