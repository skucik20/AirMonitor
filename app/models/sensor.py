from app import db

class Sensor(db.Model):
    """
        Reprezentuje czujnik przypisany do stacji pomiarowej w bazie danych.

        Atrybuty:
            id (int): Unikalny identyfikator czujnika.
            id_stanowiska (int): Identyfikator stanowiska pomiarowego.
            wskaznik (str): Nazwa wskaźnika mierzonej wielkości.
            wskaznik_wzor (str | None): Opcjonalny wzór wskaźnika.
            wskaznik_kod (str): Kod wskaźnika.
            id_wskaznika (int): Identyfikator wskaźnika.
            id_stacji (int): Identyfikator stacji, do której należy czujnik.
            station (Station): Relacja do obiektu Station, do którego należy czujnik.
    """
    __tablename__ = "sensors"

    id = db.Column(db.Integer, primary_key=True)
    id_stanowiska = db.Column(db.Integer, nullable=False)  # np. ID pomiarowe
    wskaznik = db.Column(db.String(120), nullable=False)
    wskaznik_wzor = db.Column(db.String(120), nullable=True)
    wskaznik_kod = db.Column(db.String(50), nullable=False)
    id_wskaznika = db.Column(db.Integer, nullable=False)

    # Foreign Key do stacji
    id_stacji = db.Column(db.Integer, db.ForeignKey("stations.id"), nullable=False)
    station = db.relationship("Station", back_populates="sensors")
