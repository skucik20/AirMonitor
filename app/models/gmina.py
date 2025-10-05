from app import db

class Gmina(db.Model):
    """
    Reprezentuje gminę w bazie danych.

    Atrybuty:
        id (int): Unikalny identyfikator gminy.
        gminaName (str): Nazwa gminy.
        powiatName (str): Nazwa powiatu, do którego należy gmina.
        wojewodztwoName (str): Nazwa województwa, do którego należy gmina.
        cities (list[City]): Lista miast należących do gminy.
    """
    __tablename__ = "gminy"

    id = db.Column(db.Integer, primary_key=True)
    gminaName = db.Column(db.String(120), nullable=False)
    powiatName = db.Column(db.String(120), nullable=False)
    wojewodztwoName = db.Column(db.String(120), nullable=False)

    cities = db.relationship("City", back_populates="gmina")