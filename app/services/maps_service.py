import folium
from math import radians, cos, sin, asin, sqrt
import requests

class StationMap:
    def __init__(self, stations_list, center_lat=52.0, center_lon=19.0, zoom_start=6, height=600):
        self.stations_list = stations_list
        self.center = (center_lat, center_lon)
        self.zoom_start = zoom_start
        self.height = height
        self.map = None


    def create_default_map(self):
        """Tworzy mapę i dodaje stacje jako markery."""
        self.map = folium.Map(
            location=self.center,
            zoom_start=self.zoom_start,
            height=self.height
        )
        for s in self.stations_list:
            if s.gegrLat and s.gegrLon:
                folium.Marker(
                    [float(s.gegrLat), float(s.gegrLon)],
                    popup=f"{s.stationName} ({s.city.name if getattr(s.city, 'name', None) else ''})"
                ).add_to(self.map)
        return self.map



class StationMapWithRadius(StationMap):
    """Klasa dziedzicząca po StationMap, z dodatkowymi zmiennymi aby umożliwoć filtracje."""
    def __init__(self, stations_list, location, radius,
                 center_lat=52.0, center_lon=19.0, zoom_start=6, height=600):
        # wywołanie konstruktora klasy bazowej
        super().__init__(stations_list, center_lat, center_lon, zoom_start, height)

        # nowe atrybuty
        self.location = location  # np. adres lub (lat, lon)
        self.radius = radius  # np. w km
        self.coords = []
        self.lat = None
        self.lon = None

    def create_map(self):
        """Tworzy mapę i dodaje stacje jako markery."""
        self.map = folium.Map(
            location=self.center,
            zoom_start=self.zoom_start,
            height=self.height
        )

        stations_list_sorted = self.sort_list_by_location_and_radius()

        for s in stations_list_sorted:
            if s.gegrLat and s.gegrLon:
                folium.Marker(
                    [float(s.gegrLat), float(s.gegrLon)],
                    popup=f"{s.stationName} ({s.city.name if getattr(s.city, 'name', None) else ''})"
                ).add_to(self.map)
        return self.map

    def sort_list_by_location_and_radius(self):
        """Na podstawie lokalizacji i promienia w kilometach sortuje listę"""
        if self.location and self.radius:
            self.coords = self.geocode_address()
            print(f'Coords {self.coords}')
            if self.coords:
                self.lat, self.lon = self.coords
                stations_list_in_radius = self.filter_stations_by_radius()

        return stations_list_in_radius

    def geocode_address(self):
        """Geokodowanie przez Nominatim (OpenStreetMap API)."""
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": self.location, "format": "json", "limit": 1}
        resp = requests.get(url, params=params, headers={"User-Agent": "stations-app"})
        resp.raise_for_status()
        data = resp.json()
        print(data)
        if not data:
            return None
        return float(data[0]["lat"]), float(data[0]["lon"])

    def haversine(self, lat1, lon1, lat2, lon2):
        """Odległość w km między dwoma punktami."""
        R = 6371
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        return R * c

    def filter_stations_by_radius(self):
        result = []
        for s in self.stations_list:
            slat = s.gegrLat
            slon = s.gegrLon
            if slat and slon:
                dist = self.haversine(float(slat), float(slon), self.lat, self.lon)
                if dist <= self.radius:
                    result.append(s)
        return result
