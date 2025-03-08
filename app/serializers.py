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

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

# get_recent_posts = http://127.0.0.1:8000/api/posts/recent
# specific_post = http://127.0.0.1:8000/api/posts/:slug