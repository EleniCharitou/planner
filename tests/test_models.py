import pytest
from rest_framework.exceptions import ValidationError
from django.utils.timezone import now
from datetime import timedelta
from app.models import Trip, Attraction, Post


@pytest.mark.django_db
class TestTripModels:
    def test_trip_clean_dates(self, user):
        trip = Trip(
            destination="Bad Dates",
            start_date=now(),
            end_date=now() - timedelta(days=1),
            start_time="10:00", end_time="10:00",
            owner=user
        )
        with pytest.raises(ValidationError):
            trip.clean()


@pytest.mark.django_db
class TestAttractionLogic:
    def test_auto_positioning(self, column):
        a1 = Attraction.objects.create(column_id=column, title="A1", location="L", cost=10)
        a2 = Attraction.objects.create(column_id=column, title="A2", location="L", cost=10)

        assert a1.position == 0
        assert a2.position == 1

    def test_negative_cost(self, column):
        attraction = Attraction(
            column_id=column, title="Free Money", location="L", cost=-50
        )
        with pytest.raises(ValidationError):
            attraction.clean()

@pytest.mark.django_db
class TestPostLogic:
    def test_slug_generation(self, user):
        """Test that identical titles generate unique slugs automatically.
        Logic: 'My Trip' -> 'my-trip', then 'my-trip1', 'my-trip2' """
        p1 = Post.objects.create(author=user, title="My Trip", content="Content A")
        assert p1.slug == "my-trip"
        p2 = Post.objects.create(author=user, title="My Trip", content="Content B")
        assert p2.slug == "my-trip1"
        p3 = Post.objects.create(author=user, title="My Trip", content="Content C")
        assert p3.slug == "my-trip2"