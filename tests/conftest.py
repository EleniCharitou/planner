import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.utils.timezone import now
from datetime import timedelta
from app.models import Trip, Column

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="owner@test.com",
        password="password"
    )

@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        email="hacker@test.com",
        password="password"
    )

@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def trip(user):
    return Trip.objects.create(
        destination="Paris",
        start_date=now(),
        start_time="10:00",
        end_date=now() + timedelta(days=5),
        end_time="12:00",
        owner=user
    )

@pytest.fixture
def column(trip):
    return Column.objects.create(trip_id=trip, title="Day 1", position=0)