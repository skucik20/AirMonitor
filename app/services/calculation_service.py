from app.models.calculation import Calculation

class CalculationService:
    def __init__(self, values):

        self.values = values
        self.pomiary = []
        self.pomiary_to_value_list()

    def calculation_model(self):
        """Zwraca wyniki analizy w formie modelu Pydantic"""

        return Calculation(
            min=self.min_wartosc(),
            max=self.max_wartosc(),
            srednia=self.srednia(),
            trend=self.trend()
        )

    def pomiary_to_value_list(self):

        for v in self.values:
            if v.wartosc is not None:
                self.pomiary.append(v.wartosc)


    def min_wartosc(self):
        """Zwraca najmniejszą wartość z listy pomiarów"""
        if self.values:
            return round(min(self.pomiary), 3)

    def max_wartosc(self):
        """Zwraca największą wartość z listy pomiarów"""
        if self.values:
            return round(max(self.pomiary), 3)

    def srednia(self):
        """Zwraca średnią wartość pomiarów"""
        if self.values:
            return round(sum(self.pomiary) / len(self.pomiary), 3)

    def trend(self):
        """Określa trend danych:
        - 'rosnący' jeśli dane mają tendencję do wzrostu
        - 'malejący' jeśli dane mają tendencję do spadku
        - 'stały' jeśli brak wyraźnego trendu
        """
        if self.values:
            if len(self.pomiary) < 2:
                return "za mało danych do określenia trendu"

            roznice = [self.pomiary[i+1] - self.pomiary[i] for i in range(len(self.pomiary)-1)]
            suma_roznic = sum(roznice)

            if suma_roznic > 0:
                return "rosnący"
            elif suma_roznic < 0:
                return "malejący"
            else:
                return "stały"


# P
