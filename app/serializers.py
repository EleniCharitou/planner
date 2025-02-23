from rest_framework import serializers
from .models import *


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = '__all__'

class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = '__all__'

class AttractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attraction
        fields = '__all__'

class VisitedAttractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitedAttraction
        fields = '__all__'


