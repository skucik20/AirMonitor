import requests
from typing import Dict, List
from app.models import Gmina, City, Station
from app.models.sensor import Sensor
from app.models.measurement import Measurement
from app.models.station_index import StationIndex


class Downloader:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.stations_dict: Dict[int, Station] = {}
        self.sensors_dict: Dict[int, Sensor] = {}
        self.stations_list = []

    def fetch_station_index(self, station_id, endpoint: str = "aqindex/getIndex") -> StationIndex:
        """Pobiera dane pomiarowe wskazanego stanowiska pomiarowego"""

        url = self.base_url.rstrip("/") + "/" + endpoint.lstrip("/") + "/" + station_id.lstrip("/")
        try:
            response = requests.get(url)
            response.raise_for_status()
            raw_data = response.json()

            sensors_data = raw_data.get("AqIndex")
            print(sensors_data)

            aqi = StationIndex(
                station_id=sensors_data["Identyfikator stacji pomiarowej"],
                calculation_date=sensors_data["Data wykonania obliczeń indeksu"],
                index_value=sensors_data["Wartość indeksu"],
                index_category=sensors_data["Nazwa kategorii indeksu"],
                calculation_date_st=sensors_data["Data danych źródłowych, z których policzono wartość indeksu dla wskaźnika st"],
            )

        except requests.exceptions.RequestException as e:
            print(f"Błąd pobierania danych: {e}")
            return {}

        return aqi


    def fetch_measurement(self, station_id, endpoint: str = "data/getData") -> List[Station]:
        """Pobiera dane pomiarowe wskazanego stanowiska pomiarowego"""

        url = self.base_url.rstrip("/") + "/" + endpoint.lstrip("/") + "/" + station_id.lstrip("/")
        try:
            response = requests.get(url)
            response.raise_for_status()
            raw_data = response.json()

            sensors_data = raw_data.get("Lista danych pomiarowych")

            measurements = []

            for item in sensors_data:
                measurement = Measurement(
                    kod_stanowiska=item["Kod stanowiska"],
                    data=item["Data"],
                    wartosc=item["Wartość"]
                )
                measurements.append(measurement)

        except requests.exceptions.RequestException as e:
            print(f"Błąd pobierania danych: {e}")
            return {}

        return measurements

    def fetch_station_sensors_list(self, station_id, endpoint: str = "station/sensors") -> List[Sensor]:
        """Pobiera informacje na temat sensorów w danej stacji na podstawie id {id: Station}"""

        url = self.base_url.rstrip("/") + "/" + endpoint.lstrip("/") + "/" + station_id.lstrip("/")

        try:
            response = requests.get(url)
            response.raise_for_status()
            raw_data = response.json()

            sensors_data = raw_data.get("Lista stanowisk pomiarowych dla podanej stacji")

            sensors: List[Sensor] = []
            for item in sensors_data:
                sensor = Sensor(
                    id_stanowiska=item["Identyfikator stanowiska"],
                    id_stacji=item["Identyfikator stacji"],
                    wskaznik=item["Wskaźnik"],
                    wskaznik_wzor=item["Wskaźnik - wzór"],
                    wskaznik_kod=item["Wskaźnik - kod"],
                    id_wskaznika=item["Id wskaźnika"]
                )
                sensors.append(sensor)

        except requests.exceptions.RequestException as e:
            print(f"Błąd pobierania danych: {e}")
            return {}

        return sensors

    def fetch_station_sensors_dict(self, station_id, endpoint: str = "station/sensors") -> Dict[int, Station]:
        """Pobiera informacje na temat sensorów w danej stacji na podstawie id {id: Station}"""

        url = self.base_url.rstrip("/") + "/" + endpoint.lstrip("/") + "/" + station_id.lstrip("/")

        try:
            response = requests.get(url)
            response.raise_for_status()
            raw_data = response.json()

            sensors_data = raw_data.get("Lista stanowisk pomiarowych dla podanej stacji")

            self.sensors_dict.clear()

            for item in sensors_data:
                sensor = Sensor(
                    id_stanowiska=item["Identyfikator stanowiska"],
                    id_stacji=item["Identyfikator stacji"],
                    wskaznik=item["Wskaźnik"],
                    wskaznik_wzor=item["Wskaźnik - wzór"],
                    wskaznik_kod=item["Wskaźnik - kod"],
                    id_wskaznika=item["Id wskaźnika"]
                )
                self.sensors_dict[sensor.id_stanowiska] = sensor

        except requests.exceptions.RequestException as e:
            print(f"Błąd pobierania danych: {e}")
            return {}

        return self.sensors_dict

    def fetch_stations_list(self, endpoint: str = "station/findAll") -> List[Station]:
        """Pobiera listę stacji i zapisuje je w formie listy"""
        url = self.base_url.rstrip("/") + "/" + endpoint.lstrip("/")
        try:
            response = requests.get(url)
            response.raise_for_status()
            raw_data = response.json()

            stations = raw_data.get("Lista stacji pomiarowych")

            for station in stations:

                gmina = Gmina(
                    gminaName=station["Gmina"],
                    powiatName=station["Powiat"],
                    wojewodztwoName=station["Województwo"]
                )

                city = City(
                    id=station["Identyfikator miasta"],
                    name=station["Nazwa miasta"],
                    gmina=gmina
                )

                station_obj = Station(

                    id=station["Identyfikator stacji"],
                    stationCode=station["Kod stacji"],
                    stationName=station["Nazwa stacji"],
                    gegrLat=station["WGS84 φ N"],
                    gegrLon=station["WGS84 λ E"],
                    city=city,
                    addressStreet=station["Ulica"]
                )
                self.stations_list.append(station_obj)

            return self.stations_list

        except requests.exceptions.RequestException as e:
            print(f"Błąd pobierania danych: {e}")
            return {}

    def fetch_stations_list_by_city(self, city_name: str, endpoint: str = "station/findAll") -> List[Station]:
        """Pobiera listę stacji i zapisuje je w formie listy"""
        url = self.base_url.rstrip("/") + "/" + endpoint.lstrip("/")
        try:
            response = requests.get(url)
            response.raise_for_status()
            raw_data = response.json()

            stations = raw_data.get("Lista stacji pomiarowych")

            for station in stations:

                gmina = Gmina(
                    gminaName=station["Gmina"],
                    powiatName=station["Powiat"],
                    wojewodztwoName=station["Województwo"]
                )

                city = City(
                    id=station["Identyfikator miasta"],
                    name=station["Nazwa miasta"],
                    gmina=gmina
                )

                station_obj = Station(

                    id=station["Identyfikator stacji"],
                    stationCode=station["Kod stacji"],
                    stationName=station["Nazwa stacji"],
                    gegrLat=station["WGS84 φ N"],
                    gegrLon=station["WGS84 λ E"],
                    city=city,
                    addressStreet=station["Ulica"]
                )

                if station_obj.city.name == city_name:

                    self.stations_list.append(station_obj)

            return self.stations_list

        except requests.exceptions.RequestException as e:
            print(f"Błąd pobierania danych: {e}")
            return {}

    def fetch_stations_dict(self, endpoint: str = "station/findAll") -> Dict[int, Station]:
        """Pobiera listę stacji i zapisuje je w formie {id: Station}"""
        url = self.base_url.rstrip("/") + "/" + endpoint.lstrip("/")
        try:
            response = requests.get(url)
            response.raise_for_status()
            raw_data = response.json()

            stations = raw_data.get("Lista stacji pomiarowych")

            self.stations_dict.clear()
            for station in stations:

                gmina = Gmina(
                    gminaName=station["Gmina"],
                    powiatName=station["Powiat"],
                    wojewodztwoName=station["Województwo"]
                )

                city = City(
                    id=station["Identyfikator miasta"],
                    name=station["Nazwa miasta"],
                    gmina=gmina
                )

                station_obj = Station(

                    id=station["Identyfikator stacji"],
                    stationCode=station["Kod stacji"],
                    stationName=station["Nazwa stacji"],
                    gegrLat=station["WGS84 φ N"],
                    gegrLon=station["WGS84 λ E"],
                    city=city,
                    addressStreet=station["Ulica"]
                )
                self.stations_dict[station_obj.id] = station_obj

            return self.stations_dict

        except requests.exceptions.RequestException as e:
            print(f"Błąd pobierania danych: {e}")
            return {}
