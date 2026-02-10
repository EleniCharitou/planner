import pytest
from django.urls import reverse

from app.models import Attraction, Column, Post, Trip


@pytest.mark.django_db
class TestAttractionFlow:
    def test_create_attraction(self, auth_client, column):
        """Ensure authenticated user can create attraction"""
        url = reverse("attraction-list")
        data = {
            "column_id": column.id,
            "title": "Eiffel Tower",
            "location": "Paris",
            "category": "landmark",
            "cost": "25.00",
        }
        response = auth_client.post(url, data)
        assert response.status_code == 201
        assert Attraction.objects.count() == 1

    def test_move_attraction_same_column(self, auth_client, column):
        """Test the custom 'move' action"""
        a1 = Attraction.objects.create(
            column_id=column, title="A", location="X", cost=0, position=0
        )
        a2 = Attraction.objects.create(
            column_id=column, title="B", location="X", cost=0, position=1
        )
        a3 = Attraction.objects.create(
            column_id=column, title="C", location="X", cost=0, position=2
        )

        url = reverse("attraction-move", args=[a3.id])
        data = {"column_id": column.id, "position": 0}

        response = auth_client.patch(url, data)
        assert response.status_code == 200

        a1.refresh_from_db()
        a2.refresh_from_db()
        a3.refresh_from_db()

        assert a3.position == 0
        assert a1.position == 1
        assert a2.position == 2


@pytest.mark.django_db
class TestSecurity:
    def test_cannot_access_others_trip(self, api_client, other_user, trip):
        """Hacker cannot see Owner's trip"""
        api_client.force_authenticate(user=other_user)
        url = reverse("trip-detail", args=[trip.id])

        response = api_client.get(url)
        assert response.status_code == 404


@pytest.mark.django_db
class TestGroupedAttractions:
    def test_kanban_structure(self, auth_client, trip):
        """Ensures the API returns the specific nested structure
           required by the frontend"""
        col1 = Column.objects.create(trip_id=trip, title="Day 1", position=0)
        col2 = Column.objects.create(trip_id=trip, title="Day 2", position=1)

        attraction = Attraction.objects.create(
            column_id=col1, title="Louvre Museum", location="Paris", cost=20, position=0
        )

        url = reverse("grouped_attractions-list")
        response = auth_client.get(f"{url}?trip_id={trip.id}")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 2

        day1_data = next(item for item in data if item["id"] == str(col1.id))

        assert day1_data["title"] == col1.title
        assert len(day1_data["cards"]) == 1

        card = day1_data["cards"][0]
        assert card["id"] == attraction.id
        assert card["title"] == attraction.title

        day2_data = next(item for item in data if item["id"] == str(col2.id))
        assert day2_data["title"] == col2.title
        assert len(day2_data["cards"]) == 0


@pytest.mark.django_db
class TestPostPermissions:
    def test_author_can_update_post(self, auth_client, user):
        """Owner should be able to edit their own post."""
        post = Post.objects.create(author=user, title="My Post", content="Original")

        url = reverse("posts-detail", args=[post.slug])
        data = {"title": "Updated Title", "content": "Updated"}

        response = auth_client.patch(url, data)
        assert response.status_code == 200
        post.refresh_from_db()
        assert post.title == "Updated Title"

    def test_others_cannot_update_post(self, api_client, other_user, user):
        """Random user should be FORBIDDEN from editing someone else's post."""
        post = Post.objects.create(author=user, title="User's Post", content="Private")

        api_client.force_authenticate(user=other_user)

        url = reverse("posts-detail", args=[post.slug])
        data = {"content": "Hacked"}

        response = api_client.patch(url, data)

        assert response.status_code == 403

        post.refresh_from_db()
        assert post.content == "Private"

    def test_others_can_read_post(self, api_client, other_user, user):
        """Random user CAN read posts (ReadOnly)."""
        post = Post.objects.create(author=user, title="Public Post", content="Hello")

        api_client.force_authenticate(user=other_user)
        url = reverse("posts-detail", args=[post.slug])

        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["title"] == "Public Post"


@pytest.mark.django_db
class TestTripCreationFlow:
    def test_create_trip_generates_columns_automatically(self, auth_client):
        """
        Verify that creating a multi-day trip automatically, Creates the Trip, 'Attractions' column (pos 0).
        """
        url = reverse("trip-list")

        data = {
            "destination": "Rome",
            "start_date": "2025-05-01",
            "end_date": "2025-05-03",
            "start_time": "09:00:00",
            "end_time": "18:00:00",
            "trip_members": [],
        }

        response = auth_client.post(url, data)

        assert response.status_code == 201
        assert Trip.objects.count() == 1

        trip = Trip.objects.first()
        columns = Column.objects.filter(trip_id=trip).order_by("position")

        assert columns.count() == 4

        assert columns[0].title == "🎯 Attractions to Visit"
        assert columns[0].position == 0

        assert "Day 1" in columns[1].title
        assert columns[1].position == 1

        assert "Day 3" in columns[3].title
        assert columns[3].position == 3

    def test_create_single_day_trip_success(self, auth_client):
        """
        Test that a Single Day Trip (Start == End) is ALLOWED. Should create 2 columns: 'Attractions' + 'Day 1'.
        """
        url = reverse("trip-list")

        data = {
            "destination": "Day Trip to Beach",
            "start_date": "2025-07-20",
            "end_date": "2025-07-20",
            "start_time": "08:00:00",
            "end_time": "20:00:00",
            "trip_members": []
        }

        response = auth_client.post(url, data)

        assert response.status_code == 201

        trip = Trip.objects.first()
        columns = Column.objects.filter(trip_id=trip).order_by('position')

        assert columns.count() == 2

        assert columns[0].title == "🎯 Attractions to Visit"
        assert "Day 1" in columns[1].title

    def test_create_trip_fails_without_dates(self, auth_client):
        """
        Ensure that creating a trip without start/end dates fails.
        Dates are mandatory fields.
        """
        url = reverse("trip-list")
        data = {
            "destination": "Dream Trip",
        }

        response = auth_client.post(url, data)

        assert response.status_code == 400

        errors = response.json()
        assert "start_date" in errors
        assert "end_date" in errors

        assert Trip.objects.count() == 0