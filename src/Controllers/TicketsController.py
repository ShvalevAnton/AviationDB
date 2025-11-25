# TicketsController.py
from src.Models.TicketsModel import Ticket


class TicketsController:
    def __init__(self, db):
        self.db = db
        # Создание таблицы при инициализации
        Ticket.create_table(self.db)

    def get_all_tickets_paginated(self, offset, limit):
        """Получение всех билетов с пагинацией"""
        return Ticket.read_all_paginated(self.db, offset, limit)

    def create_ticket(self, ticket_no, book_ref, passenger_id, passenger_name, contact_data=None):
        """Создание нового билета"""
        return Ticket.create(self.db, ticket_no, book_ref, passenger_id, passenger_name, contact_data)

    def find_ticket(self, ticket_no):
        """Поиск билета по номеру"""
        return Ticket.read_by_ticket_no(self.db, ticket_no)

    def update_ticket(self, ticket_no, passenger_name=None, passenger_id=None, contact_data=None):
        """Обновление данных билета"""
        return Ticket.update_passenger_info(self.db, ticket_no, passenger_name, passenger_id, contact_data)

    def delete_ticket(self, ticket_no):
        """Удаление билета"""
        return Ticket.delete(self.db, ticket_no)