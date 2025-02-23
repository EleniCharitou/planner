from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Trip, Column, Attraction, VisitedAttraction
from .serializers import TripSerializer, ColumnSerializer, AttractionSerializer, VisitedAttractionSerializer
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
