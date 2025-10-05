from app import db

class Station(db.Model):
    """
        Reprezentuje stację pomiarową w bazie danych.

        Atrybuty:
            id (int): Unikalny identyfikator stacji.
            stationCode (str): Unikalny kod stacji.
            stationName (str): Nazwa stacji.
            gegrLat (str): Szerokość geograficzna stacji.
            gegrLon (str): Długość geograficzna stacji.
            addressStreet (str | None): Opcjonalny adres ulicy stacji.
            city_id (int): Identyfikator miasta, w którym znajduje się stacja.
            city (City): Relacja do obiektu City, w którym znajduje się stacja.
            sensors (list[Sensor]): Lista czujników przypisanych do stacji.
    """
    __tablename__ = "stations"

    id = db.Column(db.Integer, primary_key=True)
    stationCode = db.Column(db.String(50), unique=True, nullable=False)
    stationName = db.Column(db.String(120), nullable=False)
    gegrLat = db.Column(db.String(50), nullable=False)
    gegrLon = db.Column(db.String(50), nullable=False)
    addressStreet = db.Column(db.String(200), nullable=True)


    city_id = db.Column(db.Integer, db.ForeignKey("cities.id"), nullable=False)
    city = db.relationship("City", back_populates="stations")

    sensors = db.relationship("Sensor", back_populates="station")
