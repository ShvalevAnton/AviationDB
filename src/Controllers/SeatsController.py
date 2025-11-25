from src.Models.SeatsModel import Seat

class SeatController:
    def __init__(self, db):
        self.db = db
        # Создание таблицы при инициализации
        Seat.create_table(self.db)

    def get_all_seats(self):
        """Получение всех мест"""
        return Seat.read_all(self.db)

    def create_seat(self, aircraft_code, seat_no, fare_conditions):
        """Создание нового места"""
        return Seat.create(self.db, aircraft_code, seat_no, fare_conditions)

    def find_seat(self, aircraft_code, seat_no):
        """Поиск места по первичному ключу"""
        return Seat.read_by_primary_key(self.db, aircraft_code, seat_no)

    def find_seats_by_aircraft(self, aircraft_code):
        """Поиск мест по коду самолета"""
        return Seat.read_by_aircraft(self.db, aircraft_code)

    def update_seat(self, aircraft_code, seat_no, fare_conditions=None):
        """Обновление данных места"""
        return Seat.update(self.db, aircraft_code, seat_no, fare_conditions)

    def delete_seat(self, aircraft_code, seat_no):
        """Удаление места"""
        return Seat.delete(self.db, aircraft_code, seat_no)

    def get_all_seats_paginated(self, offset, limit):
        """Получение мест с пагинацией"""
        return Seat.read_all_paginated(self.db, offset, limit)