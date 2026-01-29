import pytest
from rest_framework.exceptions import ValidationError
from django.utils.timezone import now
from datetime import timedelta
from app.models import Trip, Attraction


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
        a1 = Attraction.objects.create(column_id=column, title="A1", location="L", date=now(), cost=10)
        a2 = Attraction.objects.create(column_id=column, title="A2", location="L", date=now(), cost=10)

        assert a1.position == 0
        assert a2.position == 1

    def test_negative_cost(self, column):
        attraction = Attraction(
            column_id=column, title="Free Money", location="L",
            date=now(), cost=-50
        )
        with pytest.raises(ValidationError):
            attraction.clean()