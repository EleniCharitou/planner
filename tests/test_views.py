import pytest
from django.urls import reverse
from django.utils.timezone import now
from app.models import Attraction, Column, Post


@pytest.mark.django_db
class TestAttractionFlow:

    def test_create_attraction(self, auth_client, column):
        """Ensure authenticated user can create attraction"""
        url = reverse('attraction-list')
        data = {
            "column_id": column.id,
            "title": "Eiffel Tower",
            "location": "Paris",
            "category": "landmark",
            "date": now(),
            "cost": "25.00"
        }
        response = auth_client.post(url, data)
        assert response.status_code == 201
        assert Attraction.objects.count() == 1

    def test_move_attraction_same_column(self, auth_client, column):
        """Test the custom 'move' action"""
        a1 = Attraction.objects.create(column_id=column, title="A", location="X", date=now(), cost=0, position=0)
        a2 = Attraction.objects.create(column_id=column, title="B", location="X", date=now(), cost=0, position=1)
        a3 = Attraction.objects.create(column_id=column, title="C", location="X", date=now(), cost=0, position=2)

        url = reverse('attraction-move', args=[a3.id])
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
        url = reverse('trip-detail', args=[trip.id])

        response = api_client.get(url)
        assert response.status_code == 404

@pytest.mark.django_db
class TestGroupedAttractions:
    def test_kanban_structure(self, auth_client, trip):
        """Ensures the API returns the specific nested structure required by the frontend"""
        col1 = Column.objects.create(trip_id=trip, title="Day 1", position=0)
        col2 = Column.objects.create(trip_id=trip, title="Day 2", position=1)

        attraction = Attraction.objects.create(
            column_id=col1, title="Louvre Museum", location="Paris",
            date=now(), cost=20, position=0
        )

        url = reverse('grouped_attractions-list')
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

        url = reverse('posts-detail', args=[post.slug])
        data = {"title": "Updated Title", "content": "Updated"}

        response = auth_client.patch(url, data)
        assert response.status_code == 200
        post.refresh_from_db()
        assert post.title == "Updated Title"

    def test_others_cannot_update_post(self, api_client, other_user, user):
        """Random user should be FORBIDDEN from editing someone else's post."""
        post = Post.objects.create(author=user, title="User's Post", content="Private")

        api_client.force_authenticate(user=other_user)

        url = reverse('posts-detail', args=[post.slug])
        data = {"content": "Hacked"}

        response = api_client.patch(url, data)

        assert response.status_code == 403

        post.refresh_from_db()
        assert post.content == "Private"

    def test_others_can_read_post(self, api_client, other_user, user):
        """Random user CAN read posts (ReadOnly)."""
        post = Post.objects.create(author=user, title="Public Post", content="Hello")

        api_client.force_authenticate(user=other_user)
        url = reverse('posts-detail', args=[post.slug])

        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data['title'] == "Public Post"