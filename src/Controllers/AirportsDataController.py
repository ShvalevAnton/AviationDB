import json
from src.Models.AirportsDataModel import Airport


class AirportController:
    def __init__(self, db):
        self.db = db
        # Создание таблицы при инициализации
        Airport.create_table(self.db)

    def get_all_airports(self):
        """Получение всех аэропортов"""
        return Airport.read_all(self.db)

    def create_airport(self, airport_code, airport_name, city, longitude, latitude, timezone):
        """Создание нового аэропорта"""
        return Airport.create(self.db, airport_code, airport_name, city, longitude, latitude, timezone)

    def find_airport(self, airport_code):
        """Поиск аэропорта по коду"""
        return Airport.read_by_code(self.db, airport_code)

    def update_airport(self, airport_code, airport_name=None, city=None, longitude=None, latitude=None, timezone=None):
        """Обновление данных аэропорта"""
        return Airport.update(self.db, airport_code, airport_name, city, longitude, latitude, timezone)

    def delete_airport(self, airport_code):
        """Удаление аэропорта"""
        return Airport.delete(self.db, airport_code)

    def find_nearby_airports(self, longitude, latitude, radius_km=100):
        """Поиск ближайших аэропортов"""
        return Airport.find_nearby_airports(self.db, longitude, latitude, radius_km)

    def get_all_airports_paginated(self, offset, limit):
        """Получение аэропортов с пагинацией"""
        return Airport.read_all_paginated(self.db, offset, limit)