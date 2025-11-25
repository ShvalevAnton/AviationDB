# TicketFlightsController.py
from src.Models.TicketFlightsModel import TicketFlight


class TicketFlightsController:
    def __init__(self, db):
        self.db = db
        # Создание таблицы при инициализации
        TicketFlight.create_table(self.db)

    def get_all_ticket_flights(self):
        """Получение всех билетов на рейсы"""
        return TicketFlight.read_all(self.db)

    def create_ticket_flight(self, ticket_no, flight_id, fare_conditions, amount):
        """Создание нового билета на рейс"""
        return TicketFlight.create(self.db, ticket_no, flight_id, fare_conditions, amount)

    def find_ticket_flight(self, ticket_no, flight_id):
        """Поиск билета на рейс по номеру билета и рейсу"""
        return TicketFlight.read_by_ticket_and_flight(self.db, ticket_no, flight_id)

    def update_ticket_flight(self, ticket_no, flight_id, fare_conditions=None, amount=None):
        """Обновление данных билета на рейс"""
        success = True

        if fare_conditions:
            success = success and TicketFlight.update_fare_conditions(self.db, ticket_no, flight_id, fare_conditions)

        if amount is not None:
            success = success and TicketFlight.update_amount(self.db, ticket_no, flight_id, amount)

        return success

    def delete_ticket_flight(self, ticket_no, flight_id):
        """Удаление билета на рейс"""
        return TicketFlight.delete(self.db, ticket_no, flight_id)

    def get_all_ticket_flights_paginated(self, offset, limit):
        """Получение билетов на рейсы с пагинацией"""
        return TicketFlight.read_all_paginated(self.db, offset, limit)