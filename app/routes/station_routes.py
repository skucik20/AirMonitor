from flask import Blueprint, render_template, request, redirect, url_for
from app.services.downloader import Downloader
from app.services.data_service import DataService
from app.services.maps_service import StationMap, StationMapWithRadius
from app.services.calculation_service import CalculationService
from app.models.station import Station

import json
import folium

from math import radians, cos, sin, asin, sqrt
import requests

station_bp = Blueprint("stations", __name__)
api_address = "https://api.gios.gov.pl/pjp-api/v1/rest"

@station_bp.route("/")
def index():
    """
    Strona główna aplikacji.

    Renderuje szablon `home.html`, który pełni rolę punktu wejścia
    dla użytkownika (np. prezentuje menu, opis działania lub
    odnośniki do innych widoków).
    """
    return render_template("home.html")

@station_bp.route("/live")
def list_stations():
    """
    Widok wyświetlający listę stacji pomiarowych w Polsce wraz z ich lokalizacją na mapie.

    - Pobiera listę stacji z API GIOŚ przy użyciu klasy `Downloader`.
    - Tworzy mapę osadzoną w środku Polski.
    - Renderuje szablon
    """

    downloader = Downloader(api_address)
    stations_list = downloader.fetch_stations_list()

    station_map = StationMap(stations_list)
    fmap = station_map.create_default_map()

    return render_template("stations.html", source="api", stations=stations_list, map_html=fmap._repr_html_())

@station_bp.route("/archive")
def list_stations_archive():
    """
    Widok wyświetlający archiwalną listę stacji pomiarowych z bazy danych.

    - Korzysta z `DataService` do pobrania listy stacji zapisanych lokalnie w bazie.
    - Tworzy mapę za pomocą klasy `StationMap` z domyślnym ustawieniem środka i przybliżenia.
    - Renderuje szablon
    """

    service = DataService()

    stations_list = service.get_stations_list_from_db()

    station_map = StationMap(stations_list)
    fmap = station_map.create_default_map()

    return render_template("stations.html", source="db", stations=stations_list, map_html=fmap._repr_html_())

@station_bp.route("/city")
def stations_list():
    """
    Widok wyświetlający sortowaną (przez nazwę miejscowości)
    listę stacji pomiarowych w Polsce wraz z ich lokalizacją na mapie.

    - Pobiera listę stacji z API GIOŚ przy użyciu klasy `Downloader`.
    - Tworzy mapę osadzoną w środku Polski.
    - Renderuje szablon
    """

    city = request.args.get("city")
    stations_list = []


    if city:
        downloader = Downloader(api_address)
        stations_list = downloader.fetch_stations_list_by_city(city_name=city)

    station_map = StationMap(stations_list)
    fmap = station_map.create_default_map()


    return render_template("stations.html", source="api", stations=stations_list, map_html=fmap._repr_html_())


@station_bp.route("/nearby")
def stations_nearby():
    """
    Widok wyszukujący stacje pomiarowe w zadanym promieniu od wskazanej lokalizacji.

    - Pobiera parametry zapytania:
        * `location` – adres lub nazwa miejscowości podana przez użytkownika,
        * `radius` – promień wyszukiwania w kilometrach.
    - Pobiera listę stacji z API GIOŚ przy użyciu klasy `Downloader`.
    - Tworzy obiekt `StationMapWithRadius`, który umożliwia:
        * sortowanie stacji względem odległości od lokalizacji,
        * filtrowanie według promienia wyszukiwania.
    - Generuje mapę z zaznaczonymi stacjami znajdującymi się w zadanym promieniu.
    - Renderuje szablon
    """

    stations_list = []

    location = request.args.get("location")
    radius = request.args.get("radius", type=float)

    downloader = Downloader(api_address)
    stations_list = downloader.fetch_stations_list()

    station_map_with_radius = StationMapWithRadius(stations_list, location, radius)
    stations_list_sorted = station_map_with_radius.sort_list_by_location_and_radius()

    fmap = station_map_with_radius.create_map()

    return render_template("stations.html", source="api", stations=stations_list_sorted, map_html=fmap._repr_html_())

@station_bp.route("/live/<int:station_id>")
def station_detail(station_id):
    """
    Widok szczegółowy dla wybranej stacji pomiarowej (na żywo, z API GIOŚ).

    - Przyjmuje w URL identyfikator stacji (`station_id`).
    - Korzysta z `Downloader`, aby pobrać:
        * słownik wszystkich stacji (`fetch_stations_dict`),
        * listę czujników przypisanych do stacji (`fetch_station_sensors_list`),
        * aktualny wskaźnik jakości powietrza AQI (`fetch_station_index`).
    - Renderuje szablon
    """

    downloader = Downloader(api_address)
    stations_dict = downloader.fetch_stations_dict()
    sensors_list = downloader.fetch_station_sensors_list(str(station_id))
    aqi = downloader.fetch_station_index(str(station_id))

    return render_template("station_detail.html",
                           source="api",
                           station=stations_dict[station_id],
                           sensors=sensors_list,
                           aqi=aqi)

@station_bp.route("/archive/<int:station_id>")
def station_detail_archive(station_id):
    """
    Widok szczegółowy dla wybranej stacji pomiarowej (dane archiwalne, z API GIOŚ).

    - Przyjmuje w URL identyfikator stacji (`station_id`).
    - Korzysta z `Downloader`, aby pobrać:
        * słownik wszystkich stacji (`fetch_stations_dict`),
        * listę czujników przypisanych do stacji (`fetch_station_sensors_list`),
        * aktualny wskaźnik jakości powietrza AQI (`fetch_station_index`).
    - Renderuje szablon
    """

    service = DataService()

    sensors_list = service.get_sensors_list_from_db(station_id)
    stations_list = service.get_stations_list_from_db()
    station_indexes = service.get_station_index_list_from_db(station_id)

    station: Station = None
    for item in stations_list:
        if(item.id == station_id):
            station = item

    return render_template("station_detail.html", source="db", station=station, sensors=sensors_list, station_indexes=station_indexes)


@station_bp.route("/live/<int:station_id>/<int:sensor_id>", methods=["POST", "GET"])
def sensor_detail(station_id, sensor_id):
    """
    Widok szczegółowy czujnika pomiarowego w wybranej stacji (dane na żywo z API GIOŚ).

    - Parametry ścieżki:
        * `station_id` – identyfikator stacji,
        * `sensor_id` – identyfikator czujnika w tej stacji.
    - Pobiera z API:
        * listę pomiarów dla danego czujnika (`fetch_measurement`),
        * słownik wszystkich stacji (`fetch_stations_dict`),
        * słownik czujników przypisanych do wskazanej stacji (`fetch_station_sensors_dict`).
    - Tworzy obiekt `measurements_json`, czyli dane pomiarowe
      zserializowane do JSON (lista słowników: data + wartość), gotowe
      do wykorzystania w wykresach lub skryptach JS w szablonie.
    - Renderuje szablon
    """

    downloader = Downloader(api_address)
    measurements = downloader.fetch_measurement(str(sensor_id))
    stations_dict = downloader.fetch_stations_dict()
    sensors_dict = downloader.fetch_station_sensors_dict(str(station_id))

    calculation = CalculationService(measurements)
    results = calculation.calculation_model()


    measurements_json = json.dumps([
        {
            "data": m.data,
            "wartosc": m.wartosc
        } for m in measurements
    ], ensure_ascii=False)

    return render_template(
        "sensor_detail.html",
        source="api",
        station_id=station_id,
        station=stations_dict[station_id],
        sensor=sensors_dict[sensor_id],
        measurements=measurements,
        measurements_json=measurements_json,
        results=results
    )


@station_bp.route("/archive/<int:station_id>/<int:sensor_id>", methods=["POST", "GET"])
def sensor_detail_archive(station_id, sensor_id):
    """
    Widok szczegółowy czujnika pomiarowego w wybranej stacji (dane archiwalne z API GIOŚ).

    - Parametry ścieżki:
        * `station_id` – identyfikator stacji,
        * `sensor_id` – identyfikator czujnika w tej stacji.
    - Pobiera z API:
        * listę pomiarów dla danego czujnika (`fetch_measurement`),
        * słownik wszystkich stacji (`fetch_stations_dict`),
        * słownik czujników przypisanych do wskazanej stacji (`fetch_station_sensors_dict`).
    - Tworzy obiekt `measurements_json`, czyli dane pomiarowe
      zserializowane do JSON (lista słowników: data + wartość), gotowe
      do wykorzystania w wykresach lub skryptach JS w szablonie.
    - Renderuje szablon
    """

    service = DataService()
    measurements = service.get_measurements_list_from_db(sensor_id)

    downloader = Downloader(api_address)
    stations_dict = downloader.fetch_stations_dict()
    sensors_dict = downloader.fetch_station_sensors_dict(str(station_id))

    calculation = CalculationService(measurements)
    results = calculation.calculation_model()


    measurements_json = json.dumps([
        {
            "data": m.data,
            "wartosc": m.wartosc
        } for m in measurements
    ], ensure_ascii=False)



    return render_template(
        "sensor_detail.html",
        source="db",
        station_id=station_id,
        station=stations_dict[station_id],
        sensor=sensors_dict[sensor_id],
        measurements=measurements,
        measurements_json=measurements_json,
        results=results
    )

@station_bp.route("/archive/<int:station_id>/<int:sensor_id>/filtred", methods=["POST", "GET"])
def sensor_detail_archive_filtered(station_id, sensor_id):
    """
        Widok szczegółowy czujnika pomiarowego dla danych archiwalnych (z bazy danych)
        z możliwością filtrowania pomiarów po zakresie dat.

        pobiera dane takie jak w sensor_detail_archive


        - Obsługuje parametry zapytania:
            * `startDate` – początkowa data filtrowania (string),
            * `endDate` – końcowa data filtrowania (string).
        - Jeżeli podano zakres dat, filtruje pomiary tak, aby uwzględniały
          wyłącznie rekordy, których `m.data` mieści się w zadanym przedziale.
        - Tworzy `measurements_json`, czyli dane pomiarowe w formacie JSON
          (lista słowników: data + wartość), gotowe do wykorzystania
          w części frontendowej (np. na wykresach).
        - Renderuje szablon
    """

    service = DataService()
    measurements = service.get_measurements_list_from_db(sensor_id)

    downloader = Downloader(api_address)
    stations_dict = downloader.fetch_stations_dict()
    sensors_dict = downloader.fetch_station_sensors_dict(str(station_id))

    start_str = request.args.get("startDate")
    end_str = request.args.get("endDate")

    print(start_str)
    print(end_str)
    filtered = []
    measurements_json = []
    results = {}
    if(start_str and end_str != None):
        for m in measurements:
            if (m.data >= start_str and m.data <= end_str):
                calculation = CalculationService(measurements)
                results = calculation.calculation_model()
                filtered.append({
                    "data": m.data,  # jeśli m.data to datetime
                    "wartosc": m.wartosc
                })
        measurements_json = json.dumps(filtered, ensure_ascii=False)




    return render_template(
        "sensor_detail.html",
        source="db",
        station_id=station_id,
        station=stations_dict[station_id],
        sensor=sensors_dict[sensor_id],
        measurements=measurements,
        measurements_json=measurements_json,
        results=results
    )


@station_bp.route("/<int:station_id>/<int:sensor_id>/add", methods=["POST"])
def add_data(station_id, sensor_id):
    """
        Endpoint do dodawania danych pomiarowych wybranego czujnika do lokalnej bazy danych.

        - Parametry ścieżki:
            * `station_id` – identyfikator stacji,
            * `sensor_id` – identyfikator czujnika w tej stacji.
        - Pobiera dane z API GIOŚ:
            * słownik wszystkich stacji (`fetch_stations_dict`),
            * słownik czujników przypisanych do stacji (`fetch_station_sensors_dict`),
            * listę pomiarów czujnika (`fetch_measurement`),
            * bieżący wskaźnik jakości powietrza stacji (`fetch_station_index`).
        - Zapisuje pobrane pomiary do lokalnej bazy danych przy użyciu `DataService.save_measurement`.
        - Po zapisaniu danych następuje przekierowanie (HTTP redirect) do widoku szczegółowego czujnika (`sensor_detail`),
          aby użytkownik mógł od razu zobaczyć zaktualizowane dane.
    """

    service = DataService()

    downloader = Downloader(api_address)
    stations_dict = downloader.fetch_stations_dict()
    sensors_dict = downloader.fetch_station_sensors_dict(str(station_id))
    measurements = downloader.fetch_measurement(str(sensor_id))
    station_index = downloader.fetch_station_index(str(station_id))

    calculation = CalculationService(measurements)
    results = calculation.calculation_model()

    service.save_measurement(stations_dict[station_id], sensors_dict[sensor_id], measurements, sensor_id, station_index, station_id)

    return redirect(url_for("stations.sensor_detail", station_id=station_id,
                            sensor_id=sensor_id))

