from src.Models.BoardingPassesModel import BoardingPass

class BoardingPassController:
    def __init__(self, db):
        self.db = db
        # Создание таблицы при инициализации
        BoardingPass.create_table(self.db)

    # ... существующие методы ...

    # Методы для работы с представлением
    def get_all_boarding_passes(self):
        """Получение всех посадочных талонов"""
        return BoardingPass.read_all(self.db)

    def get_boarding_passes_by_flight(self, flight_id):
        """Получение посадочных талонов для рейса"""
        return BoardingPass.read_by_flight(self.db, flight_id)

    def create_boarding_pass(self, ticket_no, flight_id, boarding_no, seat_no):
        """Создание нового посадочного талона"""
        return BoardingPass.create(self.db, ticket_no, flight_id, boarding_no, seat_no)

    def find_boarding_pass(self, ticket_no, flight_id):
        """Поиск посадочного талона по номеру билета и рейсу"""
        return BoardingPass.read_by_ticket_and_flight(self.db, ticket_no, flight_id)

    def find_boarding_pass_by_boarding_no(self, flight_id, boarding_no):
        """Поиск посадочного талона по номеру посадки"""
        return BoardingPass.read_by_boarding_no(self.db, flight_id, boarding_no)

    def update_boarding_pass_seat(self, ticket_no, flight_id, seat_no):
        """Обновление места в посадочном талоне"""
        return BoardingPass.update_seat(self.db, ticket_no, flight_id, seat_no)

    def update_boarding_pass_number(self, ticket_no, flight_id, boarding_no):
        """Обновление номера посадки"""
        return BoardingPass.update_boarding_no(self.db, ticket_no, flight_id, boarding_no)

    def delete_boarding_pass(self, ticket_no, flight_id):
        """Удаление посадочного талона"""
        return BoardingPass.delete(self.db, ticket_no, flight_id)

    def get_occupied_seats(self, flight_id):
        """Получение занятых мест для рейса"""
        return BoardingPass.get_available_seats(self.db, flight_id)

    def get_next_boarding_no(self, flight_id):
        """Получение следующего номера посадки для рейса"""
        return BoardingPass.get_next_boarding_no(self.db, flight_id)

    def get_all_boarding_passes_paginated(self, offset, limit):
        """Получение посадочных талонов с пагинацией"""
        return BoardingPass.read_all_paginated(self.db, offset, limit)