from app import db
from dataclasses import dataclass


@dataclass
class Measurement(db.Model):
    """
        Reprezentuje pojedynczy pomiar z czujnika w bazie danych.

        Atrybuty:
            id (int): Unikalny identyfikator pomiaru.
            sensor_id (int): Identyfikator czujnika, który wykonał pomiar.
            kod_stanowiska (str): Kod stanowiska, z którego pochodzi pomiar.
            data (str): Data i czas wykonania pomiaru w formacie tekstowym.
            wartosc (float | None): Wartość zmierzonego parametru; może być pusta.
            sensor (Sensor): Relacja do obiektu Sensor, który wykonał pomiar.
    """
    __tablename__ = "measurements"

    id = db.Column(db.Integer, primary_key=True)

    # foreign key do Sensor.id
    sensor_id = db.Column(
        db.Integer,
        db.ForeignKey("sensors.id"),  # nazwa tabeli Sensor w bazie
        nullable=False
    )

    kod_stanowiska = db.Column(db.String(120), nullable=False)
    data = db.Column(db.String(50), nullable=False)
    wartosc = db.Column(db.Float, nullable=True)

    # relacja do obiektu Sensor
    sensor = db.relationship("Sensor", backref="measurements")

    def __repr__(self):
        return f"<Measurement sensor_id={self.sensor_id} data={self.data} wartosc={self.wartosc}>"
