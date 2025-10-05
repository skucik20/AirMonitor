from app import db
from app.models.station import Station
from app.models.sensor import Sensor
from app.models.measurement import Measurement
from app.models.station_index import StationIndex


class DataService:
    """
    Serwis do obsługi zapisu i odczytu danych (Station, Sensor, Measurement).
    """

    # -------------------------------
    # Station
    # -------------------------------
    def get_or_create_station(self, station_data: Station) -> Station:
        """
        Szuka stacji po id, jeżeli nie istnieje -> tworzy nową.
        """
        station = Station.query.filter_by(id=station_data.id).first()

        if station:
            print("Station exist")
            return station
        else:
            db.session.add(station_data)


            # sensors_data.id_stacji = station_data.id
            # db.session.add(sensors_data)

            db.session.commit()
        return station

    # -------------------------------
    # Station
    # -------------------------------
    def get_or_create_sensor(self, sensors_data: Sensor, station_data: Station) -> Sensor:
        """
        Szuka sensora po id, jeżeli nie istnieje -> tworzy nowy wiersz.
        """
        sensor = Sensor.query.filter_by(id_stanowiska=sensors_data.id_stanowiska).first()

        if sensor:
            print("Sensor exist")
            return sensor
        else:

            sensors_data.id_stacji = station_data.id
            db.session.add(sensors_data)

            db.session.commit()
        return sensor

    # -------------------------------
    # Measurement
    # -------------------------------
    def save_measurement(self, station_data: Station, sensors_data: Sensor, measurement_data: list, sensor_id: int,
                         station_index_data: StationIndex, station_id: int) -> Measurement:
        """
        1. Sprawdza czy istnieje stacja — jeżeli nie, dodaje.
        2. Sprawdza czy istnieje sensor — jeżeli nie, dodaje.
        3. Zapisuje pomiar powiązany z sensorem.
        4. Zapisuje pomiar_aqi powiązany ze stacją.
        """
        # 1. Stacja
        self.get_or_create_station(station_data)

        # 2. Sensor
        self.get_or_create_sensor(sensors_data, station_data)

        # 3. Measurement
        measurements_db = self.get_measurements_list_from_db(sensor_id)

        for measurement in measurement_data:
            if measurement not in measurements_db:
                measurement.sensor_id = sensor_id
                db.session.add(measurement)

        # 4. AQI
        station_indexes_db = self.get_station_index_list_from_db(station_id)

        if station_index_data.calculation_date not in station_indexes_db:
            db.session.add(station_index_data)

        db.session.commit()

        return measurement

    def get_stations_list_from_db(self):
        """
            Pobiera listę wszystkich stacji pomiarowych z bazy danych.

            Zwraca:
                list[Station]: Lista obiektów Station.
        """
        stations = Station.query.all()
        return stations

    def get_sensors_list_from_db(self, sensors_id: int):
        """
        Pobiera listę czujników przypisanych do konkretnej stacji.

        Argumenty:
            sensors_id (int): Identyfikator stacji, dla której mają być pobrane czujniki.

        Zwraca:
            list[Sensor]: Lista obiektów Sensor przypisanych do stacji.
        """
        sensors = Sensor.query.filter_by(id_stacji=sensors_id).all()
        return sensors

    def get_measurements_list_from_db(self, sensors_id: int):
        """
        Pobiera listę pomiarów dla konkretnego czujnika.

        Argumenty:
            sensors_id (int): Identyfikator czujnika, dla którego mają być pobrane pomiary.

        Zwraca:
            list[Measurement]: Lista obiektów Measurement przypisanych do czujnika.
        """
        measurements = Measurement.query.filter_by(sensor_id=sensors_id).all()
        return measurements

    def get_station_index_list_from_db(self, station_id: int):
        """
        Pobiera listę wszystkich indeksów stacji pomiarowych z bazy danych.

        Zwraca:
            list[StationIndex]: Lista obiektów StationIndex.
        """
        station_indexes = StationIndex.query.filter_by(station_id=station_id).all()
        return station_indexes


