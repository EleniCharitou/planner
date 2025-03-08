from django.core.serializers import serialize
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import action
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

class AttractionViewSet(viewsets.ModelViewSet):
    queryset = Attraction.objects.all()
    serializer_class = AttractionSerializer

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