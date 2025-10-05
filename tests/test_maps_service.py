import pytest
from unittest.mock import patch, Mock
from app.services.maps_service import StationMap, StationMapWithRadius
from app.models.station import Station
from app.models.city import City
from app.models.gmina import Gmina
import folium

# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def sample_station():
    gmina = Gmina()
    gmina.gminaName = "Gmina1"
    gmina.powiatName = "Powiat1"
    gmina.wojewodztwoName = "Woj1"

    city = City()
    city.id = 1
    city.name = "City1"
    city.gmina = gmina

    station = Station()
    station.id = 1
    station.stationCode = "S1"
    station.stationName = "Station1"
    station.gegrLat = 52.0
    station.gegrLon = 19.0
    station.city = city
    station.addressStreet = "Street1"

    return station

@pytest.fixture
def stations_list(sample_station):
    return [sample_station]

# -----------------------------
# Testy dla StationMap
# -----------------------------
def test_create_default_map(stations_list):
    sm = StationMap(stations_list)
    m = sm.create_default_map()
    assert isinstance(m, folium.Map)

    # sprawdzamy, czy dodano marker
    markers = [child for child in m._children.values() if isinstance(child, folium.map.Marker)]
    assert len(markers) == len(stations_list)

# -----------------------------
# Testy dla StationMapWithRadius
# -----------------------------
@patch("requests.get")
def test_geocode_address_success(mock_get):
    # Mockujemy odpowiedź API
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = [{"lat": "52.1", "lon": "19.1"}]

    smwr = StationMapWithRadius([], location="Warsaw", radius=10)
    lat, lon = smwr.geocode_address()
    assert lat == 52.1
    assert lon == 19.1

@patch("requests.get")
def test_geocode_address_empty(mock_get):
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = []

    smwr = StationMapWithRadius([], location="Unknown", radius=10)
    result = smwr.geocode_address()
    assert result is None

def test_haversine_distance():
    smwr = StationMapWithRadius([], location=None, radius=None)
    dist = smwr.haversine(52.0, 19.0, 52.0, 19.0)
    assert dist == 0
    dist2 = smwr.haversine(52.0, 19.0, 53.0, 19.0)
    assert dist2 > 0

def test_filter_stations_by_radius(stations_list):
    smwr = StationMapWithRadius(stations_list, location=None, radius=100)
    smwr.lat = 52.0
    smwr.lon = 19.0
    filtered = smwr.filter_stations_by_radius()
    assert filtered == stations_list

def test_sort_list_by_location_and_radius(monkeypatch, stations_list):
    smwr = StationMapWithRadius(stations_list, location="Warsaw", radius=100)

    # Mockujemy geocode_address i filter_stations_by_radius
    monkeypatch.setattr(smwr, "geocode_address", lambda: (52.0, 19.0))
    monkeypatch.setattr(smwr, "filter_stations_by_radius", lambda: stations_list)

    result = smwr.sort_list_by_location_and_radius()
    assert result == stations_list

def test_create_map(monkeypatch, stations_list):
    smwr = StationMapWithRadius(stations_list, location="Warsaw", radius=100)
    # mockujemy metodę sortującą
    monkeypatch.setattr(smwr, "sort_list_by_location_and_radius", lambda: stations_list)
    m = smwr.create_map()
    assert isinstance(m, folium.Map)
    markers = [child for child in m._children.values() if isinstance(child, folium.map.Marker)]
    assert len(markers) == len(stations_list)
