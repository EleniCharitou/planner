import pytest
from app.serializers import TripSerializer
from django.utils.timezone import now
from datetime import timedelta

@pytest.mark.django_db
def test_trip_serializer_date_validation():
    data = {
        "destination": "London",
        "start_date": now() + timedelta(days=5),
        "end_date": now(),
        "start_time": "10:00",
        "end_time": "12:00"
    }
    serializer = TripSerializer(data=data)
    assert not serializer.is_valid()
    assert "Start date must be before" in str(serializer.errors)