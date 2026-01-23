from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes as permission_decorator
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Trip, Column, Attraction, VisitedAttraction, Post
from .serializers import (
    TripSerializer, ColumnSerializer, AttractionSerializer,
    VisitedAttractionSerializer, PostSerializer
)
from .permissions import IsTripOwner, IsPostAuthorOrReadOnly


class TripViewSet(viewsets.ModelViewSet):
    serializer_class = TripSerializer
    permission_classes = (IsAuthenticated, IsTripOwner)

    def get_queryset(self):
        # Filter trips to only show those owned by the current user.
        if getattr(self, 'swagger_fake_view', False) or self.request.user.is_anonymous:
            return Trip.objects.none()
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
        # Safety check for Swagger schema generation
        if getattr(self, 'swagger_fake_view', False) or self.request.user.is_anonymous:
            return Column.objects.none()
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
        if getattr(self, 'swagger_fake_view', False) or self.request.user.is_anonymous:
            return Attraction.objects.none()
        return Attraction.objects.filter(column_id__trip_id__owner=self.request.user)

    def perform_create(self, serializer):
        """
        Verify the column (and by extension, the trip) belongs to the user.
        """
        column = serializer.validated_data.get('column_id')
        if column.trip_id.owner != self.request.user:
            raise PermissionDenied("You cannot add attractions to trips you don't own.")
        serializer.save()

    def perform_destroy(self, instance):
        """
        Gap Closure: Reorder column after an attraction is deleted.
        """
        col_id = instance.column_id_id
        instance.delete()
        self._reorder_column(col_id)

    @action(detail=True, methods=['patch'], url_path='move')
    def move(self, request, pk=None):
        """
        Move a single attraction to a new column and/or position
        """
        attraction = self.get_object()
        new_col_id = request.data.get('column_id', attraction.column_id_id)
        new_pos = int(request.data.get('position', 0))
        old_col_id = attraction.column_id_id
        old_pos = attraction.position

        with transaction.atomic():
            # Moving within the SAME column
            if str(old_col_id) == str(new_col_id):
                if new_pos > old_pos:
                    Attraction.objects.filter(
                        column_id_id=new_col_id,
                        position__gt=old_pos,
                        position__lte=new_pos
                    ).update(position=F('position') - 1)

                elif new_pos < old_pos:
                    Attraction.objects.filter(
                        column_id_id=new_col_id,
                        position__gte=new_pos,
                        position__lt=old_pos
                    ).update(position=F('position') + 1)

                # Update the item itself
                attraction.position = new_pos
                attraction.save()

            # Moving to a DIFFERENT column
            else:
                Attraction.objects.filter(
                    column_id_id=new_col_id,
                    position__gte=new_pos
                ).update(position=F('position') + 1)

                attraction.column_id_id = new_col_id
                attraction.position = new_pos
                attraction.save()

                self._reorder_column(old_col_id)

        serializer = self.get_serializer(attraction)
        return Response(serializer.data)

    def _reorder_column(self, column_id):
        """
        Force-updates the database so positions are strictly 0, 1, 2, 3...
        """
        attractions = Attraction.objects.filter(column_id_id=column_id).order_by('position', 'id')

        for index, attraction in enumerate(attractions):
            if attraction.position != index:
                attraction.position = index
                attraction.save(update_fields=['position'])


class GroupedAttractionsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        Group attractions by column, filtered by user ownership.
        """
        trip_id = request.query_params.get('trip_id')

        if not trip_id:
            return Response({"error": "trip_id is required"}, status=400)
        # Verify the trip belongs to the user
        trip = get_object_or_404(Trip, id=trip_id, owner=request.user)
        columns = Column.objects.filter(trip_id=trip).order_by('id')
        attractions = Attraction.objects.filter(column_id__trip_id=trip).order_by('position')

        grouped_data = {
            col.id: {"id": str(col.id), "title": col.title, "cards": []}
            for col in columns
        }

        for attraction in attractions:
            col_id = attraction.column_id.id
            if col_id in grouped_data:
                grouped_data[col_id]["cards"].append(AttractionSerializer(attraction).data)

        return Response(list(grouped_data.values()))

class VisitedAttractionViewSet(viewsets.ModelViewSet):
    serializer_class = VisitedAttractionSerializer
    permission_classes = [IsAuthenticated, IsTripOwner]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or self.request.user.is_anonymous:
            return VisitedAttraction.objects.none()

        return VisitedAttraction.objects.filter(
            attraction_id__column_id__trip_id__owner=self.request.user
        ).select_related('attraction_id', 'attraction_id__column_id', 'attraction_id__column_id__trip_id')

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
    permission_classes = [IsAuthenticatedOrReadOnly, IsPostAuthorOrReadOnly]

    def perform_create(self, serializer):
        # Automatically set the author to the logged-in user
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        # Ensure author cannot be changed during update
        serializer.save()

    @action(detail=False, methods=['GET'])
    def recent(self, request):
        posts = Post.objects.all()[:6]
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

@api_view(['POST'])
@permission_decorator([IsAuthenticated])
def upload_image(request):
    """
    Standalone endpoint for image upload
    """
    if 'image' not in request.FILES:
        return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

    image = request.FILES['image']

    return Response({
        'message': 'Image uploaded successfully',
        'filename': image.name,
        'size': image.size
    }, status=status.HTTP_200_OK)