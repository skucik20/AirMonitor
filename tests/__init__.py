import pytest
from unittest.mock import patch, Mock
from app.services.downloader import Downloader

BASE_URL = "http://fakeapi.com"

@pytest.fixture
def downloader():
    return Downloader(BASE_URL)

def mock_requests_get(json_data, status_code=200):
    mock_resp = Mock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = json_data
    return mock_resp

def test_fetch_station_index_success(downloader):
    station_id = "123"
    fake_response = {
        "AqIndex": {
            "Identyfikator stacji pomiarowej": 123,
            "Data wykonania obliczeń indeksu": "2025-08-27",
            "Wartość indeksu": 50,
            "Nazwa kategorii indeksu": "Good",
            "Data danych źródłowych, z których policzono wartość indeksu dla wskaźnika st": "2025-08-27"
        }
    }
    with patch("requests.get", return_value=mock_requests_get(fake_response)):
        aqi = downloader.fetch_station_index(station_id)
        assert aqi.station_id == 123
        assert aqi.index_value == 50
