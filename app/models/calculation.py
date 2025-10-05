from dataclasses import dataclass
from typing import Literal

@dataclass
class Calculation():
    min: float
    max: float
    srednia: float
    trend: Literal["rosnący", "malejący", "stały", "za mało danych do określenia trendu"]
