from django.core.serializers import serialize
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Trip, Column, Attraction, VisitedAttraction, Post
from .serializers import TripSerializer, ColumnSerializer, AttractionSerializer, VisitedAttractionSerializer, \
    PostSerializer
from rest_framework import viewsets

class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

class ColumnViewSet(viewsets.ModelViewSet):
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer

    def get_queryset(self):
        queryset = Column.objects.all()
        trip_id = self.request.query_params.get('trip_id', None)
        if trip_id is not None:
            queryset = queryset.filter(trip_id=trip_id)
        return queryset

class AttractionViewSet(viewsets.ModelViewSet):
    queryset = Attraction.objects.all()
    serializer_class = AttractionSerializer

class GroupedAttractionsViewSet(viewsets.ViewSet):
    def list(self, request):
        trip_id = request.query_params.get('trip_id')

        if trip_id:
            attractions = Attraction.objects.filter(column_id__trip_id=trip_id).order_by('column_id')
        else:
            attractions = Attraction.objects.order_by('column_id')

        grouped_data = {}
        attractions = Attraction.objects.order_by('column_id')

        grouped_data = {}
        for attraction in attractions:
            column = attraction.column_id
            column_id = column.id

            if column_id not in grouped_data:
                grouped_data[column_id] = {
                    "id": column_id,
                    "title": column.title,
                    "cards": []
                }
            grouped_data[column_id]["cards"].append(AttractionSerializer(attraction).data)

        return Response(list(grouped_data.values()))

class VisitedAttractionViewSet(viewsets.ModelViewSet):
    queryset = VisitedAttraction.objects.all()
    serializer_class = VisitedAttractionSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'slug'

    @action(detail=False, methods=['GET'])
    def recent(self,  request):
        posts = Post.objects.all()[:6]
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    @api_view(['POST'])
    def upload_image(request):
        if 'image' in request.FILES:
            image = request.FILES['image']
            return Response({'image_url': 'path/to/uploaded/image.jpg'})
        return Response({'error': 'No image provided'}, status=400)