from django.contrib.auth import get_user_model
from rest_framework import serializers

from app.models import Attraction, Column, Post, Trip, VisitedAttraction


class TripSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source="owner.email", read_only=True)
    duration_days = serializers.IntegerField(source="get_duration_days", read_only=True)

    class Meta:
        model = Trip
        fields = [
            "id",
            "destination",
            "trip_members",
            "start_date",
            "start_time",
            "end_date",
            "end_time",
            "owner",
            "owner_email",
            "duration_days",
        ]
        read_only_fields = ["owner"]  # Owner is set automatically in the view

    def validate(self, data):
        """
        Validate that start date is before end date.
        """
        if data.get("start_date") and data.get("end_date"):
            if data["start_date"] > data["end_date"]:
                raise serializers.ValidationError("Start date must be before end date")
        return data


class ColumnSerializer(serializers.ModelSerializer):
    trip_destination = serializers.CharField(
        source="trip_id.destination", read_only=True
    )

    class Meta:
        model = Column
        fields = ["id", "trip_id", "trip_destination", "title", "position"]

    def validate_trip_id(self, value):
        """
        Ensure the trip belongs to the current user.
        """
        request = self.context.get("request")
        if request and hasattr(request, "user") and value.owner != request.user:
            raise serializers.ValidationError(
                "You cannot add columns to trips you don't own."
            )
        return value


class AttractionSerializer(serializers.ModelSerializer):
    column_title = serializers.CharField(source="column_id.title", read_only=True)
    trip_destination = serializers.CharField(
        source="column_id.trip_id.destination", read_only=True
    )

    class Meta:
        model = Attraction
        fields = [
            "id",
            "column_id",
            "column_title",
            "trip_destination",
            "title",
            "location",
            "category",
            "mapUrl",
            "ticket",
            "cost",
            "visited",
            "position",
        ]

    def validate_column_id(self, value):
        """
        Ensure the column (and its trip) belongs to the current user.
        """
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            if value.trip_id.owner != request.user:
                raise serializers.ValidationError(
                    "You cannot add attractions to trips you don't own."
                )
        return value

    def validate_cost(self, value):
        """
        Ensure cost is not negative.
        """
        if value < 0:
            raise serializers.ValidationError("Cost cannot be negative")
        return value


class VisitedAttractionSerializer(serializers.ModelSerializer):
    attraction_title = serializers.CharField(
        source="attraction_id.title", read_only=True
    )

    class Meta:
        model = VisitedAttraction
        fields = [
            "id",
            "attraction_id",
            "attraction_title",
            "rating",
            "images",
            "moment",
            "reviewed_at",
            "actualCost",
        ]
        read_only_fields = ["reviewed_at"]

    def validate_attraction_id(self, value):
        """
        Ensure the attraction belongs to the current user's trip.
        """
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            if value.column_id.trip_id.owner != request.user:
                raise serializers.ValidationError(
                    "You cannot add visits to attractions you don't own."
                )
        return value


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.id")
    author_username = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "author_username",
            "title",
            "content",
            "slug",
            "created_at",
            "picture",
        ]
        read_only_fields = ["slug", "created_at", "author"]

    def get_author_username(self, obj):
        user = obj.author
        if not user:
            return "Unknown"

        first = (user.name or "").strip()
        last = (user.last_name or "").strip()

        if first and last:
            return f"{first.capitalize()} {last[0].upper()}."
        elif first:
            return first.capitalize()
        return user.email

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.picture:
            request = self.context.get("request")
            if request:
                representation["picture"] = request.build_absolute_uri(
                    instance.picture.url
                )
            else:
                representation["picture"] = instance.picture.url
        return representation

    def get_picture(self, obj):
        if obj.picture:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.picture.url)
            return obj.picture.url
        return None
