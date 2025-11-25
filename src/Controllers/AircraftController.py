import json
from src.Models.AircraftModel import Aircraft



class AircraftController:
    def __init__(self, db):
        self.db = db
        # Создание таблицы при инициализации
        Aircraft.create_table(self.db)

    def get_all_aircrafts(self):
        """Получение всех самолетов"""
        return Aircraft.read_all(self.db)

    def create_aircraft(self, aircraft_code, model, range):
        """Создание нового самолета"""
        return Aircraft.create(self.db, aircraft_code, model, range)

    def find_aircraft(self, aircraft_code):
        """Поиск самолета по коду"""
        return Aircraft.read_by_code(self.db, aircraft_code)

    def update_aircraft(self, aircraft_code, model=None, range=None):
        """Обновление данных самолета"""
        return Aircraft.update(self.db, aircraft_code, model, range)

    def delete_aircraft(self, aircraft_code):
        """Удаление самолета"""
        return Aircraft.delete(self.db, aircraft_code)

    def get_all_aircrafts_paginated(self, offset, limit):
        """Получение самолетов с пагинацией"""
        return Aircraft.read_all_paginated(self.db, offset, limit)