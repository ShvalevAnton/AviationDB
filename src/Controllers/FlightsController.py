# FlightsController.py
from src.Models.FlightsModel import Flight


class FlightController:
    def __init__(self, db):
        self.db = db
        # Создание таблицы при инициализации
        Flight.create_table(self.db)

    def get_all_flights(self):
        """Получение всех рейсов"""
        return Flight.read_all(self.db)

    def create_flight(self, flight_no, scheduled_departure, scheduled_arrival,
                      departure_airport, arrival_airport, status, aircraft_code,
                      actual_departure=None, actual_arrival=None):
        """Создание нового рейса"""
        return Flight.create(
            self.db, flight_no, scheduled_departure, scheduled_arrival,
            departure_airport, arrival_airport, status, aircraft_code,
            actual_departure, actual_arrival
        )

    def find_flight(self, flight_id):
        """Поиск рейса по ID"""
        return Flight.read_by_id(self.db, flight_id)

    def update_flight(self, flight_id, flight_no=None, scheduled_departure=None, scheduled_arrival=None,
                      departure_airport=None, arrival_airport=None, status=None, aircraft_code=None,
                      actual_departure=None, actual_arrival=None):
        """Обновление данных рейса"""
        success = True

        if flight_no:
            success = success and Flight.update_flight_no(self.db, flight_id, flight_no)
        if scheduled_departure:
            success = success and Flight.update_scheduled_departure(self.db, flight_id, scheduled_departure)
        if scheduled_arrival:
            success = success and Flight.update_scheduled_arrival(self.db, flight_id, scheduled_arrival)
        if departure_airport:
            success = success and Flight.update_departure_airport(self.db, flight_id, departure_airport)
        if arrival_airport:
            success = success and Flight.update_arrival_airport(self.db, flight_id, arrival_airport)
        if status:
            success = success and Flight.update_status(self.db, flight_id, status)
        if aircraft_code:
            success = success and Flight.update_aircraft_code(self.db, flight_id, aircraft_code)
        if actual_departure is not None:
            success = success and Flight.update_actual_departure(self.db, flight_id, actual_departure)
        if actual_arrival is not None:
            success = success and Flight.update_actual_arrival(self.db, flight_id, actual_arrival)

        return success

    def delete_flight(self, flight_id):
        """Удаление рейса"""
        return Flight.delete(self.db, flight_id)

    def get_all_flights_paginated(self, offset, limit):
        """Получение рейсов с пагинацией"""
        return Flight.read_all_paginated(self.db, offset, limit)

    def get_available_statuses(self):
        """Получение списка доступных статусов"""
        return Flight.get_available_statuses()