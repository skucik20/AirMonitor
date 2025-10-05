from app import db
from dataclasses import dataclass


@dataclass
class StationIndex(db.Model):
    """
        Reprezentuje indeks stacji pomiarowej w bazie danych.

        Atrybuty:
            id (int): Unikalny identyfikator rekordu indeksu.
            station_id (int): Identyfikator stacji pomiarowej, której dotyczy indeks.
            calculation_date (str): Data wykonania obliczeń indeksu.
            index_value (int): Wartość wyliczonego indeksu.
            index_category (str): Kategoria lub nazwa indeksu.
            calculation_date_st (str): Data wykonania obliczeń indeksu (alternatywne pole).
    """
    __tablename__ = "station_index"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    station_id = db.Column(db.Integer, nullable=False)  # Identyfikator stacji pomiarowej
    calculation_date = db.Column(db.String(50), nullable=False)  # Data wykonania obliczeń indeksu
    index_value = db.Column(db.Integer, nullable=False)  # Wartość indeksu
    index_category = db.Column(db.String, nullable=False)  # Nazwa kategorii indeksu
    calculation_date_st = db.Column(db.String(50), nullable=False)  # Data wykonania obliczeń indeksu
