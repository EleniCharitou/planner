from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Trip, Column, Attraction, VisitedAttraction, Post
from .serializers import (
    TripSerializer, ColumnSerializer, AttractionSerializer,
    VisitedAttractionSerializer, PostSerializer
)
from .permissions import IsTripOwner


class TripViewSet(viewsets.ModelViewSet):
    serializer_class = TripSerializer
    permission_classes = (IsAuthenticated, IsTripOwner)

    def get_queryset(self):
        # Filter trips to only show those owned by the current user.
        return Trip.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Automatically set the owner to the current user when creating a trip.
        serializer.save(owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        trip = self.get_object()
        if trip.owner != request.user:
            raise PermissionDenied("You do not have permission to access this trip.")
        serializer = self.get_serializer(trip)
        return Response(serializer.data)

class ColumnViewSet(viewsets.ModelViewSet):
    serializer_class = ColumnSerializer
    permission_classes = [IsAuthenticated, IsTripOwner]

    def get_queryset(self):
        # Filter columns to only show those belonging to the user's trips.
        queryset = Column.objects.filter(trip_id__owner=self.request.user)
        trip_id = self.request.query_params.get('trip_id', None)

        if trip_id is not None:
            # Verify the trip belongs to the user
            trip = get_object_or_404(Trip, id=trip_id, owner=self.request.user)
            queryset = queryset.filter(trip_id=trip)

        return queryset

    def perform_create(self, serializer):
       # Verify the trip belongs to the user before creating a column.
        trip = serializer.validated_data.get('trip_id')
        if trip.owner != self.request.user:
            raise PermissionDenied("You cannot add columns to trips you don't own.")
        serializer.save()

class AttractionViewSet(viewsets.ModelViewSet):
    serializer_class = AttractionSerializer
    permission_classes = [IsAuthenticated, IsTripOwner]

    def get_queryset(self):
        """
        Filter attractions to only show those belonging to the user's trips.
        """
        return Attraction.objects.filter(
            column_id__trip_id__owner=self.request.user
        )

    def perform_create(self, serializer):
        """
        Verify the column (and by extension, the trip) belongs to the user.
        """
        column = serializer.validated_data.get('column_id')
        if column.trip_id.owner != self.request.user:
            raise PermissionDenied("You cannot add attractions to trips you don't own.")
        serializer.save()

class GroupedAttractionsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        Group attractions by column, filtered by user ownership.
        """
        trip_id = request.query_params.get('trip_id')

        if trip_id:
            # Verify the trip belongs to the user
            trip = get_object_or_404(Trip, id=trip_id, owner=request.user)
            attractions = Attraction.objects.filter(
                column_id__trip_id=trip
            ).order_by('column_id')
        else:
            # Get all attractions from user's trips
            attractions = Attraction.objects.filter(
                column_id__trip_id__owner=request.user
            ).order_by('column_id')

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
            grouped_data[column_id]["cards"].append(
                AttractionSerializer(attraction).data
            )

        return Response(list(grouped_data.values()))

class VisitedAttractionViewSet(viewsets.ModelViewSet):
    serializer_class = VisitedAttractionSerializer
    permission_classes = [IsAuthenticated, IsTripOwner]

    def get_queryset(self):
        """
        Filter visited attractions to only show those from the user's trips.
        """
        return VisitedAttraction.objects.filter(
            attraction_id__column_id__trip_id__owner=self.request.user
        )

    def perform_create(self, serializer):
        """
        Verify the attraction belongs to the user before creating a visit record.
        """
        attraction = serializer.validated_data.get('attraction_id')
        if attraction.column_id_id.trip_id.owner != self.request.user:
            raise PermissionDenied("You cannot add visits to attractions you don't own.")
        serializer.save()

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['GET'])
    def recent(self, request):
        posts = Post.objects.all()[:6]
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    @api_view(['POST'])
    def upload_image(request):
        if 'image' in request.FILES:
            image = request.FILES['image']
            return Response({'image_url': 'path/to/uploaded/image.jpg'})
        return Response({'error': 'No image provided'}, status=400)