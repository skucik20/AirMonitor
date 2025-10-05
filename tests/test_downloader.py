import pytest
from unittest.mock import patch, Mock
from app.services.downloader import Downloader
from app.models.station_index import StationIndex
from app.models.measurement import Measurement
from app.models.sensor import Sensor
from app.models.station import Station
import requests

BASE_URL = "http://fakeapi.com"

@pytest.fixture
def downloader():
    return Downloader(BASE_URL)

# -----------------------------
# Helper function to mock requests.get
# -----------------------------
def mock_requests_get(json_data, status_code=200):
    mock_resp = Mock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = json_data
    return mock_resp

# -----------------------------
# Tests for fetch_station_index
# -----------------------------
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
        assert isinstance(aqi, StationIndex)
        assert aqi.station_id == 123
        assert aqi.index_value == 50

def test_fetch_station_index_failure(downloader):
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        result = downloader.fetch_station_index("123")
        assert result == {}

# -----------------------------
# Tests for fetch_measurement
# -----------------------------
def test_fetch_measurement_success(downloader):
    station_id = "123"
    fake_response = {
        "Lista danych pomiarowych": [
            {"Kod stanowiska": 1, "Data": "2025-08-27", "Wartość": 10},
            {"Kod stanowiska": 2, "Data": "2025-08-27", "Wartość": 20},
        ]
    }

    with patch("requests.get", return_value=mock_requests_get(fake_response)):
        measurements = downloader.fetch_measurement(station_id)
        assert len(measurements) == 2
        assert all(isinstance(m, Measurement) for m in measurements)
        assert measurements[0].wartosc == 10

def test_fetch_measurement_failure(downloader):
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        result = downloader.fetch_measurement("123")
        assert result == {}

# -----------------------------
# Tests for fetch_station_sensors_list
# -----------------------------
def test_fetch_station_sensors_list_success(downloader):
    station_id = "1"
    fake_response = {
        "Lista stanowisk pomiarowych dla podanej stacji": [
            {
                "Identyfikator stanowiska": 1,
                "Identyfikator stacji": 100,
                "Wskaźnik": "PM10",
                "Wskaźnik - wzór": "Formula1",
                "Wskaźnik - kod": "PM10",
                "Id wskaźnika": 10
            }
        ]
    }

    with patch("requests.get", return_value=mock_requests_get(fake_response)):
        sensors = downloader.fetch_station_sensors_list(station_id)
        assert len(sensors) == 1
        assert isinstance(sensors[0], Sensor)
        assert sensors[0].wskaznik == "PM10"

def test_fetch_station_sensors_list_failure(downloader):
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        result = downloader.fetch_station_sensors_list("1")
        assert result == {}

# -----------------------------
# Tests for fetch_station_sensors_dict
# -----------------------------
def test_fetch_station_sensors_dict_success(downloader):
    station_id = "1"
    fake_response = {
        "Lista stanowisk pomiarowych dla podanej stacji": [
            {
                "Identyfikator stanowiska": 1,
                "Identyfikator stacji": 100,
                "Wskaźnik": "PM10",
                "Wskaźnik - wzór": "Formula1",
                "Wskaźnik - kod": "PM10",
                "Id wskaźnika": 10
            }
        ]
    }

    with patch("requests.get", return_value=mock_requests_get(fake_response)):
        sensors_dict = downloader.fetch_station_sensors_dict(station_id)
        assert 1 in sensors_dict
        assert isinstance(sensors_dict[1], Sensor)

def test_fetch_station_sensors_dict_failure(downloader):
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        result = downloader.fetch_station_sensors_dict("1")
        assert result == {}

# -----------------------------
# Tests for fetch_stations_list
# -----------------------------
def test_fetch_stations_list_success(downloader):
    fake_response = {
        "Lista stacji pomiarowych": [
            {
                "Identyfikator stacji": 1,
                "Kod stacji": "S1",
                "Nazwa stacji": "Station1",
                "WGS84 φ N": 50.0,
                "WGS84 λ E": 20.0,
                "Identyfikator miasta": 1,
                "Nazwa miasta": "City1",
                "Gmina": "Gmina1",
                "Powiat": "Powiat1",
                "Województwo": "Woj1",
                "Ulica": "Street1"
            }
        ]
    }

    with patch("requests.get", return_value=mock_requests_get(fake_response)):
        stations = downloader.fetch_stations_list()
        assert len(stations) == 1
        assert isinstance(stations[0], Station)
        assert stations[0].stationName == "Station1"

def test_fetch_stations_list_failure(downloader):
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        result = downloader.fetch_stations_list()
        assert result == {}

# -----------------------------
# Tests for fetch_stations_list_by_city
# -----------------------------
def test_fetch_stations_list_by_city(downloader):
    fake_response = {
        "Lista stacji pomiarowych": [
            {
                "Identyfikator stacji": 1,
                "Kod stacji": "S1",
                "Nazwa stacji": "Station1",
                "WGS84 φ N": 50.0,
                "WGS84 λ E": 20.0,
                "Identyfikator miasta": 1,
                "Nazwa miasta": "City1",
                "Gmina": "Gmina1",
                "Powiat": "Powiat1",
                "Województwo": "Woj1",
                "Ulica": "Street1"
            },
            {
                "Identyfikator stacji": 2,
                "Kod stacji": "S2",
                "Nazwa stacji": "Station2",
                "WGS84 φ N": 51.0,
                "WGS84 λ E": 21.0,
                "Identyfikator miasta": 2,
                "Nazwa miasta": "City2",
                "Gmina": "Gmina2",
                "Powiat": "Powiat2",
                "Województwo": "Woj2",
                "Ulica": "Street2"
            }
        ]
    }

    with patch("requests.get", return_value=mock_requests_get(fake_response)):
        stations = downloader.fetch_stations_list_by_city("City1")
        assert len(stations) == 1
        assert stations[0].city.name == "City1"

def test_fetch_stations_list_by_city_failure(downloader):
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        result = downloader.fetch_stations_list_by_city("City1")
        assert result == {}

# -----------------------------
# Tests for fetch_stations_dict
# -----------------------------
def test_fetch_stations_dict_success(downloader):
    fake_response = {
        "Lista stacji pomiarowych": [
            {
                "Identyfikator stacji": 1,
                "Kod stacji": "S1",
                "Nazwa stacji": "Station1",
                "WGS84 φ N": 50.0,
                "WGS84 λ E": 20.0,
                "Identyfikator miasta": 1,
                "Nazwa miasta": "City1",
                "Gmina": "Gmina1",
                "Powiat": "Powiat1",
                "Województwo": "Woj1",
                "Ulica": "Street1"
            }
        ]
    }

    with patch("requests.get", return_value=mock_requests_get(fake_response)):
        stations_dict = downloader.fetch_stations_dict()
        assert 1 in stations_dict
        assert isinstance(stations_dict[1], Station)

def test_fetch_stations_dict_failure(downloader):
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        result = downloader.fetch_stations_dict()
        assert result == {}
