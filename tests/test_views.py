import pytest
from django.urls import reverse
from django.utils.timezone import now
from app.models import Attraction


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