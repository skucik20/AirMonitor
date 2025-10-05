from app import db

class City(db.Model):
    """
    Reprezentuje miasto w bazie danych.

    Atrybuty:
        id (int): Unikalny identyfikator miasta.
        name (str): Nazwa miasta.
        gmina_id (int): Identyfikator gminy, do której należy miasto.
        gmina (Gmina): Relacja z obiektem Gmina, do którego należy miasto.
        stations (list[Station]): Lista stacji znajdujących się w mieście.
    """
    __tablename__ = "cities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    gmina_id = db.Column(db.Integer, db.ForeignKey("gminy.id"), nullable=False)
    gmina = db.relationship("Gmina", back_populates="cities")

    stations = db.relationship("Station", back_populates="city")
