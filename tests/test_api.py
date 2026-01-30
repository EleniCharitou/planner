import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_get_trips_list(auth_client, trip):
    url = reverse("trip-list")
    response = auth_client.get(url)
    assert response.status_code == 200
